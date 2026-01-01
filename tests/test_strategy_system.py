import unittest
import pygame
import os
import json
import sys

# Add root to path
sys.path.append(os.getcwd())

from unittest.mock import MagicMock, patch
from ai import StrategyManager, TargetEvaluator, load_combat_strategies, STRATEGY_MANAGER

class TestStrategySystem(unittest.TestCase):
    def setUp(self):
        # Setup mock StrategyManager with test data
        self.manager = StrategyManager()
        # Point to tests/data which we populated earlier
        test_data_path = os.path.join(os.getcwd(), "tests", "data")
        self.manager.load_data(
            test_data_path, 
            targeting_file="test_targeting_policies.json", 
            movement_file="test_movement_policies.json", 
            strategy_file="test_combat_strategies.json"
        )
        
    def test_load_data(self):
        """Verify data loading from test files."""
        # Check if test policies loaded
        self.assertIn('test_policy_1', self.manager.targeting_policies)
        self.assertIn('test_move_kite', self.manager.movement_policies)
        self.assertIn('test_strat_simple', self.manager.strategies)
        
        strat = self.manager.get_strategy('test_strat_simple')
        self.assertEqual(strat['name'], "Test Strategy Simple")
        
    def test_resolve_strategy(self):
        """Verify strategy resolution links policies correctly."""
        resolved = self.manager.resolve_strategy('test_strat_simple')
        self.assertEqual(resolved['definition']['name'], "Test Strategy Simple")
        self.assertEqual(resolved['targeting']['name'], "Test Policy 1")
        self.assertEqual(resolved['movement']['behavior'], "kite")
        
    def test_target_evaluator_nearest(self):
        """Verify 'nearest' rule scoring."""
        # Mock ships
        me = MagicMock()
        me.position = pygame.math.Vector2(0, 0)
        
        target_near = MagicMock()
        target_near.position = pygame.math.Vector2(100, 0)
        
        target_far = MagicMock()
        target_far.position = pygame.math.Vector2(500, 0)
        
        rules = [{'type': 'nearest', 'weight': 100}]
        
        # Lower distance should act as penalty if we subtract dist*weight?
        # In current logic: val = -dist * weight. So closer (smaller dist) is less negative (higher score).
        
        score_near = TargetEvaluator.evaluate(me, target_near, rules)
        score_far = TargetEvaluator.evaluate(me, target_far, rules)
        
        self.assertGreater(score_near, score_far, "Closer target should have higher score")
        
    def test_target_evaluator_complex(self):
        """Verify complex rule interactions."""
        me = MagicMock()
        me.position = pygame.math.Vector2(0, 0)
         
        # Target 1: Far but has weapons
        t1 = MagicMock()
        t1.position = pygame.math.Vector2(1000, 0)
        t1.mass = 100
        # Mock has_weapons logic: checks components damage attribute
        # We need to mock the layer structure
        c1 = MagicMock()
        c1.damage = 10
        t1.layers = {'core': {'components': [c1]}}
        
        # Target 2: Near but no weapons
        t2 = MagicMock()
        t2.position = pygame.math.Vector2(100, 0)
        t2.mass = 100
        t2.layers = {'core': {'components': []}}
        
        # Rules: has_weapons (1000) > distance (factor -1)
        # T1 score ~= 1000 - 1000 = 0
        # T2 score ~= 0 - 100 = -100
        # T1 should win
        
        rules = [
            {"type": "has_weapons", "weight": 1000},
            {"type": "distance", "factor": -1}
        ]
        
        score_t1 = TargetEvaluator.evaluate(me, t1, rules)
        score_t2 = TargetEvaluator.evaluate(me, t2, rules)
        
        self.assertGreater(score_t1, score_t2, "Target with weapons should be preferred despite distance")

if __name__ == '__main__':
    unittest.main()
