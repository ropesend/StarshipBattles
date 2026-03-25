"""Event log data source for VirtualTable.

PROJ-188 Phase 5: EventLogDataSource provides event data for the event log table.
Supports category filtering and newest-first sorting.
"""

from typing import Any, Dict, List, Optional

from game.ui.components.table.data_source import ITableDataSource


# Column definitions for the event log table
# PROJ-215: Granular location columns (system, planet, local_hex, galaxy_hex)
EVENT_LOG_COLUMNS = [
    {"id": "category", "width": 90, "title": "Category", "visible": True, "sortable": True},
    {"id": "turn", "width": 60, "title": "Turn", "visible": True, "sortable": True},
    {"id": "system", "width": 120, "title": "System", "visible": True, "sortable": True},
    {"id": "planet", "width": 120, "title": "Planet", "visible": True, "sortable": True},
    {"id": "local_hex", "width": 80, "title": "Local Hex", "visible": False, "sortable": True},
    {"id": "galaxy_hex", "width": 80, "title": "Galaxy Hex", "visible": False, "sortable": True},
    {"id": "storm", "width": 120, "title": "Storm", "visible": False, "sortable": True},
    {"id": "message", "width": 500, "title": "Message", "visible": True, "sortable": True},
]

# Category icons (text prefix for each category)
CATEGORY_ICONS = {
    "combat": "[Combat]",
    "production": "[Prod]",
    "colonies": "[Colony]",
    "fleet_operations": "[FleetOps]",
}


class EventLogDataSource(ITableDataSource):
    """Data source providing event log data for VirtualTable.

    Handles:
    - Category filtering (all, combat, production, colonies, fleet_operations)
    - Newest-first sorting (descending by turn)
    - Cell value extraction for category, turn, message columns
    """

    def __init__(
        self,
        events: List[Dict[str, Any]],
        current_filter: str = "all",
    ) -> None:
        """Initialize with events and optional filter.

        Args:
            events: List of event dicts from facade. Each should have:
                - category: str ('combat', 'production', 'colonies', 'fleet_operations')
                - turn: int - turn number when event occurred
                - message: str - event description text
            current_filter: Initial filter ('all', 'combat', 'production', 'colonies', 'fleet_operations').
        """
        self._all_events = list(events)
        self._current_filter = current_filter
        self._filtered_events: List[Dict[str, Any]] = []
        self._recompute_filtered()

    def get_row_count(self) -> int:
        """Return number of filtered events.

        Returns:
            Count of events matching current filter.
        """
        return len(self._filtered_events)

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return column definitions.

        Returns:
            EVENT_LOG_COLUMNS constant.
        """
        return EVENT_LOG_COLUMNS

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return string value for a cell.

        Args:
            row_index: Zero-based row index (into filtered list).
            column_id: Column identifier ('category', 'turn', 'message').

        Returns:
            String representation of cell value.
        """
        event = self.get_event_at_index(row_index)
        if event is None:
            return ""

        if column_id == "category":
            category = event.get("category", "")
            icon = CATEGORY_ICONS.get(category, "")
            return icon if icon else category

        if column_id == "turn":
            return str(event.get("turn", "?"))

        # PROJ-215: Granular location columns
        if column_id == "system":
            return event.get("details", {}).get("system_name", "")

        if column_id == "planet":
            return event.get("details", {}).get("location_name", "")

        if column_id == "local_hex":
            details = event.get("details", {})
            local = details.get("local_hex")
            if local and len(local) == 2:
                return f"({local[0]}, {local[1]})"
            return ""

        if column_id == "galaxy_hex":
            details = event.get("details", {})
            hex_coords = details.get("location_hex")
            if hex_coords and len(hex_coords) == 2:
                return f"({hex_coords[0]}, {hex_coords[1]})"
            return ""

        # PROJ-215 Phase 5: Storm column
        if column_id == "storm":
            details = event.get("details", {})
            storm_names = details.get("storm_names", [])
            return ", ".join(storm_names) if storm_names else ""

        if column_id == "message":
            return event.get("message", "")

        return ""

    def get_event_at_index(self, row_index: int) -> Optional[Dict[str, Any]]:
        """Get event at given row index in filtered list.

        Args:
            row_index: Zero-based row index.

        Returns:
            Event dict or None if out of bounds.
        """
        if 0 <= row_index < len(self._filtered_events):
            return self._filtered_events[row_index]
        return None

    def set_filter(self, category: str) -> None:
        """Set the active filter category and recompute filtered list.

        Args:
            category: One of 'all', 'combat', 'production', 'colonies', 'fleet_operations'.
        """
        self._current_filter = category
        self._recompute_filtered()

    def update_events(self, events: List[Dict[str, Any]]) -> None:
        """Replace all event data and reapply filter.

        Args:
            events: New list of event dicts.
        """
        self._all_events = list(events)
        self._recompute_filtered()

    def _recompute_filtered(self) -> None:
        """Recompute filtered event list based on current filter.

        Filters by category if not 'all', then sorts newest-first.
        """
        if self._current_filter == "all":
            filtered = list(self._all_events)
        else:
            filtered = [
                e for e in self._all_events
                if e.get("category") == self._current_filter
            ]

        # Sort newest first (descending by turn)
        filtered.sort(key=lambda e: e.get("turn", 0), reverse=True)
        self._filtered_events = filtered
