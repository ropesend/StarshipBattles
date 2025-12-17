import unittest
import pygame
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics import PhysicsBody

class TestPhysics(unittest.TestCase):
    def test_initialization(self):
        body = PhysicsBody(100, 200, 90)
        self.assertEqual(body.position, pygame.math.Vector2(100, 200))
        self.assertEqual(body.angle, 90)
        self.assertEqual(body.velocity, pygame.math.Vector2(0, 0))

    def test_update_movement(self):
        """Test basic velocity application."""
        body = PhysicsBody(0, 0)
        body.velocity = pygame.math.Vector2(10, 0)
        # Update delta time 1.0s
        # PhysicsBody implementation:
        # velocity *= (1 - drag * dt)
        # position += velocity * dt
        # default drag is 0.5
        
        body.update(1.0) 
        
        # Expected:
        # Start Vel: (10, 0)
        # Dragged Vel: (10, 0) * (1 - 0.5*1.0) = (5, 0)
        # Position: (0,0) + (5,0) * 1.0 = (5, 0)
        
        self.assertEqual(body.position, pygame.math.Vector2(5, 0))
        self.assertEqual(body.velocity, pygame.math.Vector2(5, 0))

if __name__ == '__main__':
    unittest.main()
