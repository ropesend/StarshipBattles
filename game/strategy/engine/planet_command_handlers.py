"""
Planet command handlers for issuing planet orders.

PROJ-237: Handles ClearPlanetOrdersCommand and DeletePlanetOrderCommand
via the command dispatch pipeline.

PROJ-438 Phase 5: typed planet strategic intents
(``ActivatePlanetAbilityCommand`` / ``DeactivatePlanetAbilityCommand``)
replaced the stringly ``IssuePlanetOrderCommand(order_type: str)`` path.
The old class + handler are deleted; each typed command has its own
handler that calls the matching validator and queues the matching
``OrderType``.
"""

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType, Order
from game.strategy.engine.commands import (
    ActivatePlanetAbilityCommand,
    ClearPlanetOrdersCommand,
    DeactivatePlanetAbilityCommand,
    DeletePlanetOrderCommand,
    SetAtmosphereTargetCommand,
    SetGravityTargetCommand,
    SetRadiationShieldTargetCommand,
    SetWaterTargetCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.validation.planet_order_validator import PlanetOrderValidator

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


def _queue_ability_order(
    planet,
    order_type: OrderType,
    facility_instance_id: str,
    ability_name: str,
    component_key: str,
) -> ValidationResult:
    """Shared body for the two typed planet-ability handlers.

    Builds the marker-dict ``target`` payload (preserving the post-load
    rebinding shape) and queues a single ``Order`` on the planet.
    """
    target = {
        'facility_instance_id': facility_instance_id,
        'ability_name': ability_name,
        'component_key': component_key,
    }
    planet.add_order(Order(order_type, target=target))
    logger.info(
        f"Planet {planet.name}: queued {order_type.name} order "
        f"(facility={facility_instance_id})"
    )
    return ValidationResult.success()


@command_spec(
    command_class=ActivatePlanetAbilityCommand,
    order_type=OrderType.ACTIVATE_ABILITY,
    category='planet',
    execution_model='planet',
    facade_helper_name='dispatch_activate_planet_ability',
)
class ActivatePlanetAbilityCommandHandler:
    """Handler for ``ActivatePlanetAbilityCommand`` (PROJ-438 Phase 5)."""

    def execute(
        self,
        session: 'GameSession',
        cmd: 'ActivatePlanetAbilityCommand',
    ) -> ValidationResult:
        from game.strategy.engine.handlers.base import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_player_planet(
            session, cmd.planet_id
        )
        if error:
            return error

        component_registry = (
            session.registries.components if session.registries else None
        )
        result = PlanetOrderValidator.validate_activate_ability(
            planet,
            cmd.facility_instance_id,
            cmd.ability_name,
            component_registry,
            component_key=cmd.component_key,
        )
        if not result.is_valid:
            return result

        return _queue_ability_order(
            planet,
            OrderType.ACTIVATE_ABILITY,
            cmd.facility_instance_id,
            cmd.ability_name,
            cmd.component_key,
        )


@command_spec(
    command_class=DeactivatePlanetAbilityCommand,
    order_type=OrderType.DEACTIVATE_ABILITY,
    category='planet',
    execution_model='planet',
    facade_helper_name='dispatch_deactivate_planet_ability',
)
class DeactivatePlanetAbilityCommandHandler:
    """Handler for ``DeactivatePlanetAbilityCommand`` (PROJ-438 Phase 5)."""

    def execute(
        self,
        session: 'GameSession',
        cmd: 'DeactivatePlanetAbilityCommand',
    ) -> ValidationResult:
        from game.strategy.engine.handlers.base import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_player_planet(
            session, cmd.planet_id
        )
        if error:
            return error

        component_registry = (
            session.registries.components if session.registries else None
        )
        result = PlanetOrderValidator.validate_deactivate_ability(
            planet,
            cmd.facility_instance_id,
            cmd.ability_name,
            component_registry,
            component_key=cmd.component_key,
        )
        if not result.is_valid:
            return result

        return _queue_ability_order(
            planet,
            OrderType.DEACTIVATE_ABILITY,
            cmd.facility_instance_id,
            cmd.ability_name,
            cmd.component_key,
        )


@command_spec(
    command_class=ClearPlanetOrdersCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    facade_helper_name='dispatch_clear_planet_orders',
)
class ClearPlanetOrdersCommandHandler:
    """Handler for ClearPlanetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: 'ClearPlanetOrdersCommand') -> ValidationResult:
        from game.strategy.engine.handlers.base import BaseCommandHandler

        planet, error = BaseCommandHandler._resolve_player_planet(session, cmd.planet_id)
        if error:
            return error

        planet.clear_orders()
        logger.info(f"Planet {planet.name}: all orders cleared")
        return ValidationResult.success()


@command_spec(
    command_class=DeletePlanetOrderCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    facade_helper_name='dispatch_delete_planet_order',
)
class DeletePlanetOrderCommandHandler:
    """Handler for DeletePlanetOrderCommand."""

    def execute(self, session: 'GameSession', cmd: 'DeletePlanetOrderCommand') -> ValidationResult:
        from game.strategy.engine.handlers.base import BaseCommandHandler

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
    from game.strategy.engine.handlers.base import BaseCommandHandler

    planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id)
    if error:
        return error

    setattr(planet, attribute, value)
    is_clear = (value is None) or (isinstance(value, dict) and not value)
    logger.info(f"Planet {planet.name}: {clear_log if is_clear else set_log}")
    return ValidationResult.success()


@command_spec(
    command_class=SetAtmosphereTargetCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    facade_helper_name='dispatch_set_atmosphere_target',
)
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


@command_spec(
    command_class=SetGravityTargetCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    # No facade helper today.
    facade_helper_name=None,
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


@command_spec(
    command_class=SetWaterTargetCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    facade_helper_name=None,
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


@command_spec(
    command_class=SetRadiationShieldTargetCommand,
    order_type=None,
    category='planet',
    execution_model='instant',
    facade_helper_name=None,
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


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (
        ActivatePlanetAbilityCommandHandler,
        DeactivatePlanetAbilityCommandHandler,
        ClearPlanetOrdersCommandHandler,
        DeletePlanetOrderCommandHandler,
        SetAtmosphereTargetCommandHandler,
        SetGravityTargetCommandHandler,
        SetWaterTargetCommandHandler,
        SetRadiationShieldTargetCommandHandler,
    ):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
