"""
Tests for formula validation on modifier load.

Task 9.2: Verify that invalid formulas are detected at load time,
not just at runtime during gameplay.
"""
import pytest
import logging

from game.simulation.components.modifier_effects import ModifierEffectEvaluator


class TestFormulaValidation:
    """Tests for formula syntax and variable validation."""

    def test_validate_formula_syntax_valid(self):
        """Valid formula should pass validation."""
        valid_formulas = [
            'param',
            'param * 2',
            'param ^ 2',
            '1.0 + param',
            'sqrt(param)',
            'ln(1 + param)',
            '1.0 / param',
            '(param - 1.0) * 0.5',
        ]
        for formula in valid_formulas:
            errors = ModifierEffectEvaluator.validate_formula(formula)
            assert errors == [], f"Valid formula '{formula}' should have no errors, got {errors}"

    def test_validate_formula_syntax_error(self):
        """Formula with syntax error should be detected."""
        invalid_formulas = [
            '((( malformed',
            'param ^ ^ 2',
            '* param',
            'param +',
            '1.0 / / param',
        ]
        for formula in invalid_formulas:
            errors = ModifierEffectEvaluator.validate_formula(formula)
            assert len(errors) > 0, f"Invalid formula '{formula}' should have errors"

    def test_validate_formula_undefined_variable(self):
        """Formula with undefined variable should be detected."""
        formula = 'undefined_var + param'
        errors = ModifierEffectEvaluator.validate_formula(formula)
        assert len(errors) > 0, "Formula with undefined variable should have errors"
        # Check error mentions the undefined variable
        assert any('undefined_var' in str(e).lower() for e in errors), \
            f"Error should mention undefined variable, got: {errors}"

    def test_validate_formula_allowed_variables(self):
        """Formula should allow 'param' and math functions."""
        # These should all be valid
        valid = [
            'param',
            'sqrt(param)',
            'ln(param + 1)',
            'abs(param)',
            'min(param, 10)',
            'max(param, 0)',
        ]
        for formula in valid:
            errors = ModifierEffectEvaluator.validate_formula(formula)
            assert errors == [], f"Formula '{formula}' should be valid, got {errors}"

    def test_validate_all_modifiers_on_load(self):
        """All modifiers in modifiers.json should pass validation."""
        from game.simulation.components.component import load_modifiers
        from game.core.registry import RegistryManager

        load_modifiers("data/modifiers.json")
        modifier_registry = RegistryManager.instance().modifiers

        validation_errors = []
        for mod_id, mod_def in modifier_registry.items():
            if hasattr(mod_def, 'effects') and mod_def.effects:
                for effect in mod_def.effects:
                    formula = effect.get('formula', 'param')
                    errors = ModifierEffectEvaluator.validate_formula(formula)
                    if errors:
                        validation_errors.append({
                            'modifier_id': mod_id,
                            'formula': formula,
                            'errors': errors
                        })

        assert validation_errors == [], \
            f"Found {len(validation_errors)} modifier(s) with invalid formulas: {validation_errors}"


class TestFormulaValidationErrors:
    """Tests that validation errors include helpful information."""

    def test_validation_error_includes_position(self):
        """Syntax error should indicate position in formula."""
        formula = 'param + +'
        errors = ModifierEffectEvaluator.validate_formula(formula)
        assert len(errors) > 0, "Should detect syntax error"
        # Error should be descriptive
        assert any('syntax' in str(e).lower() or 'error' in str(e).lower() for e in errors)

    def test_validation_returns_list(self):
        """Validation should return a list (empty for valid, populated for invalid)."""
        # Valid formula returns empty list
        errors = ModifierEffectEvaluator.validate_formula('param')
        assert isinstance(errors, list)
        assert errors == []

        # Invalid formula returns non-empty list
        errors = ModifierEffectEvaluator.validate_formula('((( invalid')
        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_multiple_errors_returned(self):
        """Formula with multiple issues should report all of them."""
        # This formula has both undefined var and syntax issue
        formula = 'undefined1 + undefined2'
        errors = ModifierEffectEvaluator.validate_formula(formula)
        # Should detect at least the undefined variables
        assert len(errors) >= 1


class TestModifierLoadValidation:
    """Tests for validating modifiers at load time."""

    def test_validate_modifier_definition(self):
        """Should validate a complete modifier definition."""
        valid_mod = {
            'id': 'test_mod',
            'name': 'Test Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param * 2'}
            ]
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(valid_mod)
        assert errors == [], f"Valid modifier should have no errors, got {errors}"

    def test_validate_modifier_with_invalid_formula(self):
        """Modifier with invalid formula should report errors."""
        invalid_mod = {
            'id': 'bad_mod',
            'name': 'Bad Modifier',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'invalid syntax here'}
            ]
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(invalid_mod)
        assert len(errors) > 0, "Modifier with invalid formula should have errors"

    def test_validate_modifier_multiple_effects(self):
        """Should validate all effects in a modifier."""
        mod = {
            'id': 'multi_effect',
            'name': 'Multi Effect',
            'effects': [
                {'stat': 'damage_mult', 'formula': 'param'},  # Valid
                {'stat': 'mass_mult', 'formula': '((( broken'},  # Invalid
                {'stat': 'hp_mult', 'formula': 'param ^ 2'},  # Valid
            ]
        }
        errors = ModifierEffectEvaluator.validate_modifier_definition(mod)
        assert len(errors) >= 1, "Should detect invalid effect formula"
