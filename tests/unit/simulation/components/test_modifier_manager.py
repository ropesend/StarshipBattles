"""Tests for ModifierManager - extracted from Component god class.

PROJ-44 Phase 4: Tests modifier operations and stat summaries.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.modifier_manager import ModifierManager


class TestModifierManagerAddRemove:
    """Test modifier add/remove operations."""

    def test_add_modifier_success(self):
        """add_modifier should add modifier to component."""
        railgun = create_component('railgun')

        result = railgun.add_modifier('simple_size_mount', 2.0)

        assert result is True
        assert railgun.get_modifier('simple_size_mount') is not None

    def test_add_modifier_nonexistent(self):
        """add_modifier should return False for nonexistent modifier."""
        railgun = create_component('railgun')

        result = railgun.add_modifier('nonexistent_modifier', 1.0)

        assert result is False

    def test_add_modifier_replaces_existing(self):
        """add_modifier should replace existing modifier with same ID."""
        railgun = create_component('railgun')

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('simple_size_mount', 3.0)

        # Should only have one modifier
        count = len([m for m in railgun.modifiers if m.definition.id == 'simple_size_mount'])
        assert count == 1

        # Should have the new value
        mod = railgun.get_modifier('simple_size_mount')
        assert mod.value == 3.0

    def test_remove_modifier(self):
        """remove_modifier should remove modifier from component."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)

        railgun.remove_modifier('simple_size_mount')

        assert railgun.get_modifier('simple_size_mount') is None


class TestModifierManagerQuery:
    """Test modifier querying methods."""

    def test_get_modifier_returns_matching(self):
        """get_modifier should return matching modifier."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)

        mod = railgun.get_modifier('simple_size_mount')

        assert mod is not None
        assert mod.definition.id == 'simple_size_mount'

    def test_get_modifier_returns_none_for_missing(self):
        """get_modifier should return None for missing modifier."""
        railgun = create_component('railgun')

        mod = railgun.get_modifier('simple_size_mount')

        assert mod is None


class TestModifierManagerEffects:
    """Test modifier effect aggregation."""

    def test_get_all_modifier_effects_empty(self):
        """get_all_modifier_effects should return empty list for no modifiers."""
        railgun = create_component('railgun')
        railgun.modifiers.clear()

        effects = railgun.get_all_modifier_effects()

        assert effects == []

    def test_get_all_modifier_effects_with_modifiers(self):
        """get_all_modifier_effects should return effects from all modifiers."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)

        effects = railgun.get_all_modifier_effects()

        assert len(effects) > 0


class TestModifierManagerStatSummary:
    """Test stat summary generation."""

    def test_get_modifier_stat_summary_empty(self):
        """get_modifier_stat_summary should return empty dict for no modifiers."""
        railgun = create_component('railgun')
        railgun.modifiers.clear()

        summary = railgun.get_modifier_stat_summary()

        assert summary == {}

    def test_get_modifier_stat_summary_structure(self):
        """get_modifier_stat_summary should have correct structure."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)

        summary = railgun.get_modifier_stat_summary()

        # Should have at least one stat key
        assert len(summary) > 0

        # Each entry should have expected structure
        for stat_key, entry in summary.items():
            assert 'net_value' in entry
            assert 'operation' in entry
            assert 'contributors' in entry

    def test_get_modifier_stat_summary_multiplicative_stacking(self):
        """get_modifier_stat_summary should reflect multiplicative stacking."""
        railgun = create_component('railgun')
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.25)

        summary = railgun.get_modifier_stat_summary()

        # mass_mult should show combined multiplier
        if 'mass_mult' in summary:
            assert summary['mass_mult']['net_value'] == pytest.approx(2.0 * 1.25, abs=0.01)


class TestModifierManagerStandalone:
    """Test ModifierManager static methods."""

    def test_manager_add_modifier(self):
        """ModifierManager.add_modifier should work with modifiers list."""
        railgun = create_component('railgun')
        registries = railgun._registries

        result = ModifierManager.add_modifier(
            railgun.modifiers,
            'simple_size_mount',
            2.0,
            registries
        )

        assert result is True
        assert any(m.definition.id == 'simple_size_mount' for m in railgun.modifiers)

    def test_manager_remove_modifier(self):
        """ModifierManager.remove_modifier should work with modifiers list."""
        railgun = create_component('railgun')
        registries = railgun._registries
        ModifierManager.add_modifier(railgun.modifiers, 'simple_size_mount', 2.0, registries)

        new_list = ModifierManager.remove_modifier(railgun.modifiers, 'simple_size_mount')

        assert not any(m.definition.id == 'simple_size_mount' for m in new_list)

    def test_manager_get_modifier(self):
        """ModifierManager.get_modifier should find modifier in list."""
        railgun = create_component('railgun')
        registries = railgun._registries
        ModifierManager.add_modifier(railgun.modifiers, 'simple_size_mount', 2.0, registries)

        mod = ModifierManager.get_modifier(railgun.modifiers, 'simple_size_mount')

        assert mod is not None
        assert mod.definition.id == 'simple_size_mount'
