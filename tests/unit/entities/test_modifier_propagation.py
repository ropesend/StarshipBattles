import pytest
from game.simulation.components.component import Component, load_modifiers
from game.core.registry import RegistryManager
from game.simulation.entities.ship import Ship, LayerType
from tests.fixtures.paths import get_data_dir
import pygame


# Mocking builder logic
class MockBuilder:
    def __init__(self, registries):
        self.selected_components = []
        self.ship = Ship("Test Ship", 0, 0, (0,0,0), registries=registries)

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


@pytest.fixture
def builder_with_components(fresh_registries):
    # Load modifiers to ensure registry is populated
    load_modifiers(str(get_data_dir() / 'modifiers.json'))

    builder = MockBuilder(fresh_registries)

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

    comp1 = Component(base_data, registries=fresh_registries)
    comp2 = Component(base_data, registries=fresh_registries)
    comp3 = Component(base_data, registries=fresh_registries)

    # Setup Group (Simulating selection)
    # Tuples: (layer, index, comp)
    builder.selected_components = [
        ('CORE', 0, comp1),
        ('CORE', 1, comp2),
        ('CORE', 2, comp3)
    ]

    return builder, comp1, comp2, comp3


class TestModifierGroupPropagation:

    def test_add_modifier_default_value(self, builder_with_components):
        """Test that adding specific modifier respects min_val if default is not set or 0."""
        builder, comp1, comp2, comp3 = builder_with_components

        # Specifically checking simple_size_mount which had the issue
        mod_id = 'simple_size_mount'
        if mod_id not in RegistryManager.instance().modifiers:
            pytest.skip("simple_size_mount not found")

        # Add to leader
        comp1.add_modifier(mod_id)

        mod = comp1.get_modifier(mod_id)
        assert mod is not None

        # Check Value - Should be at least min_val (1)
        # If modifiers.json hasn't been fixed yet, this might fail if default_val is 0
        assert mod.value >= 1.0, "Modifier default value should be >= 1 for size mount"

    def test_propagation(self, builder_with_components):
        """Test that changes to leader propagate to group."""
        builder, comp1, comp2, comp3 = builder_with_components

        mod_id = 'hardened_mount'

        # Add to leader
        comp1.add_modifier(mod_id)

        # Trigger propagation
        builder.propagate_group_modifiers(comp1)

        # Check others
        assert comp2.get_modifier(mod_id) is not None
        assert comp3.get_modifier(mod_id) is not None

    def test_value_change_propagation(self, builder_with_components):
        """Test that value changes propagate."""
        builder, comp1, comp2, comp3 = builder_with_components

        mod_id = 'simple_size_mount'
        comp1.add_modifier(mod_id)
        mod = comp1.get_modifier(mod_id)
        mod.value = 5.0

        builder.propagate_group_modifiers(comp1)

        mod2 = comp2.get_modifier(mod_id)
        assert mod2.value == 5.0
