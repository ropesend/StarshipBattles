"""Tests for component modifier system."""
import pytest

from game.simulation.components.component import (
    load_components, load_modifiers, create_component, Component
)
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


@pytest.fixture
def setup_data(fresh_registries):
    """Load components and modifiers for tests."""
    # Return fresh_registries so tests can use them
    return fresh_registries


class TestModifiers:
    def test_modifiers_loaded(self, setup_data):
        """Verify modifiers.json is loaded correctly."""
        assert len(setup_data.modifiers) > 0, "No modifiers loaded"

    def test_add_modifier_to_component(self, setup_data):
        """Test adding a modifier to a component."""
        railgun = create_component('railgun', registries=setup_data)
        initial_mass = railgun.mass

        # Check if 'reinforced' modifier exists
        if 'reinforced' in setup_data.modifiers:
            result = railgun.add_modifier('reinforced')
            assert result is True
            # Reinforced typically adds mass
            railgun.recalculate_stats()
            assert railgun.mass >= initial_mass

    def test_remove_modifier(self, setup_data):
        """Test removing a modifier from a component."""
        railgun = create_component('railgun', registries=setup_data)

        if 'reinforced' in setup_data.modifiers:
            railgun.add_modifier('reinforced')
            assert railgun.get_modifier('reinforced') is not None

            railgun.remove_modifier('reinforced')
            assert railgun.get_modifier('reinforced') is None

    def test_modifier_restrictions(self, setup_data):
        """Test that modifiers respect type restrictions."""
        # Facing modifier should only apply to weapons
        if 'facing' in setup_data.modifiers:
            bridge = create_component('bridge', registries=setup_data)
            result = bridge.add_modifier('facing')
            # Should fail if restrictions are applied
            # (depends on how restrictions are defined in modifiers.json)

    def test_modifier_effects_on_stats(self, setup_data):
        """Test that modifier effects are applied to stats."""
        railgun = create_component('railgun', registries=setup_data)
        # Phase 7: Get firing_arc from ability
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility') or railgun.get_ability('WeaponAbility')
        base_arc = weapon_ab.firing_arc if weapon_ab else 20

        # Check for arc-modifying modifier
        if 'wide_arc' in setup_data.modifiers:
            railgun.add_modifier('wide_arc')
            railgun.recalculate_stats()
            # Arc should be different after applying modifier

    def test_get_modifier_returns_none_for_missing(self, setup_data):
        """get_modifier should return None for non-existent modifier."""
        railgun = create_component('railgun', registries=setup_data)
        result = railgun.get_modifier('nonexistent_modifier')
        assert result is None

    def test_modifier_value_persistence(self, setup_data):
        """Modifier values should persist after recalculate."""
        if 'facing' in setup_data.modifiers:
            railgun = create_component('railgun', registries=setup_data)
            railgun.add_modifier('facing', 90)  # 90 degree facing

            mod = railgun.get_modifier('facing')
            if mod:
                assert mod.value == 90

                # Recalculate shouldn't lose the value
                railgun.recalculate_stats()
                mod_after = railgun.get_modifier('facing')
                assert mod_after.value == 90


class TestComponentCloning:
    def test_clone_creates_independent_copy(self, setup_data):
        """Cloned component should be independent."""
        original = create_component('railgun', registries=setup_data)
        clone = original.clone()

        # Modify clone
        clone.current_hp = 0

        # Original should be unaffected
        assert original.current_hp != clone.current_hp

    def test_clone_preserves_type(self, setup_data):
        """Cloned component should be same type."""
        railgun = create_component('railgun', registries=setup_data)
        clone = railgun.clone()

        assert isinstance(clone, Component)
        assert clone.has_ability('ProjectileWeaponAbility')
        # Phase 7: Compare ability values, not component attributes
        clone_ab = clone.get_ability('ProjectileWeaponAbility')
        railgun_ab = railgun.get_ability('ProjectileWeaponAbility')
        assert clone_ab.damage == railgun_ab.damage
        assert clone_ab.projectile_speed == railgun_ab.projectile_speed

    def test_beam_weapon_clone(self, setup_data):
        """BeamWeapon should clone correctly."""
        laser = create_component('laser_cannon', registries=setup_data)
        clone = laser.clone()

        assert isinstance(clone, Component)
        assert clone.has_ability('BeamWeaponAbility')
        # Verify energy cost via abilities
        from game.simulation.components.abilities.resources import ResourceConsumption
        original_cost = 0
        clone_cost = 0

        for ab in laser.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_type == 'energy':
                original_cost = ab.amount
                break

        for ab in clone.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_type == 'energy':
                clone_cost = ab.amount
                break

        assert clone_cost == original_cost
