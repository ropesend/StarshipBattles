"""Formula evaluation system - re-export shim.

Canonical location: game.core.formula_evaluator
This module re-exports for backward compatibility.

PROJ-257: FormulaEvaluator extracted to game.core.formula_evaluator.
"""
from game.core.formula_evaluator import (  # noqa: F401
    FormulaEvaluator,
    FormulaContext,
    ALLOWED_MATH_FUNCTIONS,
    ALLOWED_BUILTINS,
    DANGEROUS_NAMES,
)

# Backward-compatible aliases
evaluate_math_formula = FormulaEvaluator.evaluate
safe_evaluate_math_formula = FormulaEvaluator.safe_evaluate
validate_formula = FormulaEvaluator.validate
