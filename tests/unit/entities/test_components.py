import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.components.component import (
    load_components, load_modifiers, get_all_components, create_component
)
from game.core.registry import RegistryManager

class TestComponents(unittest.TestCase):
    def setUp(self):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")

    def test_load_components(self):
        """Verify components.json is loaded correctly."""
        comps = get_all_components()
        self.assertGreater(len(comps), 0, "No components loaded")
        
        bridge = create_component('bridge')
        self.assertIsNotNone(bridge)
        # Recalculate stats to resolve formulas (uses default context k=1000)
        bridge.recalculate_stats()
        self.assertEqual(bridge.name, "Bridge")
        self.assertEqual(bridge.mass, 50)

    def test_create_component_types(self):
        railgun = create_component('railgun')
        # Phase 7: Check weapon has ability, not legacy class
        self.assertTrue(railgun.has_ability('WeaponAbility'))
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        self.assertIsNotNone(weapon_ab)
        self.assertEqual(weapon_ab.damage, 40)
        
        tank = create_component('fuel_tank')

        
        # Verify ResourceStorage ability exists
        from game.simulation.systems.resource_manager import ResourceStorage
        found_storage = False
        for ab in tank.ability_instances:
            if isinstance(ab, ResourceStorage) and ab.resource_type == 'fuel':
                found_storage = True
                break
        self.assertTrue(found_storage, "Fuel tank should have Fuel Storage ability")


class TestModifierStacking(unittest.TestCase):
    """Test that modifiers stack multiplicatively, not override each other."""
    
    def setUp(self):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def test_single_size_modifier(self):
        """Size mount 2x should double mass."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass  # 100
        
        railgun.add_modifier('simple_size_mount', 2.0)
        
        self.assertAlmostEqual(railgun.mass, base_mass * 2.0, places=2)
    
    def test_single_range_modifier(self):
        """Range mount level 1 should increase mass by 3.5x."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass  # 100
        
        railgun.add_modifier('range_mount', 1.0)  # Level 1 = 3.5x mass
        
        self.assertAlmostEqual(railgun.mass, base_mass * 3.5, places=2)
    
    def test_multiplicative_stacking_size_and_range(self):
        """Size 2x + Range level 1 (3.5x) should give 7x total mass."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass  # 100
        
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('range_mount', 1.0)  # 3.5x
        
        expected_mass = base_mass * 2.0 * 3.5  # 7x = 700
        self.assertAlmostEqual(railgun.mass, expected_mass, places=2,
            msg=f"Expected {expected_mass}, got {railgun.mass}. Modifiers should stack multiplicatively!")
    
    def test_multiplicative_stacking_size_and_hardened(self):
        """Size 2x + Hardened (+25% mass) should give 2.5x total mass."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass  # 100
        
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened')  # +25% mass = 1.25x
        
        expected_mass = base_mass * 2.0 * 1.25  # 2.5x = 250
        self.assertAlmostEqual(railgun.mass, expected_mass, places=2,
            msg=f"Expected {expected_mass}, got {railgun.mass}. Modifiers should stack multiplicatively!")
    
    def test_triple_modifier_stacking(self):
        """Size 2x + Range level 1 (3.5x) + Hardened (1.25x) = 8.75x mass."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass  # 100
        
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('range_mount', 1.0)  # 3.5x
        railgun.add_modifier('hardened')  # 1.25x
        
        expected_mass = base_mass * 2.0 * 3.5 * 1.25  # 8.75x = 875
        self.assertAlmostEqual(railgun.mass, expected_mass, places=2,
            msg=f"Expected {expected_mass}, got {railgun.mass}. Triple stacking failed!")
    
    def test_hp_stacking(self):
        """Size 2x + Hardened (2x HP) should give 4x HP."""
        railgun = create_component('railgun')
        base_hp = railgun.base_max_hp  # 150
        
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened')  # +100% HP = 2x
        
        expected_hp = base_hp * 2.0 * 2.0  # 4x = 600
        self.assertAlmostEqual(railgun.max_hp, expected_hp, places=0,
            msg=f"Expected HP {expected_hp}, got {railgun.max_hp}")
    
    def test_range_stacking(self):
        """Range mount level 2 should give 4x range."""
        railgun = create_component('railgun')
        # Phase 7: Get range from ability
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        base_range = weapon_ab.range  # 2400
        
        railgun.add_modifier('range_mount', 2.0)  # Level 2 = 4x range
        
        # Re-get ability after modifier application
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        expected_range = base_range * 4  # 9600
        self.assertAlmostEqual(weapon_ab.range, expected_range, places=0)


class TestModifierOrder(unittest.TestCase):
    """Ensure modifier application order doesn't affect final result."""
    
    def setUp(self):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def test_order_independence(self):
        """Adding modifiers in different order should give same result."""
        # Order A: size first, then range
        railgun_a = create_component('railgun')
        railgun_a.add_modifier('simple_size_mount', 2.0)
        railgun_a.add_modifier('range_mount', 1.0)
        
        # Order B: range first, then size
        railgun_b = create_component('railgun')
        railgun_b.add_modifier('range_mount', 1.0)
        railgun_b.add_modifier('simple_size_mount', 2.0)
        
        self.assertAlmostEqual(railgun_a.mass, railgun_b.mass, places=2,
            msg="Modifier order should not affect final mass!")
        self.assertAlmostEqual(railgun_a.max_hp, railgun_b.max_hp, places=0,
            msg="Modifier order should not affect final HP!")


