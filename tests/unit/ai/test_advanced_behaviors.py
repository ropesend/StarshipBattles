import unittest
from unittest.mock import MagicMock
import pygame

from game.ai.behaviors import KiteBehavior, AttackRunBehavior, OrbitBehavior
from game.ai.controller import AIController

class TestAdvancedBehaviors(unittest.TestCase):
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
            
        self.mock_controller = MagicMock()
        self.mock_controller.ship.position = pygame.math.Vector2(0, 0)
        self.mock_controller.ship.max_weapon_range = 1000
        self.mock_controller.ship.radius = 50
        
        self.target = MagicMock()
        self.target.position = pygame.math.Vector2(2000, 0) # Far away
        self.target.velocity = pygame.math.Vector2(0, 0)

    def tearDown(self):
        pygame.quit()
        super().tearDown()
        
    def test_kite_behavior(self):
        """Test KiteBehavior navigation logic."""
        kite = KiteBehavior(self.mock_controller)
        
        # Strategy: Engage at max range
        strategy = {'engage_distance': 'max_range'}
        
        

        # Setup mock return values explicitly to avoid odd collisions
        self.mock_controller.get_engage_distance_multiplier = MagicMock(return_value=1.0)
        self.mock_controller.check_avoidance = MagicMock(return_value=None)
        
        # Scenario 1: Target too far (2000 > 1000)
        # Should navigate TO target
        self.target.position = pygame.math.Vector2(2000, 0)
        # Scenario 1: Target too far (2000 > 1000)
        # Should navigate TO target
        self.target.position = pygame.math.Vector2(2000, 0)
        kite.update(self.target, strategy)



        
        # Check navigate_to call
        # navigate_to(target_pos, stop_dist=opt_dist, precise=True)
        self.mock_controller.navigate_to.assert_called_with(
            self.target.position, 
            stop_dist=1000.0, # max_range * 1.0
            precise=True
        )
        
        # Scenario 2: Target too close (500 < 1000)
        self.target.position = pygame.math.Vector2(500, 0)
        
        kite.update(self.target, strategy)
        
        # Should navigate AWAY (Kite position)
        args, _ = self.mock_controller.navigate_to.call_args
        dest = args[0] # target_pos
        self.assertAlmostEqual(dest.x, -500.0, delta=1.0)
        self.assertEqual(dest.y, 0)

    def test_attack_run_behavior(self):
        """Test AttackRun (Boom and Zoom) logic."""
        attack = AttackRunBehavior(self.mock_controller)
        attack.enter() # Reset state
        
        # Config
        strategy = {
            'attack_run_behavior': {
                'approach_distance': 0.2, # 200 units
                'retreat_distance': 0.8, # 800 units
                'retreat_duration': 2.0
            }
        }
        
        # 1. Approach Phase
        self.target.position = pygame.math.Vector2(2000, 0)
        
        attack.update(self.target, strategy)
        
        self.assertEqual(attack.attack_state, 'approach')
        # Should drive TO target
        self.mock_controller.navigate_to.assert_called()
        
        # 2. Trigger Retreat
        # Distance < approach (200 * 1.5 = 300 hysteresis)
        self.target.position = pygame.math.Vector2(100, 0)
        
        attack.update(self.target, strategy)
        
        self.assertEqual(attack.attack_state, 'retreat')
        self.assertEqual(attack.attack_timer, 2.0)
        
        # 3. Retreat Phase
        # Mock timer decrement implicitly handled by update call? No, logic decrements it.
        # We just need to check if it calls navigate_to with retreat vector
        self.mock_controller.navigate_to.reset_mock()
        attack.update(self.target, strategy)
        
        self.assertLess(attack.attack_timer, 2.0)
        self.mock_controller.navigate_to.assert_called()
        
    def test_orbit_behavior(self):
        """Test Orbit circling logic."""
        orbit = OrbitBehavior(self.mock_controller)
        strategy = {'orbit_distance': 500}
        
        self.mock_controller.ship.position = pygame.math.Vector2(600, 0)
        self.target.position = pygame.math.Vector2(0, 0)
        # Dist 600 (Too far)
        
        orbit.update(self.target, strategy)
        
        # Radial: Ship-Target = (600,0) -> (1,0) (Actually vec_to_target is -600... wait)
        # vec_to_target = Target(0) - Ship(600) = (-600, 0) -> norm (-1, 0) (Left)
        # Tangent: (-y, x) -> (0, -1) (Up)
        # Too far (600 > 550): Move dir = Tangent + Radial*0.5
        # Tangent(0,-1) + Radial(-1,0)*0.5 = (-0.5, -1)
        # Normalized...
        
        args, _ = self.mock_controller.navigate_to.call_args
        dest = args[0]
        # Destination should have negative X (inward) and negative Y (ccw orbit)
        rel_move = dest - self.mock_controller.ship.position
        
        self.assertLess(rel_move.x, 0) # Moving Left (Inward)
        self.assertLess(rel_move.y, 0) # Moving Up (Orbit)

    def test_formation_integrity__ability_check(self):
        """Verify formation breakdown checks operational propulsion abilities."""
        # This logic is in AIController._check_formation_integrity
        # But we can test it by manually creating a controller or moving logic to mixin?
        # It's a method on AIController. Let's instanciate a real one with mocks.

        real_controller = AIController(self.mock_controller.ship, MagicMock(), 0)

        # Setup Ship with Ability-based Logic
        real_controller.ship.in_formation = True
        real_controller.ship.formation_master = MagicMock()

        # Case 1: Ability Healthy
        comp = MagicMock()
        comp.has_ability.side_effect = lambda x: x == 'CombatPropulsion'
        comp.current_hp = 100
        comp.max_hp = 100

        # Mock the Ship helper methods to return our component
        real_controller.ship.get_components_by_ability = MagicMock(return_value=[comp])

        real_controller._check_formation_integrity()
        self.assertTrue(real_controller.ship.in_formation)

        # Case 2: Ability Damaged
        comp.current_hp = 50

        real_controller._check_formation_integrity()
        self.assertFalse(real_controller.ship.in_formation)

if __name__ == '__main__':
    unittest.main()
