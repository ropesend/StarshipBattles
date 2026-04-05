"""
Order types and order data class.

Extracted from fleet.py (PROJ-212) to break transitive import chains.
PROJ-238: Renamed FleetOrder -> Order. Unified with PlanetOrderType.
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
    # Planet orders — generic ability toggle
    ACTIVATE_ABILITY = auto()
    DEACTIVATE_ABILITY = auto()


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
    OrderType.ACTIVATE_ABILITY,
    OrderType.DEACTIVATE_ABILITY,
})

# Planet-specific action orders (subset of ACTION_ORDER_TYPES)
PLANET_ACTION_ORDER_TYPES: frozenset = frozenset({
    OrderType.ACTIVATE_ABILITY,
    OrderType.DEACTIVATE_ABILITY,
})


class Order:
    """
    Represents a single order in an entity's order queue.

    PROJ-238: Renamed from FleetOrder. Used by both fleets and planets.
    Orders have a type (OrderType enum) and an optional target which varies
    by order type (HexCoord for movement, Planet for colonize, dict for planet orders, etc.).
    """

    def __init__(self, order_type: OrderType, target: Any = None):
        self.type = order_type
        self.target = target  # HexCoord for MOVE/WARP, Planet for COLONIZE, dict for planet orders, etc.
        self.execution_progress: int = 0  # PROJ-187: Ticks spent executing this order

    def __repr__(self) -> str:
        if self.execution_progress > 0:
            return f"Order({self.type.name}, {self.target}, progress={self.execution_progress})"
        return f"Order({self.type.name}, {self.target})"

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
            elif isinstance(self.target, dict) and self.type == OrderType.COLONIZE:
                # COLONIZE with population/cargo amounts — serialize planet ref + amounts
                planet_obj = self.target.get('planet')
                target_data = {
                    'type': 'colonize_params',
                    'planet_id': planet_obj.id if planet_obj else None,
                    'population': self.target.get('population'),
                    'cargo': self.target.get('cargo'),
                }
            elif isinstance(self.target, dict):
                # PROJ-238: Dict targets (planet orders, etc.) — store as-is
                target_data = {'type': 'dict', 'value': self.target}
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


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Deserialize from save game data (simple format for planet-style orders).

        PROJ-238: Added for planet order compatibility. Fleet orders use
        FleetOrderSerializer for complex reference resolution.

        Args:
            data: Dict with 'type', optional 'target', optional 'execution_progress'.

        Returns:
            Reconstructed Order instance.
        """
        order_type = OrderType[data['type']]
        target = data.get('target')
        # Unwrap dict-wrapped targets from to_dict serialization
        if isinstance(target, dict) and target.get('type') == 'dict':
            target = target.get('value')
        order = cls(order_type=order_type, target=target)
        order.execution_progress = data.get('execution_progress', 0)
        return order


# PROJ-238: Backward compatibility aliases (will be removed after full migration)
FleetOrder = Order
PlanetOrder = Order
