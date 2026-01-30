"""
Fleet List View Model - Manages filtering, sorting, and ship list state.

PROJ-44 Phase 7 Task 7.4: Extracted from FleetReportWindow for testability.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any

from game.ui.screens.fleet_report_filters import filter_ships, sort_ships

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class FleetListViewModel:
    """
    Manages ship list state for FleetReportWindow.

    Handles:
    - Filter state (damaged, undamaged, derelict, destroyed, warp capable)
    - Sort state (column and direction)
    - Filtering and sorting ships
    """

    def __init__(self, ships: List[ShipInstance] = None):
        """
        Initialize view model with optional ship list.

        Args:
            ships: Initial list of ships to manage
        """
        self._ships = ships or []

        # Filter state - defaults match FleetReportWindow
        self.filter_show_damaged = True
        self.filter_show_undamaged = True
        self.filter_show_derelict = True
        self.filter_show_destroyed = False  # Destroyed hidden by default
        self.filter_show_warp_capable = True
        self.filter_show_not_warp_capable = True

        # Sort state
        self.sort_column_id = 'serial'
        self.sort_descending = False

        # Cached filtered list
        self._filtered_ships: List[ShipInstance] = []
        self._needs_refresh = True

    def update_ships(self, ships: List[ShipInstance]) -> None:
        """
        Update the source ship list.

        Args:
            ships: New list of ships
        """
        self._ships = ships or []
        self._needs_refresh = True

    def toggle_filter(self, filter_id: str) -> bool:
        """
        Toggle a filter on/off.

        Args:
            filter_id: Filter identifier ('damaged', 'undamaged', 'derelict',
                      'destroyed', 'warp_capable', 'not_warp_capable')

        Returns:
            New filter state (True = showing, False = hiding)
        """
        if filter_id == 'damaged':
            self.filter_show_damaged = not self.filter_show_damaged
            result = self.filter_show_damaged
        elif filter_id == 'undamaged':
            self.filter_show_undamaged = not self.filter_show_undamaged
            result = self.filter_show_undamaged
        elif filter_id == 'derelict':
            self.filter_show_derelict = not self.filter_show_derelict
            result = self.filter_show_derelict
        elif filter_id == 'destroyed':
            self.filter_show_destroyed = not self.filter_show_destroyed
            result = self.filter_show_destroyed
        elif filter_id == 'warp_capable':
            self.filter_show_warp_capable = not self.filter_show_warp_capable
            result = self.filter_show_warp_capable
        elif filter_id == 'not_warp_capable':
            self.filter_show_not_warp_capable = not self.filter_show_not_warp_capable
            result = self.filter_show_not_warp_capable
        else:
            return False

        self._needs_refresh = True
        return result

    def set_sort(self, column_id: str) -> None:
        """
        Set sort column. If same column, toggles direction.

        Args:
            column_id: Column to sort by
        """
        if self.sort_column_id == column_id:
            # Toggle direction if same column
            self.sort_descending = not self.sort_descending
        else:
            # New column, reset to ascending
            self.sort_column_id = column_id
            self.sort_descending = False

        self._needs_refresh = True

    def get_filter_state(self) -> Dict[str, bool]:
        """
        Get current filter state as dict for filter_ships function.

        Returns:
            Dict with filter state keys
        """
        return {
            'show_damaged': self.filter_show_damaged,
            'show_undamaged': self.filter_show_undamaged,
            'show_derelict': self.filter_show_derelict,
            'show_destroyed': self.filter_show_destroyed,
            'show_warp_capable': self.filter_show_warp_capable,
            'show_not_warp_capable': self.filter_show_not_warp_capable,
        }

    def get_filtered_ships(self) -> List[ShipInstance]:
        """
        Get filtered and sorted ship list.

        Returns:
            List of ships after filtering and sorting
        """
        if self._needs_refresh:
            self._refresh()
        return self._filtered_ships

    def _refresh(self) -> None:
        """Refresh the filtered/sorted ship list."""
        # Apply filters
        filtered = filter_ships(self._ships, self.get_filter_state())

        # Apply sort
        self._filtered_ships = sort_ships(
            filtered,
            self.sort_column_id,
            self.sort_descending
        )
        self._needs_refresh = False

    def get_ship_count(self) -> int:
        """Get count of filtered ships."""
        return len(self.get_filtered_ships())

    def get_total_ship_count(self) -> int:
        """Get total ship count (unfiltered)."""
        return len(self._ships)

    def get_filter_label(self, filter_id: str) -> str:
        """
        Get display label for a filter.

        Args:
            filter_id: Filter identifier

        Returns:
            Human-readable filter label
        """
        labels = {
            'damaged': 'Damaged',
            'undamaged': 'Undamaged',
            'derelict': 'Derelict',
            'destroyed': 'Destroyed',
            'warp_capable': 'Warp Capable',
            'not_warp_capable': 'Not Warp Capable',
        }
        return labels.get(filter_id, filter_id)

    def is_filter_enabled(self, filter_id: str) -> bool:
        """
        Check if a filter is enabled (showing matching ships).

        Args:
            filter_id: Filter identifier

        Returns:
            True if filter is enabled
        """
        state = self.get_filter_state()
        key = f'show_{filter_id}'
        return state.get(key, True)
