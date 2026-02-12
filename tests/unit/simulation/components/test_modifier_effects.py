"""
Unit tests for modifier_effects.py.

Tests ModifierEffect dataclass and ModifierEffectEvaluator class.
"""
import pytest
import math

from game.simulation.components.modifier_effects import ModifierEffect, ModifierEffectEvaluator
from game.core.exceptions import FormulaException


class TestModifierEffectDescribe:
    """Tests for ModifierEffect.describe method."""

    def test_effect_describe_multiply(self):
        """Multiply operation shows 'x' symbol."""
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.50,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )
        assert effect.describe() == "damage_mult x1.50"

    def test_effect_describe_add(self):
        """Add operation shows '+' symbol."""
        effect = ModifierEffect(
            stat_key='accuracy_add',
            value=0.50,
            operation='add',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=0.5
        )
        assert effect.describe() == "accuracy_add +0.50"

    def test_effect_describe_set(self):
        """Set operation shows '=' symbol."""
        effect = ModifierEffect(
            stat_key='arc_set',
            value=90.00,
            operation='set',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=90.0
        )
        assert effect.describe() == "arc_set =90.00"

    def test_effect_describe_with_target(self):
        """Includes '(on WeaponAbility)' when targeted."""
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.50,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )
        assert "(on WeaponAbility)" in effect.describe()


class TestModifierEffectIsTargeted:
    """Tests for ModifierEffect.is_targeted method."""

    def test_effect_is_targeted_true(self):
        """Returns True when target_ability is set."""
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )
        assert effect.is_targeted() is True

    def test_effect_is_targeted_false(self):
        """Returns False when target_ability is None."""
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability=None,
            source_modifier_id='test',
            source_modifier_name='Test',
            formula_str='param',
            param_value=1.5
        )
        assert effect.is_targeted() is False


class TestModifierEffectToDict:
    """Tests for ModifierEffect.to_dict method."""

    def test_effect_to_dict_all_fields(self):
        """All fields present in dict."""
        effect = ModifierEffect(
            stat_key='damage_mult',
            value=1.5,
            operation='multiply',
            target_ability='WeaponAbility',
            source_modifier_id='test_mod',
            source_modifier_name='Test Modifier',
            formula_str='param',
            param_value=1.5
        )
        d = effect.to_dict()
        assert d['stat_key'] == 'damage_mult'
        assert d['value'] == 1.5
        assert d['operation'] == 'multiply'
        assert d['target_ability'] == 'WeaponAbility'
        assert d['source_modifier_id'] == 'test_mod'
        assert d['source_modifier_name'] == 'Test Modifier'
        assert d['formula_str'] == 'param'
        assert d['param_value'] == 1.5
        assert 'description' in d


class TestEvaluateFormula:
    """Tests for ModifierEffectEvaluator.evaluate_formula method."""

    def test_formula_simple_param(self):
        """'param' with param=2.0 returns 2.0."""
        result = ModifierEffectEvaluator.evaluate_formula("param", {'param': 2.0})
        assert result == 2.0

    def test_formula_power(self):
        """'param ^ 2' with param=3.0 returns 9.0."""
        result = ModifierEffectEvaluator.evaluate_formula("param ^ 2", {'param': 3.0})
        assert result == 9.0

    def test_formula_exponential(self):
        """'2 ^ param' with param=3.0 returns 8.0."""
        result = ModifierEffectEvaluator.evaluate_formula("2 ^ param", {'param': 3.0})
        assert result == 8.0

    def test_formula_linear(self):
        """'1.0 + param * 0.5' with param=2.0 returns 2.0."""
        result = ModifierEffectEvaluator.evaluate_formula("1.0 + param * 0.5", {'param': 2.0})
        assert result == 2.0

    def test_formula_logarithmic(self):
        """'1.0 + 0.514 * ln(1 + param / 30)' evaluates correctly."""
        result = ModifierEffectEvaluator.evaluate_formula(
            "1.0 + 0.514 * ln(1 + param / 30)", {'param': 30.0}
        )
        expected = 1.0 + 0.514 * math.log(1 + 30 / 30)
        assert abs(result - expected) < 0.001

    def test_formula_syntax_error_raises(self):
        """'param +' raises FormulaException."""
        with pytest.raises(FormulaException) as exc_info:
            ModifierEffectEvaluator.evaluate_formula("param +", {'param': 1.0})
        assert exc_info.value.code == "F001"

    def test_formula_undefined_variable_raises(self):
        """'unknown_var' raises FormulaException."""
        with pytest.raises(FormulaException) as exc_info:
            ModifierEffectEvaluator.evaluate_formula("unknown_var", {'param': 1.0})
        assert exc_info.value.code == "F002"

    def test_formula_division_by_zero_raises(self):
        """'param / 0' raises FormulaException."""
        with pytest.raises(FormulaException) as exc_info:
            ModifierEffectEvaluator.evaluate_formula("param / 0", {'param': 1.0})
        assert exc_info.value.code == "F003"

    def test_formula_with_sqrt(self):
        """sqrt function works."""
        result = ModifierEffectEvaluator.evaluate_formula("sqrt(param)", {'param': 16.0})
        assert result == 4.0

    def test_formula_with_abs(self):
        """abs function works."""
        result = ModifierEffectEvaluator.evaluate_formula("abs(param)", {'param': -5.0})
        assert result == 5.0


