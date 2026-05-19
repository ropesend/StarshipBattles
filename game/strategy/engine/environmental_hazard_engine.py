"""EnvironmentalHazardEngine - Process storm damage and fuel drain (PROJ-189 Phase 5).

This engine processes environmental effects during the 100-tick turn loop,
applying damage and fuel drain to fleets in storm hexes.

PROJ-300: migrated from `AreaEffectManager` (deleted in Phase 7) to the
unified `system_effects_collector` pipeline. Damage and fuel-drain rates
are now read from `EnvironmentalDamage` and `FuelDrain` ability rows;
multiple sources (storms + facility-projected hazards) sum naturally.

Turn Integration:
    Phase 0f: Called each tick after Phase 0e (construction) to apply
    storm effects to all fleets. Damage is distributed across ships,
    fuel is drained from each ship.
"""

from dataclasses import dataclass
from typing import Any, List, TYPE_CHECKING

from game.strategy.interfaces.engines import IEnvironmentalHazardEngine

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet


@dataclass
class EnvironmentalEvent:
    """Record of environmental effects applied to a fleet during a tick.

    Attributes:
        fleet_id: ID of the affected fleet.
        storm_name: Name of a primary source (e.g. "Ion Storm Alpha"); kept
            for back-compat with existing UI consumers.
        damage_dealt: Total hull damage dealt to the fleet this tick.
        fuel_drained: Total fuel drained from all ships this tick.
        tick: The tick number when this event occurred.
    """

    fleet_id: int
    storm_name: str
    damage_dealt: float
    fuel_drained: float
    tick: int


