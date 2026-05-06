"""Mixin for VirtualTable list windows (planet / star).

Extracted in PROJ-319 (DUP-X-03) to remove the duplicated `_toggle_column`,
`_save_preset`, and slider-text-sync logic that previously lived in
`PlanetListWindow` and `StarListWindow`.

Adopters must already define:

  - `column_manager` (TableColumnManager)
  - `virtual_table` (VirtualTable)
  - `txt_preset_name` (UITextEntryLine)
  - `preset_manager` (PresetManager-like; `save_preset(name, state)` and
    `get_preset_names()`)
  - `dd_presets` (UIDropDownMenu — replaced after save)
  - `ui_manager` (pygame_gui.UIManager)
  - `last_preset_selection`
  - `_capture_current_state()` (subclass-specific)
  - `refresh_list()` (subclass-specific)
  - `ui_filters` dict (for `_sync_slider_text`)

The audit (DUP-X-03) noted drift between planet and star windows (planet has
effect filters, star has type filters), so this mixin only covers the
genuinely shared pieces. Subclasses keep their own `update`, but call
`self._sync_slider_text(self._slider_filter_keys)` from there.
"""
from __future__ import annotations

from typing import Iterable

from pygame_gui.elements import UIDropDownMenu


class DataListWindowMixin:
    """Mixin providing shared list-window plumbing for planet / star windows."""

    def _toggle_column(self, btn) -> None:
        """Toggle column visibility from a sidebar button.

        Works against any button whose `col_ref` points at the column dict in
        the parent window's `columns` list.
        """
        col = btn.col_ref
        new_visible = self.column_manager.toggle_column(col["id"])
        if new_visible is not None:
            label = col["title"] or col["id"]
            t = f"[x] {label}" if new_visible else f"[ ] {label}"
            btn.set_text(t)
            col["visible"] = new_visible
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()

    def _save_preset(self) -> None:
        """Save the current state as a preset and rebuild the preset dropdown."""
        name = self.txt_preset_name.get_text()
        if not name:
            return
        state = self._capture_current_state()
        self.preset_manager.save_preset(name, state)
        rect = self.dd_presets.relative_rect
        container = self.dd_presets.ui_container
        self.dd_presets.kill()
        self.dd_presets = UIDropDownMenu(
            options_list=self.preset_manager.get_preset_names(),
            starting_option=name,
            relative_rect=rect,
            manager=self.ui_manager,
            container=container,
        )
        self.last_preset_selection = name

    def _sync_slider_text(self, slider_keys: Iterable[str]) -> None:
        """For each Min/Max range slider in `slider_keys`, sync its text box.

        Updates the text box only when the slider has moved AND the box is
        not currently focused (so the user's edit isn't overwritten mid-type).
        """
        for key in slider_keys:
            f = self.ui_filters.get(key)
            if not f:
                continue
            for which in ("min", "max"):
                slider = f[which]
                if not slider.has_moved_recently:
                    continue
                txt_box = f[f"{which}_txt"]
                if not txt_box.is_focused:
                    txt_box.set_text(f"{slider.get_current_value():.1f}")

    def _run_update_template(self, slider_keys: Iterable[str]) -> None:
        """Run the shared 4-step `update()` body (PROJ-375 Task 3.2).

        Both `PlanetListWindow.update` and `StarListWindow.update` were
        identical except for the slider-key list. This collapses them.

        Steps:
        1. Scrollbar movement → `update_visible_rows()` if moved.
        2. Slider text sync via `_sync_slider_text(slider_keys)`.
        3. Header sort/swap dispatch (rebuilds headers + refreshes list).
        4. Preset dropdown selection change → `_apply_state(preset)`.

        Subclasses that need extra polling can call this then add their own.
        """
        if self.virtual_table.scroll_bar.check_has_moved_recently():
            self.virtual_table.update_visible_rows()

        self._sync_slider_text(slider_keys)

        header_result = self.virtual_table.check_header_presses()
        swap = header_result.get('swap_column')
        if swap:
            col_dict, direction = swap
            self.column_manager.swap_column(col_dict['id'], direction)
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()
        else:
            sort_col = header_result.get('sort_column')
            if sort_col:
                self.column_manager.set_sort(sort_col)
                self.virtual_table.rebuild_headers()
                self.refresh_list()

        if self.last_preset_selection is None:
            self.last_preset_selection = self.dd_presets.selected_option
        if self.dd_presets.selected_option != self.last_preset_selection:
            self.last_preset_selection = self.dd_presets.selected_option
            name = self.last_preset_selection
            if self.preset_manager.has_preset(name):
                self._apply_state(self.preset_manager.get_preset(name))
