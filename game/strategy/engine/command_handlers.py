"""Re-export shim for the decomposed command-handler package.

PROJ-309 sub-phase 3.5 (2026-04-27): the original 1076-line module was
split into the package `game.strategy.engine.handlers/`. This shim
preserves the original import path so existing callers — `game_session.py`
plus ~30 test sites — keep working without churn.

Per the System Migration Policy, this shim is **transitional**. Callers
should migrate to the canonical paths (`game.strategy.engine.handlers.*`)
in a follow-up project; the shim is then deleted. Do not add new symbols
here — add them to the appropriate sub-module under `handlers/`.

Original module documentation:

    Command Handler Registry - Strategy Command Dispatch

    Extracts command handling logic from GameSession into a registry-based
    dispatch pattern. Each command type has a dedicated handler class
    implementing the ICommandHandler protocol.

    Originally extracted in PROJ-87 Phase 5; decomposed in PROJ-309 Phase 3.5.

    Usage:
        registry = CommandHandlerRegistry()
        registry.register('IssueColonizeCommand', ColonizeCommandHandler())
        result = registry.dispatch('IssueColonizeCommand', session, command)
"""
from game.strategy.engine.handlers import (
    AddToConstructionQueueCommandHandler,
    BaseCommandHandler,
    BuildOrderCommandHandler,
    ClearOrdersCommandHandler,
    ColonizeCommandHandler,
    ColonizeMissionCommandHandler,
    CommandHandlerRegistry,
    DeleteOrderCommandHandler,
    ICommandHandler,
    InterceptCommandHandler,
    JoinCommandHandler,
    MoveCommandHandler,
    RemoveBuildOrderCommandHandler,
    RemoveFromConstructionQueueCommandHandler,
    ReorderConstructionQueueCommandHandler,
    ReorderOrderCommandHandler,
    SplitFleetCommandHandler,
    TransferCommandHandler,
    WarpCommandHandler,
    add_move_order_if_needed,
    create_default_registry,
)


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
