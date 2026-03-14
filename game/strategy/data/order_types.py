"""
Fleet order types and order data class.

Extracted from fleet.py (PROJ-212) to break transitive import chains.
Files needing only OrderType/FleetOrder no longer pull in the heavyweight
Fleet class and its dependencies.
"""

from enum import Enum, auto
from typing import Any, Dict, TYPE_CHECKING

from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet


class OrderType(Enum):
    MOVE = auto()
    WARP = auto()  # PROJ-187: Explicit warp point traversal
    COLONIZE = auto()
    MOVE_TO_FLEET = auto()
    JOIN_FLEET = auto()
    BUILD = auto()
    TRANSFER = auto()
    # Superweapon orders (PROJ-102)
    IMPLODE_PLANET = auto()
    STELLERATE_STAR = auto()
    OPEN_WARP_POINT = auto()
    CLOSE_WARP_POINT = auto()
    CREATE_DYSON_SPHERE = auto()
    SELF_DESTRUCT = auto()
    LOAD_POPULATION = auto()
    UNLOAD_POPULATION = auto()


# PROJ-187: Order type categorization for ActionExecutionEngine
# Movement orders are handled by FleetMovementEngine
MOVEMENT_ORDER_TYPES: frozenset = frozenset({
    OrderType.MOVE,
    OrderType.MOVE_TO_FLEET,
    OrderType.WARP,
})

# Action orders are handled by ActionExecutionEngine (tick-based execution)
# Excludes BUILD (persistent, handled by ProductionEngine)
# PROJ-207: JOIN_FLEET removed - handled by instant path (process_instant_orders) only
ACTION_ORDER_TYPES: frozenset = frozenset({
    OrderType.COLONIZE,
    OrderType.TRANSFER,
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
    OrderType.IMPLODE_PLANET,
    OrderType.STELLERATE_STAR,
    OrderType.OPEN_WARP_POINT,
    OrderType.CLOSE_WARP_POINT,
    OrderType.CREATE_DYSON_SPHERE,
    OrderType.SELF_DESTRUCT,
})


class FleetOrder:
    """
    Represents a single order in a fleet's order queue.

    Orders have a type (OrderType enum) and an optional target which varies
    by order type (HexCoord for movement, Planet for colonize, etc.).
    """

    def __init__(self, order_type: OrderType, target: Any = None):
        self.type = order_type
        self.target = target  # HexCoord for MOVE/WARP, Planet for COLONIZE, Fleet for MOVE_TO_FLEET/JOIN_FLEET
        self.execution_progress: int = 0  # PROJ-187: Ticks spent executing this order

    def __repr__(self) -> str:
        if self.execution_progress > 0:
            return f"FleetOrder({self.type.name}, {self.target}, progress={self.execution_progress})"
        return f"FleetOrder({self.type.name}, {self.target})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        # Import at runtime to avoid circular import with Fleet/Planet
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.planet import Planet

        target_data = None
        if self.target is not None:
            if self.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
                # TRANSFER and population orders store a dict with direction, cargo_type, amount, planet_id
                target_data = {'type': 'transfer', 'value': self.target}
            elif self.type == OrderType.IMPLODE_PLANET and isinstance(self.target, Planet):
                # Planet reference for IMPLODE_PLANET (PROJ-102)
                target_data = {'type': 'planet_ref', 'id': self.target.id}
            elif self.type == OrderType.SELF_DESTRUCT and isinstance(self.target, list):
                # Ship ID list for SELF_DESTRUCT (PROJ-102)
                target_data = {'type': 'ship_id_list', 'value': self.target}
            elif self.type in (OrderType.OPEN_WARP_POINT, OrderType.CLOSE_WARP_POINT) and isinstance(self.target, dict):
                # Warp parameters for OPEN/CLOSE_WARP_POINT (PROJ-102)
                target_data = {'type': 'warp_params', 'value': self.target}
            elif isinstance(self.target, HexCoord):
                # HexCoord for MOVE, WARP targets
                target_data = {'q': self.target.q, 'r': self.target.r}
            elif isinstance(self.target, Planet):
                # Planet reference for COLONIZE etc. (PROJ-207: use planet_ref instead of full dict)
                target_data = {'type': 'planet_ref', 'id': self.target.id}
            elif isinstance(self.target, Fleet):
                # Fleet reference - store ID
                target_data = {'type': 'fleet_ref', 'id': self.target.id}
            else:
                target_data = {'type': 'raw', 'value': str(self.target)}

        result = {
            'type': self.type.name,
            'target': target_data,
        }
        # PROJ-187: Only serialize execution_progress when > 0 (keeps saves clean)
        if self.execution_progress > 0:
            result['execution_progress'] = self.execution_progress
        return result
