"""Defeat modal dialog (issue #25).

Shown once at an empire's first turn-start after it satisfies
``Empire.is_eliminated()`` (no fleets and no colonies). Modeled on
:class:`TurnFailedDialog` — subclasses :class:`StrategyModalWindow` so
the strategy window manager registers it in ``iter_live_modals()`` and
``StrategyEventRouter.has_modal_open()`` treats it as input-blocking
(Pattern #31 modal tracking), preventing further End Turn clicks or
fleet commands while the player reads the message.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from game.ui.screens.strategy_modal_window import DismissableModalDialog

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


_DIALOG_WIDTH = 480
_DIALOG_HEIGHT = 240


def _format_body(empire_name: str) -> str:
    """Render the dialog body HTML.

    Wording is locked by the issue #25 acceptance criteria (user-confirmed
    final text). The empire name is rendered as the heading so the player
    sees which of their empires fell — relevant if a future feature gives
    one player multiple empires.
    """
    return (
        f"<b>Your empire has been destroyed.</b><br><br>"
        f"<i>{empire_name}</i><br><br>"
        "All of your units and planets are lost."
    )


class DefeatDialog(DismissableModalDialog):
    """Modal dialog shown once when an empire is first detected as defeated.

    Inherits from :class:`StrategyModalWindow` so it auto-registers with
    the :class:`StrategyWindowManager` on construction and auto-deregisters
    in :meth:`kill`. While the dialog is alive, ``iter_live_modals`` yields
    it and ``StrategyEventRouter.has_modal_open()`` returns ``True``,
    blocking End Turn and fleet commands until the player dismisses it.

    Layout: a single read-only ``UITextBox`` with the defeat message and
    a "Dismiss" button.
    """

    def __init__(
        self,
        *,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        empire_name: str,
        window_manager: "StrategyWindowManager | None",
    ) -> None:
        """Build the dialog and wire the dismiss button.

        Args:
            rect: Window rectangle (centered by the caller).
            manager: pygame_gui UIManager for widget construction.
            empire_name: Name shown in the dialog body so the player sees
                which empire fell.
            window_manager: StrategyWindowManager used for modal
                registration. Pass ``None`` only outside the strategy
                screen; production always passes the live manager.
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Empire Destroyed",
            window_manager=window_manager,
        )

        self._dismiss_button: UIButton | None = None

        if getattr(self, "_window_init_bypassed", False):
            return

        body_rect = pygame.Rect(10, 10, _DIALOG_WIDTH - 30, _DIALOG_HEIGHT - 90)
        pygame_gui.elements.UITextBox(
            html_text=_format_body(empire_name),
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
