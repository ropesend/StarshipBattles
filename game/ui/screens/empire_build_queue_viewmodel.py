"""ViewModel for EmpireBuildQueueWindow.

Manages build queue list state including filtering, selection, and search.
Emits events through EventBus for UI updates. No Pygame dependencies.

Created as part of PROJ-172 Phase 3.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Set

from game.ui.filters.filter_state import FilterState
from game.ui.screens.empire_build_queue_filter_manager import BuildQueueFilterManager
from game.ui.screens.empire_build_queue_formatter import (
    get_queue_summary,
    get_first_item_text,
    get_capabilities_text,
    get_turns_left_text,
    get_resource_rate_text,
    get_resource_total_text,
)

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.ui.screens.builder.event_bus import EventBus


class BuildQueueWindowEvents:
    """Event type constants for EmpireBuildQueueViewModel."""

    SOURCES_CHANGED = "empire_build_queue.sources_changed"
    SELECTION_CHANGED = "empire_build_queue.selection_changed"
    FILTERS_APPLIED = "empire_build_queue.filters_applied"


# Resource column mappings (duplicated from window for independence)
RESOURCE_RATE_COLS = {
    'res_metals_rate': 'metals',
    'res_organics_rate': 'organics',
    'res_vapors_rate': 'vapors',
    'res_radioactives_rate': 'radioactives',
    'res_exotics_rate': 'exotics',
}
RESOURCE_TOTAL_COLS = {
    'res_metals_total': 'metals',
    'res_organics_total': 'organics',
    'res_vapors_total': 'vapors',
    'res_radioactives_total': 'radioactives',
    'res_exotics_total': 'exotics',
}


class EmpireBuildQueueViewModel:
    """ViewModel managing state for EmpireBuildQueueWindow.

    Handles:
    - Source list management
    - Single and multi-selection
    - Filter state (location, status, capabilities, search)
    - Event emission for UI updates

    No Pygame imports - independently testable.

    Args:
        event_bus: EventBus for emitting state change events.
        sources: Initial list of BuildQueueSource objects.
    """

    def __init__(
        self,
        event_bus: EventBus,
        sources: List[BuildQueueSource] = None,
    ) -> None:
        self._event_bus = event_bus
        self._filter_mgr = BuildQueueFilterManager()

        # Source data
        self._all_sources: List[BuildQueueSource] = list(sources) if sources else []
        self._filtered_sources: List[BuildQueueSource] = []

        # Selection state (multi-select)
        self._selected_indices: Set[int] = set()

        # Search state
        self._search_text: str = ""

        # Lazy refresh flag
        self._needs_refresh: bool = True

        # Initial filter application
        self._refresh()

    # -----------------------------------------------------------------------
    # Properties - Source Data
    # -----------------------------------------------------------------------

    @property
    def all_sources(self) -> List[BuildQueueSource]:
        """All source data (unfiltered)."""
        return self._all_sources

    @property
    def filtered_sources(self) -> List[BuildQueueSource]:
        """Filtered and sorted source list."""
        if self._needs_refresh:
            self._refresh()
        return self._filtered_sources

    # -----------------------------------------------------------------------
    # Properties - Selection State
    # -----------------------------------------------------------------------

    @property
    def selected_indices(self) -> Set[int]:
        """Set of all selected indices."""
        return self._selected_indices

    @selected_indices.setter
    def selected_indices(self, value: Set[int]) -> None:
        """Set selected indices (for direct manipulation in tests)."""
        self._selected_indices = value

    # -----------------------------------------------------------------------
    # Properties - Filter State
    # -----------------------------------------------------------------------

    @property
    def search_text(self) -> str:
        """Current search filter text."""
        return self._search_text

    def get_filter_state(self, key: str) -> FilterState:
        """Get the current FilterState for a filter key.

        Args:
            key: Filter key (e.g., 'loc_Planet', 'status_Active').

        Returns:
            Current FilterState value.
        """
        return self._filter_mgr.get_filter_state(key)

    def set_filter_state(self, key: str, state: FilterState) -> None:
        """Set a filter to a specific FilterState.

        Args:
            key: Filter key (e.g., 'loc_Planet', 'status_Active').
            state: New FilterState value.
        """
        self._filter_mgr.set_filter_state(key, state)

    # -----------------------------------------------------------------------
    # Source Management
    # -----------------------------------------------------------------------

    def update_sources(self, sources: List[BuildQueueSource]) -> None:
        """Replace the source list and reset state.

        Args:
            sources: New list of BuildQueueSource objects.
        """
        self._all_sources = list(sources) if sources else []
        self._clear_selection()
        self._needs_refresh = True
        self._event_bus.emit(BuildQueueWindowEvents.SOURCES_CHANGED, None)

    # -----------------------------------------------------------------------
    # Selection Methods
    # -----------------------------------------------------------------------

    def select_source(self, index: int, ctrl_held: bool = False) -> None:
        """Select a source by index.

        Single click (ctrl_held=False): select only this index.
        Ctrl+click: toggle this index in the selection set.

        Args:
            index: Index into filtered_sources.
            ctrl_held: True if Ctrl key was held.
        """
        if index < 0 or index >= len(self.filtered_sources):
            return

        if ctrl_held:
            if index in self._selected_indices:
                # Don't allow deselecting the last item
                if len(self._selected_indices) > 1:
                    self._selected_indices.discard(index)
            else:
                self._selected_indices.add(index)
        else:
            self._selected_indices = {index}

        self._event_bus.emit(BuildQueueWindowEvents.SELECTION_CHANGED, {
            'selected_indices': self._selected_indices,
        })

    def get_selected_sources(self) -> List[BuildQueueSource]:
        """Return the BuildQueueSource objects for all selected indices.

        Returns:
            List of selected sources, in index order.
        """
        return [
            self.filtered_sources[i]
            for i in sorted(self._selected_indices)
            if 0 <= i < len(self.filtered_sources)
        ]

    def get_selection_summary(self) -> str:
        """Return a human-readable summary of the current selection.

        Returns:
            Summary string describing what is selected.
        """
        count = len(self._selected_indices)
        if count == 0:
            return "No queues selected"
        if count == 1:
            idx = next(iter(self._selected_indices))
            if 0 <= idx < len(self.filtered_sources):
                name = self.filtered_sources[idx].display_name
                return f"1 queue selected: {name}"
            return "1 queue selected"
        return f"{count} queues selected"

    def _clear_selection(self) -> None:
        """Clear all selection state."""
        self._selected_indices = set()

    # -----------------------------------------------------------------------
    # Filter Methods
    # -----------------------------------------------------------------------

    def set_search_text(self, text: str) -> None:
        """Set the search filter text.

        Args:
            text: Search string (case-insensitive substring match).
        """
        self._search_text = text
        self._filter_mgr.search_text = text

    def apply_filters(self) -> None:
        """Re-apply all filters and clear selection."""
        self._filter_mgr.search_text = self._search_text
        self._clear_selection()
        self._needs_refresh = True
        self._refresh()
        self._event_bus.emit(BuildQueueWindowEvents.FILTERS_APPLIED, None)

    # -----------------------------------------------------------------------
    # Column Value Formatting
    # -----------------------------------------------------------------------

    def get_column_value(self, source: BuildQueueSource, col_id: str) -> str:
        """Return the display value for a column and source.

        Args:
            source: The build queue source to extract data from.
            col_id: Column identifier string.

        Returns:
            Human-readable string value for the cell.
        """
        if col_id == 'location':
            return source.display_name
        if col_id == 'queue_count':
            return get_queue_summary(source)
        if col_id == 'first_item':
            return get_first_item_text(source)
        if col_id == 'turns_left':
            return get_turns_left_text(source)
        if col_id == 'capabilities':
            return get_capabilities_text(source)
        if col_id == 'build_rate':
            if source.build_rate:
                max_rate = max(source.build_rate.values())
                return f"{int(max_rate)}/turn"
            return "N/A"
        if col_id == 'paused':
            # FEAT-17: simple two-state indicator. Empty string for
            # unpaused yards keeps the column unobtrusive at a glance.
            return "PAUSED" if source.is_paused else ""
        if col_id in RESOURCE_RATE_COLS:
            return get_resource_rate_text(source, RESOURCE_RATE_COLS[col_id])
        if col_id in RESOURCE_TOTAL_COLS:
            return get_resource_total_text(source, RESOURCE_TOTAL_COLS[col_id])
        return ""

    # -----------------------------------------------------------------------
    # Internal Methods
    # -----------------------------------------------------------------------

    def _refresh(self) -> None:
        """Refresh the filtered source list."""
        self._filtered_sources = self._filter_mgr.filter_sources(self._all_sources)
        self._needs_refresh = False
