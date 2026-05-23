"""Infrastructure for the order-handler dispatch system (PROJ-368).

Owns:
    - `IOrderHandler` Protocol (typing seam for handlers)
    - `BaseOrderHandler` mixin (event-bus emission helper)
    - `OrderHandlerRegistry` (dispatch table)
    - `OrderExecutionResult` (unified result type returned by handlers)

Mirrors `game.strategy.engine.handlers.base`'s `ICommandHandler` /
`CommandHandlerRegistry` pair. The two registries dispatch different
inputs (UI Command -> Order vs Order -> state mutation) but share the
same Protocol-and-registry idiom.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    TYPE_CHECKING,
    Tuple,
    runtime_checkable,
)

from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.ship_instance import ShipInstance
    from game.strategy.services.planet_write_service import PlanetWriteService
    from game.strategy.services.ship_instance_write_service import (
        ShipInstanceWriteService,
    )


@dataclass
class OrderExecutionResult:
    """Unified result type for `IOrderHandler.execute_action_order`.

    All concrete handlers populate the fields they care about; readers
    consume the unified result directly. The class carries per-handler
    fields side by side because the runtime overhead is negligible and
    per-handler payload subclasses would complicate caller ergonomics.

    PROJ-454 Phase 3 retired the typed-result reshape on the
    `OrderProcessor` facade; the per-handler fields below are the live
    unified surface, not legacy.

    `SuperweaponResult` is still produced separately by
    `SuperweaponOrderProcessor` and is NOT this type.
    """

    success: bool
    fleet_consumed: bool = False
    message: str = ""
    # Per-handler extras read directly off the unified result.
    merged: bool = False
    cancelled: bool = False
    colonized: bool = False
    planet_name: Optional[str] = None
    amount_transferred: int = 0


@runtime_checkable
class IOrderHandler(Protocol):
    """Per-OrderType handler for the action / instant order pipelines."""

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        """OrderType values this handler claims. Drives registry registration."""
        ...

    def execute_action_order(
        self,
        fleet: "Fleet",
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Execute the fleet's current action order.

        Returns:
            OrderExecutionResult with `.success`, `.fleet_consumed`,
            `.message`, plus handler-specific fields.
        """
        ...

    def execute_for_issuer(
        self,
        *,
        issuer: Any,
        order_owner: Any,
        empire: "Empire",
        galaxy: Optional["Galaxy"] = None,
        registries: Optional[Any] = None,
    ) -> OrderExecutionResult:
        """Execute the order against an arbitrary ``IIssuerAdapter``-wrapped
        issuer (PROJ-438 Phase 6 unified contract).

        Used by the planet-FMS execution path in
        ``ActionExecutionEngine._execute_planet_action`` so a planet's
        action order can be dispatched through the same per-OrderType
        handler that a fleet uses. The canonical 5-kwarg signature
        (``issuer``, ``order_owner``, ``empire``, ``galaxy``,
        ``registries``) is identical across launch and recovery handlers;
        the recovery handlers ignore the trailing two kwargs. The
        previous reach-in into ``OrderProcessor._handler_registry`` +
        ``try / except TypeError`` fallback in
        ``ActionExecutionEngine._execute_planet_action`` is retired by
        making this contract uniform.

        Handlers that don't participate in the planet-FMS path may
        either leave this Protocol method unimplemented (concrete classes
        without it raise ``AttributeError`` at the call site, which the
        engine treats as "not dispatchable for an issuer adapter") or
        provide a no-op that returns a not-supported
        ``OrderExecutionResult``.
        """
        ...


class BaseOrderHandler:
    """Mixin providing common event-bus emission for order handlers.

    Centralizes the `if self._event_bus: self._event_bus.log_event(...)`
    null-check that appears 7+ times in the legacy `OrderProcessor`. All
    concrete handlers inherit from this mixin and call `_emit_event(...)`
    instead of touching `self._event_bus` directly.
    """

    def __init__(
        self,
        *,
        event_bus: Optional[Any] = None,
        planet_mutator: Optional[Any] = None,
        ship_mutator: Optional[Any] = None,
    ) -> None:
        self._event_bus = event_bus
        self._planet_mutator = planet_mutator
        self._ship_mutator = ship_mutator

    def _get_planet_mutator(self) -> "PlanetWriteService":
        """Lazy-default the planet mutator (PROJ-370)."""
        if self._planet_mutator is None:
            from game.strategy.services.planet_write_service import (
                PlanetWriteService,
            )
            self._planet_mutator = PlanetWriteService()
        return self._planet_mutator

    def _get_ship_mutator(self) -> "ShipInstanceWriteService":
        """Lazy-default the ship instance mutator (PROJ-370)."""
        if self._ship_mutator is None:
            from game.strategy.services.ship_instance_write_service import (
                ShipInstanceWriteService,
            )
            self._ship_mutator = ShipInstanceWriteService()
        return self._ship_mutator

    @staticmethod
    def _find_ship(
        fleet: "Fleet", ship_instance_id: Any
    ) -> Optional["ShipInstance"]:
        """Resolve a ship within ``fleet`` by stringified instance id.

        DUP-X-1 (PROJ-465): consolidated from five byte-identical copies
        in the launch/recover/lay vehicle order handlers. Compares
        ``str(ship.instance_id) == str(ship_instance_id)`` so callers may
        pass either an int or a str id.
        """
        for ship in fleet.ships:
            if str(ship.instance_id) == str(ship_instance_id):
                return ship
        return None

    def _emit_event(
        self,
        event_type: Any,
        *,
        category: Any,
        empire_id: Any,
        message: str,
        **kwargs: Any,
    ) -> None:
        """Emit a structured event if an event bus is configured.

        No-op when `self._event_bus` is None. Mirrors the inline
        `if self._event_bus: self._event_bus.log_event(...)` pattern
        from the legacy OrderProcessor.
        """
        if self._event_bus is None:
            return
        self._event_bus.log_event(
            event_type,
            category=category,
            empire_id=empire_id,
            message=message,
            **kwargs,
        )


class OrderHandlerRegistry:
    """Registry mapping `OrderType` to `IOrderHandler` for dispatch.

    Single-handler-per-OrderType. Multiple `OrderType` keys may point to
    the same handler instance (e.g. `TRANSFER`, `LOAD_POPULATION`,
    `UNLOAD_POPULATION` all share `TransferHandler`). Duplicate
    registration of the same key raises `ValueError`.
    """

    def __init__(self) -> None:
        self._by_type: Dict[OrderType, IOrderHandler] = {}

    def register(self, order_type: OrderType, handler: IOrderHandler) -> None:
        """Register `handler` for `order_type`.

        Raises:
            ValueError: if `order_type` is already registered.
        """
        if order_type in self._by_type:
            raise ValueError(
                f"OrderHandlerRegistry: handler for {order_type.name} already registered"
            )
        self._by_type[order_type] = handler

    def get(self, order_type: OrderType) -> Optional[IOrderHandler]:
        """Return the registered handler for `order_type`, or None."""
        return self._by_type.get(order_type)

    def __contains__(self, order_type: OrderType) -> bool:
        return order_type in self._by_type

    def all_registered(self) -> frozenset[OrderType]:
        """Return the frozenset of registered `OrderType` keys."""
        return frozenset(self._by_type.keys())
