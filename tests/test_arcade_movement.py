import unittest
import sys
import os
import pygame
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType
from components import load_components, create_component, Engine, Thruster

class TestArcadeMovement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")

    def setUp(self):
        self.ship = Ship("TestShip", 100, 100, (255, 255, 255))
        # Basic setup
        # Core: Bridge
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        # Inner: Tank
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        # Outer: Engine
        self.ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        
        # Initial recalc
        self.ship.recalculate_stats()
        
        # Verify stats populated
        self.assertGreater(self.ship.total_thrust, 0)
        self.assertGreater(self.ship.max_fuel, 0)
        self.ship.current_fuel = self.ship.max_fuel

    def test_stats(self):
        # Physics validation using current INVERSE MASS SCALING model
        # Acceleration = (Thrust * K_THRUST) / (Mass^2)
        # Max Speed = (Thrust * K_SPEED) / Mass
        K_THRUST = 150000
        K_SPEED = 1500
        
        expected_accel = (self.ship.total_thrust * K_THRUST) / (self.ship.mass ** 2)
        self.assertAlmostEqual(self.ship.acceleration_rate, expected_accel, places=2)
        
        # Max Speed
        expected_max_speed = (self.ship.total_thrust * K_SPEED) / self.ship.mass
        self.assertAlmostEqual(self.ship.max_speed, expected_max_speed, places=2)

    def test_thrust_increases_speed(self):
        dt = 0.1
        initial_speed = self.ship.current_speed
        self.assertEqual(initial_speed, 0)
        
        self.ship.thrust_forward(dt)
        
        # Should increase by accel * dt
        expected_speed = self.ship.acceleration_rate * dt
        self.assertAlmostEqual(self.ship.current_speed, expected_speed)
        
        # Fuel consumed
        self.assertLess(self.ship.current_fuel, self.ship.max_fuel)

    def test_movement_direction(self):
        dt = 1.0
        self.ship.current_speed = 100
        self.ship.angle = 0 # Right (1, 0)
        
        initial_pos = pygame.math.Vector2(self.ship.position)
        
        self.ship.update(dt)
        
        # Should move 100 units right (minus drag decay on speed, but position uses velocity calculated from speed)
        # Wait, update applies drag to speed!
        # self.current_speed *= (1 - self.drag * dt)
        # Then velocity = forward * speed
        # Pos += velocity * dt
        
        # So actual movement will be slightly less if drag is high
        # But direction should be purely X axis
        new_pos = self.ship.position
        diff = new_pos - initial_pos
        
        self.assertGreater(diff.x, 50) # Moved right
        self.assertAlmostEqual(diff.y, 0, places=5) # Minimal Y movement
        
        # Test Rotation
        self.ship.angle = 90 # Down (0, 1) if pygame coord (y down)
        # Rotate logic check:
        # ship.rotate not called here, manual angle set
        
        initial_pos = pygame.math.Vector2(self.ship.position)
        self.ship.current_speed = 100 # Reset speed
        self.ship.update(dt)
        
        diff = self.ship.position - initial_pos
        self.assertAlmostEqual(diff.x, 0, delta=1.0) 
        self.assertGreater(diff.y, 50) # Moved down

    def test_max_speed_cap(self):
        dt = 1.0
        # Force huge speed
        self.ship.current_speed = self.ship.max_speed + 1000
        
        # Thrusting should cap it? 
        # thrust_forward Caps it: if speed > max: speed = max
        self.ship.thrust_forward(dt)
        
        # Note: thrust_forward adds accel first, THEN caps.
        self.assertLessEqual(self.ship.current_speed, self.ship.max_speed + 0.01) # Float tolerance

if __name__ == '__main__':
    unittest.main()
