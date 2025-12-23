"""Tests for ShipPhysicsMixin movement mechanics."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component


class TestShipPhysicsThrust(unittest.TestCase):
    """Test thrust and fuel consumption."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        self.ship.recalculate_stats()
    
    def test_thrust_forward_sets_flag(self):
        """Thrusting should set is_thrusting flag."""
        self.ship.is_thrusting = False
        initial_fuel = self.ship.current_fuel
        
        self.ship.thrust_forward()
        
        # Should have set thrusting flag if we have fuel
        if initial_fuel > 0:
            self.assertTrue(self.ship.is_thrusting)
    
    def test_thrust_forward_consumes_fuel(self):
        """Thrusting should consume fuel."""
        initial_fuel = self.ship.current_fuel
        self.assertGreater(initial_fuel, 0, "Ship needs fuel for this test")
        
        self.ship.thrust_forward()
        
        # Should have consumed some fuel
        self.assertLess(self.ship.current_fuel, initial_fuel)
    
    def test_thrust_no_fuel_no_thrust(self):
        """Can't thrust without fuel."""
        self.ship.current_fuel = 0
        
        self.ship.thrust_forward()
        
        self.assertFalse(self.ship.is_thrusting)
    
    def test_update_physics_accelerates_when_thrusting(self):
        """Speed should increase toward max when thrusting."""
        initial_speed = self.ship.current_speed
        self.assertEqual(initial_speed, 0)
        
        # Thrust and update
        self.ship.thrust_forward()
        self.ship.update_physics_movement()
        
        # Speed should have increased
        self.assertGreater(self.ship.current_speed, initial_speed)
    
    def test_update_physics_decelerates_when_not_thrusting(self):
        """Speed should decrease when not thrusting."""
        # Give ship some speed first
        self.ship.current_speed = 10
        
        # Don't thrust
        self.ship.is_thrusting = False
        self.ship.update_physics_movement()
        
        # Speed should decrease toward 0
        self.assertLess(self.ship.current_speed, 10)


class TestShipPhysicsRotation(unittest.TestCase):
    """Test ship rotation mechanics."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        self.ship.add_component(create_component('thruster'), LayerType.INNER)
        self.ship.recalculate_stats()
    
    def test_rotate_left(self):
        """Rotating left (direction=-1) should decrease angle."""
        initial_angle = self.ship.angle
        
        self.ship.rotate(-1)
        
        # Allow for modular wrapping
        angle_change = self.ship.angle - initial_angle
        if angle_change > 180:
            angle_change -= 360
        
        self.assertLess(angle_change, 0)
    
    def test_rotate_right(self):
        """Rotating right (direction=+1) should increase angle."""
        initial_angle = self.ship.angle
        
        self.ship.rotate(1)
        
        # Allow for modular wrapping
        angle_change = self.ship.angle - initial_angle
        if angle_change < -180:
            angle_change += 360
        
        self.assertGreater(angle_change, 0)
    
    def test_rotation_respects_turn_speed(self):
        """Rotation amount should depend on turn_speed stat."""
        # Ship with thrusters should have turn_speed > 0
        self.assertGreater(self.ship.turn_speed, 0)
        
        # Rotation amount should be related to turn_speed
        initial_angle = self.ship.angle
        self.ship.rotate(1)
        rotation = self.ship.angle - initial_angle
        
        # Expected: turn_speed / 100.0 per rotate call
        expected_rotation = self.ship.turn_speed / 100.0
        self.assertAlmostEqual(rotation, expected_rotation, places=3)


class TestShipPhysicsMovement(unittest.TestCase):
    """Test ship position updates."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        self.ship.recalculate_stats()
    
    def test_position_updates_with_velocity(self):
        """Position should update based on velocity."""
        initial_pos = pygame.math.Vector2(self.ship.position)
        
        # Thrust first to set speed, then update to move
        self.ship.thrust_forward()  # Sets is_thrusting flag
        self.ship.update_physics_movement()  # Accelerates and moves
        
        # Position should have changed since we're now moving
        self.assertNotEqual(tuple(self.ship.position), tuple(initial_pos))
    
    def test_velocity_matches_heading(self):
        """Velocity should match ship heading direction."""
        self.ship.angle = 90  # Facing down (in screen coords)
        self.ship.current_speed = 10
        
        self.ship.update_physics_movement()
        
        # Velocity should primarily be in Y direction (down)
        self.assertGreater(abs(self.ship.velocity.y), abs(self.ship.velocity.x))


if __name__ == '__main__':
    unittest.main()
