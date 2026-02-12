"""
Unit tests for modifiers.py.

Tests _apply_effect_to_dict, get_default_stat_multipliers,
apply_modifier_effects, and calculate_stat_multipliers.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.simulation.components.modifiers import (
    _apply_effect_to_dict,
    get_default_stat_multipliers,
    apply_modifier_effects,
    calculate_stat_multipliers
)


class TestApplyEffectToDict:
    """Tests for _apply_effect_to_dict function."""

    def test_multiply_existing_key(self):
        """stats['x'] *= value."""
        stats = {'damage_mult': 2.0}
        _apply_effect_to_dict('damage_mult', 1.5, 'multiply', stats)
        assert stats['damage_mult'] == 3.0

    def test_multiply_new_key(self):
        """stats['x'] = value (no prior key)."""
        stats = {}
        _apply_effect_to_dict('damage_mult', 1.5, 'multiply', stats)
        assert stats['damage_mult'] == 1.5

    def test_add_existing_key(self):
        """stats['x'] += value."""
        stats = {'accuracy_add': 0.3}
        _apply_effect_to_dict('accuracy_add', 0.2, 'add', stats)
        assert abs(stats['accuracy_add'] - 0.5) < 0.001

    def test_add_new_key(self):
        """stats['x'] = value."""
        stats = {}
        _apply_effect_to_dict('accuracy_add', 0.2, 'add', stats)
        assert stats['accuracy_add'] == 0.2

    def test_set_key(self):
        """stats['x'] = value (always overwrite)."""
        stats = {'arc_set': 45.0}
        _apply_effect_to_dict('arc_set', 90.0, 'set', stats)
        assert stats['arc_set'] == 90.0

    def test_set_new_key(self):
        """stats['x'] = value (new key)."""
        stats = {}
        _apply_effect_to_dict('arc_set', 90.0, 'set', stats)
        assert stats['arc_set'] == 90.0

    def test_add_to_mult_existing(self):
        """stats['x'] += value."""
        stats = {'mass_mult': 1.0}
        _apply_effect_to_dict('mass_mult', 0.5, 'add_to_mult', stats)
        assert stats['mass_mult'] == 1.5

    def test_add_to_mult_new(self):
        """stats['x'] = 1.0 + value."""
        stats = {}
        _apply_effect_to_dict('mass_mult', 0.5, 'add_to_mult', stats)
        assert stats['mass_mult'] == 1.5

    def test_unknown_operation_logged(self, caplog):
        """Warning logged, no crash."""
        stats = {'damage_mult': 1.0}
        _apply_effect_to_dict('damage_mult', 1.5, 'divide', stats)
        # Value should be unchanged
        assert stats['damage_mult'] == 1.0
        assert "Unknown operation" in caplog.text


class TestGetDefaultStatMultipliers:
    """Tests for get_default_stat_multipliers function."""

    def test_defaults_mass_mult_is_1(self):
        """mass_mult starts at 1.0."""
        stats = get_default_stat_multipliers()
        assert stats['mass_mult'] == 1.0

    def test_defaults_mass_add_is_0(self):
        """mass_add starts at 0.0."""
        stats = get_default_stat_multipliers()
        assert stats['mass_add'] == 0.0

    def test_defaults_arc_set_is_none(self):
        """arc_set starts at None."""
        stats = get_default_stat_multipliers()
        assert stats['arc_set'] is None

    def test_defaults_has_properties_dict(self):
        """properties key exists as empty dict."""
        stats = get_default_stat_multipliers()
        assert 'properties' in stats
        assert isinstance(stats['properties'], dict)

    def test_defaults_all_mult_stats_are_1(self):
        """All *_mult stats are 1.0."""
        stats = get_default_stat_multipliers()
        mult_keys = [k for k in stats.keys() if k.endswith('_mult')]
        for key in mult_keys:
            assert stats[key] == 1.0, f"{key} should be 1.0"

    def test_defaults_all_add_stats_are_0(self):
        """All *_add stats are 0.0."""
        stats = get_default_stat_multipliers()
        add_keys = [k for k in stats.keys() if k.endswith('_add')]
        for key in add_keys:
            assert stats[key] == 0.0, f"{key} should be 0.0"


class TestApplyModifierEffects:
    """Tests for apply_modifier_effects function."""

    @pytest.fixture
    def mock_modifier_def(self):
        """Create a mock modifier definition."""
        mock_def = MagicMock()
        return mock_def

    @pytest.fixture
    def mock_effect(self):
        """Create a mock ModifierEffect."""
        effect = MagicMock()
        effect.stat_key = 'damage_mult'
        effect.value = 1.5
        effect.operation = 'multiply'
        effect.is_targeted.return_value = False
        return effect

    def test_apply_multiply_effect(self, mock_modifier_def, mock_effect):
        """Multiplicative effect applied to stats."""
        mock_modifier_def.evaluate_effects.return_value = [mock_effect]

        stats = {'damage_mult': 2.0}
        apply_modifier_effects(mock_modifier_def, 1.0, stats)

        assert stats['damage_mult'] == 3.0

    def test_apply_add_effect(self, mock_modifier_def):
        """Additive effect applied to stats."""
        effect = MagicMock()
        effect.stat_key = 'accuracy_add'
        effect.value = 0.1
        effect.operation = 'add'
        effect.is_targeted.return_value = False
        mock_modifier_def.evaluate_effects.return_value = [effect]

        stats = {'accuracy_add': 0.2}
        apply_modifier_effects(mock_modifier_def, 1.0, stats)

        assert abs(stats['accuracy_add'] - 0.3) < 0.001

    def test_apply_set_effect(self, mock_modifier_def):
        """Set effect overwrites stats."""
        effect = MagicMock()
        effect.stat_key = 'arc_set'
        effect.value = 90.0
        effect.operation = 'set'
        effect.is_targeted.return_value = False
        mock_modifier_def.evaluate_effects.return_value = [effect]

        stats = {'arc_set': None}
        apply_modifier_effects(mock_modifier_def, 1.0, stats)

        assert stats['arc_set'] == 90.0

    def test_apply_targeted_effect_to_ability_stats(self, mock_modifier_def):
        """Targeted effect goes to component.ability_stats."""
        effect = MagicMock()
        effect.stat_key = 'damage_mult'
        effect.value = 1.5
        effect.operation = 'multiply'
        effect.is_targeted.return_value = True
        effect.target_ability = 'WeaponAbility'
        mock_modifier_def.evaluate_effects.return_value = [effect]

        component = MagicMock()
        component.ability_stats = {}

        stats = {'damage_mult': 1.0}
        apply_modifier_effects(mock_modifier_def, 1.0, stats, component=component)

        # Should NOT modify global stats
        assert stats['damage_mult'] == 1.0
        # Should modify ability_stats
        assert 'WeaponAbility' in component.ability_stats
        assert component.ability_stats['WeaponAbility']['damage_mult'] == 1.5

    def test_apply_null_effects_no_crash(self, mock_modifier_def):
        """evaluate_effects returns None -> no crash."""
        mock_modifier_def.evaluate_effects.return_value = None

        stats = {'damage_mult': 1.0}
        # Should not raise
        apply_modifier_effects(mock_modifier_def, 1.0, stats)

        assert stats['damage_mult'] == 1.0


class TestCalculateStatMultipliers:
    """Tests for calculate_stat_multipliers function."""

    def test_calculate_with_no_modifiers(self):
        """Returns defaults with empty modifier list."""
        stats = calculate_stat_multipliers([], {})
        assert stats['mass_mult'] == 1.0
        assert stats['mass_add'] == 0.0

    def test_calculate_with_single_modifier(self):
        """Single modifier applied correctly."""
        # Create mock modifier
        mock_effect = MagicMock()
        mock_effect.stat_key = 'damage_mult'
        mock_effect.value = 1.5
        mock_effect.operation = 'multiply'
        mock_effect.is_targeted.return_value = False

        mock_def = MagicMock()
        mock_def.evaluate_effects.return_value = [mock_effect]

        modifier_entries = [{'id': 'test_mod', 'value': 50.0}]
        modifier_registry = {'test_mod': mock_def}

        stats = calculate_stat_multipliers(modifier_entries, modifier_registry)

        assert stats['damage_mult'] == 1.5

    def test_calculate_with_unknown_modifier_id(self):
        """Unknown ID silently skipped."""
        modifier_entries = [{'id': 'nonexistent_mod', 'value': 50.0}]
        modifier_registry = {}  # Empty

        stats = calculate_stat_multipliers(modifier_entries, modifier_registry)

        # Should return defaults
        assert stats['mass_mult'] == 1.0

    def test_calculate_multiple_modifiers(self):
        """Multiple modifiers stack."""
        # First modifier: damage_mult *= 1.5
        mock_effect1 = MagicMock()
        mock_effect1.stat_key = 'damage_mult'
        mock_effect1.value = 1.5
        mock_effect1.operation = 'multiply'
        mock_effect1.is_targeted.return_value = False

        mock_def1 = MagicMock()
        mock_def1.evaluate_effects.return_value = [mock_effect1]

        # Second modifier: damage_mult *= 2.0
        mock_effect2 = MagicMock()
        mock_effect2.stat_key = 'damage_mult'
        mock_effect2.value = 2.0
        mock_effect2.operation = 'multiply'
        mock_effect2.is_targeted.return_value = False

        mock_def2 = MagicMock()
        mock_def2.evaluate_effects.return_value = [mock_effect2]

        modifier_entries = [
            {'id': 'mod1', 'value': 50.0},
            {'id': 'mod2', 'value': 50.0}
        ]
        modifier_registry = {'mod1': mock_def1, 'mod2': mock_def2}

        stats = calculate_stat_multipliers(modifier_entries, modifier_registry)

        # 1.0 * 1.5 * 2.0 = 3.0
        assert stats['damage_mult'] == 3.0
