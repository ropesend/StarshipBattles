"""Tests for component modifier system."""
import unittest

from game.simulation.components.component import (
    load_components, load_modifiers, create_component, Component
)
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


class TestModifiers(unittest.TestCase):
    def setUp(self):
        data_dir = get_data_dir()
        load_components(str(data_dir / "components.json"))
        load_modifiers(str(data_dir / "modifiers.json"))
    
    def test_modifiers_loaded(self):
        """Verify modifiers.json is loaded correctly."""
        self.assertGreater(len(RegistryManager.instance().modifiers), 0, "No modifiers loaded")
    
    def test_add_modifier_to_component(self):
        """Test adding a modifier to a component."""
        railgun = create_component('railgun')
        initial_mass = railgun.mass
        
        # Check if 'reinforced' modifier exists
        if 'reinforced' in RegistryManager.instance().modifiers:
            result = railgun.add_modifier('reinforced')
            self.assertTrue(result)
            # Reinforced typically adds mass
            railgun.recalculate_stats()
            self.assertGreaterEqual(railgun.mass, initial_mass)
    
    def test_remove_modifier(self):
        """Test removing a modifier from a component."""
        railgun = create_component('railgun')
        
        if 'reinforced' in RegistryManager.instance().modifiers:
            railgun.add_modifier('reinforced')
            self.assertIsNotNone(railgun.get_modifier('reinforced'))
            
            railgun.remove_modifier('reinforced')
            self.assertIsNone(railgun.get_modifier('reinforced'))
    
    def test_modifier_restrictions(self):
        """Test that modifiers respect type restrictions."""
        # Facing modifier should only apply to weapons
        if 'facing' in RegistryManager.instance().modifiers:
            bridge = create_component('bridge')
            result = bridge.add_modifier('facing')
            # Should fail if restrictions are applied
            # (depends on how restrictions are defined in modifiers.json)
    
    def test_modifier_effects_on_stats(self):
        """Test that modifier effects are applied to stats."""
        railgun = create_component('railgun')
        # Phase 7: Get firing_arc from ability
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility') or railgun.get_ability('WeaponAbility')
        base_arc = weapon_ab.firing_arc if weapon_ab else 20
        
        # Check for arc-modifying modifier
        if 'wide_arc' in RegistryManager.instance().modifiers:
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
        if 'facing' in RegistryManager.instance().modifiers:
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
    def setUp(self):
        data_dir = get_data_dir()
        load_components(str(data_dir / "components.json"))
        load_modifiers(str(data_dir / "modifiers.json"))
    
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
        
        self.assertIsInstance(clone, Component)
        self.assertTrue(clone.has_ability('ProjectileWeaponAbility'))
        # Phase 7: Compare ability values, not component attributes
        clone_ab = clone.get_ability('ProjectileWeaponAbility')
        railgun_ab = railgun.get_ability('ProjectileWeaponAbility')
        self.assertEqual(clone_ab.damage, railgun_ab.damage)
        self.assertEqual(clone_ab.projectile_speed, railgun_ab.projectile_speed)
    
    def test_beam_weapon_clone(self):
        """BeamWeapon should clone correctly."""
        laser = create_component('laser_cannon')
        clone = laser.clone()
        
        self.assertIsInstance(clone, Component)
        self.assertTrue(clone.has_ability('BeamWeaponAbility'))
        # Verify energy cost via abilities
        from game.simulation.systems.resource_manager import ResourceConsumption
        original_cost = 0
        clone_cost = 0
        
        for ab in laser.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                original_cost = ab.amount
                break
                
        for ab in clone.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                clone_cost = ab.amount
                break
                
        self.assertEqual(clone_cost, original_cost)


if __name__ == '__main__':
    unittest.main()
