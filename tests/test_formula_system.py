import pytest
import math
from formula_system import evaluate_math_formula

def test_basic_math():
    context = {}
    assert evaluate_math_formula("1 + 1", context) == 2
    assert evaluate_math_formula("2 * 5", context) == 10
    assert evaluate_math_formula("10 / 2", context) == 5.0

def test_math_functions():
    context = {}
    assert evaluate_math_formula("sqrt(16)", context) == 4.0
    assert evaluate_math_formula("pow(2, 3)", context) == 8.0
    assert abs(evaluate_math_formula("sin(0)", context) - 0.0) < 0.001
    assert abs(evaluate_math_formula("cos(0)", context) - 1.0) < 0.001

def test_context_variables():
    context = {'x': 10, 'y': 20}
    assert evaluate_math_formula("x + y", context) == 30
    assert evaluate_math_formula("x * 2", context) == 20

def test_error_handling():
    context = {}
    # Should return 0 on error
    assert evaluate_math_formula("undefined_var", context) == 0
    assert evaluate_math_formula("1 / 0", context) == 0
    assert evaluate_math_formula("invalid syntax ??", context) == 0
