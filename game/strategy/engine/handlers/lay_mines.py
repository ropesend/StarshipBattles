"""LayMinesCommandHandler — PROJ-FMS-B Phase 1 + QA Observation B.

Command-side entry point for strategic mine-laying. Translates an
:class:`IssueLayMinesCommand` UI dispatch into an
:class:`OrderType.LAY_MINES` order queued on the issuing fleet OR
planet. Runtime execution lives in
:class:`LayMinesOrderHandler` (``order_handlers/lay_mines.py``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueLayMinesCommand
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
    command_class=IssueLayMinesCommand,
    order_type=OrderType.LAY_MINES,
    category='action',
    subcategories=frozenset({"planet_fms"}),
    execution_model='action',
    facade_helper_name='dispatch_issue_lay_mines',
    serializer_codec='dict',
)
class LayMinesCommandHandler(BaseCommandHandler):
    """Handler for :class:`IssueLayMinesCommand`."""

    def execute(
        self, session: 'GameSession', cmd: 'IssueLayMinesCommand'
    ) -> ValidationResult:
        invariant = check_issuer_invariant(cmd, "Lay Mines")
        if invariant is not None:
            return invariant

        if cmd.planet_id is not None:
            return self._execute_planet(session, cmd)
        return self._execute_fleet(session, cmd)

    # ------------------------------------------------------------------
    # Fleet path
    # ------------------------------------------------------------------

    def _execute_fleet(
        self, session: 'GameSession', cmd: 'IssueLayMinesCommand'
    ) -> ValidationResult:
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error


        if not cmd.ship_instance_id:
            return ValidationResult.error(
                "Lay Mines (fleet) requires ship_instance_id."
            )

        carrier = self._find_ship(fleet, cmd.ship_instance_id)
        if carrier is None:
            return ValidationResult.error(
                f"Ship {cmd.ship_instance_id!r} not found in Fleet {fleet.id}."
            )

        count_available = count_matching_bay(
            carrier.bay_inventory.bay, "mine", cmd.mine_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested

        if count_available <= 0:
            return ValidationResult.error(
                f"No mines of {cmd.mine_design_id!r} available to lay."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient mines: requested {requested} of "
                f"{cmd.mine_design_id!r}, only {count_available} available."
            )

        target_hex = cmd.target_hex or fleet.location
        order = Order(OrderType.LAY_MINES, target={
            "ship_instance_id": cmd.ship_instance_id,
            "mine_design_id": cmd.mine_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        fleet.add_order(order)
        logger.info(
            "LayMinesCommandHandler: Fleet %s queued LAY_MINES count=%d design=%s target=%s",
            fleet.id, requested, cmd.mine_design_id, target_hex,
        )
        return ValidationResult.success()

    # ------------------------------------------------------------------
    # Planet path (QA Observation B)
    # ------------------------------------------------------------------

    def _execute_planet(
        self, session: 'GameSession', cmd: 'IssueLayMinesCommand'
    ) -> ValidationResult:
        planet, error = self._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

        count_available = count_matching_yard(
            planet.staging_yard, "mine", cmd.mine_design_id,
        )
        requested = resolve_requested(cmd.count, count_available)
        if isinstance(requested, ValidationResult):
            return requested
        if count_available <= 0:
            return ValidationResult.error(
                f"No mines of {cmd.mine_design_id!r} available in "
                f"Planet {planet.name} staging yard."
            )
        if count_available < requested:
            return ValidationResult.error(
                f"Insufficient mines on Planet {planet.name}: "
                f"requested {requested} of {cmd.mine_design_id!r}, "
                f"only {count_available} available."
            )

        target_hex = cmd.target_hex or planet.location
        order = Order(OrderType.LAY_MINES, target={
            "mine_design_id": cmd.mine_design_id,
            "count": requested,
            "target_hex": target_hex,
        })
        planet.add_order(order)
        logger.info(
            "LayMinesCommandHandler: Planet %s queued LAY_MINES count=%d design=%s target=%s",
            planet.id, requested, cmd.mine_design_id, target_hex,
        )
        return ValidationResult.success()


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    registry.register(CommandSpec(
        handler_class=LayMinesCommandHandler,
        **LayMinesCommandHandler.__command_spec_kwargs__,
    ))


__all__ = ["LayMinesCommandHandler", "register"]
