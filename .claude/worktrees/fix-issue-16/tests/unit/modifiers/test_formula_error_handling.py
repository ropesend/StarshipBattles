"""
Tests for formula error handling in modifier effect evaluation.

Task 8.1: Verify that formula errors are logged, not silently swallowed.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock

from game.simulation.components.modifier_effects import ModifierEffectEvaluator


class TestFormulaErrorHandling:
    """Tests to verify formula errors are properly logged."""

    def test_malformed_formula_logs_error(self, caplog):
        """Formula syntax error should log error, not silently fallback."""
        mod_def = {
            'id': 'test_malformed',
            'name': 'Test Malformed',
            'effects': [
                {'stat': 'damage_mult', 'formula': '2 ^ ^ param'}  # Invalid syntax
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        # Should still return an effect (fallback behavior)
        assert len(effects) == 1
        # But should have logged an error
        assert any('formula' in record.message.lower() or 'error' in record.message.lower()
                   for record in caplog.records), \
            "Expected error log for malformed formula"

    def test_undefined_variable_logs_error(self, caplog):
        """Undefined variable in formula should log error."""
        mod_def = {
            'id': 'test_undefined',
            'name': 'Test Undefined',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'undefined_var + param'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert len(effects) == 1
        assert any('formula' in record.message.lower() or 'undefined' in record.message.lower()
                   for record in caplog.records), \
            "Expected error log for undefined variable"

    def test_math_domain_error_logs_error(self, caplog):
        """Math errors like ln(-1) should log error."""
        mod_def = {
            'id': 'test_domain',
            'name': 'Test Domain Error',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'ln(-1)'}  # Invalid - ln of negative
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert len(effects) == 1
        assert any('formula' in record.message.lower() or 'error' in record.message.lower()
                   for record in caplog.records), \
            "Expected error log for math domain error"

    def test_division_by_zero_logs_error(self, caplog):
        """Division by zero should log error."""
        mod_def = {
            'id': 'test_div_zero',
            'name': 'Test Div Zero',
            'effects': [
                {'stat': 'reload_mult', 'formula': '1.0 / param'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            # param = 0 causes division by zero
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        assert len(effects) == 1
        assert any('formula' in record.message.lower() or 'zero' in record.message.lower() or 'error' in record.message.lower()
                   for record in caplog.records), \
            "Expected error log for division by zero"

    def test_valid_formula_no_error_log(self, caplog):
        """Valid formulas should not produce error logs."""
        mod_def = {
            'id': 'test_valid',
            'name': 'Test Valid',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param ^ 2'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        assert len(effects) == 1
        assert effects[0].value == 4.0  # 2^2 = 4
        # No error logs for valid formula
        assert not any('error' in record.message.lower() for record in caplog.records), \
            "Should not log error for valid formula"

    def test_fallback_value_is_param(self, caplog):
        """When formula fails, fallback should be the param value."""
        mod_def = {
            'id': 'test_fallback',
            'name': 'Test Fallback',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'invalid syntax here'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 3.5)

        assert len(effects) == 1
        # Fallback should be param value
        assert effects[0].value == 3.5
        # And error should be logged
        assert len(caplog.records) > 0, "Should have logged an error"

    def test_error_log_includes_formula_string(self, caplog):
        """Error log should include the formula that failed."""
        bad_formula = '((( malformed'
        mod_def = {
            'id': 'test_info',
            'name': 'Test Info',
            'effects': [
                {'stat': 'damage_mult', 'formula': bad_formula}
            ]
        }

        with caplog.at_level(logging.ERROR):
            ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        # Error message should contain the formula
        error_messages = [r.message for r in caplog.records if r.levelno >= logging.ERROR]
        assert any(bad_formula in msg or 'malformed' in msg.lower() for msg in error_messages), \
            f"Error message should include formula string. Got: {error_messages}"

    def test_error_log_includes_modifier_id(self, caplog):
        """Error log should include the modifier ID for debugging."""
        mod_def = {
            'id': 'my_broken_modifier',
            'name': 'Broken',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'bad bad bad'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            ModifierEffectEvaluator.evaluate_modifier(mod_def, 2.0)

        error_messages = [r.message for r in caplog.records if r.levelno >= logging.ERROR]
        assert any('my_broken_modifier' in msg for msg in error_messages), \
            f"Error message should include modifier ID. Got: {error_messages}"
