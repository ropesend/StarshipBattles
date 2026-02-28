"""
Fleet Report filtering and stats calculation.

PROJ-03: Fleet Report Window feature implementation.
PROJ-40: Removed backward-compat wrapper - use ShipStatsCalculator directly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, List

from game.core.constants import ResourceType
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
from game.ui.screens.fleet_data_source import SPECIAL_CAPABILITY_COLUMNS

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


def calculate_fleet_stats(ships: List[ShipInstance]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a fleet.

    Args:
        ships: List of ShipInstance objects in the fleet

    Returns:
        Dictionary with calculated stats:
        - ship_count: Total number of ships
        - combat_capable_count: Ships that can fight (not destroyed/derelict)
        - total_tonnage: Sum of all ship masses
        - avg_hp_percent: Average HP percentage across all ships
        - damaged_count: Number of ships with any damage
        - derelict_count: Number of derelict ships
        - total_fuel/max_fuel: Current and max fuel
        - total_energy/max_energy: Current and max energy
    """
    if not ships:
        return {
            'ship_count': 0,
            'combat_capable_count': 0,
            'total_tonnage': 0,
            'avg_hp_percent': 0.0,
            'damaged_count': 0,
            'derelict_count': 0,
            'total_fuel': 0,
            'max_fuel': 0,
            'total_energy': 0,
            'max_energy': 0,
            'total_passengers': 0,
            'max_passengers': 0,
            'total_cargo_generic': 0,
            'max_cargo_generic': 0,
        }

    ship_count = len(ships)
    combat_capable_count = sum(1 for s in ships if s.is_combat_capable())
    total_tonnage = sum(
        s.get_calculated_stats().get('mass', 0)
        for s in ships
    )
    avg_hp_percent = sum(s.get_hp_percentage() for s in ships) / ship_count
    damaged_count = sum(1 for s in ships if s.is_damaged())
    derelict_count = sum(1 for s in ships if s.is_derelict)

    # Resource calculations
    total_fuel = 0
    max_fuel = 0
    total_energy = 0
    max_energy = 0
    total_passengers = 0
    max_passengers = 0
    total_cargo_generic = 0
    max_cargo_generic = 0

    for ship in ships:
        # Use calculated stats which respect component damage
        calculated_stats = ship.get_calculated_stats()
        resource_storage = calculated_stats.get('resource_storage', {})

        # Fuel
        ship_max_fuel = resource_storage.get(ResourceType.FUEL, 0)
        max_fuel += ship_max_fuel
        total_fuel += ship.resource_levels.get(ResourceType.FUEL, 0)

        # Energy
        ship_max_energy = resource_storage.get(ResourceType.ENERGY, 0)
        max_energy += ship_max_energy
        total_energy += ship.resource_levels.get(ResourceType.ENERGY, 0)

        # Passenger and General Cargo calculations
        cargo_storage = calculated_stats.get('cargo_storage', {})
        
        # Passengers
        max_passengers += cargo_storage.get('passengers', 0)
        total_passengers += ship.get_current_cargo('passengers')
        
        # General Cargo
        max_cargo_generic += cargo_storage.get('generic', 0)
        total_cargo_generic += ship.get_current_cargo('generic')

    # Warp capability counts
    warp_capable_count = sum(1 for s in ships if ShipStatsCalculator.has_warp_capability(s))

    return {
        'ship_count': ship_count,
        'combat_capable_count': combat_capable_count,
        'total_tonnage': total_tonnage,
        'avg_hp_percent': avg_hp_percent,
        'damaged_count': damaged_count,
        'derelict_count': derelict_count,
        'total_fuel': total_fuel,
        'max_fuel': max_fuel,
        'total_energy': total_energy,
        'max_energy': max_energy,
        'total_passengers': total_passengers,
        'max_passengers': max_passengers,
        'total_cargo_generic': total_cargo_generic,
        'max_cargo_generic': max_cargo_generic,
        'warp_capable_count': warp_capable_count,
        'all_warp_capable': warp_capable_count == ship_count and ship_count > 0,
    }


