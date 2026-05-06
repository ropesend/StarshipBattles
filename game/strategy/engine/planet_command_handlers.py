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

        # 1. Resolve + authorize (PROJ-375 DUP-X-01)
        planet, error = BaseCommandHandler._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

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

        planet, error = BaseCommandHandler._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

        planet.clear_orders()
        logger.info(f"Planet {planet.name}: all orders cleared")
        return ValidationResult.success()


class DeletePlanetOrderCommandHandler:
    """Handler for DeletePlanetOrderCommand."""

    def execute(self, session: 'GameSession', cmd: 'DeletePlanetOrderCommand') -> ValidationResult:
        from game.strategy.engine.command_handlers import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

        if cmd.order_index < 0 or cmd.order_index >= len(planet.orders):
            return ValidationResult.error("Invalid order index.")

        removed = planet.orders.pop(cmd.order_index)
        logger.info(f"Planet {planet.name}: removed order {removed.type.name} at index {cmd.order_index}")
        return ValidationResult.success()


def _apply_planet_environmental_target(
    session: 'GameSession',
    planet_id: int,
    attribute: str,
    value,
    set_log: str,
    clear_log: str,
) -> ValidationResult:
    """Shared body for the 4 SetXTarget handlers (PROJ-375 Cluster 5).

    Resolves + authorizes the planet, sets the named attribute, and emits a
    set/clear log line. Returns success or the resolution error.

    Args:
        session: Active game session.
        planet_id: Planet ID from the command.
        attribute: Planet attribute name to assign (e.g. 'atmosphere_target').
        value: Value to assign — set-vs-clear is decided by the call site
            (atmosphere uses `dict(...)` always, others may pass None).
        set_log: Log message for the "set" branch (planet name prepended).
        clear_log: Log message for the "clear" branch.
    """
    from game.strategy.engine.command_handlers import BaseCommandHandler

    planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id)
    if error:
        return error

    setattr(planet, attribute, value)
    is_clear = (value is None) or (isinstance(value, dict) and not value)
    logger.info(f"Planet {planet.name}: {clear_log if is_clear else set_log}")
    return ValidationResult.success()


class SetAtmosphereTargetCommandHandler:
    """Handler for SetAtmosphereTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetAtmosphereTargetCommand') -> ValidationResult:
        target = dict(cmd.atmosphere_target) if cmd.atmosphere_target else {}
        gases = len(target)
        return _apply_planet_environmental_target(
            session, cmd.planet_id,
            attribute='atmosphere_target',
            value=target,
            set_log=f"atmosphere target set ({gases} gases)",
            clear_log="atmosphere target cleared",
        )


class SetGravityTargetCommandHandler:
    """Handler for SetGravityTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetGravityTargetCommand') -> ValidationResult:
        return _apply_planet_environmental_target(
            session, cmd.planet_id,
            attribute='gravity_target',
            value=cmd.gravity_target,
            set_log=(
                f"gravity target set to {cmd.gravity_target:.2f} m/s²"
                if cmd.gravity_target is not None else ""
            ),
            clear_log="gravity target cleared",
        )


class SetWaterTargetCommandHandler:
    """Handler for SetWaterTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetWaterTargetCommand') -> ValidationResult:
        return _apply_planet_environmental_target(
            session, cmd.planet_id,
            attribute='water_target',
            value=cmd.water_target,
            set_log=(
                f"water target set to {cmd.water_target:.2f}"
                if cmd.water_target is not None else ""
            ),
            clear_log="water target cleared",
        )


class SetRadiationShieldTargetCommandHandler:
    """Handler for SetRadiationShieldTargetCommand."""

    def execute(self, session: 'GameSession', cmd: 'SetRadiationShieldTargetCommand') -> ValidationResult:
        return _apply_planet_environmental_target(
            session, cmd.planet_id,
            attribute='radiation_shielding_target',
            value=cmd.shielding_target,
            set_log=(
                f"radiation shielding target set to {cmd.shielding_target:.2f}"
                if cmd.shielding_target is not None else ""
            ),
            clear_log="radiation shielding target cleared",
        )
