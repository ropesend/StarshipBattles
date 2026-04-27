"""Tests for the unified FormulaEvaluator and FormulaContext.

PROJ-242: These tests define the expected behavior of the unified formula
evaluation system that replaces both formula_system.py module-level functions
and ModifierEffectEvaluator.evaluate_formula/validate_formula.
"""

import math
import logging
import pytest

from game.core.formula_evaluator import FormulaContext, FormulaEvaluator
from game.core.exceptions import FormulaException
from game.core.error_codes import ErrorCode


# =============================================================================
# TestFormulaContext
# =============================================================================


class TestFormulaContext:
    """Tests for the FormulaContext frozen dataclass."""

    def test_defaults(self):
        """Default FormulaContext has caret_as_power=False and empty extra_functions."""
        ctx = FormulaContext()
        assert ctx.caret_as_power is False
        assert ctx.extra_functions == {}

    def test_caret_as_power_true(self):
        """FormulaContext can be created with caret_as_power=True."""
        ctx = FormulaContext(caret_as_power=True)
        assert ctx.caret_as_power is True
        assert ctx.extra_functions == {}

    def test_extra_functions(self):
        """FormulaContext can carry extra functions."""
        ctx = FormulaContext(extra_functions={'ln': math.log})
        assert ctx.extra_functions == {'ln': math.log}

    def test_frozen(self):
        """FormulaContext is immutable (frozen dataclass)."""
        ctx = FormulaContext()
        with pytest.raises(AttributeError):
            ctx.caret_as_power = True

    def test_both_fields(self):
        """FormulaContext can have both fields set."""
        ctx = FormulaContext(caret_as_power=True, extra_functions={'ln': math.log})
        assert ctx.caret_as_power is True
        assert ctx.extra_functions['ln'] is math.log


# =============================================================================
# TestFormulaEvaluatorBasic
# =============================================================================


class TestFormulaEvaluatorBasic:
    """Basic evaluation tests for FormulaEvaluator."""

    def test_addition(self):
        assert FormulaEvaluator.evaluate("1 + 1", {}) == 2

    def test_subtraction(self):
        assert FormulaEvaluator.evaluate("10 - 3", {}) == 7

    def test_multiplication(self):
        assert FormulaEvaluator.evaluate("4 * 5", {}) == 20

    def test_division(self):
        assert FormulaEvaluator.evaluate("15 / 3", {}) == 5.0

    def test_context_variables(self):
        """Formulas can reference variables from the context dict."""
        result = FormulaEvaluator.evaluate("x + y", {'x': 10, 'y': 5})
        assert result == 15

    def test_complex_formula(self):
        """Complex formula with sqrt and context variable."""
        result = FormulaEvaluator.evaluate(
            "50 * sqrt(ship_class_mass / 1000)",
            {'ship_class_mass': 1000}
        )
        assert result == 50.0

    def test_native_return_type_int(self):
        """Integer expressions return int, not float."""
        result = FormulaEvaluator.evaluate("2 + 3", {})
        assert result == 5
        assert isinstance(result, int)

    def test_native_return_type_float(self):
        """Float expressions return float."""
        result = FormulaEvaluator.evaluate("2.0 + 3.0", {})
        assert result == 5.0
        assert isinstance(result, float)


# =============================================================================
# TestFormulaEvaluatorMathFunctions
# =============================================================================


class TestFormulaEvaluatorMathFunctions:
    """Tests that all required math functions are available."""

    def test_sqrt(self):
        assert FormulaEvaluator.evaluate("sqrt(16)", {}) == 4.0

    def test_sin(self):
        result = FormulaEvaluator.evaluate("sin(0)", {})
        assert result == pytest.approx(0.0)

    def test_cos(self):
        result = FormulaEvaluator.evaluate("cos(0)", {})
        assert result == pytest.approx(1.0)

    def test_log(self):
        """log() is natural logarithm (math.log)."""
        result = FormulaEvaluator.evaluate("log(e)", {})
        assert result == pytest.approx(1.0)

    def test_log10(self):
        result = FormulaEvaluator.evaluate("log10(100)", {})
        assert result == pytest.approx(2.0)

    def test_floor(self):
        assert FormulaEvaluator.evaluate("floor(2.7)", {}) == 2

    def test_ceil(self):
        assert FormulaEvaluator.evaluate("ceil(2.3)", {}) == 3

    def test_exp(self):
        result = FormulaEvaluator.evaluate("exp(0)", {})
        assert result == pytest.approx(1.0)

    def test_ln_alias(self):
        """ln is an alias for math.log (natural log)."""
        result = FormulaEvaluator.evaluate("ln(e)", {})
        assert result == pytest.approx(1.0)

    def test_pi_constant(self):
        """pi constant is available."""
        result = FormulaEvaluator.evaluate("pi", {})
        assert result == pytest.approx(math.pi)

    def test_e_constant(self):
        """e constant is available."""
        result = FormulaEvaluator.evaluate("e", {})
        assert result == pytest.approx(math.e)


