import unittest
from unittest.mock import MagicMock, patch
import pygame

from game.core.screenshot_manager import ScreenshotManager
from game.core.registry import RegistryManager

class TestScreenshotManager(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Reset singleton if possible or just re-setup
        ScreenshotManager.reset()
        self.manager = ScreenshotManager.get_instance()
        self.manager.enabled = True # Force enable for tests logic
        self.manager.base_dir = "test_screenshots"

    def tearDown(self):
        patch.stopall()
        RegistryManager.instance().clear()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.
        super().tearDown()

    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    @patch('game.core.screenshot_manager.os.path.exists')
    @patch('game.core.screenshot_manager.os.makedirs')
    def test_capture_full(self, mock_makedirs, mock_exists, mock_get_surface, mock_save):
        mock_exists.return_value = True
        mock_surface = MagicMock()
        mock_get_surface.return_value = mock_surface
        
        self.manager.capture()
        
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        self.assertEqual(saved_surface, mock_surface)
        self.assertIn("screenshot_", filepath)
        self.assertIn(".png", filepath)

    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    def test_capture_region(self, mock_get_surface, mock_save):
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
        
        self.manager.capture(region=region_rect, label="region")
        
        mock_surface.subsurface.assert_called()
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        self.assertEqual(saved_surface, mock_subsurface)
        self.assertIn("region", filepath)

    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    def test_capture_step_sequence(self, mock_get_surface, mock_save):
        mock_surface = MagicMock()
        mock_get_surface.return_value = mock_surface
        
        self.manager.capture_step("1_setup")
        
        args, _ = mock_save.call_args
        _, filepath = args
        self.assertIn("STEP_1_setup", filepath)

if __name__ == '__main__':
    unittest.main()
