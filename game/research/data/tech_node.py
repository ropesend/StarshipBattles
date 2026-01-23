"""
TechNode and TechRequirement data models for the research system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math
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
    price: float = 1.0        # Base RP multiplier (1.0 = normal, 2.0 = 2x RP needed)
    price_curve: str = "flat" # How price scales with level: flat, linear, quadratic, exponential, logarithmic, sqrt
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

    def get_effective_price(self, level: int) -> float:
        """
        Calculate effective RP multiplier for a given level.

        The effective price determines how much RP is needed - higher price means
        RP is divided by this value, making research harder.

        Args:
            level: Target level (1-based, i.e., the level you're trying to reach)

        Returns:
            Effective price multiplier (>= 1.0)
        """
        if self.price_curve == "flat":
            return self.price
        elif self.price_curve == "linear":
            # +50% per level: L1=1.5x, L2=2x, L5=3.5x
            return self.price * (1 + 0.5 * level)
        elif self.price_curve == "quadratic":
            # Slow start, accelerates: L1=1.2x, L2=1.8x, L5=6x
            return self.price * (1 + 0.2 * level * level)
        elif self.price_curve == "exponential":
            # Doubles roughly every 2 levels: L1=1.5x, L2=2.25x, L5=7.6x
            return self.price * (1.5 ** level)
        elif self.price_curve == "logarithmic":
            # Fast early, slows down: L1=1.7x, L2=2.1x, L5=2.8x
            return self.price * (1 + math.log(1 + level))
        elif self.price_curve == "sqrt":
            # Slow growth: L1=2x, L2=2.4x, L5=3.2x
            return self.price * (1 + math.sqrt(level))
        # Default to flat if unknown curve type
        return self.price

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
