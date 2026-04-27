"""Move Choice Dialog — the only window built inline from pygame_gui primitives.

A small dialog asking the player whether to move to a sector statically or
to dynamically intercept a fleet at the target. Buttons are wired through
the composer's ``UICallbackDispatcher``.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame
import pygame_gui

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class MoveChoiceDialog:
    """Inline-built dialog asking the player to choose a move type."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def show(
        self,
        fleet,
        target_hex,
        on_move_sector: Callable,
        on_intercept_fleet: Callable,
    ) -> None:
        """Open the move-choice dialog and register the two button callbacks.

        Args:
            fleet: The fleet being ordered.
            target_hex: The target hex coordinate.
            on_move_sector: Callback for static sector move.
            on_intercept_fleet: Callback for dynamic fleet intercept.
        """
        c = self._composer
        width = 300
        height = 150
        x = (c.width - width) / 2
        y = (c.height - height) / 2
        rect = pygame.Rect(x, y, width, height)

        win = pygame_gui.elements.UIWindow(
            rect=rect, manager=c.manager, window_display_title="Select Move Type"
        )
        c.move_choice_window = win

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 280, 30),
            text="Fleet detected at target.",
            manager=c.manager,
            container=win,
        )

        btn_sector = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 280, 30),
            text="Move to Sector (Static)",
            manager=c.manager,
            container=win,
        )

        btn_intercept = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 90, 280, 30),
            text="Intercept Fleet (Dynamic)",
            manager=c.manager,
            container=win,
        )

        # Store callbacks for button-press handling via UICallbackDispatcher.
        c.ui_callbacks[btn_sector] = lambda: (on_move_sector(), win.kill())
        c.ui_callbacks[btn_intercept] = lambda: (on_intercept_fleet(), win.kill())
