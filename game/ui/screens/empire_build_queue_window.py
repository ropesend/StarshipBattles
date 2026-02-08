"""Empire-wide build queue window.

Shows all space yards (planet shipyards and fleet yards) across the entire
empire in a unified, scrollable list. Provides queue summary info and
navigation to individual hex build screens.

Created as part of PROJ-76 Phase 2.
"""
from __future__ import annotations

from typing import Any, Callable, List, Optional, TYPE_CHECKING

import pygame
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIVerticalScrollBar

from game.core.config import UIConfig
from game.core.logger import log_debug
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_all_build_queues_for_empire,
)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire


class EmpireBuildQueueWindow(UIWindow):
    """Window showing all empire build queues in a scrollable list.

    Displays every space yard (planet base queues, planetary shipyard
    facilities, fleet space yards) with queue summary info. Clicking a
    row selects it; navigation to the hex build screen is handled via
    callback in a later phase.

    Args:
        rect: Window rectangle on screen.
        manager: pygame_gui UIManager instance.
        empire: Empire whose queues to display.
        galaxy: Galaxy instance for system name lookups.
        on_close_callback: Called when window is closed.
        on_navigate_to_hex: Called with (hex_coord, source) when user
            navigates to a specific queue.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: Any,
        empire: Empire,
        galaxy: Any,
        on_close_callback: Optional[Callable] = None,
        on_navigate_to_hex: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            rect, manager,
            window_display_title="Empire Build Queues",
            resizable=True,
        )

        self.empire = empire
        self.galaxy = galaxy
        self.on_close_callback = on_close_callback
        self.on_navigate_to_hex = on_navigate_to_hex

        # --- Layout constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State ---
        self.all_sources: List[BuildQueueSource] = collect_all_build_queues_for_empire(empire)
        self.filtered_sources: List[BuildQueueSource] = list(self.all_sources)
        self.selected_source: Optional[BuildQueueSource] = None
        self.selected_index: int = -1
        self.row_elements: list = []

        # --- UI Containers ---
        # Sidebar (filters - placeholder for Phase 4)
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )

        # Main content area
        main_w = rect.width - self.sidebar_width - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Header row for column titles
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, main_w, self.header_height),
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'},
        )
        self._build_header_labels(manager, main_w)

        # Scrollable list area
        self.list_view_rect = pygame.Rect(
            0, self.header_height,
            main_w - 20, rect.height - 50 - self.header_height,
        )
        self.list_panel = UIPanel(
            relative_rect=self.list_view_rect,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Vertical scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(
                -20, self.header_height, 20, self.list_view_rect.height,
            ),
            visible_percentage=1.0,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Initial population
        self._refresh_list()

    # -------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------

    def _build_header_labels(self, manager: Any, main_w: int) -> None:
        """Create column title labels in the header."""
        x = 10
        cols = [
            ("Location", 200),
            ("Items", 80),
            ("Building", 150),
            ("Can Build", 120),
        ]
        for title, width in cols:
            UILabel(
                relative_rect=pygame.Rect(x, 5, width, 30),
                text=title,
                manager=manager,
                container=self.header_container,
            )
            x += width + 10

    # -------------------------------------------------------------------
    # List Population
    # -------------------------------------------------------------------

    def _refresh_list(self) -> None:
        """Rebuild the visible row list from filtered_sources."""
        # Kill existing row elements
        for elem in self.row_elements:
            elem.kill()
        self.row_elements.clear()

        # Update scrollbar
        total_h = len(self.filtered_sources) * self.row_height
        visible_h = self.list_view_rect.height
        percentage = min(1.0, visible_h / total_h) if total_h > 0 else 1.0
        self.scroll_bar.set_visible_percentage(percentage)
        self.scroll_bar.scroll_position = 0.0
        self.scroll_bar.bottom_limit = max(visible_h, total_h)
        self.scroll_bar.redraw_scrollbar()

        # Create row labels
        for i, source in enumerate(self.filtered_sources):
            y = i * self.row_height
            x = 10

            # Location name
            lbl_name = UILabel(
                relative_rect=pygame.Rect(x, y, 200, self.row_height),
                text=source.display_name,
                manager=self.ui_manager,
                container=self.list_panel,
            )
            self.row_elements.append(lbl_name)
            x += 210

            # Queue count
            summary = self._get_queue_summary(source)
            lbl_count = UILabel(
                relative_rect=pygame.Rect(x, y, 80, self.row_height),
                text=summary,
                manager=self.ui_manager,
                container=self.list_panel,
            )
            self.row_elements.append(lbl_count)
            x += 90

            # First item building
            first_item = self._get_first_item_text(source)
            lbl_building = UILabel(
                relative_rect=pygame.Rect(x, y, 150, self.row_height),
                text=first_item,
                manager=self.ui_manager,
                container=self.list_panel,
            )
            self.row_elements.append(lbl_building)
            x += 160

            # Capabilities
            caps = self._get_capabilities_text(source)
            lbl_caps = UILabel(
                relative_rect=pygame.Rect(x, y, 120, self.row_height),
                text=caps,
                manager=self.ui_manager,
                container=self.list_panel,
            )
            self.row_elements.append(lbl_caps)

    # -------------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------------

    def _select_source(self, index: int) -> None:
        """Select a source by index in filtered_sources.

        Args:
            index: Index into filtered_sources. Invalid indices are ignored.
        """
        if index < 0 or index >= len(self.filtered_sources):
            return
        self.selected_index = index
        self.selected_source = self.filtered_sources[index]
        log_debug(f"Selected queue source: {self.selected_source.display_name}")

    # -------------------------------------------------------------------
    # Event Handling
    # -------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on rows."""
        handled = super().process_event(event)

        # Row click detection
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = event.pos
            list_abs_rect = self.list_panel.get_abs_rect()

            if list_abs_rect.collidepoint(mouse_pos):
                # Calculate which row was clicked
                scroll_offset = 0.0
                total_h = len(self.filtered_sources) * self.row_height
                if total_h > 0:
                    scroll_offset = self.scroll_bar.start_percentage * total_h

                local_y = mouse_pos[1] - list_abs_rect.y + scroll_offset
                clicked_index = int(local_y // self.row_height)

                if 0 <= clicked_index < len(self.filtered_sources):
                    self._select_source(clicked_index)
                    return True

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if self.list_panel.get_abs_rect().collidepoint(m_pos):
                total_h = len(self.filtered_sources) * self.row_height
                if total_h > 0:
                    row_percent = self.row_height / total_h
                    current_pct = self.scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - self.scroll_bar.visible_percentage, new_pct))
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)
                return True

        return handled

    def update(self, time_delta: float) -> None:
        """Update loop - check scrollbar changes."""
        super().update(time_delta)

        if self.scroll_bar.check_has_moved_recently():
            # Future: update visible rows for virtual scrolling
            pass

    # -------------------------------------------------------------------
    # Data Formatters
    # -------------------------------------------------------------------

    @staticmethod
    def _get_queue_summary(source: BuildQueueSource) -> str:
        """Return a short summary of queue contents.

        Args:
            source: The build queue source to summarize.

        Returns:
            Dash if empty, otherwise item count string.
        """
        count = len(source.construction_queue)
        if count == 0:
            return "-"
        return f"{count} item{'s' if count != 1 else ''}"

    @staticmethod
    def _get_first_item_text(source: BuildQueueSource) -> str:
        """Return the name of the first item being built.

        Args:
            source: The build queue source.

        Returns:
            Design ID of first item, or dash if empty.
        """
        if not source.construction_queue:
            return "-"
        first = source.construction_queue[0]
        design_id = first.get("design_id", "Unknown")
        turns = first.get("turns_remaining", "?")
        return f"{design_id} ({turns}t)"

    @staticmethod
    def _get_capabilities_text(source: BuildQueueSource) -> str:
        """Return human-readable capabilities string.

        Args:
            source: The build queue source.

        Returns:
            'Ships', 'Complexes', 'Ships & Complexes', or 'None'.
        """
        if source.can_build_ships and source.can_build_complexes:
            return "Ships & Complexes"
        if source.can_build_ships:
            return "Ships"
        if source.can_build_complexes:
            return "Complexes"
        return "None"

    # -------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------

    def kill(self) -> None:
        """Clean up and invoke close callback."""
        for elem in self.row_elements:
            elem.kill()
        self.row_elements.clear()

        if self.on_close_callback:
            self.on_close_callback()

        super().kill()
