"""
SpatialBehavior base class.

Spatial behaviors define how ships position relative to an anchor
(ship, group centroid, or zone). They replace the old ShipFormation
master/follower system with a richer set of positioning strategies.

Each behavior computes a target position for a ship. The AI controller
uses this target position to navigate the ship. The behavior does NOT
control the ship directly — it only says "you should be here."
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from game.core.math import Vector2


class SpatialBehavior(ABC):
    """Abstract base class for spatial positioning behaviors.

    Subclasses implement compute_target_position() which returns
    the desired position for a ship given its context (other ships,
    anchor, slot index).

    The behavior_type class attribute identifies the behavior for
    serialization and registry lookup.
    """

    behavior_type: str = "base"

    @abstractmethod
    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs: Any,
    ) -> Optional['Vector2']:
        """Compute the target position for a ship.

        Args:
            ship: The ship to position.
            group_ships: All ships in the same group (for spacing).
            **kwargs: Behavior-specific parameters:
                - leader: Leader ship (for rigid behaviors)
                - slot_index: Ship's index in the group
                - anchor_position: Vector2 anchor point
                - anchor_ship: Ship to anchor to

        Returns:
            Target position as Vector2, or None if no constraint
            (ship moves freely per its movement policy).
        """
        ...


def apply_separation(
    positions: List[Vector2],
    min_separation: float = 500,
) -> List[Vector2]:
    """Push positions apart so no two are closer than min_separation.

    Uses a single-pass repulsion: for each pair closer than min_separation,
    push them apart along the connecting vector.

    Args:
        positions: List of target positions to adjust.
        min_separation: Minimum distance between any two positions.

    Returns:
        Adjusted positions (new list, originals not mutated).
    """
    if len(positions) <= 1:
        return list(positions)

    result = [Vector2(p.x, p.y) for p in positions]

    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            delta = result[j] - result[i]
            dist = delta.length()

            if dist < min_separation:
                if dist < 0.01:
                    # Coincident — push apart along arbitrary axis
                    delta = Vector2(min_separation * 0.5, 0)
                    dist = delta.length()

                # Push each half the needed distance
                overlap = min_separation - dist
                push = delta.normalize() * (overlap * 0.5)
                result[i] = result[i] - push
                result[j] = result[j] + push

    return result
