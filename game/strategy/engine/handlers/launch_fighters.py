"""LaunchFightersCommandHandler — PROJ-FMS-C Phase 1 + QA Observation B.

Translates an :class:`IssueLaunchFightersCommand` UI dispatch into an
:class:`OrderType.LAUNCH_FIGHTERS` order queued on either the issuing
fleet OR the issuing planet (polymorphic via the planet_id field).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLaunchFightersCommand
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import BaseCommandHandler
from game.strategy.engine.handlers.fms_shared import (
    check_issuer_invariant,
    count_matching,
    resolve_requested,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=IssueLaunchFightersCommand,
    order_type=OrderType.LAUNCH_FIGHTERS,
    category='action',
    subcategories=frozenset({"planet_fms"}),
    execution_model='action',
    facade_helper_name='dispatch_issue_launch_fighters',
    serializer_codec='dict',
    action_ability_name='StrategicFighterLaunch',
)
class LaunchFightersCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLaunchFightersCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueLaunchFightersCommand'
    ) -> ValidationResult:
        invariant = check_issuer_invariant(cmd, "Launch Fighters")
        if invariant is not None:
            return invariant
        if cmd.planet_id is not None:
            return self._execute_planet(session, cmd)
        return self._execute_fleet(session, cmd)

    def _execute_fleet(
        self, session: 'GameSession', cmd: 'IssueLaunchFightersCommand'
    ) -> ValidationResult:
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error
        reject = self._reject_if_non_fleet_group(fleet, "Launch Fighters")
        if reject is not None:
            return reject
        if not cmd.ship_instance_id:
            return ValidationResult.error(
                "Launch Fighters (fleet) requires ship_instance_id."
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

        count_available = count_matching(
            carrier.carried_items, "fighter", cmd.fighter_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested
        if count_available <= 0:
            return ValidationResult.error(
                f"No fighters of {cmd.fighter_design_id!r} available to launch."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient fighters: requested {requested} of "
                f"{cmd.fighter_design_id!r}, only {count_available} available."
            )

        target_hex = cmd.target_hex or fleet.location
        order = Order(OrderType.LAUNCH_FIGHTERS, target={
            "ship_instance_id": cmd.ship_instance_id,
            "fighter_design_id": cmd.fighter_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        fleet.add_order(order)
        logger.info(
            "LaunchFightersCommandHandler: Fleet %s queued LAUNCH_FIGHTERS "
            "count=%d design=%s target=%s",
            fleet.id, requested, cmd.fighter_design_id, target_hex,
        )
        return ValidationResult.success()

    def _execute_planet(
        self, session: 'GameSession', cmd: 'IssueLaunchFightersCommand'
    ) -> ValidationResult:
        planet, error = self._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

        count_available = count_matching(
            planet.staging_yard, "fighter", cmd.fighter_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested
        if count_available <= 0:
            return ValidationResult.error(
                f"No fighters of {cmd.fighter_design_id!r} available in "
                f"Planet {planet.name} staging yard."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient fighters on Planet {planet.name}: "
                f"requested {requested} of {cmd.fighter_design_id!r}, "
                f"only {count_available} available."
            )

        target_hex = cmd.target_hex or planet.location
        order = Order(OrderType.LAUNCH_FIGHTERS, target={
            "fighter_design_id": cmd.fighter_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        planet.add_order(order)
        logger.info(
            "LaunchFightersCommandHandler: Planet %s queued LAUNCH_FIGHTERS "
            "count=%d design=%s target=%s",
            planet.id, requested, cmd.fighter_design_id, target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    registry.register(CommandSpec(
        handler_class=LaunchFightersCommandHandler,
        **LaunchFightersCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LaunchFightersCommandHandler", "register"]
