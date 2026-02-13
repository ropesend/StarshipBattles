"""
Unit tests for modifier_schema.py.

Tests V2 format validation functions for modifiers.
"""
import pytest

from game.simulation.components.modifier_schema import (
    is_v2_format,
    validate_effect_v2,
    normalize_effect_v2,
    validate_param_v2,
    validate_restrictions_v2,
    validate_modifier_v2
)


class TestIsV2Format:
    """Tests for is_v2_format function."""

    def test_v2_format_list_effects_true(self):
        """{'effects': []} returns True."""
        modifier = {'effects': []}
        assert is_v2_format(modifier) is True

    def test_v2_format_list_with_effects_true(self):
        """{'effects': [...]} returns True."""
        modifier = {'effects': [{'stat': 'damage_mult', 'formula': 'param'}]}
        assert is_v2_format(modifier) is True

    def test_dict_effects_returns_false(self):
        """{'effects': {}} returns False (not V2 format)."""
        modifier = {'id': 'test', 'effects': {}}
        assert is_v2_format(modifier) is False

    def test_dict_with_data_returns_false(self):
        """{'effects': {'special': ...}} returns False (not V2 format)."""
        modifier = {'id': 'test', 'effects': {'special': 'some_handler'}}
        assert is_v2_format(modifier) is False

    def test_no_effects_key_false(self):
        """{} returns False."""
        modifier = {}
        assert is_v2_format(modifier) is False

    def test_effects_not_list_or_dict_false(self):
        """{'effects': 'string'} returns False."""
        modifier = {'effects': 'string'}
        assert is_v2_format(modifier) is False

    def test_effects_integer_false(self):
        """{'effects': 123} returns False."""
        modifier = {'effects': 123}
        assert is_v2_format(modifier) is False


class TestValidateEffectV2:
    """Tests for validate_effect_v2 function."""

    def test_valid_effect_minimal(self):
        """{'stat': 'x', 'formula': 'param'} is valid."""
        effect = {'stat': 'damage_mult', 'formula': 'param'}
        assert validate_effect_v2(effect) is True

    def test_effect_missing_stat_invalid(self):
        """{'formula': 'param'} is invalid."""
        effect = {'formula': 'param'}
        assert validate_effect_v2(effect) is False

    def test_effect_missing_formula_invalid(self):
        """{'stat': 'x'} is invalid."""
        effect = {'stat': 'damage_mult'}
        assert validate_effect_v2(effect) is False

    def test_effect_non_dict_invalid(self):
        """'string' is invalid."""
        assert validate_effect_v2("string") is False
        assert validate_effect_v2(123) is False
        assert validate_effect_v2(None) is False

    def test_effect_valid_operation_multiply(self):
        """operation: 'multiply' is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'multiply'}
        assert validate_effect_v2(effect) is True

    def test_effect_valid_operation_add(self):
        """operation: 'add' is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'add'}
        assert validate_effect_v2(effect) is True

    def test_effect_valid_operation_set(self):
        """operation: 'set' is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'set'}
        assert validate_effect_v2(effect) is True

    def test_effect_valid_operation_add_to_mult(self):
        """operation: 'add_to_mult' is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'add_to_mult'}
        assert validate_effect_v2(effect) is True

    def test_effect_invalid_operation(self):
        """'divide' is invalid operation."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'divide'}
        assert validate_effect_v2(effect) is False

    def test_effect_target_ability_string_valid(self):
        """target_ability: 'WeaponAbility' is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'target_ability': 'WeaponAbility'}
        assert validate_effect_v2(effect) is True

    def test_effect_target_ability_non_string_invalid(self):
        """target_ability: 123 is invalid."""
        effect = {'stat': 'x', 'formula': 'param', 'target_ability': 123}
        assert validate_effect_v2(effect) is False

    def test_effect_depends_on_list_valid(self):
        """depends_on: ['a', 'b'] is valid."""
        effect = {'stat': 'x', 'formula': 'param', 'depends_on': ['a', 'b']}
        assert validate_effect_v2(effect) is True

    def test_effect_depends_on_non_list_invalid(self):
        """depends_on: 'a' is invalid."""
        effect = {'stat': 'x', 'formula': 'param', 'depends_on': 'a'}
        assert validate_effect_v2(effect) is False

    def test_effect_depends_on_non_string_item_invalid(self):
        """depends_on: [123] is invalid."""
        effect = {'stat': 'x', 'formula': 'param', 'depends_on': [123]}
        assert validate_effect_v2(effect) is False

    def test_effect_stat_non_string_invalid(self):
        """stat: 123 is invalid."""
        effect = {'stat': 123, 'formula': 'param'}
        assert validate_effect_v2(effect) is False

    def test_effect_formula_non_string_invalid(self):
        """formula: 123 is invalid."""
        effect = {'stat': 'x', 'formula': 123}
        assert validate_effect_v2(effect) is False


