"""
Auto-layout algorithm for tech tree nodes.

Generates initial positions using depth-based column layout with
section grouping. Positions can be overridden via sidecar file.
"""
from typing import Dict, List, Tuple

from game.research.data.tech_tree import TechTree

from .model import EditorModel, Section


# Layout constants
COLUMN_SPACING = 350    # Horizontal distance between depth levels
ROW_SPACING = 120       # Vertical distance between nodes
SECTION_GAP = 60        # Extra vertical gap between sections
START_X = 50            # Left margin
START_Y = 50            # Top margin


def auto_layout(model: EditorModel) -> Dict[str, Tuple[float, float]]:
    """Generate positions for all nodes using depth-based columns.

    Nodes are arranged left-to-right by dependency depth,
    vertically grouped by section within each column.

    Args:
        model: The editor model with tech_tree and sections.

    Returns:
        Dict mapping node_id to (x, y) position.
    """
    tree = model.tech_tree
    positions: Dict[str, Tuple[float, float]] = {}

    # Group nodes by depth
    max_depth = tree.get_max_depth()
    depth_buckets: Dict[int, List[str]] = {d: [] for d in range(max_depth + 1)}

    for node_id in tree.nodes:
        depth = tree.calculate_depth(node_id)
        depth_buckets[depth].append(node_id)

    # Build section ordering lookup for vertical sorting
    section_order = _build_section_order(model.sections)

    # Layout each depth column
    for depth in range(max_depth + 1):
        x = START_X + depth * COLUMN_SPACING
        node_ids = depth_buckets[depth]

        # Sort by section order, then by position within section
        node_ids.sort(key=lambda nid: _sort_key(nid, section_order, model.sections))

        # Assign vertical positions with section gaps
        y = START_Y
        prev_section = None
        for nid in node_ids:
            current_section = _get_section_name(nid, model.sections)
            if prev_section is not None and current_section != prev_section:
                y += SECTION_GAP
            positions[nid] = (float(x), float(y))
            y += ROW_SPACING
            prev_section = current_section

    return positions


def apply_auto_layout(model: EditorModel, only_unpositioned: bool = False):
    """Apply auto-layout to the model.

    Args:
        model: The editor model to update.
        only_unpositioned: If True, only position nodes that don't have
            saved positions. If False, reposition all nodes.
    """
    auto_positions = auto_layout(model)

    for node_id, pos in auto_positions.items():
        if only_unpositioned and node_id in model.positions:
            continue
        model.positions[node_id] = pos


def _build_section_order(sections: List[Section]) -> Dict[str, int]:
    """Build a mapping from section name to order index."""
    return {s.name: i for i, s in enumerate(sections)}


def _get_section_name(node_id: str, sections: List[Section]) -> str:
    """Find which section a node belongs to."""
    for section in sections:
        if node_id in section.node_ids:
            return section.name
    return ""


def _sort_key(node_id: str, section_order: Dict[str, int], sections: List[Section]) -> Tuple[int, int]:
    """Sort key for vertical ordering: (section_index, position_in_section)."""
    for section in sections:
        if node_id in section.node_ids:
            return (section_order.get(section.name, 999), section.node_ids.index(node_id))
    return (999, 0)
