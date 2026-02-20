"""
Tests for formula edge cases in modifier effect evaluation.

Task 9.3: Verify that edge cases like division by zero, negative params,
overflow, and math domain errors are handled gracefully.
"""
import pytest
import logging
import math

from game.simulation.components.modifier_effects import ModifierEffectEvaluator


class TestFormulaDivisionByZero:
    """Tests for division by zero handling."""

    def test_formula_division_by_zero(self, caplog):
        """Formula '1.0 / param' with param=0 should handle gracefully."""
        mod_def = {
            'id': 'test_div_zero',
            'name': 'Test Div Zero',
            'effects': [
                {'stat': 'reload_mult', 'formula': '1.0 / param'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        # Should return an effect (fallback behavior)
        assert len(effects) == 1
        # Fallback value should be the param (0.0)
        assert effects[0].value == 0.0
        # Should have logged an error
        assert any('error' in record.message.lower() or 'division' in record.message.lower()
                   for record in caplog.records)

    def test_formula_division_by_small_positive(self):
        """Formula '1.0 / param' with very small param should produce large result."""
        mod_def = {
            'id': 'test_div_small',
            'name': 'Test Div Small',
            'effects': [
                {'stat': 'reload_mult', 'formula': '1.0 / param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.001)

        assert len(effects) == 1
        assert effects[0].value == pytest.approx(1000.0, rel=1e-6)


class TestFormulaNegativeParams:
    """Tests for negative parameter handling."""

    def test_formula_negative_param_linear(self):
        """Formulas should handle negative parameter values in linear operations."""
        mod_def = {
            'id': 'test_negative',
            'name': 'Test Negative',
            'effects': [
                {'stat': 'damage_mult', 'formula': '1.0 + param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, -0.5)

        assert len(effects) == 1
        assert effects[0].value == pytest.approx(0.5, rel=1e-6)

    def test_formula_negative_param_multiply(self):
        """Formulas should handle negative parameter in multiplication."""
        mod_def = {
            'id': 'test_neg_mult',
            'name': 'Test Neg Mult',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'param * 2'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, -3.0)

        assert len(effects) == 1
        assert effects[0].value == pytest.approx(-6.0, rel=1e-6)

    def test_formula_sqrt_negative_param(self, caplog):
        """Formula 'sqrt(param)' with negative param should handle gracefully."""
        mod_def = {
            'id': 'test_sqrt_neg',
            'name': 'Test Sqrt Neg',
            'effects': [
                {'stat': 'cost_mult', 'formula': 'sqrt(param)'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, -1.0)

        # Should return an effect (fallback behavior)
        assert len(effects) == 1
        # Should have logged an error
        assert any('error' in record.message.lower() for record in caplog.records)


class TestFormulaLargeParams:
    """Tests for large parameter value handling."""

    def test_formula_large_param_exponential(self, caplog):
        """Formula '3.5 ^ param' with large param should handle overflow gracefully."""
        mod_def = {
            'id': 'test_overflow',
            'name': 'Test Overflow',
            'effects': [
                {'stat': 'mass_mult', 'formula': '3.5 ^ param'}
            ]
        }

        # param=1000 would give 3.5^1000 which is astronomically large
        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 1000.0)

        # Should return an effect (either very large or fallback)
        assert len(effects) == 1
        # Result might be inf or fallback to param value
        assert effects[0].value == float('inf') or effects[0].value == 1000.0

    def test_formula_reasonable_large_param(self):
        """Formula should handle reasonably large params correctly."""
        mod_def = {
            'id': 'test_large',
            'name': 'Test Large',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 1000000.0)

        assert len(effects) == 1
        assert effects[0].value == 1000000.0


class TestFormulaLogDomainErrors:
    """Tests for logarithm domain error handling."""

    def test_formula_ln_of_zero(self, caplog):
        """Formula 'ln(param)' with param=0 should handle gracefully."""
        mod_def = {
            'id': 'test_ln_zero',
            'name': 'Test Ln Zero',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'ln(param)'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        # Should return an effect (fallback behavior)
        assert len(effects) == 1
        # Should have logged an error
        assert any('error' in record.message.lower() for record in caplog.records)

    def test_formula_ln_of_negative(self, caplog):
        """Formula 'ln(param)' with param=-1 should handle gracefully."""
        mod_def = {
            'id': 'test_ln_neg',
            'name': 'Test Ln Neg',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'ln(param)'}
            ]
        }

        with caplog.at_level(logging.ERROR):
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, -1.0)

        # Should return an effect (fallback behavior)
        assert len(effects) == 1
        # Should have logged an error
        assert any('error' in record.message.lower() for record in caplog.records)

    def test_formula_ln_of_positive(self):
        """Formula 'ln(param)' with positive param should work correctly."""
        mod_def = {
            'id': 'test_ln_pos',
            'name': 'Test Ln Pos',
            'effects': [
                {'stat': 'mass_mult', 'formula': 'ln(param)'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, math.e)

        assert len(effects) == 1
        assert effects[0].value == pytest.approx(1.0, rel=1e-6)


class TestFormulaZeroParam:
    """Tests for zero parameter handling."""

    def test_formula_zero_param_direct(self):
        """Formula 'param' with param=0 should return 0."""
        mod_def = {
            'id': 'test_zero',
            'name': 'Test Zero',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        assert len(effects) == 1
        assert effects[0].value == 0.0

    def test_formula_zero_param_in_addition(self):
        """Formula '1.0 + param' with param=0 should return 1.0."""
        mod_def = {
            'id': 'test_zero_add',
            'name': 'Test Zero Add',
            'effects': [
                {'stat': 'mass_mult', 'formula': '1.0 + param'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        assert len(effects) == 1
        assert effects[0].value == 1.0

    def test_formula_power_of_zero(self):
        """Formula 'param ^ 2' with param=0 should return 0."""
        mod_def = {
            'id': 'test_power_zero',
            'name': 'Test Power Zero',
            'effects': [
                {'stat': 'hp_mult', 'formula': 'param ^ 2'}
            ]
        }

        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)

        assert len(effects) == 1
        assert effects[0].value == 0.0


class TestRealWorldFormulas:
    """Tests for actual formulas used in the game's modifiers.json."""

    def test_hardened_mount_formula(self):
        """Test hardened_mount formula: hp_mult = param ^ 2."""
        mod_def = {
            'id': 'hardened_mount',
            'name': 'Hardened Mount',
            'effects': [
                {'stat': 'hp_mult', 'formula': 'param ^ 2'}
            ]
        }

        # Test several values
        for param, expected in [(1.0, 1.0), (2.0, 4.0), (3.0, 9.0), (0.5, 0.25)]:
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param)
            assert len(effects) == 1
            assert effects[0].value == pytest.approx(expected, rel=1e-6), \
                f"param={param} should give {expected}"

    def test_range_mount_formula(self):
        """Test range_mount formula: range_mult = 2 ^ param."""
        mod_def = {
            'id': 'range_mount',
            'name': 'Range Mount',
            'effects': [
                {'stat': 'range_mult', 'formula': '2 ^ param'}
            ]
        }

        for param, expected in [(0.0, 1.0), (1.0, 2.0), (2.0, 4.0), (3.0, 8.0)]:
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param)
            assert len(effects) == 1
            assert effects[0].value == pytest.approx(expected, rel=1e-6), \
                f"param={param} should give {expected}"

    def test_turret_mount_logarithmic_formula(self):
        """Test turret_mount formula: 1.0 + 0.514 * ln(1.0 + param / 30.0)."""
        mod_def = {
            'id': 'turret_mount',
            'name': 'Turret Mount',
            'effects': [
                {'stat': 'mass_mult', 'formula': '1.0 + 0.514 * ln(1.0 + param / 30.0)'}
            ]
        }

        # At param=0, should be 1.0 + 0.514 * ln(1.0) = 1.0 + 0 = 1.0
        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 0.0)
        assert len(effects) == 1
        assert effects[0].value == pytest.approx(1.0, rel=1e-6)

        # At param=30, should be 1.0 + 0.514 * ln(2.0) ≈ 1.356
        effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, 30.0)
        expected = 1.0 + 0.514 * math.log(2.0)
        assert effects[0].value == pytest.approx(expected, rel=1e-6)

    def test_rapid_fire_inverse_formula(self):
        """Test rapid_fire formula: reload_mult = 1.0 / param."""
        mod_def = {
            'id': 'rapid_fire',
            'name': 'Rapid Fire',
            'effects': [
                {'stat': 'reload_mult', 'formula': '1.0 / param'}
            ]
        }

        for param, expected in [(1.0, 1.0), (2.0, 0.5), (4.0, 0.25)]:
            effects = ModifierEffectEvaluator.evaluate_modifier(mod_def, param)
            assert len(effects) == 1
            assert effects[0].value == pytest.approx(expected, rel=1e-6), \
                f"param={param} should give {expected}"
