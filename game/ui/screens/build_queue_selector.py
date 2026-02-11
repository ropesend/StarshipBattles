"""
Build Queue Selector - Queue source selection panel.

Manages the queue selector column UI for BuildQueueScreen.
Extracted from BuildQueueScreen (PROJ-86 Phase 8).
"""
from __future__ import annotations

import pygame
import pygame_gui.elements as ui
from typing import TYPE_CHECKING, List, Callable, Set, Optional

from game.core.logger import log_info

if TYPE_CHECKING:
    import pygame_gui
    from game.strategy.data.build_queue_source import BuildQueueSource


class BuildQueueSelector:
    """Manages the queue selector panel for choosing active build queue(s).

    PROJ-69: Panel showing all build queue sources at the hex,
    allowing single-click selection or ctrl+click multi-selection.
    """

    def __init__(
        self,
        manager: 'pygame_gui.UIManager',
        container: ui.UIPanel,
        rect: pygame.Rect,
        queue_sources: List['BuildQueueSource'],
        on_selection_changed: Callable[['BuildQueueSource', Set[int]], None],
    ):
        """Initialize the queue selector.

        Args:
            manager: pygame_gui UIManager
            container: Parent container panel
            rect: Rectangle for the selector panel
            queue_sources: List of available queue sources
            on_selection_changed: Callback(active_source, selected_indices)
        """
        self.manager = manager
        self.queue_sources = queue_sources
        self._on_selection_changed = on_selection_changed

        # Selection state
        self.selected_indices: Set[int] = {0} if queue_sources else set()
        self.active_source: Optional['BuildQueueSource'] = (
            queue_sources[0] if queue_sources else None
        )

        # Create panel
        self.panel = ui.UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        panel_width = rect.width
        panel_height = rect.height

        # Header
        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Build Yards</b>",
            manager=manager,
            container=self.panel
        )

        # Scrollable container for queue entries
        self.scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(5, 45, panel_width - 10, panel_height - 55),
            manager=manager,
            container=self.panel
        )

        # Store buttons for event handling
        self.buttons: List[ui.UIButton] = []

        self.refresh()

    def refresh(self) -> None:
        """Rebuild queue selector UI elements to reflect current selection state."""
        # Clear existing selector entries
        elements_to_kill = list(self.scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()
        self.buttons.clear()

        row_height = 30
        row_width = self.panel.get_relative_rect().width - 20
        y_offset = 0

        for idx, source in enumerate(self.queue_sources):
            is_selected = idx in self.selected_indices
            item_count = len(source.construction_queue)

            # Display name with item count and build rate on single line
            prefix = "> " if is_selected else "  "
            rate_display = int(max(source.build_rate.values())) if source.build_rate else 0
            label_text = f"{prefix}{source.display_name} ({item_count} items, {rate_display}/turn)"

            # Use object_id to distinguish selected vs unselected visually
            object_id = "#queue_selector_selected" if is_selected else "#queue_selector_item"

            btn = ui.UIButton(
                relative_rect=pygame.Rect(0, y_offset, row_width, row_height),
                text=label_text,
                manager=self.manager,
                container=self.scrollable,
                object_id=object_id
            )
            btn.queue_source_index = idx  # Tag button with source index

            self.buttons.append(btn)
            y_offset += row_height + 5

        if not self.queue_sources:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, row_width, 30),
                text="No queues available",
                manager=self.manager,
                container=self.scrollable
            )

    def handle_button_click(self, button: ui.UIButton, ctrl_held: bool) -> bool:
        """Handle click on a queue selector button.

        Args:
            button: The clicked button element
            ctrl_held: Whether ctrl modifier is held

        Returns:
            True if the button was handled, False if not a selector button
        """
        if not hasattr(button, 'queue_source_index'):
            return False

        idx = button.queue_source_index
        if ctrl_held:
            self._on_queue_toggled(idx)
        else:
            self._on_queue_selected(idx)
        return True

    def _on_queue_selected(self, index: int) -> None:
        """Handle single-click queue selection (deselects others).

        Args:
            index: Index into queue_sources to select.
        """
        self.selected_indices = {index}
        self.active_source = self.queue_sources[index]
        log_info(f"BuildQueue: Selected queue '{self.active_source.display_name}'")
        self.refresh()
        self._on_selection_changed(self.active_source, self.selected_indices)

    def _on_queue_toggled(self, index: int) -> None:
        """Handle ctrl+click queue toggle for multi-select.

        Args:
            index: Index into queue_sources to toggle.
        """
        if index in self.selected_indices:
            self.selected_indices.discard(index)
        else:
            self.selected_indices.add(index)

        # Prevent empty selection
        if not self.selected_indices:
            self.selected_indices = {0}

        # Set active source based on selection count
        if len(self.selected_indices) == 1:
            sole_idx = next(iter(self.selected_indices))
            self.active_source = self.queue_sources[sole_idx]
            log_info(f"BuildQueue: Single queue selected: '{self.active_source.display_name}'")
        else:
            self.active_source = None
            log_info(f"BuildQueue: Multi-select mode: {len(self.selected_indices)} queues")

        self.refresh()
        self._on_selection_changed(self.active_source, self.selected_indices)

    def get_selected_sources(self) -> List['BuildQueueSource']:
        """Get list of currently selected queue sources."""
        return [self.queue_sources[i] for i in sorted(self.selected_indices)]
