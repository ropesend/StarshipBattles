"""Turn-failed modal dialog (PROJ-395 / PROJ-381 CRIT-001 remediation).

Replaces the raw ``pygame_gui.windows.UIMessageWindow`` previously
constructed inline in ``StrategyGameStateManager._show_turn_failed_dialog``.
That call bypassed Pattern #31 modal tracking — players could click
through the error dialog and continue issuing fleet commands or
advance the turn while the error was still on screen.

This module supplies a ``TurnFailedDialog`` that subclasses
:class:`StrategyModalWindow` so ``StrategyWindowManager`` registers it
in ``iter_live_modals()`` and ``StrategyEventRouter.has_modal_open()``
treats it as input-blocking just like every other strategy modal.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame
import pygame_gui

from game.core.exceptions import EnginePhaseError, TurnFailedError
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


_DIALOG_WIDTH = 480
_DIALOG_HEIGHT = 280


def _format_body(error: TurnFailedError | EnginePhaseError) -> str:
    """Render the dialog body HTML from the error context.

    Args:
        error: The caught engine-phase / turn-failed error.

    Returns:
        HTML string for ``UITextBox``. Falls back to ``"unknown"`` /
        ``"?"`` for missing context keys so dialog construction never
        raises.
    """
    ctx: dict[str, Any] = error.context or {}
    phase_name = ctx.get("phase_name", "unknown")
    tick = ctx.get("tick", "?")
    original_type = ctx.get("original_type", "Exception")
    turn_number = ctx.get("turn_number", "?")
    return (
        "<b>Turn processing failed</b><br><br>"
        f"Turn: <b>{turn_number}</b><br>"
        f"Phase: <b>{phase_name}</b><br>"
        f"Tick: {tick}<br>"
        f"Cause: {original_type}<br><br>"
        "Turn has been rolled back &mdash; empire state is preserved."
    )


class TurnFailedDialog(StrategyModalWindow):
    """Modal dialog shown when a turn-processing phase fails.

    Inherits from :class:`StrategyModalWindow` so it auto-registers with
    the :class:`StrategyWindowManager` on construction and auto-deregisters
    in :meth:`kill`. While the dialog is alive, ``iter_live_modals`` yields
    it and ``StrategyEventRouter.has_modal_open()`` returns ``True``,
    blocking strategy-screen input (fleet commands, end-turn button).

    Layout: a single read-only ``UITextBox`` rendering the failure
    summary and a "Dismiss" button that closes the window.
    """

    def __init__(
        self,
        *,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        error: TurnFailedError | EnginePhaseError,
        window_manager: "StrategyWindowManager | None",
    ) -> None:
        """Build the dialog and wire the dismiss button.

        Args:
            rect: Window rectangle (centered by the caller).
            manager: pygame_gui UIManager for widget construction.
            error: The caught error whose context drives the body text.
            window_manager: StrategyWindowManager used for modal
                registration. Pass ``None`` only outside the strategy
                screen (e.g., a test fixture); production always passes
                the live manager.
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Turn Failed",
            window_manager=window_manager,
        )

        # Bypass-init shortcut for tests that skip UIWindow.__init__.
        if getattr(self, "_window_init_bypassed", False):
            self._dismiss_button = None  # type: ignore[assignment]
            return

        body_rect = pygame.Rect(10, 10, _DIALOG_WIDTH - 30, _DIALOG_HEIGHT - 90)
        pygame_gui.elements.UITextBox(
            html_text=_format_body(error),
            relative_rect=body_rect,
            manager=manager,
            container=self,
        )

        button_rect = pygame.Rect(
            (_DIALOG_WIDTH - 130) // 2,
            _DIALOG_HEIGHT - 70,
            120,
            32,
        )
        self._dismiss_button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text="Dismiss",
            manager=manager,
            container=self,
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle the dismiss-button click.

        Returns ``True`` if this dialog consumed the event so pygame_gui
        does not deliver it elsewhere; otherwise delegates to the base
        class.
        """
        if (
            event.type == pygame_gui.UI_BUTTON_PRESSED
            and getattr(self, "_dismiss_button", None) is not None
            and event.ui_element is self._dismiss_button
        ):
            self.kill()
            return True
        return super().process_event(event)