class TestNormalizeEffectV2:
    """Tests for normalize_effect_v2 function."""

    def test_normalize_adds_default_operation(self):
        """Missing operation gets 'multiply'."""
        effect = {'stat': 'x', 'formula': 'param'}
        normalized = normalize_effect_v2(effect)
        assert normalized['operation'] == 'multiply'

    def test_normalize_preserves_existing_operation(self):
        """Existing 'add' operation is unchanged."""
        effect = {'stat': 'x', 'formula': 'param', 'operation': 'add'}
        normalized = normalize_effect_v2(effect)
        assert normalized['operation'] == 'add'

    def test_normalize_does_not_modify_original(self):
        """Original effect dict is not modified."""
        effect = {'stat': 'x', 'formula': 'param'}
        normalize_effect_v2(effect)
        assert 'operation' not in effect


class TestValidateParamV2:
    """Tests for validate_param_v2 function."""

    def test_valid_param(self):
        """Complete param definition is valid."""
        param = {'name': 'x', 'type': 'linear', 'min': 0, 'max': 100, 'default': 50}
        assert validate_param_v2(param) is True

    def test_param_missing_required_field_name(self):
        """Missing 'name' is invalid."""
        param = {'type': 'linear', 'min': 0, 'max': 100, 'default': 50}
        assert validate_param_v2(param) is False

    def test_param_missing_required_field_type(self):
        """Missing 'type' is invalid."""
        param = {'name': 'x', 'min': 0, 'max': 100, 'default': 50}
        assert validate_param_v2(param) is False

    def test_param_missing_required_field_min(self):
        """Missing 'min' is invalid."""
        param = {'name': 'x', 'type': 'linear', 'max': 100, 'default': 50}
        assert validate_param_v2(param) is False

    def test_param_non_numeric_min(self):
        """min: 'zero' is invalid."""
        param = {'name': 'x', 'type': 'linear', 'min': 'zero', 'max': 100, 'default': 50}
        assert validate_param_v2(param) is False

    def test_param_non_numeric_max(self):
        """max: 'hundred' is invalid."""
        param = {'name': 'x', 'type': 'linear', 'min': 0, 'max': 'hundred', 'default': 50}
        assert validate_param_v2(param) is False

    def test_param_non_numeric_default(self):
        """default: 'fifty' is invalid."""
        param = {'name': 'x', 'type': 'linear', 'min': 0, 'max': 100, 'default': 'fifty'}
        assert validate_param_v2(param) is False

    def test_param_non_dict_invalid(self):
        """'string' is invalid."""
        assert validate_param_v2("string") is False

    def test_param_float_values_valid(self):
        """Float values for min/max/default are valid."""
        param = {'name': 'x', 'type': 'linear', 'min': 0.5, 'max': 2.5, 'default': 1.0}
        assert validate_param_v2(param) is True

    def test_param_name_non_string_invalid(self):
        """name: 123 is invalid."""
        param = {'name': 123, 'type': 'linear', 'min': 0, 'max': 100, 'default': 50}
        assert validate_param_v2(param) is False


