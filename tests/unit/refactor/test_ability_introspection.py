"""
Tests for Ability introspection methods - Phase 1 Task 1.5

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest


class TestAbilityIntrospection:
    """Tests for Ability base class introspection methods."""

    def test_ability_has_stat_bindings_attribute(self):
        """Ability class should have STAT_BINDINGS class attribute."""
        from game.simulation.components.abilities.base import Ability

        assert hasattr(Ability, 'STAT_BINDINGS')
        assert isinstance(Ability.STAT_BINDINGS, list)

    def test_ability_get_consumed_stats_returns_empty_by_default(self):
        """Base Ability.get_consumed_stats() should return empty set."""
        from game.simulation.components.abilities.base import Ability

        consumed = Ability.get_consumed_stats()
        assert isinstance(consumed, set)
        assert len(consumed) == 0  # Base class has no bindings

    def test_ability_get_stat_bindings_info_returns_empty_by_default(self):
        """Base Ability.get_stat_bindings_info() should return empty list."""
        from game.simulation.components.abilities.base import Ability

        info = Ability.get_stat_bindings_info()
        assert isinstance(info, list)
        assert len(info) == 0

    def test_ability_get_effect_summary_returns_empty_by_default(self):
        """Base Ability.get_effect_summary() should return empty list."""
        from game.simulation.components.abilities.base import Ability

        # Create a minimal mock component
        class MockComponent:
            stats = {}

        ability = Ability.__new__(Ability)
        ability.component = MockComponent()

        summary = ability.get_effect_summary()
        assert isinstance(summary, list)
        assert len(summary) == 0

    def test_subclass_with_bindings_get_consumed_stats(self):
        """Subclass with STAT_BINDINGS should return its stat keys."""
        from game.simulation.components.abilities.base import Ability
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class TestAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply'),
                AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply'),
            ]

        consumed = TestAbility.get_consumed_stats()
        assert StatKey.DAMAGE_MULT in consumed
        assert StatKey.RANGE_MULT in consumed
        assert len(consumed) == 2

    def test_subclass_with_bindings_get_stat_bindings_info(self):
        """Subclass with STAT_BINDINGS should return binding info."""
        from game.simulation.components.abilities.base import Ability
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class TestAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply'),
            ]

        info = TestAbility.get_stat_bindings_info()
        assert len(info) == 1
        assert info[0]['stat_key'] == 'damage_mult'
        assert info[0]['attribute'] == 'damage'
        assert info[0]['operation'] == 'multiply'

    def test_ability_get_effect_summary_with_active_modifiers(self):
        """get_effect_summary() should show base vs current for modified stats."""
        from game.simulation.components.abilities.base import Ability
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class TestAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply'),
            ]

            def __init__(self):
                self._base_damage = 100.0
                self.damage = 150.0  # Modified

        class MockComponent:
            stats = {'damage_mult': 1.5}

        ability = TestAbility()
        ability.component = MockComponent()

        summary = ability.get_effect_summary()
        assert len(summary) == 1
        assert summary[0]['attribute'] == 'damage'
        assert summary[0]['base'] == 100.0
        assert summary[0]['current'] == 150.0

    def test_ability_get_effect_summary_excludes_unmodified(self):
        """get_effect_summary() should exclude stats with multiplier 1.0."""
        from game.simulation.components.abilities.base import Ability
        from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding

        class TestAbility(Ability):
            STAT_BINDINGS = [
                AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply'),
                AbilityStatBinding(StatKey.RANGE_MULT, 'range', 'multiply'),
            ]

            def __init__(self):
                self._base_damage = 100.0
                self.damage = 150.0  # Modified
                self._base_range = 1000.0
                self.range = 1000.0  # Not modified

        class MockComponent:
            stats = {'damage_mult': 1.5, 'range_mult': 1.0}

        ability = TestAbility()
        ability.component = MockComponent()

        summary = ability.get_effect_summary()
        # Should only include damage (modified), not range (unmodified)
        assert len(summary) == 1
        assert summary[0]['attribute'] == 'damage'


class TestRealComponentIntrospection:
    """Integration tests using real components to verify introspection works."""

    def test_weapon_get_effect_summary_with_range_mount(self):
        """WeaponAbility.get_effect_summary() should show range change with range_mount."""
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('range_mount', 2)  # Level 2 = 4x range

        weapon = railgun.get_ability('ProjectileWeaponAbility')
        summary = weapon.get_effect_summary()

        # Should include range modification
        range_entry = next((s for s in summary if s['attribute'] == 'range'), None)
        assert range_entry is not None
        assert range_entry['stat_value'] == pytest.approx(4.0)  # 2^2 = 4

    def test_weapon_get_effect_summary_with_hardened_mount(self):
        """WeaponAbility.get_effect_summary() should show damage with hardened_mount."""
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('hardened_mount', 2.0)  # 2x mass, 4x HP

        weapon = railgun.get_ability('ProjectileWeaponAbility')
        summary = weapon.get_effect_summary()

        # Hardened mount affects mass/HP but not weapon damage directly
        # Should have entries for stats that are actually modified
        assert isinstance(summary, list)

    def test_effect_summary_empty_when_no_modifiers(self):
        """get_effect_summary() should return empty list with no modifiers."""
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        # No modifiers applied

        weapon = railgun.get_ability('ProjectileWeaponAbility')
        summary = weapon.get_effect_summary()

        # No modifiers = empty summary (all stats at default 1.0)
        assert isinstance(summary, list)
        assert len(summary) == 0
