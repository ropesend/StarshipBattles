"""Cargo / population transfer command handler.

Single handler, but heavy enough (~95 LOC with logging + cargo projector
dependency) to deserve its own module.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.handlers.base import (
    BaseCommandHandler,
    add_move_order_if_needed,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.commands import IssueTransferCommand
    from game.strategy.engine.game_session import GameSession


class TransferCommandHandler(BaseCommandHandler):
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueTransferCommand') -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations."""
        from game.strategy.validation import TransferValidator

        logger.info(f"TransferCommandHandler: fleet_id={cmd.fleet_id}, planet_id={cmd.planet_id}, cargo_type={cmd.cargo_type}, direction={cmd.direction}, amount={cmd.amount}, species_id={cmd.species_id}")

        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id, empire_id=cmd.empire_id)
        if error:
            logger.warning(f"TransferCommandHandler: Fleet {cmd.fleet_id} not found")
            return error
        logger.info(f"TransferCommandHandler: Fleet {fleet.id} resolved, location={fleet.location}")

        # 2. Find owning empire (PROJ-204: O(1) lookup via owner_id instead of O(N) loop)
        if fleet.owner_id < 0 or fleet.owner_id >= len(session.empires):
            return ValidationResult.error("Fleet owner not found.")
        owning_empire = session.empires[fleet.owner_id]

        # 3. Resolve planet
        planet, error = self._resolve_planet(session, cmd.planet_id)
        if error:
            return error
        logger.debug(f"TransferCommandHandler: Planet {planet.name} found, owner_id={planet.owner_id}")

        # 4. Validate (skip location check — we'll auto-add a MOVE order)
        # Use projected cargo to account for earlier queued orders
        from game.strategy.services.fleet_cargo_projector import FleetCargoProjector
        projected = FleetCargoProjector.get_projected_cargo(fleet, cmd.cargo_type)
        capacity = fleet.resources.get_fleet_cargo_capacity(cmd.cargo_type)
        current = fleet.resources.get_fleet_cargo_current(cmd.cargo_type)
        logger.debug(f"TransferCommandHandler: cargo capacity={capacity}, current={current}, projected={projected}")

        result = TransferValidator.validate(
            session.galaxy, fleet, planet, cmd.cargo_type, cmd.direction, cmd.amount,
            cmd.species_id, skip_location_check=True, projected_cargo=projected
        )
        logger.debug(f"TransferCommandHandler: validation is_valid={result.is_valid}, error_code={result.error_code}")

        # 5. Apply
        if result.is_valid:
            # Find planet's global hex for MOVE order
            planet_global_hex = session.galaxy.get_planet_global_hex(planet)

            # PROJ-204 Phase 3: Use helper for auto-move
            if planet_global_hex:
                orders_before = len(fleet.orders)
                move_result = add_move_order_if_needed(session, fleet, planet_global_hex)
                if move_result.is_valid and len(fleet.orders) > orders_before:
                    logger.info(f"GameSession: Auto-added MOVE order to {planet_global_hex} for Fleet {fleet.id}")

            # Create TRANSFER order with params dict
            transfer_params = {
                'direction': cmd.direction,
                'cargo_type': cmd.cargo_type,
                'amount': cmd.amount,
                'planet_id': cmd.planet_id,
                'species_id': cmd.species_id
            }
            order = Order(OrderType.TRANSFER, target=transfer_params)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued TRANSFER order for Fleet {fleet.id}, orders now={len(fleet.orders)}")

        return result
