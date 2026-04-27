"""UI callback dispatcher + confirmation dialog controller.

Two small stateful helpers extracted from the original window manager:

* ``UICallbackDispatcher`` — pops callbacks from the composer's
  ``ui_callbacks`` dict on ``UI_BUTTON_PRESSED`` events. Registered by
  prompt dialogs (move-choice today; selection prompts in future).
* ``ConfirmationDialogController`` — owns the PROJ-198 single-pending
  confirmation dialog and routes ``UI_CONFIRMATION_DIALOG_CONFIRMED``
  events back to the stored callback.

Both are class instances rather than free functions because each owns
mutable state. The composer holds one of each and forwards
``process_ui_callbacks`` / ``show_confirmation_dialog`` /
``process_confirmation_event`` to them.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame
import pygame_gui

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class UICallbackDispatcher:
    """Pops callbacks from the composer's ``ui_callbacks`` map on button press.

    The actual map lives on the composer (so prompt registrars can register
    callbacks without holding a reference to the dispatcher). The
    dispatcher is the read-and-consume side.
    """

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def process(self, event) -> bool:
        """Process button press events for prompt dialogs.

        Args:
            event: The pygame event.

        Returns:
            True if a callback was executed, False otherwise.
        """
        c = self._composer
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in c.ui_callbacks:
                c.ui_callbacks[event.ui_element]()
                del c.ui_callbacks[event.ui_element]
                return True
        return False


class ConfirmationDialogController:
    """Owns the single-pending PROJ-198 confirmation-dialog state.

    The actual dialog reference and pending callback are stored on the
    composer (``_pending_confirmation_dialog`` / ``_pending_confirmation_callback``)
    so that ``StrategyEventRouter._is_blocking_ui_element_at`` can read
    the dialog directly for click-blocking.
    """

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def show(
        self,
        title: str,
        message: str,
        on_confirm: Callable,
        is_warning: bool = False,
    ) -> None:
        """Show a confirmation dialog for dangerous actions.

        Uses pygame_gui's UIConfirmationDialog. The on_confirm callback is stored
        and called when UI_CONFIRMATION_DIALOG_CONFIRMED event is received.

        Args:
            title: Dialog window title.
            message: Message to display.
            on_confirm: Callback when user confirms.
            is_warning: If True, indicates a dangerous/irreversible action (for styling).
        """
        # Local import preserved from source.
        import pygame_gui.windows

        c = self._composer
        dialog_rect = pygame.Rect(0, 0, 400, 200)
        dialog_rect.center = (c.width // 2, c.height // 2)

        dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=dialog_rect,
            action_long_desc=message,
            manager=c.manager,
            window_title=title,
        )
        # Store callback keyed by dialog element for event routing
        c._pending_confirmation_callback = on_confirm
        c._pending_confirmation_dialog = dialog

    def process_event(self, event) -> bool:
        """Process UI_CONFIRMATION_DIALOG_CONFIRMED events.

        Called by StrategyEventRouter to route confirmation events.

        Args:
            event: The pygame_gui event.

        Returns:
            True if a confirmation callback was executed, False otherwise.
        """
        c = self._composer
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if (
                c._pending_confirmation_dialog is not None
                and event.ui_element == c._pending_confirmation_dialog
            ):
                callback = c._pending_confirmation_callback
                c._pending_confirmation_dialog = None
                c._pending_confirmation_callback = None
                if callback:
                    callback()
                return True
        return False
