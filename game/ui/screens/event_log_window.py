"""Event Log Window - Displays game events with category filter tabs.

PROJ-77 Phase 4: Modal window showing turn events (production, colonies, combat).
PROJ-188 Phase 5: Migrated to VirtualTable with EventLogDataSource.
Supports filter tabs and scrollable event list sorted newest first.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIPanel, UIButton

from game.ui.components.table import VirtualTable, TableColumnManager, NoSelect
from game.ui.screens.event_log_data_source import (
    EventLogDataSource,
    EVENT_LOG_COLUMNS,
)


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
HEADER_HEIGHT = 50
ROW_HEIGHT = 28
TABLE_HEADER_HEIGHT = 30
FILTER_BTN_WIDTH = 100
FILTER_BTN_HEIGHT = 32
FILTER_GAP = 8


class EventLogWindow(UIWindow):
    """Modal window displaying game events with filter tabs.

    Shows events in a scrollable list sorted newest-first.
    Filter tabs allow viewing All, Combat, Production, or Colonies events.

    Args:
        rect: Window position and size.
        manager: pygame_gui UIManager instance.
        events: List of event dicts (from facade).
        on_close_callback: Called when the window is closed.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: Any,
        events: list[dict],
        on_close_callback: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title="Event Log",
            resizable=True,
        )
        self.all_events = list(events)
        self.current_filter = "all"
        self.on_close_callback = on_close_callback

        # VirtualTable components
        self.data_source: Optional[EventLogDataSource] = None
        self.column_manager: Optional[TableColumnManager] = None
        self.virtual_table: Optional[VirtualTable] = None

        # --- Build UI ---
        self._init_layout()
        self._rebuild_list()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _init_layout(self) -> None:
        """Create filter header and table panel with VirtualTable."""
        window_rect = self.get_container().get_rect()
        content_height = window_rect.height - 50  # title bar offset

        # Header panel with filter buttons
        self.header_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, window_rect.width, HEADER_HEIGHT),
            manager=self.ui_manager,
            container=self,
            anchors={"left": "left", "right": "right", "top": "top"},
        )
        self._create_filter_buttons()

        # Table panel below header (contains VirtualTable)
        table_height = content_height - HEADER_HEIGHT
        self.table_panel = UIPanel(
            relative_rect=pygame.Rect(0, HEADER_HEIGHT, window_rect.width, table_height),
            manager=self.ui_manager,
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        # Create VirtualTable components
        self.data_source = EventLogDataSource(self.all_events, self.current_filter)
        self.column_manager = TableColumnManager(EVENT_LOG_COLUMNS)
        self.virtual_table = VirtualTable(
            self.table_panel,
            self.ui_manager,
            self.data_source,
            self.column_manager,
            NoSelect(),
            row_height=ROW_HEIGHT,
            header_height=TABLE_HEADER_HEIGHT,
        )

    def _create_filter_buttons(self) -> None:
        """Create filter tab buttons in the header."""
        x = 10
        y = (HEADER_HEIGHT - FILTER_BTN_HEIGHT) // 2

        self.btn_all = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="All",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_combat = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Combat",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_production = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Production",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_colonies = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Colonies",
            manager=self.ui_manager,
            container=self.header_panel,
        )

        self.filter_buttons = {
            "all": self.btn_all,
            "combat": self.btn_combat,
            "production": self.btn_production,
            "colonies": self.btn_colonies,
        }

        # Highlight the default active filter
        self.btn_all.select()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def get_filtered_events(self) -> list[dict]:
        """Return events matching current filter, sorted newest first.

        Delegates to DataSource for consistency.

        Returns:
            Filtered and sorted list of event dicts.
        """
        if self.data_source:
            # Delegate to data source's filtered list
            return [
                self.data_source.get_event_at_index(i)
                for i in range(self.data_source.get_row_count())
            ]

        # Fallback for tests without VirtualTable
        if self.current_filter == "all":
            filtered = list(self.all_events)
        else:
            filtered = [
                e for e in self.all_events if e.get("category") == self.current_filter
            ]
        filtered.sort(key=lambda e: e.get("turn", 0), reverse=True)
        return filtered

    def set_filter(self, category: str) -> None:
        """Switch the active filter category.

        Args:
            category: One of 'all', 'combat', 'production', 'colonies'.
        """
        self.current_filter = category
        if self.data_source:
            self.data_source.set_filter(category)

    # ------------------------------------------------------------------
    # List Rendering
    # ------------------------------------------------------------------

    def _rebuild_list(self) -> None:
        """Update VirtualTable with current filter."""
        if self.data_source:
            self.data_source.set_filter(self.current_filter)
        if self.virtual_table:
            self.virtual_table.update_scroll_bar()
            self.virtual_table.force_update()
            self.virtual_table.update_visible_rows()

    def _update_filter_buttons(self) -> None:
        """Highlight the currently active filter button."""
        for key, btn in self.filter_buttons.items():
            if key == self.current_filter:
                btn.select()
            else:
                btn.unselect()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events for filter button clicks."""
        handled = super().process_event(event)

        if hasattr(event, "type") and event.type == pygame_gui.UI_BUTTON_PRESSED:
            clicked = getattr(event, "ui_element", None)
            for key, btn in self.filter_buttons.items():
                if clicked is btn:
                    self.set_filter(key)
                    self._update_filter_buttons()
                    self._rebuild_list()
                    handled = True
                    break

        return handled

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def kill(self) -> None:
        """Clean up and invoke close callback."""
        if self.virtual_table:
            self.virtual_table.kill()
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
