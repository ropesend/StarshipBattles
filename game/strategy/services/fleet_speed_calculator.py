"""
FleetSpeedCalculator - Calculates strategic movement for fleets.

This calculator handles:
1. Individual ship speed calculation from design data
2. Fleet speed as minimum of all ships (slowest ship determines fleet speed)
3. Caching for performance (future)
4. Future: Tractor beam bonuses from nearby complexes/ships

Formula: hexes = (strategic_movement * K_STRATEGIC) / mass
- Uses same /mass relationship as combat speed for consistency
- K_STRATEGIC tuned so ~20% engine mass gives ~5 hexes/turn

Example calculation:
- 1000kg ship with standard_engine (80kg, 100 MP) + size mount 2x = 160kg, 200 MP
- Total mass ~1000kg, strategic_movement = 200
- hexes = (200 * 25) / 1000 = 5 hexes/turn
"""

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


# Constants
# K_STRATEGIC tuned so ships with ~20% engine mass get ~4-6 hexes/turn
# Formula: hexes = (strategic_movement * K_STRATEGIC) / mass
K_STRATEGIC = 25  # Movement point to hex conversion factor
MAX_HEXES_PER_TURN = 10
MIN_HEXES_PER_TURN = 0

# Tick interval constant: base ticks for speed-to-interval conversion
# Speed 5 = acts every 20 ticks, Speed 1 = acts every 100 ticks
BASE_TICKS_PER_MOVEMENT = 100


def get_tick_interval(speed: float) -> int:
    """
    Calculate the tick interval for a given speed value.

    Fleets act at intervals determined by their speed:
    - Speed 10 = acts every 10 ticks (fast)
    - Speed 5 = acts every 20 ticks
    - Speed 1 = acts every 100 ticks (slow)

    PROJ-204 Phase 2: Consolidates duplicated tick interval logic (CQ-44).

    Args:
        speed: Fleet speed value (hexes per turn)

    Returns:
        Number of ticks between actions. Minimum 1.
    """
    if speed <= 0:
        return BASE_TICKS_PER_MOVEMENT  # Maximum interval for immobile
    return max(1, int(BASE_TICKS_PER_MOVEMENT // speed))

# Vehicle types that cannot move independently
IMMOBILE_VEHICLE_TYPES = {'Planetary Complex', 'Satellite', 'Station'}

# Vehicle types that are carrier-based (no independent strategic movement)
CARRIER_BASED_TYPES = {'Fighter'}


class FleetSpeedCalculator:
    """Calculator for fleet strategic movement speeds."""

    @staticmethod
    def calculate_ship_speed(ship_instance: 'ShipInstance') -> int:
        """
        Calculate hexes/turn for a single ship from its design data.

        Formula: hexes = floor((movement_points * K_STRATEGIC) / mass)
        Result is clamped to [0, 10].

        This uses the same /mass relationship as combat speed, providing
        consistent scaling behavior between combat and strategic layers.

        Special cases:
        - Planetary complexes: Always 0 (stationary)
        - Fighters: 0 by default (carrier-based, no strategic movement)
        - Ships with no StrategicMovement ability: 0 (cannot move independently)

        Args:
            ship_instance: The ShipInstance to calculate speed for

        Returns:
            Integer hexes per turn (0-10)
        """
        design_data = ship_instance.design_data

        # Check vehicle type - some are inherently immobile
        vehicle_type = design_data.get('vehicle_type', 'Ship')

        if vehicle_type in IMMOBILE_VEHICLE_TYPES:
            return 0

        # Fighters are carrier-based - no independent strategic movement
        if vehicle_type in CARRIER_BASED_TYPES:
            return 0

        # Get stats from calculated values (respects component damage)
        calculated_stats = ship_instance.get_calculated_stats()
        mass = calculated_stats.get('mass', 0)
        movement_points = calculated_stats.get('strategic_movement', 0)

        if mass <= 0 or movement_points <= 0:
            return 0

        # Calculate hexes per turn (same /mass ratio as combat speed)
        raw_hexes = (movement_points * K_STRATEGIC) / mass

        # Clamp to valid range
        return max(MIN_HEXES_PER_TURN, min(MAX_HEXES_PER_TURN, int(raw_hexes)))

    @staticmethod
    def calculate_fleet_speed(fleet: 'Fleet') -> float:
        """
        Calculate fleet speed as the slowest ship's speed.

        The fleet moves at the speed of its slowest member (convoy behavior).
        Only considers combat-capable ships (excludes destroyed/derelict).

        Args:
            fleet: The Fleet to calculate speed for

        Returns:
            Float speed value (hexes per turn)
        """
        if not fleet.ships:
            return 0.0

        # Calculate speed for each combat-capable ship
        speeds = []
        for ship in fleet.ships:
            if ship.is_combat_capable():
                speed = FleetSpeedCalculator.calculate_ship_speed(ship)
                speeds.append(speed)

        if not speeds:
            return 0.0  # All ships destroyed

        # Fleet moves at slowest ship speed
        return float(min(speeds))

    @staticmethod
    def update_fleet_speed(fleet: 'Fleet') -> None:
        """
        Update fleet.speed based on current ship composition.

        Call this when:
        - Fleet is created
        - Ships are added/removed
        - Ships are damaged/repaired

        Args:
            fleet: The Fleet to update
        """
        fleet.speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

    @staticmethod
    def calculate_fleet_speed_with_strategic_mult(
        fleet: 'Fleet',
        strategic_mult: float = 1.0,
    ) -> float:
        """
        Calculate fleet speed with an explicit strategic multiplier.

        The fleet base speed is calculated normally (slowest ship), then the
        provided multiplier is applied BEFORE the final floor/clamp.

        PROJ-300 Phase 7: simplified from the legacy
        calculate_fleet_speed_with_environment(EnvironmentalEffects). Callers
        compute the multiplier from sector effects via aggregate_value_or.

        Args:
            fleet: The Fleet to calculate speed for.
            strategic_mult: Multiplier to apply (1.0 = no change).

        Returns:
            Float speed value (hexes per turn), >= 0.0.
        """
        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        if strategic_mult == 1.0:
            return base_speed
        modified_speed = base_speed * strategic_mult
        return max(0.0, float(int(modified_speed)))
