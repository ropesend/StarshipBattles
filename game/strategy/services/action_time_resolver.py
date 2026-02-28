"""
ActionTimeResolver - Resolves action_time for tick-based order execution.

PROJ-187: Strategy Orders Tick-Based Action System

This service looks up the action_time for a given order by finding the
relevant ability on the fleet's ships. Each strategic action (COLONIZE,
superweapons, etc.) has an action_time that determines how many ticks
it takes to complete.

Action times are defined on component abilities in components.json:
- ColonizePlanet: {"planet_type": "CONTINENTAL", "action_time": 2}
- DestroyPlanet: {"action_time": 3}
- DestroyStar: {"action_time": 5}
etc.
"""
from typing import TYPE_CHECKING, Any, Dict, Optional

from game.strategy.services.component_inspector import (
    iterate_design_components,
    get_component_abilities,
)
from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.order_types import FleetOrder


# PROJ-212: Module-level constants replacing wrapper functions
# Mapping from OrderType to the ability name that provides action_time
ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = {
    OrderType.COLONIZE: 'ColonizePlanet',
    OrderType.IMPLODE_PLANET: 'DestroyPlanet',
    OrderType.STELLERATE_STAR: 'DestroyStar',
    OrderType.OPEN_WARP_POINT: 'OpenWarpPoint',
    OrderType.CLOSE_WARP_POINT: 'CloseWarpPoint',
    OrderType.CREATE_DYSON_SPHERE: 'CreateDysonSphere',
    OrderType.SELF_DESTRUCT: 'SelfDestruct',
}

# Order types that are handled by movement engine, not action engine
MOVEMENT_ORDER_TYPES: frozenset = frozenset({OrderType.MOVE, OrderType.MOVE_TO_FLEET})


class ActionTimeResolver:
    """Resolves action_time for tick-based order execution.

    Looks up the action_time from the relevant ability on a fleet's ships.
    Falls back to default values when abilities aren't found or don't
    specify action_time.
    """

    @staticmethod
    def resolve_action_time(
        fleet: 'Fleet',
        order: 'FleetOrder',
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Resolve the action_time for a given order.

        For orders with ability-based action times (COLONIZE, superweapons),
        finds the first ship with the relevant ability and returns its
        action_time value.

        Args:
            fleet: The Fleet executing the order
            order: The FleetOrder being executed
            component_registry: Optional component registry for ability lookup.
                               If None, uses inline abilities from design_data.

        Returns:
            Integer action_time (ticks required to complete the action):
            - Movement orders (MOVE): 0 (handled by movement engine)
            - Ability-based orders: action_time from ability, or 1 if not specified
            - Other orders (TRANSFER, JOIN_FLEET, etc.): 1 (default)
        """
        # Movement orders are handled by movement engine, not action engine
        if order.type in MOVEMENT_ORDER_TYPES:
            return 0

        # Get the ability name for this order type
        ability_name = ORDER_TO_ABILITY_MAP.get(order.type)

        if ability_name is None:
            # Default action time for orders without ability lookup
            return 1

        # Find the ability on the fleet's ships
        action_time = ActionTimeResolver._find_ability_action_time(
            fleet, ability_name, component_registry or {}
        )

        return action_time

    @staticmethod
    def _find_ability_action_time(
        fleet: 'Fleet',
        ability_name: str,
        component_registry: Dict[str, Any]
    ) -> int:
        """
        Find action_time from the first ship with the specified ability.

        Args:
            fleet: The Fleet to search
            ability_name: Name of ability to find
            component_registry: Component registry for ability lookup

        Returns:
            action_time from ability, or 1 if not found/specified
        """
        for ship in fleet.ships:
            for _comp_entry, _comp_def, abilities in iterate_design_components(
                ship.design_data, component_registry
            ):
                if ability_name in abilities:
                    ability_data = abilities[ability_name]
                    # Extract action_time from ability data
                    return ActionTimeResolver._extract_action_time(ability_data)

        # No ship has the ability - return default
        return 1

    @staticmethod
    def _extract_action_time(ability_data: Any) -> int:
        """
        Extract action_time from ability data.

        Handles various formats:
        - Dict with action_time: {"action_time": 3} -> 3
        - Dict without action_time: {"planet_type": "X"} -> 1
        - Boolean marker: True -> 1
        - String shorthand: "CONTINENTAL" -> 1

        Args:
            ability_data: The ability data (dict, bool, or string)

        Returns:
            action_time value, defaults to 1
        """
        if isinstance(ability_data, dict):
            return ability_data.get('action_time', 1)
        # Boolean marker or string shorthand - default to 1
        return 1
