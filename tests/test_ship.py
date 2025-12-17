import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType
from components import load_components, create_component, Bridge

class TestShip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("components.json")

    def test_add_component_constraints(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        # Bridge is allowed in CORE
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        self.assertIn(bridge, ship.layers[LayerType.CORE]['components'])
        
        # Railgun allowed in OUTER. Try adding to CORE (should fail or be allowed if logic checks?)
        # Ship.add_component definition:
        # if not layer_type in component.allowed_layers: return False
        railgun = create_component('railgun') # allowed: OUTER
        result = ship.add_component(railgun, LayerType.CORE)
        self.assertFalse(result, "Should not allow Railgun in CORE")
        
        result_ok = ship.add_component(railgun, LayerType.OUTER)
        self.assertTrue(result_ok)

    def test_mass_calculation(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # Initial mass
        self.assertEqual(ship.current_mass, 0)
        
        bridge = create_component('bridge') # 50
        ship.add_component(bridge, LayerType.CORE)
        self.assertEqual(ship.current_mass, 50)

    def test_damage_armor_absorption(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        # Add Armor Plate (250 HP) to ARMOR layer
        armor = create_component('armor_plate')
        ship.add_component(armor, LayerType.ARMOR)
        
        # Add Bridge (200 HP) to CORE
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        
        # Apply 100 damage (Should be absorbed by Armor)
        ship.take_damage(100)
        
        self.assertEqual(armor.current_hp, 150)
        self.assertEqual(bridge.current_hp, 200) # Bridge untouched
        
        # Apply 200 damage (overflows armor by 50)
        # Armor has 150 left. 200 - 150 = 50 overflow to next layers.
        # Next is OUTER (empty), INNER (empty), CORE (Bridge).
        # Bridge takes 50.
        ship.take_damage(200)
        
        self.assertEqual(armor.current_hp, 0)
        self.assertFalse(armor.is_active)
        self.assertEqual(bridge.current_hp, 150)

    def test_serialization(self):
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # Add components
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('railgun'), LayerType.OUTER)
        
        data = ship.to_dict()
        
        self.assertEqual(data['name'], "TestShip")
        self.assertTrue("layers" in data)
        self.assertTrue("CORE" in data["layers"])
        self.assertTrue(len(data["layers"]["CORE"]) > 0)
        
        # Reconstruct
        new_ship = Ship.from_dict(data)
        
        self.assertEqual(new_ship.name, "TestShip")
        self.assertEqual(len(new_ship.layers[LayerType.CORE]['components']), 1)
        self.assertEqual(len(new_ship.layers[LayerType.OUTER]['components']), 1)
        # Check component types
        self.assertEqual(new_ship.layers[LayerType.CORE]['components'][0].name, "Bridge")

if __name__ == '__main__':
    unittest.main()
