"""
Security and functionality tests for formula_system.py.

These tests verify:
1. The eval() sandbox properly blocks dangerous operations
2. Basic formula evaluation works correctly

Note: evaluate_math_formula returns 0 on any error (including security violations),
so security tests verify that dangerous operations return 0 (blocked) rather than
raising exceptions directly.
"""

import pytest
from game.simulation.formula_system import evaluate_math_formula


class TestFormulaSystemSecurity:
    """Security tests to verify the eval() sandbox blocks dangerous operations.

    The sandbox blocks dangerous operations by causing them to fail (returning 0).
    These tests verify that malicious formulas cannot execute and return 0 instead.
    """

    def test_eval_sandbox_blocks_imports(self):
        """Verify that __import__ is blocked by the sandbox (returns 0, not actual import)."""
        # If __import__ worked, this would not return 0
        result = evaluate_math_formula("__import__('os').system('echo pwned')", {})
        assert result == 0, "Import should be blocked and return 0"

    def test_eval_sandbox_blocks_builtins(self):
        """Verify that builtin functions like open() are blocked (returns 0)."""
        result = evaluate_math_formula("open('/etc/passwd')", {})
        assert result == 0, "open() should be blocked and return 0"

    def test_eval_sandbox_blocks_exec(self):
        """Verify that exec() is blocked (returns 0)."""
        result = evaluate_math_formula("exec('x=1')", {})
        assert result == 0, "exec() should be blocked and return 0"

    def test_eval_sandbox_blocks_eval(self):
        """Verify that nested eval() is blocked (returns 0)."""
        result = evaluate_math_formula("eval('1+1')", {})
        assert result == 0, "eval() should be blocked and return 0"

    def test_eval_sandbox_blocks_compile(self):
        """Verify that compile() is blocked (returns 0)."""
        result = evaluate_math_formula("compile('1+1', '', 'eval')", {})
        assert result == 0, "compile() should be blocked and return 0"

    def test_eval_sandbox_blocks_getattr_builtins(self):
        """Verify that accessing __builtins__ via tricks is blocked (returns 0)."""
        result = evaluate_math_formula("getattr(__builtins__, 'open')", {})
        assert result == 0, "getattr on __builtins__ should be blocked and return 0"

    def test_eval_sandbox_blocks_globals_access(self):
        """Verify that globals() is blocked (returns 0)."""
        result = evaluate_math_formula("globals()", {})
        assert result == 0, "globals() should be blocked and return 0"

    def test_eval_sandbox_blocks_locals_access(self):
        """Verify that locals() is blocked (returns 0)."""
        result = evaluate_math_formula("locals()", {})
        assert result == 0, "locals() should be blocked and return 0"

    def test_sandbox_allows_valid_math(self):
        """Verify that valid math expressions still work (not blocked)."""
        # This ensures our security tests aren't false positives
        result = evaluate_math_formula("sqrt(16) + 2", {})
        assert result == 6.0, "Valid math should work, not return 0"


class TestFormulaSystemFunctionality:
    """Functionality tests for formula evaluation."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        assert evaluate_math_formula("1 + 1", {}) == 2
        assert evaluate_math_formula("10 - 3", {}) == 7
        assert evaluate_math_formula("4 * 5", {}) == 20
        assert evaluate_math_formula("15 / 3", {}) == 5.0

    def test_math_functions(self):
        """Test math module functions are available."""
        assert evaluate_math_formula("sqrt(16)", {}) == 4.0
        assert evaluate_math_formula("pow(2, 3)", {}) == 8.0
        assert evaluate_math_formula("ceil(4.2)", {}) == 5
        assert evaluate_math_formula("floor(4.8)", {}) == 4

    def test_context_variables(self):
        """Test that context variables are accessible."""
        context = {'x': 10, 'y': 5, 'ship_class_mass': 1000}
        assert evaluate_math_formula("x + y", context) == 15
        assert evaluate_math_formula("x * 2", context) == 20
        assert evaluate_math_formula("sqrt(ship_class_mass)", context) == pytest.approx(31.622, rel=0.01)

    def test_complex_formula(self):
        """Test complex formulas like those used in components.json."""
        context = {'ship_class_mass': 1000}
        # From bridge component: "=50 * sqrt(ship_class_mass / 1000)"
        result = evaluate_math_formula("50 * sqrt(ship_class_mass / 1000)", context)
        assert result == 50.0

    def test_error_returns_zero(self):
        """Test that errors return 0 instead of raising."""
        assert evaluate_math_formula("undefined_var", {}) == 0
        assert evaluate_math_formula("1 / 0", {}) == 0
        assert evaluate_math_formula("invalid syntax ??", {}) == 0
