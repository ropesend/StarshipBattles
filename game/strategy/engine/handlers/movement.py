"""Fleet navigation command handlers — pathfinding-related commands.

Owns: Colonize, Move, Intercept, Join, Warp.

These five handlers all need pathfinding (`add_move_order_if_needed` for
auto-MOVE prefixes, `Order(OrderType.MOVE_TO_FLEET, ...)` for fleet pursuit).
Grouping them keeps the path-related code in one module.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import (
    IssueColonizeCommand,
    IssueInterceptCommand,
    IssueJoinFleetCommand,
    IssueMoveCommand,
    IssueWarpCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import (
    BaseCommandHandler,
    add_move_order_if_needed,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=IssueColonizeCommand,
    order_type=OrderType.COLONIZE,
    category='action',
    action_ability_name='ColonizePlanet',
    execution_model='action',
    facade_helper_name='dispatch_issue_colonize',
    serializer_codec='planet_ref',
)
class ColonizeCommandHandler(BaseCommandHandler):
    """Handler for IssueColonizeCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueColonizeCommand') -> ValidationResult:
        """Handle IssueColonizeCommand."""
        # 1. Resolve Fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # Resolve Planet (None is valid for colonize validation)
        target_planet = None
        if cmd.planet_id:
            target_planet = session._get_planet_by_id(cmd.planet_id)

        # 2. Validate
        result = session.turn_engine.validate_colonize_order(session.galaxy, fleet, target_planet)

        # 3. Apply
        if result.is_valid:
            # Loading is handled by explicit TRANSFER orders from the UI dialog.

            # Add MOVE order to get to the target planet
            planet_global_hex = session.galaxy.get_planet_global_hex(target_planet)

            if planet_global_hex and fleet.location != planet_global_hex:
                move_order = Order(OrderType.MOVE, target=planet_global_hex)
                fleet.add_order(move_order)

            # Build colonize target with optional population/cargo amounts
            colonize_target = self._build_colonize_target(target_planet, cmd)
            order = Order(OrderType.COLONIZE, target=colonize_target)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")

        return result


@command_spec(
    command_class=IssueMoveCommand,
    order_type=OrderType.MOVE,
    category='movement',
    execution_model='action',
    facade_helper_name='dispatch_issue_move',
    serializer_codec='hex_coord',
)
class MoveCommandHandler(BaseCommandHandler):
    """Handler for IssueMoveCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueMoveCommand') -> ValidationResult:
        """Handle IssueMoveCommand."""
        # 1. Resolve Fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validation / Pathfinding
        path = session.preview_fleet_path(fleet, cmd.target_hex)

        if not path:
            if fleet.location == cmd.target_hex:
                return ValidationResult.success()  # Already there - no-op
            else:
                return ValidationResult.error("Target is unreachable or invalid.")

        # 3. Apply
        order = Order(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            # PROJ-370 Phase 2: route through IFleetMutator.
            session.fleet_mutator.set_path(fleet, path)

        return ValidationResult.success()


# NOTE: BuildShipCommandHandler removed in PROJ-208 Phase 2 (dead code).
# Use AddToConstructionQueueCommandHandler instead for all build queue operations.


@command_spec(
    command_class=IssueInterceptCommand,
    order_type=OrderType.MOVE_TO_FLEET,
    category='movement',
    execution_model='action',
    facade_helper_name='dispatch_issue_intercept',
    serializer_codec='fleet_ref',
)
class InterceptCommandHandler(BaseCommandHandler):
    """Handler for IssueInterceptCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueInterceptCommand') -> ValidationResult:
        """Handle IssueInterceptCommand - creates a MOVE_TO_FLEET order."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. PROJ-222: Validate not self-targeting
        if fleet.id == target_fleet.id:
            return ValidationResult.error("Fleet cannot intercept itself.")

        # 4. Create MOVE_TO_FLEET order
        order = Order(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        # 5. PROJ-222: Register as pursuer
        target_fleet.pursuer_tracker.add_pursuer(fleet)

        logger.info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


@command_spec(
    command_class=IssueJoinFleetCommand,
    order_type=OrderType.JOIN_FLEET,
    category='movement',
    execution_model='instant',
    facade_helper_name='dispatch_issue_join_fleet',
    serializer_codec='fleet_ref',
)
class JoinCommandHandler(BaseCommandHandler):
    """Handler for IssueJoinFleetCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueJoinFleetCommand') -> ValidationResult:
        """Handle IssueJoinFleetCommand - creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. PROJ-222: Validate not self-targeting
        if fleet.id == target_fleet.id:
            return ValidationResult.error("Fleet cannot join itself.")

        # 4. PROJ-222: Validate same empire
        if fleet.owner_id != target_fleet.owner_id:
            return ValidationResult.error("Cannot join fleet of another empire.")

        # 5. Create MOVE_TO_FLEET order first
        move_order = Order(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 6. Then create JOIN_FLEET order
        join_order = Order(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        # 7. PROJ-222: Register as pursuer
        target_fleet.pursuer_tracker.add_pursuer(fleet)

        logger.info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


@command_spec(
    command_class=IssueWarpCommand,
    order_type=OrderType.WARP,
    category='movement',
    execution_model='action',
    facade_helper_name='dispatch_issue_warp',
    serializer_codec='hex_coord',
)
class WarpCommandHandler(BaseCommandHandler):
    """Handler for IssueWarpCommand (PROJ-187)."""

    def execute(self, session: 'GameSession', cmd: 'IssueWarpCommand') -> ValidationResult:
        """Handle IssueWarpCommand - creates WARP order with optional MOVE prefix."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate fleet can use warp
        if not fleet.capabilities.can_use_warp():
            limiting_ship = fleet.capabilities.get_warp_limiting_ship()
            if limiting_ship:
                return ValidationResult.error(
                    f"Fleet cannot use warp - {limiting_ship.name} lacks warp capability."
                )
            return ValidationResult.error("Fleet cannot use warp points.")

        # 3. Validate warp point exists at target hex
        warp_point_hex = cmd.warp_point_hex
        source_system = session.galaxy.state.global_hex_warp_points.get(warp_point_hex)
        if not source_system:
            return ValidationResult.error(
                f"No warp point at {warp_point_hex}."
            )

        # 4. If fleet is not at warp point, auto-queue MOVE first (PROJ-204 Phase 3)
        orders_before = len(fleet.orders)
        move_result = add_move_order_if_needed(session, fleet, warp_point_hex)
        if not move_result.is_valid:
            return move_result
        if len(fleet.orders) > orders_before:  # Move was added
            logger.info(f"GameSession: Auto-added MOVE to warp point at {warp_point_hex}")

        # 5. Queue WARP order
        warp_order = Order(OrderType.WARP, target=warp_point_hex)
        fleet.add_order(warp_order)

        logger.info(f"GameSession: Issued WARP order for Fleet {fleet.id} -> {warp_point_hex}")
        return ValidationResult.success()

def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (
        MoveCommandHandler,
        WarpCommandHandler,
        InterceptCommandHandler,
        JoinCommandHandler,
        ColonizeCommandHandler,
    ):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
