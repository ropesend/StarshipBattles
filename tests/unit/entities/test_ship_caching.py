import unittest
from unittest.mock import MagicMock
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.registry import RegistryManager
# Assuming registry is populated or we mock it. 
# Better to mock components or use a minimal test case without full registry dependency if possible.

class TestShipCaching(unittest.TestCase):
    def setUp(self):
        # Create a basic ship
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))
        
    def test_cached_summary_empty_initially(self):
        self.assertEqual(self.ship.cached_summary, {})

    def test_cached_summary_populated_after_calc(self):
        # Create a mock weapon component
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 1.0, "range": 1000}
            }
        }
        weapon = Component(weapon_data)
        
        # Add to ship
        # This triggers recalculate_stats -> calculate -> populate cache
        self.ship.add_component(weapon, self.ship.layers.keys().__iter__().__next__()) # Add to first available layer (CORE)
        
        summary = self.ship.cached_summary
        self.assertTrue(summary)
        self.assertIn('dps', summary)
        self.assertIn('mass', summary)
        
        # Verify values
        self.assertEqual(summary['dps'], 10.0) # 10 / 1.0
        self.assertEqual(summary['range'], 1000)
        # Mass: Hull component (50 for Escort) + weapon component (10) = 60
        self.assertEqual(summary['mass'], 60.0)
        
    def test_cached_summary_updates(self):
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 2.0, "range": 500}
            }
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, self.ship.layers.keys().__iter__().__next__())
        
        summary = self.ship.cached_summary
        self.assertEqual(summary['dps'], 5.0)
        
        # Add another identical weapon
        weapon2 = Component(weapon_data)
        self.ship.add_component(weapon2, self.ship.layers.keys().__iter__().__next__())
        
        summary = self.ship.cached_summary
        self.assertEqual(summary['dps'], 10.0)
        # Mass: Hull component (50) + 2 weapons (10 + 10) = 70
        self.assertEqual(summary['mass'], 70.0)

if __name__ == '__main__':
    unittest.main()