class EnvironmentalHazardEngine(IEnvironmentalHazardEngine):
    """Engine for processing environmental hazard effects during turn loop.

    Processes storm effects (damage, fuel drain) for all fleets each tick.
    Damage is distributed across ships in the fleet. Fuel drain is applied
    to each ship individually.

    PROJ-189 / PROJ-300: queries the unified collector for
    `EnvironmentalDamage` (rate) and `FuelDrain` (rate) at the fleet's hex.
    """

    def __init__(self, ship_mutator=None):
        """Initialize the engine. PROJ-300: no longer takes AreaEffectManager.

        Args:
            ship_mutator: PROJ-370 IShipInstanceMutator. Lazy-defaulted.
        """
        self._ship_mutator = ship_mutator

    def _get_ship_mutator(self) -> Any:
        if self._ship_mutator is None:
            from game.strategy.services.ship_instance_write_service import (
                ShipInstanceWriteService,
            )
            self._ship_mutator = ShipInstanceWriteService()
        return self._ship_mutator

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    raise ValidationException(
                        f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                        context={"empire_id": empire.id, "fleet_id": fleet.id}
                    )

    def process_environmental_tick(
        self,
        tick: int,
        empires: List,
        galaxy
    ) -> List[EnvironmentalEvent]:
        """Process environmental effects for one tick.

        For each fleet in each empire:
        1. Query storm effects at fleet's location
        2. If in storm, apply damage and fuel drain
        3. Track totals in EnvironmentalEvent

        Damage is 1/100th of damage_per_tick per tick.
        Fuel drain is 1/100th of fuel_drain_per_tick per tick per ship.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.
            galaxy: Galaxy object for spatial queries.

        Returns:
            List of EnvironmentalEvent records for fleets affected this tick.
        """
        self._validate_tick_inputs(empires)
        events: List[EnvironmentalEvent] = []

        # PROJ-412 Phase 2.2: short-circuit when we can affirmatively confirm
        # the galaxy has zero storms. Saves the per-fleet system-lookup +
        # effects-collection loop on storm-free turns (common in early-game
        # / tiny scenarios). Conservative: only short-circuits when
        # `galaxy.systems` exposes a `.values()` we can iterate; any unusual
        # shape (test mock, alternative galaxy impl, etc.) falls through
        # to the original loop so behavior is preserved.
        systems = getattr(galaxy, 'systems', None)
        if isinstance(systems, dict) and not any(
            getattr(s, 'storms', None) for s in systems.values()
        ):
            return events

        from game.strategy.services.system_effects_collector import collect_sector_effects
        get_system = getattr(galaxy, 'get_system_at_location', None)

        for empire in empires:
            for fleet in empire.fleets:
                if get_system is None:
                    continue
                system = get_system(fleet.location)
                if system is None:
                    continue

                # PROJ-300 + PROJ-343 T1.3: pass the querying fleet's owner_id
                # so the collector's gate at system_effects_collector.py:298
                # filters owned hazards to only the owning empire. Ownerless
                # storms still apply to all empires (their owner_id is None,
                # which short-circuits the filter).
                effects = collect_sector_effects(
                    system, fleet.location, empire_id=fleet.owner_id, registries=None,
                )
                damage_effects = [e for e in effects if e['ability_name'] == 'EnvironmentalDamage']
                fuel_effects = [e for e in effects if e['ability_name'] == 'FuelDrain']
                if not damage_effects and not fuel_effects:
                    continue

                damage_per_turn = sum(e['aggregate_value'] for e in damage_effects)
                fuel_per_turn = sum(e['aggregate_value'] for e in fuel_effects)

                if damage_per_turn <= 0 and fuel_per_turn <= 0:
                    continue

                combat_ships = fleet.get_combat_capable_ships()
                if not combat_ships:
                    continue

                damage_per_tick = damage_per_turn / 100.0
                fuel_drain_per_tick = fuel_per_turn / 100.0

                total_damage = 0.0
                total_fuel_drained = 0.0

                if damage_per_tick > 0:
                    damage_per_ship = damage_per_tick / len(combat_ships)
                    for ship in combat_ships:
                        total_damage += self._apply_damage_to_ship(ship, damage_per_ship)

                if fuel_drain_per_tick > 0:
                    for ship in combat_ships:
                        drained = self._drain_fuel_from_ship(ship, fuel_drain_per_tick)
                        total_fuel_drained += drained

                # Pick a representative source label for the event record.
                source_label = "Unknown Hazard"
                for effect_list in (damage_effects, fuel_effects):
                    for e in effect_list:
                        for p in e.get('providers', []):
                            label = p.get('source_label')
                            if label:
                                source_label = label
                                break
                        if source_label != "Unknown Hazard":
                            break
                    if source_label != "Unknown Hazard":
                        break

                events.append(EnvironmentalEvent(
                    fleet_id=fleet.id,
                    storm_name=source_label,
                    damage_dealt=total_damage,
                    fuel_drained=total_fuel_drained,
                    tick=tick,
                ))

        return events

    def _apply_damage_to_ship(self, ship, damage: float) -> float:
        """Apply environmental damage to a ship.

        Environmental damage is applied directly to hull HP.
        Does not use combat damage model (shields don't protect).

        Args:
            ship: ShipInstance to damage.
            damage: Amount of damage to apply.

        Returns:
            Actual damage dealt.
        """
        # Get current HP
        stats = ship.get_calculated_stats()
        max_hp = stats.get('max_hp', 100)
        current_hp = ship.current_hp if ship.current_hp is not None else max_hp

        # Apply damage
        new_hp = max(0, current_hp - damage)
        actual_damage = current_hp - new_hp

        # Update ship HP.
        # PROJ-370 Phase 5: route through IShipInstanceMutator.
        mutator = self._get_ship_mutator()
        if new_hp < max_hp:
            mutator.set_current_hp(ship, new_hp)
        else:
            mutator.set_current_hp(ship, None)  # Reset to full

        # Check for destruction
        if new_hp <= 0:
            mutator.set_is_alive(ship, False)

        return actual_damage

    def _drain_fuel_from_ship(self, ship, amount: float) -> float:
        """Drain fuel from a ship.

        Args:
            ship: ShipInstance to drain fuel from.
            amount: Amount of fuel to drain.

        Returns:
            Actual fuel drained.
        """
        current_fuel = ship.get_current_resource("fuel")
        drain_amount = min(amount, current_fuel)

        if drain_amount > 0:
            ship.consume_resource("fuel", drain_amount)

        return drain_amount
