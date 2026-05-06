"""BattleLine — ships hold positions in a line perpendicular to facing.

Rigid behavior: ships maintain assigned positions relative to a leader.
Supports shapes: line, wedge, echelon_left, echelon_right, wall.
"""

import math
from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior


class BattleLineBehavior(SpatialBehavior):
    """Ships hold positions in a structured formation.

    The leader defines the formation center and facing. Other ships
    are assigned slots offset perpendicular to the leader's facing.

    Args:
        spacing: Distance between adjacent ships in the line.
        shape: Formation shape ('line', 'wedge', 'echelon_left',
               'echelon_right', 'wall'). Default 'line'.
    """

    behavior_type = "battle_line"

    def __init__(self, spacing: float = 2000, shape: str = "line"):
        self.spacing = spacing
        self.shape = shape

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs,
    ) -> Optional[Vector2]:
        """Compute slot position in the battle line.

        Required kwargs:
            leader: The formation leader ship.
            slot_index: This ship's index in the formation (0-based).
        """
        leader = kwargs.get("leader")
        slot_index = kwargs.get("slot_index", 0)

        if leader is None:
            return None

        total = len(group_ships)
        if total == 0:
            total = 1

        # Compute offset from center for this slot
        # Center the line: slot 0 at one end, last slot at other
        center_offset = (slot_index - (total - 1) / 2.0) * self.spacing

        # Leader's facing angle (0 = right, 90 = down in screen coords)
        angle_rad = math.radians(leader.angle)

        # Perpendicular direction (90 degrees from facing)
        perp_x = -math.sin(angle_rad)
        perp_y = math.cos(angle_rad)

        # Forward direction (along facing) — used for wedge/echelon
        fwd_x = math.cos(angle_rad)
        fwd_y = math.sin(angle_rad)

        # Base position: leader position + perpendicular offset
        target_x = leader.position.x + perp_x * center_offset
        target_y = leader.position.y + perp_y * center_offset

        # Shape adjustments
        if self.shape == "wedge":
            # V-shape: ships further from center are further back
            setback = abs(center_offset) * 0.5
            target_x -= fwd_x * setback
            target_y -= fwd_y * setback

        elif self.shape == "wall":
            # Stagger alternating slots into a second rank.
            setback = (slot_index % 2) * self.spacing * 0.5
            target_x -= fwd_x * setback
            target_y -= fwd_y * setback

        elif self.shape == "echelon_left":
            # Diagonal offset backward-left
            setback = slot_index * self.spacing * 0.3
            target_x -= fwd_x * setback
            target_y -= fwd_y * setback

        elif self.shape == "echelon_right":
            # Diagonal offset backward-right
            setback = (total - 1 - slot_index) * self.spacing * 0.3
            target_x -= fwd_x * setback
            target_y -= fwd_y * setback

        return Vector2(target_x, target_y)
