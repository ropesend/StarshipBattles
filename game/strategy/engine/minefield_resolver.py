"""MinefieldResolver — PROJ-FMS-B Phases 1 + 2.

Resolves strategic-entry damage from enemy ``mine_group`` Fleets when
an opposing fleet moves into a mined hex. Runs in the turn-engine
movement phase BEFORE :class:`ConflictResolutionEngine` so a fleet
destroyed by mines never reaches the conflict dispatch.

Math (per the shared design doc):

    p_trigger      = sensitivity * sigmoid(k_size * size_score(ship)
                                              - k_eva * maneuver_score(ship)
                                              - bias)
    P_trigger_pass = 1 - (1 - p_trigger) ** N         # N = warhead mine count

On trigger, one warhead mine is sampled uniformly and its damage is
applied to the entering ship. Mine inventory is decremented as warheads
are consumed.

Per the design:
- ``P_trigger_pass < 1`` for any finite N (asymptote — never 100%).
- ``P_trigger_pass > 0`` when N >= 1 and p_trigger > 0.
- Friendly fleets never trigger.

PROJ-FMS-B Phase 2 wires the laserhead pass in :meth:`_resolve_laserhead_pass`.
"""
from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from game.strategy.engine.minefield_balance import (
    MinefieldBalance,
    load_minefield_balance,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.ship_instance import ShipInstance


@dataclass
class MineDetonationEvent:
    """Structured event emitted by the resolver for each detonation."""

    mine_group_id: Any
    mine_owner_id: int
    target_ship_id: str
    target_fleet_id: Any
    damage: float
    pass_kind: str  # "warhead" or "laserhead"
    hit: bool = True


@dataclass
class MinefieldResolutionResult:
    """Aggregate result for a single fleet's traversal of mined hexes."""

    detonations: List[MineDetonationEvent] = field(default_factory=list)
    consumed_mine_ids: List[str] = field(default_factory=list)
    destroyed_ship_ids: List[str] = field(default_factory=list)
    removed_mine_groups: List[Any] = field(default_factory=list)

    @property
    def total_damage_applied(self) -> float:
        return sum(d.damage for d in self.detonations)


# ---------------------------------------------------------------------------
# Helpers — ship score derivation from a ShipInstance.
# ---------------------------------------------------------------------------


def _compute_size_score(diameter: float) -> float:
    """Reproduce the size_score formula at ship_stats.py:443.

    ``-2.5 * log10(diameter / 80)``, clamped against log(0).
    """
    d_ratio = max(0.1, diameter / 80.0)
    return -2.5 * math.log10(d_ratio)


def _compute_maneuver_score(acceleration_rate: float, turn_speed: float) -> float:
    """Reproduce the maneuver_score formula at ship_stats.py:446."""
    return math.sqrt(
        (max(0.0, acceleration_rate) / 20.0) + (max(0.0, turn_speed) / 360.0)
    )


def _get_ship_scores(ship: "ShipInstance") -> Tuple[float, float]:
    """Return ``(size_score, maneuver_score)`` for a strategy ShipInstance.

    Reads from the ship's ``get_calculated_stats()`` cache, which is the
    same source of truth as ``Ship.recalculate_stats``. Falls back to
    conservative defaults if the cache lookup fails — the resolver
    treats the ship as "average destroyer" rather than crashing.
    """
    try:
        stats = ship.get_calculated_stats()
    except Exception as exc:  # Intentional broad catch: stats computation can fail on partial/test ShipInstances; fall back to mid-range so the resolver still produces a non-zero p_trigger.
        logger.warning(
            "MinefieldResolver: stats lookup failed for ship %s (%s); using defaults",
            getattr(ship, "instance_id", "?"),
            exc,
        )
        return (0.0, 1.0)

    # Diameter: stats may expose 'radius' or 'diameter'. Fall back to 80
    # (the size_score baseline) so missing data gives size_score == 0.
    radius = stats.get("radius")
    diameter = stats.get("diameter")
    if diameter is None and radius is not None:
        diameter = float(radius) * 2.0
    if diameter is None:
        diameter = 80.0

    accel = float(stats.get("acceleration_rate", 0.0) or 0.0)
    turn = float(stats.get("turn_speed", 0.0) or 0.0)

    return (_compute_size_score(float(diameter)), _compute_maneuver_score(accel, turn))


def _sigmoid(x: float) -> float:
    """Numerically-stable sigmoid (clamped exponent)."""
    clamped = max(-20.0, min(20.0, x))
    try:
        return 1.0 / (1.0 + math.exp(-clamped))
    except OverflowError:
        return 0.0 if clamped < 0 else 1.0


# ---------------------------------------------------------------------------
# Mine inventory helpers
# ---------------------------------------------------------------------------


def _iter_mines(mine_group: "Fleet") -> List[Dict[str, Any]]:
    """Return the mine entries on a mine_group Fleet.

    Mines on a ``mine_group`` live on its first ship as
    ``CarriedVehicle``-shaped entries in ``ship.carried_items`` (per the
    PROJ-FMS-A Phase 3 substrate). The mine_group's ``ships`` list holds
    a single carrier instance that doubles as the mine container — this
    keeps the existing serializer/DTO surface usable.
    """
    if not mine_group.ships:
        return []
    carrier = mine_group.ships[0]
    return list(carrier.carried_items)


def _set_mines(mine_group: "Fleet", mines: List[Dict[str, Any]]) -> None:
    """Replace the carried_items mine list on the mine_group's carrier."""
    if not mine_group.ships:
        return
    mine_group.ships[0].carried_items = mines


def _mine_has_warhead(mine_dict: Dict[str, Any]) -> bool:
    """Return True if the mine carries at least one Warhead component."""
    return _get_warhead_damage(mine_dict) > 0.0


def _get_warhead_damage(mine_dict: Dict[str, Any]) -> float:
    """Extract total warhead damage from a CarriedVehicle dict.

    Walks the mine's ``design_data.layers`` looking for components with
    a ``Warhead`` ability and sums their damage. Used by the strategic
    resolver to apply damage on trigger.
    """
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    total = 0.0
    for _layer_name, layer_obj in layers.items():
        components = layer_obj.get("components") if isinstance(layer_obj, dict) else None
        if not components:
            continue
        for comp in components:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            warhead = abilities.get("Warhead")
            if warhead is None:
                continue
            if isinstance(warhead, dict):
                total += float(warhead.get("damage", 0.0))
            elif isinstance(warhead, (int, float)):
                total += float(warhead)
    return total


def _mine_has_laserhead(mine_dict: Dict[str, Any]) -> bool:
    """Return True if the mine carries at least one Laserhead ability."""
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    for _layer_name, layer_obj in layers.items():
        components = layer_obj.get("components") if isinstance(layer_obj, dict) else None
        if not components:
            continue
        for comp in components:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            if "Laserhead" in abilities:
                return True
    return False


def _get_laserhead_attrs(mine_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the first Laserhead ability dict on a mine, or None."""
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    for _layer_name, layer_obj in layers.items():
        components = layer_obj.get("components") if isinstance(layer_obj, dict) else None
        if not components:
            continue
        for comp in components:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            lh = abilities.get("Laserhead")
            if lh is None:
                continue
            if isinstance(lh, dict):
                return dict(lh)
            elif isinstance(lh, (int, float)):
                return {"damage": float(lh)}
    return None


# ---------------------------------------------------------------------------
# Strategic damage application
# ---------------------------------------------------------------------------


def _apply_strategic_damage(
    ship: "ShipInstance",
    damage: float,
    registries: Optional["GameRegistries"] = None,
) -> float:
    """Apply mine damage to a strategy-layer ShipInstance.

    Two pathways are supported:

    1. **Damage-pipeline pathway** (preferred, when ``registries`` is
       provided): materialise the ShipInstance into a transient sim
       :class:`Ship` via ``ShipInstanceBridge.to_ship()``, route the
       damage through :class:`DamageCalculator.apply_damage` (the same
       shield/armor/hull pipeline used in tactical combat), then write
       the resulting HP back. This honours shields, emissive armor,
       SRA, and the hull-layer distribution the design specifies
       (per ``damage_calculator.py:44-84``).
    2. **Fallback pathway** (no registries / pipeline failed):
       decrement ``ship.current_hp`` directly, mirroring
       :mod:`environmental_hazard_engine`'s pragmatic-strategy-layer
       pattern. Used only when the damage pipeline cannot be invoked
       cleanly (e.g. test ShipInstances without full design data).

    Returns:
        The actual damage applied (post-shield/post-armor consumption).
    """
    try:
        stats = ship.get_calculated_stats()
        max_hp = float(stats.get("max_hp", 100))
    except Exception:  # Intentional broad catch: stats lookup can fail on minimal test ShipInstances; fall back to the documented default.
        max_hp = 100.0

    current_hp_before = float(
        ship.current_hp if ship.current_hp is not None else max_hp
    )

    # Try the damage pipeline pathway when registries are available.
    if registries is not None and getattr(ship, "design_data", None):
        try:
            from game.simulation.combat.damage_calculator import DamageCalculator

            sim_ship = ship.to_ship(
                position=(0.0, 0.0), team_id=0, registries=registries,
            )
            DamageCalculator().apply_damage(sim_ship, float(damage))
            # Write resulting HP back. ``sim_ship.hp`` reflects shields +
            # armor absorption, so the strategic-layer current_hp gets
            # the same value the tactical layer would see post-trigger.
            new_hp = float(getattr(sim_ship, "hp", current_hp_before))
            new_hp = max(0.0, min(max_hp, new_hp))
            actual = max(0.0, current_hp_before - new_hp)
            ship.current_hp = int(new_hp) if new_hp == int(new_hp) else new_hp
            if new_hp <= 0.0:
                ship.is_alive = False
            ship.invalidate_stats_cache()
            return actual
        except Exception as exc:  # Intentional broad catch: damage pipeline can fail on partial / test designs; fall through to direct-HP decrement so a single broken ship doesn't break the whole turn.
            logger.warning(
                "MinefieldResolver: damage pipeline failed for ship %s (%s); "
                "falling back to direct HP decrement",
                getattr(ship, "instance_id", "?"),
                exc,
            )

    # Fallback pathway: direct HP decrement (no shields/armor at this layer).
    new_hp = max(0.0, current_hp_before - float(damage))
    actual = current_hp_before - new_hp
    ship.current_hp = int(new_hp) if new_hp == int(new_hp) else new_hp
    if new_hp <= 0.0:
        ship.is_alive = False
    return actual


# ---------------------------------------------------------------------------
# Public resolver
# ---------------------------------------------------------------------------


class MinefieldResolver:
    """Resolves strategic minefield-entry damage for a single fleet move.

    Construction takes an optional :class:`MinefieldBalance` and an
    optional :class:`random.Random` for deterministic tests; both
    default to module-level singletons / fresh RNG.
    """

    def __init__(
        self,
        balance: Optional[MinefieldBalance] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self._balance = balance if balance is not None else load_minefield_balance()
        self._rng = rng if rng is not None else random.Random()

    # ------------------------------------------------------------------
    # p_trigger / P_trigger_pass math
    # ------------------------------------------------------------------

    def compute_p_trigger(
        self, ship: "ShipInstance", sensitivity_label: str
    ) -> float:
        """Per-mine warhead trigger chance vs ``ship``."""
        size_score, maneuver_score = _get_ship_scores(ship)
        return self._compute_p_trigger_from_scores(
            size_score, maneuver_score, sensitivity_label
        )

    def _compute_p_trigger_from_scores(
        self,
        size_score: float,
        maneuver_score: float,
        sensitivity_label: str,
    ) -> float:
        # NOTE: ``size_score`` from ship_stats.py is a DEFENSE term —
        # bigger ships have a more-negative score because they are
        # easier to hit. The mine-trigger formula in the shared design
        # wants "bigger ship => higher p_trigger", so we use the
        # *negated* size_score (call it the trigger-side "bulk" score).
        # The bigger the diameter relative to the 80-baseline, the
        # larger this term, and the larger ``p_trigger``.
        wh = self._balance.warhead_trigger
        bulk_score = -size_score
        x = (wh.k_size * bulk_score) - (wh.k_eva * maneuver_score) - wh.bias
        base = _sigmoid(x)
        sens = self._balance.sensitivity_factor(sensitivity_label)
        # Cap at <1.0 so the asymptote invariant holds even when
        # sensitivity > 1.0.
        return max(0.0, min(0.9999, sens * base))

    @staticmethod
    def compute_p_trigger_pass(p_trigger: float, n_warheads: int) -> float:
        """Per-pass trigger chance across N warhead mines.

        ``P_pass = 1 - (1 - p_trigger) ** N``, but evaluated in
        log-space to keep the asymptote invariant numerically: at very
        large N, ``(1 - p) ** N`` underflows to 0.0 in IEEE-754, which
        would violate the "never 100%" invariant. We compute
        ``exp(N * log(1 - p))`` with an explicit floor on the result so
        ``P_pass`` stays strictly less than 1.0 for any finite N.
        """
        if n_warheads <= 0 or p_trigger <= 0.0:
            return 0.0
        p = max(0.0, min(0.9999, float(p_trigger)))
        # log-space evaluation to keep precision past the 1e-16 mark.
        try:
            survive = math.exp(int(n_warheads) * math.log(1.0 - p))
        except (ValueError, OverflowError):
            survive = 0.0
        # Floor at the smallest non-zero double so 1 - survive stays
        # strictly below 1.0. This preserves the asymptote invariant.
        survive = max(survive, 2.2250738585072014e-308)
        return min(0.99999999999999, 1.0 - survive)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def resolve_minefield_entry(
        self,
        galaxy: Any,
        empires: List[Any],
        fleet: "Fleet",
        registries: Optional["GameRegistries"] = None,
    ) -> MinefieldResolutionResult:
        """Resolve all enemy mine_groups at ``fleet.location`` against ``fleet``.

        Args:
            galaxy: Optional galaxy reference (kept for future hooks; not
                currently used).
            empires: List of all empires — used to enumerate enemy
                ``mine_group`` Fleets at the same hex.
            fleet: The entering fleet (must have a ``location``, ``ships``,
                and ``owner_id``).
            registries: Optional registries for stats calculation.

        Returns:
            :class:`MinefieldResolutionResult` summarising detonations,
            damage applied, ships destroyed, and mine_groups removed.
        """
        result = MinefieldResolutionResult()

        if fleet is None or not getattr(fleet, "ships", None):
            return result

        # Collect enemy mine_groups at the hex.
        mine_groups: List[Tuple[Any, "Fleet"]] = []
        for empire in empires:
            if getattr(empire, "id", None) == getattr(fleet, "owner_id", None):
                continue
            for other in getattr(empire, "fleets", []) or []:
                if getattr(other, "group_kind", "fleet") != "mine_group":
                    continue
                if other.location != fleet.location:
                    continue
                mine_groups.append((empire, other))

        if not mine_groups:
            return result

        # Process per-ship in fleet-entry order. Per the design (and the
        # decision logged in ``decisions.md``), ordering is per-ship
        # interleaved: warhead pass → laserhead pass → next ship.
        for ship in list(fleet.ships):
            if not getattr(ship, "is_alive", True):
                continue
            for owner_empire, mine_group in mine_groups:
                # Re-check liveness of the mine_group each iteration —
                # an earlier ship may have removed it.
                if mine_group not in (owner_empire.fleets or []):
                    continue
                self._resolve_warhead_pass(
                    ship, mine_group, fleet, owner_empire, registries, result
                )
                if not ship.is_alive:
                    break
                self._resolve_laserhead_pass(
                    ship, mine_group, fleet, owner_empire, registries, result
                )

            if not ship.is_alive and ship.instance_id not in result.destroyed_ship_ids:
                result.destroyed_ship_ids.append(ship.instance_id)

        # Sweep empty mine_groups out of their empire's fleet list.
        for owner_empire, mine_group in mine_groups:
            if not _iter_mines(mine_group):
                if mine_group in (owner_empire.fleets or []):
                    owner_empire.fleets.remove(mine_group)
                    result.removed_mine_groups.append(mine_group.id)

        return result

    # ------------------------------------------------------------------
    # Warhead pass
    # ------------------------------------------------------------------

    def _resolve_warhead_pass(
        self,
        ship: "ShipInstance",
        mine_group: "Fleet",
        attacking_fleet: "Fleet",
        owner_empire: Any,
        registries: Optional["GameRegistries"],
        result: MinefieldResolutionResult,
    ) -> None:
        """Run the warhead-pass roll for ``ship`` against ``mine_group``."""
        warhead_mines = [m for m in _iter_mines(mine_group) if _mine_has_warhead(m)]
        n = len(warhead_mines)
        if n == 0:
            return

        sensitivity = getattr(mine_group, "sensitivity", "MED")
        p_trigger = self.compute_p_trigger(ship, sensitivity)
        p_pass = self.compute_p_trigger_pass(p_trigger, n)

        if p_pass <= 0.0:
            return

        roll = self._rng.random()
        if roll >= p_pass:
            return

        # Trigger! Sample one warhead mine uniformly and detonate it.
        idx = self._rng.randrange(n)
        chosen = warhead_mines[idx]
        damage = _get_warhead_damage(chosen)
        actual_damage = _apply_strategic_damage(ship, damage, registries=registries)
        result.detonations.append(
            MineDetonationEvent(
                mine_group_id=mine_group.id,
                mine_owner_id=getattr(owner_empire, "id", -1),
                target_ship_id=ship.instance_id,
                target_fleet_id=attacking_fleet.id,
                damage=actual_damage,
                pass_kind="warhead",
                hit=True,
            )
        )

        # Remove the chosen mine from the carrier's inventory.
        mines = _iter_mines(mine_group)
        # Match by identity — design_id + index keeps mixed-design groups stable.
        mine_id = chosen.get("design_id", "")
        result.consumed_mine_ids.append(str(mine_id))
        # Remove the first matching entry (entries are equal-shape dicts).
        for i, m in enumerate(mines):
            if m is chosen:
                mines.pop(i)
                break
        _set_mines(mine_group, mines)

    # ------------------------------------------------------------------
    # Laserhead pass — Phase 2
    # ------------------------------------------------------------------

    def _resolve_laserhead_pass(
        self,
        ship: "ShipInstance",
        mine_group: "Fleet",
        attacking_fleet: "Fleet",
        owner_empire: Any,
        registries: Optional["GameRegistries"],
        result: MinefieldResolutionResult,
    ) -> None:
        """Phase 2: run the laserhead pass for ``ship`` against ``mine_group``."""
        laserhead_mines = [
            m for m in _iter_mines(mine_group) if _mine_has_laserhead(m)
        ]
        if not laserhead_mines:
            return

        threshold = float(
            getattr(mine_group, "expected_hit_chance_threshold", 0.30)
        )

        # Compute defense penalty from the target's total_defense_score
        # via the cached stats. Strategic layer does not have a live Ship,
        # so we approximate using the same scoring formulas the sim uses.
        try:
            stats = ship.get_calculated_stats()
            defense_score = float(stats.get("total_defense_score", 0.0) or 0.0)
        except Exception:  # Intentional broad catch: stats may be unavailable in test fixtures; fall back to 0.0.
            defense_score = 0.0

        for mine in list(laserhead_mines):
            lh_attrs = _get_laserhead_attrs(mine)
            if lh_attrs is None:
                continue
            # Pull beam params (defaults match BeamWeaponAbility shape).
            base_accuracy = float(lh_attrs.get("base_accuracy", 1.0))
            accuracy_falloff = float(lh_attrs.get("accuracy_falloff", 0.001))
            beam_range = float(lh_attrs.get("range", 0.0))
            damage = float(lh_attrs.get("damage", 0.0))

            # Strategic-layer assumption: assume mines fire at half their
            # maximum range (the average distance a moving ship sees).
            # This keeps the gate calibration honest without an explicit
            # position model at the strategic layer.
            distance = beam_range * 0.5 if beam_range > 0.0 else 0.0
            range_penalty = accuracy_falloff * distance

            # Sensor accuracy bonus from SmallTargetingSensor (and any
            # other ToHitAttackModifier on the mine) — fold into
            # base_accuracy.
            sensor_bonus = _mine_sensor_bonus(mine)
            net_score = (base_accuracy + sensor_bonus) - (range_penalty + defense_score)
            expected_hit_chance = _sigmoid(net_score)

            if expected_hit_chance < threshold:
                # Skip silently — do NOT consume the laserhead.
                continue

            # Threshold passed: roll the standard beam hit roll.
            roll = self._rng.random()
            hit = roll < expected_hit_chance
            applied = 0.0
            if hit:
                applied = _apply_strategic_damage(ship, damage, registries=registries)
            result.detonations.append(
                MineDetonationEvent(
                    mine_group_id=mine_group.id,
                    mine_owner_id=getattr(owner_empire, "id", -1),
                    target_ship_id=ship.instance_id,
                    target_fleet_id=attacking_fleet.id,
                    damage=applied,
                    pass_kind="laserhead",
                    hit=hit,
                )
            )

            # Consume the laserhead regardless of hit/miss (consume_on_fire).
            mines = _iter_mines(mine_group)
            for i, m in enumerate(mines):
                if m is mine:
                    mines.pop(i)
                    break
            _set_mines(mine_group, mines)
            result.consumed_mine_ids.append(str(mine.get("design_id", "")))

            if not ship.is_alive:
                return


def _mine_sensor_bonus(mine_dict: Dict[str, Any]) -> float:
    """Sum of ``ToHitAttackModifier`` bonuses from mine components.

    The PROJ-FMS-A ``SmallTargetingSensor`` carries a
    ``ToHitAttackModifier`` ability with an ``add`` operation on the
    accuracy stat. The strategic resolver does not run the full
    stat-aggregator, so we approximate by walking the mine's design
    and summing the modifier values.
    """
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    total = 0.0
    for _name, layer_obj in layers.items():
        components = layer_obj.get("components") if isinstance(layer_obj, dict) else None
        if not components:
            continue
        for comp in components:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            mod = abilities.get("ToHitAttackModifier")
            if mod is None:
                continue
            if isinstance(mod, dict):
                total += float(mod.get("value", mod.get("amount", 0.0)) or 0.0)
            elif isinstance(mod, (int, float)):
                total += float(mod)
    return total


# ---------------------------------------------------------------------------
# Module-level convenience entry point
# ---------------------------------------------------------------------------


def resolve_minefield_entry(
    galaxy: Any,
    empires: List[Any],
    fleet: "Fleet",
    registries: Optional["GameRegistries"] = None,
    balance: Optional[MinefieldBalance] = None,
    rng: Optional[random.Random] = None,
) -> MinefieldResolutionResult:
    """Module-level helper for the turn-engine hook.

    Builds a transient :class:`MinefieldResolver` and runs one entry
    resolution. Tests can pass an explicit ``rng`` for determinism.
    """
    resolver = MinefieldResolver(balance=balance, rng=rng)
    return resolver.resolve_minefield_entry(
        galaxy=galaxy,
        empires=empires,
        fleet=fleet,
        registries=registries,
    )


__all__ = [
    "MineDetonationEvent",
    "MinefieldResolutionResult",
    "MinefieldResolver",
    "resolve_minefield_entry",
]
