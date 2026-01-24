"""Tests for PlanetListWindow error logging (ERR-022)."""
import pytest
import pygame
import logging
from unittest.mock import MagicMock, patch


class TestPlanetListWindowErrorLogging:
    """Tests for error logging in PlanetListWindow (ERR-022)."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_screenshot_toast_failure_logs_warning(self, caplog):
        """Screenshot toast failure should log warning (ERR-022)."""
        from game.ui.screens.planet_list_window import PlanetListWindow

        # Create mock window with required attributes
        window = MagicMock(spec=PlanetListWindow)
        # Override the method we're testing with the real implementation
        window._show_screenshot_toast = lambda: PlanetListWindow._show_screenshot_toast(window)

        # Mock UIMessageWindow to raise an exception
        with patch('game.ui.screens.planet_list_window.pygame_gui.windows.UIMessageWindow',
                   side_effect=Exception("Test toast error")):
            with caplog.at_level(logging.WARNING):
                # Call the method that creates the toast
                window._show_screenshot_toast()

            # Should have logged a warning about the failure
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when screenshot toast fails"
            warning_text = ' '.join(r.message for r in warning_logs)
            assert 'screenshot' in warning_text.lower() or 'toast' in warning_text.lower(), \
                f"Warning should mention screenshot/toast. Got: {warning_text}"

    def test_screenshot_toast_success_no_warning(self, caplog):
        """Successful screenshot toast should not produce warnings."""
        from game.ui.screens.planet_list_window import PlanetListWindow

        # Create mock window with all required attributes (no spec, to allow full attribute access)
        window = MagicMock()
        window.rect.width = 800
        window.ui_manager = MagicMock()
        window._show_screenshot_toast = lambda: PlanetListWindow._show_screenshot_toast(window)

        # Mock UIMessageWindow to succeed
        with patch('game.ui.screens.planet_list_window.pygame_gui.windows.UIMessageWindow',
                   return_value=MagicMock()):
            with caplog.at_level(logging.WARNING):
                window._show_screenshot_toast()

            # Should NOT log warnings for successful toast
            toast_warnings = [r for r in caplog.records
                             if 'screenshot' in r.message.lower() or 'toast' in r.message.lower()]
            assert len(toast_warnings) == 0, "Successful toast should not log warning"
