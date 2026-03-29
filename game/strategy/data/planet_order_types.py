"""
Planet order types and order data class.

PROJ-237: Parallel to order_types.py (fleet orders) but for planet-level actions.
Extracted into its own module to avoid import chains (same pattern as PROJ-212).
"""

from enum import Enum, auto
from typing import Any, Dict, Optional


class PlanetOrderType(Enum):
    """Types of orders that can be issued to a planet."""
    ACTIVATE_SHIELD = auto()
    DEACTIVATE_SHIELD = auto()
    # Future: LAUNCH_FIGHTERS, CONVERT_RESOURCES, TOGGLE_COMPONENT


# Action order types processed by PlanetActionEngine (tick-based execution)
PLANET_ACTION_ORDER_TYPES: frozenset = frozenset({
    PlanetOrderType.ACTIVATE_SHIELD,
    PlanetOrderType.DEACTIVATE_SHIELD,
})


class PlanetOrder:
    """
    Represents a single order in a planet's order queue.

    Orders have a type (PlanetOrderType enum) and an optional target
    which varies by order type (typically a dict with facility_instance_id).
    """

    def __init__(self, order_type: PlanetOrderType, target: Any = None):
        self.type = order_type
        self.target = target  # dict with facility_instance_id, component_id, etc.
        self.execution_progress: int = 0  # Ticks spent executing this order

    def __repr__(self) -> str:
        if self.execution_progress > 0:
            return f"PlanetOrder({self.type.name}, progress={self.execution_progress})"
        return f"PlanetOrder({self.type.name})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        result: Dict[str, Any] = {
            'type': self.type.name,
        }
        if self.target is not None:
            result['target'] = self.target
        if self.execution_progress > 0:
            result['execution_progress'] = self.execution_progress
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanetOrder':
        """Deserialize from save game data."""
        order_type = PlanetOrderType[data['type']]
        order = cls(
            order_type=order_type,
            target=data.get('target'),
        )
        order.execution_progress = data.get('execution_progress', 0)
        return order
