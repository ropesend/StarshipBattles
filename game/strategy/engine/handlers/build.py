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
from game.strategy.engine.handlers.base import BaseCommandHandler

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.commands import (
        IssueBuildOrderCommand,
        RemoveBuildOrderCommand,
    )
    from game.strategy.engine.game_session import GameSession


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

        # 2. Create BUILD order and insert at front
        build_order = Order(OrderType.BUILD)
        fleet.orders.insert(0, build_order)

        # 3. Clear movement path - fleet must stay stationary to build
        fleet.path = []

        logger.info(f"GameSession: Issued BUILD order for Fleet {fleet.id}")
        return ValidationResult.success()


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
