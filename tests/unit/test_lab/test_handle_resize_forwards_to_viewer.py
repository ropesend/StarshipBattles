"""PROJ-342 regression: TestLabScreen.handle_resize forwards to BattleStateViewer.

Pre-refactor, the viewer was constructed with `WIDTH/HEIGHT` constants and
never received resize events. PROJ-342 fixes both: explicit dimensions at
construction, plus `handle_resize` forwarding so panels reflow correctly.
"""
from __future__ import annotations

from unittest.mock import Mock, patch

from game.ui.screens.test_lab.screen import TestLabScreen


def test_handle_resize_forwards_to_battle_state_viewer() -> None:
    """`handle_resize(w, h)` must call `battle_state_viewer.handle_resize(w, h)`."""
    with patch.object(TestLabScreen, "__init__", lambda self, *a, **kw: None):
        screen = TestLabScreen.__new__(TestLabScreen)
        screen.screen_width = 3840
        screen.screen_height = 2160
        screen.ui_manager = Mock()
        screen.battle_state_viewer = Mock()
        # `_create_ui` reads several panel-manager / button attrs; stub it out.
        screen._create_ui = Mock()

        screen.handle_resize(1920, 1080)

    assert screen.screen_width == 1920
    assert screen.screen_height == 1080
    screen.ui_manager.set_window_resolution.assert_called_once_with((1920, 1080))
    screen.battle_state_viewer.handle_resize.assert_called_once_with(1920, 1080)
