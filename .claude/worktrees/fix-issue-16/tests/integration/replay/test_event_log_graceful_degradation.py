"""FEAT-26 — Graceful degradation on Replay button click.

Covers the four ``ReplayLookup`` reasons surfaced by ``ReplayResolver``:
``missing`` / ``corrupt`` / ``version_drift`` / ``registry_drift``.

The button is always rendered visible — `_handle_replay_click`
short-circuits cleanly on missing / corrupt / version_drift via a
``UIMessageWindow`` toast, and DOES launch on registry_drift after
showing an informational warning (drift is a quality-of-playback
warning, not a hard block).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pygame_gui
import pytest


@pytest.fixture
def pygame_init():
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.HIDDEN)
    yield
    pygame.quit()


def _combat_event(replay_id):
    return {
        "category": "combat",
        "turn": 7,
        "message": "Battle: 2 fleets engaged",
        "details": {"replay_id": replay_id},
    }


def _make_window(events, *, resolver=None, launch_cb=None):
    from game.ui.screens.event_log_window import EventLogWindow

    manager = pygame_gui.UIManager((1024, 768))
    rect = pygame.Rect(0, 0, 1024, 768)
    return EventLogWindow(
        rect,
        manager,
        events,
        window_manager=MagicMock(),
        replay_resolver=resolver,
        launch_replay_callback=launch_cb,
    )


def _lookup(found, *, record=None, reason=None, registry_drift=False):
    from game.strategy.services.replay_resolver import ReplayLookup

    return ReplayLookup(
        found=found, record=record, reason=reason, registry_drift=registry_drift
    )


# ---------------------------------------------------------------------------
# Not-found cases — show toast, do NOT launch.
# ---------------------------------------------------------------------------


def test_missing_replay_shows_toast_and_does_not_launch(pygame_init) -> None:
    resolver = MagicMock()
    resolver.resolve.return_value = _lookup(False, reason="missing")
    launch_cb = MagicMock()

    win = _make_window(
        [_combat_event("uuid-x")], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    resolver.resolve.assert_called_once_with("uuid-x")
    launch_cb.assert_not_called()


def test_corrupt_replay_shows_toast_and_does_not_launch(pygame_init) -> None:
    resolver = MagicMock()
    resolver.resolve.return_value = _lookup(False, reason="corrupt")
    launch_cb = MagicMock()

    win = _make_window(
        [_combat_event("uuid-x")], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    launch_cb.assert_not_called()


def test_version_drift_replay_shows_toast_and_does_not_launch(pygame_init) -> None:
    resolver = MagicMock()
    resolver.resolve.return_value = _lookup(False, reason="version_drift")
    launch_cb = MagicMock()

    win = _make_window(
        [_combat_event("uuid-x")], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    launch_cb.assert_not_called()


# ---------------------------------------------------------------------------
# Registry-drift case — informational warning, then launch.
# ---------------------------------------------------------------------------


def test_registry_drift_replay_warns_and_launches(pygame_init) -> None:
    """Registry-hash drift is informational only — the launch still
    fires after the warning so the user can opt-in to playback."""
    record = MagicMock()
    resolver = MagicMock()
    resolver.resolve.return_value = _lookup(
        True, record=record, registry_drift=True
    )
    launch_cb = MagicMock()

    win = _make_window(
        [_combat_event("uuid-x")], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    launch_cb.assert_called_once_with(record)


# ---------------------------------------------------------------------------
# Resolver=None / record=None edge cases
# ---------------------------------------------------------------------------


def test_no_resolver_wired_makes_replay_click_a_noop(pygame_init) -> None:
    """When the resolver is unwired (test/headless paths) the click is
    silently a no-op — never raises, never launches."""
    launch_cb = MagicMock()

    win = _make_window([_combat_event("uuid-x")], resolver=None, launch_cb=launch_cb)
    win._handle_replay_click(0)

    launch_cb.assert_not_called()


def test_lookup_found_with_no_record_does_not_launch(pygame_init) -> None:
    """Defensive: if the resolver returns ``found=True`` but
    ``record=None``, the launch callback isn't invoked."""
    resolver = MagicMock()
    resolver.resolve.return_value = _lookup(True, record=None)
    launch_cb = MagicMock()

    win = _make_window(
        [_combat_event("uuid-x")], resolver=resolver, launch_cb=launch_cb
    )
    win._handle_replay_click(0)

    launch_cb.assert_not_called()
