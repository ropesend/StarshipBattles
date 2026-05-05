"""Strategy screen lifecycle / menu / save-load helper (PROJ-330).

Extracted from ``strategy_screen.py`` as part of the LOC decomposition.
This module owns the menu-option dispatch, save/load dialogs, and
quit-confirmation flow. Each function takes the ``StrategyScreen`` as a
parameter and mutates it directly — there is no new MVVM seam.

The extraction is mechanical: the screen's public methods (``on_menu_option``,
``on_save_game_click``, ``on_design_click``) delegate to the functions here,
so the test surface is unchanged.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from game.ui.config import UIConfig

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen

logger = logging.getLogger(__name__)


def on_design_click(screen: "StrategyScreen") -> None:
    """Handle 'Design' button click - opens Design Workshop."""
    logger.debug("Design button clicked - opening Design Workshop")

    context_data = {
        "empire": screen.session.active_empire,
        "game_session": screen.session,
    }

    if screen.scene_callback:
        screen.scene_callback("open_builder", context_data=context_data)


def on_menu_option(screen: "StrategyScreen", option: str) -> None:
    """Dispatch menu option from the strategy menu panel.

    Calls back through the screen's bound methods (rather than this module's
    free functions) so tests that monkey-patch ``screen.on_save_game_click``,
    ``screen._show_load_game_dialog``, or ``screen._confirm_quit_to_menu``
    continue to observe the call.
    """
    if option == "save_game":
        screen.on_save_game_click()
    elif option == "load_game":
        screen._show_load_game_dialog()
    elif option == "settings":
        screen.ui.window_manager.open_settings()
    elif option == "controls":
        if screen.scene_callback:
            screen.scene_callback("open_keybindings")
    elif option == "quit_to_menu":
        screen._confirm_quit_to_menu()
    elif option == "quit_game":
        if screen.scene_callback:
            screen.scene_callback("quit_game")


def show_load_game_dialog(screen: "StrategyScreen") -> None:
    """Open the save selection window for loading a game.

    PROJ-352 T6.6: pass ``screen.ui.window_manager`` so the dialog
    auto-registers as a strategy modal and blocks strategy-screen input
    while open. Without this the load dialog historically coexisted with
    hex-clicks / sidebar-buttons because it was a raw ``UIWindow`` and
    the modal tracker never saw it.
    """
    from game.ui.screens.save_selection_window import SaveSelectionWindow
    from game.ui.utils import create_centered_rect

    window_rect = create_centered_rect(600, 500, screen.screen_width, screen.screen_height)
    SaveSelectionWindow(
        window_rect,
        screen.ui.manager,
        on_load_callback=lambda save_path, turn_number=None: on_load_selected(
            screen, save_path, turn_number
        ),
        on_cancel_callback=lambda: None,
        window_manager=screen.ui.window_manager,
    )


def on_load_selected(screen: "StrategyScreen", save_path, turn_number=None) -> None:
    """Handle save selection from load dialog."""
    if screen.scene_callback:
        screen.scene_callback("load_game", save_path=save_path, turn_number=turn_number)


def confirm_quit_to_menu(screen: "StrategyScreen") -> None:
    """Show confirmation dialog before quitting to main menu."""
    import pygame_gui.windows

    dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
    dialog_rect.center = (screen.screen_width // 2, screen.screen_height // 2)
    screen._quit_confirm_dialog = pygame_gui.windows.UIConfirmationDialog(
        rect=dialog_rect,
        action_long_desc="Unsaved progress will be lost. Return to main menu?",
        manager=screen.ui.manager,
        window_title="Quit to Menu",
    )


def handle_quit_confirmed(screen: "StrategyScreen") -> None:
    """Handle quit-to-menu confirmation dialog result."""
    screen._quit_confirm_dialog = None
    if screen.scene_callback:
        screen.scene_callback("quit_to_menu")


def show_coming_soon(screen: "StrategyScreen", feature_name: str) -> None:
    """Show a 'Coming Soon' placeholder dialog."""
    import pygame_gui.windows

    dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
    dialog_rect.center = (screen.screen_width // 2, screen.screen_height // 2)
    pygame_gui.windows.UIMessageWindow(
        rect=dialog_rect,
        html_message=f"<b>{feature_name}</b><br><br>Coming Soon!",
        manager=screen.ui.manager,
        window_title=feature_name,
    )


def on_save_game_click(screen: "StrategyScreen") -> None:
    """Handle 'Save Game' button click."""
    from game.strategy.systems.save_game_service import SaveGameService
    import pygame_gui.windows

    logger.info("Saving game...")

    success, message, _save_path = SaveGameService.save_game(screen.session)

    dialog_rect = pygame.Rect(0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT)
    dialog_rect.center = (screen.screen_width // 2, screen.screen_height // 2)

    if success:
        pygame_gui.windows.UIMessageWindow(
            rect=dialog_rect,
            html_message=f"<b>Game Saved Successfully!</b><br><br>{message}",
            manager=screen.ui.manager,
            window_title="Save Game",
        )
        logger.info(f"Game saved: {message}")
    else:
        pygame_gui.windows.UIMessageWindow(
            rect=dialog_rect,
            html_message=f"<b>Save Failed</b><br><br>{message}",
            manager=screen.ui.manager,
            window_title="Save Game Error",
        )
        logger.warning(f"Save failed: {message}")
