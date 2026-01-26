
import unittest
from unittest.mock import MagicMock
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, COMPONENT_REGISTRY


class TestShipCaching(unittest.TestCase):
    def setUp(self):
        # Create a basic ship (Escort class auto-equips hull with 50 mass)
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))
        self.ship.recalculate_stats()
        # Get the hull mass for assertions
        self.hull_mass = sum(c.mass for c in self.ship.get_all_components())

    def test_cached_summary_empty_initially(self):
        # Note: recalculate_stats in setUp populates the cache
        # Test a fresh ship without recalculate
        fresh_ship = Ship("Fresh Ship", 0, 0, (255, 255, 255))
        self.assertEqual(fresh_ship.cached_summary, {})

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

        # Add to ship in OUTER layer (weapons go in OUTER, not HULL)
        self.ship.add_component(weapon, LayerType.OUTER)

        summary = self.ship.cached_summary
        self.assertTrue(summary)
        self.assertIn('dps', summary)
        self.assertIn('mass', summary)

        # Verify values
        self.assertEqual(summary['dps'], 10.0)  # 10 / 1.0
        self.assertEqual(summary['range'], 1000)
        # Mass = hull mass + weapon mass
        self.assertEqual(summary['mass'], self.hull_mass + 10.0)

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
        self.ship.add_component(weapon, LayerType.OUTER)

        summary = self.ship.cached_summary
        self.assertEqual(summary['dps'], 5.0)

        # Add another identical weapon
        weapon2 = Component(weapon_data)
        self.ship.add_component(weapon2, LayerType.OUTER)

        summary = self.ship.cached_summary
        self.assertEqual(summary['dps'], 10.0)
        # Mass = hull mass + 2 weapons
        self.assertEqual(summary['mass'], self.hull_mass + 20.0)

if __name__ == '__main__':
    unittest.main()
