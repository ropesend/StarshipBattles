"""
Security and functionality tests for formula_system.py.

These tests verify:
1. The eval() sandbox properly blocks dangerous operations
2. Basic formula evaluation works correctly

PROJ-45: Updated to expect FormulaException on errors instead of returning 0.
Use safe_evaluate_math_formula for backwards-compatible behavior that returns defaults.
"""

import pytest
from game.core.formula_evaluator import evaluate_math_formula, safe_evaluate_math_formula
from game.core.exceptions import FormulaException


class TestFormulaSystemSecurity:
    """Security tests to verify the eval() sandbox blocks dangerous operations.

    The sandbox blocks dangerous operations by raising FormulaException.
    These tests verify that malicious formulas cannot execute and raise exceptions.
    """

    def test_eval_sandbox_blocks_imports(self):
        """Verify that __import__ is blocked by the sandbox (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("__import__('os').system('echo pwned')", {})

    def test_eval_sandbox_blocks_builtins(self):
        """Verify that builtin functions like open() are blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("open('/etc/passwd')", {})

    def test_eval_sandbox_blocks_exec(self):
        """Verify that exec() is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("exec('x=1')", {})

    def test_eval_sandbox_blocks_eval(self):
        """Verify that nested eval() is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("eval('1+1')", {})

    def test_eval_sandbox_blocks_compile(self):
        """Verify that compile() is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("compile('1+1', '', 'eval')", {})

    def test_eval_sandbox_blocks_getattr_builtins(self):
        """Verify that accessing __builtins__ via tricks is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("getattr(__builtins__, 'open')", {})

    def test_eval_sandbox_blocks_globals_access(self):
        """Verify that globals() is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("globals()", {})

    def test_eval_sandbox_blocks_locals_access(self):
        """Verify that locals() is blocked (raises FormulaException)."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("locals()", {})

    def test_sandbox_allows_valid_math(self):
        """Verify that valid math expressions still work (not blocked)."""
        # This ensures our security tests aren't false positives
        result = evaluate_math_formula("sqrt(16) + 2", {})
        assert result == 6.0, "Valid math should work"


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

    def test_error_raises_formula_exception(self):
        """Test that errors raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("undefined_var", {})
        with pytest.raises(FormulaException):
            evaluate_math_formula("1 / 0", {})
        with pytest.raises(FormulaException):
            evaluate_math_formula("invalid syntax ??", {})

    def test_safe_evaluate_returns_zero_on_error(self):
        """Test that safe_evaluate_math_formula returns default on error."""
        assert safe_evaluate_math_formula("undefined_var", {}, default=0) == 0
        assert safe_evaluate_math_formula("1 / 0", {}, default=0) == 0
        assert safe_evaluate_math_formula("invalid syntax ??", {}, default=0) == 0


class TestFormulaSystemErrorLogging:
    """Tests for error logging in formula evaluation (ERR-002).

    PROJ-45: evaluate_math_formula now raises FormulaException.
    Use safe_evaluate_math_formula for logging behavior.
    """

    def test_syntax_error_raises_exception(self):
        """Syntax errors should raise FormulaException with details."""
        bad_formula = "1 +* 2"  # Actually invalid Python syntax

        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula(bad_formula, {})

        # Exception should include the formula
        assert bad_formula in exc_info.value.context.get("formula", "")

    def test_safe_evaluate_logs_warning(self, caplog):
        """safe_evaluate_math_formula should log warning on error."""
        import logging
        bad_formula = "1 +* 2"

        with caplog.at_level(logging.WARNING):
            result = safe_evaluate_math_formula(bad_formula, {}, default=0)

        assert result == 0
        assert len(caplog.records) > 0, "Should log warning on formula error"
        warning_text = ' '.join(r.message for r in caplog.records)
        assert bad_formula in warning_text, "Warning should include the formula string"

    def test_undefined_variable_raises_exception(self):
        """Undefined variable errors should raise FormulaException."""
        with pytest.raises(FormulaException) as exc_info:
            evaluate_math_formula("unknown_var * 2", {'x': 1})

        assert "unknown_var" in str(exc_info.value).lower()

    def test_math_error_raises_exception(self):
        """Math errors like division by zero should raise FormulaException."""
        with pytest.raises(FormulaException):
            evaluate_math_formula("1 / 0", {})

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
        from game.core.formula_evaluator import validate_formula

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
        from game.core.formula_evaluator import validate_formula

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
        from game.core.formula_evaluator import validate_formula

        errors = validate_formula('undefined_var + x', ['x'])
        assert len(errors) > 0, "Formula with undefined variable should have errors"
        assert any('undefined_var' in str(e) for e in errors)

    def test_validate_formula_allows_math_functions(self):
        """Math functions should be allowed."""
        from game.core.formula_evaluator import validate_formula

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
        from game.core.formula_evaluator import validate_formula

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
        from game.core.formula_evaluator import validate_formula

        with caplog.at_level(logging.WARNING):
            errors = validate_formula('__import__("os")', [])

        assert len(errors) > 0
        # Should log a warning about the dangerous attempt
        assert len(caplog.records) > 0, "Should log warning for dangerous formula"
