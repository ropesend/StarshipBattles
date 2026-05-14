"""Tests for strategy menu action routing (PROJ-72 Phase 3).

Tests the on_menu_option dispatcher in StrategyScreen, helper methods
(_show_load_game_dialog, _confirm_quit_to_menu, _show_coming_soon),
UIConfirmationDialog handling, and App.py scene action handlers.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock, call
import pygame


# --- Helpers ---

def _make_strategy_screen():
    """Create a StrategyScreen with mocked dependencies.

    Returns (screen, scene_callback_mock, ui_mock).
    """
    from game.ui.screens.strategy_screen import StrategyScreen

    # PROJ-327 Phase 4: bypass-init via __new__ only (no need to patch
    # __init__ to a no-op — __new__ skips it entirely). This file's tests
    # only exercise menu-action routing and do not touch the 8 sub-object
    # slots, so MockStrategyScreenComposition is not needed here.
    screen = StrategyScreen.__new__(StrategyScreen)

    scene_callback = MagicMock()
    ui_mock = MagicMock()
    manager_mock = MagicMock()
    ui_mock.manager = manager_mock

    screen.scene_callback = scene_callback
    screen.ui = ui_mock
    screen.screen_width = 1920
    screen.screen_height = 1080
    screen.session = MagicMock()
    screen._quit_confirm_dialog = None

    return screen, scene_callback, ui_mock


# ===========================================================================
# Task 3.1: on_menu_option dispatcher
# ===========================================================================

class TestOnMenuOption:
    """Test the on_menu_option method dispatches correctly."""

    def test_save_game_calls_on_save_game_click(self):
        """'save_game' option should call existing on_save_game_click."""
        screen, _, _ = _make_strategy_screen()
        screen.on_save_game_click = MagicMock()

        screen.on_menu_option("save_game")

        screen.on_save_game_click.assert_called_once()

    def test_load_game_calls_show_load_game_dialog(self):
        """'load_game' option should call _show_load_game_dialog."""
        screen, _, _ = _make_strategy_screen()
        screen._show_load_game_dialog = MagicMock()

        screen.on_menu_option("load_game")

        screen._show_load_game_dialog.assert_called_once()

    def test_settings_calls_open_settings(self):
        """'settings' option should call window_manager.open_settings()."""
        screen, _, ui = _make_strategy_screen()

        screen.on_menu_option("settings")

        ui.window_manager.open_settings.assert_called_once()

    def test_controls_calls_scene_callback(self):
        """'controls' option should call scene_callback('open_keybindings')."""
        screen, _, _ = _make_strategy_screen()
        screen.scene_callback = MagicMock()

        screen.on_menu_option("controls")

        screen.scene_callback.assert_called_once_with("open_keybindings")

    def test_quit_to_menu_calls_confirm_quit(self):
        """'quit_to_menu' option should call _confirm_quit_to_menu."""
        screen, _, _ = _make_strategy_screen()
        screen._confirm_quit_to_menu = MagicMock()

        screen.on_menu_option("quit_to_menu")

        screen._confirm_quit_to_menu.assert_called_once()

    def test_quit_game_calls_scene_callback(self):
        """'quit_game' option should call scene_callback('quit_game')."""
        screen, scene_callback, _ = _make_strategy_screen()

        screen.on_menu_option("quit_game")

        scene_callback.assert_called_once_with("quit_game")

    def test_quit_game_no_callback(self):
        """'quit_game' should not crash when scene_callback is None."""
        screen, _, _ = _make_strategy_screen()
        screen.scene_callback = None

        # Should not raise
        screen.on_menu_option("quit_game")

    def test_unknown_option_no_crash(self):
        """Unknown option should not crash."""
        screen, _, _ = _make_strategy_screen()

        # Should not raise
        screen.on_menu_option("nonexistent_option")


# ===========================================================================
# Task 3.1: _show_load_game_dialog
# ===========================================================================

class TestShowLoadGameDialog:
    """Test the _show_load_game_dialog method."""

    def test_creates_save_selection_window(self):
        """_show_load_game_dialog should create a SaveSelectionWindow."""
        screen, _, ui = _make_strategy_screen()

        with patch('game.ui.screens.save_selection_window.SaveSelectionWindow') as MockWindow:
            screen._show_load_game_dialog()

            # SaveSelectionWindow constructor should have been called
            MockWindow.assert_called_once()
            # Check it got the right manager
            args, kwargs = MockWindow.call_args
            assert args[1] == ui.manager  # manager argument


# ===========================================================================
# Task 3.1: _on_load_selected
# ===========================================================================

class TestOnLoadSelected:
    """Test the _on_load_selected callback."""

    def test_calls_scene_callback_with_load_game(self):
        """_on_load_selected should call scene_callback with load_game action."""
        screen, scene_callback, _ = _make_strategy_screen()

        screen._on_load_selected("/saves/test.json", turn_number=5)

        scene_callback.assert_called_once_with(
            "load_game", save_path="/saves/test.json", turn_number=5
        )

    def test_calls_scene_callback_without_turn(self):
        """_on_load_selected should work without turn_number."""
        screen, scene_callback, _ = _make_strategy_screen()

        screen._on_load_selected("/saves/test.json")

        scene_callback.assert_called_once_with(
            "load_game", save_path="/saves/test.json", turn_number=None
        )


# ===========================================================================
# Task 3.1: _confirm_quit_to_menu
# ===========================================================================

class TestConfirmQuitToMenu:
    """Test the _confirm_quit_to_menu method."""

    def test_creates_confirmation_dialog(self):
        """_confirm_quit_to_menu should create a UIConfirmationDialog."""
        screen, _, ui = _make_strategy_screen()

        with patch('pygame_gui.windows.UIConfirmationDialog') as MockDialog:
            screen._confirm_quit_to_menu()

            MockDialog.assert_called_once()
            _, kwargs = MockDialog.call_args
            assert kwargs['manager'] == ui.manager
            assert 'Quit to Menu' in kwargs['window_title']

    def test_stores_dialog_reference(self):
        """_confirm_quit_to_menu should store dialog reference."""
        screen, _, ui = _make_strategy_screen()

        with patch('pygame_gui.windows.UIConfirmationDialog') as MockDialog:
            mock_dialog_instance = MagicMock()
            MockDialog.return_value = mock_dialog_instance

            screen._confirm_quit_to_menu()

            assert screen._quit_confirm_dialog is mock_dialog_instance


# ===========================================================================
# Task 3.1: _show_coming_soon
# ===========================================================================

class TestShowComingSoon:
    """Test the _show_coming_soon method."""

    def test_creates_message_window(self):
        """_show_coming_soon should create a UIMessageWindow."""
        screen, _, ui = _make_strategy_screen()

        with patch('pygame_gui.windows.UIMessageWindow') as MockWindow:
            screen._show_coming_soon("Settings")

            MockWindow.assert_called_once()
            _, kwargs = MockWindow.call_args
            assert kwargs['manager'] == ui.manager
            assert kwargs['window_title'] == "Settings"
            assert "Coming Soon" in kwargs['html_message']

    def test_shows_feature_name(self):
        """_show_coming_soon should include the feature name."""
        screen, _, ui = _make_strategy_screen()

        with patch('pygame_gui.windows.UIMessageWindow') as MockWindow:
            screen._show_coming_soon("Controls")

            _, kwargs = MockWindow.call_args
            assert "Controls" in kwargs['html_message']


# ===========================================================================
# Task 3.1: UIConfirmationDialog handling
# ===========================================================================

class TestQuitConfirmationHandling:
    """Test that quit-to-menu confirmation triggers scene_callback."""

    def test_confirmed_quit_calls_scene_callback(self):
        """When quit dialog is confirmed, scene_callback('quit_to_menu') should be called."""
        screen, scene_callback, ui = _make_strategy_screen()

        # Simulate the dialog existing
        mock_dialog = MagicMock()
        screen._quit_confirm_dialog = mock_dialog

        # Call the handler
        screen._handle_quit_confirmed()

        scene_callback.assert_called_once_with("quit_to_menu")

    def test_confirmed_quit_clears_dialog_ref(self):
        """After confirmation, dialog reference should be cleared."""
        screen, _, _ = _make_strategy_screen()
        screen._quit_confirm_dialog = MagicMock()

        screen._handle_quit_confirmed()

        assert screen._quit_confirm_dialog is None


# ===========================================================================
# Task 3.2: App.py _handle_strategy_action extensions
# ===========================================================================

class TestAppStrategyActionHandler:
    """Test App._handle_strategy_action with new actions."""

    def _make_game(self):
        """Create a minimal Game-like object for testing."""
        from game.app import Game

        with patch.object(Game, '__init__', lambda self, *a, **kw: None):
            game = Game.__new__(Game)

        game.width = 1920
        game.height = 1080
        game._loop = MagicMock()
        game.strategy_scene = MagicMock()
        game.menu_scene = MagicMock()

        return game

    def test_load_game_handler(self):
        """'load_game' action should call _on_load_game."""
        game = self._make_game()
        game._on_load_game = MagicMock()

        game._handle_strategy_action("load_game", save_path="/saves/test.json", turn_number=3)

        game._on_load_game.assert_called_once_with("/saves/test.json", 3)

    def test_load_game_no_path(self):
        """'load_game' with no save_path should not call _on_load_game."""
        game = self._make_game()
        game._on_load_game = MagicMock()

        game._handle_strategy_action("load_game")

        game._on_load_game.assert_not_called()

    def test_quit_to_menu_handler(self):
        """'quit_to_menu' action should switch to MENU scene."""
        game = self._make_game()
        game._switch_scene = MagicMock()

        from game.core.constants import GameState
        game._handle_strategy_action("quit_to_menu")

        game._switch_scene.assert_called_once_with(GameState.MENU, game.menu_scene)

    def test_quit_game_handler(self):
        """'quit_game' action must route through `_request_shutdown` so
        the RunLoop's shutdown path runs (not a stale attribute write)."""
        game = self._make_game()

        game._handle_strategy_action("quit_game")

        game._loop.request_shutdown.assert_called_once_with()

    def test_open_builder_still_works(self):
        """Existing 'open_builder' action should still work."""
        game = self._make_game()
        game._create_workshop_context = MagicMock(return_value=None)
        game.start_builder = MagicMock()

        from game.core.constants import GameState
        game._handle_strategy_action("open_builder", context_data={"empire": MagicMock()})

        game.start_builder.assert_called_once()

    def test_launch_replay_handler_calls_start_replay(self):
        """'launch_replay' action should delegate to Game.start_replay (PROJ-368)."""
        game = self._make_game()
        game.start_replay = MagicMock()
        record = MagicMock()

        game._handle_strategy_action("launch_replay", record=record)

        game.start_replay.assert_called_once_with(record)

    def test_launch_replay_handler_no_record_is_noop(self):
        """'launch_replay' without a record kwarg should be a no-op (PROJ-368)."""
        game = self._make_game()
        game.start_replay = MagicMock()

        game._handle_strategy_action("launch_replay")

        game.start_replay.assert_not_called()
