import unittest
import math
from tests.test_combat_targeting import TestCombatTargeting  # Reuse logic if needed, or just standard import

class TestFiringArcLogic(unittest.TestCase):
    """
    Tests for firing arc calculation logic.
    Replaces the manual test_firing_arc.py script.
    """

    def check_arc(self, ship_angle, facing_angle, arc, ship_pos, target_pos):
        """
        Helper method to reproduce the check_arc logic and return the result.
        Returns check_arc status as boolean.
        """
        # 1. Global Component Facing
        comp_facing = (ship_angle + facing_angle) % 360
        
        # 2. Aim Vector
        aim_vec = (target_pos[0] - ship_pos[0], target_pos[1] - ship_pos[1])
        
        # 3. Aim Angle
        # math.atan2(y, x) -> In Y-Down: (0, -1) -> -90 = 270.
        aim_angle = math.degrees(math.atan2(aim_vec[1], aim_vec[0])) % 360
        
        # 4. Diff
        diff = (aim_angle - comp_facing + 180) % 360 - 180
        
        # 5. Check
        return abs(diff) <= (arc / 2)

    def test_forward_fire(self):
        # Scenario 1: Forward Fire (Working)
        # Ship Right(0), Target Right, Weapon Forward(0)
        result = self.check_arc(0, 0, 45, (0,0), (100, 0))
        self.assertTrue(result, "Target directly ahead should be in arc")

    def test_broadside_fire(self):
        # Scenario 2: Broadside
        # Ship Left (180). Weapon Starboard (90). Total Up (270). Target Up (0, -100).
        result = self.check_arc(180, 90, 45, (0,0), (0, -100))
        self.assertTrue(result, "Target in broadside arc should be valid")

    def test_broadside_miss(self):
        # Scenario 3: Broadside Miss
        # Ship Left (180). Weapon Starboard (90). Total Up (270). Target Down (0, 100).
        result = self.check_arc(180, 90, 45, (0,0), (0, 100))
        self.assertFalse(result, "Target opposite to broadside should be invalid")

    def test_user_report_miss(self):
        # Scenario 4: User Report (90/270)
        # Ship Right (0). Weapon 90. Target in Front (Right).
        # This was marked as "SHOULD Fail" in the original script.
        result = self.check_arc(0, 90, 45, (0,0), (100, 0))
        self.assertFalse(result, "Target out of side arc should be invalid")

    def test_half_angle_restriction(self):
        # Scenario 5: Half Angle Restriction (New Behavior)
        # Arc 45 (Total). Target at 30 degrees.
        # Old behavior: 30 <= 45 (Hit).
        # New behavior: 30 <= 22.5 (Miss).
        result = self.check_arc(0, 0, 45, (0,0), (100, 57)) # tan(30) ~ 0.57
        self.assertFalse(result, "Target at 30 deg should be outside 45 deg total arc (±22.5)")
