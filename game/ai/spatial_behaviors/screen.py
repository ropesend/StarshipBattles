"""Screen — ships orbit/patrol around an anchor point.

Loose behavior: ships distribute evenly around the anchor at a
configured radius, maintaining spread to avoid clumping.
"""

from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior
from game.ai.spatial_behaviors._formation_utils import compute_circular_position


class ScreenBehavior(SpatialBehavior):
    """Ships distribute evenly around an anchor point.

    Args:
        radius: Distance from anchor to maintain.
        reactivity: How to respond to threats — 'passive', 'active',
                    or 'aggressive'. Default 'passive'.
    """

    behavior_type = "screen"

    def __init__(
        self,
        radius: float = 2000,
        reactivity: str = "passive",
    ):
        self.radius = radius
        self.reactivity = reactivity

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs: Any,
    ) -> Optional[Vector2]:
        """Compute position on the screen circle around anchor.

        Required kwargs:
            anchor_position: Vector2 center of the screen.
            slot_index: This ship's index in the screen formation.
        """
        anchor_position = kwargs.get("anchor_position")
        slot_index = kwargs.get("slot_index", 0)

        if anchor_position is None:
            return None

        return compute_circular_position(
            anchor_position.x,
            anchor_position.y,
            self.radius,
            slot_index,
            len(group_ships),
        )
