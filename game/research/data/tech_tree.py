"""
TechTree container class for loading and managing the tech tree structure.
"""
from typing import Dict, List, Optional
import os
import random

from game.core.json_utils import load_json
from game.core.paths import Paths
from game.core.logger import log_info
from .tech_node import TechNode, TechRequirement


class TechTree:
    """
    Container for all tech nodes with loading and layout utilities.

    Handles:
    - Loading from JSON file
    - Fuzzy requirement resolution
    - Depth calculation for left-to-right layout
    """

    def __init__(self):
        self.nodes: Dict[str, TechNode] = {}
        self._depth_cache: Dict[str, int] = {}

    @classmethod
    def load_from_json(cls, file_path: str = None) -> 'TechTree':
        """
        Load tech tree from JSON file.

        Args:
            file_path: Path to JSON file. Defaults to data/techtree.json

        Returns:
            Populated TechTree instance
        """
        if file_path is None:
            file_path = os.path.join(Paths.DATA_DIR, "techtree.json")

        tree = cls()
        data = load_json(file_path, default={"tech_tree": []})

        loaded_count = 0
        skipped_count = 0

        for node_data in data.get("tech_tree", []):
            # Skip comment-only entries (have 'comment' but no 'id')
            if "comment" in node_data and "id" not in node_data:
                skipped_count += 1
                continue

            # Skip entries without required fields
            if "id" not in node_data or "name" not in node_data:
                skipped_count += 1
                continue

            # Parse requirements
            requirements = []
            for or_group in node_data.get("requirements", []):
                and_conditions = []
                for req in or_group:
                    # Use level_range format; default to (1, 1) if missing
                    level_range = tuple(req.get("level_range", (1, 1)))

                    and_conditions.append(TechRequirement(
                        node_id=req["node_id"],
                        level_range=level_range,
                        negate=req.get("negate", False)
                    ))
                if and_conditions:
                    requirements.append(and_conditions)

            node = TechNode(
                id=node_data["id"],
                name=node_data["name"],
                max_levels=node_data.get("max_levels", 1),
                requirements=requirements,
                base_decay=node_data.get("base_decay", 0.005),
                volatility=node_data.get("volatility", 0.1),
                price=node_data.get("price", 1.0),
                price_curve=node_data.get("price_curve", "flat"),
                comment=node_data.get("comment")
            )
            tree.nodes[node.id] = node
            loaded_count += 1

        log_info(f"TechTree: Loaded {loaded_count} nodes from {file_path}")
        if skipped_count > 0:
            log_info(f"TechTree: Skipped {skipped_count} comment/invalid entries")

        return tree

    def resolve_all_requirements(self, seed: int) -> None:
        """
        Resolve all fuzzy requirements using a seeded RNG.

        This should be called once at session start to lock in
        the specific level requirements for each dependency.

        Args:
            seed: Random seed for deterministic resolution
        """
        rng = random.Random(seed)
        for node in self.nodes.values():
            node.resolve_requirements(rng)
        log_info(f"TechTree: Resolved fuzzy requirements with seed {seed}")

    def calculate_depth(self, node_id: str) -> int:
        """
        Calculate dependency depth for layout (left-to-right positioning).

        Depth 0 = root nodes (no requirements)
        Depth N = max(prereq depths) + 1

        Args:
            node_id: ID of the node to calculate depth for

        Returns:
            Depth level (0 for root nodes)
        """
        if node_id in self._depth_cache:
            return self._depth_cache[node_id]

        node = self.nodes.get(node_id)
        if not node:
            self._depth_cache[node_id] = 0
            return 0

        if not node.requirements:
            # Root node - no requirements
            self._depth_cache[node_id] = 0
            return 0

        # Find max depth among all prerequisites
        max_dep_depth = 0
        for or_group in node.requirements:
            for req in or_group:
                if req.node_id in self.nodes:
                    dep_depth = self.calculate_depth(req.node_id)
                    max_dep_depth = max(max_dep_depth, dep_depth)

        self._depth_cache[node_id] = max_dep_depth + 1
        return max_dep_depth + 1

    def get_nodes_at_depth(self, depth: int) -> List[TechNode]:
        """
        Get all nodes at a specific depth level.

        Args:
            depth: The depth level to query

        Returns:
            List of TechNode objects at that depth
        """
        return [n for n in self.nodes.values() if self.calculate_depth(n.id) == depth]

    def get_max_depth(self) -> int:
        """
        Get the maximum depth in the tree.

        Returns:
            Maximum depth level, or 0 if empty
        """
        if not self.nodes:
            return 0
        return max(self.calculate_depth(n.id) for n in self.nodes.values())

    def get_node(self, node_id: str) -> Optional[TechNode]:
        """
        Get a node by ID.

        Args:
            node_id: The node ID to look up

        Returns:
            TechNode if found, None otherwise
        """
        return self.nodes.get(node_id)

    def get_all_node_ids(self) -> List[str]:
        """
        Get all node IDs in the tree.

        Returns:
            List of node IDs
        """
        return list(self.nodes.keys())

    def validate_requirements(self) -> List[str]:
        """
        Validate that all requirement references point to existing nodes.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        for node in self.nodes.values():
            for or_group in node.requirements:
                for req in or_group:
                    if req.node_id not in self.nodes:
                        errors.append(
                            f"Node '{node.id}' references unknown node '{req.node_id}'"
                        )
        return errors

    def detect_cycles(self) -> List[str]:
        """
        Detect circular dependencies in the tech tree.

        Uses DFS with recursion stack to find cycles.
        Only follows positive (non-negated) dependencies since
        negative requirements don't create true dependencies.

        Returns:
            List of error messages describing cycles found
        """
        errors = []
        visited = set()
        rec_stack = set()  # Nodes in current recursion path

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in rec_stack:
                # Found a cycle - extract the cycle portion
                cycle_start = path.index(node_id)
                cycle = " -> ".join(path[cycle_start:] + [node_id])
                errors.append(f"Cycle detected: {cycle}")
                return
            if node_id in visited:
                return

            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for or_group in node.requirements:
                    for req in or_group:
                        # Only follow positive dependencies (not negated)
                        if not req.negate and req.node_id in self.nodes:
                            dfs(req.node_id, path)

            path.pop()
            rec_stack.remove(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return errors

    def validate(self) -> List[str]:
        """
        Run all validations (missing refs + cycles).

        Returns:
            List of all error messages (empty if valid)
        """
        errors = self.validate_requirements()
        errors.extend(self.detect_cycles())
        return errors
