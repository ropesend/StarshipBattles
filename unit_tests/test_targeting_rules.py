
import unittest
from unittest.mock import MagicMock
import pygame
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import TargetEvaluator, AIController
from game_constants import AttackType

class TestTargetingRules(unittest.TestCase):
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
            
        self.ship = MagicMock()
        self.ship.position = pygame.math.Vector2(0, 0)
        self.ship.angle = 0
        self.ship.team_id = 0
        
        self.target_near = MagicMock()
        self.target_near.position = pygame.math.Vector2(100, 0)
        self.target_near.mass = 100
        self.target_near.velocity = pygame.math.Vector2(0,0)
        
        self.target_far = MagicMock()
        self.target_far.position = pygame.math.Vector2(1000, 0)
        self.target_far.mass = 500
        
    def test_rule_nearest(self):
        """Test 'nearest' rule scores closer targets higher."""
        # weight=1 => val = -dist
        rule = {'type': 'nearest', 'weight': 1}
        rules = [rule]
        
        score_near = TargetEvaluator.evaluate(self.ship, self.target_near, rules)
        score_far = TargetEvaluator.evaluate(self.ship, self.target_far, rules)
        
        # Near (-100) > Far (-1000)
        self.assertGreater(score_near, score_far)
        
    def test_rule_most_damaged(self):
        """Test 'most_damaged' rule scores lower HP% higher."""
        # Using a rule with weight > 0
        rule = {'type': 'most_damaged', 'weight': 1}
        rules = [rule]
        
        # Mock HP% on targets via AIController._stat_get_hp_percent
        # Since _stat_get_hp_percent is static and complex, let's mock the targets to look like ships 
        # or mock the static method if possible.
        # However, TargetEvaluator calls AIController._stat_get_hp_percent directly.
        # Easier to mock the return value if we could, but it's hardwired.
        # Let's mock the component structures on the targets.
        
        # Target 1: 10/100 HP (10%)
        t1 = MagicMock()
        t1.layers = {
            'core': {
                'max_hp_pool': 100,
                'hp_pool': 10
            }
        }
        
        # Target 2: 90/100 HP (90%)
        t2 = MagicMock()
        t2.layers = {
            'core': {
                'max_hp_pool': 100,
                'hp_pool': 90
            }
        }
        
        # Rule: val = -hp_pct * weight * 100
        # T1 Score = -0.1 * 100 = -10
        # T2 Score = -0.9 * 100 = -90
        # T1 (Most damaged) should have higher score
        
        score_1 = TargetEvaluator.evaluate(self.ship, t1, rules)
        score_2 = TargetEvaluator.evaluate(self.ship, t2, rules)
        
        self.assertGreater(score_1, score_2)
        
    def test_rule_pdc_arc(self):
        """Test 'pdc_arc' rule filters by angle and type."""
        # Rule expects target type to be 'missile'
        rule = {'type': 'pdc_arc', 'weight': 1, 'required': True}
        rules = [rule]
        
        missile = MagicMock()
        missile.type = AttackType.MISSILE
        missile.position = pygame.math.Vector2(100, 0) # Directly ahead
        
        ship_not_missile = MagicMock()
        ship_not_missile.type = 'Ship'
        ship_not_missile.position = pygame.math.Vector2(100, 0)
        
        # Case 1: Non-missile target passes or is ignored?
        # Logic: if is_missile check...
        # "if is_missile: check arc... else: pass"
        # So non-missile gets score 0 (neutral).
        
        score_ship = TargetEvaluator.evaluate(self.ship, ship_not_missile, rules)
        self.assertEqual(score_ship, 0)
        
        # Case 2: Missile in arc. Need to mock ship's PDC ability logic.
        # TargetEvaluator calls AIController._stat_is_in_pdc_arc(ship, target)
        # We need to set up self.ship with a mock weapon in arc.
        
        # Setup Ship with PDC Weapon
        layer = {'components': []}
        self.ship.layers = {'outer': layer}
        self.ship.angle = 0
        
        # Mock Component
        comp = MagicMock()
        comp.has_ability.side_effect = lambda x: True if x == 'WeaponAbility' else False
        comp.is_active = True
        comp.has_pdc_ability.return_value = True
        
        # Mock WeaponAbility
        ab = MagicMock()
        ab.range = 500
        ab.facing_angle = 0
        ab.firing_arc = 90
        comp.get_ability.return_value = ab
        
        layer['components'].append(comp)
        
        # Now Check Missile (In Arc)
        score_missile = TargetEvaluator.evaluate(self.ship, missile, rules)
        self.assertGreater(score_missile, 0) # Should get weight val
        
        # Case 3: Missile Out of Arc (Behind)
        missile.position = pygame.math.Vector2(-100, 0)
        score_missile_out = TargetEvaluator.evaluate(self.ship, missile, rules)
        self.assertEqual(score_missile_out, -float('inf')) # Required rule failed
        
    def test_rule_required_flag(self):
        """Test that failure of a required rule returns -inf."""
        # Example: 'has_weapons'
        rule = {'type': 'has_weapons', 'required': True, 'weight': 1}
        rules = [rule]
        
        # Target with no weapons
        target = MagicMock()
        # Mocking recursive attribute access for components... tricky.
        # TargetEvaluator iterates: for layer in getattr(candidate, 'layers'...
        target.layers = {} # No components
        
        score = TargetEvaluator.evaluate(self.ship, target, rules)
        self.assertEqual(score, -float('inf'))

    def test_secondary_targeting(self):
        """Test secondary targeting logic."""
        # Mock AIController partial for test
        # We don't want the full grid query, just the filtering logic.
        # But find_secondary_targets is an instance method that calls grid.
        # We can construct a controller with a mock grid.
        
        mock_grid = MagicMock()
        controller = AIController(self.ship, mock_grid, enemy_team_id=1)
        
        t1 = MagicMock(); t1.team_id=1; t1.is_alive=True; t1.name="t1"
        t2 = MagicMock(); t2.team_id=1; t2.is_alive=True; t2.name="t2"
        
        self.ship.current_target = t1
        self.ship.max_targets = 2
        
        mock_grid.query_radius.return_value = [self.ship, t1, t2]
        
        # Strategy mock logic is complex (get_resolved_strategy).
        # We can mock get_resolved_strategy on the controller instance.
        controller.get_resolved_strategy = MagicMock(return_value={
            'targeting': {'rules': [{'type': 'nearest', 'weight': 1}]}
        })
        
        # Helper evaluator mock to avoid layout issues?
        # Or just ensure targets have positions so evaluators work.
        t1.position = pygame.math.Vector2(100,0)
        t2.position = pygame.math.Vector2(200,0)
        self.ship.layers = {}; t1.layers={}; t2.layers={}
        
        secondary = controller.find_secondary_targets()
        
        # Should return [t2] because t1 is current_target
        self.assertEqual(len(secondary), 1)
        self.assertEqual(secondary[0], t2)

if __name__ == '__main__':
    unittest.main()
