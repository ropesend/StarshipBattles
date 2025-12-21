import unittest
import pygame
import os
from ship import initialize_ship_data, SHIP_CLASSES, VEHICLE_CLASSES
from ship_theme import ShipThemeManager

class TestShipClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Initialize with CWD
        cwd = os.getcwd()
        initialize_ship_data(cwd)
        cls.theme_manager = ShipThemeManager.get_instance()
        # Initialize theme manager with CWD to load themes
        cls.theme_manager.initialize(cwd)
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_all_classes_exist(self):
        expected_classes = [
            "Escort", "Frigate", "Destroyer", 
            "Light Cruiser", "Cruiser", "Heavy Cruiser", 
            "Battle Cruiser", "Battleship", "Dreadnought", 
            "Superdreadnaugh", "Monitor"
        ]
        
        self.assertTrue(len(VEHICLE_CLASSES) >= 11, f"Expected at least 11 classes, found {len(VEHICLE_CLASSES)}")
        
        for cls_name in expected_classes:
            self.assertIn(cls_name, VEHICLE_CLASSES, f"Class '{cls_name}' missing from VEHICLE_CLASSES")
            
    def test_mass_limits(self):
        # Verify a selection of mass limits in VEHICLE_CLASSES
        self.assertEqual(VEHICLE_CLASSES["Escort"]["max_mass"], 1000)
        self.assertEqual(VEHICLE_CLASSES["Frigate"]["max_mass"], 2000)
        self.assertEqual(VEHICLE_CLASSES["Monitor"]["max_mass"], 1024000)
        
        # Verify SHIP_CLASSES legacy mapping
        self.assertEqual(SHIP_CLASSES["Escort"], 1000)

    def test_theme_image_loading(self):
        themes = ["Federation", "Atlantians", "Klingons", "Romulans"]
        classes = [
            "Escort", "Frigate", "Destroyer", 
            "Light Cruiser", "Cruiser", "Heavy Cruiser", 
            "Battle Cruiser", "Battleship", "Dreadnought", 
            "Superdreadnaugh", "Monitor"
        ]
        
        for theme in themes:
            for ship_class in classes:
                # Get image directly
                img = self.theme_manager.get_image(theme, ship_class)
                
                self.assertIsNotNone(img, f"Failed to load image for {theme} / {ship_class}")
                self.assertIsInstance(img, pygame.Surface)
