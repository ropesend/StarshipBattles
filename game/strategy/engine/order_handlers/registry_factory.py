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


def create_default_order_handler_registry(
    *,
    event_bus: Optional[Any] = None,
) -> OrderHandlerRegistry:
    """Create the default order-handler registry.

    Args:
        event_bus: Optional EventBus threaded through to every handler so
            structured events (`FLEET_JOINED`, `FLEET_JOIN_CANCELLED`,
            etc.) can fire.

    Returns:
        OrderHandlerRegistry with all currently-extracted handlers
        registered. Phase 4 will add 5 superweapon adapters.
    """
    registry = OrderHandlerRegistry()
    registry.register(OrderType.JOIN_FLEET, JoinFleetHandler(event_bus=event_bus))
    registry.register(OrderType.COLONIZE, ColonizeHandler(event_bus=event_bus))
    registry.register(OrderType.SELF_DESTRUCT, SelfDestructHandler(event_bus=event_bus))
    return registry
