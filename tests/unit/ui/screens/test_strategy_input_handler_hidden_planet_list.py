"""PROJ-411 Task 2.9: ``StrategyInputHandler`` must treat a hidden
PlanetListWindow as not-open.

Phase 2 window-reuse keeps the ``planet_list_window`` slot populated
across user-close cycles (so re-open is cheap). Before this fix,
``handle_event`` gated on ``planet_list_window is not None`` — which
matches a hidden, reusable instance — and early-returned without ever
reaching ``_handle_button_press`` / ``handle_click`` / ``_handle_scroll``.
Effect: after the user closes the planet list (X or Esc), End Turn /
hex-click / mouse-wheel zoom were all dead until scene exit.

Fix: gate also on the window's ``visible`` flag, so a *visible* planet
list still routes events to pygame_gui and skips local hotkeys (the
original intent of the branch), but a hidden one falls through to the
normal handler chain.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pygame_gui

from game.ui.screens.strategy_input_handler import StrategyInputHandler


def _make_scene_with_planet_list(*, visible: int) -> MagicMock:
    """Mock StrategyScreen with planet_list_window populated and visibility set."""
    scene = MagicMock()
    scene.ui = MagicMock()
    scene.ui.manager = MagicMock()
    scene.ui.window_manager = MagicMock()
    planet_list = MagicMock(name="planet_list_window")
    planet_list.visible = visible
    scene.ui.window_manager.planet_list_window = planet_list
    scene.ui._has_modal_open = MagicMock(return_value=False)
    scene.build_queue_screen = None
    scene.selected_fleet = None
    return scene


def test_hidden_planet_list_does_not_block_end_turn_button_press():
    """planet_list_window present-but-hidden → ``_handle_button_press`` still runs.

    Regression for the symptom the user reported: open Planet List, Esc-close,
    End Turn no longer responds. The slot stays populated under Phase 2 reuse,
    so an ``is not None`` gate misfires forever once the window has been
    constructed once.
    """
    scene = _make_scene_with_planet_list(visible=0)
    handler = StrategyInputHandler(scene)
    # The btn_next_turn handler is what advance_turn lives behind.
    scene.ui.btn_next_turn = MagicMock(name="btn_next_turn")

    event = MagicMock(name="ui_button_pressed_event")
    event.type = pygame_gui.UI_BUTTON_PRESSED
    event.ui_element = scene.ui.btn_next_turn

    handler.handle_event(event)

    scene.advance_turn.assert_called_once_with()


def test_visible_planet_list_still_short_circuits_local_button_press():
    """Visible planet list → original behaviour preserved (local handler skipped).

    The original branch existed to keep local F11/F12 hotkeys and stray button
    handlers from firing while the modal is up. We must not regress that.
    """
    scene = _make_scene_with_planet_list(visible=1)
    handler = StrategyInputHandler(scene)
    scene.ui.btn_next_turn = MagicMock(name="btn_next_turn")

    event = MagicMock(name="ui_button_pressed_event")
    event.type = pygame_gui.UI_BUTTON_PRESSED
    event.ui_element = scene.ui.btn_next_turn

    handler.handle_event(event)

    scene.advance_turn.assert_not_called()


def test_hidden_planet_list_does_not_block_mouse_wheel_zoom():
    """Hidden planet list must not block ``_handle_scroll``."""
    scene = _make_scene_with_planet_list(visible=0)
    scene.screen_width = 1920
    scene.TOP_BAR_HEIGHT = 50
    scene.camera = MagicMock()
    handler = StrategyInputHandler(scene)

    event = pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": 1})
    # Place mouse over the map (not sidebar / topbar).
    pygame.mouse.set_pos((400, 400))

    handler.handle_event(event)

    scene.camera.update_input.assert_called_once()


def test_hidden_planet_list_does_not_block_hex_click():
    """Hidden planet list must not block ``handle_click`` for hex selection."""
    scene = _make_scene_with_planet_list(visible=0)
    scene.ui.handle_click = MagicMock(return_value=False)
    scene.camera = MagicMock()
    scene.camera.zoom = 1.0
    scene._get_system_at_hex = MagicMock(return_value=None)
    scene.hex_size = 10
    scene.screen_width = 1920
    scene.TOP_BAR_HEIGHT = 50
    scene.empires = []
    handler = StrategyInputHandler(scene)

    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (400, 400)}
    )

    handler.handle_event(event)

    # handle_click is the local pathway; the assertion is that it was reached.
    scene.ui.handle_click.assert_called_once()
