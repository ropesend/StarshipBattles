"""LaunchFightersCommandHandler — PROJ-FMS-C Phase 1.

Command-side entry point for strategic fighter launching. Translates an
:class:`IssueLaunchFightersCommand` UI dispatch into an
:class:`OrderType.LAUNCH_FIGHTERS` order queued on the issuing fleet.

Mirrors :class:`LayMinesCommandHandler` (PROJ-FMS-B Phase 1) in shape;
runtime execution lives in
:class:`LaunchFightersOrderHandler` (``order_handlers/launch_fighters.py``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLaunchFightersCommand
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
    command_class=IssueLaunchFightersCommand,
    order_type=OrderType.LAUNCH_FIGHTERS,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_launch_fighters',
    serializer_codec='dict',
    # PROJ-FMS-C audit Fix (inline risk): action-time lookup maps to the
    # ``StrategicFighterLaunch`` ability on the carrier ship's components.
    # Closes the gating loophole codex flagged — previously the order
    # type was exempt from the ability-lookup contract and fell through
    # to ``action_time=1`` regardless of which ship was issuing it.
    action_ability_name='StrategicFighterLaunch',
)
class LaunchFightersCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLaunchFightersCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueLaunchFightersCommand'
    ) -> ValidationResult:
        # 1. Resolve fleet & authorization.
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Deployed groups cannot launch fighters (PROJ-FMS-A Phase 4).
        reject = self._reject_if_non_fleet_group(fleet, "Launch Fighters")
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

        # 4. Count available fighters of the requested design.
        wants_any = (not cmd.fighter_design_id) or cmd.fighter_design_id == "auto"
        count_available = 0
        for item in carrier.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "fighter":
                continue
            if wants_any or cv.design_id == cmd.fighter_design_id:
                count_available += 1
        if cmd.count <= 0:
            return ValidationResult.error("Fighter launch count must be > 0.")
        if count_available < cmd.count:
            return ValidationResult.error(
                f"Insufficient fighters: requested {cmd.count} of "
                f"{cmd.fighter_design_id!r}, only {count_available} available."
            )

        # 5. Queue the LAUNCH_FIGHTERS order on the fleet.
        target_hex = cmd.target_hex or fleet.location
        order_target = {
            "ship_instance_id": cmd.ship_instance_id,
            "fighter_design_id": cmd.fighter_design_id,
            "count": int(cmd.count),
            "target_hex": target_hex,
        }
        order = Order(OrderType.LAUNCH_FIGHTERS, target=order_target)
        fleet.add_order(order)
        logger.info(
            "LaunchFightersCommandHandler: Fleet %s queued LAUNCH_FIGHTERS "
            "count=%d design=%s target=%s",
            fleet.id,
            cmd.count,
            cmd.fighter_design_id,
            target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """Register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=LaunchFightersCommandHandler,
        **LaunchFightersCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LaunchFightersCommandHandler", "register"]
