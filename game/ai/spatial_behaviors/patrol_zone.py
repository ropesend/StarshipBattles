"""PatrolZone — ships move within a defined area.

Loose behavior: ships distribute within a circular zone,
covering the area by positioning at evenly-spaced points.
"""

import math
from typing import Any, List, Optional

from game.core.math import Vector2
from game.ai.spatial_behaviors.base import SpatialBehavior


class PatrolZoneBehavior(SpatialBehavior):
    """Ships distribute within a circular patrol zone.

    Args:
        zone_center: Center of the patrol zone.
        zone_radius: Radius of the patrol zone.
    """

    behavior_type = "patrol_zone"

    def __init__(
        self,
        zone_center: Optional[Vector2] = None,
        zone_radius: float = 5000,
    ):
        self.zone_center = zone_center or Vector2(0, 0)
        self.zone_radius = zone_radius

    def compute_target_position(
        self,
        ship: Any,
        group_ships: List[Any],
        **kwargs,
    ) -> Optional[Vector2]:
        """Compute position within the patrol zone.

        Ships distribute at fraction of the zone radius on evenly
        spaced angles to cover the zone.

        Required kwargs:
            slot_index: This ship's index in the patrol group.
        """
        slot_index = kwargs.get("slot_index", 0)

        total = max(len(group_ships), 1)

        # Distribute at ~70% of zone radius on evenly spaced angles
        patrol_radius = self.zone_radius * 0.7
        angle = (2 * math.pi * slot_index) / total

        target_x = self.zone_center.x + math.cos(angle) * patrol_radius
        target_y = self.zone_center.y + math.sin(angle) * patrol_radius

        return Vector2(target_x, target_y)
