"""Formula evaluation system for Starship Battles.

This module provides safe formula evaluation for component stats, modifiers,
and other dynamic calculations using Python's eval() with a restricted sandbox.

The primary API is FormulaEvaluator, a unified evaluator that replaces both
the original module-level functions and ModifierEffectEvaluator formula methods.

Use FormulaContext to configure behavior (e.g., caret-as-power for modifiers).

PROJ-45: Error handling updated to raise FormulaException for evaluation errors.
PROJ-242: Unified FormulaEvaluator class replaces module-level functions.
"""
import ast
import builtins
import logging
import math
from dataclasses import dataclass, field
from typing import Dict, Any, Union, List, Optional
from game.core.exceptions import FormulaException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)

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


# =============================================================================
# Unified FormulaEvaluator (PROJ-242)
# =============================================================================


@dataclass(frozen=True)
class FormulaContext:
    """Configuration for formula evaluation behavior.

    Attributes:
        caret_as_power: If True, replace '^' with '**' before eval.
            Used by modifier formulas which use '^' for exponentiation.
        extra_functions: Additional name->callable mappings to add to eval context.
            E.g., {'ln': math.log} for modifier formulas.
    """
    caret_as_power: bool = False
    extra_functions: Dict[str, Any] = field(default_factory=dict)


class FormulaEvaluator:
    """Unified formula evaluation with configurable context.

    Provides a single eval() sandbox for all formula evaluation in the game.
    Replaces both module-level evaluate_math_formula() and
    ModifierEffectEvaluator.evaluate_formula().

    Usage:
        # Basic evaluation (component formulas)
        result = FormulaEvaluator.evaluate("sqrt(mass) * 2", {'mass': 100})

        # Modifier evaluation (with caret substitution)
        result = FormulaEvaluator.evaluate(
            "param ^ 2", {'param': 3.0},
            formula_context=FormulaEvaluator.MODIFIER_CONTEXT
        )

        # Safe evaluation with fallback
        result = FormulaEvaluator.safe_evaluate("x + y", {'x': 1}, default=0)
    """

    # Default context used when none specified
    DEFAULT_CONTEXT = FormulaContext()

    # Modifier context with caret substitution and ln alias
    MODIFIER_CONTEXT = FormulaContext(
        caret_as_power=True,
        extra_functions={'ln': math.log}
    )

    @classmethod
    def evaluate(
        cls,
        formula: str,
        context: Dict[str, Any],
        formula_context: Optional[FormulaContext] = None,
    ) -> Union[int, float]:
        """Safely evaluate a mathematical formula string within a given context.

        Args:
            formula: The formula string (e.g. "sqrt(mass) * 2").
            context: Dictionary of variable names and values available to the formula.
            formula_context: Optional FormulaContext to configure behavior.
                Defaults to DEFAULT_CONTEXT (no caret substitution).

        Returns:
            The result of the evaluation (int or float).

        Raises:
            FormulaException: If evaluation fails (syntax error, undefined variable,
                runtime error, or security violation).
        """
        if formula_context is None:
            formula_context = cls.DEFAULT_CONTEXT

        # Build allowed namespace from math module
        names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}

        # Add safe builtins (min, max, abs, etc.)
        for name in ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                names[name] = getattr(builtins, name)

        # Add ln alias (always available -- superset of both old systems)
        names['ln'] = math.log

        # Add extra functions from formula context
        if formula_context.extra_functions:
            names.update(formula_context.extra_functions)

        # Add caller's context variables
        names.update(context)

        # Apply caret substitution if configured
        eval_formula = formula
        if formula_context.caret_as_power:
            eval_formula = formula.replace('^', '**')

        # Build error context for exceptions
        error_context = {
            "formula": formula,
            "available_vars": list(context.keys()) if context else [],
        }

        try:
            return eval(eval_formula, {"__builtins__": {}}, names)
        except SyntaxError as e:
            raise FormulaException(
                f"Syntax error in formula '{formula}': {e.msg}",
                code=ErrorCode.FORMULA_SYNTAX_ERROR.value,
                context=error_context
            ) from e
        except NameError as e:
            raise FormulaException(
                f"Undefined variable in formula '{formula}': {e}",
                code=ErrorCode.FORMULA_UNDEFINED_VAR.value,
                context=error_context
            ) from e
        except (ZeroDivisionError, ValueError, ArithmeticError) as e:
            raise FormulaException(
                f"Runtime error in formula '{formula}': {e}",
                code=ErrorCode.EVAL_ERROR.value,
                context=error_context
            ) from e
        except Exception as e:  # Intentional broad catch: catch-and-convert to FormulaException for any eval() error
            raise FormulaException(
                f"Formula evaluation failed for '{formula}': {e}",
                code=ErrorCode.FORMULA_GENERAL_ERROR.value,
                context=error_context
            ) from e

    @classmethod
    def validate(
        cls,
        formula: str,
        allowed_variables: List[str],
        formula_context: Optional[FormulaContext] = None,
    ) -> List[str]:
        """Validate a formula string before evaluation.

        Args:
            formula: The formula string to validate.
            allowed_variables: List of variable names allowed in the formula.
            formula_context: Optional FormulaContext to configure behavior.
                If caret_as_power is True, '^' is replaced with '**' before parsing.

        Returns:
            List of error messages. Empty list if formula is valid.
        """
        if formula_context is None:
            formula_context = cls.DEFAULT_CONTEXT

        errors = []

        # Apply caret substitution if configured
        parse_formula = formula
        if formula_context.caret_as_power:
            parse_formula = formula.replace('^', '**')

        # Try to parse the formula as Python AST
        try:
            tree = ast.parse(parse_formula, mode='eval')
        except SyntaxError as e:
            errors.append(f"Syntax error: {e.msg}")
            return errors

        # Walk the AST to check for allowed names
        allowed_names = (
            ALLOWED_MATH_FUNCTIONS | ALLOWED_BUILTINS | {'ln'}
            | set(allowed_variables)
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                name = node.id
                if name in DANGEROUS_NAMES:
                    logger.warning(
                        f"Dangerous function '{name}' detected in formula: {formula}"
                    )
                    errors.append(f"Dangerous function not allowed: {name}")
                elif name not in allowed_names:
                    errors.append(f"Undefined variable: {name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in DANGEROUS_NAMES:
                        logger.warning(
                            f"Dangerous function call '{func_name}' detected "
                            f"in formula: {formula}"
                        )
                        errors.append(f"Dangerous function not allowed: {func_name}")

        return errors

    @classmethod
    def safe_evaluate(
        cls,
        formula: str,
        context: Dict[str, Any],
        default: Union[int, float] = 0,
        formula_context: Optional[FormulaContext] = None,
    ) -> Union[int, float]:
        """Safely evaluate a formula with fallback to default on error.

        Wrapper around evaluate() that catches FormulaException and returns
        a default value instead, while logging a warning.

        Args:
            formula: The formula string.
            context: Dictionary of variable names and values.
            default: Value to return if evaluation fails. Defaults to 0.
            formula_context: Optional FormulaContext to configure behavior.

        Returns:
            The result of the evaluation, or the default value on error.
        """
        try:
            return cls.evaluate(formula, context, formula_context)
        except FormulaException as e:
            logger.warning(f"Formula evaluation failed for '{formula}': {e}")
            return default


# =============================================================================
# Backward-compatible aliases for existing test imports
# =============================================================================

evaluate_math_formula = FormulaEvaluator.evaluate
safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
validate_formula = FormulaEvaluator.validate
