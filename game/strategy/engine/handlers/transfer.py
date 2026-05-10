"""Cargo / population transfer command handler.

Single handler, but heavy enough (~95 LOC with logging + cargo projector
dependency) to deserve its own module.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import (
    BaseCommandHandler,
    add_move_order_if_needed,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=IssueTransferCommand,
    order_type=OrderType.TRANSFER,
    category='action',
    execution_model='action',
    facade_helper_name='dispatch_issue_transfer',
    serializer_codec='transfer',
)
class TransferCommandHandler(BaseCommandHandler):
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueTransferCommand') -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations.

        Two target shapes are supported:
        - planet target: ``cmd.planet_id`` set, ``cmd.target_fleet_id`` None.
          Validates against the colony and may auto-queue a MOVE order so the
          fleet arrives at the planet before the TRANSFER executes.
        - fleet target: ``cmd.target_fleet_id`` set, ``cmd.planet_id`` None.
          Validates fleet-to-fleet at the source fleet's current hex; both
          fleets must be co-located (the validator enforces this).

        PROJ-343 T1.1: prior to this fix the handler unconditionally resolved
        ``cmd.planet_id`` and dropped ``target_fleet_id`` from ``transfer_params``,
        breaking fleet-to-fleet transfers entirely.
        """
        from game.strategy.validation import TransferValidator

        logger.info(
            "TransferCommandHandler: fleet_id=%s, planet_id=%s, target_fleet_id=%s, "
            "cargo_type=%s, direction=%s, amount=%s, species_id=%s",
            cmd.fleet_id, cmd.planet_id, cmd.target_fleet_id, cmd.cargo_type,
            cmd.direction, cmd.amount, cmd.species_id,
        )

        # 1. Resolve source fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            logger.warning(f"TransferCommandHandler: Fleet {cmd.fleet_id} not found")
            return error
        logger.info(f"TransferCommandHandler: Fleet {fleet.id} resolved, location={fleet.location}")

        # 2. Resolve target — fleet-to-fleet OR fleet-to-planet
        if cmd.target_fleet_id is not None:
            # Cross-empire fleet-to-fleet is a legitimate cargo path; use
            # `_resolve_fleet(empire_id=None)` per BaseCommandHandler convention.
            target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
            if error:
                return error
            logger.debug(
                "TransferCommandHandler: target Fleet %s resolved, location=%s",
                target_fleet.id, target_fleet.location,
            )
            transfer_target = target_fleet
        else:
            planet, error = self._resolve_planet(session, cmd.planet_id)
            if error:
                return error
            logger.debug(f"TransferCommandHandler: Planet {planet.name} found, owner_id={planet.owner_id}")
            transfer_target = planet

        # 3. Validate (skip location check — we'll auto-add a MOVE order for
        # planet targets; fleet targets are validated at current hex by the
        # validator's fleet-to-fleet branch).
        from game.strategy.services.fleet_cargo_projector import FleetCargoProjector
        projected = FleetCargoProjector.get_projected_cargo(fleet, cmd.cargo_type)
        capacity = fleet.resources.get_fleet_cargo_capacity(cmd.cargo_type)
        current = fleet.resources.get_fleet_cargo_current(cmd.cargo_type)
        logger.debug(f"TransferCommandHandler: cargo capacity={capacity}, current={current}, projected={projected}")

        result = TransferValidator.validate(
            session.galaxy, fleet, transfer_target, cmd.cargo_type, cmd.direction, cmd.amount,
            cmd.species_id, skip_location_check=True, projected_cargo=projected
        )
        logger.debug(f"TransferCommandHandler: validation is_valid={result.is_valid}, error_code={result.error_code}")

        # 4. Apply
        if result.is_valid:
            # Auto-MOVE only applies for planet targets; fleet-to-fleet
            # transfers require co-location and the validator already enforced it.
            if cmd.target_fleet_id is None:
                planet_global_hex = session.galaxy.get_planet_global_hex(transfer_target)
                if planet_global_hex:
                    orders_before = len(fleet.orders)
                    move_result = add_move_order_if_needed(session, fleet, planet_global_hex)
                    if move_result.is_valid and len(fleet.orders) > orders_before:
                        logger.info(f"GameSession: Auto-added MOVE order to {planet_global_hex} for Fleet {fleet.id}")

            # Create TRANSFER order with params dict. T1.1: persist
            # `target_fleet_id` so the order executor (order_processor.py:308)
            # can resolve the target fleet at execution time.
            transfer_params = {
                'direction': cmd.direction,
                'cargo_type': cmd.cargo_type,
                'amount': cmd.amount,
                'planet_id': cmd.planet_id,
                'target_fleet_id': cmd.target_fleet_id,
                'species_id': cmd.species_id,
            }
            order = Order(OrderType.TRANSFER, target=transfer_params)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued TRANSFER order for Fleet {fleet.id}, orders now={len(fleet.orders)}")

        return result


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (TransferCommandHandler,):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
