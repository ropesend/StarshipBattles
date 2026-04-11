"""FreeManeuver — no spatial constraints.

Ship moves purely according to its movement policy with no
positional obligations to a group or anchor.
"""

from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior


class FreeManeuverBehavior(SpatialBehavior):
    """No spatial constraints — ship maneuvers independently."""

    behavior_type = "free_maneuver"

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs,
    ) -> Optional[Vector2]:
        """Returns None — no positional constraint."""
        return None
