import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.core.screenshot_manager import ScreenshotManager
from game.core.registry import RegistryManager


@pytest.fixture
def screenshot_manager():
    """Set up and tear down the ScreenshotManager for each test."""
    if not pygame.get_init():
        pygame.init()
    # Reset singleton if possible or just re-setup
    ScreenshotManager.reset()
    manager = ScreenshotManager.get_instance()
    manager.enabled = True  # Force enable for tests logic
    manager.base_dir = "test_screenshots"

    yield manager

    patch.stopall()
    RegistryManager.instance().clear()
    # NOTE: Do not call pygame.quit() here - the root conftest manages
    # pygame lifecycle at session scope. Calling quit() here would break
    # subsequent tests with "No video mode set" errors.


class TestScreenshotManager:
    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    @patch('game.core.screenshot_manager.os.path.exists')
    @patch('game.core.screenshot_manager.os.makedirs')
    def test_capture_full(self, mock_makedirs, mock_exists, mock_get_surface, mock_save, screenshot_manager):
        mock_exists.return_value = True
        mock_surface = MagicMock()
        mock_get_surface.return_value = mock_surface

        screenshot_manager.capture()

        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        assert saved_surface == mock_surface
        assert "screenshot_" in filepath
        assert ".png" in filepath

    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    def test_capture_region(self, mock_get_surface, mock_save, screenshot_manager):
        mock_surface = MagicMock()
        mock_rect = MagicMock()
        mock_surface.get_rect.return_value = mock_rect
        mock_get_surface.return_value = mock_surface

        # Mock subsurface behavior
        mock_subsurface = MagicMock()
        mock_surface.subsurface.return_value = mock_subsurface

        # Region rect
        region_rect = MagicMock()
        region_rect.clip.return_value = region_rect
        region_rect.width = 100
        region_rect.height = 100

        screenshot_manager.capture(region=region_rect, label="region")

        mock_surface.subsurface.assert_called()
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        assert saved_surface == mock_subsurface
        assert "region" in filepath

    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    def test_capture_step_sequence(self, mock_get_surface, mock_save, screenshot_manager):
        mock_surface = MagicMock()
        mock_get_surface.return_value = mock_surface

        screenshot_manager.capture_step("1_setup")

        args, _ = mock_save.call_args
        _, filepath = args
        assert "STEP_1_setup" in filepath
