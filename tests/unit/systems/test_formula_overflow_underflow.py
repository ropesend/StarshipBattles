"""
Tests for overflow/underflow edge cases in formula_system.py.

TCG-SIM-009: FormulaSystem Overflow/Underflow Not Tested
These tests verify that the formula system handles extreme numerical values gracefully.
"""
import math
import sys
import pytest

from game.simulation.formula_system import (
    evaluate_math_formula,
    safe_evaluate_math_formula,
)
from game.core.exceptions import FormulaException


class TestFloatOverflow:
    """Tests for float overflow handling."""

    def test_large_exponent_with_builtin_pow_returns_large_int(self):
        """pow() uses Python builtin which handles arbitrary precision integers."""
        # Python's builtin pow returns a large integer, not infinity
        result = evaluate_math_formula("pow(10, 1000)", {})
        assert result == 10 ** 1000
        assert isinstance(result, int)

    def test_float_exponentiation_overflow_raises_exception(self):
        """Float exponentiation overflow should raise FormulaException."""
        # 10.0 ** 1000 causes OverflowError
        with pytest.raises(FormulaException):
            evaluate_math_formula("10.0 ** 1000", {})

    def test_very_large_multiplication_produces_infinity(self):
        """Multiplying very large floats should produce infinity."""
        # sys.float_info.max * 2 should overflow to inf
        result = evaluate_math_formula(
            "x * 2",
            {"x": sys.float_info.max}
        )
        assert result == float('inf')

    def test_exp_large_argument_raises_exception(self):
        """exp() with large argument causes math range error."""
        # exp(1000) = e^1000 causes math range error
        with pytest.raises(FormulaException):
            evaluate_math_formula("exp(1000)", {})

    def test_infinity_in_context_propagates(self):
        """Infinity passed in context should propagate correctly."""
        result = evaluate_math_formula("x + 1", {"x": float('inf')})
        assert result == float('inf')

    def test_infinity_arithmetic(self):
        """Arithmetic with infinity should follow IEEE 754."""
        assert evaluate_math_formula("x * 2", {"x": float('inf')}) == float('inf')
        assert evaluate_math_formula("x / 2", {"x": float('inf')}) == float('inf')
        assert evaluate_math_formula("-x", {"x": float('inf')}) == float('-inf')


class TestFloatUnderflow:
    """Tests for float underflow (values approaching zero)."""

    def test_very_small_division(self):
        """Division producing very small results should not crash."""
        # sys.float_info.min is the smallest positive normalized float
        result = evaluate_math_formula(
            "x / 1e100",
            {"x": sys.float_info.min}
        )
        # Should be a very small number or zero (subnormal underflow)
        assert result >= 0.0
        assert result < 1e-200

    def test_exp_large_negative_produces_zero(self):
        """exp() with large negative argument should produce zero (underflow)."""
        result = evaluate_math_formula("exp(-1000)", {})
        assert result == 0.0

    def test_tiny_number_times_tiny_number(self):
        """Multiplying very small numbers should underflow to zero gracefully."""
        result = evaluate_math_formula(
            "x * y",
            {"x": 1e-200, "y": 1e-200}
        )
        # Should underflow to zero
        assert result == 0.0

    def test_subnormal_numbers_supported(self):
        """Subnormal (denormalized) numbers should be handled."""
        # sys.float_info.min / 2 creates a subnormal number
        subnormal = sys.float_info.min / 2
        result = evaluate_math_formula("x * 2", {"x": subnormal})
        # Should approximately equal sys.float_info.min
        assert result > 0


class TestNaNHandling:
    """Tests for NaN (Not a Number) handling."""

    def test_nan_from_invalid_operation(self):
        """Invalid operations that produce NaN should not crash."""
        # 0/0 raises ZeroDivisionError, but inf - inf = nan
        # First create inf, then subtract inf
        result = evaluate_math_formula("x - x", {"x": float('inf')})
        assert math.isnan(result)

    def test_nan_in_context_propagates(self):
        """NaN passed in context should propagate (NaN is contagious)."""
        result = evaluate_math_formula("x + 1", {"x": float('nan')})
        assert math.isnan(result)

    def test_nan_comparison_behavior(self):
        """NaN comparisons should follow IEEE 754 (always false)."""
        # min/max with NaN - Python's min/max propagate NaN
        result = evaluate_math_formula("min(x, 5)", {"x": float('nan')})
        assert math.isnan(result)

    def test_zero_times_infinity_is_nan(self):
        """0 * inf should produce NaN."""
        result = evaluate_math_formula("x * y", {"x": 0.0, "y": float('inf')})
        assert math.isnan(result)


class TestInfinityDivision:
    """Tests for division involving infinity."""

    def test_finite_divided_by_infinity(self):
        """Finite number divided by infinity should be zero."""
        result = evaluate_math_formula("1 / x", {"x": float('inf')})
        assert result == 0.0

    def test_infinity_divided_by_infinity_is_nan(self):
        """Infinity divided by infinity should be NaN."""
        result = evaluate_math_formula("x / y", {"x": float('inf'), "y": float('inf')})
        assert math.isnan(result)

    def test_infinity_divided_by_finite(self):
        """Infinity divided by finite should be infinity."""
        result = evaluate_math_formula("x / 2", {"x": float('inf')})
        assert result == float('inf')

    def test_negative_infinity_division(self):
        """Negative infinity division should preserve sign rules."""
        result = evaluate_math_formula("x / 2", {"x": float('-inf')})
        assert result == float('-inf')


