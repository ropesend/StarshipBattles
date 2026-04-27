"""Contract test for the public API of game.strategy.engine.command_handlers (PROJ-309 sub-phase 3.5).

The 1076-line monolith was decomposed into a package of cohesive sub-modules
under `game.strategy.engine.handlers/`. The original `command_handlers.py`
becomes a re-export shim (Option A) so that ~30 import sites — production
(`game_session.py`) plus tests — keep working unchanged.

This contract test asserts every symbol on the documented public-API list
remains importable from `game.strategy.engine.command_handlers`. The same
symbols must also be importable from their new canonical home in `handlers/`.
"""

import pytest


PUBLIC_COMMAND_HANDLER_SYMBOLS = (
    # Infrastructure
    "ICommandHandler",
    "BaseCommandHandler",
    "CommandHandlerRegistry",
    "add_move_order_if_needed",
    # Movement (5)
    "ColonizeCommandHandler",
    "MoveCommandHandler",
    "InterceptCommandHandler",
    "JoinCommandHandler",
    "WarpCommandHandler",
    # Order-queue (5)
    "ColonizeMissionCommandHandler",
    "ClearOrdersCommandHandler",
    "SplitFleetCommandHandler",
    "DeleteOrderCommandHandler",
    "ReorderOrderCommandHandler",
    # Transfer (1)
    "TransferCommandHandler",
    # Build (2)
    "BuildOrderCommandHandler",
    "RemoveBuildOrderCommandHandler",
    # Construction queue (3)
    "AddToConstructionQueueCommandHandler",
    "RemoveFromConstructionQueueCommandHandler",
    "ReorderConstructionQueueCommandHandler",
    # Factory
    "create_default_registry",
)


@pytest.mark.parametrize("symbol", PUBLIC_COMMAND_HANDLER_SYMBOLS)
def test_symbol_importable_from_shim(symbol: str) -> None:
    """Every public symbol remains importable from the original module path."""
    import game.strategy.engine.command_handlers as shim

    assert hasattr(shim, symbol), (
        f"{symbol!r} is no longer exported from game.strategy.engine.command_handlers. "
        "Production callers (game_session.py) and ~30 test sites depend on this path."
    )


def test_symbol_count_matches_design() -> None:
    """Public symbol count matches the decomposition design (21 symbols)."""
    assert len(PUBLIC_COMMAND_HANDLER_SYMBOLS) == 21


def test_create_default_registry_dispatches_all_command_classes() -> None:
    """The factory must register handlers for every Command class declared in
    `game.strategy.engine.commands`. Catches the case where a handler moves
    to a new module but its `registry.register(...)` call gets dropped.
    """
    from game.strategy.engine.command_handlers import create_default_registry
    import game.strategy.engine.commands as commands_module

    registry = create_default_registry()

    declared_commands = {
        name for name in dir(commands_module)
        if name.endswith("Command")
        and not name.startswith("_")
        and isinstance(getattr(commands_module, name), type)
    }
    declared_commands.discard("Command")

    registered = set(registry._handlers.keys())
    unregistered = declared_commands - registered
    assert not unregistered, (
        f"Command classes declared in commands.py but not registered with a handler: "
        f"{sorted(unregistered)}. Either add a handler or remove the unused command class."
    )
