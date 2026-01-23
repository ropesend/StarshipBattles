"""
TechNode and TechRequirement data models for the research system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random


@dataclass
class TechRequirement:
    """
    A single AND-condition requirement for a tech node.

    Uses fuzzy level_range that gets resolved to a fixed integer at session start.
    """
    node_id: str
    level_range: Tuple[int, int]  # [min, max] for fuzzy resolution
    resolved_level: Optional[int] = None  # Set at session start

    def resolve(self, rng: random.Random) -> int:
        """
        Resolve fuzzy level_range to a fixed integer for this session.

        Args:
            rng: Seeded random number generator for deterministic resolution

        Returns:
            The resolved level requirement
        """
        self.resolved_level = rng.randint(self.level_range[0], self.level_range[1])
        return self.resolved_level

    def is_met(self, tech_levels: Dict[str, int]) -> bool:
        """
        Check if this requirement is satisfied.

        Args:
            tech_levels: Mapping of node_id -> current_level

        Returns:
            True if the requirement is met
        """
        current = tech_levels.get(self.node_id, 0)
        target = self.resolved_level if self.resolved_level is not None else self.level_range[0]
        return current >= target

    def get_required_level(self) -> int:
        """Get the required level (resolved or minimum of range)."""
        return self.resolved_level if self.resolved_level is not None else self.level_range[0]


@dataclass
class TechNode:
    """
    Represents a single technology in the research tree.

    Requirements are organized as OR-groups of AND-conditions:
    - Outer list: OR groups (any one group satisfied unlocks the tech)
    - Inner list: AND conditions (all conditions in a group must be met)
    """
    id: str
    name: str
    max_levels: int
    requirements: List[List[TechRequirement]] = field(default_factory=list)
    base_decay: float = 0.005  # Default 0.5% decay per turn
    volatility: float = 0.1   # Default volatility coefficient
    comment: Optional[str] = None  # Optional section comment from JSON

    def resolve_requirements(self, rng: random.Random) -> None:
        """
        Resolve all fuzzy requirements using a seeded RNG.

        Args:
            rng: Seeded random number generator
        """
        for or_group in self.requirements:
            for req in or_group:
                req.resolve(rng)

    def get_status(self, current_level: int, tech_levels: Dict[str, int]) -> str:
        """
        Determine the status of this node.

        Args:
            current_level: The current level of this node
            tech_levels: Mapping of node_id -> current_level for all nodes

        Returns:
            'completed' if at max level
            'available' if unlocked and can research
            'locked' if requirements not met
        """
        if current_level >= self.max_levels:
            return 'completed'

        if not self.requirements:
            # No requirements = root node, always available
            return 'available'

        # Check OR-groups: at least one group must have ALL requirements met
        for or_group in self.requirements:
            if all(req.is_met(tech_levels) for req in or_group):
                return 'available'

        return 'locked'

    def get_prerequisite_node_ids(self) -> List[str]:
        """
        Get all prerequisite node IDs (for drawing dependency lines).

        Returns:
            List of unique node IDs that this node depends on
        """
        prereqs = set()
        for or_group in self.requirements:
            for req in or_group:
                prereqs.add(req.node_id)
        return list(prereqs)
