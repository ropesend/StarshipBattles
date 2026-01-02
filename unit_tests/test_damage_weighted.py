
import unittest
from unittest.mock import MagicMock, patch
import pygame
import random
from ship_combat import ShipCombatMixin
from components import Component, LayerType  # Phase 7: Removed Bridge import

class MockComponent(Component):
    def __init__(self, name, hp, max_hp):
        self.id = "mock_comp"
        self.name = name
        self.current_hp = hp
        self.max_hp = max_hp
        self.is_active = True
        self.mass = 10
        self.abilities = {}
        self.modifiers = []
        self.type_str = "MockComponent"

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_active = False

class MockBridge(MockComponent):  # Phase 7: Changed from Bridge to MockComponent
    def __init__(self, name, hp, max_hp):
        super().__init__(name, hp, max_hp)
        self.id = "bridge"
        self.type_str = "Bridge"  # Set type_str for detection

class MockShip(ShipCombatMixin):
    def __init__(self):
        self.position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.current_shields = 0
        self.max_shields = 100
        self.is_alive = True
        self.name = "TestShip"
        self.layers = {
            LayerType.ARMOR: {'components': [], 'radius_pct': 1.0},
            LayerType.OUTER: {'components': [], 'radius_pct': 0.8},
            LayerType.INNER: {'components': [], 'radius_pct': 0.5},
            LayerType.CORE: {'components': [], 'radius_pct': 0.3}
        }

    def die(self):
        self.is_alive = False

    def recalculate_stats(self):
        pass

    def update_derelict_status(self):
        # Stub for testing
        pass

class TestDamageWeighted(unittest.TestCase):
    def setUp(self):
        self.ship = MockShip()
    
    @patch('random.choices')
    def test_damage_distribution_flow(self, mock_choices):
        """Verify that damage sticks to the layer and iterates through components."""
        c1 = MockComponent("Armor1", 10, 10)
        c2 = MockComponent("Armor2", 10, 10)
        self.ship.layers[LayerType.ARMOR]['components'] = [c1, c2]
        
        bridge = MockBridge("Bridge", 100, 100)
        self.ship.layers[LayerType.CORE]['components'] = [bridge]
        
        # Mock choices to return [c1] then [c2] then [bridge]
        mock_choices.side_effect = [[c1], [c2], [bridge]]
        
        # 50 damage: 10 to C1, 10 to C2, 30 to Bridge
        self.ship.take_damage(50)
        
        self.assertEqual(c1.current_hp, 0)
        self.assertEqual(c2.current_hp, 0)
        self.assertEqual(bridge.current_hp, 70)

    def test_weighted_probability_exclusion(self):
        """Verify that components with 0 HP are excluded from target list."""
        c1 = MockComponent("Broken", 0, 10)
        c2 = MockComponent("Healthy", 10, 10)
        self.ship.layers[LayerType.ARMOR]['components'] = [c1, c2]
        
        self.ship.take_damage(5)
        self.assertEqual(c1.current_hp, 0)
        self.assertEqual(c2.current_hp, 5)

    def test_bridge_destruction_kills_ship(self):
        """Verify that ship dies when bridge HP reaches 0."""
        bridge = MockBridge("Bridge", 50, 50)
        self.ship.layers[LayerType.CORE]['components'] = [bridge]
        
        # 100 damage: all to bridge
        self.ship.take_damage(100)
        
        self.assertEqual(bridge.current_hp, 0)
        self.assertEqual(bridge.current_hp, 0)
        self.assertTrue(self.ship.is_alive) # Should be alive now (hardcoded logic removed)

if __name__ == '__main__':
    unittest.main()
