"""
Spatial behavior system for fleet combat positioning.

Replaces the old ShipFormation master/follower system with a richer
set of positioning strategies. Each behavior computes target positions
for ships based on their relationship to an anchor.

Behavior types:
    - free_maneuver: No spatial constraints
    - battle_line: Rigid line/wedge/echelon formation
    - column: Rigid single-file following
    - screen: Loose orbit around anchor point
    - escort: Loose close-protection of anchor ship
    - patrol_zone: Loose coverage of an area
"""

import logging
from typing import Any

from game.ai.spatial_behaviors.base import SpatialBehavior
from game.ai.spatial_behaviors.free_maneuver import FreeManeuverBehavior
from game.ai.spatial_behaviors.battle_line import BattleLineBehavior
from game.ai.spatial_behaviors.column import ColumnBehavior
from game.ai.spatial_behaviors.screen import ScreenBehavior
from game.ai.spatial_behaviors.escort import EscortBehavior
from game.ai.spatial_behaviors.patrol_zone import PatrolZoneBehavior

logger = logging.getLogger(__name__)

__all__ = [
    'SpatialBehavior',
    'FreeManeuverBehavior',
    'BattleLineBehavior',
    'ColumnBehavior',
    'ScreenBehavior',
    'EscortBehavior',
    'PatrolZoneBehavior',
    'create_spatial_behavior',
]

_BEHAVIOR_REGISTRY: dict[str, type[SpatialBehavior]] = {
    'free_maneuver': FreeManeuverBehavior,
    'battle_line': BattleLineBehavior,
    'column': ColumnBehavior,
    'screen': ScreenBehavior,
    'escort': EscortBehavior,
    'patrol_zone': PatrolZoneBehavior,
}


def create_spatial_behavior(behavior_type: str, **kwargs: Any) -> SpatialBehavior:
    """Create a spatial behavior instance by type string.

    Args:
        behavior_type: Behavior type identifier (e.g., 'battle_line').
        **kwargs: Behavior-specific constructor parameters.

    Returns:
        SpatialBehavior instance. Defaults to FreeManeuverBehavior
        for unknown types.
    """
    cls = _BEHAVIOR_REGISTRY.get(behavior_type)
    if cls is None:
        logger.warning(f"Unknown spatial behavior type: '{behavior_type}', defaulting to free_maneuver")
        return FreeManeuverBehavior()
    return cls(**kwargs)
