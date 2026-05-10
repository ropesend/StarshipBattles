"""
Ship Stats Calculator — coordinator for derived ship statistics.

This module owns the *phase order* of ship-stat calculation. Per-domain
aggregation (movement, defense, weapons, command, launch) lives in
``stat_contributors/`` modules. The coordinator preserves the legacy
mutation order verbatim so the golden snapshot from PROJ-360 Phase 1
keeps passing bit-for-bit.

Stat Calculation Phases:

    Phase 1 — DAMAGE CHECK & SUPPLY GATHERING
    Phase 2 — RESOURCE ALLOCATION (crew + life support)
    Phase 3 — STATS AGGREGATION (active components only)
    Phase 4 — PHYSICS & LIMITS
    Phase 5 — SENSOR / DEFENSE SCORES + RESOURCE INIT

Physics constants (`K_SPEED`, `K_THRUST`, `K_TURN`) live in
``physics_constants.py``.

Example:
    calculator = ShipStatsCalculator(
        registries.vehicle_classes,
        resource_catalog=registries.resource_catalog,
    )
    calculator.calculate(ship)
    # ship.max_speed, ship.turn_speed, etc. are now updated
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.config import PhysicsConfig
from game.simulation.components.component_constants import ComponentStatus
from game.core.constants import LayerType
from game.simulation.entities.ability_aggregator import calculate_ability_totals
from game.simulation.entities.combat_endurance import calculate_combat_endurance
from game.simulation.entities.stat_contributors import (
    command as _cmd,
    defense as _def,
    weapons as _wep,
)
from game.simulation.entities.stat_contributors.accumulator import StatAccumulator
from game.simulation.entities.stat_contributors.registry import (
    STAT_CONTRIBUTOR_REGISTRY,
)
from game.simulation.interfaces import (
    is_resource_consumption,
    is_resource_generation,
    is_resource_storage,
)
from game.simulation.physics_constants import (
    DEFAULT_MAX_MASS,
    K_TURN,
    compute_acceleration,
    compute_max_speed,
)

if TYPE_CHECKING:
    from game.core.resources import ResourceCatalog
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def _get_planetary_resource_ids(resource_catalog: "ResourceCatalog") -> List[str]:
    """Return planetary resource IDs from the injected catalog."""
    return [d.id for d in resource_catalog.by_display_group("planetary")]


class ShipStatsCalculator:
    """Coordinator for ship-stat calculation.

    Owns phase ordering and a small amount of cross-cutting state (the
    planetary resource id cache). All per-domain logic delegates to
    ``stat_contributors/``.
    """

    def __init__(
        self,
        vehicle_classes: dict,
        *,
        resource_catalog: Optional["ResourceCatalog"] = None,
        planetary_resource_ids: Optional[List[str]] = None,
    ):
        self.vehicle_classes = vehicle_classes
        self._resource_catalog = resource_catalog
        if planetary_resource_ids is not None:
            self._planetary_resource_ids = list(planetary_resource_ids)
        else:
            self._planetary_resource_ids = None  # Lazy: resolved on first calculate()

    def _get_or_resolve_planetary_ids(self) -> list:
        """Return cached planetary resource IDs, resolving lazily from catalog."""
        if self._planetary_resource_ids is not None:
            return self._planetary_resource_ids
        if self._resource_catalog is None:
            raise TypeError(
                "ShipStatsCalculator requires either resource_catalog or "
                "planetary_resource_ids to call calculate()"
            )
        self._planetary_resource_ids = _get_planetary_resource_ids(self._resource_catalog)
        return self._planetary_resource_ids

    def calculate(self, ship: "Ship") -> None:
        """Recalculate all derived stats for ``ship`` from its components and class."""
        self._reset_base_state(ship)

        # Phase 1: Damage Check & Resource Supply Gathering
        component_pool, available_crew, available_life_support = (
            self._phase_damage_check_and_supply(ship)
        )

        # Phase 2: Resource Allocation (Crew & Life Support)
        _cmd.allocate_crew_and_life_support(
            ship,
            component_pool,
            available_crew,
            available_life_support,
            self.vehicle_classes,
        )

        # Phase 3: Stats Aggregation (Active Components Only)
        self._phase_stats_aggregation(ship, component_pool)

        # Phase 4: Physics & Limits
        self._phase_physics_and_limits(ship)

        # Phase 5: To-Hit & Electronic Warfare Stats
        self._phase_sensor_defense_scores(ship, component_pool)

    # ------------------------------------------------------------------ #
    # Phase 1: damage check + supply
    # ------------------------------------------------------------------ #

    def _reset_base_state(self, ship: "Ship") -> None:
        """Zero out every field the calculator will rewrite this pass."""
        ship.current_mass = 0
        ship.layer_status = {}
        ship.mass_limits_ok = True
        ship.drag = PhysicsConfig.DEFAULT_LINEAR_DRAG

        # Mass per layer (mass never changes due to damage; dead weight remains)
        for _, layer_data in ship.layers.items():
            l_mass = sum(c.mass for c in layer_data.components)
            layer_data.mass = l_mass
            ship.current_mass += l_mass

        ship.mass = ship.current_mass + ship.base_mass
        all_components = ship.get_all_components()
        ship.max_hp = sum(c.max_hp for c in all_components)
        ship.hp = sum(c.current_hp for c in all_components)

        # Resource costs aggregation — pre-fill with planetary resource ids
        ship.construction_cost = {}
        for res in self._get_or_resolve_planetary_ids():
            ship.construction_cost[res] = 0

        for comp in all_components:
            for res, amount in comp.get_resource_cost().items():
                if res in ship.construction_cost:
                    ship.construction_cost[res] += amount

        # Base stats reset
        ship.total_thrust = 0
        ship.total_strategic_movement = 0
        ship.turn_speed = 0
        ship.resources.reset_stats()

        ship.max_shields = 0
        ship.shield_regen_rate = 0
        ship.shield_regen_cost = 0
        ship.repair_rate = 0
        if LayerType.ARMOR in ship.layers:
            ship.layers[LayerType.ARMOR].max_hp_pool = 0

        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.total_maneuver_points = 0

        ship.fighter_capacity = 0
        ship.fighters_per_wave = 0
        ship.fighter_size_cap = 0
        ship.launch_cycle = 0

    def _phase_damage_check_and_supply(
        self, ship: "Ship"
    ) -> Tuple[List["Component"], int, int]:
        """Phase 1: Reset component status, mark damaged, gather crew/LS supply."""
        available_crew = 0
        available_life_support = 0
        component_pool: List["Component"] = []

        for _layer_type, comp in ship.iter_components():
            comp.is_active = True
            comp.status = ComponentStatus.ACTIVE
            comp.mark_hp_cache_dirty()  # PROJ-49

            # Damage threshold (armor uses HP pool, not per-component threshold)
            # PROJ-367 Phase 1 (closes EXT-07): Armor is consumed via
            # `has_ability` (marker idiom) — no typed class needed.
            if not comp.has_ability("Armor"):
                if comp.hp_ratio <= comp.damage_threshold:
                    comp.is_active = False
                    comp.status = ComponentStatus.DAMAGED

            # Dead armor (0 hp) is inactive
            if comp.has_ability("Armor") and comp.current_hp <= 0:
                comp.is_active = False
                comp.status = ComponentStatus.DAMAGED

            # Gather supply from FUNCTIONAL components
            if comp.is_active:
                for ab in comp.get_abilities("CrewCapacity"):
                    available_crew += ab.amount
                for ab in comp.get_abilities("LifeSupportCapacity"):
                    available_life_support += ab.amount

            component_pool.append(comp)

        return component_pool, available_crew, available_life_support

    # ------------------------------------------------------------------ #
    # Phase 3: stats aggregation (delegates per-domain aggregation)
    # ------------------------------------------------------------------ #

    def _phase_stats_aggregation(
        self, ship: "Ship", component_pool: List["Component"]
    ) -> None:
        """Phase 3: Aggregate stats from active components.

        PROJ-367 Phase 3: ``acc`` is a typed ``StatAccumulator`` dataclass
        (10 scalar fields + 4 named map fields = 14 total). Misspelled
        scalar/map field names raise ``AttributeError`` at runtime
        (``slots=True`` semantics). Dynamic resource keys live INSIDE
        ``acc.resource_storage`` / ``acc.resource_generation`` map fields —
        any resource type from data files works without code changes.
        """
        acc = StatAccumulator()

        for comp in component_pool:
            if not comp.is_active:
                continue

            # Resource storage is always aggregated (batteries provide capacity
            # even when consumption isn't met — they have no consumption).
            self._aggregate_resource_abilities(comp, acc)
            self._aggregate_cargo_and_pod_abilities(comp, acc)

            # All other stats require the component to be operational.
            if not comp.is_operational:
                continue

            # PROJ-367 Phase 2: single unified pipeline — built-in contributors
            # are seeded as default registry entries with phase_order in
            # 10..50; modder entries default to phase_order=99 so they fire
            # after non-replaced built-ins. ``iter_for(comp)`` yields all
            # entries the component qualifies for (via has_ability) in
            # phase_order ascending, then registration order.
            for entry in STAT_CONTRIBUTOR_REGISTRY.iter_for(comp):
                entry.contributor(ship, comp, acc)

        self._apply_aggregated_stats(ship, acc)

    def _aggregate_resource_abilities(
        self, comp: "Component", acc: StatAccumulator
    ) -> None:
        """Aggregate ResourceStorage, ResourceGeneration, ResourceConsumption.

        PROJ-367 Phase 3: writes into ``acc.resource_storage`` /
        ``acc.resource_generation`` map fields (was synthetic
        ``max_<resource>`` / ``gen_<resource>`` keys on the legacy dict).
        Discovers resource types dynamically from component abilities so any
        resource defined in data files works without code changes. Also
        registers resources from consumption abilities (with 0 capacity) so
        the ResourceRegistry knows about all resource types even when no
        storage is present.
        """
        for ability in comp.ability_instances:
            if is_resource_storage(ability):
                rt = ability.resource_type
                acc.resource_storage[rt] = (
                    acc.resource_storage.get(rt, 0) + ability.max_amount
                )
            elif is_resource_generation(ability):
                rt = ability.resource_type
                acc.resource_generation[rt] = (
                    acc.resource_generation.get(rt, 0) + ability.rate
                )
            elif is_resource_consumption(ability):
                rt = ability.resource_type
                # Ensure resource_storage has an entry for consumed resources
                # so the registry sees them even with zero storage.
                if rt not in acc.resource_storage:
                    acc.resource_storage[rt] = 0
                if getattr(ability, "trigger", "") == "warp_jump":
                    acc.warp_resource_costs[rt] = (
                        acc.warp_resource_costs.get(rt, 0) + ability.amount
                    )

    def _aggregate_cargo_and_pod_abilities(
        self, comp: "Component", acc: StatAccumulator
    ) -> None:
        """Aggregate CargoStorage and PodStorage abilities."""
        for ab in comp.get_abilities("CargoStorage"):
            cargo_type = getattr(ab, "cargo_type", "generic")
            capacity = getattr(ab, "capacity", 0.0)
            if capacity > 0:
                acc.cargo_storage[cargo_type] = (
                    acc.cargo_storage.get(cargo_type, 0) + capacity
                )

        # PROJ-367 Phase 1 (closes EXT-07): PodStorage is now a typed class
        # (`PodStorageAbility.capacity_mass: float`). Sum across instances
        # on the same component (legacy semantics ignored 0/empty entries).
        for ab in comp.get_abilities("PodStorage"):
            capacity = getattr(ab, "capacity_mass", 0.0)
            if capacity > 0:
                acc.pod_storage_mass += capacity

    def _apply_aggregated_stats(self, ship: "Ship", acc: StatAccumulator) -> None:
        """Atomic application of accumulated totals to ship.

        PROJ-367 Phase 3: reads from typed ``StatAccumulator`` fields. Resource
        registration uses the dedicated ``resource_storage`` / ``resource_generation``
        map fields (no more "starts with max_/gen_" string-prefix heuristic).
        """
        # Resource storage + generation registration (data-driven keys live
        # in the dedicated map fields).
        for resource_type, amount in acc.resource_storage.items():
            ship.resources.register_storage(resource_type, amount)
        for resource_type, rate in acc.resource_generation.items():
            ship.resources.register_generation(resource_type, rate)

        ship.total_thrust = acc.thrust
        ship.total_strategic_movement = acc.strategic_movement
        ship.turn_speed = acc.turn_speed
        ship.total_maneuver_points = acc.maneuver_points
        ship.max_shields = acc.max_shields

        # PROJ-271 Phase 1: flat shield bonus from external_stats acts as a
        # virtual extra shield component. Pipeline order (base + flat) × mult:
        # real shield components already have external shield_capacity_mult
        # applied via ShieldProjection.recalculate(); we apply the same
        # multiplier to the flat bonus so both compose identically.
        # isinstance(dict) guard matches abilities/base.py:281 — test Mocks
        # often have external_stats as a bare MagicMock, not a real dict.
        external_stats = getattr(ship, "external_stats", None)
        if isinstance(external_stats, dict):
            flat_shield_bonus = external_stats.get("shield_bonus_add", 0.0)
            if flat_shield_bonus:
                # PROJ-272 Phase 6: reverted PROJ-271 Phase 12.1's
                # `capacity_mult` read. No current aura populates
                # `capacity_mult` — reading it from external_stats was a
                # latent double-multiply if any future aura would populate it.
                shield_cap_mult = external_stats.get("shield_capacity_mult", 1.0)
                ship.max_shields += flat_shield_bonus * shield_cap_mult

        ship.shield_regen_rate = acc.shield_regen
        ship.shield_regen_cost = acc.shield_cost
        ship.warp_max_tonnage = acc.warp_max_tonnage
        ship.warp_energy_cost = acc.warp_energy_cost
        ship.cargo_storage = acc.cargo_storage
        ship.pod_storage_mass = acc.pod_storage_mass
        ship.warp_resource_costs = acc.warp_resource_costs

    # ------------------------------------------------------------------ #
    # Phase 4: physics & limits
    # ------------------------------------------------------------------ #

    def _phase_physics_and_limits(self, ship: "Ship") -> None:
        """Apply inverse-mass scaling for physics and check mass budget."""
        if ship.mass > 0:
            ship.acceleration_rate = compute_acceleration(ship.total_thrust, ship.mass)
            raw_turn_speed = ship.turn_speed
            ship.turn_speed = (raw_turn_speed * K_TURN) / (ship.mass ** 1.5)
            ship.max_speed = (
                compute_max_speed(ship.total_thrust, ship.mass)
                if ship.total_thrust > 0
                else 0
            )
        else:
            ship.acceleration_rate = 0
            ship.max_speed = 0

        self._check_mass_limits(ship)

        # Radius
        base_radius = PhysicsConfig.DEFAULT_BASE_RADIUS
        ref_mass = PhysicsConfig.REFERENCE_MASS
        actual_mass = max(ship.mass, 100)
        ratio = actual_mass / ref_mass
        ship.radius = base_radius * (ratio ** (1 / 3.0))

    def _check_mass_limits(self, ship: "Ship") -> None:
        ship.mass_limits_ok = True
        ship.max_mass_budget = DEFAULT_MAX_MASS

        if ship.ship_class in self.vehicle_classes:
            ship.max_mass_budget = self.vehicle_classes[ship.ship_class].get(
                "max_mass", DEFAULT_MAX_MASS
            )

        for layer_type, layer_data in ship.layers.items():
            limit_ratio = layer_data.max_mass_pct
            ratio = layer_data.mass / ship.max_mass_budget
            is_ok = ratio <= limit_ratio
            ship.layer_status[layer_type] = {
                "mass": layer_data.mass,
                "ratio": ratio,
                "limit": limit_ratio,
                "ok": is_ok,
            }
            if not is_ok:
                ship.mass_limits_ok = False

        if ship.mass > ship.max_mass_budget:
            ship.mass_limits_ok = False

    # ------------------------------------------------------------------ #
    # Phase 5: sensor / defense scores + resource init + endurance
    # ------------------------------------------------------------------ #

    def _phase_sensor_defense_scores(
        self, ship: "Ship", component_pool: List["Component"]
    ) -> None:
        """Phase 5: defense score, repair, armor totals, ammo gen, resource init."""
        diameter = ship.radius * 2

        # Size score: baseline diameter 80 (mass ~1k) = 0.0
        # Formula: -2.5 * log10(diameter / 80); guard against log(0)
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        # Maneuver score
        maneuver_score = math.sqrt(
            (ship.acceleration_rate / 20.0) + (ship.turn_speed / 360.0)
        )

        # ECM (defense) + sensor (offense) scores via weapons contributor.
        # Returns the ECM term so we can compose total_defense_score here.
        ecm_score = _wep.aggregate_targeting_scores(ship, component_pool)

        ship.total_defense_score = size_score + maneuver_score + ecm_score

        # Armor abilities + repair via defense contributor.
        _def.apply_armor_and_repair_scores(ship, component_pool)

        # Ammo generation passthrough — the resource registry already has the rate.
        ammo_res = ship.resources.get_resource("ammo")
        ship.ammo_gen_rate = ammo_res.regen_rate if ammo_res else 0.0

        # Armor pool init (first-time fill).
        _def.init_armor_pool(ship)

        # Resources + combat endurance.
        self._initialize_resources(ship)
        calculate_combat_endurance(ship, component_pool)

    def _initialize_resources(self, ship: "Ship") -> None:
        """Initialize or update resource values after stats aggregation.

        On first load, fills all resources to max capacity. On subsequent
        recalculations, adds capacity deltas (preserves current usage).
        Handles any resource type dynamically — no hardcoded fuel/energy/ammo.
        """
        prev_max = ship._prev_max_resources
        prev_max_shields = ship._prev_max_shields

        if not ship._resources_initialized:
            for name in ship.resources.get_resource_names():
                max_val = ship.resources.get_max_value(name)
                if max_val > 0:
                    ship.resources.set_value(name, max_val)
            if ship.max_shields > 0:
                ship.current_shields = ship.max_shields
            ship._resources_initialized = True
        else:
            for name in ship.resources.get_resource_names():
                curr_max = ship.resources.get_max_value(name)
                prev = prev_max.get(name, 0)
                if curr_max > prev:
                    ship.resources.modify_value(name, curr_max - prev)
            if ship.max_shields > prev_max_shields:
                ship.current_shields += ship.max_shields - prev_max_shields
            if ship.current_shields > ship.max_shields:
                ship.current_shields = ship.max_shields

        ship._prev_max_resources = {
            name: ship.resources.get_max_value(name)
            for name in ship.resources.get_resource_names()
        }
        ship._prev_max_shields = ship.max_shields

    # ------------------------------------------------------------------ #
    # Public passthroughs (legacy API surface)
    # ------------------------------------------------------------------ #

    def calculate_ability_totals(self, components: List["Component"]) -> Dict[str, Any]:
        """Total values for all abilities. Delegates to ``ability_aggregator``."""
        return calculate_ability_totals(components)
