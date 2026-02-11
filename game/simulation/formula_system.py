"""Formula evaluation system for Starship Battles.

This module provides safe formula evaluation for component stats, modifiers,
and other dynamic calculations using Python's eval() with a restricted sandbox.

PROJ-45: Error handling updated to raise FormulaException for evaluation errors.
"""
import ast
import math
from typing import Dict, Any, Union, List, Optional
from game.core.logger import log_warning
from game.core.exceptions import FormulaException

# Whitelisted math functions that are allowed in formulas
ALLOWED_MATH_FUNCTIONS = {
    name for name in dir(math) if not name.startswith('_')
}

# Safe builtin functions for math
ALLOWED_BUILTINS = {'abs', 'min', 'max', 'round', 'sum', 'len', 'int', 'float', 'pow'}

# Dangerous builtins that must never be allowed
DANGEROUS_NAMES = {
    'eval', 'exec', 'compile', 'open', 'input', 'print',
    '__import__', 'globals', 'locals', 'vars', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr',
    'breakpoint', 'help', 'exit', 'quit',
}

# Error codes for formula failures
FORMULA_ERROR_SYNTAX = "F001"      # Syntax error in formula
FORMULA_ERROR_UNDEFINED = "F002"  # Undefined variable
FORMULA_ERROR_RUNTIME = "F003"    # Runtime error (div by zero, domain error)
FORMULA_ERROR_SECURITY = "F004"   # Security violation (dangerous function)


def validate_formula(formula: str, allowed_variables: List[str]) -> List[str]:
    """
    Validate a formula string before evaluation.

    Args:
        formula: The formula string to validate.
        allowed_variables: List of variable names allowed in the formula.

    Returns:
        List of error messages. Empty list if formula is valid.
    """
    errors = []

    # Try to parse the formula as Python AST
    try:
        tree = ast.parse(formula, mode='eval')
    except SyntaxError as e:
        errors.append(f"Syntax error: {e.msg}")
        return errors

    # Walk the AST to check for allowed names
    allowed_names = ALLOWED_MATH_FUNCTIONS | ALLOWED_BUILTINS | set(allowed_variables)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            name = node.id
            if name in DANGEROUS_NAMES:
                log_warning(f"Dangerous function '{name}' detected in formula: {formula}")
                errors.append(f"Dangerous function not allowed: {name}")
            elif name not in allowed_names:
                errors.append(f"Undefined variable: {name}")
        elif isinstance(node, ast.Call):
            # Check function calls
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in DANGEROUS_NAMES:
                    log_warning(f"Dangerous function call '{func_name}' detected in formula: {formula}")
                    errors.append(f"Dangerous function not allowed: {func_name}")

    return errors


def evaluate_math_formula(formula: str, context: Dict[str, Any]) -> Union[int, float]:
    """
    Safely evaluate a mathematical formula string within a given context.

    Args:
        formula: The formula string (e.g. "sqrt(mass) * 2"). Should NOT start with '='.
        context: Dictionary of variable names and values available to the formula.

    Returns:
        The result of the evaluation (int or float).

    Raises:
        FormulaException: If evaluation fails (syntax error, undefined variable,
            runtime error, or security violation).
    """
    # SECURITY NOTE: eval() is used here for formula evaluation.
    # Risk mitigation:
    # - __builtins__ is disabled (no imports, no dangerous functions)
    # - names dict is whitelisted to only allow specific variables (math functions + context)
    # - Formulas are only loaded from internal game data files (data/components.json)
    # - No user input or external sources are evaluated
    # - Security tests in tests/unit/systems/test_formula_system.py verify sandbox blocks attacks

    # Build allowed namespace from math module and context
    # We allow basic math functions and constants, plus provided context variables
    names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    # Add safe builtins (min, max, abs, etc.) using builtins module directly
    import builtins
    for name in ALLOWED_BUILTINS:
        if hasattr(builtins, name):
            names[name] = getattr(builtins, name)
    names.update(context)

    # Build error context for exceptions
    error_context = {
        "formula": formula,
        "available_vars": list(context.keys()) if context else [],
    }

    try:
        # Use eval with restricted globals (none) and our constructed locals
        return eval(formula, {"__builtins__": {}}, names)
    except SyntaxError as e:
        raise FormulaException(
            f"Syntax error in formula '{formula}': {e.msg}",
            code=FORMULA_ERROR_SYNTAX,
            context=error_context
        ) from e
    except NameError as e:
        raise FormulaException(
            f"Undefined variable in formula '{formula}': {e}",
            code=FORMULA_ERROR_UNDEFINED,
            context=error_context
        ) from e
    except (ZeroDivisionError, ValueError, ArithmeticError) as e:
        raise FormulaException(
            f"Runtime error in formula '{formula}': {e}",
            code=FORMULA_ERROR_RUNTIME,
            context=error_context
        ) from e
    except Exception as e:  # Intentional broad catch: catch-and-convert to FormulaException for any eval() error
        raise FormulaException(
            f"Formula evaluation failed for '{formula}': {e}",
            code=FORMULA_ERROR_SECURITY,
            context=error_context
        ) from e


def safe_evaluate_math_formula(
    formula: str,
    context: Dict[str, Any],
    default: Union[int, float] = 0
) -> Union[int, float]:
    """
    Safely evaluate a formula with fallback to default on error.

    Wrapper around evaluate_math_formula that catches FormulaException and
    returns a default value instead, while logging a warning. Use this when
    formula errors should not be fatal.

    Args:
        formula: The formula string (e.g. "sqrt(mass) * 2"). Should NOT start with '='.
        context: Dictionary of variable names and values available to the formula.
        default: Value to return if evaluation fails. Defaults to 0.

    Returns:
        The result of the evaluation, or the default value on error.
    """
    try:
        return evaluate_math_formula(formula, context)
    except FormulaException as e:
        log_warning(f"Formula evaluation failed for '{formula}': {e}")
        return default
