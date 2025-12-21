import unittest
import pygame
import os
from ship_theme import ShipThemeManager

class TestNewThemes(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Initialize manager with base path (cwd)
        self.manager = ShipThemeManager.get_instance()
        # Create dummy display for image loading
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
        
        # Verify resources exist
        if not os.path.exists("resources/ShipThemes/Klingons/theme.json"):
            print("Klingon theme.json missing")
        if not os.path.exists("resources/ShipThemes/Romulans/theme.json"):
            print("Romulan theme.json missing")
            
        # Re-initialize to ensure new files are picked up if manager was already loaded
        # (Though in a fresh process it shouldn't matter, but good for interactive testing)
        self.manager.themes = {} 
        self.manager.loaded = False
        self.manager.initialize(os.getcwd())

    def test_klingon_theme_loads(self):
        """Verify Klingon theme loads and has images."""
        self.assertIn("Klingons", self.manager.get_available_themes())
        img = self.manager.get_image("Klingons", "Battlecruiser")
        self.assertIsNotNone(img)
        # Verify it's not the fallback (100x100)
        self.assertNotEqual(img.get_size(), (100, 100), "Should not be fallback image")
        
    def test_romulan_theme_loads(self):
        """Verify Romulan theme loads and has images."""
        self.assertIn("Romulans", self.manager.get_available_themes())
        img = self.manager.get_image("Romulans", "Battlecruiser")
        self.assertIsNotNone(img)
        # Verify it's not the fallback (100x100)
        self.assertNotEqual(img.get_size(), (100, 100), "Should not be fallback image")

if __name__ == '__main__':
    unittest.main()
