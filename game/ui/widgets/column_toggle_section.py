"""Shared column-toggle section builder for sidebars.

Extracted in PROJ-319 (DUP-X-08) to remove the duplicated
`_build_column_section` method that previously lived in both
`EventLogSidebar` and `FleetReportSidebar`.
"""
from typing import Any, Dict, Tuple

import pygame
from pygame_gui.elements import UILabel, UIButton


def build_column_toggle_section(
    y: int,
    column_manager: Any,
    sidebar_width: int,
    manager: Any,
    container: Any,
    label_text: str = "COLUMNS",
) -> Tuple[int, Dict[str, UIButton]]:
    """Build a label plus per-column toggle buttons inside a sidebar panel.

    Args:
        y: Starting y position inside the sidebar panel.
        column_manager: Object exposing `get_toggleable_columns()` -> iterable of
            column dicts with keys "id", "title", and optional "visible".
        sidebar_width: Width of the sidebar panel (used for button width).
        manager: pygame_gui UIManager.
        container: Parent UIPanel.
        label_text: Section label (default "COLUMNS").

    Returns:
        (new_y, column_buttons_by_id) where new_y is the y position after the
        section (with trailing spacing) and column_buttons_by_id maps each
        toggleable column's id to its created UIButton (with `col_ref` set to
        the column config dict).
    """
    UILabel(
        relative_rect=pygame.Rect(10, y, sidebar_width - 20, 30),
        text=label_text,
        manager=manager,
        container=container,
    )
    y += 35

    column_buttons: Dict[str, UIButton] = {}
    for col in column_manager.get_toggleable_columns():
        col_id = col["id"]
        title = col["title"] or col_id
        is_visible = col.get("visible", True)
        btn_text = f"[x] {title}" if is_visible else f"[ ] {title}"
        btn = UIButton(
            relative_rect=pygame.Rect(10, y, sidebar_width - 20, 28),
            text=btn_text,
            manager=manager,
            container=container,
            object_id=f"#column_{col_id}",
        )
        btn.col_ref = col
        column_buttons[col_id] = btn
        y += 30

    y += 20
    return y, column_buttons
