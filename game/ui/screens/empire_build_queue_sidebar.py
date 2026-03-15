"""Sidebar component for EmpireBuildQueueWindow.

Owns all filter and column toggle UI elements. Communicates with ViewModel
for state changes. One-way dependency: Sidebar -> ViewModel (not Window).

Created as part of PROJ-172 Phase 3.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pygame
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextEntryLine

from game.ui.components.filters.tri_state_widget import TriStateFilterWidget
from game.ui.config import UIConfig
from game.ui.filters.filter_state import FilterState

if TYPE_CHECKING:
    from game.ui.screens.empire_build_queue_viewmodel import EmpireBuildQueueViewModel
    from game.ui.screens.builder.event_bus import EventBus


# Tri-state filter definitions: (section_header, [(filter_key, label), ...])
_TRI_STATE_SECTIONS = [
    ('LOCATION TYPE', [
        ('loc_Planet', 'Planet'),
        ('loc_Fleet', 'Fleet'),
    ]),
    ('QUEUE STATUS', [
        ('status_Active', 'Active'),
        ('status_Empty', 'Empty'),
    ]),
    ('CAPABILITIES', [
        ('cap_Ships', 'Ships'),
        ('cap_Complexes', 'Complexes'),
    ]),
]


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
        self.tri_state_widgets: Dict[str, TriStateFilterWidget] = {}
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
        """Create tri-state filter widgets and search box."""
        # Start below column toggles
        y_off = 40 + len(self.columns) * 35 + 15

        # --- Tri-state filter sections ---
        for section_header, filters in _TRI_STATE_SECTIONS:
            UILabel(
                relative_rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
                text=section_header,
                manager=self.ui_manager,
                container=self.container,
            )
            y_off += 30
            for filter_key, label in filters:
                widget = TriStateFilterWidget(
                    attribute_name=filter_key,
                    label=label,
                    rect=pygame.Rect(10, y_off, self.sidebar_width, 25),
                    manager=self.ui_manager,
                    container=self.container,
                )
                self.tri_state_widgets[filter_key] = widget
                y_off += 30
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
        Note: Tri-state filter widgets are polled via check_tri_state_presses(),
        not through this event-based handler.

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

        return False

    def check_tri_state_presses(self) -> Optional[Tuple[str, FilterState]]:
        """Poll tri-state filter widgets for presses.

        Called from the window's update() loop. Returns the first
        widget press found, or None if no press occurred.

        Returns:
            Tuple of (filter_key, new_state) if a widget was pressed,
            or None if no press occurred.
        """
        for filter_key, widget in self.tri_state_widgets.items():
            new_state = widget.check_pressed()
            if new_state is not None:
                widget.set_state(new_state)
                self.viewmodel.set_filter_state(filter_key, new_state)
                self.viewmodel.apply_filters()
                return (filter_key, new_state)
        return None

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

    def _handle_apply_click(self) -> None:
        """Handle Apply Filters button click."""
        if self.search_entry is not None:
            self.viewmodel.set_search_text(self.search_entry.get_text())
        self.viewmodel.apply_filters()

