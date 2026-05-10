"""
EditorModel — wraps the game's TechTree with editor-specific state.

Manages node positions, section grouping, node ordering, and dirty tracking.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.tech_tree import TechTree

from .persistence import load_node_order_from_json, save_tech_tree


# Valid price curve options
PRICE_CURVES = ("flat", "linear", "quadratic", "exponential", "logarithmic", "sqrt")


@dataclass
class Section:
    """A named group of tech nodes (derived from comment headers)."""
    name: str
    node_ids: List[str] = field(default_factory=list)


class EditorModel:
    """Central model for the tech tree editor.

    Wraps TechTree with:
    - Node positions for visual layout
    - Section grouping for branch management
    - Node ordering for JSON serialization
    - Dirty flag for unsaved changes tracking
    """

    def __init__(self):
        self.tech_tree: TechTree = TechTree()
        self.node_order: List[str] = []
        self.sections: List[Section] = []
        self.positions: Dict[str, Tuple[float, float]] = {}
        self.file_path: Optional[str] = None
        self.layout_path: Optional[str] = None
        self._dirty: bool = False

    @property
    def dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    @property
    def nodes(self) -> Dict[str, TechNode]:
        return self.tech_tree.nodes

    # ── Loading ──────────────────────────────────────────────────────

    def load(self, file_path: str) -> List[str]:
        """Load a tech tree from JSON.

        Args:
            file_path: Path to techtree.json

        Returns:
            List of validation errors (empty if valid).
        """
        self.file_path = file_path
        self.layout_path = self._derive_layout_path(file_path)

        # Load tree structure (uses game's loader)
        self.tech_tree = TechTree.load_from_json(file_path)

        # Load node ordering from file (for round-trip fidelity)
        self.node_order = load_node_order_from_json(file_path)

        # Derive sections from comment fields
        self.sections = self._derive_sections()

        # Load positions from sidecar file (or empty)
        self.positions = self._load_positions()

        self._dirty = False
        return self.tech_tree.validate()

    def _derive_layout_path(self, file_path: str) -> str:
        """Derive the layout sidecar file path from the data file path."""
        base, _ = os.path.splitext(file_path)
        return base + "_layout.json"

    def _derive_sections(self) -> List[Section]:
        """Derive sections from node comment fields and ordering."""
        sections: List[Section] = []
        current_section = Section(name="Unsorted")

        for nid in self.node_order:
            node = self.tech_tree.nodes.get(nid)
            if not node:
                continue
            if node.comment:
                # Start a new section
                current_section = Section(name=node.comment)
                sections.append(current_section)
                current_section.node_ids.append(nid)
            else:
                if not sections:
                    sections.append(current_section)
                current_section.node_ids.append(nid)

        # Ensure all nodes are in a section (catch any missed)
        assigned = {nid for s in sections for nid in s.node_ids}
        unassigned = [nid for nid in self.node_order if nid not in assigned]
        if unassigned:
            unsorted = Section(name="Unsorted", node_ids=unassigned)
            sections.append(unsorted)

        return sections

    # ── Positions ────────────────────────────────────────────────────

    def _load_positions(self) -> Dict[str, Tuple[float, float]]:
        """Load positions from sidecar layout file."""
        if not self.layout_path or not os.path.exists(self.layout_path):
            return {}
        try:
            with open(self.layout_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                k: (v[0], v[1])
                for k, v in data.get("positions", {}).items()
                if isinstance(v, list) and len(v) >= 2
            }
        except (OSError, json.JSONDecodeError):
            return {}

    def save_positions(self) -> bool:
        """Save positions to sidecar layout file."""
        if not self.layout_path:
            return False
        data = {
            "version": 1,
            "positions": {k: list(v) for k, v in self.positions.items()},
        }
        try:
            with open(self.layout_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
            return True
        except OSError:
            return False

    def get_position(self, node_id: str) -> Tuple[float, float]:
        """Get position for a node (defaults to 0,0 if unset)."""
        return self.positions.get(node_id, (0.0, 0.0))

    def set_position(self, node_id: str, x: float, y: float):
        """Set position for a node."""
        self.positions[node_id] = (x, y)

    # ── Saving ───────────────────────────────────────────────────────

    def save(self, file_path: Optional[str] = None) -> bool:
        """Save the tech tree to JSON.

        Args:
            file_path: Optional override path. Uses loaded path if None.

        Returns:
            True on success.
        """
        path = file_path or self.file_path
        if not path:
            return False

        # Rebuild node_order from sections to preserve grouping
        self.node_order = self._rebuild_node_order()

        # Sync section comments onto nodes
        self._sync_section_comments()

        success = save_tech_tree(path, self.node_order, self.tech_tree.nodes)
        if success:
            if file_path:
                self.file_path = file_path
                self.layout_path = self._derive_layout_path(file_path)
            self.save_positions()
            self._dirty = False
        return success

    def _rebuild_node_order(self) -> List[str]:
        """Rebuild node_order from current sections."""
        order = []
        for section in self.sections:
            for nid in section.node_ids:
                if nid in self.tech_tree.nodes:
                    order.append(nid)

        # Add any nodes not in any section
        in_sections = set(order)
        for nid in self.tech_tree.nodes:
            if nid not in in_sections:
                order.append(nid)

        return order

    def _sync_section_comments(self):
        """Update node comment fields to match section assignments."""
        # Clear all comments first
        for node in self.tech_tree.nodes.values():
            node.comment = None

        # Set comment on first node of each section
        for section in self.sections:
            if section.node_ids and section.name != "Unsorted":
                first_nid = section.node_ids[0]
                node = self.tech_tree.nodes.get(first_nid)
                if node:
                    node.comment = section.name

    # ── Node CRUD ────────────────────────────────────────────────────

    def add_node(self, node: TechNode, section_name: Optional[str] = None) -> None:
        """Add a new node to the tree."""
        self.tech_tree.nodes[node.id] = node
        self.node_order.append(node.id)

        # Add to appropriate section
        placed = False
        if section_name:
            for section in self.sections:
                if section.name == section_name:
                    section.node_ids.append(node.id)
                    placed = True
                    break

        if not placed:
            # Add to last section or create Unsorted
            if self.sections:
                self.sections[-1].node_ids.append(node.id)
            else:
                self.sections.append(Section(name="Unsorted", node_ids=[node.id]))

        self._dirty = True

    def remove_node(self, node_id: str) -> Optional[TechNode]:
        """Remove a node from the tree. Returns the removed node or None."""
        node = self.tech_tree.nodes.pop(node_id, None)
        if node is None:
            return None

        if node_id in self.node_order:
            self.node_order.remove(node_id)
        self.positions.pop(node_id, None)

        for section in self.sections:
            if node_id in section.node_ids:
                section.node_ids.remove(node_id)
                break

        # Remove any requirements that reference this node
        for other_node in self.tech_tree.nodes.values():
            other_node.requirements = [
                [req for req in or_group if req.node_id != node_id]
                for or_group in other_node.requirements
            ]
            # Clean up empty OR-groups
            other_node.requirements = [
                og for og in other_node.requirements if og
            ]

        # Clear depth cache since topology changed
        self.tech_tree._depth_cache.clear()
        self._dirty = True
        return node

    # ── Requirement CRUD ─────────────────────────────────────────────

    def add_requirement(
        self,
        target_node_id: str,
        prereq_node_id: str,
        level_range: Tuple[int, int] = (1, 1),
        negate: bool = False,
        or_group_index: int = 0,
    ) -> bool:
        """Add a requirement to a node.

        Args:
            target_node_id: The node that gains the requirement.
            prereq_node_id: The prerequisite node.
            level_range: Fuzzy level range [min, max].
            negate: Whether this is a negated (mutually exclusive) requirement.
            or_group_index: Which OR-group to add to (0-based). Creates if needed.

        Returns:
            True on success.
        """
        node = self.tech_tree.nodes.get(target_node_id)
        if not node or prereq_node_id not in self.tech_tree.nodes:
            return False

        req = TechRequirement(
            node_id=prereq_node_id,
            level_range=level_range,
            negate=negate,
        )

        # Extend OR-groups if needed
        while len(node.requirements) <= or_group_index:
            node.requirements.append([])

        node.requirements[or_group_index].append(req)
        self.tech_tree._depth_cache.clear()
        self._dirty = True
        return True

    def remove_requirement(
        self,
        target_node_id: str,
        prereq_node_id: str,
        or_group_index: int = 0,
    ) -> Optional[TechRequirement]:
        """Remove a requirement from a node.

        Removes the first matching requirement in the given OR-group.

        Returns:
            The removed TechRequirement, or None if not found.
        """
        node = self.tech_tree.nodes.get(target_node_id)
        if not node or or_group_index >= len(node.requirements):
            return None

        or_group = node.requirements[or_group_index]
        for i, req in enumerate(or_group):
            if req.node_id == prereq_node_id:
                removed = or_group.pop(i)
                # Clean up empty OR-groups
                if not or_group:
                    node.requirements.pop(or_group_index)
                self.tech_tree._depth_cache.clear()
                self._dirty = True
                return removed
        return None

    def add_or_group(self, node_id: str) -> int:
        """Add a new empty OR-group to a node. Returns the new group index."""
        node = self.tech_tree.nodes.get(node_id)
        if not node:
            return -1
        node.requirements.append([])
        self._dirty = True
        return len(node.requirements) - 1

    def remove_or_group(self, node_id: str, or_group_index: int) -> List[TechRequirement]:
        """Remove an OR-group from a node. Returns the removed requirements."""
        node = self.tech_tree.nodes.get(node_id)
        if not node or or_group_index >= len(node.requirements):
            return []
        removed = node.requirements.pop(or_group_index)
        self.tech_tree._depth_cache.clear()
        self._dirty = True
        return removed

    # ── Section Management ───────────────────────────────────────────

    def get_section_for_node(self, node_id: str) -> Optional[Section]:
        """Find which section a node belongs to."""
        for section in self.sections:
            if node_id in section.node_ids:
                return section
        return None

    def move_node_to_section(self, node_id: str, target_section_name: str) -> bool:
        """Move a node from its current section to another."""
        # Remove from current section
        for section in self.sections:
            if node_id in section.node_ids:
                section.node_ids.remove(node_id)
                break

        # Add to target section
        for section in self.sections:
            if section.name == target_section_name:
                section.node_ids.append(node_id)
                self._dirty = True
                return True
        return False

    def create_section(self, name: str) -> Section:
        """Create a new empty section."""
        section = Section(name=name)
        self.sections.append(section)
        self._dirty = True
        return section

    def rename_section(self, old_name: str, new_name: str) -> bool:
        """Rename a section."""
        for section in self.sections:
            if section.name == old_name:
                section.name = new_name
                self._dirty = True
                return True
        return False

    # ── Validation ───────────────────────────────────────────────────

    def validate(self) -> List[str]:
        """Run all validations on the current tree state."""
        errors = self.tech_tree.validate()

        # Check for duplicate IDs (shouldn't happen with dict, but check order list)
        seen = set()
        for nid in self.node_order:
            if nid in seen:
                errors.append(f"Duplicate node ID in ordering: '{nid}'")
            seen.add(nid)

        # Check for orphan nodes (no parents, no children, not a root)
        all_prereq_ids = set()
        all_dependent_ids = set()
        for node in self.tech_tree.nodes.values():
            if node.requirements:
                all_dependent_ids.add(node.id)
            for og in node.requirements:
                for req in og:
                    all_prereq_ids.add(req.node_id)

        for nid, node in self.tech_tree.nodes.items():
            if nid not in all_prereq_ids and nid not in all_dependent_ids:
                if node.requirements:  # Has reqs but nobody depends on it and it depends on nothing valid
                    errors.append(f"Orphan node: '{nid}' ({node.name}) has no connections")

        return errors

    # ── Utility ──────────────────────────────────────────────────────

    def get_next_id(self, prefix: str) -> str:
        """Generate the next available ID with the given prefix."""
        existing_nums = []
        for nid in self.tech_tree.nodes:
            if nid.startswith(prefix):
                suffix = nid[len(prefix):]
                try:
                    existing_nums.append(int(suffix))
                except ValueError:
                    pass
        next_num = max(existing_nums, default=0) + 1
        return f"{prefix}{next_num}"

    def get_section_names(self) -> List[str]:
        """Get all section names in order."""
        return [s.name for s in self.sections]

    def get_all_links(self) -> List[Dict[str, Any]]:
        """Get all requirement links for rendering.

        Returns list of dicts with keys:
            source_id, target_id, or_group_index, req_index,
            level_range, negate
        """
        links = []
        for node in self.tech_tree.nodes.values():
            for og_idx, or_group in enumerate(node.requirements):
                for req_idx, req in enumerate(or_group):
                    links.append({
                        "source_id": req.node_id,
                        "target_id": node.id,
                        "or_group_index": og_idx,
                        "req_index": req_idx,
                        "level_range": req.level_range,
                        "negate": req.negate,
                    })
        return links
