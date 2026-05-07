"""Unit coverage for RunLoop event routing and shutdown helpers."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame

import game.run_loop as run_loop_module
from game.core.constants import GameState
from game.core.input_actions import InputAction
from game.run_loop import RunLoop


def _make_loop(state=GameState.MENU):
    profiler = MagicMock()
    profiler.toggle.return_value = True
    profiler.is_active.return_value = False
    boot = SimpleNamespace(
        input_mapper=MagicMock(),
        ctx=SimpleNamespace(profiler=profiler),
        screen=MagicMock(),
        font_med=object(),
        font_large=object(),
        width=100,
        height=100,
    )
    router = SimpleNamespace(
        show_exit_dialog=False,
        showing_new_game_setup=False,
        showing_load_menu=False,
        showing_race_setup=False,
        menu_ui_manager=MagicMock(),
        active_scene=MagicMock(),
        strategy_scene=MagicMock(),
        battle_scene=SimpleNamespace(headless_mode=False, draw_hud=MagicMock()),
        update_resolution=MagicMock(),
    )
    state_machine = SimpleNamespace(state=state)
    return RunLoop(boot, router, state_machine), boot, router, state_machine


def test_request_shutdown_stops_loop():
    loop, _, _, _ = _make_loop()

    loop.request_shutdown()

    assert loop.running is False


def test_run_smoke_processes_one_frame_and_shutdown(monkeypatch):
    import game.services.llm.background as llm_background

    loop, boot, _, _ = _make_loop()
    boot.clock = MagicMock()
    boot.clock.tick.return_value = 250
    events = [SimpleNamespace(type=pygame.USEREVENT)]
    handle_normal_events = MagicMock(side_effect=lambda actual_events: loop.request_shutdown())
    update_and_draw = MagicMock()
    display_flip = MagicMock()
    pygame_quit = MagicMock()
    shutdown_all_calls = MagicMock()
    monkeypatch.setattr(pygame.event, "get", lambda: events)
    monkeypatch.setattr(pygame.display, "flip", display_flip)
    monkeypatch.setattr(pygame, "quit", pygame_quit)
    monkeypatch.setattr(loop, "_handle_normal_events", handle_normal_events)
    monkeypatch.setattr(loop, "_update_and_draw", update_and_draw)
    monkeypatch.setattr(llm_background, "shutdown_all_calls", shutdown_all_calls)

    loop.run()

    boot.clock.tick.assert_called_once_with(0)
    handle_normal_events.assert_called_once_with(events)
    update_and_draw.assert_called_once_with(0.1, events)
    display_flip.assert_called_once_with()
    shutdown_all_calls.assert_called_once_with(timeout=5.0)
    pygame_quit.assert_called_once_with()


def test_escape_closes_exit_dialog():
    loop, _, router, _ = _make_loop()
    router.show_exit_dialog = True
    event = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)

    loop._handle_exit_dialog_events([event])

    assert router.show_exit_dialog is False


def test_exit_dialog_yes_click_stops_loop(monkeypatch):
    loop, _, router, _ = _make_loop()
    router.show_exit_dialog = True
    monkeypatch.setattr(run_loop_module, "handle_exit_dialog_click", lambda pos: True)
    monkeypatch.setattr(run_loop_module, "handle_exit_dialog_cancel", lambda pos: False)
    event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, pos=(10, 10))

    loop._handle_exit_dialog_events([event])

    assert loop.running is False


def test_exit_dialog_cancel_click_hides_dialog(monkeypatch):
    loop, _, router, _ = _make_loop()
    router.show_exit_dialog = True
    monkeypatch.setattr(run_loop_module, "handle_exit_dialog_click", lambda pos: False)
    monkeypatch.setattr(run_loop_module, "handle_exit_dialog_cancel", lambda pos: True)
    event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, pos=(10, 10))

    loop._handle_exit_dialog_events([event])

    assert router.show_exit_dialog is False


def test_global_exit_action_opens_exit_dialog():
    loop, boot, router, _ = _make_loop()
    boot.input_mapper.resolve.return_value = InputAction.GLOBAL_EXIT
    event = SimpleNamespace(type=pygame.KEYDOWN)

    loop._handle_normal_events([event])

    assert router.show_exit_dialog is True
    boot.input_mapper.resolve.assert_called_once_with(event, contexts=["global"])


def test_global_profiler_action_toggles_profiler():
    loop, boot, _, _ = _make_loop()
    boot.input_mapper.resolve.return_value = InputAction.GLOBAL_TOGGLE_PROFILER
    event = SimpleNamespace(type=pygame.KEYDOWN)

    loop._handle_normal_events([event])

    boot.ctx.profiler.toggle.assert_called_once_with()


def test_menu_overlay_events_go_to_menu_ui_manager():
    loop, _, router, _ = _make_loop(GameState.MENU)
    router.showing_new_game_setup = True
    event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN)

    loop._forward_event_to_scene(event)

    router.menu_ui_manager.process_events.assert_called_once_with(event)
    router.active_scene.handle_event.assert_not_called()


def test_handle_resize_updates_boot_router_and_active_scene(monkeypatch):
    loop, boot, router, _ = _make_loop()
    new_surface = object()
    monkeypatch.setattr(pygame.display, "set_mode", lambda size, flags: new_surface)

    loop._handle_resize(640, 480)

    assert boot.screen is new_surface
    assert boot.width == 640
    assert boot.height == 480
    router.update_resolution.assert_called_once_with(640, 480)
    router.active_scene.handle_resize.assert_called_once_with(640, 480)


def test_update_and_draw_strategy_updates_input_before_scene_draw():
    loop, boot, router, _ = _make_loop(GameState.STRATEGY)
    events = [object()]

    loop._update_and_draw(0.25, events)

    router.strategy_scene.update_input.assert_called_once_with(0.25, events)
    router.active_scene.update.assert_called_once_with(0.25)
    router.active_scene.draw.assert_called_once_with(boot.screen)


def test_update_and_draw_battle_skips_headless_draw():
    loop, _, router, _ = _make_loop(GameState.BATTLE)
    router.battle_scene.headless_mode = True

    loop._update_and_draw(0.25, [])

    router.active_scene.update.assert_called_once_with(0.25)
    router.active_scene.draw.assert_not_called()
    router.battle_scene.draw_hud.assert_not_called()
