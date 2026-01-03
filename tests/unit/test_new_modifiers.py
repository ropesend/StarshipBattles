import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.simulation.components.component import Component, Modifier, MODIFIER_REGISTRY
from game.simulation.components.modifiers import apply_modifier_effects, ModifierEffects

class TestNewModifiers(unittest.TestCase):

    def setUp(self):
        # Base stats for testing
        self.stats = {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'range_mult': 1.0,
            'cost_mult': 1.0,
            'consumption_mult': 1.0,
            'reload_mult': 1.0,
            'endurance_mult': 1.0,
            'projectile_hp_mult': 1.0,
            'projectile_damage_mult': 1.0,
            'projectile_stealth_level': 0.0,
            'crew_req_mult': 1.0,
            'properties': {}
        }

    def test_rapid_fire_scaling(self):
        # "It the firing rate is doubled the mass should be tripled."
        # rate = 2.0. reload_mult = 0.5. Mass increase = (2.0 - 1.0) * 2.0 = 2.0. Total Mass = 1.0 + 2.0 = 3.0.
        ModifierEffects.rapid_fire(2.0, self.stats)
        
        self.assertAlmostEqual(self.stats['reload_mult'], 0.5)
        self.assertAlmostEqual(self.stats['mass_mult'], 3.0)

        # 3x fire rate -> 5x mass? (Inc = 2 * 2 = 4. 1+4=5)
        self.setUp() # Reset
        ModifierEffects.rapid_fire(3.0, self.stats)
        self.assertAlmostEqual(self.stats['reload_mult'], 1.0/3.0)
        self.assertAlmostEqual(self.stats['mass_mult'], 1.0 + (3.0-1.0)*2.0) # 5.0

    def test_seeker_endurance_scaling(self):
        # "2x endurance should result in 1.5x mass"
        ModifierEffects.seeker_endurance(2.0, self.stats)
        
        self.assertAlmostEqual(self.stats['endurance_mult'], 2.0)
        # Mass factor = 1.0 + (2.0 - 1.0) * 0.5 = 1.5
        self.assertAlmostEqual(self.stats['mass_mult'], 1.5)
        
        # 10x endurance
        self.setUp()
        ModifierEffects.seeker_endurance(10.0, self.stats)
        self.assertAlmostEqual(self.stats['endurance_mult'], 10.0)
        # Mass factor = 1.0 + (9.0) * 0.5 = 5.5
        self.assertAlmostEqual(self.stats['mass_mult'], 5.5)

    def test_seeker_damage_scaling(self):
        # "2x damage should result in 1.75x mass"
        ModifierEffects.seeker_damage(2.0, self.stats)
        
        self.assertAlmostEqual(self.stats['projectile_damage_mult'], 2.0)
        # Mass factor = 1.0 + (2.0 - 1.0) * 0.75 = 1.75
        self.assertAlmostEqual(self.stats['mass_mult'], 1.75)

    def test_seeker_armored(self):
        # "2x hit points means 1.75 mass increase"
        ModifierEffects.seeker_armored(2.0, self.stats)
        
        self.assertAlmostEqual(self.stats['projectile_hp_mult'], 2.0)
        # Mass factor = 1.0 + (2.0 - 1.0) * 0.75 = 1.75
        self.assertAlmostEqual(self.stats['mass_mult'], 1.75)

    def test_seeker_stealth(self):
        # "mass rises dramatically". Implemented as linear factor 2x per level.
        ModifierEffects.seeker_stealth(1.0, self.stats)
        
        self.assertAlmostEqual(self.stats['projectile_stealth_level'], 1.0)
        self.assertAlmostEqual(self.stats['mass_mult'], 3.0) # 1 * (1 + 1*2) = 3

    def test_automation(self):
        # "mass increases with the degree of automation"
        # 0.5 reduction (50% automation) -> 1.5x Mass
        ModifierEffects.automation(0.5, self.stats)
        
        self.assertAlmostEqual(self.stats['crew_req_mult'], 0.5)
        self.assertAlmostEqual(self.stats['mass_mult'], 1.5)
        
        # 0.99 reduction (99% automation)
        self.setUp()
        ModifierEffects.automation(0.99, self.stats)
        self.assertAlmostEqual(self.stats['crew_req_mult'], 1.0 - 0.99)
        self.assertAlmostEqual(self.stats['mass_mult'], 1.99)

    # Phase 7: Legacy SeekerWeapon tests removed.
    # test_component_integration and test_seeker_damage_application tested 
    # SeekerWeapon._apply_custom_stats which no longer exists after aliasing.
    # Proper modifier → ability value sync is noted as a future enhancement.

if __name__ == '__main__':
    unittest.main()
