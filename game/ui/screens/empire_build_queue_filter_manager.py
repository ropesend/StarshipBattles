"""Filter state management for the Empire Build Queue Window.

Manages filter state, column visibility configuration, and filter predicates
for the EmpireBuildQueueWindow. This module extracts filter/column logic
to allow unit testing of filter behavior without pygame/UI dependencies.

Created as part of PROJ-89 Phase 3.
"""
from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource


# Default column definitions for the empire build queue window
DEFAULT_COLUMNS: List[Dict[str, Any]] = [
    {'id': 'location', 'width': 180, 'title': 'Location', 'visible': True},
    {'id': 'system', 'width': 120, 'title': 'System', 'visible': True},
    {'id': 'sector', 'width': 80, 'title': 'Sector', 'visible': True},
    {'id': 'queue_count', 'width': 80, 'title': 'Items', 'visible': True},
    {'id': 'first_item', 'width': 150, 'title': 'Building', 'visible': True},
    {'id': 'turns_left', 'width': 80, 'title': 'Turns', 'visible': True},
    {'id': 'capabilities', 'width': 100, 'title': 'Can Build', 'visible': True},
    {'id': 'build_rate', 'width': 80, 'title': 'Build Rate', 'visible': True},
    # Resource consumption rate columns (per-turn)
    {'id': 'res_metals_rate', 'width': 70, 'title': 'Met/t', 'visible': True},
    {'id': 'res_organics_rate', 'width': 70, 'title': 'Org/t', 'visible': True},
    {'id': 'res_vapors_rate', 'width': 70, 'title': 'Vap/t', 'visible': True},
    {'id': 'res_radioactives_rate', 'width': 70, 'title': 'Rad/t', 'visible': True},
    {'id': 'res_exotics_rate', 'width': 70, 'title': 'Exo/t', 'visible': True},
    # Resource total cost columns
    {'id': 'res_metals_total', 'width': 70, 'title': 'Met Tot', 'visible': True},
    {'id': 'res_organics_total', 'width': 70, 'title': 'Org Tot', 'visible': True},
    {'id': 'res_vapors_total', 'width': 70, 'title': 'Vap Tot', 'visible': True},
    {'id': 'res_radioactives_total', 'width': 70, 'title': 'Rad Tot', 'visible': True},
    {'id': 'res_exotics_total', 'width': 70, 'title': 'Exo Tot', 'visible': True},
]


class BuildQueueFilterManager:
    """Manages filter state and column visibility for the Empire Build Queue.

    Attributes:
        filter_location_type: Dict mapping 'Planet'/'Fleet' to enabled state.
        filter_status: Dict mapping 'Active'/'Empty' to enabled state.
        filter_capabilities: Dict mapping 'Ships'/'Complexes' to enabled state.
        search_text: Current text search filter (case-insensitive).
        columns: List of column configuration dicts.
    """

    def __init__(
        self,
        columns: List[Dict[str, Any]] | None = None,
    ) -> None:
        """Initialize filter manager with default state.

        Args:
            columns: Optional column definitions. If None, uses DEFAULT_COLUMNS.
        """
        # Filter state - all enabled by default
        self.filter_location_type: Dict[str, bool] = {'Planet': True, 'Fleet': True}
        self.filter_status: Dict[str, bool] = {'Active': True, 'Empty': True}
        self.filter_capabilities: Dict[str, bool] = {'Ships': True, 'Complexes': True}
        self.search_text: str = ""

        # Column configuration - deep copy to allow independent modification
        if columns is None:
            self.columns: List[Dict[str, Any]] = [
                dict(col) for col in DEFAULT_COLUMNS
            ]
        else:
            self.columns = [dict(col) for col in columns]

    def get_visible_columns(self) -> List[Dict[str, Any]]:
        """Return list of currently visible columns.

        Returns:
            List of column dicts where 'visible' is True.
        """
        return [c for c in self.columns if c.get('visible', True)]

    def toggle_column_visibility(self, col_id: str) -> bool:
        """Toggle visibility of a column by ID.

        Args:
            col_id: ID of the column to toggle.

        Returns:
            True if visibility was toggled, False if column not found.
        """
        for col in self.columns:
            if col['id'] == col_id:
                col['visible'] = not col['visible']
                return True
        return False

    def filter_sources(
        self, sources: List[BuildQueueSource],
    ) -> List[BuildQueueSource]:
        """Apply all active filters to a list of sources.

        Filters are combined with AND logic: a source must pass all
        enabled filters to appear in the result.

        Args:
            sources: The full list of sources to filter.

        Returns:
            Filtered list of sources matching all criteria.
        """
        result = list(sources)

        # Location type filter
        result = [
            s for s in result
            if (s.context_type == "planet" and self.filter_location_type.get('Planet', True))
            or (s.context_type == "fleet" and self.filter_location_type.get('Fleet', True))
        ]

        # Queue status filter
        result = [
            s for s in result
            if (len(s.construction_queue) > 0 and self.filter_status.get('Active', True))
            or (len(s.construction_queue) == 0 and self.filter_status.get('Empty', True))
        ]

        # Capabilities filter - show source if ANY of its capabilities match
        # an enabled filter. If all filters are on, show everything.
        if not (self.filter_capabilities.get('Ships', True)
                and self.filter_capabilities.get('Complexes', True)):
            result = [
                s for s in result
                if (s.can_build_ships and self.filter_capabilities.get('Ships', True))
                or (s.can_build_complexes and self.filter_capabilities.get('Complexes', True))
            ]

        # Text search filter
        if self.search_text.strip():
            search_lower = self.search_text.strip().lower()
            result = [
                s for s in result
                if search_lower in s.display_name.lower()
            ]

        return result

    def reset_selection_state(self) -> Dict[str, Any]:
        """Return default selection state values for the window.

        The window can use this to reset its selection after filtering.

        Returns:
            Dict with 'selected_source' (None), 'selected_index' (-1),
            and 'selected_indices' (empty set).
        """
        return {
            'selected_source': None,
            'selected_index': -1,
            'selected_indices': set(),
        }
