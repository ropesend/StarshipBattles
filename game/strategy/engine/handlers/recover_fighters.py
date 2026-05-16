"""RecoverFightersCommandHandler — PROJ-FMS-C Phase 3.

Command-side entry point for strategic fighter recovery. Translates an
:class:`IssueRecoverFightersCommand` UI dispatch into an
:class:`OrderType.RECOVER_FIGHTERS` order queued on the issuing fleet.

Mirrors :class:`LaunchFightersCommandHandler` in shape; runtime execution
lives in
:class:`RecoverFightersOrderHandler` (``order_handlers/recover_fighters.py``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueRecoverFightersCommand
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
    command_class=IssueRecoverFightersCommand,
    order_type=OrderType.RECOVER_FIGHTERS,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_recover_fighters',
    serializer_codec='dict',
    # PROJ-FMS-C audit Fix (inline risk): action-time lookup maps to the
    # ``RecoverFighters`` ability on the carrier ship's components.
    # Closes the gating loophole codex flagged.
    action_ability_name='RecoverFighters',
)
class RecoverFightersCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueRecoverFightersCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueRecoverFightersCommand'
    ) -> ValidationResult:
        # 1. Resolve fleet & authorization.
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Deployed groups cannot run recovery actions.
        reject = self._reject_if_non_fleet_group(fleet, "Recover Fighters")
        if reject is not None:
            return reject

        # 3. Find the carrier ship in the fleet.
        carrier = None
        for ship in fleet.ships:
            if str(ship.instance_id) == str(cmd.ship_instance_id):
                carrier = ship
                break
        if carrier is None:
            return ValidationResult.error(
                f"Ship {cmd.ship_instance_id!r} not found in Fleet {fleet.id}."
            )

        # 4. Queue the RECOVER_FIGHTERS order. Detailed validation
        # (specific fighter_group existence, bay capacity, etc.) is
        # deferred to the order handler so this surface stays a thin
        # adapter and partial-recovery semantics live in one place.
        order_target = {
            "ship_instance_id": cmd.ship_instance_id,
            "fighter_group_id": cmd.fighter_group_id,
            "count": cmd.count,
        }
        order = Order(OrderType.RECOVER_FIGHTERS, target=order_target)
        fleet.add_order(order)
        logger.info(
            "RecoverFightersCommandHandler: Fleet %s queued RECOVER_FIGHTERS "
            "group=%s count=%s",
            fleet.id,
            cmd.fighter_group_id,
            cmd.count,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """Register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=RecoverFightersCommandHandler,
        **RecoverFightersCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["RecoverFightersCommandHandler", "register"]
