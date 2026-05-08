"""Virtual scrolling table component.

Renders a scrollable table with:
- Virtual scrolling (only renders visible rows)
- Column headers with sort/reorder
- Row selection highlighting
- Image column support
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame
from pygame_gui.elements import UIButton, UIImage, UILabel, UIPanel, UIVerticalScrollBar

from game.ui.colors import TABLE_SELECTED, TABLE_UNSELECTED
from game.ui.components.table.column_manager import TableColumnManager
from game.ui.components.table.data_source import ITableDataSource
from game.ui.components.table.header import TableHeader
from game.ui.components.table.selection import ISelectionStrategy
from game.ui.config import UIConfig


# Issue #8: structural reasons that the Replay button is disabled,
# mapped to user-facing tooltips. Anything else (or no reason key)
# falls back to the legacy "older save" wording, which is correct for
# events from saves predating FEAT-26.
_REPLAY_DISABLED_TOOLTIPS: Dict[str, str] = {
    "sole_survivor": "No combat — one side had no ships.",
    "no_ships": "No combat — neither side had any ships.",
}
_LEGACY_REPLAY_DISABLED_TOOLTIP = "No replay available — older save."


def _disabled_replay_tooltip(data_source: Any, row_index: int) -> str:
    """Pick the disabled-Replay tooltip for ``row_index`` (issue #8)."""
    reason_getter = getattr(
        data_source, "get_cell_replay_unavailable_reason", None
    )
    if reason_getter is None:
        return _LEGACY_REPLAY_DISABLED_TOOLTIP
    reason = reason_getter(row_index)
    return _REPLAY_DISABLED_TOOLTIPS.get(
        reason, _LEGACY_REPLAY_DISABLED_TOOLTIP
    )


class VirtualTable:
    """Virtual scrolling table with headers and selection.

    Creates a scrollable table that only renders visible rows for performance.
    Supports sortable/reorderable column headers and row selection.
    """

    # Selection highlighting colors
    SELECTED_COLOR = pygame.Color(*TABLE_SELECTED)  # Blue tint
    UNSELECTED_COLOR = pygame.Color(*TABLE_UNSELECTED)  # Dark grey

    def __init__(
        self,
        panel: UIPanel,
        manager,
        data_source: ITableDataSource,
        column_manager: TableColumnManager,
        selection_strategy: ISelectionStrategy,
        row_height: int = UIConfig.ROW_HEIGHT_LARGE,
        header_height: int = UIConfig.HEADER_HEIGHT,
    ) -> None:
        """Initialize the virtual table.

        Args:
            panel: The UIPanel container for the table.
            manager: pygame_gui UIManager.
            data_source: Data source providing row/cell data.
            column_manager: Column configuration manager.
            selection_strategy: Selection behavior strategy.
            row_height: Height of each row in pixels.
            header_height: Height of header row in pixels.
        """
        self._panel = panel
        self._manager = manager
        self._data_source = data_source
        self._column_manager = column_manager
        self._selection_strategy = selection_strategy
        self._row_height = row_height
        self._header_height = header_height

        # Containers
        self._header_container: Optional[UIPanel] = None
        self._list_view_panel: Optional[UIPanel] = None
        self._scroll_bar: Optional[UIVerticalScrollBar] = None
        self._header: Optional[TableHeader] = None

        # Row pool
        self._row_pool: List[Dict[str, Any]] = []

        # Dirty tracking for optimization
        self._last_scroll_pct: float = -1.0
        self._last_row_count: int = -1

        # PROJ-373 Phase 3: cache last-rebuild dimensions so subsequent
        # rebuild_row_pool() calls can skip the (~1.5s) tear-down/rebuild
        # when the pool is already correctly sized.
        self._last_pool_dims: Optional[Tuple[int, int]] = None

        # Build UI
        self._build_containers()
        self._header = TableHeader(
            self._header_container,
            self._manager,
            self._column_manager,
            self._header_height,
        )
        self._rebuild_row_pool()
        self.update_scroll_bar()

    def _build_containers(self) -> None:
        """Build the header container, list viewport, and scrollbar."""
        panel_rect = self._panel.get_relative_rect()

        # Header row
        self._header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, panel_rect.width, self._header_height),
            manager=self._manager,
            container=self._panel,
            anchors={"left": "left", "right": "right", "top": "top"},
        )

        # List viewport
        list_height = panel_rect.height - self._header_height
        self._list_view_panel = UIPanel(
            relative_rect=pygame.Rect(
                0, self._header_height, panel_rect.width - 20, list_height
            ),
            manager=self._manager,
            container=self._panel,
            anchors={"left": "left", "right": "right", "top": "top", "bottom": "bottom"},
        )

        # Scrollbar
        self._scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, self._header_height, 20, list_height),
            visible_percentage=1.0,
            manager=self._manager,
            container=self._panel,
            anchors={"left": "right", "right": "right", "top": "top", "bottom": "bottom"},
        )

    def _pool_dims_changed(self) -> bool:
        """PROJ-373 Phase 3: True if list-panel dims changed since last build.

        Compares the current cache fingerprint against ``self._last_pool_dims``.
        A no-op rebuild when the fingerprint is unchanged keeps the existing
        widget pool alive and saves ~1.5s of widget tear-down/recreate per
        yard switch (when reached via the public ``rebuild_row_pool()`` entry
        point).

        Cache fingerprint contents (PROJ-373 review MAJ-001 + MAJ-002):
            - ``panel_rect.height`` — drives ``visible_rows`` count.
            - ``panel_rect.width`` — row backgrounds are sized to it
              (``virtual_table.py`` row-bg rect uses ``panel_rect.width``);
              a width-only resize must invalidate.
            - ``self._row_height``.
            - Visible-column fingerprint as ``((col_id, col_width), …)`` —
              ``column_manager.toggle_column()`` and ``swap_column()`` mutate
              the visible-column list without changing panel dimensions, and
              every production caller of ``rebuild_row_pool()``
              (``data_list_window_mixin``, ``event_log_window``,
              ``fleet_report_window``, ``empire_build_queue_window``)
              expects the rebuild to reflect the new column set.
        """
        panel_rect = self._list_view_panel.get_relative_rect()
        visible_cols = self._column_manager.get_visible_columns()
        col_fp = tuple((c["id"], c.get("width", 100)) for c in visible_cols)
        current = (panel_rect.height, panel_rect.width, self._row_height, col_fp)
        return self._last_pool_dims != current

    def _rebuild_row_pool(self) -> None:
        """Build the row pool for virtual scrolling.

        PROJ-373 Phase 3: Early-return when dimensions are unchanged AND a
        pool already exists. The constructor calls this once with no prior
        pool, so the first invocation always builds.
        """
        if self._row_pool and not self._pool_dims_changed():
            return

        # Clear existing rows
        for row in self._row_pool:
            if "bg" in row and row["bg"]:
                row["bg"].kill()
            for widget in row.get("widgets", []):
                if "el" in widget:
                    widget["el"].kill()
                if "actions_dict" in widget:
                    for btn in widget["actions_dict"].values():
                        btn.kill()
                if widget.get("type") == "replay_action" and "button" in widget:
                    widget["button"].kill()
        self._row_pool.clear()

        # Calculate how many rows we need
        panel_rect = self._list_view_panel.get_relative_rect()
        visible_rows = max(1, (panel_rect.height // self._row_height) + 2)

        visible_cols = self._column_manager.get_visible_columns()
        # PROJ-373 Phase 3: cache the fingerprint this pool was built for.
        # Must match the tuple shape in `_pool_dims_changed`.
        col_fp = tuple((c["id"], c.get("width", 100)) for c in visible_cols)
        self._last_pool_dims = (
            panel_rect.height, panel_rect.width, self._row_height, col_fp,
        )

        for i in range(visible_rows):
            y = i * self._row_height

            # Row background panel
            row_bg = UIPanel(
                relative_rect=pygame.Rect(0, y, panel_rect.width, self._row_height),
                manager=self._manager,
                container=self._list_view_panel,
            )

            # Create widgets for each visible column
            widgets = []
            x = 0
            for col in visible_cols:
                width = col.get("width", 100)
                col_id = col["id"]
                is_image = self._column_manager.is_image_column(col_id)

                if is_image:
                    # Image widget
                    img_size = min(width - 10, self._row_height - 10)
                    img = UIImage(
                        relative_rect=pygame.Rect(x + 5, 5, img_size, img_size),
                        image_surface=pygame.Surface((img_size, img_size)),
                        manager=self._manager,
                        container=row_bg,
                    )
                    widgets.append({
                        "type": "image", "el": img, "col": col,
                        "_last_img": None,
                    })
                elif col.get("type") == "actions":
                    actions_dict = {}
                    btn_size = self._row_height - 10
                    if btn_size > 30:
                        btn_size = 30

                    spacing = 5
                    btn_x = x + 5

                    for action, text in [("add", "+"), ("remove", "-"), ("up", "^"), ("down", "v")]:
                        btn = UIButton(
                            relative_rect=pygame.Rect(btn_x, (self._row_height - btn_size) // 2, btn_size, btn_size),
                            text=text,
                            manager=self._manager,
                            container=row_bg,
                        )
                        actions_dict[action] = btn
                        btn_x += btn_size + spacing

                    widgets.append({
                        "type": "actions", "col": col, "actions_dict": actions_dict
                    })
                elif col.get("type") == "replay_action":
                    # FEAT-26: generic single-button action column. The
                    # column dict carries the action key + button label,
                    # so the table layer stays domain-neutral. Per-row
                    # enable/disable + button-press dispatch lives in
                    # update_visible_rows + check_action_button_press.
                    btn_height = self._row_height - 6
                    btn = UIButton(
                        relative_rect=pygame.Rect(
                            x + 4, 3, max(width - 8, 30), btn_height
                        ),
                        text=str(col.get("label", "")),
                        manager=self._manager,
                        container=row_bg,
                    )
                    widgets.append({
                        "type": "replay_action",
                        "col": col,
                        "button": btn,
                        "action": col.get("action", "replay"),
                    })
                else:
                    # Label widget
                    lbl = UILabel(
                        relative_rect=pygame.Rect(x, 0, width, self._row_height),
                        text="",
                        manager=self._manager,
                        container=row_bg,
                    )
                    widgets.append({
                        "type": "label", "el": lbl, "col": col,
                        "_last_text": "",
                    })

                x += width

            self._row_pool.append({
                "bg": row_bg,
                "widgets": widgets,
                "row_index": -1,
                "_last_color": None,
            })

    def update_visible_rows(self) -> None:
        """Update content of row pool based on scroll position.

        Uses dirty tracking to skip updates when nothing changed.
        Caches text/color values to avoid redundant pygame_gui calls.
        """
        current_pct = self._scroll_bar.start_percentage
        current_count = self._data_source.get_row_count()

        # Dirty check
        if (
            current_pct == self._last_scroll_pct
            and current_count == self._last_row_count
        ):
            return

        self._last_scroll_pct = current_pct
        self._last_row_count = current_count

        # Calculate scroll position
        total_h = current_count * self._row_height
        scroll_y = current_pct * total_h
        start_index = int(scroll_y // self._row_height)
        offset_y = scroll_y % self._row_height

        selected = self._selection_strategy.get_selected_indices()

        for pool_idx, row in enumerate(self._row_pool):
            data_idx = start_index + pool_idx
            row["row_index"] = data_idx

            # Position row
            y_pos = (pool_idx * self._row_height) - offset_y
            row["bg"].set_relative_position((0, y_pos))

            if data_idx < current_count:
                row["bg"].show()

                # Determine target color
                if data_idx in selected:
                    target_color = self.SELECTED_COLOR
                else:
                    highlight = self._data_source.get_row_highlight(data_idx)
                    if highlight:
                        target_color = pygame.Color(*highlight)
                    else:
                        target_color = self.UNSELECTED_COLOR

                # Only rebuild panel if color actually changed
                if row["_last_color"] != target_color:
                    row["_last_color"] = target_color
                    row["bg"].background_colour = target_color
                    row["bg"].rebuild()

                # Update cell contents (skip if text unchanged)
                for widget in row["widgets"]:
                    col = widget["col"]
                    col_id = col["id"]

                    if widget["type"] == "image":
                        img_surface = self._data_source.get_cell_image(data_idx, col_id)
                        if img_surface is not widget.get("_last_img"):
                            widget["_last_img"] = img_surface
                            if img_surface:
                                widget["el"].set_image(img_surface)
                            else:
                                rect = widget["el"].get_relative_rect()
                                widget["el"].set_image(
                                    pygame.Surface((rect.width, rect.height))
                                )
                    elif widget["type"] == "actions":
                        actions_dict = widget.get("actions_dict", {})
                        up_btn = actions_dict.get("up")
                        down_btn = actions_dict.get("down")
                        if up_btn is not None:
                            if data_idx == 0:
                                up_btn.disable()
                            else:
                                up_btn.enable()
                        if down_btn is not None:
                            if data_idx >= current_count - 1:
                                down_btn.disable()
                            else:
                                down_btn.enable()
                    elif widget["type"] == "replay_action":
                        # FEAT-26: enable iff the data source reports a
                        # non-None replay id for this row. Generic seam:
                        # data sources without the hook leave the button
                        # disabled (no replays => no clickable button).
                        # Issue #8: when disabled, prefer a structural
                        # reason (sole_survivor / no_ships) over the
                        # generic "older save" wording.
                        btn = widget["button"]
                        replay_id_getter = getattr(
                            self._data_source, "get_cell_replay_id", None
                        )
                        replay_id = (
                            replay_id_getter(data_idx)
                            if replay_id_getter is not None
                            else None
                        )
                        if replay_id:
                            btn.enable()
                            btn.tool_tip_text = "Replay this battle"
                        else:
                            btn.disable()
                            btn.tool_tip_text = _disabled_replay_tooltip(
                                self._data_source, data_idx
                            )
                    else:
                        text = str(self._data_source.get_cell_value(data_idx, col_id))
                        if text != widget.get("_last_text"):
                            widget["_last_text"] = text
                            widget["el"].set_text(text)
            else:
                row["bg"].hide()
                row["_last_color"] = None
                # Reset cached text/image so re-shown rows get updated
                for widget in row["widgets"]:
                    if widget["type"] == "label":
                        widget["_last_text"] = None
                    else:
                        widget["_last_img"] = None

    def update_scroll_bar(self) -> None:
        """Update scroll bar visible percentage."""
        panel_rect = self._list_view_panel.get_relative_rect()
        total_h = self._data_source.get_row_count() * self._row_height

        if total_h > 0:
            visible_pct = min(1.0, panel_rect.height / total_h)
        else:
            visible_pct = 1.0

        self._scroll_bar.set_visible_percentage(visible_pct)

    def find_clicked_row(self, pos: Tuple[int, int]) -> int:
        """Find which row was clicked.

        Args:
            pos: Click position in screen coordinates.

        Returns:
            Data row index, or -1 if no row hit.
        """
        for row in self._row_pool:
            if not row["bg"].visible:
                continue

            row_rect = row["bg"].get_abs_rect()
            if row_rect.collidepoint(pos):
                return row.get("row_index", -1)

        return -1

    def handle_click(self, pos: Tuple[int, int], ctrl_held: bool = False) -> int:
        """Handle a click on the table.

        Args:
            pos: Click position in screen coordinates.
            ctrl_held: Whether Ctrl key was held.

        Returns:
            Clicked row index, or -1 if no row hit.
        """
        row_idx = self.find_clicked_row(pos)
        if row_idx >= 0:
            self._selection_strategy.handle_click(row_idx, ctrl_held)
            self._update_selection_highlights()
        return row_idx

    def _update_selection_highlights(self) -> None:
        """Update row background colors based on selection."""
        selected = self._selection_strategy.get_selected_indices()

        for row in self._row_pool:
            data_idx = row.get("row_index", -1)
            if data_idx < 0:
                continue

            if data_idx in selected:
                target_color = self.SELECTED_COLOR
            else:
                highlight = self._data_source.get_row_highlight(data_idx)
                if highlight:
                    target_color = pygame.Color(*highlight)
                else:
                    target_color = self.UNSELECTED_COLOR

            if row["_last_color"] != target_color:
                row["_last_color"] = target_color
                row["bg"].background_colour = target_color
                row["bg"].rebuild()

    def check_action_button_press(self, ui_element: Any) -> Optional[Tuple[str, int]]:
        """Check if an action button was pressed.

        Handles both action-column types:
        - ``"actions"`` — multi-button (build queue: add/remove/up/down)
        - ``"replay_action"`` — single button (FEAT-26: Event Log Replay)

        Args:
            ui_element: The UI element that triggered the event.

        Returns:
            Tuple of (action_name, row_index) if matched, None otherwise.
        """
        for row in self._row_pool:
            if not row.get("bg", None) or not row["bg"].visible:
                continue

            for widget in row.get("widgets", []):
                if widget["type"] == "actions":
                    for action, btn in widget.get("actions_dict", {}).items():
                        if ui_element == btn:
                            return (action, row.get("row_index", -1))
                elif widget["type"] == "replay_action":
                    if ui_element == widget.get("button"):
                        return (
                            widget.get("action", "replay"),
                            row.get("row_index", -1),
                        )
        return None

    def check_header_presses(self) -> Dict[str, Any]:
        """Check for header button presses.

        Returns:
            Dict with 'swap_column' and 'sort_column' keys.
        """
        return self._header.check_presses()

    def rebuild_headers(self) -> None:
        """Rebuild column headers."""
        self._header.rebuild()

    def rebuild_row_pool(self) -> None:
        """Public method to rebuild the row pool.

        Note: Reads ``_list_view_panel.get_relative_rect()`` for dimension
        fingerprinting. Callers MUST ensure pygame_gui has completed its
        layout pass before calling — typically by running ``manager.update(0.0)``
        beforehand. PROJ-373 review MIN-003.
        """
        self._rebuild_row_pool()

    def force_update(self) -> None:
        """Force update by resetting dirty tracking."""
        self._last_scroll_pct = -1.0
        self._last_row_count = -1

    def kill(self) -> None:
        """Clean up all widgets."""
        # Kill header
        if self._header:
            self._header.kill()

        # Kill rows
        for row in self._row_pool:
            if "bg" in row and row["bg"]:
                row["bg"].kill()
            for widget in row.get("widgets", []):
                if "el" in widget:
                    widget["el"].kill()
                if "actions_dict" in widget:
                    for btn in widget["actions_dict"].values():
                        btn.kill()
                if widget.get("type") == "replay_action" and "button" in widget:
                    widget["button"].kill()
        self._row_pool.clear()

        # Kill containers
        if self._scroll_bar:
            self._scroll_bar.kill()
        if self._list_view_panel:
            self._list_view_panel.kill()
        if self._header_container:
            self._header_container.kill()

    @property
    def scroll_bar(self) -> UIVerticalScrollBar:
        """Get the scroll bar widget."""
        return self._scroll_bar

    @property
    def selection_strategy(self) -> ISelectionStrategy:
        """Get the selection strategy."""
        return self._selection_strategy

    @property
    def data_source(self) -> ITableDataSource:
        """Get the data source."""
        return self._data_source

    @data_source.setter
    def data_source(self, source: ITableDataSource) -> None:
        """Set the data source."""
        self._data_source = source
        self.force_update()
