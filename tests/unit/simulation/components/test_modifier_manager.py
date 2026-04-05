"""Tests for ModifierManager - extracted from Component god class.

PROJ-44 Phase 4: Tests modifier operations and stat summaries.
"""
import pytest
from game.simulation.components.component import create_component
from game.simulation.components.modifier_manager import ModifierManager


class TestModifierManagerAddRemove:
    """Test modifier add/remove operations."""

    def test_add_modifier_success(self, fresh_registries):
        """add_modifier should add modifier to component."""
        railgun = create_component('railgun', registries=fresh_registries)

        result = railgun.add_modifier('simple_size_mount', 2.0)

        assert result is True
        assert railgun.get_modifier('simple_size_mount') is not None

    def test_add_modifier_nonexistent(self, fresh_registries):
        """add_modifier should return False for nonexistent modifier."""
        railgun = create_component('railgun', registries=fresh_registries)

        result = railgun.add_modifier('nonexistent_modifier', 1.0)

        assert result is False

    def test_add_modifier_replaces_existing(self, fresh_registries):
        """add_modifier should replace existing modifier with same ID."""
        railgun = create_component('railgun', registries=fresh_registries)

        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('simple_size_mount', 3.0)

        # Should only have one modifier
        count = len([m for m in railgun.modifiers if m.definition.id == 'simple_size_mount'])
        assert count == 1

        # Should have the new value
        mod = railgun.get_modifier('simple_size_mount')
        assert mod.value == 3.0

    def test_remove_modifier(self, fresh_registries):
        """remove_modifier should remove modifier from component."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        railgun.remove_modifier('simple_size_mount')

        assert railgun.get_modifier('simple_size_mount') is None


class TestModifierManagerQuery:
    """Test modifier querying methods."""

    def test_get_modifier_returns_matching(self, fresh_registries):
        """get_modifier should return matching modifier."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        mod = railgun.get_modifier('simple_size_mount')

        assert mod is not None
        assert mod.definition.id == 'simple_size_mount'

    def test_get_modifier_returns_none_for_missing(self, fresh_registries):
        """get_modifier should return None for missing modifier."""
        railgun = create_component('railgun', registries=fresh_registries)

        mod = railgun.get_modifier('simple_size_mount')

        assert mod is None


class TestModifierManagerEffects:
    """Test modifier effect aggregation."""

    def test_get_all_modifier_effects_empty(self, fresh_registries):
        """get_all_modifier_effects should return empty list for no modifiers."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers.clear()

        effects = railgun.get_all_modifier_effects()

        assert effects == []

    def test_get_all_modifier_effects_with_modifiers(self, fresh_registries):
        """get_all_modifier_effects should return effects from all modifiers."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        effects = railgun.get_all_modifier_effects()

        assert len(effects) > 0


