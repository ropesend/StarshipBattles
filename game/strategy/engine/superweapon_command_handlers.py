"""
Superweapon Command Handlers - Strategy Command Dispatch

PROJ-102 Phase 5: Command handlers for superweapon orders.
Each handler wires a command to its validator and creates the appropriate fleet order.

Usage:
    handler = ImplodePlanetCommandHandler()
    result = handler.execute(session, command)
"""
from typing import Any, TYPE_CHECKING
import logging

from game.core.validation import ValidationResult
from game.strategy.engine.handlers.base import BaseCommandHandler, add_move_order_if_needed

logger = logging.getLogger(__name__)
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import (
    IssueCloseWarpPointCommand,
    IssueCreateDysonSphereCommand,
    IssueImplodePlanetCommand,
    IssueOpenWarpPointCommand,
    IssueSelfDestructCommand,
    IssueStellerateStarCommand,
    QueueCloseWarpPointMissionCommand,
    QueueCreateDysonSphereMissionCommand,
    QueueImplodePlanetMissionCommand,
    QueueOpenWarpPointMissionCommand,
    QueueStellerateStarMissionCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.validation import SuperweaponValidator

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


# =============================================================================
# Direct Command Handlers
# =============================================================================

@command_spec(
    command_class=IssueImplodePlanetCommand,
    order_type=OrderType.IMPLODE_PLANET,
    category='superweapon',
    action_ability_name='DestroyPlanet',
    execution_model='action',
    facade_helper_name='dispatch_issue_implode_planet',
    serializer_codec='planet_ref',
)
class ImplodePlanetCommandHandler(BaseCommandHandler):
    """Handler for IssueImplodePlanetCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueImplodePlanetCommand') -> ValidationResult:
        """Handle IssueImplodePlanetCommand - creates IMPLODE_PLANET order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve planet
        planet, error = self._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        # 3. Validate
        result = SuperweaponValidator.validate_implode_planet(
            session.galaxy, fleet, planet,
            component_registry=session.registries.components
        )

        # 4. Apply
        return self._emit_validated_order(
            fleet, OrderType.IMPLODE_PLANET, planet, result, "IMPLODE_PLANET",
        )


@command_spec(
    command_class=IssueStellerateStarCommand,
    order_type=OrderType.STELLERATE_STAR,
    category='superweapon',
    action_ability_name='DestroyStar',
    execution_model='action',
    facade_helper_name='dispatch_issue_stellerate_star',
)
class StellerateStarCommandHandler(BaseCommandHandler):
    """Handler for IssueStellerateStarCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueStellerateStarCommand') -> ValidationResult:
        """Handle IssueStellerateStarCommand - creates STELLERATE_STAR order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_stellerate_star(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )

        # 3. Apply
        return self._emit_validated_order(
            fleet, OrderType.STELLERATE_STAR, None, result, "STELLERATE_STAR",
        )


@command_spec(
    command_class=IssueOpenWarpPointCommand,
    order_type=OrderType.OPEN_WARP_POINT,
    category='superweapon',
    action_ability_name='OpenWarpPoint',
    execution_model='action',
    facade_helper_name='dispatch_issue_open_warp_point',
    serializer_codec='warp_params',
)
class OpenWarpPointCommandHandler(BaseCommandHandler):
    """Handler for IssueOpenWarpPointCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueOpenWarpPointCommand') -> ValidationResult:
        """Handle IssueOpenWarpPointCommand - creates OPEN_WARP_POINT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_open_warp_point(
            session.galaxy, fleet, cmd.target_system_name,
            component_registry=session.registries.components
        )

        # 3. Apply
        target_dict = {
            'target_hex': cmd.target_hex,
            'target_system_name': cmd.target_system_name,
        }
        return self._emit_validated_order(
            fleet, OrderType.OPEN_WARP_POINT, target_dict, result, "OPEN_WARP_POINT",
        )


@command_spec(
    command_class=IssueCloseWarpPointCommand,
    order_type=OrderType.CLOSE_WARP_POINT,
    category='superweapon',
    action_ability_name='CloseWarpPoint',
    execution_model='action',
    facade_helper_name='dispatch_issue_close_warp_point',
    serializer_codec='warp_params',
)
class CloseWarpPointCommandHandler(BaseCommandHandler):
    """Handler for IssueCloseWarpPointCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueCloseWarpPointCommand') -> ValidationResult:
        """Handle IssueCloseWarpPointCommand - creates CLOSE_WARP_POINT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_close_warp_point(
            session.galaxy, fleet, cmd.warp_point_destination_id,
            component_registry=session.registries.components
        )

        # 3. Apply — store the warp point's sector (hex) for execution-time validation
        target_dict = {
            'destination_id': cmd.warp_point_destination_id,
            'target_hex': {'q': fleet.location.q, 'r': fleet.location.r},
        }
        return self._emit_validated_order(
            fleet, OrderType.CLOSE_WARP_POINT, target_dict, result, "CLOSE_WARP_POINT",
        )


@command_spec(
    command_class=IssueCreateDysonSphereCommand,
    order_type=OrderType.CREATE_DYSON_SPHERE,
    category='superweapon',
    action_ability_name='CreateDysonSphere',
    execution_model='action',
    facade_helper_name='dispatch_issue_create_dyson_sphere',
)
class CreateDysonSphereCommandHandler(BaseCommandHandler):
    """Handler for IssueCreateDysonSphereCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueCreateDysonSphereCommand') -> ValidationResult:
        """Handle IssueCreateDysonSphereCommand - creates CREATE_DYSON_SPHERE order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_create_dyson_sphere(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )

        # 3. Apply
        return self._emit_validated_order(
            fleet, OrderType.CREATE_DYSON_SPHERE, None, result, "CREATE_DYSON_SPHERE",
        )


@command_spec(
    command_class=IssueSelfDestructCommand,
    order_type=OrderType.SELF_DESTRUCT,
    category='superweapon',
    action_ability_name='SelfDestruct',
    execution_model='action',
    facade_helper_name='dispatch_issue_self_destruct',
    serializer_codec='ship_id_list',
)
class SelfDestructCommandHandler(BaseCommandHandler):
    """Handler for IssueSelfDestructCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueSelfDestructCommand') -> ValidationResult:
        """Handle IssueSelfDestructCommand - creates SELF_DESTRUCT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_self_destruct(fleet, cmd.ship_ids)

        # 3. Apply
        return self._emit_validated_order(
            fleet, OrderType.SELF_DESTRUCT, cmd.ship_ids, result, "SELF_DESTRUCT",
        )


# =============================================================================
# Mission Command Handlers (Move + Action)
# =============================================================================

@command_spec(
    command_class=QueueImplodePlanetMissionCommand,
    order_type=None,
    category='superweapon',
    execution_model='mission',
    facade_helper_name='dispatch_queue_implode_planet_mission',
)
class ImplodePlanetMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueImplodePlanetMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueImplodePlanetMissionCommand') -> ValidationResult:
        """Handle QueueImplodePlanetMissionCommand - queues MOVE + IMPLODE_PLANET."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve planet
        planet, error = self._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        # 3. Validate ability
        result = SuperweaponValidator.validate_implode_planet(
            session.galaxy, fleet, planet,
            component_registry=session.registries.components
        )
        if not result.is_valid:
            return result

        # 4. Setup move
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 5. Queue IMPLODE_PLANET order (PROJ-375 review MIN-001)
        return self._emit_validated_order(
            fleet, OrderType.IMPLODE_PLANET, planet, result, "IMPLODE_PLANET mission",
        )


@command_spec(
    command_class=QueueStellerateStarMissionCommand,
    order_type=None,
    category='superweapon',
    execution_model='mission',
    facade_helper_name='dispatch_queue_stellerate_star_mission',
)
class StellerateStarMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueStellerateStarMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueStellerateStarMissionCommand') -> ValidationResult:
        """Handle QueueStellerateStarMissionCommand - queues MOVE + STELLERATE_STAR."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ability
        result = SuperweaponValidator.validate_stellerate_star(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue STELLERATE_STAR order (PROJ-375 Task 2.4)
        return self._emit_validated_order(
            fleet, OrderType.STELLERATE_STAR, None, result, "STELLERATE_STAR mission",
        )


@command_spec(
    command_class=QueueOpenWarpPointMissionCommand,
    order_type=None,
    category='superweapon',
    execution_model='mission',
    facade_helper_name='dispatch_queue_open_warp_point_mission',
)
class OpenWarpPointMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueOpenWarpPointMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueOpenWarpPointMissionCommand') -> ValidationResult:
        """Handle QueueOpenWarpPointMissionCommand - queues MOVE + OPEN_WARP_POINT."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ability (skip location check — fleet will move there first)
        result = SuperweaponValidator.validate_open_warp_point(
            session.galaxy, fleet, cmd.target_system_name,
            component_registry=session.registries.components,
            skip_location_check=True
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue OPEN_WARP_POINT order with target dict (PROJ-375 Task 2.4)
        target_dict = {
            'target_hex': cmd.target_hex,
            'target_system_name': cmd.target_system_name
        }
        return self._emit_validated_order(
            fleet, OrderType.OPEN_WARP_POINT, target_dict, result, "OPEN_WARP_POINT mission",
        )


@command_spec(
    command_class=QueueCloseWarpPointMissionCommand,
    order_type=None,
    category='superweapon',
    execution_model='mission',
    facade_helper_name='dispatch_queue_close_warp_point_mission',
)
class CloseWarpPointMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueCloseWarpPointMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueCloseWarpPointMissionCommand') -> ValidationResult:
        """Handle QueueCloseWarpPointMissionCommand - queues MOVE + CLOSE_WARP_POINT."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ability (skip location check — fleet will move there first)
        result = SuperweaponValidator.validate_close_warp_point(
            session.galaxy, fleet, cmd.warp_point_destination_id,
            component_registry=session.registries.components,
            skip_location_check=True
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue CLOSE_WARP_POINT order with target sector for execution-time validation
        # (PROJ-375 Task 2.4)
        target_dict = {
            'destination_id': cmd.warp_point_destination_id,
            'target_hex': {'q': cmd.target_hex.q, 'r': cmd.target_hex.r},
        }
        return self._emit_validated_order(
            fleet, OrderType.CLOSE_WARP_POINT, target_dict, result, "CLOSE_WARP_POINT mission",
        )


@command_spec(
    command_class=QueueCreateDysonSphereMissionCommand,
    order_type=None,
    category='superweapon',
    execution_model='mission',
    facade_helper_name='dispatch_queue_create_dyson_sphere_mission',
)
class CreateDysonSphereMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueCreateDysonSphereMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueCreateDysonSphereMissionCommand') -> ValidationResult:
        """Handle QueueCreateDysonSphereMissionCommand - queues MOVE + CREATE_DYSON_SPHERE."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ability
        result = SuperweaponValidator.validate_create_dyson_sphere(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue CREATE_DYSON_SPHERE order (PROJ-375 Task 2.4)
        return self._emit_validated_order(
            fleet, OrderType.CREATE_DYSON_SPHERE, None, result, "CREATE_DYSON_SPHERE mission",
        )


def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (
        ImplodePlanetCommandHandler,
        StellerateStarCommandHandler,
        OpenWarpPointCommandHandler,
        CloseWarpPointCommandHandler,
        CreateDysonSphereCommandHandler,
        SelfDestructCommandHandler,
        ImplodePlanetMissionCommandHandler,
        StellerateStarMissionCommandHandler,
        OpenWarpPointMissionCommandHandler,
        CloseWarpPointMissionCommandHandler,
        CreateDysonSphereMissionCommandHandler,
    ):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
