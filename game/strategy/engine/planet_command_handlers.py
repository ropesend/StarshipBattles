"""
Planet command handlers for issuing planet orders.

PROJ-237: Handles IssuePlanetOrderCommand, ClearPlanetOrdersCommand,
and DeletePlanetOrderCommand via the command dispatch pipeline.
"""

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.planet_order_types import PlanetOrderType, PlanetOrder
from game.strategy.validation.planet_order_validator import PlanetOrderValidator

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.commands import (
        IssuePlanetOrderCommand,
        ClearPlanetOrdersCommand,
        DeletePlanetOrderCommand,
    )


class IssuePlanetOrderCommandHandler:
    """Handler for IssuePlanetOrderCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssuePlanetOrderCommand') -> ValidationResult:
        """Issue a planet order (e.g., activate/deactivate shield).

        Args:
            session: Active game session.
            cmd: Command with planet_id, order_type, facility_instance_id.

        Returns:
            ValidationResult indicating success or failure.
        """
        from game.strategy.engine.command_handlers import BaseCommandHandler

        # 1. Resolve planet
        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        # 2. Validate ownership
        if planet.owner_id != session.player_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        # 3. Parse order type
        try:
            order_type = PlanetOrderType[cmd.order_type]
        except KeyError:
            return ValidationResult.error(f"Unknown planet order type: {cmd.order_type}")

        # 4. Validate based on order type
        component_registry = session.registries.components if session.registries else None

        if order_type == PlanetOrderType.ACTIVATE_SHIELD:
            result = PlanetOrderValidator.validate_activate_shield(
                planet, cmd.facility_instance_id, component_registry
            )
        elif order_type == PlanetOrderType.DEACTIVATE_SHIELD:
            result = PlanetOrderValidator.validate_deactivate_shield(
                planet, cmd.facility_instance_id, component_registry
            )
        else:
            return ValidationResult.error(f"Unsupported planet order type: {cmd.order_type}")

        if not result.is_valid:
            return result

        # 5. Create and queue the order
        target = {
            'facility_instance_id': cmd.facility_instance_id,
        }
        if cmd.component_id:
            target['component_id'] = cmd.component_id

        order = PlanetOrder(order_type, target=target)
        planet.add_planet_order(order)

        logger.info(
            f"Planet {planet.name}: queued {order_type.name} order "
            f"(facility={cmd.facility_instance_id})"
        )
        return ValidationResult.success()


class ClearPlanetOrdersCommandHandler:
    """Handler for ClearPlanetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: 'ClearPlanetOrdersCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.player_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.clear_planet_orders()
        logger.info(f"Planet {planet.name}: all orders cleared")
        return ValidationResult.success()


class DeletePlanetOrderCommandHandler:
    """Handler for DeletePlanetOrderCommand."""

    def execute(self, session: 'GameSession', cmd: 'DeletePlanetOrderCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.player_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        if cmd.order_index < 0 or cmd.order_index >= len(planet.planet_orders):
            return ValidationResult.error("Invalid order index.")

        removed = planet.planet_orders.pop(cmd.order_index)
        logger.info(f"Planet {planet.name}: removed order {removed.type.name} at index {cmd.order_index}")
        return ValidationResult.success()