class TestMathDomainErrors:
    """Tests for math domain errors that should raise FormulaException."""

    def test_sqrt_negative_raises_exception(self):
        """sqrt of negative number should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("sqrt(-1)", {})

    def test_log_zero_raises_exception(self):
        """log of zero should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("log(0)", {})

    def test_log_negative_raises_exception(self):
        """log of negative number should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("log(-1)", {})

    def test_acos_out_of_range_raises_exception(self):
        """acos outside [-1, 1] should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("acos(2)", {})

    def test_asin_out_of_range_raises_exception(self):
        """asin outside [-1, 1] should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("asin(2)", {})


class TestSafeEvaluateOverflowUnderflow:
    """Tests for safe_evaluate_math_formula with overflow/underflow."""

    def test_safe_evaluate_handles_large_int_result(self):
        """safe_evaluate should return large int result from pow()."""
        result = safe_evaluate_math_formula("pow(10, 100)", {}, default=0)
        assert result == 10 ** 100

    def test_safe_evaluate_handles_nan_result(self):
        """safe_evaluate should return NaN result, not default."""
        result = safe_evaluate_math_formula("x - x", {"x": float('inf')}, default=0)
        assert math.isnan(result)

    def test_safe_evaluate_domain_error_returns_default(self):
        """safe_evaluate should return default on domain error."""
        result = safe_evaluate_math_formula("sqrt(-1)", {}, default=0)
        assert result == 0

    def test_safe_evaluate_underflow_to_zero(self):
        """safe_evaluate should handle underflow to zero."""
        result = safe_evaluate_math_formula("exp(-1000)", {}, default=-1)
        assert result == 0.0  # Actual result, not default


class TestExtremeBoundaryValues:
    """Tests for extreme float boundary values."""

    def test_float_max_value(self):
        """sys.float_info.max should be usable in formulas."""
        result = evaluate_math_formula("x", {"x": sys.float_info.max})
        assert result == sys.float_info.max

    def test_float_min_value(self):
        """sys.float_info.min (smallest positive) should be usable."""
        result = evaluate_math_formula("x", {"x": sys.float_info.min})
        assert result == sys.float_info.min

    def test_float_epsilon_precision(self):
        """Float epsilon operations should maintain precision."""
        eps = sys.float_info.epsilon
        result = evaluate_math_formula("1.0 + x", {"x": eps})
        assert result > 1.0  # Should be distinguishable from 1.0

    def test_negative_float_max(self):
        """Negative of float max should work."""
        result = evaluate_math_formula("-x", {"x": sys.float_info.max})
        assert result == -sys.float_info.max

    def test_addition_at_boundary(self):
        """Adding small value to float max should overflow to inf."""
        result = evaluate_math_formula(
            "x + x",
            {"x": sys.float_info.max}
        )
        assert result == float('inf')


class TestComplexOverflowScenarios:
    """Tests for complex formulas with potential overflow/underflow."""

    def test_compound_exponential_with_builtin_pow(self):
        """Compound exponential with pow() handles large integers."""
        # 2^2^10 = 2^1024 - Python handles arbitrary precision
        result = evaluate_math_formula("pow(2, pow(2, 10))", {})
        assert result == 2 ** 1024
        assert isinstance(result, int)

    def test_gamma_large_argument_raises_exception(self):
        """gamma() with very large argument raises math range error."""
        # gamma(172) causes overflow (170! ≈ 7.26e+306, 171! overflows)
        with pytest.raises(FormulaException):
            evaluate_math_formula("gamma(172)", {})

    def test_float_pow_overflow_raises_exception(self):
        """Float exponentiation overflow raises FormulaException."""
        # 1.1 ** 10000 causes OverflowError
        with pytest.raises(FormulaException):
            evaluate_math_formula("1.1 ** 10000", {})

    def test_nested_sqrt_convergence(self):
        """Deeply nested sqrt should converge toward 1."""
        # sqrt(sqrt(sqrt(x))) approaches 1 for any positive x
        result = evaluate_math_formula(
            "sqrt(sqrt(sqrt(sqrt(x))))",
            {"x": 1e100}
        )
        # x^(1/16) where x=1e100 = 10^(100/16) = 10^6.25 ≈ 1778279.4
        assert result == pytest.approx(10 ** 6.25, rel=0.01)

    def test_alternating_sign_large_sum(self):
        """Large numbers with alternating signs should not overflow."""
        result = evaluate_math_formula(
            "x - x + x - x",
            {"x": sys.float_info.max}
        )
        assert result == 0.0

    def test_pow_vs_operator_difference(self):
        """Document difference between pow() and ** operator for floats."""
        # pow(2, 100) returns int (arbitrary precision)
        int_result = evaluate_math_formula("pow(2, 100)", {})
        assert isinstance(int_result, int)
        assert int_result == 2 ** 100

        # 2.0 ** 100 returns float (limited precision but manageable)
        float_result = evaluate_math_formula("2.0 ** 100", {})
        assert isinstance(float_result, float)
        assert float_result == pytest.approx(2 ** 100, rel=1e-10)
