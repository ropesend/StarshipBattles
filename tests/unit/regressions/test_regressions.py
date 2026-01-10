import unittest
import pygame
import os
from game.simulation.entities import ship as ship
from game.simulation.entities.ship import Ship, load_vehicle_classes
from game.core.registry import RegistryManager
from game.simulation.ship_theme import ShipThemeManager

class TestRegressions(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Ensure we have a display for image operations if needed (though mostly headless works for surfaces)
        # ship.py might depend on initialized pygame
        pass

    def tearDown(self):
        pygame.quit()
        RegistryManager.instance().clear()

    def test_ship_classes_update_in_place(self):
        """
        Regression Test for Builder Dropdown Bug:
        Verify that load_vehicle_classes updates the RegistryManager vehicle_classes dict in-place
        instead of replacing the reference.
        """
        # Store original reference
        original_ref = RegistryManager.instance().vehicle_classes
        original_id = id(original_ref)
        
        # Call loader
        ship.load_vehicle_classes()
        
        # Verify reference is identical
        self.assertEqual(id(RegistryManager.instance().vehicle_classes), original_id, 
                         "vehicle_classes reference changed! Imports in other modules will be stale.")
        self.assertIs(RegistryManager.instance().vehicle_classes, original_ref)
        
        # Verify it has content
        self.assertTrue(len(RegistryManager.instance().vehicle_classes) > 0, "vehicle_classes should not be empty")

    def test_theme_fallback_image(self):
        """
        Regression Test for Crash on Missing Image:
        Verify that getting an image for a non-existent theme or class returns a valid fallback surface.
        """
        manager = ShipThemeManager.get_instance()
        # Force reload to ensure clean state if needed, but singleton persists.
        # Just use it.
        
        # 1. Test invalid theme -> Should fallback to Default (Federation) if Escort exists
        img = manager.get_image("NonExistentTheme", "Escort")
        self.assertIsInstance(img, pygame.Surface)
        # If Federation/Escort exists, it won't be 100x100. 
        # But we know "NonExistentClass" shouldn't exist in any theme.
        
        # 2. Test valid theme, invalid class -> Should be fallback 100x100
        img2 = manager.get_image("Federation", "NonExistentClass")
        self.assertIsInstance(img2, pygame.Surface)
        self.assertEqual(img2.get_width(), 100)
        
        # 3. Test invalid theme AND invalid class -> Should be fallback 100x100
        img3 = manager.get_image("NonExistentTheme", "NonExistentClass")
        self.assertIsInstance(img3, pygame.Surface)
        self.assertEqual(img3.get_width(), 100)

    def test_ship_theme_persistence(self):
        """
        Regression Test for Theme Not Saving:
        Verify theme_id is saved and loaded correctly.
        """
        s = Ship("TestShip", 0, 0, (255,0,0), theme_id="Atlantians")
        
        data = s.to_dict()
        self.assertEqual(data.get('theme_id'), "Atlantians")
        
        s2 = Ship.from_dict(data)
        self.assertEqual(s2.theme_id, "Atlantians")
        
        # Test Default
        s_def = Ship("DefShip", 0, 0, (255,0,0)) # defaults to Federation
        data_def = s_def.to_dict()
        self.assertEqual(data_def.get('theme_id'), "Federation")

if __name__ == '__main__':
    unittest.main()
