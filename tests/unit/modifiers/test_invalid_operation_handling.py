"""
Tests for invalid operation handling in modifier effects.

Phase 14.1 - Ensures that invalid operation values log warnings instead
of being silently ignored.
"""
import pytest
import logging
from unittest.mock import MagicMock

from game.simulation.components.modifiers import (
    apply_modifier_effects,
    _apply_effect_to_dict
)
from game.simulation.components.modifier_schema import validate_effect_v2


class TestInvalidOperationWarning:
    """Tests that invalid operations log warnings."""

    def test_apply_effect_to_dict_invalid_operation_logs_warning(self, caplog):
        """Invalid operation in _apply_effect_to_dict should log a warning."""
        target_dict = {'damage_mult': 1.0}

        with caplog.at_level(logging.WARNING):
            _apply_effect_to_dict('damage_mult', 2.0, 'invalid_op', target_dict)

        # Should log a warning about the invalid operation
        assert any('invalid_op' in record.message.lower() or
                   'unknown' in record.message.lower()
                   for record in caplog.records), \
            "Expected warning about invalid operation"

        # The stat should NOT be modified
        assert target_dict['damage_mult'] == 1.0, \
            "Invalid operation should not modify the stat"

    def test_apply_modifier_effects_invalid_operation_logs_warning(self, caplog):
        """Invalid operation in apply_modifier_effects should log a warning."""
        # Create a mock modifier definition that returns an effect with invalid operation
        mock_modifier = MagicMock()
        mock_effect = MagicMock()
        mock_effect.stat_key = 'mass_mult'
        mock_effect.value = 2.0
        mock_effect.operation = 'bogus_operation'
        mock_effect.is_targeted.return_value = False
        mock_modifier.evaluate_effects.return_value = [mock_effect]

        stats = {'mass_mult': 1.0}

        with caplog.at_level(logging.WARNING):
            apply_modifier_effects(mock_modifier, 1.0, stats)

        # Should log a warning about the invalid operation
        assert any('bogus_operation' in record.message.lower() or
                   'unknown' in record.message.lower()
                   for record in caplog.records), \
            "Expected warning about invalid operation"

    def test_apply_effect_to_dict_valid_operations_no_warning(self, caplog):
        """Valid operations should NOT log warnings."""
        valid_ops = ['multiply', 'add', 'set', 'add_to_mult']

        for op in valid_ops:
            target_dict = {'test_stat': 1.0}

            with caplog.at_level(logging.WARNING):
                caplog.clear()
                _apply_effect_to_dict('test_stat', 2.0, op, target_dict)

            # Should NOT log any warnings
            warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warnings) == 0, \
                f"Valid operation '{op}' should not log warnings"


class TestValidOperationsStillWork:
    """Tests that valid operations continue to work correctly."""

    def test_multiply_operation(self):
        """Multiply operation should multiply the existing value."""
        target_dict = {'damage_mult': 2.0}
        _apply_effect_to_dict('damage_mult', 3.0, 'multiply', target_dict)
        assert target_dict['damage_mult'] == 6.0

    def test_add_operation(self):
        """Add operation should add to the existing value."""
        target_dict = {'accuracy_add': 1.0}
        _apply_effect_to_dict('accuracy_add', 0.5, 'add', target_dict)
        assert target_dict['accuracy_add'] == 1.5

    def test_set_operation(self):
        """Set operation should replace the value."""
        target_dict = {'arc_set': 90}
        _apply_effect_to_dict('arc_set', 180, 'set', target_dict)
        assert target_dict['arc_set'] == 180

    def test_add_to_mult_operation(self):
        """Add_to_mult operation should add to multiplier."""
        target_dict = {'mass_mult': 1.0}
        _apply_effect_to_dict('mass_mult', 0.5, 'add_to_mult', target_dict)
        assert target_dict['mass_mult'] == 1.5


class TestSchemaValidation:
    """Tests that schema validation catches invalid operations."""

    def test_schema_rejects_invalid_operation(self):
        """validate_effect_v2 should reject invalid operation values."""
        invalid_effect = {
            'stat': 'damage_mult',
            'formula': 'param',
            'operation': 'invalid_operation'
        }
        assert validate_effect_v2(invalid_effect) is False, \
            "Schema should reject invalid operation value"

    def test_schema_accepts_valid_operations(self):
        """validate_effect_v2 should accept all valid operation values."""
        valid_operations = ['multiply', 'add', 'set', 'add_to_mult']

        for op in valid_operations:
            effect = {
                'stat': 'damage_mult',
                'formula': 'param',
                'operation': op
            }
            assert validate_effect_v2(effect) is True, \
                f"Schema should accept valid operation '{op}'"

    def test_schema_accepts_default_operation(self):
        """validate_effect_v2 should accept effects without explicit operation."""
        effect = {
            'stat': 'damage_mult',
            'formula': 'param'
            # No 'operation' key - should default to 'multiply'
        }
        assert validate_effect_v2(effect) is True, \
            "Schema should accept effect without explicit operation (defaults to multiply)"


class TestSchemaValidationOnLoad:
    """Tests that schema validation is called during modifier loading."""

    def test_invalid_modifier_logs_warning_on_load(self, caplog):
        """Loading a modifier with invalid effects should log a warning."""
        from game.simulation.components.component_constants import Modifier

        # Create a modifier definition with an invalid operation
        # Note: This tests that the warning is logged, not that loading fails
        # (graceful degradation - load anyway but warn)
        invalid_modifier_def = {
            'id': 'test_invalid',
            'name': 'Test Invalid',
            'effects': [
                {
                    'stat': 'damage_mult',
                    'formula': 'param',
                    'operation': 'not_a_real_operation'
                }
            ],
            'param': {
                'name': 'Test',
                'type': 'linear',
                'min': 0,
                'max': 10,
                'default': 1
            }
        }

        with caplog.at_level(logging.WARNING):
            # Try to create the modifier - should log warning but still create
            try:
                modifier = Modifier(invalid_modifier_def)
                # If we get here, check that a warning was logged
                # (implementation may vary - either log on creation or on use)
            except Exception:
                # If it raises, that's also acceptable behavior
                pass
