"""Tests for game.core.formula_evaluator — FormulaEvaluator in core layer."""
import math
from unittest.mock import patch

import pytest

from game.core.exceptions import FormulaException
from game.core.formula_evaluator import FormulaEvaluator, _parse_formula


class TestFormulaEvaluatorCoreImport:
    """Verify FormulaEvaluator is importable from game.core."""

    def test_import_formula_evaluator(self):
        from game.core.formula_evaluator import FormulaEvaluator
        assert FormulaEvaluator is not None

    def test_import_formula_context(self):
        from game.core.formula_evaluator import FormulaContext
        assert FormulaContext is not None


class TestFormulaEvaluatorBasic:
    """Basic evaluation tests for the core FormulaEvaluator."""

    def test_simple_arithmetic(self):
        from game.core.formula_evaluator import FormulaEvaluator
        assert FormulaEvaluator.evaluate("2 + 3", {}) == 5

    def test_variable_substitution(self):
        from game.core.formula_evaluator import FormulaEvaluator
        assert FormulaEvaluator.evaluate("x * 2", {"x": 5}) == 10

    def test_math_functions(self):
        from game.core.formula_evaluator import FormulaEvaluator
        assert FormulaEvaluator.evaluate("sqrt(16)", {}) == 4.0

    def test_safe_evaluate_fallback(self):
        from game.core.formula_evaluator import FormulaEvaluator
        result = FormulaEvaluator.safe_evaluate("bad!", {}, default=42)
        assert result == 42

    def test_validate_valid_formula(self):
        from game.core.formula_evaluator import FormulaEvaluator
        errors = FormulaEvaluator.validate("x + y", ["x", "y"])
        assert errors == []

    def test_validate_catches_undefined(self):
        from game.core.formula_evaluator import FormulaEvaluator
        errors = FormulaEvaluator.validate("z + 1", ["x"])
        assert any("z" in e for e in errors)

    def test_modifier_context_caret(self):
        from game.core.formula_evaluator import FormulaEvaluator
        result = FormulaEvaluator.evaluate(
            "x ^ 2", {"x": 3},
            formula_context=FormulaEvaluator.MODIFIER_CONTEXT,
        )
        assert result == 9

    def test_security_rejects_import(self):
        from game.core.formula_evaluator import FormulaEvaluator
        with pytest.raises(FormulaException):
            FormulaEvaluator.evaluate("__import__('os')", {})


class TestASTWalker:
    """Tests for AST-based evaluation (no eval() usage)."""

    def test_operator_precedence(self):
        assert FormulaEvaluator.evaluate("2 + 3 * 4", {}) == 14

    def test_parentheses(self):
        assert FormulaEvaluator.evaluate("(2 + 3) * 4", {}) == 20

    def test_power(self):
        assert FormulaEvaluator.evaluate("2 ** 3", {}) == 8

    def test_floor_division(self):
        assert FormulaEvaluator.evaluate("7 // 2", {}) == 3

    def test_modulo(self):
        assert FormulaEvaluator.evaluate("7 % 3", {}) == 1

    def test_unary_negation(self):
        assert FormulaEvaluator.evaluate("-x", {"x": 5}) == -5

    def test_unary_positive(self):
        assert FormulaEvaluator.evaluate("+x", {"x": 5}) == 5

    def test_nested_function_calls(self):
        assert FormulaEvaluator.evaluate("max(sqrt(16), 2)", {}) == 4.0

    def test_no_eval_used(self):
        """Verify eval() builtin is NOT called during evaluation."""
        with patch("builtins.eval", side_effect=AssertionError("eval() should not be called")):
            # This will fail if the implementation still uses eval()
            result = FormulaEvaluator.evaluate("2 + 3", {})
            assert result == 5

    def test_lru_cache_hit(self):
        """Second call with same formula reuses cached AST."""
        _parse_formula.cache_clear()
        FormulaEvaluator.evaluate("x + 1", {"x": 1})
        FormulaEvaluator.evaluate("x + 1", {"x": 2})
        info = _parse_formula.cache_info()
        assert info.hits >= 1

    def test_rejects_attribute_access(self):
        with pytest.raises(FormulaException):
            FormulaEvaluator.evaluate("x.y", {"x": object()})

    def test_rejects_subscript(self):
        with pytest.raises(FormulaException):
            FormulaEvaluator.evaluate("x[0]", {"x": [1, 2, 3]})

    def test_error_includes_formula_and_vars(self):
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("undefined_var + 1", {})
        assert "undefined_var" in str(exc_info.value)

    def test_complex_modifier_formula(self):
        """Real production formula from modifiers.json."""
        result = FormulaEvaluator.evaluate(
            "1.0 + 0.514 * ln(1.0 + param / 30.0)",
            {"param": 60.0},
            formula_context=FormulaEvaluator.MODIFIER_CONTEXT,
        )
        expected = 1.0 + 0.514 * math.log(1.0 + 60.0 / 30.0)
        assert abs(result - expected) < 1e-10

    def test_caret_power_formula(self):
        """Caret substitution in modifier context."""
        result = FormulaEvaluator.evaluate(
            "param ^ 2",
            {"param": 4.0},
            formula_context=FormulaEvaluator.MODIFIER_CONTEXT,
        )
        assert result == 16.0
