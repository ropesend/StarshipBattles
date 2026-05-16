"""Fleet BUILD-order toggling — in-fleet construction.

Owns: BuildOrder, RemoveBuildOrder.

These two handlers manage the BUILD order on a fleet, which keeps the fleet
stationary while it constructs items from its own construction queue.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import (
    IssueBuildOrderCommand,
    RemoveBuildOrderCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import BaseCommandHandler

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=IssueBuildOrderCommand,
    order_type=OrderType.BUILD,
    category='build',
    execution_model='production',
    facade_helper_name='dispatch_issue_build_order',
)
class BuildOrderCommandHandler(BaseCommandHandler):
    """Handler for IssueBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: 'IssueBuildOrderCommand') -> ValidationResult:
        """Handle IssueBuildOrderCommand - creates BUILD order for fleet construction.

        Inserts BUILD order at position 0 (front of queue) so it executes first.
        Clears the fleet path since fleet must stay stationary to build.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # PROJ-FMS-A Phase 4: deployed groups have no build queue.
        reject = self._reject_if_non_fleet_group(fleet, "Build Order")
        if reject is not None:
            return reject

        # 2. Create BUILD order and insert at front
        build_order = Order(OrderType.BUILD)
        # PROJ-370 Phase 2: route order insertion through IFleetMutator.
        session.fleet_mutator.insert_order(fleet, 0, build_order)

        # 3. Clear movement path - fleet must stay stationary to build
        session.fleet_mutator.set_path(fleet, [])

        logger.info(f"GameSession: Issued BUILD order for Fleet {fleet.id}")
        return ValidationResult.success()


@command_spec(
    command_class=RemoveBuildOrderCommand,
    order_type=None,
    category='build',
    execution_model='instant',
    facade_helper_name='dispatch_remove_build_order',
)
class RemoveBuildOrderCommandHandler(BaseCommandHandler):
    """Handler for RemoveBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: 'RemoveBuildOrderCommand') -> ValidationResult:
        """Handle RemoveBuildOrderCommand - removes BUILD orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Remove all BUILD orders (PROJ-222: use Fleet API for consistency)
        fleet.remove_orders_by_type(OrderType.BUILD)

        logger.info(f"GameSession: Removed BUILD orders from Fleet {fleet.id}")
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (BuildOrderCommandHandler, RemoveBuildOrderCommandHandler):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
