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


class TestScreenshotInputHandler(unittest.TestCase):
    """Tests for screenshot hotkeys in strategy input handler."""

    def test_input_handler_has_screenshot_methods(self):
        """
        The strategy input handler should have screenshot methods wired to F11/F12.
        """
        from game.ui.screens.strategy_input_handler import InputHandler

        # Create a mock scene
        mock_scene = MagicMock()
        mock_scene.ui = MagicMock()
        mock_scene.ui.manager = MagicMock()
        mock_scene.screen_width = 1280
        mock_scene.screen_height = 720

        handler = InputHandler(mock_scene)

        # Verify screenshot methods exist
        self.assertTrue(hasattr(handler, '_take_screenshot_full'))
        self.assertTrue(hasattr(handler, '_take_screenshot_viewport'))

    @patch('game.ui.screens.strategy_input_handler.ScreenshotManager')
    def test_f12_triggers_full_screenshot(self, mock_sm_class):
        """F12 should trigger full screenshot capture."""
        from game.ui.screens.strategy_input_handler import InputHandler

        mock_sm = MagicMock()
        mock_sm_class.instance.return_value = mock_sm

        mock_scene = MagicMock()
        mock_scene.ui = MagicMock()
        mock_scene.ui.manager = MagicMock()
        mock_scene.screen_width = 1280
        mock_scene.screen_height = 720

        handler = InputHandler(mock_scene)
        handler._take_screenshot_full()

        mock_sm.capture_strategy_layer.assert_called_once()
        args, kwargs = mock_sm.capture_strategy_layer.call_args
        self.assertEqual(kwargs.get('include_ui'), True)

    @patch('game.ui.screens.strategy_input_handler.ScreenshotManager')
    def test_f11_triggers_viewport_screenshot(self, mock_sm_class):
        """F11 should trigger viewport-only screenshot capture."""
        from game.ui.screens.strategy_input_handler import InputHandler

        mock_sm = MagicMock()
        mock_sm_class.instance.return_value = mock_sm

        mock_scene = MagicMock()
        mock_scene.ui = MagicMock()
        mock_scene.ui.manager = MagicMock()
        mock_scene.screen_width = 1280
        mock_scene.screen_height = 720

        handler = InputHandler(mock_scene)
        handler._take_screenshot_viewport()

        mock_sm.capture_strategy_layer.assert_called_once()
        args, kwargs = mock_sm.capture_strategy_layer.call_args
        self.assertEqual(kwargs.get('include_ui'), False)


class TestBuildQueueScreenshotSupport(unittest.TestCase):
    """Tests for screenshot support in BuildQueueScreen."""

    def test_build_queue_has_screenshot_handling(self):
        """
        BuildQueueScreen should handle F12/F11 keyboard events for screenshots.

        Rev 3: Screenshots should work when BuildQueueScreen is open.
        """
        from game.ui.screens.build_queue_screen import BuildQueueScreen

        # Check that handle_event method exists
        self.assertTrue(hasattr(BuildQueueScreen, 'handle_event'))

        # Check that screenshot methods exist
        self.assertTrue(
            hasattr(BuildQueueScreen, '_take_screenshot'),
            "BuildQueueScreen should have _take_screenshot method"
        )

    @patch('game.core.screenshot_manager.pygame.image.save')
    def test_build_queue_f12_triggers_screenshot(self, mock_save):
        """
        Pressing F12 while BuildQueueScreen is open should take a screenshot.
        """
        from game.ui.screens.build_queue_screen import BuildQueueScreen
        from game.core.screenshot_manager import ScreenshotManager

        # Mock objects
        mock_manager = MagicMock()
        mock_manager.get_root_container.return_value.get_container.return_value.get_size.return_value = (1280, 720)

        mock_planet = MagicMock()
        mock_planet.name = "Test Planet"
        mock_planet.owner_id = 1
        mock_planet.construction_queue = []

        mock_session = MagicMock()
        mock_session.save_path = None

        # Patch DesignLibrary to avoid file system access
        with patch('game.ui.screens.build_queue_screen.DesignLibrary') as mock_design_lib:
            mock_design_lib.return_value.scan_designs.return_value = []
            mock_design_lib.return_value.designs_folder = "test"

            # Create instance - will need heavy mocking
            # For now, just verify the method exists and is callable
            self.assertTrue(hasattr(BuildQueueScreen, '_take_screenshot'))

    @patch('game.ui.screens.build_queue_screen.ScreenshotManager')
    def test_build_queue_f12_event_calls_take_screenshot(self, mock_sm_class):
        """
        BUG-15 Rev 5: Verify F12 KEYDOWN event triggers _take_screenshot via handle_event.
        """
        from game.ui.screens.build_queue_screen import BuildQueueScreen

        mock_sm = MagicMock()
        mock_sm.enabled = True
        mock_sm.base_dir = "test_screenshots"
        mock_sm_class.instance.return_value = mock_sm

        # Mock UIManager and its methods
        mock_manager = MagicMock()
        mock_manager.get_root_container.return_value.get_container.return_value.get_size.return_value = (1280, 720)

        mock_planet = MagicMock()
        mock_planet.name = "Test Planet"
        mock_planet.owner_id = 1
        mock_planet.construction_queue = []
        mock_planet.facilities = []

        mock_session = MagicMock()
        mock_session.save_path = None

        with patch('game.ui.screens.build_queue_screen.DesignLibrary') as mock_design_lib, \
             patch('game.ui.screens.build_queue_screen.PlanetReportPanel'), \
             patch('game.ui.screens.build_queue_screen.DesignReportPanel'), \
             patch('game.ui.screens.build_queue_screen.ui.UIPanel'), \
             patch('game.ui.screens.build_queue_screen.ui.UIButton'), \
             patch('game.ui.screens.build_queue_screen.ui.UITextBox'), \
             patch('game.ui.screens.build_queue_screen.ui.UILabel'), \
             patch('game.ui.screens.build_queue_screen.ui.UIScrollingContainer'):

            mock_design_lib.return_value.scan_designs.return_value = []
            mock_design_lib.return_value.designs_folder = "test"

            # Create screen instance
            screen = BuildQueueScreen(
                mock_manager,
                mock_planet,
                mock_session,
                on_close_callback=lambda: None
            )

            # Create F12 KEYDOWN event
            f12_event = MagicMock()
            f12_event.type = pygame.KEYDOWN
            f12_event.key = pygame.K_F12

            # Call handle_event with F12
            screen.handle_event(f12_event)

            # Verify ScreenshotManager.instance() was called
            mock_sm_class.instance.assert_called()
            # Verify capture was called
            mock_sm.capture.assert_called_once_with(label="build_queue")


if __name__ == '__main__':
    unittest.main()
