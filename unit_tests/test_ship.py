import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component  # Phase 7: Removed Bridge import

class TestShip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data() 
        load_components("data/components.json")

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
        # Inject TestShip definition strictly
        from ship import VEHICLE_CLASSES
        VEHICLE_CLASSES["TestShip"] = {
            "hull_mass": 50, "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }
        
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # ship._initialize_layers() # Ship init calls this, and it sees the new class def logic
        
        # Add Armor Plate (250 HP) to ARMOR layer
        armor = create_component('armor_plate')
        ship.add_component(armor, LayerType.ARMOR)
        
        # Add Bridge (200 HP) to CORE - requires crew to be active
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        
        # Add crew support so bridge is active and can receive damage
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        
        ship.recalculate_stats()
        self.assertTrue(bridge.is_active, "Bridge should be active with crew support")
        
        # Apply 100 damage (Should be absorbed by Armor)
        ship.take_damage(100)
        
        self.assertEqual(armor.current_hp, 150)
        self.assertEqual(bridge.current_hp, 200) # Bridge untouched
        
        # Apply 200 damage (overflows armor by 50)
        # Armor has 150 left. 200 - 150 = 50 overflow to next layers.
        # Next is OUTER (empty), INNER (empty), CORE (Bridge + crew_quarters + life_support).
        # Damage is dealt to a random component - if that component has less HP than 
        # the damage, the remaining damage continues to next random component.
        # Note: With current damage mechanics, one component takes as much as it can absorb.
        ship.take_damage(200)
        
        self.assertEqual(armor.current_hp, 0)
        self.assertFalse(armor.is_active)
        # 50 damage should be distributed to CORE components
        # Due to random selection and HP caps, verify total damage absorbed is correct
        core_hp_lost = sum(c.max_hp - c.current_hp for c in ship.layers[LayerType.CORE]['components'])
        self.assertGreaterEqual(core_hp_lost, 40, 
            f"At least 40 HP should be lost in CORE (got {core_hp_lost})")
        self.assertLessEqual(core_hp_lost, 50,
            f"At most 50 HP should be lost in CORE (got {core_hp_lost})")

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
