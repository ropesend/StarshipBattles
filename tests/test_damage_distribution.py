
import unittest
from unittest.mock import MagicMock, patch
import pygame
import random
from ship_combat import ShipCombatMixin
from components import Component, LayerType, Bridge

class MockComponent(Component):
    def __init__(self, name, hp, max_hp):
        self.name = name
        self.current_hp = hp
        self.max_hp = max_hp
        self.is_active = True
        self.mass = 10
        self.power_draw = 0
        self.crew_req = 0

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_active = False

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
            LayerType.ARMOR: {'components': []},
            LayerType.OUTER: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.CORE: {'components': []}
        }

    def die(self):
        self.is_alive = False

    def recalculate_stats(self):
        pass

class TestDamageDistribution(unittest.TestCase):
    def setUp(self):
        self.ship = MockShip()
    
    @patch('random.choices')
    def test_damage_distribution_flow(self, mock_choices):
        """
        Verify that damage sticks to the layer and iterates through components.
        """
        # Armor layer: C1 (10 HP), C2 (10 HP)
        c1 = MockComponent("Armor1", 10, 10)
        c2 = MockComponent("Armor2", 10, 10)
        self.ship.layers[LayerType.ARMOR]['components'] = [c1, c2]
        
        # Core layer: Bridge (100 HP)
        bridge = MockComponent("Bridge", 100, 100)
        bridge.is_bridge = True
        self.ship.layers[LayerType.CORE]['components'] = [bridge]
        
        # We want to simulate:
        # 1. 50 Damage comes in.
        # 2. Pick C1 first.
        # 3. Pick C2 second.
        # 4. Remaining 30 goes to next layers.
        
        # Mock choices to return [c1] then [c2]
        mock_choices.side_effect = [[c1], [c2], [bridge]]
        
        self.ship.take_damage(50)
        
        # Assertions
        self.assertEqual(c1.current_hp, 0, "C1 should be destroyed")
        self.assertEqual(c2.current_hp, 0, "C2 should be destroyed")
        
        # Previous logic would have left C2 intact and Bridge taking 40 dmg.
        # New logic: Bridge takes 30 dmg (50 - 10 - 10).
        self.assertEqual(bridge.current_hp, 70, "Bridge should take remaining 30 damage")

    def test_weighted_probability(self):
        """
        Verify that selection is weighted by HP.
        Since we can't easily assert probability in a single run without mocking,
        we verify the weights passed to random.choices would be correct.
        This is slightly implicit, relying on the implementation correctness.
        
        Instead, we can test that components with 0 HP are excluded from target list.
        """
        c1 = MockComponent("Broken", 0, 10)
        c1.is_active = False # Normal state
        c2 = MockComponent("Healthy", 10, 10)
        
        self.ship.layers[LayerType.ARMOR]['components'] = [c1, c2]
        
        # With real random, checks.
        # C1 has 0 HP, so it should NEVER be picked. 
        # C2 should absorb all damage (up to 10).
        
        self.ship.take_damage(5)
        
        self.assertEqual(c1.current_hp, 0)
        self.assertEqual(c2.current_hp, 5)

if __name__ == '__main__':
    unittest.main()
