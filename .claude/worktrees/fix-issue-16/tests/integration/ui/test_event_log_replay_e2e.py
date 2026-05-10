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


@pytest.fixture
def pygame_init():
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
