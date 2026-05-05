"""Characterization tests for ``SaveSelectionWindow`` Pattern §33
widget-ref placeholders (PROJ-347 T4.3a).

``SaveSelectionWindow.process_event`` accesses ``self.btn_load``,
``self.btn_expand``, ``self.btn_delete``, ``self.btn_cancel``, and
``self.saves_listbox``. Stage 1 must set these to ``None`` before the
bypass guard so a Null-builder test does not AttributeError on those
slots.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame

from game.ui.screens.save_selection_window import SaveSelectionWindow
from tests.fixtures.save_selection_window_ui_builder import (
    NullSaveSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _make_window(*, ui_builder):
    rect = pygame.Rect(0, 0, 600, 400)
    with bypass_init(SaveSelectionWindow):
        return SaveSelectionWindow(
            rect,
            MagicMock(name="ui_manager"),
            MagicMock(name="on_load_callback"),
            MagicMock(name="on_cancel_callback"),
            ui_builder=ui_builder,
        )


class TestSaveSelectionWindowWidgetPlaceholders:
    """PROJ-347 T4.3a — Pattern §33 widget-ref placeholders.

    The 6 widget refs ``process_event`` reads (saves_listbox,
    info_label, btn_load, btn_expand, btn_delete, btn_cancel) must be
    ``None`` after a Null-builder bypass-init construction.
    """

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        window = _make_window(ui_builder=NullSaveSelectionWindowUiBuilder())
        for slot in (
            "saves_listbox", "info_label",
            "btn_load", "btn_expand", "btn_delete", "btn_cancel",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )

    def test_stage_1_state_survives_bypass(self):
        """Stage 1 cheap state survives the bypass guard."""
        window = _make_window(ui_builder=NullSaveSelectionWindowUiBuilder())
        assert window.saves_list == []
        assert window.selected_save is None
        assert window.selected_turn is None
        assert window.expanded_save_idx is None
        assert window.list_item_mapping == []
