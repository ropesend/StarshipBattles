"""
Build Queue Helpers - Pure formatting functions for build queue display.

Extracted from BuildQueueScreen (PROJ-86 Phase 8).
"""
from game.core.constants import PLANET_RESOURCES

# Resource abbreviations for compact UI display
RESOURCE_ABBREVS = {
    "Metals": "Met",
    "Organics": "Org",
    "Vapors": "Vap",
    "Radioactives": "Rad",
    "Exotics": "Exo",
}

# Short abbreviations for very compact displays (e.g., cost strings)
RESOURCE_ABBREVS_SHORT = {
    "Metals": "M",
    "Organics": "O",
    "Vapors": "V",
    "Radioactives": "R",
    "Exotics": "E",
}


def format_empire_resources(empire) -> str:
    """Format empire resource pool for display in build queue bottom bar.

    Args:
        empire: Empire instance with resource_pool.

    Returns:
        Formatted string like "Met: 500/1000  Org: 200/500  Vap: 0"
    """
    parts = []
    for res in PLANET_RESOURCES:
        current = empire.resource_pool.get(res, 0.0)
        cap = empire.max_storage.get(res, 0.0)
        abbr = RESOURCE_ABBREVS.get(res, res[:3])
        if cap > 0:
            parts.append(f"{abbr}: {int(current)}/{int(cap)}")
        elif current > 0:
            parts.append(f"{abbr}: {int(current)}")
    return "  |  ".join(parts) if parts else "No resources"


def calculate_per_turn_spend(
    queue_item: dict, build_rate: dict
) -> dict:
    """Calculate proportional per-turn resource spend for a queue item.

    Uses the limiting-resource formula: find the resource that takes the
    longest to complete (max remaining/rate), then each resource spends
    remaining/limiting_turns per turn. This matches the proportional
    calculation in ProductionEngine._calculate_tick_expenditure().

    Args:
        queue_item: Dict with 'total_cost' and 'resources_consumed' keys.
        build_rate: Dict mapping resource name to production rate per turn.

    Returns:
        Dict mapping resource name to per-turn spend amount. Returns empty
        dict if no remaining costs. Returns all zeros if any required
        resource has zero production rate.
    """
    total_cost = queue_item.get("total_cost", {})
    resources_consumed = queue_item.get("resources_consumed", {})

    if not total_cost:
        return {}

    # Calculate remaining cost per resource
    remaining = {}
    for res, amount in total_cost.items():
        rem = max(0.0, amount - resources_consumed.get(res, 0.0))
        if rem > 0:
            remaining[res] = rem

    # No remaining cost = fully consumed
    if not remaining:
        return {res: 0.0 for res in total_cost}

    # Find limiting resource (max remaining/rate)
    limiting_turns = 0.0
    for res, rem in remaining.items():
        rate = build_rate.get(res, 0.0)
        if rate <= 0:
            # Cannot build - zero rate for a required resource
            return {res: 0.0 for res in total_cost}
        turns = rem / rate
        if turns > limiting_turns:
            limiting_turns = turns

    if limiting_turns <= 0:
        return {res: 0.0 for res in total_cost}

    # Calculate per-turn spend: remaining / limiting_turns
    result = {}
    for res in total_cost:
        rem = remaining.get(res, 0.0)
        result[res] = rem / limiting_turns

    return result


def format_resource_cost(cost: dict) -> str:
    """Format resource cost dict into compact display string.

    Args:
        cost: Dict mapping resource type to amount.

    Returns:
        Compact string like "M:100 O:50 V:20"
    """
    parts = []
    for res in PLANET_RESOURCES:
        amount = cost.get(res, 0)
        if amount > 0:
            abbr = RESOURCE_ABBREVS_SHORT.get(res, res[0])
            parts.append(f"{abbr}:{int(amount)}")
    return " ".join(parts) if parts else ""
