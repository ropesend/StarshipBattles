"""Characterization tests for ``RaceBrowserDialog`` Pattern §33
widget-ref placeholders (PROJ-347 T4.3b).

``RaceBrowserDialog.process_event`` accesses ``self.btn_cancel`` and
``self.btn_load``. Stage 1 must set these to ``None`` before the
bypass guard so a Null-builder test does not AttributeError on those
slots.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame

from game.ui.screens.race_browser_dialog import RaceBrowserDialog
from tests.fixtures.race_browser_dialog_ui_builder import (
    NullRaceBrowserDialogUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _make_window(*, ui_builder):
    rect = pygame.Rect(0, 0, 600, 500)
    race_library = MagicMock(name="race_library")
    race_library.get_all_races.return_value = []
    with bypass_init(RaceBrowserDialog):
        return RaceBrowserDialog(
            rect,
            MagicMock(name="ui_manager"),
            race_library,
            MagicMock(name="on_select_callback"),
            MagicMock(name="on_cancel_callback"),
            ui_builder=ui_builder,
        )


class TestRaceBrowserDialogWidgetPlaceholders:
    """PROJ-347 T4.3b — Pattern §33 widget-ref placeholders.

    The 4 widget refs the dialog body reads (scroll_container,
    btn_cancel, btn_load, no_races_label) must be ``None`` after a
    Null-builder bypass-init construction.
    """

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        window = _make_window(ui_builder=NullRaceBrowserDialogUiBuilder())
        for slot in (
            "scroll_container", "btn_cancel", "btn_load", "no_races_label",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )

    def test_stage_1_state_survives_bypass(self):
        """Stage 1 cheap state (race_library, callbacks, race_rows) is
        intact after bypass."""
        window = _make_window(ui_builder=NullRaceBrowserDialogUiBuilder())
        assert window.race_rows == []
        assert window.selected_race is None
        assert window.selected_row_index == -1
        assert window.race_library is not None
