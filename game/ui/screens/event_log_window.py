"""Event Log Window - Displays game events with category filter tabs.

PROJ-77 Phase 4: Modal window showing turn events (production, colonies, combat).
Supports filter tabs and scrollable event list sorted newest first.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIVerticalScrollBar


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
HEADER_HEIGHT = 50
ROW_HEIGHT = 28
FILTER_BTN_WIDTH = 100
FILTER_BTN_HEIGHT = 32
FILTER_GAP = 8

# Category icons (text prefix for each category)
CATEGORY_ICONS = {
    "combat": "[Combat]",
    "production": "[Prod]",
    "colonies": "[Colony]",
}


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

        # --- Build UI ---
        self._init_layout()
        self._rebuild_list()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _init_layout(self) -> None:
        """Create filter header and scrollable list panels."""
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

        # List panel below header
        list_height = content_height - HEADER_HEIGHT
        self.list_panel = UIPanel(
            relative_rect=pygame.Rect(
                0, HEADER_HEIGHT, window_rect.width - 20, list_height
            ),
            manager=self.ui_manager,
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        # Scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, HEADER_HEIGHT, 20, list_height),
            visible_percentage=1.0,
            manager=self.ui_manager,
            container=self,
            anchors={
                "left": "right",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        self.row_labels: list[UILabel] = []

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

        Returns:
            Filtered and sorted list of event dicts.
        """
        if self.current_filter == "all":
            filtered = list(self.all_events)
        else:
            filtered = [
                e for e in self.all_events if e.get("category") == self.current_filter
            ]
        # Sort newest first (descending by turn)
        filtered.sort(key=lambda e: e.get("turn", 0), reverse=True)
        return filtered

    def set_filter(self, category: str) -> None:
        """Switch the active filter category.

        Args:
            category: One of 'all', 'combat', 'production', 'colonies'.
        """
        self.current_filter = category

    # ------------------------------------------------------------------
    # List Rendering
    # ------------------------------------------------------------------

    def _rebuild_list(self) -> None:
        """Clear and repopulate the event row labels."""
        # Clear existing rows
        for lbl in self.row_labels:
            lbl.kill()
        self.row_labels.clear()

        events = self.get_filtered_events()
        panel_rect = self.list_panel.get_relative_rect()
        row_width = panel_rect.width - 10

        for i, evt in enumerate(events):
            y = i * ROW_HEIGHT
            category = evt.get("category", "")
            icon = CATEGORY_ICONS.get(category, "")
            turn = evt.get("turn", "?")
            message = evt.get("message", "")
            text = f" {icon} Turn {turn}: {message}"

            lbl = UILabel(
                relative_rect=pygame.Rect(5, y, row_width, ROW_HEIGHT),
                text=text,
                manager=self.ui_manager,
                container=self.list_panel,
            )
            self.row_labels.append(lbl)

        # Update scrollbar
        total_height = max(1, len(events) * ROW_HEIGHT)
        visible_height = panel_rect.height
        visible_pct = min(1.0, visible_height / total_height)
        self.scroll_bar.set_visible_percentage(visible_pct)

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
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
