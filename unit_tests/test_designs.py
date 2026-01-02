"""Tests for ship design factory functions."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, Bridge, Engine
from designs import create_brick, create_interceptor


class TestDesignFactories(unittest.TestCase):
    """Test programmatic ship creation functions."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_create_brick_returns_ship(self):
        """create_brick should return a valid Ship object."""
        ship = create_brick(100, 200)
        
        self.assertIsInstance(ship, Ship)
        self.assertEqual(ship.name, "The Brick")
        self.assertEqual(ship.position.x, 100)
        self.assertEqual(ship.position.y, 200)
    
    def test_create_brick_has_bridge(self):
        """create_brick ship should have a bridge component."""
        ship = create_brick(0, 0)
        
        core_components = ship.layers[LayerType.CORE]['components']
        has_bridge = any(isinstance(c, Bridge) for c in core_components)
        
        self.assertTrue(has_bridge, "Brick should have a Bridge in CORE layer")
    
    def test_create_brick_has_engines(self):
        """create_brick ship should have engine components."""
        ship = create_brick(0, 0)
        
        all_components = []
        for layer_data in ship.layers.values():
            all_components.extend(layer_data['components'])
        
        has_engine = any(isinstance(c, Engine) for c in all_components)
        self.assertTrue(has_engine, "Brick should have engines")
    
    def test_create_brick_has_armor(self):
        """create_brick ship should have armor plates."""
        ship = create_brick(0, 0)
        
        armor_components = ship.layers[LayerType.ARMOR]['components']
        self.assertGreater(len(armor_components), 0, "Brick should have armor")
    
    def test_create_interceptor_returns_ship(self):
        """create_interceptor should return a valid Ship object."""
        ship = create_interceptor(300, 400)
        
        self.assertIsInstance(ship, Ship)
        self.assertEqual(ship.name, "The Interceptor")
        self.assertEqual(ship.position.x, 300)
        self.assertEqual(ship.position.y, 400)
    
    def test_create_interceptor_has_bridge(self):
        """create_interceptor ship should have a bridge component."""
        ship = create_interceptor(0, 0)
        
        core_components = ship.layers[LayerType.CORE]['components']
        has_bridge = any(isinstance(c, Bridge) for c in core_components)
        
        self.assertTrue(has_bridge, "Interceptor should have a Bridge in CORE layer")
    
    def test_create_interceptor_has_weapons(self):
        """create_interceptor ship should have weapons."""
        ship = create_interceptor(0, 0)
        
        outer_components = ship.layers[LayerType.OUTER]['components']
        # Should have railguns in OUTER layer
        has_weapons = any(hasattr(c, 'damage') for c in outer_components)
        
        self.assertTrue(has_weapons, "Interceptor should have weapons")
    
    def test_designs_can_recalculate_stats(self):
        """Design ships should be able to recalculate stats without error."""
        brick = create_brick(0, 0)
        interceptor = create_interceptor(0, 0)
        
        # Should not raise any exceptions
        brick.recalculate_stats()
        interceptor.recalculate_stats()
        
        # Should have positive mass after recalculating
        self.assertGreater(brick.mass, 0)
        self.assertGreater(interceptor.mass, 0)


if __name__ == '__main__':
    unittest.main()
