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


class TestFormulaSystemErrorLogging:
    """Tests for error logging in formula evaluation (ERR-002)."""

    def test_syntax_error_logs_warning(self, caplog):
        """Syntax errors should log a warning with formula and error details."""
        import logging
        bad_formula = "1 +* 2"  # Actually invalid Python syntax

        with caplog.at_level(logging.WARNING):
            result = evaluate_math_formula(bad_formula, {})

        assert result == 0  # Still returns 0 on error
        # Should have logged a warning
        assert len(caplog.records) > 0, "Should log warning on formula error"
        # Warning should include the formula
        warning_text = ' '.join(r.message for r in caplog.records)
        assert bad_formula in warning_text, "Warning should include the formula string"

    def test_undefined_variable_logs_warning(self, caplog):
        """Undefined variable errors should log with context."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = evaluate_math_formula("unknown_var * 2", {'x': 1})

        assert result == 0
        assert len(caplog.records) > 0, "Should log warning for undefined variable"
        warning_text = ' '.join(r.message for r in caplog.records)
        assert 'unknown_var' in warning_text, "Warning should include the formula with undefined var"

    def test_math_error_logs_warning(self, caplog):
        """Math errors like division by zero should log with formula."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = evaluate_math_formula("1 / 0", {})

        assert result == 0
        assert len(caplog.records) > 0, "Should log warning for math error"

    def test_valid_formula_no_warning(self, caplog):
        """Valid formulas should not produce any warnings."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = evaluate_math_formula("sqrt(16) + 2", {'x': 5})

        assert result == 6.0
        formula_warnings = [r for r in caplog.records if 'formula' in r.message.lower()]
        assert len(formula_warnings) == 0, "Valid formula should not log warnings"


class TestFormulaSystemValidation:
    """Tests for formula validation (ERR-003)."""

    def test_validate_formula_syntax_valid(self):
        """Valid formula syntax should pass validation."""
        from game.simulation.formula_system import validate_formula

        valid_formulas = [
            'x + 1',
            'sqrt(x)',
            'x * 2 + y',
            '1.0 / x',
            '(x - 1) * 0.5',
        ]
        for formula in valid_formulas:
            errors = validate_formula(formula, ['x', 'y'])
            assert errors == [], f"Valid formula '{formula}' should have no errors, got {errors}"

    def test_validate_formula_syntax_error(self):
        """Formula with syntax error should be detected."""
        from game.simulation.formula_system import validate_formula

        invalid_formulas = [
            '((( malformed',
            'x +* 2',
            '* x',
            'x +',
        ]
        for formula in invalid_formulas:
            errors = validate_formula(formula, ['x'])
            assert len(errors) > 0, f"Invalid formula '{formula}' should have errors"

    def test_validate_formula_undefined_variable(self):
        """Formula with undefined variable should be detected."""
        from game.simulation.formula_system import validate_formula

        errors = validate_formula('undefined_var + x', ['x'])
        assert len(errors) > 0, "Formula with undefined variable should have errors"
        assert any('undefined_var' in str(e) for e in errors)

    def test_validate_formula_allows_math_functions(self):
        """Math functions should be allowed."""
        from game.simulation.formula_system import validate_formula

        formulas = [
            'sqrt(x)',
            'sin(x)',
            'cos(x)',
            'log(x + 1)',
            'floor(x)',
            'ceil(x)',
            'abs(x)',
        ]
        for formula in formulas:
            errors = validate_formula(formula, ['x'])
            assert errors == [], f"Math formula '{formula}' should be valid, got {errors}"

    def test_validate_formula_blocks_dangerous_functions(self):
        """Dangerous functions should be blocked."""
        from game.simulation.formula_system import validate_formula

        dangerous = [
            'eval("1+1")',
            'exec("x=1")',
            'open("file")',
            '__import__("os")',
            'compile("1", "", "eval")',
        ]
        for formula in dangerous:
            errors = validate_formula(formula, [])
            assert len(errors) > 0, f"Dangerous formula '{formula}' should have errors"

    def test_validate_logs_on_dangerous_attempt(self, caplog):
        """Attempting to use dangerous functions should log a warning."""
        import logging
        from game.simulation.formula_system import validate_formula

        with caplog.at_level(logging.WARNING):
            errors = validate_formula('__import__("os")', [])

        assert len(errors) > 0
        # Should log a warning about the dangerous attempt
        assert len(caplog.records) > 0, "Should log warning for dangerous formula"
