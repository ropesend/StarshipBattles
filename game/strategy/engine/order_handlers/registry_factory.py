"""`create_default_order_handler_registry()` -- composes the default
order-handler registry (PROJ-368).

Mirrors `game.strategy.engine.handlers.registry_factory.create_default_registry`
in shape. Each phase of PROJ-368 appends new handler registrations:

- Phase 1: JoinFleetHandler.
- Phase 2: ColonizeHandler, SelfDestructHandler.
- Phase 3: TransferHandler (registered against TRANSFER, LOAD_POPULATION,
  UNLOAD_POPULATION -- single instance, three keys).
- Phase 4: 5 SuperweaponHandlerAdapters built from `SUPERWEAPONS`.
"""
from __future__ import annotations

from typing import Any, Optional

from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import OrderHandlerRegistry
from game.strategy.engine.order_handlers.colonize import ColonizeHandler
from game.strategy.engine.order_handlers.join_fleet import JoinFleetHandler
from game.strategy.engine.order_handlers.self_destruct import SelfDestructHandler
from game.strategy.engine.order_handlers.superweapons import (
    build_superweapon_handlers,
)
from game.strategy.engine.order_handlers.transfer import TransferHandler


def create_default_order_handler_registry(
    *,
    event_bus: Optional[Any] = None,
    superweapon_processor: Optional[Any] = None,
) -> OrderHandlerRegistry:
    """Create the default order-handler registry.

    Args:
        event_bus: Optional EventBus threaded through to every handler so
            structured events (`FLEET_JOINED`, `FLEET_JOIN_CANCELLED`,
            etc.) can fire.
        superweapon_processor: Optional pre-constructed
            `SuperweaponOrderProcessor`. When None, one is constructed
            internally with the supplied event_bus.

    Returns:
        OrderHandlerRegistry with every currently-handled OrderType
        registered: JOIN_FLEET, COLONIZE, SELF_DESTRUCT, TRANSFER,
        LOAD_POPULATION, UNLOAD_POPULATION, and the 5 spec-driven
        superweapons.
    """
    registry = OrderHandlerRegistry()
    registry.register(OrderType.JOIN_FLEET, JoinFleetHandler(event_bus=event_bus))
    registry.register(OrderType.COLONIZE, ColonizeHandler(event_bus=event_bus))
    registry.register(OrderType.SELF_DESTRUCT, SelfDestructHandler(event_bus=event_bus))
    # TransferHandler is a single instance registered against three OrderType keys.
    transfer_handler = TransferHandler(event_bus=event_bus)
    registry.register(OrderType.TRANSFER, transfer_handler)
    registry.register(OrderType.LOAD_POPULATION, transfer_handler)
    registry.register(OrderType.UNLOAD_POPULATION, transfer_handler)

    # 5 superweapon adapters wrap the existing SuperweaponOrderProcessor.process_*
    # methods. SELF_DESTRUCT is NOT in SUPERWEAPONS -- it is handled above by
    # the lifted SelfDestructHandler.
    if superweapon_processor is None:
        # Lazy import to avoid circular dependency on engine layer.
        from game.strategy.engine.superweapon_order_processor import (
            SuperweaponOrderProcessor,
        )
        superweapon_processor = SuperweaponOrderProcessor(event_bus=event_bus)
    for adapter in build_superweapon_handlers(superweapon_processor):
        registry.register(adapter.supported_order_types[0], adapter)
    return registry
