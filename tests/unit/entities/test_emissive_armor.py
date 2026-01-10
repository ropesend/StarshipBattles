from game.simulation.components.component import Component
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_combat import ShipCombatMixin
import unittest

class TestEmissiveArmor(unittest.TestCase):
    def setUp(self):
        # Create a dummy ship
        self.ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Escort")
        # Create an Emissive Armor component
        # We need to mock the component definition since we haven't loaded json yet in this test context,
        # or we rely on the registry. simpler to mock.
        
        # Manually constructing a component with the ability
        self.armor_data = {
            "id": "emissive_armor",
            "name": "Emissive Armor",
            "type": "Armor",
            "mass": "=40 * (ship_class_mass / 1000)",
            "hp": 200,
            "hp_formula": "=200 * (ship_class_mass / 1000)**(1/3)",
            "allowed_layers": ["ARMOR"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": {
                "Armor": True,
                "EmissiveArmor": { "value": "=15 * (ship_class_mass / 1000)**(1/3)", "stack_group": "Emissive" }
            }
        }
        # Register it so it can be cloned if needed, or just use it directly
        from game.core.registry import RegistryManager
        from game.simulation.components.component import Component
        
        # Ensure ship has mass budget for formula eval when added
        self.ship.max_mass_budget = 1000
        
        c = Component(self.armor_data)
        RegistryManager.instance().components["emissive_armor"] = c
        
        # Add to ship
        self.emissive_comp = c.clone()
        if LayerType.ARMOR not in self.ship.layers:
             self.ship.layers[LayerType.ARMOR] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}

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
        
        # Total reduction should still be 15 (MAX of 15, 15)
        initial_hp = self.ship.hp
        
        # Damage 10 < 15 -> Ignored
        self.ship.take_damage(10)
        self.assertEqual(self.ship.hp, initial_hp, "Damage 10 < 15 should be ignored")
        
        # Damage 25 > 15 -> Take 10
        self.ship.take_damage(25)
        self.assertEqual(self.ship.hp, initial_hp - 10, "Damage 25 > 15 should take 10")

if __name__ == '__main__':
    unittest.main()
