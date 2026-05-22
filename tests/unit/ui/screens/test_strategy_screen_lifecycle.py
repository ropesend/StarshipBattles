"""Tests for ``strategy_screen_lifecycle`` (PROJ-330).

Each helper takes the screen as a parameter; tests pass a ``MagicMock``
shaped just enough to satisfy the helper. The helpers do not import the
screen class itself (``TYPE_CHECKING`` only), so no real screen is needed.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.ui.screens import strategy_screen_lifecycle as lifecycle


def _make_screen():
    screen = MagicMock()
    screen.screen_width = 1920
    screen.screen_height = 1080
    screen.scene_callback = MagicMock()
    screen.session = MagicMock()
    screen.session.active_empire = MagicMock(id=0)
    # QA Obs 1 (post-PROJ-FMS, 2026-05-16): on_design_click now anchors
    # ``context_data["empire"]`` to ``screen.current_empire`` (the viewing
    # human), not ``session.active_empire``. The mock exposes a separate
    # ``current_empire`` so the test can verify the anchor.
    screen.current_empire = MagicMock(id=0)
    screen.ui = MagicMock()
    screen.ui.manager = MagicMock()
    screen.ui.window_manager = MagicMock()
    screen._quit_confirm_dialog = None
    return screen


class TestOnDesignClick:
    def test_invokes_callback_with_context(self):
        screen = _make_screen()
        lifecycle.on_design_click(screen)
        screen.scene_callback.assert_called_once()
        args, kwargs = screen.scene_callback.call_args
        assert args[0] == "open_builder"
        # QA Obs 1: anchor is ``current_empire`` (viewing human), NOT
        # ``session.active_empire`` (turn-acting empire). The dedicated
        # regression suite lives in ``test_viewing_empire_anchor.py``.
        assert kwargs["context_data"]["empire"] is screen.current_empire
        # PROJ-475 Phase 2 Task 2.4: the workshop context now carries a scalar
        # ``save_path`` (from facade.session_meta.save_path()), not the live
        # ``game_session``.
        assert (
            kwargs["context_data"]["save_path"]
            is screen.facade.session_meta.save_path.return_value
        )
        assert "game_session" not in kwargs["context_data"]

    def test_no_callback_no_call(self):
        screen = _make_screen()
        screen.scene_callback = None
        # Must not raise
        lifecycle.on_design_click(screen)


class TestOnMenuOption:
    """``on_menu_option`` routes through the screen's bound methods so that
    tests/code monkey-patching the screen still observe the call. Each
    branch is verified by inspecting the screen mock."""

    def test_save_game_dispatches(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "save_game")
        screen.on_save_game_click.assert_called_once()

    def test_load_game_dispatches(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "load_game")
        screen._show_load_game_dialog.assert_called_once()

    def test_settings_opens_settings_window(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "settings")
        screen.ui.window_manager.open_settings.assert_called_once()

    def test_controls_calls_callback(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "controls")
        screen.scene_callback.assert_called_once_with("open_keybindings")

    def test_quit_to_menu_dispatches(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "quit_to_menu")
        screen._confirm_quit_to_menu.assert_called_once()

    def test_quit_game_calls_callback(self):
        screen = _make_screen()
        lifecycle.on_menu_option(screen, "quit_game")
        screen.scene_callback.assert_called_once_with("quit_game")

    def test_unknown_option_is_noop(self):
        screen = _make_screen()
        # Must not raise; nothing called.
        lifecycle.on_menu_option(screen, "definitely_not_a_real_option")
        screen.scene_callback.assert_not_called()


class TestLoadGameDialog:
    def test_show_load_game_dialog_creates_window(self):
        screen = _make_screen()
        with patch("game.ui.screens.save_selection_window.SaveSelectionWindow") as mock_win, \
             patch("game.ui.utils.create_centered_rect", return_value="RECT"):
            lifecycle.show_load_game_dialog(screen)
            mock_win.assert_called_once()
            args, kwargs = mock_win.call_args
            assert args[0] == "RECT"
            assert kwargs["on_load_callback"] is not None
            assert kwargs["on_cancel_callback"] is not None

    def test_on_load_selected_calls_callback(self):
        screen = _make_screen()
        lifecycle.on_load_selected(screen, "/path/to/save", turn_number=7)
        screen.scene_callback.assert_called_once_with(
            "load_game", save_path="/path/to/save", turn_number=7
        )

    def test_on_load_selected_no_callback_safe(self):
        screen = _make_screen()
        screen.scene_callback = None
        lifecycle.on_load_selected(screen, "/p")  # must not raise


class TestQuitConfirmation:
    def test_confirm_quit_creates_dialog(self):
        screen = _make_screen()
        with patch("pygame_gui.windows.UIConfirmationDialog") as mock_dlg:
            mock_dlg.return_value = "DIALOG"
            lifecycle.confirm_quit_to_menu(screen)
            assert screen._quit_confirm_dialog == "DIALOG"
            mock_dlg.assert_called_once()

    def test_handle_quit_confirmed_clears_and_callbacks(self):
        screen = _make_screen()
        screen._quit_confirm_dialog = MagicMock()
        lifecycle.handle_quit_confirmed(screen)
        assert screen._quit_confirm_dialog is None
        screen.scene_callback.assert_called_once_with("quit_to_menu")


class TestComingSoon:
    def test_show_coming_soon_creates_message_window(self):
        screen = _make_screen()
        with patch("pygame_gui.windows.UIMessageWindow") as mock_win:
            lifecycle.show_coming_soon(screen, "Diplomacy")
            mock_win.assert_called_once()
            kwargs = mock_win.call_args.kwargs
            assert "Diplomacy" in kwargs["html_message"]
            assert kwargs["window_title"] == "Diplomacy"


class TestSaveGameClick:
    """PROJ-475 Phase 2 Task 2.4: manual save routes through
    ``screen.facade.session_meta.save_current_game()`` (the facade owns the
    session and calls SaveGameService internally) — the UI no longer imports
    or calls SaveGameService directly."""

    def test_save_success_shows_success_dialog(self):
        screen = _make_screen()
        screen.facade.session_meta.save_current_game.return_value = (
            True, "Saved to slot 1", "/p"
        )
        with patch("pygame_gui.windows.UIMessageWindow") as mock_win:
            lifecycle.on_save_game_click(screen)
            screen.facade.session_meta.save_current_game.assert_called_once_with()
            mock_win.assert_called_once()
            kwargs = mock_win.call_args.kwargs
            assert "Successfully" in kwargs["html_message"]
            assert kwargs["window_title"] == "Save Game"

    def test_save_failure_shows_error_dialog(self):
        screen = _make_screen()
        screen.facade.session_meta.save_current_game.return_value = (
            False, "Disk full", None
        )
        with patch("pygame_gui.windows.UIMessageWindow") as mock_win:
            lifecycle.on_save_game_click(screen)
            mock_win.assert_called_once()
            kwargs = mock_win.call_args.kwargs
            assert "Save Failed" in kwargs["html_message"]
            assert kwargs["window_title"] == "Save Game Error"