class TestTurretMount(unittest.TestCase):
    """Test turret mount logarithmic diminishing returns."""
    
    def setUp(self):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")
    
    def test_turret_0_degrees_no_change(self):
        """0 degree turret should not increase mass."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass
        
        railgun.add_modifier('turret_mount', 0)
        
        self.assertAlmostEqual(railgun.mass, base_mass, places=2)
    
    def test_turret_diminishing_returns(self):
        """Mass increase should diminish as arc increases."""
        import math
        
        railgun_45 = create_component('railgun')
        railgun_90 = create_component('railgun')
        railgun_180 = create_component('railgun')
        base_mass = railgun_45.base_mass
        
        railgun_45.add_modifier('turret_mount', 45)
        railgun_90.add_modifier('turret_mount', 90)
        railgun_180.add_modifier('turret_mount', 180)
        
        # Calculate increases from base
        increase_45 = railgun_45.mass - base_mass
        increase_90 = railgun_90.mass - base_mass
        increase_180 = railgun_180.mass - base_mass
        
        # Going from 0-45 should cost more than 90-180
        cost_0_to_45 = increase_45
        cost_90_to_180 = increase_180 - increase_90
        
        self.assertGreater(cost_0_to_45, cost_90_to_180,
            msg="First 45° should cost more than 90°-180°!")
    
    def test_turret_180_only_slightly_more_than_90(self):
        """180 degree turret should only cost slightly more than 90."""
        railgun_90 = create_component('railgun')
        railgun_180 = create_component('railgun')
        base_mass = railgun_90.base_mass
        
        railgun_90.add_modifier('turret_mount', 90)
        railgun_180.add_modifier('turret_mount', 180)
        
        # 180 should be less than 20% more than 90
        ratio = railgun_180.mass / railgun_90.mass
        self.assertLess(ratio, 1.20, 
            msg=f"180° should be <20% more than 90°, got {ratio:.2%}")
    
    def test_turret_stacks_with_size(self):
        """Turret mount should stack multiplicatively with size mount."""
        railgun = create_component('railgun')
        base_mass = railgun.base_mass
        
        railgun.add_modifier('simple_size_mount', 2.0)  # 2x
        railgun.add_modifier('turret_mount', 90)  # ~1.71x
        
        # Should be approximately 2.0 * 1.71 = 3.42x
        expected_mult = 2.0 * (1.0 + 0.514 * 1.386)  # ln(1 + 90/30) = ln(4)
        expected_mass = base_mass * expected_mult
        
        self.assertAlmostEqual(railgun.mass, expected_mass, places=0,
            msg=f"Size 2x + Turret 90° should stack multiplicatively")


if __name__ == '__main__':
    unittest.main()