# =============================================================================
# TestFormulaEvaluatorBuiltins
# =============================================================================


class TestFormulaEvaluatorBuiltins:
    """Tests that safe builtin functions are available."""

    def test_abs(self):
        assert FormulaEvaluator.evaluate("abs(-5)", {}) == 5

    def test_min(self):
        assert FormulaEvaluator.evaluate("min(3, 7)", {}) == 3

    def test_max(self):
        assert FormulaEvaluator.evaluate("max(3, 7)", {}) == 7

    def test_round(self):
        assert FormulaEvaluator.evaluate("round(3.7)", {}) == 4

    def test_sum(self):
        assert FormulaEvaluator.evaluate("sum([1, 2, 3])", {}) == 6

    def test_len(self):
        assert FormulaEvaluator.evaluate("len([1, 2, 3])", {}) == 3

    def test_int(self):
        assert FormulaEvaluator.evaluate("int(3.9)", {}) == 3

    def test_float(self):
        result = FormulaEvaluator.evaluate("float(3)", {})
        assert result == 3.0
        assert isinstance(result, float)

    def test_pow(self):
        assert FormulaEvaluator.evaluate("pow(2, 3)", {}) == 8


# =============================================================================
# TestFormulaEvaluatorCaret
# =============================================================================


class TestFormulaEvaluatorCaret:
    """Tests for caret (^) handling based on FormulaContext."""

    def test_caret_as_xor_by_default(self):
        """With default context, ^ is Python XOR (bitwise)."""
        result = FormulaEvaluator.evaluate("3 ^ 1", {})
        assert result == 2  # XOR: 0b11 ^ 0b01 = 0b10 = 2

    def test_caret_as_power(self):
        """With caret_as_power=True, ^ becomes **."""
        ctx = FormulaContext(caret_as_power=True)
        result = FormulaEvaluator.evaluate("3 ^ 2", {}, formula_context=ctx)
        assert result == 9

    def test_caret_param_squared(self):
        """param ^ 2 with caret_as_power=True and param=3.0 gives 9.0."""
        ctx = FormulaContext(caret_as_power=True)
        result = FormulaEvaluator.evaluate(
            "param ^ 2", {'param': 3.0}, formula_context=ctx
        )
        assert result == 9.0

    def test_caret_two_to_param(self):
        """2 ^ param with caret_as_power=True and param=3.0 gives 8.0."""
        ctx = FormulaContext(caret_as_power=True)
        result = FormulaEvaluator.evaluate(
            "2 ^ param", {'param': 3.0}, formula_context=ctx
        )
        assert result == 8.0


# =============================================================================
# TestFormulaEvaluatorErrors
# =============================================================================


class TestFormulaEvaluatorErrors:
    """Error handling tests for FormulaEvaluator."""

    def test_syntax_error_raises_formula_exception(self):
        """SyntaxError in formula raises FormulaException with correct code."""
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("1 +", {})
        assert exc_info.value.code == ErrorCode.FORMULA_SYNTAX_ERROR.value

    def test_name_error_raises_formula_exception(self):
        """NameError (undefined variable) raises FormulaException with correct code."""
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("undefined_var + 1", {})
        assert exc_info.value.code == ErrorCode.FORMULA_UNDEFINED_VAR.value

    def test_zero_division_raises_formula_exception(self):
        """ZeroDivisionError raises FormulaException with correct code."""
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("1 / 0", {})
        assert exc_info.value.code == ErrorCode.EVAL_ERROR.value

    def test_security_dangerous_names_raise_formula_exception(self):
        """Dangerous names like eval, exec, open raise FormulaException."""
        for name in ['eval', 'exec', 'open']:
            with pytest.raises(FormulaException) as exc_info:
                FormulaEvaluator.evaluate(f"{name}('test')", {})
            # These will fail either as NameError or general error, both acceptable
            assert exc_info.value.code in (
                ErrorCode.FORMULA_UNDEFINED_VAR.value,
                ErrorCode.FORMULA_GENERAL_ERROR.value,
            )

    def test_exception_includes_context(self):
        """FormulaException includes context dict with formula and available_vars."""
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("bad_formula +", {'x': 1})
        exc = exc_info.value
        assert 'formula' in exc.context
        assert exc.context['formula'] == "bad_formula +"
        assert 'available_vars' in exc.context
        assert 'x' in exc.context['available_vars']

    def test_exception_chains_from_original(self):
        """FormulaException has __cause__ set to the original error."""
        with pytest.raises(FormulaException) as exc_info:
            FormulaEvaluator.evaluate("1 / 0", {})
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ZeroDivisionError)


