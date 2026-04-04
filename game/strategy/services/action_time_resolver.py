"""
ActionTimeResolver - Resolves action_time for tick-based order execution.

PROJ-187: Strategy Orders Tick-Based Action System
PROJ-238: Unified to handle both fleet and planet orders.

This service looks up the action_time for a given order by finding the
relevant ability on the entity's components. Each strategic action has an
action_time that determines how many ticks it takes to complete.

Action times are defined on component abilities in components.json:
- ColonizePlanet: {"planet_type": "CONTINENTAL", "action_time": 2}
- DestroyPlanet: {"action_time": 3}
- PlanetaryShield: {"activation_time": 50, "deactivation_time": 10}
etc.
"""
from typing import TYPE_CHECKING, Any, Dict, Optional

from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import (
    iterate_design_components,
)
from game.strategy.data.order_types import OrderType, PLANET_ACTION_ORDER_TYPES

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.data.order_types import Order


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
    # PROJ-238: Planet orders
    OrderType.ACTIVATE_SHIELD: 'PlanetaryShield',
    OrderType.DEACTIVATE_SHIELD: 'PlanetaryShield',
}

# PROJ-238: Order types that use a non-standard time field name.
# If not listed here, 'action_time' is used (the default).
ORDER_TO_TIME_FIELD: Dict[OrderType, str] = {
    OrderType.ACTIVATE_SHIELD: 'activation_time',
    OrderType.DEACTIVATE_SHIELD: 'deactivation_time',
}

# Order types that are handled by movement engine, not action engine
MOVEMENT_ORDER_TYPES: frozenset = frozenset({OrderType.MOVE, OrderType.MOVE_TO_FLEET})


class ActionTimeResolver:
    """Resolves action_time for tick-based order execution.

    PROJ-238: Unified resolver for both fleet and planet orders.
    Looks up the action_time from the relevant ability on either
    fleet ships or planet facilities, depending on entity type.
    """

    @staticmethod
    def resolve_action_time(
        entity,
        order: 'Order',
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Resolve the action_time for a given order.

        PROJ-238: Accepts either Fleet or Planet as entity.

        Args:
            entity: The Fleet or Planet executing the order.
            order: The Order being executed.
            component_registry: Optional component registry for ability lookup.

        Returns:
            Integer action_time (ticks required to complete the action).
        """
        # Movement orders are handled by movement engine, not action engine
        if order.type in MOVEMENT_ORDER_TYPES:
            return 0

        # Get the ability name for this order type
        ability_name = ORDER_TO_ABILITY_MAP.get(order.type)
        if ability_name is None:
            return 1

        # Determine the time field to extract
        time_field = ORDER_TO_TIME_FIELD.get(order.type, 'action_time')

        # Search entity's components (ships for fleets, facilities for planets)
        # PROJ-238: Use order type to determine search path (avoids MagicMock hasattr issues)
        if order.type in PLANET_ACTION_ORDER_TYPES:
            # Planet order: search facility components
            return ActionTimeResolver._find_planet_ability_time(
                entity, order, ability_name, time_field, component_registry
            )
        else:
            # Fleet order: search ship components
            return ActionTimeResolver._find_fleet_ability_time(
                entity, ability_name, time_field, component_registry or {}
            )

        return 1

    @staticmethod
    def _find_fleet_ability_time(
        fleet: 'Fleet',
        ability_name: str,
        time_field: str,
        component_registry: Dict[str, Any]
    ) -> int:
        """Find action_time from the first ship with the specified ability."""
        for ship in fleet.ships:
            for _comp_entry, _comp_def, abilities in iterate_design_components(
                ship.design_data, component_registry
            ):
                if ability_name in abilities:
                    ability_data = abilities[ability_name]
                    return ActionTimeResolver._extract_time(ability_data, time_field)
        return 1

    @staticmethod
    def _find_planet_ability_time(
        planet: 'Planet',
        order: 'Order',
        ability_name: str,
        time_field: str,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """Find action_time from the target facility's components.

        PROJ-238: Searches facilities for the ability, optionally filtering
        by the target facility specified in order.target.
        """
        # Find target facility if specified
        target = order.target
        facility_id = None
        if isinstance(target, dict):
            facility_id = target.get('facility_instance_id')

        facilities_to_search = planet.facilities
        if facility_id:
            facilities_to_search = [
                f for f in planet.facilities
                if f.instance_id == facility_id
            ]

        for facility in facilities_to_search:
            if not facility.is_operational:
                continue
            for comp in iter_components(facility.design_data):
                abilities = _get_abilities(comp, component_registry)
                ability_data = abilities.get(ability_name)
                if isinstance(ability_data, dict):
                    time_value = ability_data.get(time_field)
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        return int(time_value)

        return 1

    @staticmethod
    def _extract_time(ability_data: Any, time_field: str = 'action_time') -> int:
        """Extract time value from ability data.

        Args:
            ability_data: The ability data (dict, bool, or string).
            time_field: The field name to extract (default 'action_time').

        Returns:
            Time value, defaults to 1.
        """
        if isinstance(ability_data, dict):
            return ability_data.get(time_field, 1)
        return 1


def _get_abilities(comp, component_registry: Optional[Dict[str, Any]] = None) -> dict:
    """Extract abilities from a component entry.

    Delegates to centralized extract_abilities_from_component().
    """
    from game.strategy.services.component_inspector import extract_abilities_from_component
    return extract_abilities_from_component(comp, component_registry)
