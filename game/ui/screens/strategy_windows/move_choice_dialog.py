"""Move Choice Dialog.

A small dialog asking the player whether to move to a sector statically or
to dynamically intercept a fleet at the target. Buttons are wired through
the composer's ``UICallbackDispatcher``.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
PROJ-313 Phase 6: promoted from inline ``pygame_gui.UIWindow`` construction
to a named ``MoveChoiceWindow`` subclass of ``StrategyModalWindow`` so it
follows the structural modal-tracking contract uniformly with all other
strategy modals.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame
import pygame_gui

from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class MoveChoiceWindow(StrategyModalWindow):
    """Modal window asking the player to choose a move type.

    PROJ-313: Promoted from inline `pygame_gui.UIWindow(...)` construction
    so move-choice follows the same StrategyModalWindow contract as every
    other strategy modal. Auto-registers in __init__, auto-deregisters
    in kill().
    """


class MoveChoiceDialog:
    """Registrar for the move-choice dialog."""

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

        win = MoveChoiceWindow(
            rect=rect, manager=c.manager,
            window_display_title="Select Move Type",
            window_manager=c,
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
