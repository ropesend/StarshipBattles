"""Column — ships follow leader in single file.

Rigid behavior: ships trail behind the leader along its
facing direction at regular intervals.
"""

import math
from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior


class ColumnBehavior(SpatialBehavior):
    """Ships follow a leader in single file.

    Args:
        follow_distance: Distance between ships in the column.
    """

    behavior_type = "column"

    def __init__(self, follow_distance: float = 1500):
        self.follow_distance = follow_distance

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs: Any,
    ) -> Optional[Vector2]:
        """Compute position behind the leader in column.

        Required kwargs:
            leader: The column leader ship.
            slot_index: This ship's index (0 = closest to leader).
        """
        leader = kwargs.get("leader")
        slot_index = kwargs.get("slot_index", 0)

        if leader is None:
            return None

        # Position behind the leader along its facing direction
        angle_rad = math.radians(leader.angle)
        fwd_x = math.cos(angle_rad)
        fwd_y = math.sin(angle_rad)

        # Each slot is further behind (negative forward direction)
        offset = (slot_index + 1) * self.follow_distance

        target_x = leader.position.x - fwd_x * offset
        target_y = leader.position.y - fwd_y * offset

        return Vector2(target_x, target_y)
