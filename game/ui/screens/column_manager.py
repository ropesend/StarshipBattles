"""
Column Manager - Manages column configuration for table displays.

PROJ-44 Phase 7 Task 7.4: Extracted from FleetReportWindow for testability.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any, Optional

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
]


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
            if ship.is_destroyed:
                return "DESTROYED"
            elif ship.is_derelict:
                return "DERELICT"
            elif ship.is_damaged():
                return "DAMAGED"
            else:
                return "OK"

        return ""

    def is_image_column(self, col: Dict[str, Any]) -> bool:
        """Check if column is an image type."""
        return col.get('type') == 'image'
