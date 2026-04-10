"""Filter state management for the Empire Build Queue Window.

Manages filter state, column visibility configuration, and filter predicates
for the EmpireBuildQueueWindow. This module extracts filter/column logic
to allow unit testing of filter behavior without pygame/UI dependencies.

Created as part of PROJ-89 Phase 3.
PROJ-220 Phase 4: Replaced 3 bool filter dicts with FilterStateManager.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, TYPE_CHECKING

from game.ui.filters.filter_state import FilterState
from game.ui.filters.filter_state_manager import FilterStateManager

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource


# Columns that should use numeric sorting (parse to float)
NUMERIC_COLUMNS: set[str] = {
    'queue_count', 'turns_left', 'build_rate',
    'res_metals_rate', 'res_organics_rate', 'res_vapors_rate',
    'res_radioactives_rate', 'res_exotics_rate',
    'res_metals_total', 'res_organics_total', 'res_vapors_total',
    'res_radioactives_total', 'res_exotics_total',
}


# Default column definitions for the empire build queue window
DEFAULT_COLUMNS: List[Dict[str, Any]] = [
    {'id': 'location', 'width': 200, 'title': 'Location', 'visible': True},
    {'id': 'system', 'width': 130, 'title': 'System', 'visible': True},
    {'id': 'sector', 'width': 80, 'title': 'Sector', 'visible': True},
    {'id': 'queue_count', 'width': 80, 'title': 'Items', 'visible': True},
    {'id': 'first_item', 'width': 170, 'title': 'Building', 'visible': True},
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

# Mapping from filter key to (trait_extractor) for tri-state filtering
_FILTER_TRAIT_MAP = {
    'loc_Planet': lambda s: s.context_type == "planet",
    'loc_Fleet': lambda s: s.context_type == "fleet",
    'status_Active': lambda s: len(s.construction_queue) > 0,
    'status_Empty': lambda s: len(s.construction_queue) == 0,
    'cap_Ships': lambda s: s.can_build_ships,
    'cap_Complexes': lambda s: s.can_build_complexes,
}


class BuildQueueFilterManager:
    """Manages filter state and column visibility for the Empire Build Queue.

    Uses FilterStateManager for tri-state (YES/NO/IGNORE) filter control.

    Attributes:
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
        # Tri-state filters via FilterStateManager
        self._filter_mgr = FilterStateManager({
            'loc_Planet': FilterState.IGNORE,
            'loc_Fleet': FilterState.IGNORE,
            'status_Active': FilterState.IGNORE,
            'status_Empty': FilterState.IGNORE,
            'cap_Ships': FilterState.IGNORE,
            'cap_Complexes': FilterState.IGNORE,
        })

        self.search_text: str = ""

        # Column configuration - deep copy to allow independent modification
        if columns is None:
            self.columns: List[Dict[str, Any]] = [
                dict(col) for col in DEFAULT_COLUMNS
            ]
        else:
            self.columns = [dict(col) for col in columns]

    @property
    def filter_manager(self) -> FilterStateManager:
        """Access the tri-state FilterStateManager."""
        return self._filter_mgr

    def get_filter_state(self, key: str) -> FilterState:
        """Get the current FilterState for a filter key."""
        return self._filter_mgr.get_state(key)

    def set_filter_state(self, key: str, state: FilterState) -> None:
        """Set a filter to a specific FilterState."""
        self._filter_mgr.set_state(key, state)

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
        active filters to appear in the result.

        Args:
            sources: The full list of sources to filter.

        Returns:
            Filtered list of sources matching all criteria.
        """
        result = list(sources)

        # Apply tri-state filters
        for key, trait_fn in _FILTER_TRAIT_MAP.items():
            state = self._filter_mgr.get_state(key)
            if state is FilterState.IGNORE:
                continue
            if state is FilterState.YES:
                result = [s for s in result if trait_fn(s)]
            else:  # FilterState.NO
                result = [s for s in result if not trait_fn(s)]

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

    def sort_sources(
        self,
        sources: List[BuildQueueSource],
        sort_column_id: str | None,
        sort_descending: bool,
        get_column_value_fn: Callable[[BuildQueueSource, str], str],
    ) -> List[BuildQueueSource]:
        """Sort sources by the specified column.

        Args:
            sources: List of sources to sort (modified in place).
            sort_column_id: ID of column to sort by, or None for no sort.
            sort_descending: Whether to sort in descending order.
            get_column_value_fn: Function to get display value for a source/column.

        Returns:
            The sorted list (same reference as input).
        """
        if not sort_column_id:
            return sources

        # Check if column exists
        col = next((c for c in self.columns if c['id'] == sort_column_id), None)
        if not col:
            return sources

        is_numeric = sort_column_id in NUMERIC_COLUMNS

        def sort_key(source: BuildQueueSource) -> Any:
            """Generate sort key for a source."""
            val = get_column_value_fn(source, sort_column_id)

            if is_numeric:
                # Parse to float, "-" or unparseable -> infinity (sorts last)
                if val == "-" or val == "":
                    return float('inf')
                try:
                    return float(val.replace(',', ''))
                except (ValueError, AttributeError):
                    return float('inf')
            else:
                # String sort: lowercase, "-" sorts after all other values
                if val == "-":
                    return ("\xff", val)  # Sort after everything
                return (val.lower() if isinstance(val, str) else str(val).lower(), val)

        sources.sort(key=sort_key, reverse=sort_descending)
        return sources
