"""Event Log Sidebar - Column toggle sidebar for Event Log Window.

PROJ-215 Phase 3: Sidebar component providing column visibility toggles
following the FleetReportSidebar pattern.
"""
from typing import Callable, Dict, Optional

import pygame
from pygame_gui.elements import UIPanel, UILabel, UIButton


class EventLogSidebar:
    """
    Sidebar component for EventLogWindow containing column visibility toggles.

    This is a UI component, not a UIElement - it creates and manages
    a collection of pygame_gui elements within a container panel.
    """

    def __init__(
        self,
        panel: UIPanel,
        manager,
        column_manager,
        on_column_toggle: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the sidebar component.

        Args:
            panel: The UIPanel container to build widgets in.
            manager: pygame_gui UIManager.
            column_manager: TableColumnManager for column visibility.
            on_column_toggle: Callback when a column is toggled. Receives column_id.
        """
        self.panel = panel
        self.manager = manager
        self.column_manager = column_manager
        self.on_column_toggle = on_column_toggle

        # Panel width for layout
        self.sidebar_width = panel.get_relative_rect().width

        # Widget collections
        self.column_buttons: Dict[str, UIButton] = {}

        # Build all widgets
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Build all sidebar widgets."""
        y = 10

        # Column toggle section
        y = self._build_column_section(y)

    def _build_column_section(self, y: int) -> int:
        """Build column visibility toggle buttons.

        Args:
            y: Starting y position.

        Returns:
            Updated y position after building section.
        """
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="COLUMNS",
            manager=self.manager,
            container=self.panel,
        )
        y += 35

        # Column visibility toggles
        for col in self.column_manager.get_toggleable_columns():
            col_id = col["id"]
            title = col["title"] or col_id
            is_visible = col.get("visible", True)
            btn_text = f"[x] {title}" if is_visible else f"[ ] {title}"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                text=btn_text,
                manager=self.manager,
                container=self.panel,
                object_id=f"#column_{col_id}",
            )
            btn.col_ref = col  # Store reference to column config
            self.column_buttons[col_id] = btn
            y += 30

        y += 20
        return y

    def handle_button_click(self, ui_element) -> Optional[str]:
        """Check if clicked element is a column toggle button.

        Args:
            ui_element: The clicked UI element.

        Returns:
            Column ID if a column button was clicked, None otherwise.
        """
        if ui_element is None:
            return None

        for col_id, btn in self.column_buttons.items():
            if ui_element is btn:
                return col_id

        return None

    def refresh_button_labels(self) -> None:
        """Update button labels to reflect current column visibility state."""
        for col_id, btn in self.column_buttons.items():
            col = btn.col_ref
            title = col["title"] or col_id
            is_visible = self.column_manager.is_column_visible(col_id)
            btn_text = f"[x] {title}" if is_visible else f"[ ] {title}"
            btn.set_text(btn_text)
