"""
Tests for FormulaException raising in formula_system.py.

PROJ-45 Phase 3: Test that formula errors raise FormulaException instead of returning 0.
"""
import pytest
from game.core.exceptions import FormulaException


class TestFormulaExceptionRaising:
    """Tests that formula errors raise FormulaException."""

    def test_syntax_error_raises_formula_exception(self):
        """Syntax errors should raise FormulaException."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("1 +* 2", {})

        assert "syntax" in str(exc_info.value).lower()
        assert exc_info.value.context.get("formula") == "1 +* 2"

    def test_undefined_variable_raises_formula_exception(self):
        """Undefined variable should raise FormulaException."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("undefined_var * 2", {"x": 1})

        assert "undefined_var" in str(exc_info.value).lower() or exc_info.value.context.get("formula")
        assert exc_info.value.context.get("formula") == "undefined_var * 2"

    def test_division_by_zero_raises_formula_exception(self):
        """Division by zero should raise FormulaException."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("1 / 0", {})

        assert exc_info.value.context.get("formula") == "1 / 0"

    def test_dangerous_function_raises_formula_exception(self):
        """Dangerous functions should raise FormulaException."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("__import__('os')", {})

        # Should include security-related info
        assert exc_info.value.context.get("formula") == "__import__('os')"

    def test_exception_includes_context_variables(self):
        """FormulaException should include available context variables."""
        from game.simulation.formula_system import evaluate_math_formula

        context = {"x": 10, "y": 5}
        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("unknown_var", context)

        # Context should include available variables for debugging
        assert "context_vars" in exc_info.value.context or "available_vars" in exc_info.value.context

    def test_exception_preserves_original_error(self):
        """FormulaException should chain from the original error."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("1 / 0", {})

        # Should have chained from ZeroDivisionError
        assert exc_info.value.__cause__ is not None

    def test_valid_formula_does_not_raise(self):
        """Valid formulas should not raise exceptions."""
        from game.simulation.formula_system import evaluate_math_formula

        # These should all succeed
        assert evaluate_math_formula("1 + 1", {}) == 2
        assert evaluate_math_formula("sqrt(16)", {}) == 4.0
        assert evaluate_math_formula("x * 2", {"x": 5}) == 10
        assert evaluate_math_formula("min(x, y)", {"x": 3, "y": 7}) == 3


class TestFormulaExceptionErrorCodes:
    """Tests for error codes in FormulaException."""

    def test_syntax_error_has_code(self):
        """Syntax errors should have error code."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("((( malformed", {})

        assert exc_info.value.code is not None
        assert "SYNTAX" in exc_info.value.code or "F" in exc_info.value.code

    def test_undefined_variable_has_code(self):
        """Undefined variable errors should have error code."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("missing_var", {})

        assert exc_info.value.code is not None

    def test_runtime_error_has_code(self):
        """Runtime errors should have error code."""
        from game.simulation.formula_system import evaluate_math_formula

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("1 / 0", {})

        assert exc_info.value.code is not None


class TestValidateFormulaDetailedErrors:
    """Tests for detailed error info from validate_formula."""

    def test_validate_returns_error_details(self):
        """validate_formula should return detailed error info."""
        from game.simulation.formula_system import validate_formula

        errors = validate_formula("undefined_var + x", ["x"])

        assert len(errors) > 0
        # Errors should be strings (existing behavior maintained)
        assert all(isinstance(e, str) for e in errors)

    def test_validate_multiple_errors(self):
        """validate_formula should catch multiple undefined variables."""
        from game.simulation.formula_system import validate_formula

        errors = validate_formula("a + b + c", ["c"])

        # Should find 'a' and 'b' as undefined
        assert len(errors) >= 2
        error_text = " ".join(errors)
        assert "a" in error_text or "b" in error_text


class TestSafeEvaluate:
    """Tests for safe_evaluate_math_formula function (optional backward compat)."""

    def test_safe_evaluate_returns_default_on_error(self):
        """safe_evaluate_math_formula should return default on error."""
        from game.simulation.formula_system import safe_evaluate_math_formula

        result = safe_evaluate_math_formula("1 / 0", {}, default=0)
        assert result == 0

    def test_safe_evaluate_returns_custom_default(self):
        """safe_evaluate_math_formula should return specified default."""
        from game.simulation.formula_system import safe_evaluate_math_formula

        result = safe_evaluate_math_formula("undefined", {}, default=-1)
        assert result == -1

    def test_safe_evaluate_success_returns_value(self):
        """safe_evaluate_math_formula should return computed value on success."""
        from game.simulation.formula_system import safe_evaluate_math_formula

        result = safe_evaluate_math_formula("2 + 3", {}, default=0)
        assert result == 5

    def test_safe_evaluate_logs_warning(self, caplog):
        """safe_evaluate_math_formula should log warning on error."""
        import logging
        from game.simulation.formula_system import safe_evaluate_math_formula

        with caplog.at_level(logging.WARNING):
            safe_evaluate_math_formula("bad syntax ??", {}, default=0)

        assert len(caplog.records) > 0
