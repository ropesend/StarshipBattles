
import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import load_components, get_all_components, create_component, SeekerWeapon

class TestSeekerRange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")

    def test_seeker_initial_range_is_80_percent(self):
        """Test that seeker weapon range is 80% of speed * endurance."""
        missile = create_component('capital_missile')
        
        self.assertIsInstance(missile, SeekerWeapon)
        
        expected_straight_range = missile.projectile_speed * missile.endurance
        expected_range = int(expected_straight_range * 0.8)
        
        self.assertEqual(missile.range, expected_range, 
            f"Range should be {expected_range} (80% of {expected_straight_range}), got {missile.range}")
            
    def test_seeker_range_with_modifier(self):
        """Test that range modifier works on top of 80% calculation."""
        # Seeker range = (speed * endurance) * 0.8 * modifier
        missile = create_component('capital_missile')
        
        # We need a range modifier. 'range_mount' level 1 gives 2^1 = 2x range.
        # Check standard modifiers from test_components: 'range_mount' level 1 => 2x range?
        # Actually in test_components: "Range mount level 1 should increase mass by 3.5x."
        # And "Range mount level 2 should give 4x range."
        # component_modifiers.py: stats['range_mult'] *= 2.0 ** level.
        # So level 1 = 2.0x range.
        
        from components import load_modifiers
        load_modifiers("data/modifiers.json")
        
        # Note: 'range_mount' is no longer allowed on Seekers. We use 'seeker_endurance' for range extension.
        # 'seeker_endurance' value acts as a direct multiplier for endurance, which scales range.
        missile.add_modifier('seeker_endurance', 2.0)
        
        straight_range = missile.projectile_speed * missile.endurance
        # Since we applied 2.0 multiplier to endurance, missile.endurance is already doubled inside the component logic.
        # The formula is (Speed * Endurance) * 0.8.
        # So we expect (Speed * (BaseEndurance * 2.0)) * 0.8.
        
        # Let's recalculate expected based on base values to be sure
        base_endurance = missile.data.get('endurance', 5.0)
        expected_range = int((missile.projectile_speed * (base_endurance * 2.0)) * 0.8)
        
        self.assertEqual(missile.range, expected_range,
             f"Range with modifier should be {expected_range}, got {missile.range}")

if __name__ == '__main__':
    unittest.main()
