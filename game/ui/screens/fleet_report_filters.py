"""
Fleet Report filtering and stats calculation.

PROJ-03: Fleet Report Window feature implementation.
PROJ-40: Removed backward-compat wrapper - use ShipStatsCalculator directly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, List

from game.core.constants import ResourceType
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

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

    for ship in ships:
        # Use calculated stats which respect component damage
        calculated_stats = ship.get_calculated_stats()
        resource_storage = calculated_stats.get('resource_storage', {})

        # Fuel
        ship_max_fuel = resource_storage.get(ResourceType.FUEL, 0)
        max_fuel += ship_max_fuel
        if ResourceType.FUEL in ship.resource_levels:
            total_fuel += ship.resource_levels[ResourceType.FUEL]
        else:
            total_fuel += ship_max_fuel  # Full if not tracked

        # Energy
        ship_max_energy = resource_storage.get(ResourceType.ENERGY, 0)
        max_energy += ship_max_energy
        if ResourceType.ENERGY in ship.resource_levels:
            total_energy += ship.resource_levels[ResourceType.ENERGY]
        else:
            total_energy += ship_max_energy  # Full if not tracked

    # Warp capability counts - PROJ-40: Call ShipStatsCalculator directly
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
        'warp_capable_count': warp_capable_count,
        'all_warp_capable': warp_capable_count == ship_count and ship_count > 0,
    }


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
        # Warp capability filter (if either warp filter is specified)
        show_warp = filter_state.get('show_warp_capable', True)
        show_not_warp = filter_state.get('show_not_warp_capable', True)

        # If either filter is off, we need to check warp capability
        # PROJ-40: Call ShipStatsCalculator directly
        if not show_warp or not show_not_warp:
            is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
            if is_warp_capable and not show_warp:
                continue
            if not is_warp_capable and not show_not_warp:
                continue

        # Destroyed filter
        if ship.is_destroyed:
            if not filter_state.get('show_destroyed', True):
                continue
            result.append(ship)
            continue

        # Derelict filter (checked before damaged since derelict implies damaged)
        if ship.is_derelict:
            if not filter_state.get('show_derelict', True):
                continue
            result.append(ship)
            continue

        # Damaged filter
        if ship.is_damaged():
            if not filter_state.get('show_damaged', True):
                continue
            result.append(ship)
            continue

        # Undamaged (healthy) ships
        if not filter_state.get('show_undamaged', True):
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
        sort_column: Column ID to sort by ('serial', 'design', 'name', 'hp_pct', 'status')
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
            if ship.is_destroyed:
                return 3
            elif ship.is_derelict:
                return 2
            elif ship.is_damaged():
                return 1
            return 0
        return 0

    return sorted(ships, key=get_sort_key, reverse=descending)
