"""
OrderProcessor - centralized order lifecycle management (facade).

PROJ-368 made this a thin facade over the per-OrderType handler
registry in `game.strategy.engine.order_handlers`. PROJ-454 Phase 3
deleted the three legacy per-action shims (`process_join_fleet` /
`process_colonize` / `process_transfer`) and their typed result
dataclasses (`JoinFleetResult` / `ColonizeResult` / `TransferResult`);
every consumer now invokes the unified handler-direct path
``processor.get_handler(OrderType.X).execute_action_order(...)`` and
reads fields directly off the unified ``OrderExecutionResult``.

Surviving public surface:
- ``get_handler(order_type)`` — registry accessor (PROJ-438 Phase 6).
- ``process_instant_orders(empires)`` — drives the BUG-122 three-phase
  JOIN_FLEET pipeline; the only place ``OrderType.JOIN_FLEET`` is
  referenced inside the facade module.
- ``execute_action_order(fleet, empire, galaxy, ...)`` — the canonical
  per-fleet action dispatch used by ``ActionExecutionEngine``.
"""
from __future__ import annotations

from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
import logging

from game.strategy.interfaces.engines import IOrderProcessor
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import IOrderHandler

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy

logger = logging.getLogger(__name__)


class OrderProcessor(IOrderProcessor):
    """Facade dispatching every order through the order-handler registry."""

    def __init__(self, event_bus: Optional[Any] = None) -> None:
        """Initialize the order processor.

        Args:
            event_bus: Optional EventBus for structured event logging.
        """
        self._event_bus = event_bus
        # Lazy import to avoid circular dependency
        from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
        self._superweapon_processor = SuperweaponOrderProcessor(event_bus=event_bus)
        # PROJ-368: per-OrderType handler registry. Reuses the same
        # SuperweaponOrderProcessor instance so SuperweaponHandlerAdapter
        # adapters delegate to a single processor (rather than constructing a
        # second one).
        from game.strategy.engine.order_handlers import create_default_order_handler_registry
        self._handler_registry = create_default_order_handler_registry(
            event_bus=event_bus,
            superweapon_processor=self._superweapon_processor,
        )

    def get_handler(self, order_type: OrderType) -> Optional[IOrderHandler]:
        """Public accessor for the per-OrderType handler (PROJ-438 Phase 6).

        Replaces the previous ``getattr(self._order_processor,
        "_handler_registry", ...)`` reach-in pattern used by
        ``ActionExecutionEngine._execute_planet_action``. External callers
        that need to dispatch through a handler (e.g., the planet-FMS
        execution path running orders against a
        ``PlanetStagingYardIssuerAdapter``) must use this method rather
        than touching ``_handler_registry`` directly.
        """
        return self._handler_registry.get(order_type)

    def process_instant_orders(
        self,
        empires: List["Empire"],
    ) -> List[Tuple["Empire", Fleet]]:
        """Process JOIN_FLEET orders for co-located fleets during a tick.

        BUG-122 three-phase pipeline lives in JoinFleetHandler; this
        method is the public entry point.

        PROJ-412 Phase 2.2 note: a "no JOIN_FLEET order anywhere" short-
        circuit was tried and dropped — bench-attributed cost of this
        phase is < 5 μs / tick, and structural prechecks broke
        MagicMock-driven tests. Not worth the fragility.
        """
        handler = self._handler_registry.get(OrderType.JOIN_FLEET)
        return handler.process_instant_orders(empires)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> bool:
        """Execute the fleet's current action order.

        PROJ-368 Phase 4: pure registry lookup. Returns True iff the
        order consumed the fleet.
        """
        order = fleet.get_current_order()
        if order is None:
            return False
        handler = self._handler_registry.get(order.type)
        if handler is None:
            return False
        result = handler.execute_action_order(
            fleet, empire, galaxy,
            component_registry=component_registry,
            empires=empires,
        )
        return result.fleet_consumed
