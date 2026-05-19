"""
OrderProcessor - centralized order lifecycle management (facade).

PROJ-368: this module is now a thin facade over the per-OrderType
handler registry in `game.strategy.engine.order_handlers`. Every method
delegates to a registered `IOrderHandler`. The legacy private helpers
(`_execute_fleet_merge`, `_execute_load`, `_execute_unload`,
`_execute_fleet_transfer`, `_load_pod_from_staging_yard`,
`_unload_pod_to_staging_yard`, `_deploy_drop_pod`,
`_validate_tick_inputs`, `_elect_canonical_merges`,
`_emit_join_cancelled`) were deleted in Phase 4 -- their live copies
live on the corresponding handlers.

Public surface kept for backward compatibility with existing
characterization tests (PROJ-333):
- `JoinFleetResult`, `ColonizeResult`, `TransferResult` typed result
  dataclasses (legacy contracts).
- `process_join_fleet`, `process_colonize`, `process_transfer`,
  `process_instant_orders`, `execute_action_order` public methods.
"""
from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class JoinFleetResult:
    """Result of a JOIN_FLEET operation."""
    merged: bool
    cancelled: bool = False


@dataclass
class ColonizeResult:
    """Result of a COLONIZE operation."""
    colonized: bool
    planet_name: Optional[str] = None


@dataclass
class TransferResult:
    """Result of a TRANSFER operation."""
    success: bool
    amount_transferred: int = 0
    message: str = ""


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

    def process_join_fleet(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
    ) -> JoinFleetResult:
        """Process a JOIN_FLEET order. Delegates to JoinFleetHandler."""
        handler = self._handler_registry.get(OrderType.JOIN_FLEET)
        result = handler.execute_action_order(fleet, empire, galaxy)
        return JoinFleetResult(merged=result.merged, cancelled=result.cancelled)

    def process_colonize(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Dict[str, Any],
    ) -> ColonizeResult:
        """Process a COLONIZE order. Delegates to ColonizeHandler."""
        handler = self._handler_registry.get(OrderType.COLONIZE)
        result = handler.execute_action_order(
            fleet, empire, galaxy,
            component_registry=component_registry,
        )
        return ColonizeResult(colonized=result.colonized, planet_name=result.planet_name)

    def process_transfer(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
    ) -> TransferResult:
        """Process a TRANSFER / LOAD_POPULATION / UNLOAD_POPULATION order.

        PROJ-368 review MIN-001: delegates immediately like the other facade
        shims. ``TransferHandler`` is registered as a single instance for all
        three transfer-family OrderTypes and validates the current order
        internally — a wrong/missing order returns
        ``success=False, message="No TRANSFER order"`` from the handler.
        """
        handler = self._handler_registry.get(OrderType.TRANSFER)
        result = handler.execute_action_order(fleet, empire, galaxy)
        return TransferResult(
            success=result.success,
            amount_transferred=result.amount_transferred,
            message=result.message,
        )

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
