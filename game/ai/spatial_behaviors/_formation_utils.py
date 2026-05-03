"""Shared formation-math helpers for spatial behaviors.

Extracted in PROJ-319 (DUP-X-13) to remove the duplicated circular-positioning
math from `EscortBehavior.compute_target_position` and
`ScreenBehavior.compute_target_position`.
"""
from __future__ import annotations

import math
from typing import Optional

from game.core.math import Vector2


def compute_circular_position(
    anchor_x: float,
    anchor_y: float,
    distance: float,
    slot_index: int,
    total: int,
) -> Optional[Vector2]:
    """Distribute a slot evenly around an anchor at the given radius.

    Args:
        anchor_x, anchor_y: World coordinates of the formation centre.
        distance: Radius of the circle.
        slot_index: This ship's index in the group (0-based).
        total: Total number of slots in the group; treated as `max(1, total)`.

    Returns:
        Vector2 of the slot's target world position. Always non-None — callers
        should perform their own anchor / ability checks before invoking.
    """
    total = max(int(total), 1)
    angle = (2 * math.pi * slot_index) / total
    return Vector2(
        anchor_x + math.cos(angle) * distance,
        anchor_y + math.sin(angle) * distance,
    )
