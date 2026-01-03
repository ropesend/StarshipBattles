import unittest
import sys
import os
import math

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import Component, LayerType, load_components

class TestDynamicLayers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize with the real data files (../../data)
        initialize_ship_data(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        load_components(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'components.json')))

    def test_fighter_layers(self):
        # Fighter (Small) should have CORE and ARMOR only
        ship = Ship("Test Fighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        
        self.assertIn(LayerType.CORE, ship.layers)
        self.assertIn(LayerType.ARMOR, ship.layers)
        # Should NOT have OUTER or INNER
        self.assertNotIn(LayerType.OUTER, ship.layers)
        self.assertNotIn(LayerType.INNER, ship.layers)
        
        # Check radii
        self.assertAlmostEqual(ship.layers[LayerType.CORE]['radius_pct'], 0.877, places=3)
        self.assertEqual(ship.layers[LayerType.ARMOR]['radius_pct'], 1.0)

    def test_satellite_layers(self):
        # Satellite (Small) should have CORE, OUTER, ARMOR
        ship = Ship("Test Satellite", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")
        
        self.assertIn(LayerType.CORE, ship.layers)
        self.assertIn(LayerType.OUTER, ship.layers)
        self.assertIn(LayerType.ARMOR, ship.layers)
        self.assertNotIn(LayerType.INNER, ship.layers)

    def test_cruiser_layers(self):
        # Cruiser should have all 4
        ship = Ship("Test Cruiser", 0, 0, (255, 0, 0), ship_class="Cruiser")
        
        self.assertIn(LayerType.CORE, ship.layers)
        self.assertIn(LayerType.INNER, ship.layers)
        self.assertIn(LayerType.OUTER, ship.layers)
        self.assertIn(LayerType.ARMOR, ship.layers)

    def test_restriction_logic(self):
        # To test restrictions, we need a ship class that HAS a restriction.
        # But our current vehicleclasses.json doesn't have any explicit restriction strings added yet.
        # So we will mock one for this test instance.
        
        ship = Ship("Restricted Ship", 0, 0, (255, 0, 0), ship_class="Escort")
        # Add a fake restriction to OUTER layer
        ship.layers[LayerType.OUTER]['restrictions'].append("block_classification:Weapons")
        # Clear restrictions on CORE to ensure test isolation (since Escort now has default blocks)
        ship.layers[LayerType.CORE]['restrictions'] = []
        
        # Create a mock Weapon component
        # We can simulate a component nicely
        weapon_data = {
            "id": "test_weapon", 
            "name": "Test Weapon", 
            "type": "Weapon", 
            "mass": 10, "hp": 10, 
            # allowed_layers removed
            "allowed_vehicle_types": ["Ship"],
            "major_classification": "Weapons"
        }
        weapon = Component(weapon_data)
        
        # Try to add to OUTER (should fail)
        success = ship.add_component(weapon, LayerType.OUTER)
        self.assertFalse(success, "Should satisfy block_classification:Weapons restriction")
        
        # Try to add to CORE (should succeed if allowed)
        success = ship.add_component(weapon, LayerType.CORE)
        self.assertTrue(success, "Should allow in non-restricted layer")

if __name__ == '__main__':
    unittest.main()
