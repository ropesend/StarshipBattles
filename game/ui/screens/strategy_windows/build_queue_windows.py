"""Build-queue window registrars: per-empire list + empire-wide queue.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.ui.screens.build_queue_list_window import BuildQueueListWindow
from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class BuildQueueListRegistrar:
    """Lifecycle for the Build Queue List Window slot (BUG-67)."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer
        if c.build_queue_list_window:
            c.build_queue_list_window.kill()

        empire = c.scene.current_empire

        w, h = 700, 500
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        c.build_queue_list_window = BuildQueueListWindow(
            rect,
            c.manager,
            empire,
            window_manager=c,
            on_close_callback=self._on_closed,
            input_mapper=c._mapper,
        )

    def _on_closed(self) -> None:
        self._composer.build_queue_list_window = None


class EmpireBuildQueueRegistrar:
    """Lifecycle for the Empire-Wide Build Queue Window slot (PROJ-76)."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self) -> None:
        c = self._composer
        if c.empire_build_queue_window:
            c.empire_build_queue_window.kill()

        empire = c.scene.current_empire
        galaxy = c.scene.galaxy

        w, h = int(c.width * 0.9), int(c.height * 0.9)
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        # PROJ-208 Phase 3: Pass facade for CQRS-compliant command dispatch
        c.empire_build_queue_window = EmpireBuildQueueWindow(
            rect,
            c.manager,
            empire,
            galaxy,
            window_manager=c,
            on_close_callback=self._on_closed,
            on_navigate_to_hex=c.scene.on_navigate_to_hex_build,
            session=c.scene.session,
            facade=c.scene.facade,
        )

    def close(self) -> None:
        c = self._composer
        if c.empire_build_queue_window:
            c.empire_build_queue_window.kill()
            c.empire_build_queue_window = None

    def _on_closed(self) -> None:
        self._composer.empire_build_queue_window = None
