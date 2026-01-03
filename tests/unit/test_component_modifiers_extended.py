"""Extended tests for component modifier effects."""
import unittest
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.components.component import load_components, load_modifiers, create_component, MODIFIER_REGISTRY
from game.simulation.components.modifiers import ModifierEffects, apply_modifier_effects, SPECIAL_EFFECT_HANDLERS


class TestModifierEffectsFunctions(unittest.TestCase):
    """Test individual modifier effect functions from ModifierEffects class."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def _create_default_stats(self):
        """Create a fresh default stats dictionary."""
        return {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'cost_mult': 1.0,
            'thrust_mult': 1.0,
            'turn_mult': 1.0,
            'energy_gen_mult': 1.0,
            'capacity_mult': 1.0,
            'crew_capacity_mult': 1.0,
            'life_support_capacity_mult': 1.0,
            'consumption_mult': 1.0,
            'range_mult': 1.0,
            'mass_add': 0,
            'arc_add': 0,
            'arc_set': None,
            'properties': {}
        }
    
    def test_simple_size_scales_all_stats(self):
        """Simple size modifier should scale mass, hp, damage, etc."""
        stats = self._create_default_stats()
        
        ModifierEffects.simple_size(2.0, stats)
        
        self.assertEqual(stats['mass_mult'], 2.0)
        self.assertEqual(stats['hp_mult'], 2.0)
        self.assertEqual(stats['damage_mult'], 2.0)
        self.assertEqual(stats['cost_mult'], 2.0)
        self.assertEqual(stats['thrust_mult'], 2.0)
        self.assertEqual(stats['turn_mult'], 2.0)
        self.assertEqual(stats['consumption_mult'], 2.0)
    
    def test_range_mount_increases_range(self):
        """Range mount should double range at level 1."""
        stats = self._create_default_stats()
        
        ModifierEffects.range_mount(1, stats)  # Level 1
        
        # Range = 2^1 = 2x
        self.assertAlmostEqual(stats['range_mult'], 2.0, places=2)
    
    def test_range_mount_level_2(self):
        """Range mount level 2 should quadruple range."""
        stats = self._create_default_stats()
        
        ModifierEffects.range_mount(2, stats)  # Level 2
        
        # Range = 2^2 = 4x
        self.assertAlmostEqual(stats['range_mult'], 4.0, places=2)
    
    def test_range_mount_increases_mass(self):
        """Range mount should increase mass by 3.5^val."""
        stats = self._create_default_stats()
        
        ModifierEffects.range_mount(1, stats)  # Level 1
        
        # Mass = 3.5^1 = 3.5x
        self.assertAlmostEqual(stats['mass_mult'], 3.5, places=2)
    
    def test_turret_mount_logarithmic_scaling(self):
        """Turret mount should use logarithmic scaling for mass."""
        stats = self._create_default_stats()
        
        ModifierEffects.turret_mount(90, stats)  # 90 degree arc
        
        # Expected: 1.0 + 0.514 * ln(1 + 90/30) = 1.0 + 0.514 * ln(4)
        expected_mult = 1.0 + 0.514 * math.log(1.0 + 90 / 30.0)
        self.assertAlmostEqual(stats['mass_mult'], expected_mult, places=2)
    
    def test_turret_mount_zero_arc_no_change(self):
        """0 degree turret arc should not change mass."""
        stats = self._create_default_stats()
        
        ModifierEffects.turret_mount(0, stats)
        
        self.assertEqual(stats['mass_mult'], 1.0)
    
    def test_turret_mount_sets_arc(self):
        """Turret mount should set arc_set to half the total arc."""
        stats = self._create_default_stats()
        
        ModifierEffects.turret_mount(90, stats)
        
        # Now sets FULL arc (90.0)
        self.assertEqual(stats['arc_set'], 90.0)
    
    def test_facing_sets_property(self):
        """Facing modifier should set facing_angle property."""
        stats = self._create_default_stats()
        
        ModifierEffects.facing(180, stats)
        
        self.assertEqual(stats['properties']['facing_angle'], 180)


class TestApplyModifierEffects(unittest.TestCase):
    """Test the apply_modifier_effects function."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def _create_default_stats(self):
        return {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'damage_mult': 1.0,
            'cost_mult': 1.0,
            'thrust_mult': 1.0,
            'turn_mult': 1.0,
            'energy_gen_mult': 1.0,
            'capacity_mult': 1.0,
            'consumption_mult': 1.0,
            'range_mult': 1.0,
            'mass_add': 0,
            'arc_add': 0,
            'arc_set': None,
            'properties': {}
        }
    
    def test_special_effect_handlers_exist(self):
        """Verify all expected special handlers are registered."""
        self.assertIn('simple_size', SPECIAL_EFFECT_HANDLERS)
        self.assertIn('range_mount', SPECIAL_EFFECT_HANDLERS)
        self.assertIn('turret_mount', SPECIAL_EFFECT_HANDLERS)
        self.assertIn('facing', SPECIAL_EFFECT_HANDLERS)


class TestModifierStackingIntegration(unittest.TestCase):
    """Test modifier stacking on actual components."""
    
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def test_range_mount_increases_component_mass(self):
        """Range mount modifier should increase component mass."""
        # Create base railgun
        railgun_base = create_component('railgun')
        base_mass = railgun_base.mass
        
        # Create railgun with range modifier
        railgun_range = create_component('railgun')
        railgun_range.add_modifier('range_mount', 1)
        railgun_range.recalculate_stats()
        
        # Range mount should increase mass
        self.assertGreater(railgun_range.mass, base_mass)
    
    def test_multiple_modifiers_order_independent(self):
        """Adding modifiers in different order should give same result."""
        # Create two weapons, add modifiers in different order
        w1 = create_component('railgun')
        w1.add_modifier('size_mount', 2)
        w1.add_modifier('range_mount', 1)
        w1.recalculate_stats()
        
        w2 = create_component('railgun')
        w2.add_modifier('range_mount', 1)
        w2.add_modifier('size_mount', 2)
        w2.recalculate_stats()
        
        self.assertEqual(w1.mass, w2.mass)
        self.assertEqual(w1.max_hp, w2.max_hp)


if __name__ == '__main__':
    unittest.main()
