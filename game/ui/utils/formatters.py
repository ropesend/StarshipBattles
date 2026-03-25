"""Shared UI formatting utilities.

Provides common formatting functions used across UI panels and screens,
eliminating duplicated inline patterns for number display and color mapping.

Usage:
    from game.ui.utils.formatters import format_compact_number, get_damage_color

    format_compact_number(1500)      # "2k"
    format_compact_number(2_500_000) # "2.5M"
    get_damage_color(0.75)           # HP_HEALTHY (green)
"""
from typing import Tuple

from game.ui.colors import HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, HP_DESTROYED


def format_compact_number(value: float) -> str:
    """Format a number with K/M suffixes for compact display.

    Converts large numbers to human-readable strings with metric suffixes.
    Provides consistent formatting across all UI panels and screens.

    Args:
        value: The numeric value to format.

    Returns:
        Formatted string: "2.5M" for millions, "15k" for thousands,
        or integer string for smaller values.
    """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.0f}k"
    elif value <= -1_000:
        # Negative large numbers formatted as plain integers
        return str(int(value))
    else:
        return str(int(value))


def get_damage_color(hp_pct: float, is_active: bool = True) -> Tuple[int, int, int]:
    """Get color representing damage/health level.

    Maps an HP percentage to a color using consistent thresholds
    across all UI views (battle, strategy, detail panels).

    Args:
        hp_pct: HP as fraction 0.0-1.0
        is_active: Whether the entity is active/powered. Inactive
                   entities always show as destroyed (gray).

    Returns:
        RGB tuple for damage visualization:
        - Green (HP_HEALTHY) for >= 50%
        - Yellow (HP_DAMAGED) for 25-49%
        - Red (HP_CRITICAL) for 1-24%
        - Gray (HP_DESTROYED) for <= 0% or inactive
    """
    if not is_active:
        return HP_DESTROYED
    if hp_pct <= 0:
        return HP_DESTROYED
    if hp_pct < 0.25:
        return HP_CRITICAL
    if hp_pct < 0.50:
        return HP_DAMAGED
    return HP_HEALTHY