class TestModifierManagerStatSummary:
    """Test stat summary generation."""

    def test_get_modifier_stat_summary_empty(self, fresh_registries):
        """get_modifier_stat_summary should return empty dict for no modifiers."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.modifiers.clear()

        summary = railgun.get_modifier_stat_summary()

        assert summary == {}

    def test_get_modifier_stat_summary_structure(self, fresh_registries):
        """get_modifier_stat_summary should have correct structure."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)

        summary = railgun.get_modifier_stat_summary()

        # Should have at least one stat key
        assert len(summary) > 0

        # Each entry should have expected structure
        for stat_key, entry in summary.items():
            assert 'net_value' in entry
            assert 'operation' in entry
            assert 'contributors' in entry

    def test_get_modifier_stat_summary_multiplicative_stacking(self, fresh_registries):
        """get_modifier_stat_summary should reflect multiplicative stacking."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.add_modifier('simple_size_mount', 2.0)
        railgun.add_modifier('hardened_mount', 1.25)

        summary = railgun.get_modifier_stat_summary()

        # mass_mult should show combined multiplier
        if 'mass_mult' in summary:
            assert summary['mass_mult']['net_value'] == pytest.approx(2.0 * 1.25, abs=0.01)


class TestModifierManagerStandalone:
    """Test ModifierManager deprecated static methods (legacy API)."""

    def test_manager_add_modifier_static(self, fresh_registries):
        """ModifierManager.add_modifier_static should work with modifiers list."""
        railgun = create_component('railgun', registries=fresh_registries)
        registries = railgun._registries

        result = ModifierManager.add_modifier_static(
            railgun.modifiers,
            'simple_size_mount',
            2.0,
            registries
        )

        assert result is True
        assert any(m.definition.id == 'simple_size_mount' for m in railgun.modifiers)

    def test_manager_remove_modifier_static(self, fresh_registries):
        """ModifierManager.remove_modifier_static should work with modifiers list."""
        railgun = create_component('railgun', registries=fresh_registries)
        registries = railgun._registries
        ModifierManager.add_modifier_static(railgun.modifiers, 'simple_size_mount', 2.0, registries)

        new_list = ModifierManager.remove_modifier_static(railgun.modifiers, 'simple_size_mount')

        assert not any(m.definition.id == 'simple_size_mount' for m in new_list)

    def test_manager_get_modifier_static(self, fresh_registries):
        """ModifierManager.get_modifier_static should find modifier in list."""
        railgun = create_component('railgun', registries=fresh_registries)
        registries = railgun._registries
        ModifierManager.add_modifier_static(railgun.modifiers, 'simple_size_mount', 2.0, registries)

        mod = ModifierManager.get_modifier_static(railgun.modifiers, 'simple_size_mount')

        assert mod is not None
        assert mod.definition.id == 'simple_size_mount'


class TestStatefulModifierManagerConstruction:
    """Test stateful ModifierManager delegate construction (PROJ-241)."""

    def test_construction_no_initial_modifiers(self, fresh_registries):
        """ModifierManager(component) with no data modifiers should have empty list."""
        railgun = create_component('railgun', registries=fresh_registries)
        # railgun has no 'modifiers' in its data definition

        mgr = ModifierManager(railgun)

        assert mgr.modifiers == []
        assert len(mgr.modifiers) == 0

    def test_construction_loads_modifiers_from_data(self, fresh_registries):
        """ModifierManager(component) should load modifiers from component.data['modifiers']."""
        railgun = create_component('railgun', registries=fresh_registries)
        # Inject modifier data into component's data dict
        railgun.data['modifiers'] = [{'id': 'simple_size_mount', 'value': 2.0}]

        mgr = ModifierManager(railgun)

        assert len(mgr.modifiers) == 1
        assert mgr.modifiers[0].definition.id == 'simple_size_mount'
        assert mgr.modifiers[0].value == 2.0

    def test_construction_skips_unknown_modifiers(self, fresh_registries):
        """ModifierManager(component) should skip modifiers not in registry."""
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.data['modifiers'] = [
            {'id': 'nonexistent_mod'},
            {'id': 'simple_size_mount', 'value': 1.5}
        ]

        mgr = ModifierManager(railgun)

        # Only the valid modifier should be loaded
        assert len(mgr.modifiers) == 1
        assert mgr.modifiers[0].definition.id == 'simple_size_mount'


class TestStatefulModifierManagerAddModifier:
    """Test stateful ModifierManager.add_modifier instance method (PROJ-241)."""

    def test_add_modifier_success(self, fresh_registries):
        """add_modifier(mod_id, value) should add to internal list and return True."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        result = mgr.add_modifier('simple_size_mount', 2.0)

        assert result is True
        assert len(mgr.modifiers) == 1
        assert mgr.modifiers[0].definition.id == 'simple_size_mount'
        assert mgr.modifiers[0].value == 2.0

    def test_add_modifier_replaces_existing(self, fresh_registries):
        """add_modifier should replace existing modifier with same ID (not duplicate)."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        mgr.add_modifier('simple_size_mount', 2.0)
        mgr.add_modifier('simple_size_mount', 3.0)

        # Should only have one modifier
        count = len([m for m in mgr.modifiers if m.definition.id == 'simple_size_mount'])
        assert count == 1
        # Should have the new value
        assert mgr.get_modifier('simple_size_mount').value == 3.0

    def test_add_modifier_returns_false_for_unknown(self, fresh_registries):
        """add_modifier should return False for unknown modifier ID."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        result = mgr.add_modifier('nonexistent_modifier', 1.0)

        assert result is False
        assert len(mgr.modifiers) == 0

    def test_add_modifier_respects_deny_types(self, fresh_registries):
        """add_modifier should respect deny_types restriction using component.type_str."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        # Create a modifier definition with deny_types that includes the railgun type
        from game.simulation.components.component_constants import Modifier
        mod_def = Modifier({
            'id': 'test_deny_mod',
            'name': 'Test Deny',
            'effects': [],
            'restrictions': {'deny_types': ['ProjectileWeaponAbility']}
        })
        fresh_registries.modifiers['test_deny_mod'] = mod_def

        result = mgr.add_modifier('test_deny_mod', 1.0)

        assert result is False
        assert len(mgr.modifiers) == 0

    def test_add_modifier_respects_allow_types(self, fresh_registries):
        """add_modifier should respect allow_types restriction."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        # Create a modifier that only allows 'Engine' type
        from game.simulation.components.component_constants import Modifier
        mod_def = Modifier({
            'id': 'test_allow_mod',
            'name': 'Test Allow',
            'effects': [],
            'restrictions': {'allow_types': ['Engine']}
        })
        fresh_registries.modifiers['test_allow_mod'] = mod_def

        result = mgr.add_modifier('test_allow_mod', 1.0)

        assert result is False
        assert len(mgr.modifiers) == 0

    def test_add_modifier_allow_types_permits_matching_type(self, fresh_registries):
        """add_modifier should allow when component type is in allow_types."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        from game.simulation.components.component_constants import Modifier
        mod_def = Modifier({
            'id': 'test_allow_match',
            'name': 'Test Allow Match',
            'effects': [],
            'restrictions': {'allow_types': ['ProjectileWeaponAbility']}
        })
        fresh_registries.modifiers['test_allow_match'] = mod_def

        result = mgr.add_modifier('test_allow_match', 1.0)

        assert result is True
        assert len(mgr.modifiers) == 1


class TestStatefulModifierManagerRemoveModifier:
    """Test stateful ModifierManager.remove_modifier instance method (PROJ-241)."""

    def test_remove_modifier_by_id(self, fresh_registries):
        """remove_modifier(mod_id) should remove the modifier from internal list."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        mgr.remove_modifier('simple_size_mount')

        assert len(mgr.modifiers) == 0
        assert mgr.get_modifier('simple_size_mount') is None

    def test_remove_modifier_preserves_others(self, fresh_registries):
        """remove_modifier should only remove the specified modifier."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)
        mgr.add_modifier('hardened_mount', 1.5)

        mgr.remove_modifier('simple_size_mount')

        assert len(mgr.modifiers) == 1
        assert mgr.modifiers[0].definition.id == 'hardened_mount'


class TestStatefulModifierManagerQuery:
    """Test stateful ModifierManager query methods (PROJ-241)."""

    def test_get_modifier_returns_correct(self, fresh_registries):
        """get_modifier(mod_id) should return correct ApplicationModifier."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        mod = mgr.get_modifier('simple_size_mount')

        assert mod is not None
        assert mod.definition.id == 'simple_size_mount'
        assert mod.value == 2.0

    def test_get_modifier_returns_none_for_missing(self, fresh_registries):
        """get_modifier should return None for modifier not in list."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        mod = mgr.get_modifier('simple_size_mount')

        assert mod is None

    def test_get_all_effects_returns_effects(self, fresh_registries):
        """get_all_effects() should return aggregated effects from internal list."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        effects = mgr.get_all_effects()

        assert len(effects) > 0
        # simple_size_mount has mass_mult and other effects
        stat_keys = {e.stat_key for e in effects}
        assert 'mass_mult' in stat_keys

    def test_get_all_effects_empty_when_no_modifiers(self, fresh_registries):
        """get_all_effects() should return empty list when no modifiers."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        effects = mgr.get_all_effects()

        assert effects == []

    def test_get_stat_summary_groups_by_stat(self, fresh_registries):
        """get_stat_summary() should group effects by stat correctly."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        summary = mgr.get_stat_summary()

        assert len(summary) > 0
        for stat_key, entry in summary.items():
            assert 'net_value' in entry
            assert 'operation' in entry
            assert 'contributors' in entry

    def test_get_stat_summary_empty_when_no_modifiers(self, fresh_registries):
        """get_stat_summary() should return empty dict when no modifiers."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        summary = mgr.get_stat_summary()

        assert summary == {}


class TestStatefulModifierManagerProperty:
    """Test stateful ModifierManager.modifiers property (PROJ-241)."""

    def test_modifiers_property_iterable(self, fresh_registries):
        """modifiers property should return an iterable list."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        mods = mgr.modifiers
        assert hasattr(mods, '__iter__')
        items = list(mods)
        assert len(items) == 1

    def test_modifiers_property_truthy_when_non_empty(self, fresh_registries):
        """modifiers property should be truthy when non-empty."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)
        mgr.add_modifier('simple_size_mount', 2.0)

        assert mgr.modifiers  # truthy

    def test_modifiers_property_falsy_when_empty(self, fresh_registries):
        """modifiers property should be falsy when empty."""
        railgun = create_component('railgun', registries=fresh_registries)
        mgr = ModifierManager(railgun)

        assert not mgr.modifiers  # falsy
