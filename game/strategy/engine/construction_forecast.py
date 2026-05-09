"""
Construction Forecast - Queue-level distribution of per-turn resource spend.

Walks a construction queue sequentially with carry-over capacity, mirroring
ProductionEngine._process_queue_tick_dynamic() logic. Each item consumes
production capacity until the turn's budget is exhausted.

Used by:
- FEAT-06: Aggregate construction expenses for Treasury display
- BUG-98: Per-item "next turn" column values in build queue UI
"""

from functools import lru_cache
from typing import Dict, List

from game.core.resources import ResourceCatalog
from game.strategy.engine.production_math import find_limiting_resource_ticks


@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-397 F-07: lazy-load planetary resource IDs (was module-level)."""
    return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))


def forecast_queue_turn_spend(
    queue: List[Dict], build_rate: Dict[str, float]
) -> List[Dict[str, float]]:
    """Calculate per-item resource spend for one turn across a queue.

    Walks items sequentially with carry-over capacity. When an item
    completes mid-turn, remaining capacity flows to the next item.
    Uses the limiting-resource formula from ProductionEngine.

    Args:
        queue: Construction queue (list of item dicts with
               'total_cost' and 'resources_consumed' keys).
        build_rate: Per-resource production rates (units per turn).

    Returns:
        List of dicts (one per queue item), each mapping resource name
        to the amount that will be spent on that item during the next turn.
        Items beyond production capacity get all-zero dicts.
    """
    if not queue or not build_rate:
        return [{r: 0.0 for r in _get_planetary_ids()} for _ in queue]

    remaining_capacity = 1.0  # Fraction of turn remaining
    result: List[Dict[str, float]] = []

    for item in queue:
        if remaining_capacity <= 0.0001:
            # No capacity left — zero spend for remaining items
            result.append({r: 0.0 for r in _get_planetary_ids()})
            continue

        total_cost = item.get("total_cost", {})
        resources_consumed = item.get("resources_consumed", {})

        if not total_cost:
            result.append({r: 0.0 for r in _get_planetary_ids()})
            continue

        # Calculate remaining cost per resource
        remaining_cost = {}
        for res, amount in total_cost.items():
            rem = max(0.0, amount - resources_consumed.get(res, 0.0))
            if rem > 0:
                remaining_cost[res] = rem

        if not remaining_cost:
            # Item already complete — zero spend, no capacity consumed
            result.append({r: 0.0 for r in _get_planetary_ids()})
            continue

        # Find limiting resource (PROJ-233: shared formula, ticks_per_turn=1 for turns)
        turns_needed = find_limiting_resource_ticks(
            remaining_cost, build_rate, ticks_per_turn=1
        )
        if turns_needed is None or turns_needed <= 0:
            result.append({r: 0.0 for r in _get_planetary_ids()})
            continue

        # How much of the turn this item uses
        turns_to_spend = min(remaining_capacity, turns_needed)

        # Calculate per-resource spend for this item
        item_spend = {}
        for res in _get_planetary_ids():
            rate = build_rate.get(res, 0.0)
            rem = remaining_cost.get(res, 0.0)
            spend = rate * turns_to_spend
            # Clamp to remaining cost (don't overshoot)
            spend = min(spend, rem)
            item_spend[res] = spend

        result.append(item_spend)
        remaining_capacity -= turns_to_spend

    return result
