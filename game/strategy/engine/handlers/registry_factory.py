"""`create_default_registry()` — composes the default command-handler registry.

Wires together every handler from the `handlers/` package plus the two
sibling modules (`superweapon_command_handlers`, `planet_command_handlers`)
that remain at their original locations for this PROJ. Splitting them into
the package is out of scope for PROJ-309.

Imports of the sibling modules are kept function-scoped — that pattern from
the original monolith is preserved here. Whether it remains necessary
post-decomposition (now that `BaseCommandHandler` lives at leaf-level
`handlers/base.py`) is flagged in `findings/command_handlers_decomposition.md`
risk #4 for a follow-up audit; not changing it here per the design spec.
"""
from __future__ import annotations

from game.strategy.engine.handlers.base import CommandHandlerRegistry
from game.strategy.engine.handlers.build import (
    BuildOrderCommandHandler,
    RemoveBuildOrderCommandHandler,
)
from game.strategy.engine.handlers.construction_queue import (
    AddToConstructionQueueCommandHandler,
    RemoveFromConstructionQueueCommandHandler,
    ReorderConstructionQueueCommandHandler,
    SetBuildQueuePausedCommandHandler,
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
from game.strategy.engine.handlers.transfer import TransferCommandHandler


def create_default_registry() -> CommandHandlerRegistry:
    """Create a registry with all standard command handlers registered.

    Returns:
        CommandHandlerRegistry with all handlers registered.
    """
    from game.strategy.engine.superweapon_command_handlers import (
        ImplodePlanetCommandHandler,
        StellerateStarCommandHandler,
        OpenWarpPointCommandHandler,
        CloseWarpPointCommandHandler,
        CreateDysonSphereCommandHandler,
        SelfDestructCommandHandler,
        ImplodePlanetMissionCommandHandler,
        StellerateStarMissionCommandHandler,
        OpenWarpPointMissionCommandHandler,
        CloseWarpPointMissionCommandHandler,
        CreateDysonSphereMissionCommandHandler,
    )

    registry = CommandHandlerRegistry()

    # Core handlers
    registry.register('IssueColonizeCommand', ColonizeCommandHandler())
    registry.register('IssueMoveCommand', MoveCommandHandler())
    # NOTE: IssueBuildShipCommand removed (PROJ-208) - use AddToConstructionQueueCommand
    registry.register('IssueInterceptCommand', InterceptCommandHandler())
    registry.register('IssueJoinFleetCommand', JoinCommandHandler())
    registry.register('QueueColonizeMissionCommand', ColonizeMissionCommandHandler())
    registry.register('ClearOrdersCommand', ClearOrdersCommandHandler())
    registry.register('IssueTransferCommand', TransferCommandHandler())
    registry.register('IssueWarpCommand', WarpCommandHandler())  # PROJ-187

    # Build order handlers (PROJ-207 Phase 4)
    registry.register('IssueBuildOrderCommand', BuildOrderCommandHandler())
    registry.register('RemoveBuildOrderCommand', RemoveBuildOrderCommandHandler())

    # Fleet management handlers (PROJ-208 Phase 1)
    registry.register('SplitFleetCommand', SplitFleetCommandHandler())
    registry.register('DeleteOrderCommand', DeleteOrderCommandHandler())
    registry.register('ReorderOrderCommand', ReorderOrderCommandHandler())

    # Construction queue handlers (PROJ-208 Phase 2; FEAT-17 added pause toggle)
    registry.register('AddToConstructionQueueCommand', AddToConstructionQueueCommandHandler())
    registry.register('RemoveFromConstructionQueueCommand', RemoveFromConstructionQueueCommandHandler())
    registry.register('ReorderConstructionQueueCommand', ReorderConstructionQueueCommandHandler())
    registry.register('SetBuildQueuePausedCommand', SetBuildQueuePausedCommandHandler())

    # Superweapon direct handlers (PROJ-102)
    registry.register('IssueImplodePlanetCommand', ImplodePlanetCommandHandler())
    registry.register('IssueStellerateStarCommand', StellerateStarCommandHandler())
    registry.register('IssueOpenWarpPointCommand', OpenWarpPointCommandHandler())
    registry.register('IssueCloseWarpPointCommand', CloseWarpPointCommandHandler())
    registry.register('IssueCreateDysonSphereCommand', CreateDysonSphereCommandHandler())
    registry.register('IssueSelfDestructCommand', SelfDestructCommandHandler())

    # Superweapon mission handlers (PROJ-102)
    registry.register('QueueImplodePlanetMissionCommand', ImplodePlanetMissionCommandHandler())
    registry.register('QueueStellerateStarMissionCommand', StellerateStarMissionCommandHandler())
    registry.register('QueueOpenWarpPointMissionCommand', OpenWarpPointMissionCommandHandler())
    registry.register('QueueCloseWarpPointMissionCommand', CloseWarpPointMissionCommandHandler())
    registry.register('QueueCreateDysonSphereMissionCommand', CreateDysonSphereMissionCommandHandler())

    # PROJ-237: Planet order command handlers
    from game.strategy.engine.planet_command_handlers import (
        IssuePlanetOrderCommandHandler,
        ClearPlanetOrdersCommandHandler,
        DeletePlanetOrderCommandHandler,
        SetAtmosphereTargetCommandHandler,
        SetGravityTargetCommandHandler,
        SetWaterTargetCommandHandler,
        SetRadiationShieldTargetCommandHandler,
    )
    registry.register('IssuePlanetOrderCommand', IssuePlanetOrderCommandHandler())
    registry.register('ClearPlanetOrdersCommand', ClearPlanetOrdersCommandHandler())
    registry.register('DeletePlanetOrderCommand', DeletePlanetOrderCommandHandler())
    registry.register('SetAtmosphereTargetCommand', SetAtmosphereTargetCommandHandler())
    registry.register('SetGravityTargetCommand', SetGravityTargetCommandHandler())
    registry.register('SetWaterTargetCommand', SetWaterTargetCommandHandler())
    registry.register('SetRadiationShieldTargetCommand', SetRadiationShieldTargetCommandHandler())

    return registry