class TestEvaluateModifier:
    """Tests for ModifierEffectEvaluator.evaluate_modifier method."""

    def test_evaluate_modifier_single_effect(self):
        """One effect produces one ModifierEffect."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)
        assert len(results) == 1
        assert results[0].stat_key == 'damage_mult'
        assert results[0].value == 2.0

    def test_evaluate_modifier_multiple_effects(self):
        """Multiple effects produce list."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'},
                {'stat': 'accuracy_add', 'formula': 'param * 0.1'}
            ]
        }
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)
        assert len(results) == 2
        assert results[0].stat_key == 'damage_mult'
        assert results[0].value == 2.0
        assert results[1].stat_key == 'accuracy_add'
        assert results[1].value == 0.2

    def test_evaluate_modifier_formula_error_fallback(self):
        """Bad formula falls back to param value."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [{'stat': 'damage_mult', 'formula': 'undefined_var'}]
        }
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)
        assert len(results) == 1
        # Should fall back to param_value
        assert results[0].value == 2.0

    def test_evaluate_modifier_with_target_ability(self):
        """target_ability passed through."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [{'stat': 'damage_mult', 'formula': 'param', 'target_ability': 'WeaponAbility'}]
        }
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 1.5)
        assert results[0].target_ability == 'WeaponAbility'

    def test_evaluate_modifier_default_operation(self):
        """Default operation is 'multiply'."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]  # No operation specified
        }
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 1.5)
        assert results[0].operation == 'multiply'

    def test_evaluate_modifier_with_stats_context(self):
        """stats_context allows referencing other stats."""
        mod_def = {
            'id': 'test',
            'name': 'Test',
            'effects': [{'stat': 'hp_mult', 'formula': 'param + mass_mult'}]
        }
        stats_context = {'mass_mult': 1.5}
        results = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0, stats_context)
        assert results[0].value == 3.5  # 2.0 + 1.5


class TestValidateFormula:
    """Tests for ModifierEffectEvaluator.validate_formula method."""

    def test_validate_formula_valid(self):
        """'param ^ 2' returns empty errors list."""
        errors = ModifierEffectEvaluator.validate_formula("param ^ 2")
        assert errors == []

    def test_validate_formula_syntax_error(self):
        """'param +' returns error."""
        errors = ModifierEffectEvaluator.validate_formula("param +")
        assert len(errors) > 0
        assert "Syntax error" in errors[0]

    def test_validate_formula_undefined_var(self):
        """'xyz' returns error about undefined var."""
        errors = ModifierEffectEvaluator.validate_formula("xyz")
        assert len(errors) > 0
        assert "Undefined variable" in errors[0]
        assert "xyz" in errors[0]

    def test_validate_formula_math_functions_allowed(self):
        """Math functions like ln, sqrt are allowed."""
        errors = ModifierEffectEvaluator.validate_formula("ln(param)")
        assert errors == []
        errors = ModifierEffectEvaluator.validate_formula("sqrt(param)")
        assert errors == []
        errors = ModifierEffectEvaluator.validate_formula("abs(param)")
        assert errors == []


class TestValidateModifierDefinition:
    """Tests for ModifierEffectEvaluator.validate_modifier_definition method."""

    def test_validate_modifier_valid(self):
        """Valid modifier returns empty errors."""
        mod_def = {
            'id': 'test',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
        assert errors == []

    def test_validate_modifier_with_bad_formula(self):
        """Bad formula in modifier returns error."""
        mod_def = {
            'id': 'test',
            'effects': [{'stat': 'damage_mult', 'formula': 'unknown_var'}]
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
        assert len(errors) > 0
        assert "test" in errors[0]

    def test_validate_modifier_no_effects(self):
        """Missing effects returns empty (not an error for validation)."""
        mod_def = {'id': 'test'}
        errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
        assert errors == []

    def test_validate_modifier_effects_not_list(self):
        """Non-list effects returns error."""
        mod_def = {
            'id': 'test',
            'effects': {'stat': 'damage_mult'}  # Should be a list
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
        assert len(errors) > 0
        assert "must be a list" in errors[0]
