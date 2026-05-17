"""RecoverFightersCommandHandler — PROJ-FMS-C Phase 3 + QA Observation B.

Polymorphic across fleet- and planet-issued recovery via the planet_id
field on :class:`IssueRecoverFightersCommand`.
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
from game.strategy.engine.handlers.fms_shared import check_issuer_invariant

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
    action_ability_name='RecoverFighters',
)
class RecoverFightersCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueRecoverFightersCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueRecoverFightersCommand'
    ) -> ValidationResult:
        invariant = check_issuer_invariant(cmd, "Recover Fighters")
        if invariant is not None:
            return invariant
        if cmd.planet_id is not None:
            return self._execute_planet(session, cmd)
        return self._execute_fleet(session, cmd)

    def _execute_fleet(
        self, session: 'GameSession', cmd: 'IssueRecoverFightersCommand'
    ) -> ValidationResult:
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error
        reject = self._reject_if_non_fleet_group(fleet, "Recover Fighters")
        if reject is not None:
            return reject
        if not cmd.ship_instance_id:
            return ValidationResult.error(
                "Recover Fighters (fleet) requires ship_instance_id."
            )
        carrier = None
        for ship in fleet.ships:
            if str(ship.instance_id) == str(cmd.ship_instance_id):
                carrier = ship
                break
        if carrier is None:
            return ValidationResult.error(
                f"Ship {cmd.ship_instance_id!r} not found in Fleet {fleet.id}."
            )

        order = Order(OrderType.RECOVER_FIGHTERS, target={
            "ship_instance_id": cmd.ship_instance_id,
            "fighter_group_id": cmd.fighter_group_id,
            "count": cmd.count,
        })
        fleet.add_order(order)
        logger.info(
            "RecoverFightersCommandHandler: Fleet %s queued RECOVER_FIGHTERS "
            "group=%s count=%s",
            fleet.id, cmd.fighter_group_id, cmd.count,
        )
        return ValidationResult.success()

    def _execute_planet(
        self, session: 'GameSession', cmd: 'IssueRecoverFightersCommand'
    ) -> ValidationResult:
        planet, error = self._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error
        order = Order(OrderType.RECOVER_FIGHTERS, target={
            "fighter_group_id": cmd.fighter_group_id,
            "count": cmd.count,
        })
        planet.add_order(order)
        logger.info(
            "RecoverFightersCommandHandler: Planet %s queued RECOVER_FIGHTERS "
            "group=%s count=%s",
            planet.id, cmd.fighter_group_id, cmd.count,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    registry.register(CommandSpec(
        handler_class=RecoverFightersCommandHandler,
        **RecoverFightersCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["RecoverFightersCommandHandler", "register"]
