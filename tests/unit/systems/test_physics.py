import unittest
import pygame
import sys
import os
import math

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.engine.physics import PhysicsBody


class TestPhysicsBasics(unittest.TestCase):
    """Test basic PhysicsBody initialization and properties."""
    
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
    
    
    def test_initialization(self):
        """PhysicsBody should initialize with correct position and angle."""
        body = PhysicsBody(100, 200, 90)
        self.assertEqual(body.position, pygame.math.Vector2(100, 200))
        self.assertEqual(body.angle, 90)
        self.assertEqual(body.velocity, pygame.math.Vector2(0, 0))
    
    def test_default_values(self):
        """PhysicsBody should have sensible defaults."""
        body = PhysicsBody(0, 0)
        self.assertEqual(body.angle, 0)
        self.assertEqual(body.mass, 1.0)
        self.assertGreater(body.drag, 0)


class TestPhysicsMovement(unittest.TestCase):
    """Test PhysicsBody movement and physics update."""
    
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
    
    
    def test_update_movement(self):
        """Test basic velocity application."""
        body = PhysicsBody(0, 0)
        body.velocity = pygame.math.Vector2(10, 0)
        # PhysicsBody implementation:
        # velocity *= (1 - drag)
        # position += velocity
        # default drag is 0.5
        
        body.update(1.0) 
        
        # Expected:
        # Start Vel: (10, 0)
        # Dragged Vel: (10, 0) * (1 - 0.5) = (5, 0)
        # Position: (0,0) + (5,0) = (5, 0)
        
        self.assertEqual(body.position, pygame.math.Vector2(5, 0))
        self.assertEqual(body.velocity, pygame.math.Vector2(5, 0))
    
    def test_angular_velocity(self):
        """Angular velocity should rotate the body."""
        body = PhysicsBody(0, 0, 0)
        body.angular_velocity = 45
        body.angular_drag = 0  # Disable drag for predictable test
        
        body.update()
        
        self.assertEqual(body.angle, 45)


class TestPhysicsForces(unittest.TestCase):
    """Test force application and acceleration."""
    
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
    
    
    def test_apply_force_accelerates(self):
        """apply_force should add to acceleration based on mass."""
        body = PhysicsBody(0, 0)
        body.mass = 2.0
        body.drag = 0  # Disable drag
        
        force = pygame.math.Vector2(10, 0)
        body.apply_force(force)
        
        # Acceleration should be force / mass
        expected_accel = pygame.math.Vector2(5, 0)
        self.assertEqual(body.acceleration, expected_accel)
    
    def test_apply_force_accumulates(self):
        """Multiple apply_force calls should accumulate."""
        body = PhysicsBody(0, 0)
        body.mass = 1.0
        
        body.apply_force(pygame.math.Vector2(5, 0))
        body.apply_force(pygame.math.Vector2(3, 2))
        
        self.assertEqual(body.acceleration, pygame.math.Vector2(8, 2))
    
    def test_apply_force_updates_velocity(self):
        """After update, acceleration should affect velocity."""
        body = PhysicsBody(0, 0)
        body.mass = 1.0
        body.drag = 0  # Disable for test
        
        body.apply_force(pygame.math.Vector2(10, 0))
        body.update()
        
        # Velocity should have increased by acceleration
        self.assertGreater(body.velocity.x, 0)
        # Acceleration should be reset
        self.assertEqual(body.acceleration, pygame.math.Vector2(0, 0))


class TestPhysicsDirection(unittest.TestCase):
    """Test forward vector calculation."""
    
    def setUp(self):
        pygame.init()
    
    def tearDown(self):
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
    
    
    def test_forward_vector_angle_0(self):
        """Angle 0 should point right (1, 0)."""
        body = PhysicsBody(0, 0, 0)
        forward = body.forward_vector()
        
        self.assertAlmostEqual(forward.x, 1.0, places=5)
        self.assertAlmostEqual(forward.y, 0.0, places=5)
    
    def test_forward_vector_angle_90(self):
        """Angle 90 should point down (0, 1) in screen coords."""
        body = PhysicsBody(0, 0, 90)
        forward = body.forward_vector()
        
        self.assertAlmostEqual(forward.x, 0.0, places=5)
        self.assertAlmostEqual(forward.y, 1.0, places=5)
    
    def test_forward_vector_angle_180(self):
        """Angle 180 should point left (-1, 0)."""
        body = PhysicsBody(0, 0, 180)
        forward = body.forward_vector()
        
        self.assertAlmostEqual(forward.x, -1.0, places=5)
        self.assertAlmostEqual(forward.y, 0.0, places=5)
    
    def test_forward_vector_is_unit(self):
        """Forward vector should be unit length."""
        body = PhysicsBody(0, 0, 45)
        forward = body.forward_vector()
        
        self.assertAlmostEqual(forward.length(), 1.0, places=5)



class TestAbilityDrivenPhysics(unittest.TestCase):
    """Refactored Tests for Ability-Driven Physics."""
    

    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Mocking Ability System usage
        from game.simulation.entities.ship_physics import ShipPhysicsMixin
        from game.engine.physics import PhysicsBody
        
        class MockShip(PhysicsBody, ShipPhysicsMixin):
            def __init__(self):
                super().__init__(0, 0)
                self.mass = 1000
                self.drag = 0.5
                self.turn_speed = 90
                self.acceleration_rate = 100
                self.max_speed = 500
                self.current_speed = 0
                self.is_active = True
                self.is_thrusting = False
                self.engine_throttle = 1.0
                self.turn_throttle = 1.0
                self.stats = {}
                
            def get_total_ability_value(self, name, operational_only=True):
                if name == 'CombatPropulsion':
                    # Return a value that results in acceleration_rate being used or calculated?
                    # ShipPhysicsMixin uses this to CALCULATE current_accel.
                    # current_accel = (total_thrust * 2500) / mass^2
                    # If we want to control behavior, we return a thrust value.
                    return getattr(self, '_mock_thrust', 100000) 
                return 0
                
        self.ship = MockShip()
        
    def tearDown(self):
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
        
    def test_ability_driven_thrust(self):
        """Test that physics uses stats derived from CombatPropulsion abilities."""
        self.ship.angle = 0 # Facing Right
        self.ship._mock_thrust = 200000 # High thrust
        
        # Apply Thrust using Mixin method
        self.ship.thrust_forward()
        self.ship.update_physics_movement()
        
        # Velocity should be > 0
        self.assertGreater(self.ship.current_speed, 0)
        self.assertGreater(self.ship.velocity.x, 0)
        
    def test_mass_dampening(self):
        """Test that higher mass reduces effective response."""
        # Baseline
        self.ship.mass = 100
        self.ship._mock_thrust = 100000
        self.ship.current_speed = 0
        self.ship.thrust_forward()
        self.ship.update_physics_movement()
        fast_speed = self.ship.current_speed
        
        # High Mass
        self.ship.mass = 10000
        self.ship.current_speed = 0
        self.ship.velocity = pygame.math.Vector2(0,0)
        self.ship.thrust_forward()
        self.ship.update_physics_movement()
        slow_speed = self.ship.current_speed
        
        self.assertGreater(fast_speed, slow_speed)


if __name__ == '__main__':
    unittest.main()


