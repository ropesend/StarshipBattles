import math
from typing import Dict, Any, Union

def evaluate_math_formula(formula: str, context: Dict[str, Any]) -> Union[int, float]:
    """
    Safely evaluate a mathematical formula string within a given context.
    
    Args:
        formula: The formula string (e.g. "sqrt(mass) * 2"). Should NOT start with '='.
        context: Dictionary of variable names and values available to the formula.
        
    Returns:
        The result of the evaluation (int or float). Returns 0 on error.
    """
    # Build allowed namespace from math module and context
    # We allow basic math functions and constants, plus provided context variables
    names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    names.update(context)
    
    try:
        # Use eval with restricted globals (none) and our constructed locals
        return eval(formula, {"__builtins__": {}}, names)
    except Exception as e:
        # Log error in a real app, for now just return 0 as per original behavior
        # print(f"Error evaluating formula '{formula}': {e}")
        return 0
