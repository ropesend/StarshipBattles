"""Tests for PlanetListWindow and ScreenshotManager toast functionality (ERR-022).

DUP-UI1-001: Toast functionality moved to ScreenshotManager.show_toast.
These tests now verify the consolidated implementation.
"""
import pytest
import pygame
import logging
from unittest.mock import MagicMock, patch


class TestScreenshotToastErrorLogging:
    """Tests for error logging in ScreenshotManager.show_toast (ERR-022, DUP-UI1-001)."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_screenshot_toast_failure_logs_warning(self, caplog):
        """Screenshot toast failure should log warning (ERR-022)."""
        import game.ui.services.screenshot_manager as ssm_module
        from game.ui.services.screenshot_manager import ScreenshotManager, get_default_screenshot_manager

        # Clear to ensure fresh state
        ssm_module._default_screenshot_manager = None

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                manager = get_default_screenshot_manager()

        mock_ui_manager = MagicMock()

        # Mock UIMessageWindow to raise an exception
        with patch('pygame_gui.windows.UIMessageWindow',
                   side_effect=Exception("Test toast error")):
            with caplog.at_level(logging.WARNING):
                # Call the method that creates the toast
                manager.show_toast(mock_ui_manager, screen_width=800)

            # Should have logged a warning about the failure
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when screenshot toast fails"
            warning_text = ' '.join(r.message for r in warning_logs)
            assert 'screenshot' in warning_text.lower() or 'toast' in warning_text.lower(), \
                f"Warning should mention screenshot/toast. Got: {warning_text}"

        # Cleanup
        ssm_module._default_screenshot_manager = None

    def test_screenshot_toast_success_no_warning(self, caplog):
        """Successful screenshot toast should not produce warnings."""
        import game.ui.services.screenshot_manager as ssm_module
        from game.ui.services.screenshot_manager import ScreenshotManager, get_default_screenshot_manager

        # Clear to ensure fresh state
        ssm_module._default_screenshot_manager = None

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                manager = get_default_screenshot_manager()

        mock_ui_manager = MagicMock()

        # Mock UIMessageWindow to succeed
        with patch('pygame_gui.windows.UIMessageWindow',
                   return_value=MagicMock()):
            with patch('game.ui.config.UIConfig') as mock_config:
                mock_config.TOAST_WIDTH = 300
                mock_config.TOAST_HEIGHT = 80
                with caplog.at_level(logging.WARNING):
                    manager.show_toast(mock_ui_manager, screen_width=800)

                # Should NOT log warnings for successful toast
                toast_warnings = [r for r in caplog.records
                                 if 'screenshot' in r.message.lower() or 'toast' in r.message.lower()]
                assert len(toast_warnings) == 0, "Successful toast should not log warning"

        # Cleanup
        ssm_module._default_screenshot_manager = None
