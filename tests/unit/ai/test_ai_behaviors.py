import unittest
import sys
import os
import pygame
import math
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.ai.behaviors import KiteBehavior, FormationBehavior, RamBehavior

class TestKiteBehavior(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.ship = MagicMock()
        self.target = MagicMock()
        self.controller.ship = self.ship
        
        # Default mock values
        self.ship.position = pygame.math.Vector2(0, 0)
        self.ship.max_weapon_range = 1000
        self.target.position = pygame.math.Vector2(2000, 0) # Far away initially
        
        self.behavior = KiteBehavior(self.controller)
        self.strategy = {'avoid_collisions': True}
        
        # Ensure check_avoidance returns None by default so it doesn't trigger
        self.controller.check_avoidance.return_value = None

    def tearDown(self):
        pygame.quit()
        super().tearDown()

    def test_opt_dist_calculation(self):
        """Verify optimal distance calculation based on engage multiplier."""
        # Setup controller to return specific multiplier
        self.controller.get_engage_distance_multiplier.return_value = 0.8
        
        # Run update
        self.behavior.update(self.target, self.strategy)
        
        # Check that get_engage_distance_multiplier was called
        self.controller.get_engage_distance_multiplier.assert_called_with(self.strategy)
        
        # Expected opt_dist is 1000 * 0.8 = 800
        # Since dist (2000) > opt_dist (800), it should call navigate_to with stop_dist=opt_dist
        self.controller.navigate_to.assert_called_with(
            self.target.position, 
            stop_dist=800.0, 
            precise=True
        )

    def test_opt_dist_min_clamp(self):
        """Verify optimal distance is clamped to minimum 150."""
        self.controller.get_engage_distance_multiplier.return_value = 0.1
        # max_range 1000 * 0.1 = 100. Should clamp to 150.
        
        self.behavior.update(self.target, self.strategy)
        
        self.controller.navigate_to.assert_called_with(
            self.target.position, 
            stop_dist=150, 
            precise=True
        )

    def test_branching_close_in(self):
        """Behavior should close in when distance > optimal."""
        self.controller.get_engage_distance_multiplier.return_value = 0.5 # opt_dist = 500
        self.target.position = pygame.math.Vector2(1000, 0) # dist = 1000
        
        self.behavior.update(self.target, self.strategy)
        
        # Should navigate TO target with stop_dist = opt_dist
        self.controller.navigate_to.assert_called_with(
            self.target.position,
            stop_dist=500.0,
            precise=True
        )

    def test_branching_kite_maintain(self):
        """Behavior should kite (back away) when distance <= optimal."""
        self.controller.get_engage_distance_multiplier.return_value = 0.5 # opt_dist = 500
        self.target.position = pygame.math.Vector2(300, 0) # dist = 300 (too close)
        
        # Vector from target to ship is (-300, 0) if ship is at 0,0 and target at 300,0?
        # Wait, ship is at 0,0. Target at 300,0.
        # Vector ship - target = (-300, 0). Normalize -> (-1, 0).
        # Kite pos = target.position (300,0) + (-1,0 * 500) = (300-500, 0) = (-200, 0).
        # Wait, let's re-read the code logic.
        # vec = ship.pos - target.pos
        # kite_pos = target.position + vec.normalize() * opt_dist
        
        self.behavior.update(self.target, self.strategy)
        
        # Calculate expected position
        # ship(0,0), target(300,0) -> vec(-300, 0) -> norm(-1, 0)
        # kite_pos = (300,0) + (-1, 0)*500 = (-200, 0)
        
        # Verify call
        args, kwargs = self.controller.navigate_to.call_args
        target_pos = args[0]
        self.assertEqual(target_pos, pygame.math.Vector2(-200, 0))
        self.assertEqual(kwargs['stop_dist'], 0)
        self.assertEqual(kwargs['precise'], True)

    def test_collision_avoidance_trigger(self):
        """Verify collision avoidance overrides kiting logic."""
        self.controller.check_avoidance.return_value = pygame.math.Vector2(50, 50)
        
        self.behavior.update(self.target, self.strategy)
        
        self.controller.check_avoidance.assert_called()
        self.controller.navigate_to.assert_called_with(
            pygame.math.Vector2(50, 50),
            stop_dist=0,
            precise=False
        )

    def test_collision_avoidance_disabled(self):
        """Verify avoidance check is skipped if strategy disables it."""
        self.strategy['avoid_collisions'] = False
        self.controller.get_engage_distance_multiplier.return_value = 1.0
        
        self.behavior.update(self.target, self.strategy)
        
        self.controller.check_avoidance.assert_not_called()


class TestFormationBehavior(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.ship = MagicMock()
        self.master = MagicMock()
        
        self.controller.ship = self.ship
        self.ship.formation_master = self.master
        
        # Defaults
        self.ship.position = pygame.math.Vector2(100, 100)
        self.ship.angle = 0
        self.ship.radius = 10
        self.ship.acceleration_rate = 5
        self.ship.turn_speed = 10
        self.ship.turn_throttle = 1.0
        self.ship.max_speed = 100
        self.ship.formation_offset = pygame.math.Vector2(50, 0)
        self.ship.formation_rotation_mode = 'relative'
        
        self.master.is_alive = True
        self.master.is_derelict = False
        self.master.position = pygame.math.Vector2(0, 0) # Master at 0,0
        self.master.angle = 0
        self.master.current_speed = 0
        self.master.is_thrusting = False
        self.master.engine_throttle = 0
        
        self.behavior = FormationBehavior(self.controller)
        self.strategy = {}

    def test_abandon_if_master_invalid(self):
        """Should set in_formation False if master dead or missing."""
        self.master.is_alive = False
        self.behavior.update(None, self.strategy)
        self.assertEqual(self.ship.in_formation, False)

    def test_target_pos_fixed_rotation(self):
        """Verify target position calculation for fixed rotation."""
        self.ship.formation_rotation_mode = 'fixed'
        self.ship.formation_offset = pygame.math.Vector2(50, 50)
        self.master.position = pygame.math.Vector2(100, 100)
        self.master.angle = 90 # Should ignore this for offset
        
        # We need to simulate the ship being far away so it hits the "Navigate" logic
        # allowing us to verify the target_pos calculation passed to navigate_to is NOT affected by master angle
        # Actually logic splits: if far -> navigate. if close -> drift.
        # Let's put ship far away.
        self.ship.position = pygame.math.Vector2(5000, 5000)
        
        self.behavior.update(None, self.strategy)
        
        # Navigate logic uses prediction (master pos + velocity predict + offset)
        # Master speed 0 -> prediction is 0.
        # So target = master.pos (100,100) + offset (50,50) = 150, 150.
        
        args, _ = self.controller.navigate_to.call_args
        target_pos = args[0]
        self.assertEqual(target_pos, pygame.math.Vector2(150, 150))

    def test_target_pos_relative_rotation(self):
        """Verify target position calculation for relative rotation."""
        self.ship.formation_rotation_mode = 'relative'
        # Offset is (50, 0) relative to master. 
        self.ship.formation_offset = pygame.math.Vector2(50, 0)
        self.master.position = pygame.math.Vector2(100, 100)
        self.master.angle = 90 # Facing down
        
        # Relative means offset rotates with master. (50, 0) rotated 90 deg -> (0, 50).
        # Target should be (100, 100) + (0, 50) = (100, 150).
        
        self.ship.position = pygame.math.Vector2(5000, 5000) # Force navigate logic
        
        self.behavior.update(None, self.strategy)
        
        args, _ = self.controller.navigate_to.call_args
        target_pos = args[0]
        self.assertAlmostEqual(target_pos.x, 100)
        self.assertAlmostEqual(target_pos.y, 150)

    def test_drift_logic_correction(self):
        """Verify small error triggers drift correction logic."""
        # Set up scenario where we are CLOSE to target spot
        self.master.position = pygame.math.Vector2(0, 0)
        self.master.angle = 0
        self.ship.formation_offset = pygame.math.Vector2(50, 0)
        # Target is (50,0). Ship is at (55, 0). Error 5.
        self.ship.position = pygame.math.Vector2(55, 0) 
        
        # Drift threshold check: 
        # diameter = radius(10)*2 = 20. 
        # accel(5)*1.2 = 6.
        # Threshold = 20. Dist 5 is <= 20. -> Enter Drift Logic.
        
        self.behavior.update(None, self.strategy)
        
        # Verify navigate_to NOT called
        self.controller.navigate_to.assert_not_called()
        
        # Verify position updated (spring correction)
        # Future master pos = 0,0. Future offset = 50,0. Future target = 50,0.
        # Vec to spot = (50,0) - (55,0) = (-5, 0).
        # Correction = (-5, 0) * 0.2 = (-1, 0).
        # New pos should be (55,0) + (-1,0) = (54,0).
        self.assertTrue(self.ship.position.x < 55) # Moved left
        self.assertEqual(self.ship.position.y, 0)

    def test_velocity_sync(self):
        """Verify engine throttle is synced with master."""
        # Setup drift scenario
        self.master.position = pygame.math.Vector2(0, 0)
        self.ship.position = pygame.math.Vector2(50, 0) # Target spot
        self.ship.formation_offset = pygame.math.Vector2(50, 0)

        # Master is moving
        self.master.is_thrusting = True
        self.master.max_speed = 200
        self.master.engine_throttle = 0.5
        # Master current target speed = 100.
        
        self.ship.max_speed = 100
        
        self.behavior.update(None, self.strategy)
        
        # Ship throttle should be master_speed (100) / ship_max (100) = 1.0
        self.assertEqual(self.ship.engine_throttle, 1.0)
        self.ship.thrust_forward.assert_called()


class TestRamBehavior(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.behavior = RamBehavior(self.controller)
        self.target = MagicMock()
        self.target.position = pygame.math.Vector2(100, 100)
        self.strategy = {}

    def test_ram_parameters(self):
        """Verify RamBehavior calls navigate_to with correct params."""
        self.behavior.update(self.target, self.strategy)
        
        self.controller.navigate_to.assert_called_with(
            self.target.position,
            stop_dist=0,
            precise=False
        )

if __name__ == '__main__':
    unittest.main()
