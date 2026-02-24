"""Sidebar component for EmpireBuildQueueWindow.

Owns all filter and column toggle UI elements. Communicates with ViewModel
for state changes. One-way dependency: Sidebar -> ViewModel (not Window).

Created as part of PROJ-172 Phase 3.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pygame
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextEntryLine

from game.ui.config import UIConfig

if TYPE_CHECKING:
    from game.ui.screens.empire_build_queue_viewmodel import EmpireBuildQueueViewModel
    from game.ui.screens.builder.event_bus import EventBus


class EmpireBuildQueueSidebar:
    """Sidebar component for column toggles and filters.

    Owns all sidebar UI elements:
    - Column visibility toggle buttons
    - Location type filter buttons
    - Queue status filter buttons
    - Capabilities filter buttons
    - Search text entry
    - Apply filters button

    Communicates state changes through ViewModel methods.

    Args:
        ui_manager: pygame_gui UIManager instance.
        parent_container: UI container (typically sidebar panel).
        viewmodel: EmpireBuildQueueViewModel for state management.
        event_bus: EventBus for UI event communication.
        columns: Column definition list from filter manager.
    """

    def __init__(
        self,
        ui_manager: Any,
        parent_container: UIPanel,
        viewmodel: EmpireBuildQueueViewModel,
        event_bus: EventBus,
        columns: List[Dict[str, Any]],
    ) -> None:
        self.ui_manager = ui_manager
        self.container = parent_container
        self.viewmodel = viewmodel
        self.event_bus = event_bus
        self.columns = columns

        self.sidebar_width = UIConfig.SIDEBAR_WIDTH - 20

        # UI element references
        self.column_toggle_buttons: Dict[str, UIButton] = {}
        self.filter_toggle_buttons: Dict[str, UIButton] = {}
        self.search_entry: Optional[UITextEntryLine] = None
        self.btn_apply_filters: Optional[UIButton] = None

        # Build UI
        self._build_column_toggles()
        self._build_filters()

    # -----------------------------------------------------------------------
    # UI Building
    # -----------------------------------------------------------------------

    def _build_column_toggles(self) -> None:
        """Create column visibility toggle buttons."""
        UILabel(
            relative_rect=pygame.Rect(10, 10, self.sidebar_width, 25),
            text="COLUMNS",
            manager=self.ui_manager,
            container=self.container,
        )

        y_off = 40
        for col in self.columns:
            prefix = "[x]" if col['visible'] else "[ ]"
            label = col['title'] or col['id']
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 30),
                text=f"{prefix} {label}",
                manager=self.ui_manager,
                container=self.container,
            )
            self.column_toggle_buttons[col['id']] = btn
            y_off += 35

    def _build_filters(self) -> None:
        """Create filter toggle buttons and search box."""
        # Start below column toggles
        y_off = 40 + len(self.columns) * 35 + 15

        # --- Location Type ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
            text="LOCATION TYPE",
            manager=self.ui_manager,
            container=self.container,
        )
        y_off += 30
        for key in ('Planet', 'Fleet'):
            prefix = "[x]" if self.viewmodel.filter_location_type[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 30),
                text=f"{prefix} {key}",
                manager=self.ui_manager,
                container=self.container,
            )
            self.filter_toggle_buttons[f"loc_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Queue Status ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
            text="QUEUE STATUS",
            manager=self.ui_manager,
            container=self.container,
        )
        y_off += 30
        for key in ('Active', 'Empty'):
            prefix = "[x]" if self.viewmodel.filter_status[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 30),
                text=f"{prefix} {key}",
                manager=self.ui_manager,
                container=self.container,
            )
            self.filter_toggle_buttons[f"status_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Capabilities ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
            text="CAPABILITIES",
            manager=self.ui_manager,
            container=self.container,
        )
        y_off += 30
        for key in ('Ships', 'Complexes'):
            prefix = "[x]" if self.viewmodel.filter_capabilities[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 30),
                text=f"{prefix} {key}",
                manager=self.ui_manager,
                container=self.container,
            )
            self.filter_toggle_buttons[f"cap_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Text Search ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
            text="SEARCH",
            manager=self.ui_manager,
            container=self.container,
        )
        y_off += 30
        self.search_entry = UITextEntryLine(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 30),
            manager=self.ui_manager,
            container=self.container,
        )
        y_off += 40

        # --- Apply Button ---
        self.btn_apply_filters = UIButton(
            relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 35),
            text="Apply Filters",
            manager=self.ui_manager,
            container=self.container,
        )

    # -----------------------------------------------------------------------
    # Event Handling
    # -----------------------------------------------------------------------

    def handle_button_click(self, button: UIButton) -> bool:
        """Handle a UI button click event.

        Checks if button is one of the sidebar buttons and processes it.

        Args:
            button: The UIButton that was clicked.

        Returns:
            True if the button was handled by the sidebar, False otherwise.
        """
        # Check apply button
        if button is self.btn_apply_filters:
            self._handle_apply_click()
            return True

        # Check column toggles
        for col_id, btn in self.column_toggle_buttons.items():
            if btn is button:
                self._handle_column_toggle(col_id)
                return True

        # Check filter toggles
        for filter_key, btn in self.filter_toggle_buttons.items():
            if btn is button:
                self._handle_filter_toggle(filter_key)
                return True

        return False

    def _handle_column_toggle(self, col_id: str) -> None:
        """Handle column toggle button click.

        Args:
            col_id: ID of the column to toggle.
        """
        # Find and toggle column in config
        for col in self.columns:
            if col['id'] == col_id:
                col['visible'] = not col['visible']
                # Update button text
                btn = self.column_toggle_buttons[col_id]
                prefix = "[x]" if col['visible'] else "[ ]"
                label = col['title'] or col['id']
                btn.set_text(f"{prefix} {label}")
                return

    def _handle_filter_toggle(self, filter_key: str) -> None:
        """Handle filter toggle button click.

        Args:
            filter_key: Filter key (e.g., "loc_Planet").
        """
        new_state = self.viewmodel.toggle_filter(filter_key)

        # Update button text
        btn = self.filter_toggle_buttons[filter_key]
        parts = filter_key.split("_", 1)
        value = parts[1] if len(parts) > 1 else filter_key
        prefix = "[x]" if new_state else "[ ]"
        btn.set_text(f"{prefix} {value}")

        # Apply filters immediately on toggle
        self.viewmodel.apply_filters()

    def _handle_apply_click(self) -> None:
        """Handle Apply Filters button click."""
        if self.search_entry is not None:
            self.viewmodel.set_search_text(self.search_entry.get_text())
        self.viewmodel.apply_filters()

    # -----------------------------------------------------------------------
    # Column State Access (for window to rebuild headers)
    # -----------------------------------------------------------------------

    def get_column_visibility_changed(self) -> bool:
        """Check if column visibility needs UI rebuild.

        Note: This is a simple flag check - window calls this after
        handle_button_click returns True for a column toggle.

        Returns:
            True if column visibility was toggled in last button click.
        """
        # Currently handled synchronously - window rebuilds immediately
        # after handle_button_click returns True for column toggle
        return False
