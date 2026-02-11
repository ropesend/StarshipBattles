"""Shared value formatting utilities for test lab UI.

Consolidates duplicate formatting logic from test_run_details.py and test_run_card.py.
DUP-UI1-002 resolution.
"""


def format_value(value, precision: str = "full") -> str:
    """Format a value for display.

    Args:
        value: The value to format (can be None, int, float, bool, or other)
        precision: 'full' for details panel (more precision) or 'compact' for cards

    Returns:
        Formatted string representation of the value
    """
    if value is None:
        return "None"

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return _format_float(value, precision)

    return str(value)


def _format_float(value: float, precision: str) -> str:
    """Format a float value with appropriate precision.

    Args:
        value: Float value to format
        precision: 'full' or 'compact'

    Returns:
        Formatted string
    """
    # Check if it's essentially an integer
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))

    # Check if it's a probability/percentage (between 0 and 1, exclusive)
    if 0 < value < 1:
        if precision == "compact":
            return f"{value:.1%}"
        return f"{value:.2%}"

    # Check if it's a very small number (use scientific notation)
    threshold = 0.001 if precision == "compact" else 0.0001
    if abs(value) < threshold and value != 0:
        if precision == "compact":
            return f"{value:.2e}"
        return f"{value:.6e}"

    # Large numbers in compact mode
    if precision == "compact" and abs(value) >= 100:
        return f"{value:.1f}"

    # Regular float formatting
    if precision == "compact":
        return f"{value:.3f}"
    return f"{value:.4f}"
