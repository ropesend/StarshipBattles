"""Table header component with sortable, reorderable columns.

Renders column headers with:
- Title buttons (clickable to sort)
- Arrow buttons (clickable to reorder)
- Sort direction indicators (▲/▼)
"""

from typing import Any, Dict, List, Optional

import pygame
from pygame_gui.elements import UIButton, UIPanel

from game.ui.components.table.column_manager import TableColumnManager


class TableHeader:
    """Renders and manages table column headers.

    Creates three buttons per column:
    - Left arrow (move column left)
    - Title (sort by column)
    - Right arrow (move column right)

    Edge columns omit their boundary arrows.
    """

    ARROW_WIDTH = 20

    def __init__(
        self,
        panel: UIPanel,
        manager,
        column_manager: TableColumnManager,
        header_height: int = 40,
    ) -> None:
        """Initialize the table header.

        Args:
            panel: The UIPanel container for header buttons.
            manager: pygame_gui UIManager.
            column_manager: TableColumnManager for column config.
            header_height: Height of header row in pixels.
        """
        self._panel = panel
        self._manager = manager
        self._column_manager = column_manager
        self._header_height = header_height
        self._header_elements: List[UIButton] = []

        self.rebuild()

    def rebuild(self) -> None:
        """Rebuild all header buttons.

        Clears existing widgets and creates new ones based on
        current visible columns and sort state.
        """
        # Clear existing
        for widget in self._header_elements:
            widget.kill()
        self._header_elements = []

        visible_cols = self._column_manager.get_visible_columns()
        arrow_w = self.ARROW_WIDTH

        x = 0
        for vis_idx, col in enumerate(visible_cols):
            width = col.get("width", 100)
            title_w = width - (arrow_w * 2)

            # Left Arrow (not for first column)
            if vis_idx > 0:
                btn_l = UIButton(
                    relative_rect=pygame.Rect(x, 0, arrow_w, self._header_height),
                    text="<",
                    manager=self._manager,
                    container=self._panel,
                )
                btn_l.col_ref = col
                btn_l.direction = -1
                self._header_elements.append(btn_l)

            # Sort indicator
            sort_indicator = ""
            if col["id"] == self._column_manager.sort_column_id:
                sort_indicator = " ▼" if self._column_manager.sort_descending else " ▲"

            # Title button (sortable)
            label = col.get("label", col.get("title", col["id"]))
            btn = UIButton(
                relative_rect=pygame.Rect(
                    x + arrow_w, 0, title_w, self._header_height
                ),
                text=label + sort_indicator,
                manager=self._manager,
                container=self._panel,
                object_id=f"#header_{col['id']}",
            )
            btn.sort_col_ref = col
            self._header_elements.append(btn)

            # Right Arrow (not for last column)
            if vis_idx < len(visible_cols) - 1:
                btn_r = UIButton(
                    relative_rect=pygame.Rect(
                        x + width - arrow_w, 0, arrow_w, self._header_height
                    ),
                    text=">",
                    manager=self._manager,
                    container=self._panel,
                )
                btn_r.col_ref = col
                btn_r.direction = 1
                self._header_elements.append(btn_r)

            x += width

    def check_presses(self) -> Dict[str, Any]:
        """Check for header button presses.

        Returns:
            Dict with keys:
            - 'swap_column': (col_dict, direction) or None
            - 'sort_column': column_id or None
        """
        result: Dict[str, Any] = {"swap_column": None, "sort_column": None}

        for el in self._header_elements:
            if el.check_pressed():
                if hasattr(el, "col_ref") and hasattr(el, "direction"):
                    # Move column
                    result["swap_column"] = (el.col_ref, el.direction)
                    return result
                elif hasattr(el, "sort_col_ref"):
                    # Sort column
                    result["sort_column"] = el.sort_col_ref["id"]
                    return result

        return result

    def kill(self) -> None:
        """Clean up all header widgets."""
        for widget in self._header_elements:
            widget.kill()
        self._header_elements = []
