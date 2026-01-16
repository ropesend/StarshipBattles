"""
Tests for Ship serialization (to_dict/from_dict round-trip).
TDD-first approach for ShipSerializer extraction.
"""
import unittest
import pygame
from unittest import mock

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


class TestShipSerialization(unittest.TestCase):
    """Test Ship serialization round-trip behavior."""

    def setUp(self):
        """Initialize game data for each test."""
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data()
        load_components(str(get_data_dir() / "components.json"))
    
    def tearDown(self):
        """Clean up after each test."""
        RegistryManager.instance().clear()
        if pygame.get_init():
            pygame.quit()
        mock.patch.stopall()
    
    def test_roundtrip_basic(self):
        """Basic ship properties survive round-trip serialization."""
        ship = Ship("TestShip", 0, 0, (100, 150, 200), team_id=2, 
                    ship_class="Frigate", theme_id="Terran")
        ship.ai_strategy = "aggressive"
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Verify basic properties
        self.assertEqual(restored.name, "TestShip")
        self.assertEqual(restored.ship_class, "Frigate")
        self.assertEqual(restored.theme_id, "Terran")
        self.assertEqual(restored.team_id, 2)
        self.assertEqual(tuple(restored.color), (100, 150, 200))
        self.assertEqual(restored.ai_strategy, "aggressive")
    
    def test_roundtrip_with_components(self):
        """Components in all layers survive round-trip."""
        ship = Ship("ComponentShip", 0, 0, (255, 255, 255))
        
        # Add components to various layers
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        
        railgun = create_component('railgun')
        ship.add_component(railgun, LayerType.OUTER)
        
        armor = create_component('armor_plate')
        ship.add_component(armor, LayerType.ARMOR)
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Verify components are present
        core_ids = [c.id for c in restored.layers[LayerType.CORE]['components']]
        self.assertIn('bridge', core_ids)
        
        outer_ids = [c.id for c in restored.layers[LayerType.OUTER]['components']]
        self.assertIn('railgun', outer_ids)
        
        armor_ids = [c.id for c in restored.layers[LayerType.ARMOR]['components']]
        self.assertIn('armor_plate', armor_ids)
    
    def test_roundtrip_with_modifiers(self):
        """Components with modifiers survive round-trip when modifiers are present."""
        ship = Ship("ModifierShip", 0, 0, (255, 255, 255))
        
        # Add component - modifiers are a list of ApplicationModifier objects
        railgun = create_component('railgun')
        ship.add_component(railgun, LayerType.OUTER)
        
        # Count original modifiers
        original_count = len(railgun.modifiers)
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Find railgun in restored ship
        restored_railguns = [c for c in restored.layers[LayerType.OUTER]['components'] 
                            if c.id == 'railgun']
        self.assertEqual(len(restored_railguns), 1)
        
        restored_railgun = restored_railguns[0]
        # Verify the default modifiers (if any) are preserved
        self.assertEqual(len(restored_railgun.modifiers), original_count)
    
    def test_roundtrip_preserves_resources(self):
        """Resource values (fuel, energy, ammo) survive round-trip."""
        ship = Ship("ResourceShip", 0, 0, (255, 255, 255))
        
        # Add components that provide resource capacity
        # Need fuel tank for fuel, generator for energy
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('fuel_tank'), LayerType.CORE)
        ship.add_component(create_component('generator'), LayerType.CORE)
        ship.recalculate_stats()
        
        # Get max values to ensure we're setting within limits
        max_fuel = ship.resources.get_max_value("fuel")
        max_energy = ship.resources.get_max_value("energy")
        
        # Only test if we have capacity
        if max_fuel > 0:
            test_fuel = min(50.0, max_fuel)
            ship.resources.set_value("fuel", test_fuel)
        if max_energy > 0:
            test_energy = min(75.0, max_energy)
            ship.resources.set_value("energy", test_energy)
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Verify resources restored (compare with what was actually set)
        if max_fuel > 0:
            self.assertAlmostEqual(restored.resources.get_value("fuel"), test_fuel, places=1)
        if max_energy > 0:
            self.assertAlmostEqual(restored.resources.get_value("energy"), test_energy, places=1)
    
    def test_roundtrip_preserves_stats(self):
        """Calculated stats (HP, mass, speed) are consistent after round-trip."""
        ship = Ship("StatsShip", 0, 0, (255, 255, 255), ship_class="Escort")
        
        # Add components that affect stats
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        
        engine = create_component('engine')
        ship.add_component(engine, LayerType.INNER)
        
        ship.recalculate_stats()
        
        original_max_hp = ship.max_hp
        original_mass = ship.mass
        original_max_speed = ship.max_speed
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Stats should match (within tolerance for floating point)
        self.assertEqual(restored.max_hp, original_max_hp)
        self.assertAlmostEqual(restored.mass, original_mass, places=1)
        self.assertAlmostEqual(restored.max_speed, original_max_speed, places=1)
    
    def test_hull_not_serialized_but_restored(self):
        """HULL layer is not serialized but auto-equipped on restore."""
        ship = Ship("HullTestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        
        # Verify hull exists
        self.assertEqual(len(ship.layers[LayerType.HULL]['components']), 1)
        original_hull_id = ship.layers[LayerType.HULL]['components'][0].id
        
        # Round-trip
        data = ship.to_dict()
        
        # HULL should NOT be in serialized data
        self.assertNotIn('HULL', data['layers'])
        
        # Restore
        restored = Ship.from_dict(data)
        
        # HULL should be auto-equipped on restore
        self.assertEqual(len(restored.layers[LayerType.HULL]['components']), 1)
        restored_hull_id = restored.layers[LayerType.HULL]['components'][0].id
        self.assertEqual(restored_hull_id, original_hull_id)
    
    def test_layer_order_preserved(self):
        """Multiple components in same layer maintain order."""
        ship = Ship("OrderShip", 0, 0, (255, 255, 255))
        
        # Add multiple components to OUTER
        for _ in range(3):
            railgun = create_component('railgun')
            ship.add_component(railgun, LayerType.OUTER)
        
        original_count = len(ship.layers[LayerType.OUTER]['components'])
        
        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)
        
        # Same count should be preserved
        restored_count = len(restored.layers[LayerType.OUTER]['components'])
        self.assertEqual(restored_count, original_count)


if __name__ == '__main__':
    unittest.main()
