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
