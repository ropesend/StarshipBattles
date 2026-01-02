import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import pygame

# Ensure we can import modules from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rendering import draw_ship, LAYER_COLORS, LayerType

class TestRenderingLogic(unittest.TestCase):
    def setUp(self):
        # Mock Surface
        self.mock_surface = MagicMock(spec=pygame.Surface)
        
        # Mock Camera
        self.mock_camera = MagicMock()
        self.mock_camera.width = 800
        self.mock_camera.height = 600
        self.mock_camera.zoom = 1.0
        self.mock_camera.position = pygame.math.Vector2(0, 0)
        self.mock_camera.show_overlay = False
        
        # Simple world_to_screen logic for the mock to make assertions predictable
        # We use side_effect to implement the logic
        def world_to_screen_side_effect(pos):
             # Center is (400, 300)
             center = pygame.math.Vector2(400, 300)
             # Offset
             offset = (pos - self.mock_camera.position) * self.mock_camera.zoom
             return center + offset
        
        self.mock_camera.world_to_screen.side_effect = world_to_screen_side_effect
        
        # Mock Ship
        self.mock_ship = MagicMock()
        self.mock_ship.is_alive = True
        self.mock_ship.position = pygame.math.Vector2(100, 100)
        self.mock_ship.radius = 20
        self.mock_ship.angle = 0
        self.mock_ship.ship_class = "TestClass"
        self.mock_ship.theme_id = "TestTheme"
        self.mock_ship.layers = {}
        self.mock_ship.color = (255, 255, 255)
        self.mock_ship.forward_vector.return_value = pygame.math.Vector2(1, 0)

    @patch('ship_theme.ShipThemeManager')
    @patch('rendering.pygame.draw.circle')
    def test_world_to_screen_transformation(self, mock_draw_circle, MockThemeManager):
        """Verify that draw_ship calculates the correct screen coordinates (cx, cy)."""
        # Ensure no image is drawn so we fall back to the circle which uses cx, cy
        instance = MockThemeManager.get_instance.return_value
        instance.get_image.return_value = None
        
        self.mock_camera.position = pygame.math.Vector2(0, 0)
        self.mock_camera.zoom = 1.0
        # World pos (100, 50). Center (400, 300).
        # Screen = (400+100, 300+50) = (500, 350)
        self.mock_ship.position = pygame.math.Vector2(100, 50)
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        # Verify the fallback circle was drawn at the correct coordinates
        # pygame.draw.circle(surface, color, (cx, cy), radius)
        # We expect at least one call to circle (the ship dot)
        self.assertTrue(mock_draw_circle.called)
        
        # Check the last call args
        args, _ = mock_draw_circle.call_args_list[-1]
        # args: surface, color, center, radius
        self.assertEqual(args[2], (500, 350))

    @patch('ship_theme.ShipThemeManager')
    @patch('rendering.pygame.draw.circle')
    def test_culling_logic(self, mock_draw_circle, MockThemeManager):
        """Verify that ships outside the camera's viewport are not drawn."""
        instance = MockThemeManager.get_instance.return_value
        instance.get_image.return_value = None
        
        # Position ship far outside the 800x600 view
        # (10000, 10000) -> Screen (10400, 10300)
        self.mock_ship.position = pygame.math.Vector2(10000, 10000)
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        # Should return early and not draw anything
        mock_draw_circle.assert_not_called()
        self.mock_surface.blit.assert_not_called()

    @patch('ship_theme.ShipThemeManager')
    @patch('rendering.pygame.transform.scale')
    @patch('rendering.pygame.transform.rotate')
    def test_zoom_scaling(self, mock_rotate, mock_scale, MockThemeManager):
        """Verify that calculated scaled_radius responds correctly to changes in camera.zoom."""
        # Setup Theme with image so we can check scaling calls
        instance = MockThemeManager.get_instance.return_value
        mock_img = MagicMock()
        mock_img.get_size.return_value = (100, 100)
        instance.get_image.return_value = mock_img
        
        # Metrics return same size
        instance.get_image_metrics.return_value = MagicMock(width=100, height=100)
        instance.get_manual_scale.return_value = 1.0
        
        # Base radius 50. Diameter 100.
        self.mock_ship.radius = 50
        
        # Test Zoom = 2.0
        self.mock_camera.zoom = 2.0
        # scaled_radius = 50 * 2 = 100
        # target_size = 2 * scaled_radius = 200
        # visible_size = 100
        # scale_factor = 200/100 = 2.0
        # New size = 100 * 2.0 = 200
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        mock_scale.assert_called_with(mock_img, (200, 200))
        
        # Test Zoom = 0.5
        self.mock_camera.zoom = 0.5
        # scaled_radius = 50 * 0.5 = 25
        # target_size = 2 * 25 = 50
        # scale_factor = 50/100 = 0.5
        # New size = 100 * 0.5 = 50
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        # Check the most recent call
        mock_scale.assert_called_with(mock_img, (50, 50))

    @patch('ship_theme.ShipThemeManager')
    @patch('rendering.pygame.transform.scale')
    @patch('rendering.pygame.transform.rotate')
    def test_theme_image_scaling(self, mock_rotate, mock_scale, MockThemeManager):
        """Test logic for scale_factor and division by zero prevention."""
        instance = MockThemeManager.get_instance.return_value
        mock_img = MagicMock()
        mock_img.get_size.return_value = (100, 100)
        instance.get_image.return_value = mock_img
        
        # Case 1: Visible size is 0 (should be treated as 1)
        instance.get_image_metrics.return_value = MagicMock(width=0, height=0)
        instance.get_manual_scale.return_value = 1.0
        
        self.mock_ship.radius = 50
        self.mock_camera.zoom = 1.0
        # target_size = 100
        # visible_size -> clamped to 1
        # scale_factor = 100 / 1 = 100
        # new size = 100 * 100 = 10000
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        mock_scale.assert_called_with(mock_img, (10000, 10000))
        
        # Case 2: Manual scale is applied
        instance.get_image_metrics.return_value = MagicMock(width=100, height=100)
        instance.get_manual_scale.return_value = 2.0
        
        # target_size = 100
        # visible_size = 100
        # scale_factor = (100/100) * 2.0 = 2.0
        # new size = 200
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        mock_scale.assert_called_with(mock_img, (200, 200))

    @patch('ship_theme.ShipThemeManager')
    @patch('rendering.pygame.draw.circle')
    @patch('rendering.pygame.draw.line')
    def test_overlay_logic(self, mock_draw_line, mock_draw_circle, MockThemeManager):
        """Verify that overlay circles are drawn when camera.show_overlay is True."""
        instance = MockThemeManager.get_instance.return_value
        instance.get_image.return_value = None # No image, so we focus on overlay + fallback
        
        self.mock_camera.show_overlay = True
        self.mock_ship.layers = {
            LayerType.ARMOR: {'components': []}, 
            LayerType.CORE: {'components': []}
        }
        self.mock_ship.radius = 100
        self.mock_camera.zoom = 1.0
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        # We expect calls for:
        # 1. Collision Radius (Green) (100, 255, 100)
        # 2. Armor Layer Circle
        # 3. Core Layer Circle
        # 4. Fallback ship dot
        
        colors = [call[0][1] for call in mock_draw_circle.call_args_list]
        
        # Check Collision Radius
        self.assertIn((100, 255, 100), colors)
        
        # Check Layer Colors
        self.assertIn(LAYER_COLORS[LayerType.ARMOR], colors)
        self.assertIn(LAYER_COLORS[LayerType.CORE], colors)
        
        # Test Overlay OFF
        self.mock_camera.show_overlay = False
        mock_draw_circle.reset_mock()
        
        draw_ship(self.mock_surface, self.mock_ship, self.mock_camera)
        
        colors_off = [call[0][1] for call in mock_draw_circle.call_args_list]
        self.assertNotIn((100, 255, 100), colors_off)
        self.assertNotIn(LAYER_COLORS[LayerType.ARMOR], colors_off)

if __name__ == '__main__':
    unittest.main()