def _should_exclude_by_warp(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship should be excluded based on warp capability filters."""
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)

    # If both filters are on, no exclusion needed
    if show_warp and show_not_warp:
        return False

    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        return True
    if not is_warp_capable and not show_not_warp:
        return True
    return False


def _should_exclude_by_spaceyard(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship should be excluded based on spaceyard capability filters."""
    show_has_yard = filter_state.get('show_has_spaceyard', True)
    show_no_yard = filter_state.get('show_no_spaceyard', True)

    # If both filters are on, no exclusion needed
    if show_has_yard and show_no_yard:
        return False

    # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    if has_yard and not show_has_yard:
        return True
    if not has_yard and not show_no_yard:
        return True
    return False


def _should_exclude_by_cargo(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship should be excluded based on cargo content filters."""
    show_has_cargo = filter_state.get('show_has_cargo', True)
    show_no_cargo = filter_state.get('show_no_cargo', True)

    # If both filters are on, no exclusion needed
    if show_has_cargo and show_no_cargo:
        return False

    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    if has_cargo and not show_has_cargo:
        return True
    if not has_cargo and not show_no_cargo:
        return True
    return False


def _should_exclude_by_special_capabilities(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """Check if ship should be excluded based on special capability filters."""
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        # Derive filter keys from column id: 'can_destroy_planet' -> show_can_destroy_planet / show_no_destroy_planet
        # The "no" variant strips the "can_" prefix
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if not show_has or not show_not:
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
            from game.strategy.services.component_inspector import ship_has_ability
            registry = ship._registries.components if ship._registries else {}
            has_ability = ship_has_ability(ship, ability_name, registry)
            if has_ability and not show_has:
                return True
            if not has_ability and not show_not:
                return True
    return False


def _should_exclude_by_status(ship: 'ShipInstance', filter_state: Dict[str, bool]) -> bool:
    """
    Check if ship should be excluded based on status filters.

    CRITICAL: Order matters. Check destroyed -> derelict -> damaged -> undamaged.
    A derelict ship is also damaged, so derelict must be checked first.
    """
    # Destroyed ships
    if not ship.is_alive:
        return not filter_state.get('show_destroyed', True)

    # Derelict ships (checked before damaged since derelict implies damaged)
    if ship.is_derelict:
        return not filter_state.get('show_derelict', True)

    # Damaged ships
    if ship.is_damaged():
        return not filter_state.get('show_damaged', True)

    # Undamaged (healthy) ships
    return not filter_state.get('show_undamaged', True)


def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with keys:
            - show_damaged: Include damaged ships
            - show_undamaged: Include undamaged ships
            - show_derelict: Include derelict ships
            - show_destroyed: Include destroyed ships
            - show_warp_capable: Include warp-capable ships
            - show_not_warp_capable: Include ships without warp capability

    Returns:
        Filtered list of ships
    """
    result = []
    for ship in ships:
        # Warp capability filter
        if _should_exclude_by_warp(ship, filter_state):
            continue

        # Spaceyard capability filter
        if _should_exclude_by_spaceyard(ship, filter_state):
            continue

        # Cargo filter (includes population)
        if _should_exclude_by_cargo(ship, filter_state):
            continue

        # Special capability filters
        if _should_exclude_by_special_capabilities(ship, filter_state):
            continue

        # Status filters (destroyed, derelict, damaged, undamaged)
        if _should_exclude_by_status(ship, filter_state):
            continue

        result.append(ship)

    return result


def sort_ships(
    ships: List[ShipInstance],
    sort_column: str,
    descending: bool = False
) -> List[ShipInstance]:
    """
    Sort ships by the specified column.

    Args:
        ships: List of ShipInstance objects
        sort_column: Column ID to sort by ('serial', 'design', 'name', 'hp_pct', 'status', etc.)
        descending: If True, sort in descending order

    Returns:
        Sorted list of ships
    """
    def get_sort_key(ship):
        if sort_column == 'serial':
            return ship.serial or 0
        elif sort_column == 'design':
            return ship.design_data.get('name', '').lower()
        elif sort_column == 'name':
            return ship.name.lower()
        elif sort_column == 'hp_pct':
            return ship.get_hp_percentage()
        elif sort_column == 'status':
            # Sort by severity: OK=0, DAMAGED=1, DERELICT=2, DESTROYED=3
            if not ship.is_alive:
                return 3
            elif ship.is_derelict:
                return 2
            elif ship.is_damaged():
                return 1
            return 0
        elif sort_column == 'speed':
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy services
            from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
            return FleetSpeedCalculator.calculate_ship_speed(ship)
        elif sort_column == 'tonnage':
            return ship.get_calculated_stats().get('mass', 0)
        elif sort_column == 'warp':
            return 1 if ShipStatsCalculator.has_warp_capability(ship) else 0
        elif sort_column == 'spaceyard':
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
            from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
            return 1 if FleetCapabilityCalculator.ship_has_spaceyard(ship) else 0
        elif sort_column == 'transport':
            return ship.get_cargo_capacity('passengers')
        elif sort_column == 'cargo':
            return sum(ship.cargo_contents.values()) if ship.cargo_contents else 0
        elif sort_column == 'resources':
            # No meaningful sort for combined column
            return 0
        elif sort_column in SPECIAL_CAPABILITY_COLUMNS:
            from game.strategy.services.component_inspector import ship_has_ability
            ability_name = SPECIAL_CAPABILITY_COLUMNS[sort_column]
            registry = ship._registries.components if ship._registries else {}
            return 1 if ship_has_ability(ship, ability_name, registry) else 0
        return 0

    return sorted(ships, key=get_sort_key, reverse=descending)
