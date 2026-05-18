"""
Order serialization and deserialization.

Extracted from fleet.py (PROJ-210) to reduce complexity.
PROJ-238: Renamed from fleet_order_serializer.py.
Handles 7 distinct target formats for Order persistence.
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
from game.core.hex_math import HexCoord
from game.core.validation_helpers import validate_enum
from game.strategy.data.order_types import OrderType, Order

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet

logger = logging.getLogger(__name__)


class OrderSerializer:
    """
    Handles serialization and deserialization of Order target values.

    Supports 7 target formats:
    1. HexCoord - {'q': x, 'r': y} for MOVE, WARP targets
    2. Fleet reference - {'type': 'fleet_ref', 'id': xxx} for MOVE_TO_FLEET, JOIN_FLEET
    3. Planet reference - {'type': 'planet_ref', 'id': xxx} for COLONIZE, IMPLODE_PLANET
    4. Transfer params - {'type': 'transfer', 'value': {...}} for TRANSFER orders
    5. Warp params - {'type': 'warp_params', 'value': {...}} for OPEN_WARP_POINT
    6. Ship ID list - {'type': 'ship_id_list', 'value': [...]} for SELF_DESTRUCT
    7. Raw fallback - {'type': 'raw', 'value': str} for unknown types
    """

    @staticmethod
    def deserialize_orders(
        orders_data: List[Dict[str, Any]],
        fleet_id: Any
    ) -> List[Order]:
        """
        Deserialize a list of orders from save data.

        Args:
            orders_data: List of order dictionaries from save
            fleet_id: Fleet ID for logging purposes

        Returns:
            List of Order objects.

        Raises:
            PersistenceException: If any order entry is corrupt (PROJ-251: strict deserialization).
        """
        orders = []
        for i, order_data in enumerate(orders_data):
            try:
                order = OrderSerializer._deserialize_single_order(order_data, i)
                orders.append(order)
            except (PersistenceException, KeyError, TypeError, ValueError) as e:
                raise PersistenceException(
                    f"Corrupt order data at index {i} in fleet '{fleet_id}'",
                    code=ErrorCode.CORRUPT_DATA.value,
                    context={"fleet_id": fleet_id, "order_index": i, "original_error": str(e)}
                ) from e
        return orders

    @staticmethod
    def _deserialize_single_order(order_data: Dict[str, Any], index: int) -> Order:
        """
        Deserialize a single order from save data.

        Args:
            order_data: Order dictionary from save
            index: Order index for error messages

        Returns:
            Order object

        Raises:
            Exception: If order data is invalid
        """
        order_type = validate_enum(
            order_data['type'],
            OrderType,
            'type',
            f'Fleet order[{index}]'
        )
        target = OrderSerializer._deserialize_target(order_data.get('target'))

        order = Order(order_type, target)
        # PROJ-187: Restore execution_progress (default 0 for backward compat)
        order.execution_progress = order_data.get('execution_progress', 0)
        return order

    @staticmethod
    def _deserialize_target(target_data: Any) -> Any:
        """
        Deserialize order target from save format.

        Args:
            target_data: Target data in one of 7 formats, or None

        Returns:
            Deserialized target (HexCoord, marker dict, or raw value)
        """
        if target_data is None:
            return None

        if not isinstance(target_data, dict):
            return target_data

        # Format 1: HexCoord - {'q': x, 'r': y}
        if 'q' in target_data and 'r' in target_data:
            return HexCoord(target_data['q'], target_data['r'])

        # Format 2: Fleet reference
        if target_data.get('type') == 'fleet_ref':
            return {'_fleet_ref': target_data['id']}

        # Format 3: Planet reference
        if target_data.get('type') == 'planet_ref':
            return {'_planet_ref': target_data['id']}

        # Format 3b: Colonize params (planet ref + population/cargo amounts)
        if target_data.get('type') == 'colonize_params':
            return {
                '_colonize_planet_ref': target_data.get('planet_id'),
                'population': target_data.get('population'),
                'cargo': target_data.get('cargo'),
            }

        # Format 4: Transfer params (PROJ-68)
        if target_data.get('type') == 'transfer':
            return target_data['value']

        # Format 5: Warp params (PROJ-102)
        if target_data.get('type') == 'warp_params':
            return target_data['value']

        # Format 6: Ship ID list (PROJ-102)
        if target_data.get('type') == 'ship_id_list':
            return target_data['value']

        # Format 7: Raw fallback
        if target_data.get('type') == 'raw':
            return target_data['value']

        # F-A-020: a typed dict whose `type:` does not match any known
        # branch is a save-format drift signal — fail fast at load time
        # rather than letting a dict target propagate into an order
        # handler and crash with AttributeError later.
        if 'type' in target_data:
            raise PersistenceException(
                f"Unknown target type: {target_data['type']!r}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"target_data": target_data},
            )

        # Untyped dicts (no `type` key) pre-date the typed formats and
        # round-trip as opaque payloads — keep the pass-through.
        return target_data

    @staticmethod
    def resolve_order_references(
        fleet: 'Fleet',
        galaxy: Any,
        empires: List[Any]
    ) -> None:
        """
        Resolve order target references after deserialization.

        During from_dict(), order targets that reference Fleets or Planets are stored
        as marker dicts (_fleet_ref, _planet_ref). This method resolves those markers
        to actual object references.

        Orders with unresolvable references (deleted fleets/planets) are removed
        with a warning.

        Args:
            fleet: Fleet whose orders need resolution
            galaxy: Galaxy object with get_planet_by_id() method
            empires: List of Empire objects containing all fleets
        """
        # Build fleet lookup across all empires
        fleet_lookup: Dict[Any, 'Fleet'] = {}
        for empire in empires:
            for f in empire.fleets:
                fleet_lookup[f.id] = f

        # Resolve references, collecting indices of orders to remove
        orders_to_remove: List[int] = []

        for i, order in enumerate(fleet.orders):
            target = order.target
            if not isinstance(target, dict):
                continue

            # Resolve _fleet_ref
            if '_fleet_ref' in target:
                fleet_id = target['_fleet_ref']
                resolved_fleet = fleet_lookup.get(fleet_id)
                if resolved_fleet is not None:
                    order.target = resolved_fleet
                else:
                    logger.warning(
                        f"Fleet {fleet.id}: Cannot resolve _fleet_ref {fleet_id} - fleet no longer exists, removing order"
                    )
                    orders_to_remove.append(i)

            # Resolve _planet_ref
            elif '_planet_ref' in target:
                planet_id = target['_planet_ref']
                resolved_planet = galaxy.get_planet_by_id(planet_id)
                if resolved_planet is not None:
                    order.target = resolved_planet
                else:
                    logger.warning(
                        f"Fleet {fleet.id}: Cannot resolve _planet_ref {planet_id} - planet no longer exists, removing order"
                    )
                    orders_to_remove.append(i)

            # Resolve _colonize_planet_ref (COLONIZE with population/cargo amounts)
            elif '_colonize_planet_ref' in target:
                planet_id = target['_colonize_planet_ref']
                resolved_planet = galaxy.get_planet_by_id(planet_id) if planet_id else None
                if planet_id is not None and resolved_planet is None:
                    logger.warning(
                        f"Fleet {fleet.id}: Cannot resolve colonize planet {planet_id}, removing order"
                    )
                    orders_to_remove.append(i)
                else:
                    order.target = {
                        'planet': resolved_planet,
                        'population': target.get('population'),
                        'cargo': target.get('cargo'),
                    }

        # Remove invalid orders in reverse order to maintain indices
        for i in reversed(orders_to_remove):
            fleet.orders.pop(i)
