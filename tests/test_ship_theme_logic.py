
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pygame
import os
import json
from ship_theme import ShipThemeManager

class TestShipThemeLogic(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for surface creation
        pygame.init()
        # Create dummy display for image loading/convert_alpha
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

        # Ensure singleton is reset before each test
        ShipThemeManager._instance = None
        self.manager = ShipThemeManager.get_instance()

    def tearDown(self):
        # Clean up singleton
        ShipThemeManager._instance = None
        pygame.quit()

    def test_singleton_handling(self):
        """Test that the singleton pattern works and enforces unique instance."""
        instance1 = ShipThemeManager.get_instance()
        instance2 = ShipThemeManager.get_instance()
        self.assertIs(instance1, instance2)
        
        # Test direct init raises exception
        with self.assertRaises(Exception) as context:
            ShipThemeManager()
        self.assertTrue("singleton" in str(context.exception))

    def test_fallback_generation(self):
        """Test that fallback image is generated with expected properties."""
        fallback = self.manager._create_fallback_image("UnknownClass")
        
        self.assertIsInstance(fallback, pygame.Surface)
        self.assertEqual(fallback.get_size(), (100, 100))

    def test_get_image_fallback_behavior(self):
        """Test get_image returns fallback when not loaded or theme missing."""
        # Not loaded yet
        img = self.manager.get_image("AnyTheme", "AnyClass")
        self.assertEqual(img.get_size(), (100, 100))

        # Pretend loaded but theme missing
        self.manager.loaded = True
        img = self.manager.get_image("NonExistentTheme", "AnyClass")
        self.assertEqual(img.get_size(), (100, 100))

    @patch('ship_theme.log_error')
    @patch('os.scandir')
    @patch('os.path.exists')
    @patch('ship_theme.json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pygame.image.load')
    def test_manual_scaling_and_loading(self, mock_load, mock_open_file, mock_json_load, mock_exists, mock_scandir, mock_log):
        """Test loading a theme with manual scaling configured."""
        
        # Setup mock file system structure
        theme_name = "ScaledTheme"
        ship_class = "BigShip"
        json_content = {
            "name": theme_name,
            "images": {
                ship_class: {
                    "file": "big_ship.png",
                    "scale": 1.5
                }
            }
        }
        
        # Mock directory entry
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_entry.name = theme_name
        mock_scandir.return_value = [mock_entry]
        
        # Mock file existence
        def side_effect(path):
            if path.endswith("ShipThemes"): return True
            if "theme.json" in path: return True
            if "big_ship.png" in path: return True
            return False
        mock_exists.side_effect = side_effect
        
        # Mock json load
        mock_json_load.return_value = json_content
        
        # Mock image loading
        dummy_surface = pygame.Surface((50, 50))
        mock_load.return_value = dummy_surface
        
        # Run initialize
        self.manager.initialize("/fake/base/path")
        
        # Verify no errors logged (e.g. convert_alpha failure)
        mock_log.assert_not_called()

        # Verify scaling
        scale = self.manager.get_manual_scale(theme_name, ship_class)
        self.assertEqual(scale, 1.5)
        
        # Verify default scaling for unknown class
        scale_default = self.manager.get_manual_scale(theme_name, "OtherShip")
        self.assertEqual(scale_default, 1.0)

    @patch('ship_theme.log_error')
    @patch('os.scandir')
    @patch('os.path.exists')
    @patch('ship_theme.json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pygame.image.load')
    def test_get_image_metrics(self, mock_load, mock_open_file, mock_json_load, mock_exists, mock_scandir, mock_log):
        """Test that bounding rect is correctly calculated and cached."""
        
        theme_name = "MetricsTheme"
        ship_class = "TestShip"
        json_content = {
            "name": theme_name,
            "images": {
                ship_class: "ship.png"
            }
        }
        
        # Mocks setup
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_scandir.return_value = [mock_entry]
        
        mock_exists.return_value = True # Simplify exists checks
        mock_json_load.return_value = json_content
        
        # Create a surface with specific transparency
        # 20x20 surface
        # Rect at (5, 5) size 10x10 is opaque
        mock_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        mock_surface.fill((0, 0, 0, 0)) # Transparent
        pygame.draw.rect(mock_surface, (255, 255, 255, 255), (5, 5, 10, 10))
        
        mock_load.return_value = mock_surface
        
        # Initialize
        self.manager.initialize("/fake/base/path")
        
        # Verify no errors logged
        mock_log.assert_not_called()
        
        # Verify metrics
        rect = self.manager.get_image_metrics(theme_name, ship_class)
        self.assertIsNotNone(rect)
        self.assertEqual(rect.x, 5)
        self.assertEqual(rect.y, 5)
        self.assertEqual(rect.width, 10)
        self.assertEqual(rect.height, 10)

    @patch('ship_theme.log_error')
    @patch('os.scandir')
    @patch('os.path.exists')
    @patch('ship_theme.json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_malformed_theme_json(self, mock_open_file, mock_json_load, mock_exists, mock_scandir, mock_log):
        """Test handling of malformed JSON in theme file."""
        
        theme_name = "BadTheme"
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = True
        mock_entry.path = f"/themes/{theme_name}"
        mock_scandir.return_value = [mock_entry]
        
        mock_exists.return_value = True
        
        # Mock json load raising error
        mock_json_load.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        
        # Initialize shouldn't crash
        try:
            self.manager.initialize("/fake/base/path")
        except Exception as e:
            self.fail(f"initialize raised exception on malformed JSON: {e}")
            
        # Verify log_error was called
        mock_log.assert_called()
        args, _ = mock_log.call_args
        self.assertIn("Failed to load theme", args[0])
