import unittest
import sys
import os
import pygame
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, create_component

class TestArcadeMovement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")

    def setUp(self):
        # Use Cruiser class which has INNER layer (Capital_Standard config)
        self.ship = Ship("TestShip", 100, 100, (255, 255, 255), ship_class="Cruiser")
        # Basic setup - need crew infrastructure for components to be active
        # Core: Bridge (requires crew to function)
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        # Core: Generator
        self.ship.add_component(create_component('generator'), LayerType.CORE)
        
        # INNER: Multiple crew quarters and life support (Cruiser needs more crew than Escort)
        for _ in range(3):
            self.ship.add_component(create_component('crew_quarters'), LayerType.INNER)
            self.ship.add_component(create_component('life_support'), LayerType.INNER)
        
        # Inner: Fuel Tank
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        # Outer: Engine (requires crew to be active)
        self.ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        
        # Initial recalc
        self.ship.recalculate_stats()
        
        # Verify stats populated - engine should be active with crew support
        self.assertGreater(self.ship.total_thrust, 0, 
            f"Engine should have thrust. Crew: {self.ship.crew_onboard}, Required: {self.ship.crew_required}")
        self.assertGreater(self.ship.resources.get_max_value("fuel"), 0)
        self.ship.resources.get_resource("fuel").current_value = self.ship.resources.get_max_value("fuel")

    def test_stats(self):
        # Physics validation using tick-based INVERSE MASS SCALING model
        # Acceleration = (Thrust * K_THRUST) / (Mass^2)
        # Max Speed = (Thrust * K_SPEED) / Mass
        # Constants scaled for dt=1.0 per tick
        K_THRUST = 2500   # Tick-based constant
        K_SPEED = 25      # Tick-based constant
        
        expected_accel = (self.ship.total_thrust * K_THRUST) / (self.ship.mass ** 2)
        self.assertAlmostEqual(self.ship.acceleration_rate, expected_accel, places=2)
        
        # Max Speed
        expected_max_speed = (self.ship.total_thrust * K_SPEED) / self.ship.mass
        self.assertAlmostEqual(self.ship.max_speed, expected_max_speed, places=2)

    def test_thrust_increases_speed(self):
        # dt = 1.0 # 1 tick (removed)
        initial_speed = self.ship.current_speed
        self.assertEqual(initial_speed, 0)
        
        self.ship.thrust_forward()
        self.ship.update()  # Full update triggers component fuel consumption
        
        # Speed should increase by acceleration_rate (flag-based physics)
        self.assertGreater(self.ship.current_speed, 0)
        
        # Fuel consumed via engine's ResourceConsumption ability
        self.assertLess(self.ship.resources.get_value("fuel"), self.ship.resources.get_max_value("fuel"))

    def test_movement_direction(self):
        dt = 1.0
        self.ship.current_speed = 100
        self.ship.angle = 0 # Right (1, 0)
        
        initial_pos = pygame.math.Vector2(self.ship.position)
        
        initial_pos = pygame.math.Vector2(self.ship.position)
        
        self.ship.update()
        
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
        self.ship.update()
        
        diff = self.ship.position - initial_pos
        self.assertAlmostEqual(diff.x, 0, delta=1.0) 
        self.assertGreater(diff.y, 50) # Moved down

    def test_max_speed_cap(self):
        """Speed above max should decelerate toward max_speed when thrusting."""
        initial_over_speed = self.ship.max_speed + 1000
        self.ship.current_speed = initial_over_speed
        
        # Thrusting sets target_speed = max_speed, so ship decelerates toward it
        self.ship.thrust_forward()
        self.ship.update_physics_movement()
        
        # Speed should have decreased (moving toward max_speed)
        self.assertLess(self.ship.current_speed, initial_over_speed, 
            "Speed should decrease when above max_speed and thrusting")
        
        # Run multiple updates to reach max_speed
        for _ in range(3000):  # Enough iterations to converge
            self.ship.thrust_forward()
            self.ship.update_physics_movement()
        
        # After many updates, should be at or very close to max_speed
        self.assertAlmostEqual(self.ship.current_speed, self.ship.max_speed, places=1,
            msg="Speed should converge to max_speed when thrusting")

if __name__ == '__main__':
    unittest.main()
