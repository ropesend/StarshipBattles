
import sys
import os
import unittest
from unittest.mock import MagicMock

# Use real pygame instead of mocking it - mocking at module level pollutes other tests
import pygame
pygame.init()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import Component
from ship import Ship, LayerType, initialize_ship_data
from ship_combat import ShipCombatMixin

class TestCrystallineArmor(unittest.TestCase):
    def setUp(self):
        # Initialize ship data (VEHICLE_CLASSES, etc.)
        initialize_ship_data()
        
        # Create a dummy ship (use Cruiser for sufficient layers)
        self.ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Cruiser")
        
        # Define Crystalline Armor Data
        self.armor_data = {
            "id": "crystalline_armor",
            "name": "Crystalline Armor",
            "type": "Armor",
            "mass": "=40 * (ship_class_mass / 1000)",
            "hp": 200,
            "hp_formula": "=200 * (ship_class_mass / 1000)**(1/3)",
            "allowed_layers": ["ARMOR"],
            "allowed_vehicle_types": ["Ship"],
            "abilities": {
                "Armor": True,
                "CrystallineArmor": { 
                    "value": 10,  # Fixed value for testing simplicity
                    "stack_group": "Crystalline" 
                }
            }
        }
        
        # Mock Registry
        from components import COMPONENT_REGISTRY, Component
        self.ship.max_mass_budget = 1000
        
        c = Component(self.armor_data)
        COMPONENT_REGISTRY["crystalline_armor"] = c
        
        # Add Armor Layer
        if LayerType.ARMOR not in self.ship.layers:
             self.ship.layers[LayerType.ARMOR] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}

        # Be "Alive"
        self.ship.is_alive = True
        
        # Give shields for regen testing
        self.ship.max_shields = 100
        self.ship.current_shields = 50
        
        # Ensure we have some HP so we don't die instantly (Armor provides HP)
        # add_armor() will add components.

    def add_armor(self):
        print("DEBUG: Adding armor...")
        from components import COMPONENT_REGISTRY
        c = COMPONENT_REGISTRY["crystalline_armor"].clone()
        self.ship.layers[LayerType.ARMOR]['components'].append(c)
        
        # Also need a shield generator so max_shields > 0
        shield_data = {
            "id": "test_shield",
            "name": "Test Shield",
            "type": "Shield",
            "mass": 10,
            "hp": 50,
            "sprite_index": 0,
            "abilities": { "ShieldProjection": 100 }
        }
        # Create ad-hoc component instance (cannot use registry if not registered)
        from components import Component
        s_comp = Component(shield_data)
        self.ship.layers[LayerType.ARMOR]['components'].append(s_comp)
        
        self.ship.recalculate_stats()
        # Reset shields for predictable testing (recalculate_stats overwrites these)
        self.ship.max_shields = 100
        self.ship.current_shields = 50
        return c

    def test_damage_absorption_and_regen(self):
        self.add_armor()
        initial_hp = self.ship.hp  # Save initial HP after setup
        # Armor Value = 10
        # Shields = 50
        
        # Incoming Damage 20
        # - 10 Absorbed by Crystalline
        # - Net Damage = 10
        # - Shields + 10 = 60
        # - Shields take 10 damage -> 50
        
        self.ship.take_damage(20)
        
        self.assertEqual(self.ship.current_shields, 50, "Shields should net same (50 + 10 - 10)")
        self.assertEqual(self.ship.hp, initial_hp, "HP should be untouched")

    def test_damage_absorption_and_regen_low_damage(self):
        self.add_armor()
        initial_hp = self.ship.hp  # Save initial HP after setup
        # Armor Value = 10
        # Shields = 50
        
        # Incoming Damage 5
        # - 5 Absorbed (max is 10)
        # - Net Damage = 0
        # - Shields + 5 = 55
        
        self.ship.take_damage(5)
        
        self.assertEqual(self.ship.current_shields, 55, "Shields should increase by 5")
        self.assertEqual(self.ship.hp, initial_hp, "HP should be untouched")

    def test_stacking_behavior(self):
        # Add TWO armor plates
        self.add_armor()
        self.add_armor()
        
        # Should NOT stack values because of "stack_group": "Crystalline"
        # Total Value = 10 (not 20)
        self.assertEqual(self.ship.crystalline_armor, 10, "Should use max value of stack group")

    def test_stacking_with_other_source(self):
        self.add_armor()
        
        # Add a component with SAME ability but DIFFERENT group (or no group)
        other_data = {
            "id": "crystalline_hull",
            "name": "Crystalline Hull",
            "type": "Amor", # Typo doesn't matter for ability calc
            "mass": 10,
            "hp": 10,
            "abilities": {
                "CrystallineArmor": 5 # No group -> stacks
            }
        }
        from components import Component
        c = Component(other_data)
        self.ship.layers[LayerType.ARMOR]['components'].append(c)
        self.ship.recalculate_stats()
        
        # Total = 10 (Armor) + 5 (Hull) = 15
        self.assertEqual(self.ship.crystalline_armor, 15, "Should stack with non-grouped source")

if __name__ == '__main__':
    unittest.main()
