"""Event Log Window registrar (PROJ-77).

Two openers — one pulls all events via the facade, the other accepts a
pre-built list (used at turn start). The navigate callback closes the
window and re-centers the camera on the event hex.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
BUG-123: ``open_all`` now scopes to the active empire and surfaces the
empire name in the window title. ``open_with_events`` continues to accept
a pre-filtered list (turn-start path filters at the call site).
FEAT-26: injects a ``ReplayResolver`` (built from the active save's
``ReplayStore`` + the loaded component registry) and a
``launch_replay_callback`` that closes the modal and dispatches into
the scene-router's replay-mode battle entry.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import pygame

from game.ui.screens.event_log_window import EventLogWindow

if TYPE_CHECKING:
    from game.simulation.replay import ReplayRecord
    from game.strategy.services.replay_resolver import ReplayResolver
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


class EventLogRegistrar:
    """Lifecycle for the Event Log Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open_all(self) -> None:
        """Open the event-log window for the active empire (BUG-123).

        Reads ``scene.current_empire`` to scope the facade query and
        surface the empire name in the window title.
        """
        c = self._composer
        empire = c.scene.current_empire
        events = c.scene.facade.get_all_events(empire_id=empire.id)
        self._open_with(events, empire_name=getattr(empire, "name", None))

    def open_with_events(
        self, events: list, *, empire_name: Optional[str] = None
    ) -> None:
        """Open the event-log window with a specific event list.

        Used by the per-turn auto-popup path. ``empire_name`` (BUG-123)
        is optional — if provided, the window title shows the active
        empire so the player can confirm the filter is active.
        """
        self._open_with(events, empire_name=empire_name)

    # ---------------------------------------------------------------- helpers

    def _open_with(
        self, events: list, *, empire_name: Optional[str] = None
    ) -> None:
        c = self._composer
        if c.event_log_window:
            c.event_log_window.kill()

        w, h = int(c.width * 0.7), int(c.height * 0.7)
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        c.event_log_window = EventLogWindow(
            rect,
            c.manager,
            events,
            window_manager=c,
            on_close_callback=self._on_closed,
            on_navigate_callback=self._on_navigate,
            empire_name=empire_name,
            replay_resolver=self._build_replay_resolver(),
            launch_replay_callback=self._on_launch_replay,
        )

    def _build_replay_resolver(self) -> "Optional[ReplayResolver]":
        """FEAT-26: build a ``ReplayResolver`` for the active save.

        Returns None when no ``ReplayStore`` is registered (test paths /
        bootstrapping). The Replay button stays visible-but-disabled in
        that case (resolver=None ⇒ click is a no-op per
        ``EventLogWindow._handle_replay_click``).
        """
        from game.strategy.systems.save_game_service import get_replay_store

        store = get_replay_store()
        if store is None:
            return None
        try:
            from game.core.registry import (
                GameRegistries,
                get_default_registry_provider,
            )
            from game.strategy.services.replay_resolver import ReplayResolver
            provider = get_default_registry_provider()
            registries = GameRegistries(
                components=provider.get_components(),
                modifiers=provider.get_modifiers(),
                vehicle_classes=provider.get_vehicle_classes(),
                resources=provider.get_resources(),
                resource_catalog=provider.get_resource_catalog(),
            )
            return ReplayResolver.from_registries(store, registries)
        except Exception:  # Intentional broad catch: resolver build must not crash the Event Log open path
            logger.exception(
                "FEAT-26: failed to build ReplayResolver; "
                "Replay buttons will fall back to disabled."
            )
            return None

    def _on_launch_replay(self, record: "ReplayRecord") -> None:
        """FEAT-26: launch a captured replay in the BattleScreen.

        Closes the Event Log modal first (mirrors the navigate path),
        then dispatches into the scene router's replay-mode entry.
        """
        c = self._composer
        if c.event_log_window:
            c.event_log_window.kill()

        scene = c.scene
        # The router sits behind `scene.game` for production; tests using
        # the registrar in isolation may not wire it. Stay defensive.
        game = getattr(scene, "game", None)
        if game is None:
            logger.debug(
                "FEAT-26 launch_replay_callback skipped — scene has no game ref."
            )
            return
        try:
            game.start_replay(record)
        except AttributeError:
            logger.debug(
                "FEAT-26 launch_replay_callback skipped — game has no start_replay()."
            )

    def _on_navigate(self, location_hex: list) -> None:
        from game.core.hex_math import HexCoord

        hex_coord = HexCoord(location_hex[0], location_hex[1])

        c = self._composer
        if c.event_log_window:
            c.event_log_window.kill()

        if hasattr(c.scene, "_camera_nav"):
            c.scene._camera_nav.center_on_hex(hex_coord)

    def _on_closed(self) -> None:
        self._composer.event_log_window = None
