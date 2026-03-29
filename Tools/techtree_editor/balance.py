"""
Balance preview utilities.

Wraps ResearchService estimation methods to provide
balance analysis for the editor.
"""
from typing import Dict, List, Tuple

from game.research.data.tech_node import TechNode
from game.research.systems.research_service import ResearchService


# Standard RP test levels for balance preview
RP_LEVELS = (10, 25, 50, 100)


def estimate_node_balance(node: TechNode, level: int = 1) -> Dict:
    """Calculate balance metrics for a node at a given target level.

    Args:
        node: The tech node to analyze.
        level: Target level (1-based).

    Returns:
        Dict with keys: effective_price, and per-RP-level metrics.
    """
    effective_price = node.get_effective_price(level)

    metrics = {
        "effective_price": effective_price,
        "rp_levels": {},
    }

    for rp in RP_LEVELS:
        effective_rp = rp / effective_price if effective_price > 0 else 0
        added_chance = ResearchService.calculate_added_chance(node.volatility, effective_rp)
        net_chance = added_chance - node.base_decay
        est_turns = ResearchService.estimate_turns_to_breakthrough(
            node.volatility, node.base_decay, effective_rp,
        )

        metrics["rp_levels"][rp] = {
            "effective_rp": round(effective_rp, 2),
            "added_chance": round(added_chance, 4),
            "net_chance": round(net_chance, 4),
            "est_turns": round(est_turns, 1) if est_turns != float('inf') else float('inf'),
            "starvation": net_chance <= 0,
        }

    return metrics


def find_outliers(nodes: Dict[str, TechNode], rp: int = 50) -> List[Tuple[str, float, str]]:
    """Find nodes with unusually high or low turns-to-breakthrough.

    Args:
        nodes: Dict of node_id → TechNode.
        rp: RP level to test at.

    Returns:
        List of (node_id, est_turns, reason) for outlier nodes.
    """
    estimates = {}
    for nid, node in nodes.items():
        effective_price = node.get_effective_price(1)
        effective_rp = rp / effective_price if effective_price > 0 else 0
        est = ResearchService.estimate_turns_to_breakthrough(
            node.volatility, node.base_decay, effective_rp,
        )
        if est != float('inf'):
            estimates[nid] = est

    if not estimates:
        return []

    values = sorted(estimates.values())
    median = values[len(values) // 2]

    outliers = []
    for nid, est in estimates.items():
        if est > median * 2.5:
            outliers.append((nid, est, f"Very slow ({est:.0f} turns, median {median:.0f})"))
        elif est < median * 0.3:
            outliers.append((nid, est, f"Very fast ({est:.0f} turns, median {median:.0f})"))

    # Also flag infinite (starvation) nodes
    for nid, node in nodes.items():
        if nid not in estimates:
            outliers.append((nid, float('inf'), "RP starvation at this level"))

    return sorted(outliers, key=lambda x: x[1], reverse=True)
