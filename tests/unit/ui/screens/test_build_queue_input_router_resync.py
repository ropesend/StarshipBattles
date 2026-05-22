"""PROJ-472 1D — pin the stale-DTO resync auto-trigger.

PROJ-472 1B introduced ``_resync_sources_from_facade`` so that, after a
command mutates the domain queue, the held immutable ``BuildQueueSourceDTO``
snapshots are re-projected and the display reflects the new state. The Codex
end-of-project audit (2026-05-21) flagged that no test directly pinned that
each command dispatcher auto-calls the resync — if one hook regressed (drops
the resync call) the display would silently go stale. These tests pin it.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.ui.screens.build_queue_input_router import BuildQueueInputRouter


def _router_with_active_source(context_type: str = "planet"):
    screen = MagicMock()
    screen.facade = MagicMock()
    source = SimpleNamespace(
        context_type=context_type,
        entity_id=7,
        queue_id="q-1",
        is_paused=False,
        construction_queue=[],
    )
    screen.active_queue_source = source
    router = BuildQueueInputRouter(screen)
    router._resync_sources_from_facade = MagicMock()
    router._refresh_queue_display = MagicMock()
    return router, screen, source


def test_add_dispatch_auto_resyncs_after_command() -> None:
    router, screen, _ = _router_with_active_source()
    router._dispatch_add_to_queue_command(
        entity_id=7,
        entity_type="planet",
        design_id="d1",
        category="ships",
        index=None,
        target_planet_id=None,
        queue_id="q-1",
    )
    screen.facade.handle_command.assert_called_once()
    router._resync_sources_from_facade.assert_called_once()


def test_remove_dispatch_auto_resyncs_after_command() -> None:
    router, screen, _ = _router_with_active_source()
    router._dispatch_remove_from_queue_command(item_index=0)
    screen.facade.handle_command.assert_called_once()
    router._resync_sources_from_facade.assert_called_once()


def test_pause_dispatch_auto_resyncs_and_refreshes() -> None:
    router, screen, _ = _router_with_active_source()
    router._dispatch_toggle_pause_command()
    screen.facade.handle_command.assert_called_once()
    router._resync_sources_from_facade.assert_called_once()
    router._refresh_queue_display.assert_called_once()


def test_pause_dispatch_noop_when_no_active_source() -> None:
    router, screen, _ = _router_with_active_source()
    screen.active_queue_source = None
    router._dispatch_toggle_pause_command()
    screen.facade.handle_command.assert_not_called()
    router._resync_sources_from_facade.assert_not_called()
