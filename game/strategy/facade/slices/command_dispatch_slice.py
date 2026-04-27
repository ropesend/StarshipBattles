"""Command dispatch slice (PROJ-309 sub-phase 3.7).

Holds the 28 `dispatch_*` helpers and the `handle_command` entry point.

Each `dispatch_*` is the same one-line shape: import the command, instantiate
it from kwargs, and forward to `handle_command`. The slice routes through a
caller-supplied `handle_command` callable so tests that monkey-patch
`facade.handle_command = MagicMock(...)` (see `test_facade_dispatch.py`) still
intercept the call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from game.core.validation import ValidationResult
    from game.strategy.engine.commands import Command
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class CommandDispatchSlice:
    """All write-path helpers, isolated from query slices."""

    __slots__ = ("_state", "_handle_command")

    def __init__(
        self,
        state: "FacadeSessionState",
        handle_command: Callable[["Command"], "ValidationResult"],
    ) -> None:
        self._state = state
        # `handle_command` is supplied as a callable so dispatchers go through
        # whatever the facade currently exposes (including monkey-patched
        # MagicMocks in tests).
        self._handle_command = handle_command

    # ------------------------------------------------------------------
    # Universal entry point
    # ------------------------------------------------------------------

    def handle_command(self, command: "Command") -> "ValidationResult":
        """Execute a command against the game session."""
        return self._state.session.handle_command(command)

    # ------------------------------------------------------------------
    # Fleet-order dispatchers
    # ------------------------------------------------------------------

    def dispatch_issue_colonize(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueColonizeCommand."""
        from game.strategy.engine.commands import IssueColonizeCommand
        return self._handle_command(IssueColonizeCommand(**kwargs))

    def dispatch_issue_move(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueMoveCommand."""
        from game.strategy.engine.commands import IssueMoveCommand
        return self._handle_command(IssueMoveCommand(**kwargs))

    def dispatch_issue_intercept(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueInterceptCommand."""
        from game.strategy.engine.commands import IssueInterceptCommand
        return self._handle_command(IssueInterceptCommand(**kwargs))

    def dispatch_issue_join_fleet(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueJoinFleetCommand."""
        from game.strategy.engine.commands import IssueJoinFleetCommand
        return self._handle_command(IssueJoinFleetCommand(**kwargs))

    def dispatch_clear_orders(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch ClearOrdersCommand."""
        from game.strategy.engine.commands import ClearOrdersCommand
        return self._handle_command(ClearOrdersCommand(**kwargs))

    def dispatch_issue_transfer(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueTransferCommand."""
        from game.strategy.engine.commands import IssueTransferCommand
        return self._handle_command(IssueTransferCommand(**kwargs))

    def dispatch_issue_warp(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueWarpCommand."""
        from game.strategy.engine.commands import IssueWarpCommand
        return self._handle_command(IssueWarpCommand(**kwargs))

    def dispatch_split_fleet(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch SplitFleetCommand."""
        from game.strategy.engine.commands import SplitFleetCommand
        return self._handle_command(SplitFleetCommand(**kwargs))

    def dispatch_delete_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch DeleteOrderCommand."""
        from game.strategy.engine.commands import DeleteOrderCommand
        return self._handle_command(DeleteOrderCommand(**kwargs))

    def dispatch_reorder_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch ReorderOrderCommand."""
        from game.strategy.engine.commands import ReorderOrderCommand
        return self._handle_command(ReorderOrderCommand(**kwargs))

    def dispatch_issue_self_destruct(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueSelfDestructCommand."""
        from game.strategy.engine.commands import IssueSelfDestructCommand
        return self._handle_command(IssueSelfDestructCommand(**kwargs))

    # ------------------------------------------------------------------
    # Mission queueing dispatchers
    # ------------------------------------------------------------------

    def dispatch_queue_colonize_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueColonizeMissionCommand."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand
        return self._handle_command(QueueColonizeMissionCommand(**kwargs))

    def dispatch_queue_implode_planet_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueImplodePlanetMissionCommand."""
        from game.strategy.engine.commands import QueueImplodePlanetMissionCommand
        return self._handle_command(QueueImplodePlanetMissionCommand(**kwargs))

    def dispatch_queue_stellerate_star_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueStellerateStarMissionCommand."""
        from game.strategy.engine.commands import QueueStellerateStarMissionCommand
        return self._handle_command(QueueStellerateStarMissionCommand(**kwargs))

    def dispatch_queue_open_warp_point_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueOpenWarpPointMissionCommand."""
        from game.strategy.engine.commands import QueueOpenWarpPointMissionCommand
        return self._handle_command(QueueOpenWarpPointMissionCommand(**kwargs))

    def dispatch_queue_close_warp_point_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueCloseWarpPointMissionCommand."""
        from game.strategy.engine.commands import QueueCloseWarpPointMissionCommand
        return self._handle_command(QueueCloseWarpPointMissionCommand(**kwargs))

    def dispatch_queue_create_dyson_sphere_mission(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch QueueCreateDysonSphereMissionCommand."""
        from game.strategy.engine.commands import QueueCreateDysonSphereMissionCommand
        return self._handle_command(QueueCreateDysonSphereMissionCommand(**kwargs))

    # ------------------------------------------------------------------
    # Superweapon (immediate) dispatchers
    # ------------------------------------------------------------------

    def dispatch_issue_implode_planet(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueImplodePlanetCommand."""
        from game.strategy.engine.commands import IssueImplodePlanetCommand
        return self._handle_command(IssueImplodePlanetCommand(**kwargs))

    def dispatch_issue_stellerate_star(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueStellerateStarCommand."""
        from game.strategy.engine.commands import IssueStellerateStarCommand
        return self._handle_command(IssueStellerateStarCommand(**kwargs))

    def dispatch_issue_open_warp_point(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueOpenWarpPointCommand."""
        from game.strategy.engine.commands import IssueOpenWarpPointCommand
        return self._handle_command(IssueOpenWarpPointCommand(**kwargs))

    def dispatch_issue_close_warp_point(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueCloseWarpPointCommand."""
        from game.strategy.engine.commands import IssueCloseWarpPointCommand
        return self._handle_command(IssueCloseWarpPointCommand(**kwargs))

    def dispatch_issue_create_dyson_sphere(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueCreateDysonSphereCommand."""
        from game.strategy.engine.commands import IssueCreateDysonSphereCommand
        return self._handle_command(IssueCreateDysonSphereCommand(**kwargs))

    # ------------------------------------------------------------------
    # Build / construction dispatchers
    # ------------------------------------------------------------------

    def dispatch_issue_build_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssueBuildOrderCommand."""
        from game.strategy.engine.commands import IssueBuildOrderCommand
        return self._handle_command(IssueBuildOrderCommand(**kwargs))

    def dispatch_remove_build_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch RemoveBuildOrderCommand."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        return self._handle_command(RemoveBuildOrderCommand(**kwargs))

    def dispatch_add_to_construction_queue(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch AddToConstructionQueueCommand."""
        from game.strategy.engine.commands import AddToConstructionQueueCommand
        return self._handle_command(AddToConstructionQueueCommand(**kwargs))

    def dispatch_remove_from_construction_queue(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch RemoveFromConstructionQueueCommand."""
        from game.strategy.engine.commands import RemoveFromConstructionQueueCommand
        return self._handle_command(RemoveFromConstructionQueueCommand(**kwargs))

    def dispatch_reorder_construction_queue(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch ReorderConstructionQueueCommand."""
        from game.strategy.engine.commands import ReorderConstructionQueueCommand
        return self._handle_command(ReorderConstructionQueueCommand(**kwargs))

    # ------------------------------------------------------------------
    # Planet-order dispatchers
    # ------------------------------------------------------------------

    def dispatch_issue_planet_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch IssuePlanetOrderCommand."""
        from game.strategy.engine.commands import IssuePlanetOrderCommand
        return self._handle_command(IssuePlanetOrderCommand(**kwargs))

    def dispatch_clear_planet_orders(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch ClearPlanetOrdersCommand."""
        from game.strategy.engine.commands import ClearPlanetOrdersCommand
        return self._handle_command(ClearPlanetOrdersCommand(**kwargs))

    def dispatch_delete_planet_order(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch DeletePlanetOrderCommand."""
        from game.strategy.engine.commands import DeletePlanetOrderCommand
        return self._handle_command(DeletePlanetOrderCommand(**kwargs))

    def dispatch_set_atmosphere_target(self, **kwargs) -> "ValidationResult":
        """Helper to dispatch SetAtmosphereTargetCommand."""
        from game.strategy.engine.commands import SetAtmosphereTargetCommand
        return self._handle_command(SetAtmosphereTargetCommand(**kwargs))
