"""EnvironmentalHazardEngine - Process storm damage and fuel drain (PROJ-189 Phase 5).

This engine processes environmental effects during the 100-tick turn loop,
applying damage and fuel drain to fleets in storm hexes.

Turn Integration:
    Phase 0f: Called each tick after Phase 0e (construction) to apply
    storm effects to all fleets. Damage is distributed across ships,
    fuel is drained from each ship.

Dependencies:
    - AreaEffectManager: Queries aggregated storm effects at hex locations
"""

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from game.strategy.interfaces.engines import IEnvironmentalHazardEngine

if TYPE_CHECKING:
    from game.strategy.services.area_effect_manager import AreaEffectManager
    from game.strategy.data.fleet import Fleet


@dataclass
class EnvironmentalEvent:
    """Record of environmental effects applied to a fleet during a tick.

    Attributes:
        fleet_id: ID of the affected fleet.
        storm_name: Name of the primary storm affecting the fleet.
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

    PROJ-189: Part of the turn engine Phase 0f processing.
    """

    def __init__(self, area_effect_manager: Optional['AreaEffectManager'] = None):
        """Initialize the environmental hazard engine.

        Args:
            area_effect_manager: Optional AreaEffectManager for dependency injection.
                                If None, creates a default instance lazily.
        """
        if area_effect_manager is not None:
            self._area_effect_manager = area_effect_manager
        else:
            from game.strategy.services.area_effect_manager import AreaEffectManager
            self._area_effect_manager = AreaEffectManager()

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

        for empire in empires:
            for fleet in empire.fleets:
                # Query effects at fleet location
                effects = self._area_effect_manager.get_effects_at_global_hex(
                    galaxy, fleet.location
                )

                if not effects.in_storm:
                    continue

                # Get combat-capable ships
                combat_ships = fleet.get_combat_capable_ships()
                if not combat_ships:
                    continue

                # Calculate per-tick amounts (1/100th of per-turn value)
                damage_per_tick = effects.damage_per_tick / 100.0
                fuel_drain_per_tick = effects.fuel_drain_per_tick / 100.0

                total_damage = 0.0
                total_fuel_drained = 0.0

                # Apply damage: distribute across ships
                if damage_per_tick > 0:
                    damage_per_ship = damage_per_tick / len(combat_ships)
                    for ship in combat_ships:
                        total_damage += self._apply_damage_to_ship(ship, damage_per_ship)
                else:
                    # Record 0 damage for tracking
                    total_damage = 0.0

                # Apply fuel drain: each ship drains fuel
                if fuel_drain_per_tick > 0:
                    for ship in combat_ships:
                        drained = self._drain_fuel_from_ship(ship, fuel_drain_per_tick)
                        total_fuel_drained += drained
                else:
                    total_fuel_drained = 0.0

                # Create event for this fleet
                storm_name = effects.storm_names[0] if effects.storm_names else "Unknown Storm"
                events.append(EnvironmentalEvent(
                    fleet_id=fleet.id,
                    storm_name=storm_name,
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

        # Update ship HP
        if new_hp < max_hp:
            ship.current_hp = new_hp
        else:
            ship.current_hp = None  # Reset to full (won't happen with damage > 0)

        # Check for destruction
        if new_hp <= 0:
            ship.is_alive = False

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
