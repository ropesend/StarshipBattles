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
    """Handle 'Design' button click - opens Design Workshop.

    Anchors ``context_data["empire"]`` to ``screen.current_empire``
    (the viewing human), NOT ``session.active_empire`` (the turn-acting
    empire). In hot-seat play the two can diverge — the user saw QA
    Obs 1 (post-PROJ-FMS, 2026-05-16) where saving a Mine design while
    ``active_empire`` had rotated wrote the JSON under the wrong
    empire's ``designs/`` folder and the build queue (which scans the
    planet owner's folder) showed empty Available Designs.

    See ``feedback_viewing_empire_anchor`` memory for the rule.
    """
    logger.debug("Design button clicked - opening Design Workshop")

    # QA Obs 3 (2026-05-16) / PROJ-434 Phase 2: pass the live facade so
    # the app-side workshop context can thread ``facade_state`` through
    # to the per-empire ``DesignCatalog``. Without this, the workshop
    # save can't route through the same catalog instance the Build Queue
    # reads from and the new design appears stale after a save. See
    # ``feedback_viewing_empire_anchor`` for the related
    # current_empire-vs-active_empire anchoring rule.
    # PROJ-475 Phase 2 Task 2.4: hand the workshop a scalar ``save_path``
    # (read via the facade) instead of the live ``game_session`` — the app
    # only reads ``.save_path`` off it, so the UI never threads the session.
    context_data = {
        "empire": screen.current_empire,
        "save_path": screen.facade.session_meta.save_path(),
        "facade": screen.facade,
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

    PROJ-352A T6.6: pass ``screen.ui.window_manager`` so the dialog
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
    import pygame_gui.windows

    logger.info("Saving game...")

    # PROJ-475 Phase 2 Task 2.4: save via the facade (it owns the session and
    # calls SaveGameService internally) — the UI no longer imports the service.
    success, message, _save_path = screen.facade.session_meta.save_current_game()

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
