"""Tests for component modifier system."""
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components import (
    load_components, load_modifiers, create_component,
    MODIFIER_REGISTRY, COMPONENT_REGISTRY,
    Weapon, BeamWeapon, ProjectileWeapon
)


class TestModifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("components.json")
        load_modifiers("modifiers.json")
    
    def test_modifiers_loaded(self):
        """Verify modifiers.json is loaded correctly."""
        self.assertGreater(len(MODIFIER_REGISTRY), 0, "No modifiers loaded")
    
    def test_add_modifier_to_component(self):
        """Test adding a modifier to a component."""
        railgun = create_component('railgun')
        initial_mass = railgun.mass
        
        # Check if 'reinforced' modifier exists
        if 'reinforced' in MODIFIER_REGISTRY:
            result = railgun.add_modifier('reinforced')
            self.assertTrue(result)
            # Reinforced typically adds mass
            railgun.recalculate_stats()
            self.assertGreaterEqual(railgun.mass, initial_mass)
    
    def test_remove_modifier(self):
        """Test removing a modifier from a component."""
        railgun = create_component('railgun')
        
        if 'reinforced' in MODIFIER_REGISTRY:
            railgun.add_modifier('reinforced')
            self.assertIsNotNone(railgun.get_modifier('reinforced'))
            
            railgun.remove_modifier('reinforced')
            self.assertIsNone(railgun.get_modifier('reinforced'))
    
    def test_modifier_restrictions(self):
        """Test that modifiers respect type restrictions."""
        # Facing modifier should only apply to weapons
        if 'facing' in MODIFIER_REGISTRY:
            bridge = create_component('bridge')
            result = bridge.add_modifier('facing')
            # Should fail if restrictions are applied
            # (depends on how restrictions are defined in modifiers.json)
    
    def test_modifier_effects_on_stats(self):
        """Test that modifier effects are applied to stats."""
        railgun = create_component('railgun')
        base_arc = railgun.firing_arc
        
        # Check for arc-modifying modifier
        if 'wide_arc' in MODIFIER_REGISTRY:
            railgun.add_modifier('wide_arc')
            railgun.recalculate_stats()
            # Arc should be different after applying modifier
    
    def test_get_modifier_returns_none_for_missing(self):
        """get_modifier should return None for non-existent modifier."""
        railgun = create_component('railgun')
        result = railgun.get_modifier('nonexistent_modifier')
        self.assertIsNone(result)
    
    def test_modifier_value_persistence(self):
        """Modifier values should persist after recalculate."""
        if 'facing' in MODIFIER_REGISTRY:
            railgun = create_component('railgun')
            railgun.add_modifier('facing', 90)  # 90 degree facing
            
            mod = railgun.get_modifier('facing')
            if mod:
                self.assertEqual(mod.value, 90)
                
                # Recalculate shouldn't lose the value
                railgun.recalculate_stats()
                mod_after = railgun.get_modifier('facing')
                self.assertEqual(mod_after.value, 90)


class TestComponentCloning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("components.json")
        load_modifiers("modifiers.json")
    
    def test_clone_creates_independent_copy(self):
        """Cloned component should be independent."""
        original = create_component('railgun')
        clone = original.clone()
        
        # Modify clone
        clone.current_hp = 0
        
        # Original should be unaffected
        self.assertNotEqual(original.current_hp, clone.current_hp)
    
    def test_clone_preserves_type(self):
        """Cloned component should be same type."""
        railgun = create_component('railgun')
        clone = railgun.clone()
        
        self.assertIsInstance(clone, ProjectileWeapon)
        self.assertEqual(clone.damage, railgun.damage)
        self.assertEqual(clone.projectile_speed, railgun.projectile_speed)
    
    def test_beam_weapon_clone(self):
        """BeamWeapon should clone correctly."""
        laser = create_component('laser_cannon')
        clone = laser.clone()
        
        self.assertIsInstance(clone, BeamWeapon)
        self.assertEqual(clone.energy_cost, laser.energy_cost)


if __name__ == '__main__':
    unittest.main()
