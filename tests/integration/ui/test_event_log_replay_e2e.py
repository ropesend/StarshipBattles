"""FEAT-26 — End-to-end Replay button click flow through EventLogWindow.

Drives the path from a real ``pygame_gui.UI_BUTTON_PRESSED`` event
through the table action-column dispatch into ``_handle_replay_click``,
the resolver, and the launch callback.

Re-clicking after a successful launch must work (idempotent — common
playback pattern: open Event Log → Replay → exit replay → Replay
again on the same row).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pygame_gui
import pytest


@pytest.fixture(scope="module")
def pygame_init():
    """PROJ-479 Task 2.6: module-scoped pygame init — reusable across all
    tests in this module since pygame.display.set_mode HIDDEN is read-only."""
    pygame.init()
    pygame.display.set_mode((1024, 768), pygame.HIDDEN)
    yield
    pygame.quit()


def _combat_event(replay_id, turn=7):
    return {
        "category": "combat",
        "turn": turn,
        "message": "Battle: 2 fleets engaged",
        "details": {"replay_id": replay_id},
    }


def _make_window(events, *, resolver, launch_cb):
    from game.ui.screens.event_log_window import EventLogWindow

    manager = pygame_gui.UIManager((1024, 768))
    rect = pygame.Rect(0, 0, 1024, 768)
    win = EventLogWindow(
        rect,
        manager,
        events,
        window_manager=MagicMock(),
        empire_name="Test Empire",
        replay_resolver=resolver,
        launch_replay_callback=launch_cb,
    )
    return win, manager


def _find_replay_button_for_row(virtual_table, row_index):
    """Walk the row pool and return the replay_action button for the
    requested data row index."""
    for row in virtual_table._row_pool:
        if row.get("row_index") != row_index:
            continue
        for widget in row.get("widgets", []):
            if widget.get("type") == "replay_action":
                return widget["button"]
    return None


def test_button_press_event_invokes_resolver_and_launch(pygame_init) -> None:
    from game.strategy.services.replay_resolver import ReplayLookup

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(found=True, record=record)
    launch_cb = MagicMock()

    win, _manager = _make_window(
        [_combat_event("uuid-1")], resolver=resolver, launch_cb=launch_cb
    )
    win.virtual_table.update_visible_rows()

    btn = _find_replay_button_for_row(win.virtual_table, 0)
    assert btn is not None
    assert btn.is_enabled

    fake_event = pygame.event.Event(
        pygame_gui.UI_BUTTON_PRESSED, {"ui_element": btn}
    )
    handled = win.process_event(fake_event)

    assert handled is True
    resolver.resolve.assert_called_once_with("uuid-1")
    launch_cb.assert_called_once_with(record)


def test_two_clicks_in_a_row_both_launch_idempotently(pygame_init) -> None:
    """User opens Event Log, clicks Replay, replay finishes, returns to
    Event Log, clicks Replay again — second click must work too."""
    from game.strategy.services.replay_resolver import ReplayLookup

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(found=True, record=record)
    launch_cb = MagicMock()

    win, _manager = _make_window(
        [_combat_event("uuid-2")], resolver=resolver, launch_cb=launch_cb
    )
    win.virtual_table.update_visible_rows()
    btn = _find_replay_button_for_row(win.virtual_table, 0)

    win.process_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": btn})
    )
    win.process_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": btn})
    )

    assert resolver.resolve.call_count == 2
    assert launch_cb.call_count == 2


def test_replay_button_routes_through_scene_callback_end_to_end(pygame_init) -> None:
    """PROJ-368: the full path — UI button press → EventLogWindow →
    EventLogRegistrar._on_launch_replay → scene.scene_callback —
    must reach the strategy scene callback with ('launch_replay', record=...).

    Regression for the bug where the registrar reached for a non-existent
    `scene.game` attribute and silently swallowed the click.
    """
    from game.strategy.services.replay_resolver import ReplayLookup
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    # Build a real registrar wired through StrategyWindowManager. The scene
    # is a Mock with a real callable scene_callback that captures the call.
    captured: list[tuple] = []

    def scene_callback(action, **kwargs):
        captured.append((action, kwargs))

    scene = MagicMock()
    scene.scene_callback = scene_callback
    scene.current_empire = MagicMock()
    scene.current_empire.id = 1

    wm = StrategyWindowManager(
        scene=scene,
        manager=MagicMock(),
        width=1024,
        height=768,
        input_mapper=None,
        asset_resolver=None,
    )

    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = ReplayLookup(found=True, record=record)

    # Build a real EventLogWindow whose launch callback IS the registrar's
    # _on_launch_replay. The composer is the real wm so the registrar can
    # close the modal on success.
    from game.ui.screens.event_log_window import EventLogWindow
    manager = pygame_gui.UIManager((1024, 768))
    rect = pygame.Rect(0, 0, 1024, 768)
    win = EventLogWindow(
        rect,
        manager,
        [_combat_event("uuid-e2e")],
        window_manager=wm,
        empire_name="Test Empire",
        replay_resolver=resolver,
        launch_replay_callback=wm._event_log._on_launch_replay,
    )
    wm.event_log_window = win
    win.virtual_table.update_visible_rows()

    btn = _find_replay_button_for_row(win.virtual_table, 0)
    assert btn is not None and btn.is_enabled

    win.process_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": btn})
    )

    assert captured == [("launch_replay", {"record": record})]


def test_legacy_row_button_is_disabled_and_click_is_noop(pygame_init) -> None:
    """A legacy combat event (no replay_id) renders the button disabled
    and clicks short-circuit before the resolver is reached."""
    legacy = {
        "category": "combat",
        "turn": 5,
        "message": "old battle",
        "details": {},
    }
    resolver = MagicMock()
    launch_cb = MagicMock()

    win, _manager = _make_window([legacy], resolver=resolver, launch_cb=launch_cb)
    win.virtual_table.update_visible_rows()
    btn = _find_replay_button_for_row(win.virtual_table, 0)
    assert btn is not None
    assert not btn.is_enabled

    # Even if a click event somehow reaches process_event (defensive):
    # the data source returns None for replay_id and the handler bails.
    win.process_event(
        pygame.event.Event(pygame_gui.UI_BUTTON_PRESSED, {"ui_element": btn})
    )
    resolver.resolve.assert_not_called()
    launch_cb.assert_not_called()
