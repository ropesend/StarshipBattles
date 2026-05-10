"""
Serialize TechTree data back to JSON format.

Produces output compatible with TechTree.load_from_json() for round-trip fidelity.
Field ordering matches the existing techtree.json convention.
"""
import json
from typing import Any, Dict, List, Optional

from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.tech_tree import TechTree


def tech_requirement_to_dict(req: TechRequirement) -> Dict[str, Any]:
    """Serialize a TechRequirement to JSON-compatible dict."""
    d: Dict[str, Any] = {
        "node_id": req.node_id,
        "level_range": list(req.level_range),
    }
    if req.negate:
        d["negate"] = True
    return d


def tech_node_to_dict(node: TechNode) -> Dict[str, Any]:
    """Serialize a TechNode to JSON-compatible dict.

    Field order matches the existing techtree.json convention:
    comment, id, name, max_levels, requirements, base_decay, volatility, price, price_curve
    """
    d: Dict[str, Any] = {}

    if node.comment:
        d["comment"] = node.comment

    d["id"] = node.id
    d["name"] = node.name
    d["max_levels"] = node.max_levels

    # Serialize requirements: List[List[TechRequirement]] → List[List[dict]]
    d["requirements"] = [
        [tech_requirement_to_dict(req) for req in or_group]
        for or_group in node.requirements
    ]

    d["base_decay"] = node.base_decay
    d["volatility"] = node.volatility
    d["price"] = node.price
    d["price_curve"] = node.price_curve

    return d


def tech_tree_to_dict(node_order: List[str], nodes: Dict[str, TechNode]) -> Dict[str, Any]:
    """Serialize the full tech tree to a JSON-compatible dict.

    Args:
        node_order: List of node IDs in the desired JSON array order.
        nodes: Dict mapping node ID to TechNode.

    Returns:
        Dict with "tech_tree" key containing the serialized node list.
    """
    return {
        "tech_tree": [tech_node_to_dict(nodes[nid]) for nid in node_order if nid in nodes]
    }


def save_tech_tree(
    file_path: str,
    node_order: List[str],
    nodes: Dict[str, TechNode],
) -> bool:
    """Save the tech tree to a JSON file.

    Uses indent=4 to match the existing techtree.json formatting.

    Args:
        file_path: Output file path.
        node_order: List of node IDs in the desired JSON array order.
        nodes: Dict mapping node ID to TechNode.

    Returns:
        True on success, False on error.
    """
    data = tech_tree_to_dict(node_order, nodes)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.write('\n')  # trailing newline
        return True
    except (OSError, TypeError) as e:
        print(f"Error saving tech tree: {e}")
        return False


def load_node_order_from_json(file_path: str) -> List[str]:
    """Load just the node ID ordering from a techtree JSON file.

    This preserves the original ordering for round-trip fidelity.

    Args:
        file_path: Path to techtree.json

    Returns:
        List of node IDs in file order.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    order = []
    for entry in data.get("tech_tree", []):
        if "id" in entry:
            order.append(entry["id"])
    return order
