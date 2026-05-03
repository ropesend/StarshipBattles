"""Escort — ships stay close to a specific ship.

Loose behavior: ships position near an anchor ship, spreading
evenly around it at a configured distance.
"""

from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior
from game.ai.spatial_behaviors._formation_utils import compute_circular_position


class EscortBehavior(SpatialBehavior):
    """Ships stay close to an anchor ship.

    Args:
        distance: Distance from anchor ship to maintain.
    """

    behavior_type = "escort"

    def __init__(self, distance: float = 1000):
        self.distance = distance

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs,
    ) -> Optional[Vector2]:
        """Compute position near the anchor ship.

        Required kwargs:
            anchor_ship: The ship to escort.
            slot_index: This ship's index in the escort group.
        """
        anchor_ship = kwargs.get("anchor_ship")
        slot_index = kwargs.get("slot_index", 0)

        if anchor_ship is None:
            return None

        return compute_circular_position(
            anchor_ship.position.x,
            anchor_ship.position.y,
            self.distance,
            slot_index,
            len(group_ships),
        )
