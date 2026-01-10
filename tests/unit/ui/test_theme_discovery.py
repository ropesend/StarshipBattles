import unittest
from unittest.mock import patch
import pygame
import os
from game.simulation.ship_theme import ShipThemeManager

from game.core.constants import ASSET_DIR

class TestNewThemes(unittest.TestCase):
    def setUp(self):
        # Initialize manager with base path (cwd)
        import os
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()
        
        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
             pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        ShipThemeManager._instance = None
        self.manager = ShipThemeManager.get_instance()
        
        # Verify resources exist
        klingon_json = os.path.join(ASSET_DIR, "ShipThemes", "Klingons", "theme.json")
        romulan_json = os.path.join(ASSET_DIR, "ShipThemes", "Romulans", "theme.json")
        
        if not os.path.exists(klingon_json):
            print(f"Klingon theme.json missing at {klingon_json}")
        if not os.path.exists(romulan_json):
            print(f"Romulan theme.json missing at {romulan_json}")
            
        self.manager.initialize()
        
        # Verify resources exist
        klingon_json = os.path.join(ASSET_DIR, "ShipThemes", "Klingons", "theme.json")
        romulan_json = os.path.join(ASSET_DIR, "ShipThemes", "Romulans", "theme.json")
        
        if not os.path.exists(klingon_json):
            print(f"Klingon theme.json missing at {klingon_json}")
        if not os.path.exists(romulan_json):
            print(f"Romulan theme.json missing at {romulan_json}")
            
        # Re-initialize to ensure new files are picked up if manager was already loaded
        # (Though in a fresh process it shouldn't matter, but good for interactive testing)
        self.manager.themes = {} 
        self.manager.loaded = False
        
        # Ensure display is initialized for convert_alpha
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
            
        self.manager.initialize()
    def tearDown(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        # Clean up singleton
        ShipThemeManager._instance = None
        
        pygame.display.quit()
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()

    def test_theme_discovery(self):
        """Verify themes are discovered."""
        themes = self.manager.get_available_themes()
        self.assertTrue(len(themes) > 0, "No themes discovered!")
        self.assertIn("Klingons", themes)
        self.assertIn("Romulans", themes)

    def test_klingon_theme_loads(self):
        """Verify Klingon theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.get_image("Klingons", "Battle Cruiser")
        self.assertIsNotNone(img)
        # Verify it's not the fallback (100x100)
        self.assertNotEqual(img.get_size(), (100, 100), "Should not be fallback image")
        
    def test_romulan_theme_loads(self):
        """Verify Romulan theme loads and has images."""
        # Note: JSON key is "Battle Cruiser" with space
        img = self.manager.get_image("Romulans", "Battle Cruiser")
        self.assertIsNotNone(img)
        # Verify it's not the fallback (100x100)
        self.assertNotEqual(img.get_size(), (100, 100), "Should not be fallback image")

if __name__ == '__main__':
    unittest.main()
