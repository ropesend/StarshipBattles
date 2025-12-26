
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import Component
from ship import Ship, LayerType
from ship_combat import ShipCombatMixin
import unittest

class TestEmissiveArmor(unittest.TestCase):
    def setUp(self):
        # Create a dummy ship
        self.ship = Ship("Test Ship", 0, 0, (255, 0, 0))
        # Create an Emissive Armor component
        # We need to mock the component definition since we haven't loaded json yet in this test context,
        # or we rely on the registry. simpler to mock.
        
        # Manually constructing a component with the ability
        self.armor_data = {
            "id": "emissive_armor",
            "name": "Emissive Armor",
            "type": "Armor",
            "mass": 10,
            "hp": 50,
            "allowed_layers": ["ARMOR"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": {
                "Armor": True,
                "EmissiveArmor": 15
            }
        }
        # Register it so it can be cloned if needed, or just use it directly
        from components import COMPONENT_REGISTRY, Component
        c = Component(self.armor_data)
        COMPONENT_REGISTRY["emissive_armor"] = c
        
        # Add to ship
        self.emissive_comp = c.clone()
        if LayerType.ARMOR not in self.ship.layers:
             self.ship.layers[LayerType.ARMOR] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100}

        self.ship.layers[LayerType.ARMOR]['components'].append(self.emissive_comp)
        self.ship.recalculate_stats()

    def test_damage_reduction_below_threshold(self):
        # Damage 10 < 15
        initial_hp = self.ship.hp
        self.ship.take_damage(10)
        self.assertEqual(self.ship.hp, initial_hp, "Damage should be completely ignored")

    def test_damage_reduction_above_threshold(self):
        # Damage 20 > 15. Should take 5 damage.
        initial_hp = self.ship.hp
        self.ship.take_damage(20)
        expected_hp = initial_hp - 5
        self.assertEqual(self.ship.hp, expected_hp, "Damage should be reduced by 15")

    def test_multiple_emissive_armor(self):
        # Add another plate
        comp2 = self.emissive_comp.clone()
        self.ship.layers[LayerType.ARMOR]['components'].append(comp2)
        self.ship.recalculate_stats()
        
        # Total reduction should be 30
        initial_hp = self.ship.hp
        self.ship.take_damage(25)
        self.assertEqual(self.ship.hp, initial_hp, "Damage 25 < 30 should be ignored")
        
        self.ship.take_damage(35)
        self.assertEqual(self.ship.hp, initial_hp - 5, "Damage 35 > 30 should take 5")

if __name__ == '__main__':
    unittest.main()
