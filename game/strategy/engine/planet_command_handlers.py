"""
Planet command handlers for issuing planet orders.

PROJ-237: Handles IssuePlanetOrderCommand, ClearPlanetOrdersCommand,
and DeletePlanetOrderCommand via the command dispatch pipeline.
"""

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType, Order
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
        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        # 3. Parse order type
        try:
            order_type = OrderType[cmd.order_type]
        except KeyError:
            return ValidationResult.error(f"Unknown planet order type: {cmd.order_type}")

        # 4. Validate based on order type
        component_registry = session.registries.components if session.registries else None

        if order_type == OrderType.ACTIVATE_ABILITY:
            if not cmd.ability_name:
                return ValidationResult.error("ability_name is required for ACTIVATE_ABILITY.")
            result = PlanetOrderValidator.validate_activate_ability(
                planet, cmd.facility_instance_id, cmd.ability_name, component_registry,
                component_key=cmd.component_key,
            )
        elif order_type == OrderType.DEACTIVATE_ABILITY:
            if not cmd.ability_name:
                return ValidationResult.error("ability_name is required for DEACTIVATE_ABILITY.")
            result = PlanetOrderValidator.validate_deactivate_ability(
                planet, cmd.facility_instance_id, cmd.ability_name, component_registry,
                component_key=cmd.component_key,
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
        if cmd.ability_name:
            target['ability_name'] = cmd.ability_name
        if cmd.component_key:
            target['component_key'] = cmd.component_key

        order = Order(order_type, target=target)
        planet.add_order(order)

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

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.clear_orders()
        logger.info(f"Planet {planet.name}: all orders cleared")
        return ValidationResult.success()


class DeletePlanetOrderCommandHandler:
    """Handler for DeletePlanetOrderCommand."""

    def execute(self, session: 'GameSession', cmd: 'DeletePlanetOrderCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        if cmd.order_index < 0 or cmd.order_index >= len(planet.orders):
            return ValidationResult.error("Invalid order index.")

        removed = planet.orders.pop(cmd.order_index)
        logger.info(f"Planet {planet.name}: removed order {removed.type.name} at index {cmd.order_index}")
        return ValidationResult.success()


class SetAtmosphereTargetCommandHandler:
    """Handler for SetAtmosphereTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetAtmosphereTargetCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.atmosphere_target = dict(cmd.atmosphere_target)
        if cmd.atmosphere_target:
            logger.info(f"Planet {planet.name}: atmosphere target set ({len(cmd.atmosphere_target)} gases)")
        else:
            logger.info(f"Planet {planet.name}: atmosphere target cleared")
        return ValidationResult.success()


class SetGravityTargetCommandHandler:
    """Handler for SetGravityTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetGravityTargetCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.gravity_target = cmd.gravity_target
        if cmd.gravity_target is not None:
            logger.info(f"Planet {planet.name}: gravity target set to {cmd.gravity_target:.2f} m/s²")
        else:
            logger.info(f"Planet {planet.name}: gravity target cleared")
        return ValidationResult.success()


class SetWaterTargetCommandHandler:
    """Handler for SetWaterTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetWaterTargetCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.water_target = cmd.water_target
        if cmd.water_target is not None:
            logger.info(f"Planet {planet.name}: water target set to {cmd.water_target:.2f}")
        else:
            logger.info(f"Planet {planet.name}: water target cleared")
        return ValidationResult.success()


class SetRadiationShieldTargetCommandHandler:
    """Handler for SetRadiationShieldTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetRadiationShieldTargetCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        if planet.owner_id != session.active_empire.id:
            return ValidationResult.error("Planet does not belong to this empire.")

        planet.radiation_shielding_target = cmd.shielding_target
        if cmd.shielding_target is not None:
            logger.info(f"Planet {planet.name}: radiation shielding target set to {cmd.shielding_target:.2f}")
        else:
            logger.info(f"Planet {planet.name}: radiation shielding target cleared")
        return ValidationResult.success()
