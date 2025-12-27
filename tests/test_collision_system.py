import unittest
from unittest.mock import MagicMock, patch
from pygame.math import Vector2
import sys
import os

# Ensure the root directory is in python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from collision_system import CollisionSystem

class TestCollisionSystem(unittest.TestCase):
    def setUp(self):
        self.collision_system = CollisionSystem()
        
    def test_beam_weapon_raycasting(self):
        """
        Unit test process_beam_attack with hardcoded vectors.
        Verify hit detection math: direct hit, near miss, range limits.
        """
        # Setup source and target
        source_pos = Vector2(0, 0)
        
        # Mocking generic object for Target since we don't want to rely on Ship class complexities
        target = MagicMock()
        target.position = Vector2(200, 0)
        target.radius = 20
        target.is_alive = True
        
        # Mock component for hit chance (always hit)
        mock_component = MagicMock()
        mock_component.calculate_hit_chance.return_value = 1.0
        
        recent_beams = []
        
        # Case 1: Direct Hit
        attack_hit = {
            'origin': source_pos,
            'direction': Vector2(1, 0), # Directly at target (200, 0)
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        with patch('random.random', return_value=0.0):
             self.collision_system.process_beam_attack(attack_hit, recent_beams)
             target.take_damage.assert_called_with(10)
        
        # Verify beam recorded
        self.assertEqual(len(recent_beams), 1)
        
        # Case 2: Near Miss
        target.reset_mock()
        aim_vec = Vector2(200, 21).normalize()
        
        attack_miss = {
            'origin': source_pos,
            'direction': aim_vec,
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        with patch('random.random', return_value=0.0):
             self.collision_system.process_beam_attack(attack_miss, recent_beams)
             target.take_damage.assert_not_called()
        
        # Case 3: Range Limits
        target.reset_mock()
        attack_range = {
            'origin': source_pos,
            'direction': Vector2(1, 0),
            'range': 150, 
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        with patch('random.random', return_value=0.0):
             self.collision_system.process_beam_attack(attack_range, recent_beams)
             target.take_damage.assert_not_called()

    def test_ramming_logic(self):
        """
        test process_ramming.
        """
        # Setup
        # Mock Ships
        ships = []
        
        rammer = MagicMock()
        rammer.name = "Rammer"
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.ai_strategy = 'kamikaze'
        rammer.is_alive = True
        rammer.hp = 50
        
        target = MagicMock()
        target.name = "Target"
        target.position = Vector2(15, 0) # Colliding
        target.radius = 10
        target.is_alive = True
        target.hp = 100
        
        rammer.current_target = target
        
        ships = [rammer, target]
        
        logger = MagicMock()
        
        # Case A: Rammer HP (50) < Target HP (100)
        self.collision_system.process_ramming(ships, logger)
        
        rammer.take_damage.assert_called_with(50 + 9999)
        target.take_damage.assert_called_with(25.0) # 50 * 0.5
        
        # Case B: Rammer HP (100) > Target HP (50)
        rammer.reset_mock()
        target.reset_mock()
        rammer.hp = 100
        target.hp = 50
        
        self.collision_system.process_ramming(ships, logger)
        
        target.take_damage.assert_called_with(50 + 9999)
        rammer.take_damage.assert_called_with(25.0)

if __name__ == '__main__':
    unittest.main()
