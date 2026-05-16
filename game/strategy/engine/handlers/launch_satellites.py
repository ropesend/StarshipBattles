"""LaunchSatellitesCommandHandler — PROJ-FMS-D Phase 1.

Command-side entry point for strategic satellite launching. Mirrors
:class:`LaunchFightersCommandHandler` (PROJ-FMS-C Phase 1) but operates
on satellite CarriedVehicles so a fighter-only carrier cannot
accidentally launch satellites.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLaunchSatellitesCommand
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
    command_class=IssueLaunchSatellitesCommand,
    order_type=OrderType.LAUNCH_SATELLITES,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_launch_satellites',
    serializer_codec='dict',
    # PROJ-FMS-D Phase 1: action-time lookup maps to the
    # ``StrategicSatelliteLaunch`` ability on the carrier ship's
    # components. Mirrors the PROJ-FMS-C audit Fix that closed the
    # gating loophole for the fighter equivalents.
    action_ability_name='StrategicSatelliteLaunch',
)
class LaunchSatellitesCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLaunchSatellitesCommand`."""

    def execute(
        self,
        session: 'GameSession',
        cmd: 'IssueLaunchSatellitesCommand',
    ) -> ValidationResult:
        # 1. Resolve fleet & authorization.
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Deployed groups cannot launch satellites.
        reject = self._reject_if_non_fleet_group(fleet, "Launch Satellites")
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

        # 4. Count available satellites of the requested design.
        wants_any = (
            (not cmd.satellite_design_id)
            or cmd.satellite_design_id == "auto"
        )
        count_available = 0
        for item in carrier.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "satellite":
                continue
            if wants_any or cv.design_id == cmd.satellite_design_id:
                count_available += 1
        if cmd.count <= 0:
            return ValidationResult.error("Satellite launch count must be > 0.")
        if count_available < cmd.count:
            return ValidationResult.error(
                f"Insufficient satellites: requested {cmd.count} of "
                f"{cmd.satellite_design_id!r}, only {count_available} available."
            )

        # 5. Queue the LAUNCH_SATELLITES order on the fleet.
        target_hex = cmd.target_hex or fleet.location
        order_target = {
            "ship_instance_id": cmd.ship_instance_id,
            "satellite_design_id": cmd.satellite_design_id,
            "count": int(cmd.count),
            "target_hex": target_hex,
        }
        order = Order(OrderType.LAUNCH_SATELLITES, target=order_target)
        fleet.add_order(order)
        logger.info(
            "LaunchSatellitesCommandHandler: Fleet %s queued "
            "LAUNCH_SATELLITES count=%d design=%s target=%s",
            fleet.id,
            cmd.count,
            cmd.satellite_design_id,
            target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """Register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=LaunchSatellitesCommandHandler,
        **LaunchSatellitesCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LaunchSatellitesCommandHandler", "register"]
