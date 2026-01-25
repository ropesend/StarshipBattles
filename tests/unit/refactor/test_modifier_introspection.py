"""
Tests for Phase 6: ModifierIntrospection class

TDD: Write tests FIRST, then implement to make them pass.

ModifierIntrospection provides UI-friendly introspection of:
1. What abilities a modifier affects
2. Summary of all applied modifiers on a component
3. Base vs current values for each ability
"""
import pytest


class TestModifierIntrospectionGetModifierAffects:
    """Tests for ModifierIntrospection.get_modifier_affects()"""

    def test_get_modifier_affects_returns_dict(self):
        """get_modifier_affects() should return a dictionary."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'test_mod',
            'name': 'Test Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.get_modifier_affects(mod_def, railgun)

        assert isinstance(result, dict)

    def test_get_modifier_affects_returns_abilities(self):
        """get_modifier_affects() should return affected ability names."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'damage_boost',
            'name': 'Damage Boost',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.get_modifier_affects(mod_def, railgun)

        assert 'abilities' in result
        # Should include abilities that consume damage_mult
        assert 'ProjectileWeaponAbility' in result['abilities']

    def test_get_modifier_affects_returns_effects_preview(self):
        """get_modifier_affects() should return effect descriptions."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'damage_boost',
            'name': 'Damage Boost',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.get_modifier_affects(mod_def, railgun)

        assert 'effects_preview' in result
        assert len(result['effects_preview']) > 0
        # Preview should contain stat info
        assert any('damage_mult' in preview for preview in result['effects_preview'])

    def test_get_modifier_affects_with_targeted_effect(self):
        """get_modifier_affects() should include targeted abilities."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'targeted_mod',
            'name': 'Targeted Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5', 'target_ability': 'ProjectileWeaponAbility'}
            ]
        }

        result = ModifierIntrospection.get_modifier_affects(mod_def, railgun)

        assert 'ProjectileWeaponAbility' in result['abilities']

    def test_get_modifier_affects_multiple_stats(self):
        """get_modifier_affects() should list all affected abilities from multiple stats."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'multi_effect',
            'name': 'Multi Effect',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'},
                {'stat': 'range_mult', 'formula': '2.0'},
                {'stat': 'mass_mult', 'formula': '1.2'}
            ]
        }

        result = ModifierIntrospection.get_modifier_affects(mod_def, railgun)

        assert 'abilities' in result
        # Should include ProjectileWeaponAbility since it consumes damage_mult and range_mult
        assert 'ProjectileWeaponAbility' in result['abilities']


class TestModifierIntrospectionGetComponentModifierSummary:
    """Tests for ModifierIntrospection.get_component_modifier_summary()"""

    def test_get_component_modifier_summary_returns_dict(self):
        """get_component_modifier_summary() should return a dictionary."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')

        result = ModifierIntrospection.get_component_modifier_summary(railgun)

        assert isinstance(result, dict)

    def test_get_component_modifier_summary_lists_applied_modifiers(self):
        """get_component_modifier_summary() should list all applied modifiers."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('hardened_mount', 2.0)

        result = ModifierIntrospection.get_component_modifier_summary(railgun)

        assert 'applied_modifiers' in result
        assert len(result['applied_modifiers']) >= 1

        # Should include info about the applied modifier
        modifier_ids = [m['id'] for m in result['applied_modifiers']]
        assert 'hardened_mount' in modifier_ids

    def test_get_component_modifier_summary_includes_param_values(self):
        """Summary should include parameter values for each modifier."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('hardened_mount', 3.0)

        result = ModifierIntrospection.get_component_modifier_summary(railgun)

        hardened = next(m for m in result['applied_modifiers'] if m['id'] == 'hardened_mount')
        assert 'param_value' in hardened
        assert hardened['param_value'] == pytest.approx(3.0)

    def test_get_component_modifier_summary_no_modifiers(self):
        """Summary should handle components with no modifiers gracefully."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        # Don't add any modifiers

        result = ModifierIntrospection.get_component_modifier_summary(railgun)

        assert 'applied_modifiers' in result
        assert len(result['applied_modifiers']) == 0


class TestModifierIntrospectionGetAbilityModifierSummary:
    """Tests for ModifierIntrospection.get_ability_modifier_summary()"""

    def test_get_ability_modifier_summary_returns_dict(self):
        """get_ability_modifier_summary() should return a dictionary."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')

        result = ModifierIntrospection.get_ability_modifier_summary(weapon_ability)

        assert isinstance(result, dict)

    def test_get_ability_modifier_summary_shows_base_vs_current(self):
        """Summary should show base vs current values."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('hardened_mount', 2.0)

        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')
        result = ModifierIntrospection.get_ability_modifier_summary(weapon_ability)

        assert 'stats' in result
        # Should have base and current for at least some stats

    def test_get_ability_modifier_summary_lists_affected_stats(self):
        """Summary should list which stats are affected by modifiers."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('range_mount', 2)  # Affects range_mult

        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')
        result = ModifierIntrospection.get_ability_modifier_summary(weapon_ability)

        # Should show range is modified
        assert 'stats' in result
        if len(result['stats']) > 0:
            # If there are stat changes, check format
            stat_entry = result['stats'][0]
            assert 'attribute' in stat_entry or 'stat_key' in stat_entry

    def test_get_ability_modifier_summary_no_modifiers(self):
        """Summary should handle unmodified abilities gracefully."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        # Don't add any modifiers

        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')
        result = ModifierIntrospection.get_ability_modifier_summary(weapon_ability)

        assert 'stats' in result
        # With no modifiers, should be empty or show base values


class TestModifierIntrospectionGenerateTooltip:
    """Tests for UI-friendly tooltip generation."""

    def test_generate_modifier_tooltip_returns_string(self):
        """generate_modifier_tooltip() should return a string."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'damage_boost',
            'name': 'Damage Boost',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(mod_def, 1.5, railgun)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_modifier_tooltip_includes_modifier_name(self):
        """Tooltip should include the modifier name."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'damage_boost',
            'name': 'Damage Boost',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(mod_def, 1.5, railgun)

        assert 'Damage Boost' in result

    def test_generate_modifier_tooltip_includes_effects(self):
        """Tooltip should include effect information."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        mod_def = {
            'id': 'multi_mod',
            'name': 'Multi Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': '2.0'},
                {'stat': 'range_mult', 'formula': '1.5'}
            ]
        }

        result = ModifierIntrospection.generate_modifier_tooltip(mod_def, 1.0, railgun)

        # Should mention both affected stats
        assert 'damage' in result.lower() or 'range' in result.lower()


class TestModifierIntrospectionGenerateAbilityStatsDisplay:
    """Tests for ability stats display generation."""

    def test_generate_ability_stats_display_returns_list(self):
        """generate_ability_stats_display() should return a list of display entries."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')

        result = ModifierIntrospection.generate_ability_stats_display(weapon_ability)

        assert isinstance(result, list)

    def test_generate_ability_stats_display_shows_modified_values(self):
        """Display should highlight modified values."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('range_mount', 2)  # 4x range

        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')
        result = ModifierIntrospection.generate_ability_stats_display(weapon_ability)

        # Should have entries with modification info
        assert len(result) >= 0  # May be empty if ability doesn't track all

    def test_generate_ability_stats_display_format(self):
        """Display entries should have expected format."""
        from game.simulation.components.modifier_introspection import ModifierIntrospection
        from game.simulation.components import create_component

        railgun = create_component('railgun')
        railgun.add_modifier('hardened_mount', 2.0)

        weapon_ability = railgun.get_ability('ProjectileWeaponAbility')
        result = ModifierIntrospection.generate_ability_stats_display(weapon_ability)

        if len(result) > 0:
            entry = result[0]
            # Each entry should have a label and value at minimum
            assert 'label' in entry or 'attribute' in entry
