"""Event Log Window registrar (PROJ-77).

Two openers — one pulls all events via the facade, the other accepts a
pre-built list (used at turn start). The navigate callback closes the
window and re-centers the camera on the event hex.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.ui.screens.event_log_window import EventLogWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class EventLogRegistrar:
    """Lifecycle for the Event Log Window slot."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open_all(self) -> None:
        """Open the event-log window with every event the facade currently has."""
        c = self._composer
        events = c.scene.facade.get_all_events()
        self._open_with(events)

    def open_with_events(self, events: list) -> None:
        """Open the event-log window with a specific event list (turn-start usage)."""
        self._open_with(events)

    # ---------------------------------------------------------------- helpers

    def _open_with(self, events: list) -> None:
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
