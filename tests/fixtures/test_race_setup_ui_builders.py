"""Smoke tests for ``tests/fixtures/race_setup_ui_builders.py``.

PROJ-325 Phase 3 — verifies the test-only Null/Mock builders honor the
``build(screen)`` contract used by ``RaceSetupScreen.__init__`` and
populate / leave-untouched widget slots as documented.
"""
from __future__ import annotations

import pygame
from unittest.mock import MagicMock

from tests.fixtures.race_setup_ui_builders import (
    MockRaceSetupUiBuilder,
    NullRaceSetupUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init, make_ui_widget


def _build_screen(*, ui_builder):
    from game.ui.screens.race_setup_screen import RaceSetupScreen

    with bypass_init(RaceSetupScreen):
        return make_ui_widget(
            RaceSetupScreen,
            rect=pygame.Rect(0, 0, 800, 600),
            manager=MagicMock(),
            on_complete_callback=MagicMock(),
            on_cancel_callback=MagicMock(),
            ui_builder=ui_builder,
        )


def test_null_builder_leaves_widget_slots_at_placeholder():
    """``NullRaceSetupUiBuilder`` is a no-op — widget slots stay at the
    placeholder values assigned by ``RaceSetupScreen._init_widget_refs``."""
    screen = _build_screen(ui_builder=NullRaceSetupUiBuilder())

    assert screen.btn_save is None
    assert screen.btn_cancel is None
    assert screen.btn_randomize is None
    assert screen.error_label is None
    assert screen.step_panels == []
    assert screen.tab_buttons == []
    assert screen._summary_panel is None
    assert screen._identity_panel is None


def test_mock_builder_populates_widget_slots():
    """``MockRaceSetupUiBuilder`` fills every widget slot the legacy
    ``_make_race_setup_screen`` helper used to wire by hand."""
    screen = _build_screen(ui_builder=MockRaceSetupUiBuilder())

    # Bottom-bar buttons
    assert screen.btn_save is not None
    assert screen.btn_cancel is not None
    assert screen.btn_randomize is not None
    assert screen.btn_randomize_all is not None
    assert screen.btn_load is not None
    # Misc widget refs
    assert screen.error_label is not None
    assert screen.ship_preview_scroll is not None
    # Tab + step collections
    assert len(screen.step_panels) == 7
    assert len(screen.tab_buttons) == 7
    for i, btn in enumerate(screen.tab_buttons):
        assert btn.tab_index == i
    # Panels
    assert screen._summary_panel is not None
    assert screen._identity_panel is not None
    assert screen._environment_panel is not None
    assert screen._aptitudes_panel is not None
    assert screen._description_panel is not None
    assert screen._flag_gallery is not None
    assert screen._portrait_gallery is not None
    assert screen._theme_gallery is not None
    # Renderer-internal widget refs (mirrors legacy helper)
    assert screen._renderer.save_update_dialog is None
    assert screen._renderer.llm_dialog_window is None
    assert screen._renderer.llm_dialog_field == ""


def test_mock_builder_button_supports_show_hide():
    """Smoke check: ``btn_save.show()`` / ``hide()`` work as MagicMock
    (existing tests call these to assert visibility behavior)."""
    screen = _build_screen(ui_builder=MockRaceSetupUiBuilder())

    screen.btn_save.show()
    screen.btn_save.show.assert_called_once()
    screen.btn_save.hide()
    screen.btn_save.hide.assert_called_once()
