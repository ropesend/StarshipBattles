"""LayMinesCommandHandler — PROJ-FMS-B Phase 1.

Command-side entry point for strategic mine-laying. Translates an
:class:`IssueLayMinesCommand` UI dispatch into an
:class:`OrderType.LAY_MINES` order queued on the issuing fleet.

Mirrors :class:`ColonizeCommandHandler` in shape; runtime execution
lives in :class:`LayMinesOrderHandler` (``order_handlers/lay_mines.py``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLayMinesCommand
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
    command_class=IssueLayMinesCommand,
    order_type=OrderType.LAY_MINES,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_lay_mines',
    serializer_codec='dict',
)
class LayMinesCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLayMinesCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueLayMinesCommand'
    ) -> ValidationResult:
        # 1. Resolve fleet & authorization.
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Deployed groups cannot lay mines (PROJ-FMS-A Phase 4).
        reject = self._reject_if_non_fleet_group(fleet, "Lay Mines")
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

        # 4. Count available mines of the requested design.
        count_available = 0
        for item in carrier.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "mine":
                continue
            if cv.design_id == cmd.mine_design_id:
                count_available += 1
        if cmd.count <= 0:
            return ValidationResult.error("Mine count must be > 0.")
        if count_available < cmd.count:
            return ValidationResult.error(
                f"Insufficient mines: requested {cmd.count} of "
                f"{cmd.mine_design_id!r}, only {count_available} available."
            )

        # 5. Queue the LAY_MINES order on the fleet.
        target_hex = cmd.target_hex or fleet.location
        order_target = {
            "ship_instance_id": cmd.ship_instance_id,
            "mine_design_id": cmd.mine_design_id,
            "count": int(cmd.count),
            "target_hex": target_hex,
        }
        order = Order(OrderType.LAY_MINES, target=order_target)
        fleet.add_order(order)
        logger.info(
            "LayMinesCommandHandler: Fleet %s queued LAY_MINES count=%d design=%s "
            "target=%s",
            fleet.id,
            cmd.count,
            cmd.mine_design_id,
            target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=LayMinesCommandHandler,
        **LayMinesCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LayMinesCommandHandler", "register"]