# =============================================================================
# TestFormulaEvaluatorValidate
# =============================================================================


class TestFormulaEvaluatorValidate:
    """Tests for FormulaEvaluator.validate()."""

    def test_valid_formula_returns_empty_list(self):
        """A valid formula with known variables returns no errors."""
        errors = FormulaEvaluator.validate("x + y", ['x', 'y'])
        assert errors == []

    def test_syntax_error_returns_error_list(self):
        """A formula with syntax error returns error list."""
        errors = FormulaEvaluator.validate("1 +", ['x'])
        assert len(errors) > 0
        assert any("syntax" in e.lower() or "Syntax" in e for e in errors)

    def test_undefined_variable_detected(self):
        """An undefined variable is reported."""
        errors = FormulaEvaluator.validate("x + unknown", ['x'])
        assert len(errors) > 0
        assert any("unknown" in e for e in errors)

    def test_math_functions_allowed(self):
        """Math functions like sqrt, sin are allowed."""
        errors = FormulaEvaluator.validate("sqrt(x) + sin(y)", ['x', 'y'])
        assert errors == []

    def test_dangerous_functions_blocked(self):
        """Dangerous functions like eval, exec are blocked."""
        errors = FormulaEvaluator.validate("eval(x)", ['x'])
        assert len(errors) > 0
        assert any("eval" in e.lower() or "Dangerous" in e for e in errors)

    def test_caret_substitution_in_validation(self):
        """With caret_as_power=True, ^ is treated as ** in validation."""
        ctx = FormulaContext(caret_as_power=True)
        errors = FormulaEvaluator.validate(
            "param ^ 2", ['param'], formula_context=ctx
        )
        assert errors == []

    def test_caret_without_substitution_fails(self):
        """Without caret_as_power, ^ is XOR which is valid Python -- no error."""
        # ^ is a valid Python operator (XOR), so no syntax error
        errors = FormulaEvaluator.validate("param ^ 2", ['param'])
        assert errors == []

    def test_allowed_variables_restricts_names(self):
        """Only variables in the allowed list pass validation."""
        errors = FormulaEvaluator.validate("x + y", ['x'])
        assert len(errors) > 0
        assert any("y" in e for e in errors)

    def test_ln_alias_allowed(self):
        """ln is recognized as a valid function name in validation."""
        errors = FormulaEvaluator.validate("ln(x)", ['x'])
        assert errors == []


# =============================================================================
# TestFormulaEvaluatorSafeEvaluate
# =============================================================================


class TestFormulaEvaluatorSafeEvaluate:
    """Tests for FormulaEvaluator.safe_evaluate()."""

    def test_returns_computed_value_on_success(self):
        """On success, safe_evaluate returns the computed value."""
        result = FormulaEvaluator.safe_evaluate("2 + 3", {})
        assert result == 5

    def test_returns_default_on_error(self):
        """On error, safe_evaluate returns 0 (the default)."""
        result = FormulaEvaluator.safe_evaluate("undefined_var", {})
        assert result == 0

    def test_returns_custom_default(self):
        """On error, safe_evaluate returns the provided custom default."""
        result = FormulaEvaluator.safe_evaluate("undefined_var", {}, default=-1)
        assert result == -1

    def test_logs_warning_on_error(self, caplog):
        """On error, safe_evaluate logs a warning."""
        with caplog.at_level(logging.WARNING, logger="game.simulation.formula_system"):
            FormulaEvaluator.safe_evaluate("bad_var", {})
        assert any("bad_var" in record.message for record in caplog.records)


# =============================================================================
# TestFormulaEvaluatorClassConstants
# =============================================================================


class TestFormulaEvaluatorClassConstants:
    """Tests for class-level FormulaContext constants."""

    def test_default_context(self):
        """DEFAULT_CONTEXT has caret_as_power=False."""
        ctx = FormulaEvaluator.DEFAULT_CONTEXT
        assert ctx.caret_as_power is False
        assert ctx.extra_functions == {}

    def test_modifier_context(self):
        """MODIFIER_CONTEXT has caret_as_power=True and ln alias."""
        ctx = FormulaEvaluator.MODIFIER_CONTEXT
        assert ctx.caret_as_power is True
        assert 'ln' in ctx.extra_functions
        assert ctx.extra_functions['ln'] is math.log
