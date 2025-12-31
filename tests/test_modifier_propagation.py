
import unittest
from components import Component, MODIFIER_REGISTRY, load_modifiers
from ship import Ship, LayerType
import pygame

# Mocking builder logic
class MockBuilder:
    def __init__(self):
        self.selected_components = []
        self.ship = Ship("Test Ship", 0, 0, (0,0,0))

    def propagate_group_modifiers(self, leader_comp):
        if not self.selected_components: return
        
        leader_mods = leader_comp.modifiers
        
        # In real app selected_components is list of tuples (layer, idx, comp)
        for _, _, comp in self.selected_components:
            if comp is leader_comp: continue
            
            # Clear and Copy
            comp.modifiers = []
            for m in leader_mods:
                # Create new AppMod with same def and value
                new_mod = m.__class__(m.definition, m.value)
                comp.modifiers.append(new_mod)
            
            comp.recalculate_stats()

class TestModifierGroupPropagation(unittest.TestCase):
    def setUp(self):
        # Load modifiers to ensure registry is populated
        load_modifiers('data/modifiers.json')
        
        self.builder = MockBuilder()
        
        # Create 3 identical components
        base_data = {
            "id": "laser_cannon",
            "name": "Laser Cannon",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "allowed_layers": ["CORE", "INNER", "OUTER"],
            "allowed_vehicle_types": ["Ship"],
            "cost": 100
        }
        
        self.comp1 = Component(base_data)
        self.comp2 = Component(base_data)
        self.comp3 = Component(base_data)
        
        # Setup Group (Simulating selection)
        # Tuples: (layer, index, comp)
        self.builder.selected_components = [
            ('CORE', 0, self.comp1),
            ('CORE', 1, self.comp2),
            ('CORE', 2, self.comp3)
        ]
        
    def test_add_modifier_default_value(self):
        """Test that adding specific modifier respects min_val if default is not set or 0."""
        # Specifically checking simple_size_mount which had the issue
        mod_id = 'simple_size_mount'
        if mod_id not in MODIFIER_REGISTRY:
            self.skipTest("simple_size_mount not found")
            
        # Add to leader
        self.comp1.add_modifier(mod_id)
        
        mod = self.comp1.get_modifier(mod_id)
        self.assertIsNotNone(mod)
        
        # Check Value - Should be at least min_val (1)
        # If modifiers.json hasn't been fixed yet, this might fail if default_val is 0
        self.assertGreaterEqual(mod.value, 1.0, "Modifier default value should be >= 1 for size mount")
        
    def test_propagation(self):
        """Test that changes to leader propagate to group."""
        mod_id = 'hardened'
        
        # Add to leader
        self.comp1.add_modifier(mod_id)
        
        # Trigger propagation
        self.builder.propagate_group_modifiers(self.comp1)
        
        # Check others
        self.assertIsNotNone(self.comp2.get_modifier(mod_id))
        self.assertIsNotNone(self.comp3.get_modifier(mod_id))
        
    def test_value_change_propagation(self):
        """Test that value changes propagate."""
        mod_id = 'simple_size_mount'
        self.comp1.add_modifier(mod_id)
        mod = self.comp1.get_modifier(mod_id)
        mod.value = 5.0
        
        self.builder.propagate_group_modifiers(self.comp1)
        
        mod2 = self.comp2.get_modifier(mod_id)
        self.assertEqual(mod2.value, 5.0)
        
if __name__ == '__main__':
    unittest.main()
