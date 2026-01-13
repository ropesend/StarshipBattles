import unittest
import os
import pygame

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, create_component  # Phase 7: Removed Bridge import
from game.core.registry import RegistryManager

class TestShip(unittest.TestCase):
    def setUp(self):
        initialize_ship_data() 
        load_components("data/components.json")

    def tearDown(self):
        RegistryManager.instance().clear()
        if pygame.get_init():
            pygame.quit()

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
        # Initial mass: Ships now auto-equip Hull component (50 mass for Escort)
        # Hull is added in __init__ but current_mass not updated until recalculate_stats
        ship.recalculate_stats()  # Trigger calculation
        self.assertEqual(ship.current_mass, 50)  # Hull mass
        
        bridge = create_component('bridge') # 50
        ship.add_component(bridge, LayerType.CORE)
        self.assertEqual(ship.current_mass, 100)  # Hull (50) + Bridge (50)

    def test_damage_armor_absorption(self):
        # Inject TestShip definition strictly
        from game.core.registry import RegistryManager
        RegistryManager.instance().vehicle_classes["TestShip"] = {
            "default_hull_id": "hull_escort", "max_mass": 1000,
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
        # Add components (Hull is auto-equipped already)
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
        # HULL: Hull (auto-equipped) = 1 component
        # CORE: Bridge (from data) = 1 component
        self.assertEqual(len(new_ship.layers[LayerType.HULL]['components']), 1)
        self.assertEqual(len(new_ship.layers[LayerType.CORE]['components']), 1)
        self.assertEqual(len(new_ship.layers[LayerType.OUTER]['components']), 1)
        # Check Bridge is present
        bridge_found = any(c.type_str == 'Bridge' for c in new_ship.layers[LayerType.CORE]['components'])
        self.assertTrue(bridge_found, "Bridge component should be in CORE layer")

class TestShipClassMutation(unittest.TestCase):
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data(os.getcwd())
        load_components("data/components.json")
        self.ship = Ship("Mutation Test", 0, 0, (255, 255, 255), ship_class="Frigate")

    def tearDown(self):
        RegistryManager.instance().clear()
        if pygame.get_init():
            pygame.quit()

    def test_change_class_migration(self):
        """Verify components migrate or are removed during class change."""
        # Add components to Frigate
        bridge = create_component('bridge')
        self.ship.add_component(bridge, LayerType.CORE)
        
        railgun = create_component('railgun')
        self.ship.add_component(railgun, LayerType.OUTER)
        
        # Change to "Destroyer" with migration
        self.ship.change_class("Destroyer", migrate_components=True)
        
        # Verify components remained
        self.assertEqual(self.ship.ship_class, "Destroyer")
        
        # Helper to find component in layer
        def has_comp(layer_type, comp):
            return comp in self.ship.layers[layer_type]['components']
            
        self.assertTrue(has_comp(LayerType.CORE, bridge))
        self.assertTrue(has_comp(LayerType.OUTER, railgun))
        
    def test_derelict_status_logic(self):
        """
        Verify is_derelict update logic when key components are destroyed.

        The new data-driven system:
        - Ships with hulls have RequiresCommandAndControl ability
        - Ships only become derelict if they have components requiring command
        - CommandAndControl is provided by bridges or similar components
        - Destroying all command components makes the ship derelict
        """
        # Frigate ships automatically get a hull with RequiresCommandAndControl ability
        # Verify the ship requires command and control
        requires_command = self.ship.get_total_ability_value('RequiresCommandAndControl')
        self.assertGreater(requires_command, 0, "Frigate hull should require CommandAndControl")

        # Add bridge to provide CommandAndControl
        bridge = create_component('bridge')
        self.ship.add_component(bridge, LayerType.CORE)

        # Add crew support to keep bridge operational
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)

        # Recalculate and verify ship is operational
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict, "Ship should be operational with active bridge")

        # Verify bridge provides CommandAndControl
        has_command = self.ship.get_total_ability_value('CommandAndControl', operational_only=True)
        self.assertGreater(has_command, 0, "Bridge should provide CommandAndControl")

        # Destroy the bridge
        bridge.current_hp = 0
        bridge.is_active = False

        # Update status and verify ship becomes derelict
        self.ship.recalculate_stats()
        self.ship.update_derelict_status()

        # Verify no operational command remaining
        has_command_after = self.ship.get_total_ability_value('CommandAndControl', operational_only=True)
        self.assertEqual(has_command_after, 0, "No CommandAndControl should remain after bridge destruction")

        # Ship should now be derelict
        self.assertTrue(self.ship.is_derelict, "Ship should be derelict after losing all CommandAndControl")

if __name__ == '__main__':
    unittest.main()
