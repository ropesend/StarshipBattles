"""
BUG-15 Reproduction Test: Screenshot System Strategy Layer Support

This test validates that the screenshot system can:
1. Capture the galaxy viewport region (excluding sidebar/top bar)
2. Capture a specific sub-window surface
3. Capture the full screen including all UI layers
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame

from game.core.screenshot_manager import ScreenshotManager


class TestScreenshotStrategyLayerSupport(unittest.TestCase):
    """Tests for screenshot system integration with strategy layer."""

    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        ScreenshotManager.reset()
        self.manager = ScreenshotManager.instance()
        self.manager.enabled = True
        self.manager.base_dir = "test_screenshots"

    def tearDown(self):
        patch.stopall()

    # =========================================================================
    # Test 1: Capture Galaxy Viewport Region
    # =========================================================================
    @patch('game.core.screenshot_manager.pygame.image.save')
    @patch('game.core.screenshot_manager.pygame.display.get_surface')
    def test_capture_galaxy_viewport_region(self, mock_get_surface, mock_save):
        """
        The screenshot system should be able to capture just the galaxy viewport,
        excluding the sidebar and top bar UI elements.

        Expected: capture() with a viewport_rect region saves only that portion.
        """
        # Arrange: Mock a 1280x720 display
        mock_surface = MagicMock()
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 1280, 720)
        mock_get_surface.return_value = mock_surface

        # Mock subsurface behavior
        mock_subsurface = MagicMock()
        mock_surface.subsurface.return_value = mock_subsurface

        # Define viewport region (exclude 300px sidebar, 40px top bar)
        SIDEBAR_WIDTH = 300
        TOP_BAR_HEIGHT = 40
        viewport_rect = pygame.Rect(0, TOP_BAR_HEIGHT, 1280 - SIDEBAR_WIDTH, 720 - TOP_BAR_HEIGHT)

        # Act
        self.manager.capture(region=viewport_rect, label="galaxy_viewport")

        # Assert
        mock_surface.subsurface.assert_called()
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        self.assertEqual(saved_surface, mock_subsurface)
        self.assertIn("galaxy_viewport", filepath)

    # =========================================================================
    # Test 2: Capture Arbitrary Sub-Window Surface
    # =========================================================================
    @patch('game.core.screenshot_manager.pygame.image.save')
    def test_capture_subwindow_surface(self, mock_save):
        """
        The screenshot system should be able to capture a sub-window's surface
        directly when passed as a parameter.

        This supports capturing modal dialogs, build queue screens, etc.
        """
        # Arrange: Create a mock sub-window surface (e.g., 400x500 FleetOrdersWindow)
        subwindow_surface = MagicMock()
        subwindow_surface.get_rect.return_value = pygame.Rect(0, 0, 400, 500)

        # Act
        self.manager.capture(surface=subwindow_surface, label="fleet_orders_window")

        # Assert
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args
        self.assertEqual(saved_surface, subwindow_surface)
        self.assertIn("fleet_orders_window", filepath)

    # =========================================================================
    # Test 3: capture_strategy_layer() Method (NEW FEATURE NEEDED)
    # =========================================================================
    def test_capture_strategy_layer_method_exists(self):
        """
        The ScreenshotManager should have a capture_strategy_layer() method
        that understands how to capture the strategy scene with proper layering.

        This method should accept:
        - scene: The StrategyScene instance
        - include_ui: Whether to include UI panels (default True)
        - include_subwindows: Whether to include modal windows (default True)
        """
        # Assert the method exists
        self.assertTrue(
            hasattr(self.manager, 'capture_strategy_layer'),
            "ScreenshotManager should have a capture_strategy_layer() method"
        )

    # =========================================================================
    # Test 4: capture_strategy_layer() Captures Correct Layers
    # =========================================================================
    @patch('game.core.screenshot_manager.pygame.image.save')
    def test_capture_strategy_layer_renders_all_layers(self, mock_save):
        """
        capture_strategy_layer() should render the scene to a temporary surface
        and capture it with all requested layers.
        """
        # Skip if method doesn't exist yet (Phase 1 - this should FAIL)
        if not hasattr(self.manager, 'capture_strategy_layer'):
            self.skipTest("capture_strategy_layer() not implemented yet")

        # Arrange: Mock a StrategyScene
        mock_scene = MagicMock()
        mock_scene.screen_width = 1280
        mock_scene.screen_height = 720

        # Act
        self.manager.capture_strategy_layer(mock_scene, label="full_strategy")

        # Assert
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        _, filepath = args
        self.assertIn("full_strategy", filepath)

    # =========================================================================
    # Test 5: Viewport-Only Capture via capture_strategy_layer()
    # =========================================================================
    @patch('game.core.screenshot_manager.pygame.image.save')
    def test_capture_strategy_layer_viewport_only(self, mock_save):
        """
        capture_strategy_layer() with include_ui=False should capture only
        the galaxy viewport without sidebar/top bar UI.
        """
        # Skip if method doesn't exist yet
        if not hasattr(self.manager, 'capture_strategy_layer'):
            self.skipTest("capture_strategy_layer() not implemented yet")

        # Arrange
        mock_scene = MagicMock()
        mock_scene.screen_width = 1280
        mock_scene.screen_height = 720
        mock_scene.SIDEBAR_WIDTH = 300
        mock_scene.TOP_BAR_HEIGHT = 40

        # Act
        self.manager.capture_strategy_layer(mock_scene, include_ui=False, label="viewport_only")

        # Assert
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        saved_surface, filepath = args

        # The saved surface should be the viewport size, not full screen
        self.assertIn("viewport_only", filepath)


if __name__ == '__main__':
    unittest.main()
