import unittest
import pygame
import os
from game.simulation.entities.ship import initialize_ship_data
from game.core.registry import RegistryManager
from game.simulation.ship_theme import ShipThemeManager

class TestShipClasses(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Initialize with CWD
        cwd = os.getcwd()
        initialize_ship_data(cwd)
        self.theme_manager = ShipThemeManager.get_instance()
        # Initialize theme manager with CWD to load themes
        self.theme_manager.initialize(cwd)
        

    def test_all_classes_exist(self):
        expected_classes = [
            "Escort", "Frigate", "Destroyer", 
            "Light Cruiser", "Cruiser", "Heavy Cruiser", 
            "Battle Cruiser", "Battleship", "Dreadnought", 
            "Superdreadnaugh", "Monitor"
        ]
        
        classes = RegistryManager.instance().vehicle_classes
        self.assertTrue(len(classes) >= 11, f"Expected at least 11 classes, found {len(classes)}")
        
        for cls_name in ["Escort", "Frigate", "Destroyer", "Cruiser", "Battleship", "Dreadnought"]:
            self.assertIn(cls_name, classes, f"Class '{cls_name}' missing from vehicle_classes")
            
        # Verify a selection of mass limits in vehicle_classes
        self.assertEqual(classes["Escort"]["max_mass"], 1000)
        self.assertEqual(classes["Frigate"]["max_mass"], 2000)
        self.assertEqual(classes["Monitor"]["max_mass"], 1024000)
        


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
