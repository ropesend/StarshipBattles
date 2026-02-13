"""
Unit tests for game/ui/services/screenshot_manager.py

Tests singleton behavior, capture functionality, and clipboard operations.
All tests mock pygame and filesystem operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import os


class TestScreenshotManagerSingleton:
    """Tests for ScreenshotManager singleton behavior."""

    def test_instance_returns_same_object(self):
        """Two calls return same instance."""
        # Need to reset before test to ensure clean state
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.core.singleton import SingletonMeta

        # Clear any existing instance
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                instance1 = ScreenshotManager.instance()
                instance2 = ScreenshotManager.instance()

        assert instance1 is instance2

        # Cleanup
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

    def test_reset_allows_new_instance(self):
        """After reset(), instance() creates new object."""
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.core.singleton import SingletonMeta

        # Clear any existing instance
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                instance1 = ScreenshotManager.instance()

                # Reset by removing from SingletonMeta
                if ScreenshotManager in SingletonMeta._instances:
                    del SingletonMeta._instances[ScreenshotManager]

                instance2 = ScreenshotManager.instance()

        assert instance1 is not instance2

        # Cleanup
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]


class TestScreenshotCapture:
    """Tests for capture functionality (mocked)."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock-patched ScreenshotManager."""
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.core.singleton import SingletonMeta

        # Clear any existing instance
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                manager = ScreenshotManager.instance()

        yield manager

        # Cleanup
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

    def test_capture_disabled_does_nothing(self, mock_manager):
        """No file ops when enabled=False."""
        mock_manager.enabled = False
        mock_surface = Mock()

        with patch('game.ui.services.screenshot_manager.pygame') as mock_pygame:
            mock_manager.capture(surface=mock_surface)

        # pygame.image.save should not be called
        mock_pygame.image.save.assert_not_called()

    def test_capture_no_surface_logs_warning(self, mock_manager):
        """Logs warning when surface is None."""
        mock_manager.enabled = True

        with patch('game.ui.services.screenshot_manager.pygame') as mock_pygame:
            mock_pygame.display.get_surface.return_value = None
            with patch('game.ui.services.screenshot_manager.log_warning') as mock_log:
                mock_manager.capture(surface=None)

        mock_log.assert_called()

    def test_capture_with_label_includes_label(self, mock_manager):
        """Filename contains label."""
        mock_manager.enabled = True
        mock_surface = Mock()
        mock_surface.get_rect.return_value = Mock(width=100, height=100)

        with patch('game.ui.services.screenshot_manager.pygame') as mock_pygame:
            with patch('game.ui.services.screenshot_manager.log_info'):
                with patch.object(mock_manager, '_copy_to_clipboard'):
                    mock_manager.capture(surface=mock_surface, label="test_label")

        # Check that save was called with a path containing the label
        save_call = mock_pygame.image.save.call_args
        assert save_call is not None
        filepath = save_call[0][1]
        assert "test_label" in filepath

    def test_capture_region_clips_to_surface(self, mock_manager):
        """Region clipped to surface bounds."""
        mock_manager.enabled = True

        mock_surface = Mock()
        surf_rect = Mock()
        surf_rect.width = 100
        surf_rect.height = 100
        mock_surface.get_rect.return_value = surf_rect

        # Create a region that extends beyond surface
        import pygame
        region = Mock()
        region.clip.return_value = Mock(width=50, height=50)

        mock_sub = Mock()
        mock_surface.subsurface.return_value = mock_sub

        with patch('game.ui.services.screenshot_manager.pygame') as mock_pygame:
            with patch('game.ui.services.screenshot_manager.log_info'):
                with patch.object(mock_manager, '_copy_to_clipboard'):
                    mock_manager.capture(surface=mock_surface, region=region)

        # Should have used subsurface
        mock_surface.subsurface.assert_called()

    def test_capture_region_outside_surface_logs_warning(self, mock_manager):
        """Zero-size clip logs warning."""
        mock_manager.enabled = True

        mock_surface = Mock()
        surf_rect = Mock()
        mock_surface.get_rect.return_value = surf_rect

        # Region that clips to zero size
        region = Mock()
        region.clip.return_value = Mock(width=0, height=0)

        with patch('game.ui.services.screenshot_manager.pygame'):
            with patch('game.ui.services.screenshot_manager.log_warning') as mock_log:
                mock_manager.capture(surface=mock_surface, region=region)

        mock_log.assert_called()

    def test_capture_io_error_handled(self, mock_manager):
        """IOError caught, no crash."""
        import pygame as real_pygame
        mock_manager.enabled = True
        mock_surface = Mock()
        mock_surface.get_rect.return_value = Mock(width=100, height=100)

        with patch('game.ui.services.screenshot_manager.pygame.image.save', side_effect=IOError("test error")):
            with patch('game.ui.services.screenshot_manager.log_error') as mock_log:
                # Should not raise
                mock_manager.capture(surface=mock_surface)

        mock_log.assert_called()


class TestClipboardOperations:
    """Tests for clipboard operations (mocked)."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock-patched ScreenshotManager."""
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.core.singleton import SingletonMeta

        # Clear any existing instance
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

        with patch('game.ui.services.screenshot_manager.os.path.exists', return_value=True):
            with patch('game.ui.services.screenshot_manager.os.makedirs'):
                manager = ScreenshotManager.instance()

        yield manager

        # Cleanup
        if ScreenshotManager in SingletonMeta._instances:
            del SingletonMeta._instances[ScreenshotManager]

    def test_clipboard_tkinter_success(self, mock_manager):
        """Tkinter path works without error."""
        mock_tk = Mock()
        mock_tk_class = Mock(return_value=mock_tk)

        with patch.dict('sys.modules', {'tkinter': Mock(Tk=mock_tk_class)}):
            import importlib
            # Call clipboard method
            mock_manager._copy_to_clipboard("/path/to/file.png")

        # Tkinter methods should have been called
        mock_tk.withdraw.assert_called()
        mock_tk.clipboard_clear.assert_called()

    def test_clipboard_tkinter_failure_falls_back(self, mock_manager):
        """On Tkinter error, tries clip on Windows."""
        with patch('game.ui.services.screenshot_manager.os.name', 'nt'):
            with patch('game.ui.services.screenshot_manager.subprocess.run') as mock_run:
                # Make tkinter import fail by having it raise an exception
                with patch.dict('sys.modules', {'tkinter': None}):
                    # Simulate tkinter failure
                    def raise_error():
                        raise ImportError("No tkinter")

                    with patch('builtins.__import__', side_effect=ImportError):
                        mock_manager._copy_to_clipboard("/path/to/file.png")

    def test_clipboard_windows_fallback(self, mock_manager):
        """subprocess.run with clip called on Windows when tkinter fails."""
        # This test verifies that when tkinter fails and we're on Windows,
        # the code attempts to use the clip command
        with patch('game.ui.services.screenshot_manager.os.name', 'nt'):
            with patch('game.ui.services.screenshot_manager.subprocess.run') as mock_run:
                # Create a mock tkinter that raises on use
                mock_tkinter = Mock()
                mock_tk_instance = Mock()
                mock_tk_instance.clipboard_clear.side_effect = Exception("tkinter error")
                mock_tkinter.Tk.return_value = mock_tk_instance

                with patch.dict('sys.modules', {'tkinter': mock_tkinter}):
                    mock_manager._copy_to_clipboard("/path/to/file.png")

                # Should have called subprocess.run with clip
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == ['clip']
