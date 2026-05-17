"""LaunchSatellitesCommandHandler — PROJ-FMS-D Phase 1 + QA Observation B.

Mirrors :class:`LaunchFightersCommandHandler` but for satellites.
Polymorphic across fleet- and planet-issued FMS orders.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLaunchSatellitesCommand
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import BaseCommandHandler
from game.strategy.engine.handlers.fms_shared import (
    check_issuer_invariant,
    count_matching_bay,
    count_matching_yard,
    resolve_requested,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=IssueLaunchSatellitesCommand,
    order_type=OrderType.LAUNCH_SATELLITES,
    category='action',
    subcategories=frozenset({"planet_fms"}),
    execution_model='action',
    facade_helper_name='dispatch_issue_launch_satellites',
    serializer_codec='dict',
    action_ability_name='StrategicSatelliteLaunch',
)
class LaunchSatellitesCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLaunchSatellitesCommand`."""

    def execute(
        self,
        session: 'GameSession',
        cmd: 'IssueLaunchSatellitesCommand',
    ) -> ValidationResult:
        invariant = check_issuer_invariant(cmd, "Launch Satellites")
        if invariant is not None:
            return invariant
        if cmd.planet_id is not None:
            return self._execute_planet(session, cmd)
        return self._execute_fleet(session, cmd)

    def _execute_fleet(
        self, session: 'GameSession', cmd: 'IssueLaunchSatellitesCommand'
    ) -> ValidationResult:
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error
        reject = self._reject_if_non_fleet_group(fleet, "Launch Satellites")
        if reject is not None:
            return reject
        if not cmd.ship_instance_id:
            return ValidationResult.error(
                "Launch Satellites (fleet) requires ship_instance_id."
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

        count_available = count_matching_bay(
            carrier.bay_inventory.bay, "satellite", cmd.satellite_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested
        if count_available <= 0:
            return ValidationResult.error(
                f"No satellites of {cmd.satellite_design_id!r} available "
                f"to launch."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient satellites: requested {requested} of "
                f"{cmd.satellite_design_id!r}, only {count_available} available."
            )

        target_hex = cmd.target_hex or fleet.location
        order = Order(OrderType.LAUNCH_SATELLITES, target={
            "ship_instance_id": cmd.ship_instance_id,
            "satellite_design_id": cmd.satellite_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        fleet.add_order(order)
        logger.info(
            "LaunchSatellitesCommandHandler: Fleet %s queued "
            "LAUNCH_SATELLITES count=%d design=%s target=%s",
            fleet.id, requested, cmd.satellite_design_id, target_hex,
        )
        return ValidationResult.success()

    def _execute_planet(
        self, session: 'GameSession', cmd: 'IssueLaunchSatellitesCommand'
    ) -> ValidationResult:
        planet, error = self._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error
        count_available = count_matching_yard(
            planet.staging_yard, "satellite", cmd.satellite_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested
        if count_available <= 0:
            return ValidationResult.error(
                f"No satellites of {cmd.satellite_design_id!r} available "
                f"in Planet {planet.name} staging yard."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient satellites on Planet {planet.name}: "
                f"requested {requested} of {cmd.satellite_design_id!r}, "
                f"only {count_available} available."
            )
        target_hex = cmd.target_hex or planet.location
        order = Order(OrderType.LAUNCH_SATELLITES, target={
            "satellite_design_id": cmd.satellite_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        planet.add_order(order)
        logger.info(
            "LaunchSatellitesCommandHandler: Planet %s queued "
            "LAUNCH_SATELLITES count=%d design=%s target=%s",
            planet.id, requested, cmd.satellite_design_id, target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    registry.register(CommandSpec(
        handler_class=LaunchSatellitesCommandHandler,
        **LaunchSatellitesCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LaunchSatellitesCommandHandler", "register"]
