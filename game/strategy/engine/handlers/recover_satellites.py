"""RecoverSatellitesCommandHandler — PROJ-FMS-D Phase 2.

Command-side entry point for strategic satellite recovery. Mirrors
:class:`RecoverFightersCommandHandler` (PROJ-FMS-C Phase 3) but acts on
``satellite_group`` Fleets and requires :class:`RecoverSatellitesAbility`
on the recovering ship.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueRecoverSatellitesCommand
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
    command_class=IssueRecoverSatellitesCommand,
    order_type=OrderType.RECOVER_SATELLITES,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_recover_satellites',
    serializer_codec='dict',
    # PROJ-FMS-D Phase 2: ability-lookup gating mirrors the PROJ-FMS-C
    # audit Fix for fighter recovery. A ship without
    # ``RecoverSatellitesAbility`` cannot recover satellites.
    action_ability_name='RecoverSatellites',
)
class RecoverSatellitesCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueRecoverSatellitesCommand`."""

    def execute(
        self,
        session: 'GameSession',
        cmd: 'IssueRecoverSatellitesCommand',
    ) -> ValidationResult:
        # 1. Resolve fleet & authorization.
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Deployed groups cannot run recovery actions.
        reject = self._reject_if_non_fleet_group(fleet, "Recover Satellites")
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

        # 4. Queue the RECOVER_SATELLITES order. Detailed validation
        # (specific satellite_group existence, bay capacity, etc.) is
        # deferred to the order handler so this surface stays a thin
        # adapter and partial-recovery semantics live in one place.
        order_target = {
            "ship_instance_id": cmd.ship_instance_id,
            "satellite_group_id": cmd.satellite_group_id,
            "count": cmd.count,
        }
        order = Order(OrderType.RECOVER_SATELLITES, target=order_target)
        fleet.add_order(order)
        logger.info(
            "RecoverSatellitesCommandHandler: Fleet %s queued "
            "RECOVER_SATELLITES group=%s count=%s",
            fleet.id,
            cmd.satellite_group_id,
            cmd.count,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """Register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=RecoverSatellitesCommandHandler,
        **RecoverSatellitesCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["RecoverSatellitesCommandHandler", "register"]
