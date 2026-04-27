"""Command-handler dispatch system, decomposed from `command_handlers.py`.

PROJ-309 sub-phase 3.5 (2026-04-27): the original 1076-line monolith was
split into cohesive sub-modules grouped by domain (movement, order_queue,
transfer, build, construction_queue) plus infrastructure (`base.py`) and
the dispatcher factory (`registry_factory.py`). The legacy
`game.strategy.engine.command_handlers` module is now a re-export shim
preserving every public symbol so callers don't need to update imports.
"""
from game.strategy.engine.handlers.base import (
    BaseCommandHandler,
    CommandHandlerRegistry,
    ICommandHandler,
    add_move_order_if_needed,
)
from game.strategy.engine.handlers.build import (
    BuildOrderCommandHandler,
    RemoveBuildOrderCommandHandler,
)
from game.strategy.engine.handlers.construction_queue import (
    AddToConstructionQueueCommandHandler,
    RemoveFromConstructionQueueCommandHandler,
    ReorderConstructionQueueCommandHandler,
)
from game.strategy.engine.handlers.movement import (
    ColonizeCommandHandler,
    InterceptCommandHandler,
    JoinCommandHandler,
    MoveCommandHandler,
    WarpCommandHandler,
)
from game.strategy.engine.handlers.order_queue import (
    ClearOrdersCommandHandler,
    ColonizeMissionCommandHandler,
    DeleteOrderCommandHandler,
    ReorderOrderCommandHandler,
    SplitFleetCommandHandler,
)
from game.strategy.engine.handlers.registry_factory import create_default_registry
from game.strategy.engine.handlers.transfer import TransferCommandHandler


__all__ = [
    # Infrastructure
    "ICommandHandler",
    "BaseCommandHandler",
    "CommandHandlerRegistry",
    "add_move_order_if_needed",
    # Movement
    "ColonizeCommandHandler",
    "MoveCommandHandler",
    "InterceptCommandHandler",
    "JoinCommandHandler",
    "WarpCommandHandler",
    # Order-queue
    "ColonizeMissionCommandHandler",
    "ClearOrdersCommandHandler",
    "SplitFleetCommandHandler",
    "DeleteOrderCommandHandler",
    "ReorderOrderCommandHandler",
    # Transfer
    "TransferCommandHandler",
    # Build
    "BuildOrderCommandHandler",
    "RemoveBuildOrderCommandHandler",
    # Construction queue
    "AddToConstructionQueueCommandHandler",
    "RemoveFromConstructionQueueCommandHandler",
    "ReorderConstructionQueueCommandHandler",
    # Factory
    "create_default_registry",
]
