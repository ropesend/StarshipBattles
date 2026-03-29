"""Shared production math utilities.

PROJ-233: Extracted from ProductionEngine._calculate_tick_expenditure
and construction_forecast.forecast_queue_turn_spend to eliminate duplication.
"""
from typing import Dict, Optional


def find_limiting_resource_ticks(
    remaining_cost: Dict[str, float],
    rate_per_turn: Dict[str, float],
    ticks_per_turn: int = 100,
) -> Optional[float]:
    """Return total ticks needed to complete, or None if any required rate is zero.

    Finds the limiting resource (the one that takes longest to produce at the
    given rate) and returns the number of ticks needed.

    Args:
        remaining_cost: Resource amounts still needed (resource_name -> amount).
        rate_per_turn: Production rate per turn (resource_name -> amount_per_turn).
        ticks_per_turn: Number of ticks per turn (default 100).

    Returns:
        Total ticks needed (float), or None if any required resource has zero rate.
    """
    if not remaining_cost:
        return 0.0

    max_ticks = 0.0
    for resource, amount in remaining_cost.items():
        rate = rate_per_turn.get(resource, 0.0)
        if rate <= 0:
            return None
        rate_per_tick = rate / ticks_per_turn
        ticks = amount / rate_per_tick
        if ticks > max_ticks:
            max_ticks = ticks
    return max_ticks
