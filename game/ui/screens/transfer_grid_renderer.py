"""Pygame_gui widget builder for ``TransferDialog`` (PROJ-328 Phase C).

Owns every ``pygame_gui.elements.UI*`` construction call:

* The top chrome (source/target dropdowns, filter button, column
  headers, scrolling grid container, bottom buttons).
* Per-row widget construction inside the scrolling grid.
* Dropdown recreation (``UIDropDownMenu`` lacks a dynamic-update
  API).

The renderer reads from the dialog's ``view_model`` for row data
and writes widget references back onto the dialog so the dialog's
event-routing code keeps the same ``self.btn_confirm`` /
``self._arrow_buttons`` / ``self.drop_source`` etc. attributes.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
TransferDialog is "command-heavy. Split ... grid/dropdown widgets
into a renderer."
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import pygame
from pygame_gui.elements import (
    UIButton,
    UIDropDownMenu,
    UILabel,
    UIScrollingContainer,
)

if TYPE_CHECKING:
    from game.ui.screens.transfer_dialog import TransferDialog


# Arrow button increments (5 gradations per direction).
ARROW_INCREMENTS_LOAD = [100000, 10000, 1000, 10, 1]
ARROW_INCREMENTS_DROP = [1, 10, 1000, 10000, 100000]
ARROW_LABELS_LOAD = ["<<<<<", "<<<<", "<<<", "<<", "<"]
ARROW_LABELS_DROP = [">", ">>", ">>>", ">>>>", ">>>>>"]


class TransferGridRenderer:
    """Builds and rebuilds the transfer dialog's widget tree.

    The dialog calls:

    * ``build_chrome(dialog)`` once during ``__init__`` (Stage 3).
    * ``build_grid(dialog)`` after source/target selection or on
      filter toggle.
    * ``recreate_dropdown(...)`` when the source/target options
      change.
    * ``update_pending_label(dialog, cargo_key)`` on each pending
      mutation.
    """

    ROW_HEIGHT = 32

    # Layout X positions and widths (inside scrolling container).
    NAME_X = 5
    NAME_W = 95
    SOURCE_AMT_X = 105
    SOURCE_AMT_W = 60
    MAX_LOAD_X = 170
    MAX_LOAD_W = 42
    LOAD_ARROWS_X = 216
    ARROW_W = 38
    ARROW_GAP = 2
    ARROW_COUNT = 5
    PENDING_X = 420
    PENDING_W = 120
    ZERO_BTN_X = 544
    ZERO_BTN_W = 26
    DROP_ARROWS_X = 574
    MAX_DROP_X = 776
    MAX_DROP_W = 42
    TARGET_AMT_X = 822
    TARGET_AMT_W = 60

    # ------------------------------------------------------------------
    # Chrome (one-shot at __init__ time)
    # ------------------------------------------------------------------

    def build_chrome(self, dialog: "TransferDialog") -> None:
        """Build the top-level dialog chrome: dropdowns + filter
        button + column headers + scrolling container + bottom
        buttons. Writes widget refs onto ``dialog``.
        """
        padding = 10
        label_h = 20
        element_h = 30
        content_w = dialog.rect.width - 40

        curr_y = padding

        # Source dropdown.
        UILabel(
            pygame.Rect(padding, curr_y, 60, label_h),
            "Source:", dialog.ui_manager, container=dialog,
        )
        dialog.drop_source = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(75, curr_y, content_w // 2 - 80, element_h),
            manager=dialog.ui_manager,
            container=dialog,
        )

        # Target dropdown.
        target_x = content_w // 2 + 10
        UILabel(
            pygame.Rect(target_x, curr_y, 60, label_h),
            "Target:", dialog.ui_manager, container=dialog,
        )
        dialog.drop_target = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(target_x + 65, curr_y, content_w // 2 - 80, element_h),
            manager=dialog.ui_manager,
            container=dialog,
        )

        # Filter button.
        dialog.btn_filter = UIButton(
            pygame.Rect(content_w - 100, curr_y, 110, element_h),
            "Filter Empty",
            dialog.ui_manager,
            container=dialog,
        )
        curr_y += element_h + padding

        # Column headers.
        UILabel(
            pygame.Rect(self.SOURCE_AMT_X, curr_y, self.SOURCE_AMT_W, label_h),
            "Source", dialog.ui_manager, container=dialog,
        )
        UILabel(
            pygame.Rect(self.PENDING_X, curr_y, self.PENDING_W, label_h),
            "Transfer", dialog.ui_manager, container=dialog,
        )
        UILabel(
            pygame.Rect(self.TARGET_AMT_X, curr_y, self.TARGET_AMT_W, label_h),
            "Target", dialog.ui_manager, container=dialog,
        )
        curr_y += label_h + 5

        # Scrolling grid container.
        grid_bottom_margin = 80  # space for buttons.
        grid_h = dialog.rect.height - curr_y - grid_bottom_margin - 40
        dialog.grid_container = UIScrollingContainer(
            relative_rect=pygame.Rect(padding, curr_y, content_w, grid_h),
            manager=dialog.ui_manager,
            container=dialog,
        )
        dialog._grid_top_y = curr_y

        # Bottom buttons.
        btn_y = dialog.rect.height - 100
        btn_w = 120
        dialog.btn_confirm = UIButton(
            pygame.Rect(padding, btn_y, btn_w, 40),
            "Confirm All",
            dialog.ui_manager,
            container=dialog,
        )
        clear_x = padding + btn_w + 10
        dialog.btn_clear_all = UIButton(
            pygame.Rect(clear_x, btn_y, btn_w, 40),
            "Clear All",
            dialog.ui_manager,
            container=dialog,
        )
        dialog.btn_cancel = UIButton(
            pygame.Rect(content_w - btn_w + padding, btn_y, btn_w, 40),
            "Cancel",
            dialog.ui_manager,
            container=dialog,
        )

    # ------------------------------------------------------------------
    # Dropdown recreation
    # ------------------------------------------------------------------

    def recreate_dropdown(self, dialog: "TransferDialog", old_dropdown,
                          options: List[str], selected: str) -> Any:
        """Recreate a dropdown — ``UIDropDownMenu`` lacks a dynamic
        options-update API, so the only way to refresh the option
        list is to kill and re-create."""
        rect = old_dropdown.relative_rect
        container = old_dropdown.ui_container
        old_dropdown.kill()
        return UIDropDownMenu(
            options_list=options if options else [""],
            starting_option=(selected if selected in options
                             else (options[0] if options else "")),
            relative_rect=rect,
            manager=dialog.ui_manager,
            container=container,
        )

    @staticmethod
    def extract_dropdown_value(value: Any) -> Any:
        """Some pygame_gui versions emit ``(label, object_id)``
        tuples; older code expects plain strings."""
        if isinstance(value, tuple):
            return value[0]
        return value

    # ------------------------------------------------------------------
    # Grid (re-built on selection / filter change)
    # ------------------------------------------------------------------

    def build_grid(self, dialog: "TransferDialog") -> None:
        """Rebuild every row inside the scrolling grid container.

        Uses ``dialog.view_model.visible_rows()`` for the row data;
        writes widget refs onto the dialog's per-row maps.
        """
        # Clear old grid.
        for w in dialog._grid_widgets:
            w.kill()
        dialog._grid_widgets.clear()
        dialog._arrow_buttons.clear()
        dialog._max_buttons.clear()
        dialog._zero_buttons.clear()
        dialog._pending_labels.clear()

        y = 5
        for row in dialog.view_model.visible_rows():
            self._add_row(dialog, y, row["cargo_key"],
                          row["display_name"], row["source_amt"],
                          row["target_amt"])
            y += self.ROW_HEIGHT

        total_h = max(y + 10, 100)
        container_w = dialog.grid_container.relative_rect.width - 20
        dialog.grid_container.set_scrollable_area_dimensions(
            (container_w, total_h),
        )

    def _add_row(self, dialog: "TransferDialog", y: int, cargo_key: str,
                 display_name: str, source_amt: int, target_amt: int) -> None:
        container = dialog.grid_container
        vm = dialog.view_model

        # Resource name.
        lbl = UILabel(
            pygame.Rect(self.NAME_X, y, self.NAME_W, self.ROW_HEIGHT),
            display_name, dialog.ui_manager, container=container,
        )
        dialog._grid_widgets.append(lbl)

        # Source amount.
        src_lbl = UILabel(
            pygame.Rect(self.SOURCE_AMT_X, y, self.SOURCE_AMT_W, self.ROW_HEIGHT),
            str(source_amt), dialog.ui_manager, container=container,
        )
        dialog._grid_widgets.append(src_lbl)

        # Max Load button.
        btn = UIButton(
            pygame.Rect(self.MAX_LOAD_X, y + 2, self.MAX_LOAD_W, self.ROW_HEIGHT - 4),
            "Max", dialog.ui_manager, container=container,
        )
        dialog._max_buttons[id(btn)] = (cargo_key, "load")
        dialog._grid_widgets.append(btn)

        # Load arrow buttons.
        x = self.LOAD_ARROWS_X
        for inc, label in zip(ARROW_INCREMENTS_LOAD, ARROW_LABELS_LOAD):
            btn = UIButton(
                pygame.Rect(x, y + 2, self.ARROW_W, self.ROW_HEIGHT - 4),
                label, dialog.ui_manager, container=container,
            )
            dialog._arrow_buttons[id(btn)] = (cargo_key, inc)
            dialog._grid_widgets.append(btn)
            x += self.ARROW_W + self.ARROW_GAP

        # Pending transfer label.
        pending_lbl = UILabel(
            pygame.Rect(self.PENDING_X, y, self.PENDING_W, self.ROW_HEIGHT),
            vm.format_pending(vm.get_pending(cargo_key)),
            dialog.ui_manager, container=container,
        )
        dialog._pending_labels[cargo_key] = pending_lbl
        dialog._grid_widgets.append(pending_lbl)

        # Zero button.
        zero_btn = UIButton(
            pygame.Rect(self.ZERO_BTN_X, y + 2, self.ZERO_BTN_W, self.ROW_HEIGHT - 4),
            "0", dialog.ui_manager, container=container,
        )
        dialog._zero_buttons[id(zero_btn)] = cargo_key
        dialog._grid_widgets.append(zero_btn)

        # Drop arrow buttons.
        x = self.DROP_ARROWS_X
        for inc, label in zip(ARROW_INCREMENTS_DROP, ARROW_LABELS_DROP):
            btn = UIButton(
                pygame.Rect(x, y + 2, self.ARROW_W, self.ROW_HEIGHT - 4),
                label, dialog.ui_manager, container=container,
            )
            dialog._arrow_buttons[id(btn)] = (cargo_key, -inc)
            dialog._grid_widgets.append(btn)
            x += self.ARROW_W + self.ARROW_GAP

        # Max Drop button.
        btn = UIButton(
            pygame.Rect(self.MAX_DROP_X, y + 2, self.MAX_DROP_W, self.ROW_HEIGHT - 4),
            "Max", dialog.ui_manager, container=container,
        )
        dialog._max_buttons[id(btn)] = (cargo_key, "drop")
        dialog._grid_widgets.append(btn)

        # Target amount.
        tgt_lbl = UILabel(
            pygame.Rect(self.TARGET_AMT_X, y, self.TARGET_AMT_W, self.ROW_HEIGHT),
            str(target_amt), dialog.ui_manager, container=container,
        )
        dialog._grid_widgets.append(tgt_lbl)

    # ------------------------------------------------------------------
    # Per-row label refresh
    # ------------------------------------------------------------------

    def update_pending_label(self, dialog: "TransferDialog",
                             cargo_key: str) -> None:
        """Refresh the pending label for ``cargo_key`` from the
        view model."""
        lbl = dialog._pending_labels.get(cargo_key)
        if lbl is None:
            return
        val = dialog.view_model.get_pending(cargo_key)
        lbl.set_text(dialog.view_model.format_pending(val))

    def set_filter_button_text(self, dialog: "TransferDialog",
                               filter_empty: bool) -> None:
        """Toggle the filter button label."""
        if dialog.btn_filter is None:
            return
        dialog.btn_filter.set_text(
            "Show All" if filter_empty else "Filter Empty",
        )


class TransferDialogUiBuilder:
    """Production UI builder. Invoked from
    ``TransferDialog.__init__`` (Stage 3) to build the chrome and
    seed the initial grid via ``populate_initial_data``.
    """

    def build(self, dialog: "TransferDialog") -> None:
        dialog._renderer.build_chrome(dialog)
        dialog._apply_tooltips()
        dialog.populate_initial_data()


__all__ = [
    "ARROW_INCREMENTS_LOAD",
    "ARROW_INCREMENTS_DROP",
    "ARROW_LABELS_LOAD",
    "ARROW_LABELS_DROP",
    "TransferGridRenderer",
    "TransferDialogUiBuilder",
]
