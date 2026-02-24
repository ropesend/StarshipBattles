"""ViewModel for BuildQueueScreen.

Manages UI state for build queue screen: selection, queue sources, and category filter.
Emits events through EventBus for UI updates. No Pygame dependencies.

Created as part of PROJ-172 Phase 4.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Set

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.ui.screens.builder.event_bus import EventBus


class BuildQueueScreenEvents:
    """Event type constants for BuildQueueScreenViewModel."""

    QUEUE_LOADED = "build_queue_screen.queue_loaded"
    SELECTION_CHANGED = "build_queue_screen.selection_changed"
    QUEUE_REFRESHED = "build_queue_screen.queue_refreshed"
    CATEGORY_CHANGED = "build_queue_screen.category_changed"
    ACTIVE_SOURCE_CHANGED = "build_queue_screen.active_source_changed"


class BuildQueueScreenViewModel:
    """ViewModel managing UI state for BuildQueueScreen.

    Handles:
    - Queue item selection state
    - Active queue source tracking
    - Multi-select mode support
    - Design category filter
    - Event emission for UI updates

    No Pygame imports - independently testable.

    Args:
        event_bus: EventBus for emitting state change events.
        queue_sources: Initial list of BuildQueueSource objects at this hex.
    """

    def __init__(
        self,
        event_bus: 'EventBus',
        queue_sources: List['BuildQueueSource'] = None,
    ) -> None:
        self._event_bus = event_bus

        # Queue source data
        self._queue_sources: List['BuildQueueSource'] = list(queue_sources) if queue_sources else []

        # Selection state
        self._selected_queue_index: Optional[int] = None
        self._selected_queue_indices: Set[int] = {0} if self._queue_sources else set()
        self._active_queue_source: Optional['BuildQueueSource'] = (
            self._queue_sources[0] if self._queue_sources else None
        )

        # Category filter
        self._selected_category: str = "complex"

    # -----------------------------------------------------------------------
    # Properties - Queue Sources
    # -----------------------------------------------------------------------

    @property
    def queue_sources(self) -> List['BuildQueueSource']:
        """All available queue sources at this hex."""
        return self._queue_sources

    @property
    def queue_source_count(self) -> int:
        """Number of available queue sources."""
        return len(self._queue_sources)

    # -----------------------------------------------------------------------
    # Properties - Active Queue Source
    # -----------------------------------------------------------------------

    @property
    def active_queue_source(self) -> Optional['BuildQueueSource']:
        """Currently active queue source for single-select mode.

        Returns None when in multi-select mode (multiple indices selected).
        """
        return self._active_queue_source

    @property
    def selected_queue_indices(self) -> Set[int]:
        """Set of selected queue source indices."""
        return self._selected_queue_indices

    @property
    def is_multi_select(self) -> bool:
        """True if multiple queue sources are selected."""
        return len(self._selected_queue_indices) > 1

    # -----------------------------------------------------------------------
    # Properties - Queue Item Selection
    # -----------------------------------------------------------------------

    @property
    def selected_queue_index(self) -> Optional[int]:
        """Currently selected item index within the active queue.

        None if no item is selected.
        """
        return self._selected_queue_index

    # -----------------------------------------------------------------------
    # Properties - Category Filter
    # -----------------------------------------------------------------------

    @property
    def selected_category(self) -> str:
        """Current design category filter."""
        return self._selected_category

    # -----------------------------------------------------------------------
    # Queue Source Selection Methods
    # -----------------------------------------------------------------------

    def select_queue_source(self, index: int, ctrl_held: bool = False) -> None:
        """Select a queue source by index.

        Single click (ctrl_held=False): select only this index.
        Ctrl+click: toggle this index in the selection set.

        Args:
            index: Index into queue_sources.
            ctrl_held: True if Ctrl key was held.
        """
        if index < 0 or index >= len(self._queue_sources):
            return

        if ctrl_held:
            if index in self._selected_queue_indices:
                # Don't allow deselecting the last item
                if len(self._selected_queue_indices) > 1:
                    self._selected_queue_indices.discard(index)
            else:
                self._selected_queue_indices.add(index)
        else:
            self._selected_queue_indices = {index}

        # Update active source (single-select mode only)
        if len(self._selected_queue_indices) == 1:
            sole_idx = next(iter(self._selected_queue_indices))
            self._active_queue_source = self._queue_sources[sole_idx]
        else:
            self._active_queue_source = None

        # Clear item selection when queue source changes
        self._selected_queue_index = None

        self._event_bus.emit(BuildQueueScreenEvents.ACTIVE_SOURCE_CHANGED, {
            'active_source': self._active_queue_source,
            'selected_indices': self._selected_queue_indices,
        })

    def get_selected_sources(self) -> List['BuildQueueSource']:
        """Return BuildQueueSource objects for all selected indices.

        Returns:
            List of selected sources, in index order.
        """
        return [
            self._queue_sources[i]
            for i in sorted(self._selected_queue_indices)
            if 0 <= i < len(self._queue_sources)
        ]

    # -----------------------------------------------------------------------
    # Queue Item Selection Methods
    # -----------------------------------------------------------------------

    def select_queue_item(self, index: Optional[int]) -> None:
        """Select a queue item by index.

        Args:
            index: Index of item in active queue, or None to deselect.
        """
        old_index = self._selected_queue_index
        self._selected_queue_index = index

        if old_index != index:
            self._event_bus.emit(BuildQueueScreenEvents.SELECTION_CHANGED, {
                'selected_index': index,
                'previous_index': old_index,
            })

    def clear_item_selection(self) -> None:
        """Clear queue item selection."""
        self.select_queue_item(None)

    # -----------------------------------------------------------------------
    # Category Filter Methods
    # -----------------------------------------------------------------------

    def set_category(self, category: str) -> None:
        """Set the design category filter.

        Args:
            category: One of "complex", "ship", "satellite", "fighter".
        """
        old_category = self._selected_category
        self._selected_category = category

        if old_category != category:
            self._event_bus.emit(BuildQueueScreenEvents.CATEGORY_CHANGED, {
                'category': category,
                'previous_category': old_category,
            })

    # -----------------------------------------------------------------------
    # Queue Data Access
    # -----------------------------------------------------------------------

    def get_active_queue(self) -> list:
        """Return the construction queue list for the active source.

        Returns:
            The construction_queue list from the active source,
            or empty list if no source is active.
        """
        if self._active_queue_source is not None:
            return self._active_queue_source.construction_queue
        return []

    def get_queue_item(self, index: int) -> Optional[dict]:
        """Get a queue item by index from the active queue.

        Args:
            index: Index into the active queue.

        Returns:
            Queue item dict, or None if index is invalid.
        """
        queue = self.get_active_queue()
        if 0 <= index < len(queue):
            return queue[index]
        return None

    def get_selected_queue_item(self) -> Optional[dict]:
        """Get the currently selected queue item.

        Returns:
            The selected queue item dict, or None if nothing selected.
        """
        if self._selected_queue_index is not None:
            return self.get_queue_item(self._selected_queue_index)
        return None

    # -----------------------------------------------------------------------
    # Notification Methods
    # -----------------------------------------------------------------------

    def notify_queue_refreshed(self) -> None:
        """Notify that the queue contents have changed.

        Call this after add/remove operations to trigger UI refresh.
        """
        self._event_bus.emit(BuildQueueScreenEvents.QUEUE_REFRESHED, {
            'active_source': self._active_queue_source,
            'queue_length': len(self.get_active_queue()),
        })
