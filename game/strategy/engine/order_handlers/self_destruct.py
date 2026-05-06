"""SelfDestructHandler -- handles `OrderType.SELF_DESTRUCT` (PROJ-368 Phase 2).

Lifted from `SuperweaponOrderProcessor.process_self_destruct` (the only
superweapon path that did NOT flow through the spec-driven
`execute_superweapon` dispatcher -- see decisions.md row 6 +
`design.md` § Phase 2.4). Surfacing it as a peer handler in
`order_handlers/` puts it on equal footing with the 5 spec-driven
SuperweaponHandlerAdapter siblings introduced in Phase 4.

Removes the specified ships from the fleet; if the fleet ends up empty,
the empty fleet is removed from the empire (SG-003 fix). The carrying
fleet is consumed only when emptied, never as a precondition.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.events.event_types import EventCategory, EventType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


class SelfDestructHandler(BaseOrderHandler):
    """Handler for `OrderType.SELF_DESTRUCT`."""

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.SELF_DESTRUCT,)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Execute a SELF_DESTRUCT order.

        Removes the specified ships from the fleet. If the fleet is
        emptied, the fleet is removed from the empire and
        `fleet_consumed=True` is reported.
        """
        order = fleet.get_current_order()
        if not order or order.type != OrderType.SELF_DESTRUCT:
            return OrderExecutionResult(success=False, message="No SELF_DESTRUCT order")

        # Target is list of ship IDs
        ship_ids = order.target
        if not isinstance(ship_ids, list) or not ship_ids:
            fleet.pop_order()
            return OrderExecutionResult(success=False, message="No ships specified")

        # Build ship lookup
        ships_by_id = {ship.id: ship for ship in fleet.ships}

        # Collect ships to remove
        ships_to_remove = []
        ship_names = []
        for ship_id in ship_ids:
            ship = ships_by_id.get(ship_id)
            if ship:
                ships_to_remove.append(ship)
                # Get name -- ship.name always exists on ShipInstance
                name = ship.name if isinstance(ship.name, str) else str(ship_id)
                ship_names.append(name)

        # FEAT-04: Capture location before fleet may be consumed
        fleet_loc = fleet.location

        # Remove ships
        for ship in ships_to_remove:
            fleet.remove_ship(ship)

        fleet.pop_order()

        # Check if fleet is now empty
        fleet_consumed = len(fleet.ships) == 0

        # Clean up empty fleet (SG-003 fix)
        if fleet_consumed:
            empire.remove_fleet(fleet, event_bus=self._event_bus)

        logger.info(f"Ships self-destructed: {', '.join(ship_names)}")
        self._emit_event(
            EventType.SHIPS_SELF_DESTRUCTED,
            category=EventCategory.SUPERWEAPONS,
            empire_id=empire.id,
            message=f"{len(ships_to_remove)} ships self-destructed",
            fleet_id=fleet.id,
            ship_count=len(ships_to_remove),
            ship_names=ship_names,
            location_hex=[fleet_loc.q, fleet_loc.r],
        )

        return OrderExecutionResult(
            success=True,
            fleet_consumed=fleet_consumed,
            message=f"{len(ships_to_remove)} ships self-destructed",
        )
