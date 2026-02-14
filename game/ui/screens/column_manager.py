"""
Column Manager - Manages column configuration for table displays.

PROJ-44 Phase 7 Task 7.4: Extracted from FleetReportWindow for testability.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any, Optional

from game.core.constants import ResourceType

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


# Default column configuration for fleet reports
DEFAULT_FLEET_COLUMNS = [
    {'id': 'portrait', 'width': 44, 'title': '', 'type': 'image', 'visible': True},
    {'id': 'topdown', 'width': 60, 'title': '', 'type': 'image', 'visible': True},
    {'id': 'serial', 'width': 130, 'title': 'Serial ID', 'visible': True},
    {'id': 'design', 'width': 100, 'title': 'Design', 'visible': True},
    {'id': 'name', 'width': 120, 'title': 'Name', 'visible': True},
    {'id': 'hp_pct', 'width': 80, 'title': 'HP %', 'visible': True},
    {'id': 'status', 'width': 100, 'title': 'Status', 'visible': True},
    {'id': 'speed', 'width': 70, 'title': 'Spd', 'visible': False},
    {'id': 'tonnage', 'width': 80, 'title': 'Tons', 'visible': False},
    {'id': 'warp', 'width': 55, 'title': 'Warp', 'visible': False},
    {'id': 'spaceyard', 'width': 60, 'title': 'Yard', 'visible': False},
    {'id': 'transport', 'width': 65, 'title': 'Pax', 'visible': False},
    {'id': 'resources', 'width': 130, 'title': 'Resources', 'visible': False},
    {'id': 'cargo', 'width': 65, 'title': 'Cargo', 'visible': False},
    {'id': 'can_destroy_planet', 'width': 75, 'title': 'DestrPlanet', 'visible': False},
    {'id': 'can_open_warp', 'width': 75, 'title': 'OpenWarp', 'visible': False},
    {'id': 'can_close_warp', 'width': 75, 'title': 'CloseWarp', 'visible': False},
    {'id': 'can_destroy_star', 'width': 75, 'title': 'DestrStar', 'visible': False},
    {'id': 'can_create_sphere', 'width': 75, 'title': 'Sphere', 'visible': False},
]

# Special capability columns and their corresponding ability names
SPECIAL_CAPABILITY_COLUMNS = {
    'can_destroy_planet': 'DestroyPlanet',
    'can_open_warp': 'OpenWarpPoint',
    'can_close_warp': 'CloseWarpPoint',
    'can_destroy_star': 'DestroyStar',
    'can_create_sphere': 'CreateSphereWorld',
}


class ColumnManager:
    """
    Manages column configuration for table displays.

    Handles:
    - Column visibility
    - Column ordering (reordering)
    - Column value extraction from data objects
    """

    def __init__(self, columns: List[Dict[str, Any]] = None):
        """
        Initialize column manager.

        Args:
            columns: Custom column configuration. Uses DEFAULT_FLEET_COLUMNS if None.
        """
        if columns is None:
            # Deep copy default columns
            self._columns = [dict(c) for c in DEFAULT_FLEET_COLUMNS]
        else:
            self._columns = [dict(c) for c in columns]

    def get_columns(self) -> List[Dict[str, Any]]:
        """Get all columns."""
        return self._columns

    def get_visible_columns(self) -> List[Dict[str, Any]]:
        """Get only visible columns."""
        return [c for c in self._columns if c.get('visible', True)]

    def get_toggleable_columns(self) -> List[Dict[str, Any]]:
        """Get columns that can have visibility toggled (non-image columns)."""
        return [c for c in self._columns if c.get('type') != 'image']

    def get_column(self, col_id: str) -> Optional[Dict[str, Any]]:
        """
        Get column by ID.

        Args:
            col_id: Column identifier

        Returns:
            Column dict or None if not found
        """
        for col in self._columns:
            if col['id'] == col_id:
                return col
        return None

    def toggle_column(self, col_id: str) -> bool:
        """
        Toggle column visibility.

        Args:
            col_id: Column identifier

        Returns:
            New visibility state
        """
        col = self.get_column(col_id)
        if col:
            col['visible'] = not col.get('visible', True)
            return col['visible']
        return False

    def swap_column(self, col: Dict[str, Any], direction: int) -> bool:
        """
        Swap column with adjacent column.

        Args:
            col: Column dict to move
            direction: -1 for left, 1 for right

        Returns:
            True if swap occurred
        """
        try:
            idx = self._columns.index(col)
        except ValueError:
            return False

        new_idx = idx + direction
        if 0 <= new_idx < len(self._columns):
            self._columns[idx], self._columns[new_idx] = self._columns[new_idx], self._columns[idx]
            return True
        return False

    def get_total_visible_width(self) -> int:
        """Get total width of all visible columns."""
        return sum(c['width'] for c in self.get_visible_columns())

    def get_column_value(self, ship: ShipInstance, col: Dict[str, Any]) -> str:
        """
        Get display value for a column from a ship.

        Args:
            ship: Ship instance
            col: Column configuration

        Returns:
            String value to display
        """
        col_id = col['id']

        if col_id in ('portrait', 'topdown'):
            return ""  # Images handled separately

        elif col_id == 'serial':
            display_id = ship.get_display_id()
            return display_id if display_id else ship.instance_id[:8]

        elif col_id == 'design':
            return ship.design_data.get('name', ship.design_id)

        elif col_id == 'name':
            return ship.name

        elif col_id == 'hp_pct':
            return f"{ship.get_hp_percentage() * 100:.0f}%"

        elif col_id == 'status':
            if not ship.is_alive:
                return "DESTROYED"
            elif ship.is_derelict:
                return "DERELICT"
            elif ship.is_damaged():
                return "DAMAGED"
            else:
                return "OK"

        elif col_id == 'speed':
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy services
            from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
            speed = FleetSpeedCalculator.calculate_ship_speed(ship)
            return str(speed)

        elif col_id == 'tonnage':
            mass = ship.get_calculated_stats().get('mass', 0)
            return f"{mass:,.0f}"

        elif col_id == 'warp':
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy services
            from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
            return "Yes" if ShipStatsCalculator.has_warp_capability(ship) else "No"

        elif col_id == 'spaceyard':
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
            from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
            return "Yes" if FleetCapabilityCalculator.ship_has_spaceyard(ship) else "No"

        elif col_id == 'transport':
            capacity = ship.get_cargo_capacity('passengers')
            current = ship.get_current_cargo('passengers')
            return f"{current}/{capacity}" if capacity > 0 else "--"

        elif col_id == 'resources':
            # Build compact string: "E:80 F:90 A:100"
            parts = []
            resource_abbrevs = [
                (ResourceType.ENERGY, 'E'),
                (ResourceType.FUEL, 'F'),
                (ResourceType.AMMO, 'A'),
            ]
            for res_type, abbrev in resource_abbrevs:
                pct = ship.get_resource_percentage(res_type)
                if pct is not None and pct >= 0:
                    parts.append(f"{abbrev}:{int(pct * 100)}")
            return " ".join(parts) if parts else "--"

        elif col_id == 'cargo':
            total = sum(ship.cargo_contents.values()) if ship.cargo_contents else 0
            return str(total) if total > 0 else "--"

        elif col_id in SPECIAL_CAPABILITY_COLUMNS:
            # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
            from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
            ability_name = SPECIAL_CAPABILITY_COLUMNS[col_id]
            return "Yes" if FleetCapabilityCalculator.ship_has_ability(ship, ability_name) else "No"

        return ""

    def is_image_column(self, col: Dict[str, Any]) -> bool:
        """Check if column is an image type."""
        return col.get('type') == 'image'