class TestValidateRestrictionsV2:
    """Tests for validate_restrictions_v2 function."""

    def test_valid_restrictions(self):
        """{'allow_abilities': ['WeaponAbility']} is valid."""
        restrictions = {'allow_abilities': ['WeaponAbility']}
        assert validate_restrictions_v2(restrictions) is True

    def test_valid_restrictions_with_deny(self):
        """deny_abilities list is valid."""
        restrictions = {'deny_abilities': ['ShieldAbility']}
        assert validate_restrictions_v2(restrictions) is True

    def test_valid_restrictions_require_mode_any(self):
        """require_mode: 'any' is valid."""
        restrictions = {'allow_abilities': ['A'], 'require_mode': 'any'}
        assert validate_restrictions_v2(restrictions) is True

    def test_valid_restrictions_require_mode_all(self):
        """require_mode: 'all' is valid."""
        restrictions = {'allow_abilities': ['A'], 'require_mode': 'all'}
        assert validate_restrictions_v2(restrictions) is True

    def test_restrictions_invalid_require_mode(self):
        """require_mode: 'some' is invalid."""
        restrictions = {'allow_abilities': ['A'], 'require_mode': 'some'}
        assert validate_restrictions_v2(restrictions) is False

    def test_restrictions_non_string_ability(self):
        """allow_abilities: [123] is invalid."""
        restrictions = {'allow_abilities': [123]}
        assert validate_restrictions_v2(restrictions) is False

    def test_restrictions_deny_non_string_ability(self):
        """deny_abilities: [123] is invalid."""
        restrictions = {'deny_abilities': [123]}
        assert validate_restrictions_v2(restrictions) is False

    def test_restrictions_non_dict_invalid(self):
        """'string' is invalid."""
        assert validate_restrictions_v2("string") is False

    def test_restrictions_allow_abilities_non_list_invalid(self):
        """allow_abilities: 'WeaponAbility' is invalid."""
        restrictions = {'allow_abilities': 'WeaponAbility'}
        assert validate_restrictions_v2(restrictions) is False

    def test_empty_restrictions_valid(self):
        """Empty restrictions dict is valid."""
        restrictions = {}
        assert validate_restrictions_v2(restrictions) is True


class TestValidateModifierV2:
    """Tests for validate_modifier_v2 function."""

    def test_valid_modifier_complete(self):
        """Full modifier definition is valid."""
        modifier = {
            'id': 'test_mod',
            'name': 'Test Modifier',
            'description': 'A test',
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}],
            'param': {'name': 'Level', 'type': 'linear', 'min': 1, 'max': 10, 'default': 5},
            'restrictions': {'allow_abilities': ['WeaponAbility']}
        }
        assert validate_modifier_v2(modifier) is True

    def test_modifier_missing_id(self):
        """No id is invalid."""
        modifier = {
            'effects': [{'stat': 'damage_mult', 'formula': 'param'}]
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_missing_effects(self):
        """No effects is invalid."""
        modifier = {'id': 'test'}
        assert validate_modifier_v2(modifier) is False

    def test_modifier_empty_effects(self):
        """Empty effects array is invalid."""
        modifier = {'id': 'test', 'effects': []}
        assert validate_modifier_v2(modifier) is False

    def test_modifier_invalid_effect_propagates(self):
        """Bad effect invalidates modifier."""
        modifier = {
            'id': 'test',
            'effects': [{'stat': 'x'}]  # Missing formula
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_invalid_param_propagates(self):
        """Bad param invalidates modifier."""
        modifier = {
            'id': 'test',
            'effects': [{'stat': 'x', 'formula': 'param'}],
            'param': {'name': 'Level'}  # Missing required fields
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_invalid_restrictions_propagates(self):
        """Bad restrictions invalidates modifier."""
        modifier = {
            'id': 'test',
            'effects': [{'stat': 'x', 'formula': 'param'}],
            'restrictions': {'allow_abilities': 'not_a_list'}
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_non_dict_invalid(self):
        """Non-dict modifier is invalid."""
        assert validate_modifier_v2("string") is False

    def test_modifier_id_non_string_invalid(self):
        """Non-string id is invalid."""
        modifier = {
            'id': 123,
            'effects': [{'stat': 'x', 'formula': 'param'}]
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_effects_non_list_invalid(self):
        """Non-list effects is invalid."""
        modifier = {
            'id': 'test',
            'effects': {'stat': 'x', 'formula': 'param'}
        }
        assert validate_modifier_v2(modifier) is False

    def test_modifier_invalid_formula_propagates(self):
        """Invalid formula syntax invalidates modifier."""
        modifier = {
            'id': 'test',
            'effects': [{'stat': 'x', 'formula': 'param +'}]  # Bad syntax
        }
        assert validate_modifier_v2(modifier) is False
