"""Order-handler dispatch package (PROJ-368).

Per-OrderType handlers for action / instant order pipelines. Mirrors the
parallel `engine/handlers/` (command-handler) package: same Protocol
idiom, same `create_default_*_registry()` factory shape, same per-handler
test colocation under `tests/unit/strategy/engine/order_handlers/`.

Order handlers run on the action / instant tick path — they mutate
Fleet, Planet, and Empire state. Command handlers run on the UI command
path — they validate and emit Orders. The two registries operate on
different inputs and live side-by-side in the strategy engine.
"""
from __future__ import annotations

from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    IOrderHandler,
    OrderExecutionResult,
    OrderHandlerRegistry,
)
from game.strategy.engine.order_handlers.join_fleet import JoinFleetHandler
from game.strategy.engine.order_handlers.registry_factory import (
    create_default_order_handler_registry,
)

__all__ = [
    "BaseOrderHandler",
    "IOrderHandler",
    "OrderExecutionResult",
    "OrderHandlerRegistry",
    "JoinFleetHandler",
    "create_default_order_handler_registry",
]
