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
from game.strategy.engine.command_handlers import BaseCommandHandler, add_move_order_if_needed

logger = logging.getLogger(__name__)
from game.strategy.data.order_types import FleetOrder, OrderType
from game.strategy.validation import SuperweaponValidator

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


# =============================================================================
# Direct Command Handlers
# =============================================================================

class ImplodePlanetCommandHandler(BaseCommandHandler):
    """Handler for IssueImplodePlanetCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueImplodePlanetCommand - creates IMPLODE_PLANET order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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
        if result.is_valid:
            order = FleetOrder(OrderType.IMPLODE_PLANET, target=planet)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued IMPLODE_PLANET order for Fleet {fleet.id}")

        return result


class StellerateStarCommandHandler(BaseCommandHandler):
    """Handler for IssueStellerateStarCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueStellerateStarCommand - creates STELLERATE_STAR order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_stellerate_star(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )

        # 3. Apply
        if result.is_valid:
            order = FleetOrder(OrderType.STELLERATE_STAR, target=None)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued STELLERATE_STAR order for Fleet {fleet.id}")

        return result


class OpenWarpPointCommandHandler(BaseCommandHandler):
    """Handler for IssueOpenWarpPointCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueOpenWarpPointCommand - creates OPEN_WARP_POINT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_open_warp_point(
            session.galaxy, fleet, cmd.target_system_name,
            component_registry=session.registries.components
        )

        # 3. Apply
        if result.is_valid:
            target_dict = {
                'target_hex': cmd.target_hex,
                'target_system_name': cmd.target_system_name
            }
            order = FleetOrder(OrderType.OPEN_WARP_POINT, target=target_dict)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued OPEN_WARP_POINT order for Fleet {fleet.id}")

        return result


class CloseWarpPointCommandHandler(BaseCommandHandler):
    """Handler for IssueCloseWarpPointCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueCloseWarpPointCommand - creates CLOSE_WARP_POINT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_close_warp_point(
            session.galaxy, fleet, cmd.warp_point_destination_id,
            component_registry=session.registries.components
        )

        # 3. Apply
        if result.is_valid:
            # Store the warp point's sector (hex) for execution-time validation
            target_dict = {
                'destination_id': cmd.warp_point_destination_id,
                'target_hex': {'q': fleet.location.q, 'r': fleet.location.r},
            }
            order = FleetOrder(OrderType.CLOSE_WARP_POINT, target=target_dict)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued CLOSE_WARP_POINT order for Fleet {fleet.id}")

        return result


class CreateDysonSphereCommandHandler(BaseCommandHandler):
    """Handler for IssueCreateDysonSphereCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueCreateDysonSphereCommand - creates CREATE_DYSON_SPHERE order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_create_dyson_sphere(
            session.galaxy, fleet,
            component_registry=session.registries.components
        )

        # 3. Apply
        if result.is_valid:
            order = FleetOrder(OrderType.CREATE_DYSON_SPHERE, target=None)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued CREATE_DYSON_SPHERE order for Fleet {fleet.id}")

        return result


class SelfDestructCommandHandler(BaseCommandHandler):
    """Handler for IssueSelfDestructCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueSelfDestructCommand - creates SELF_DESTRUCT order."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate
        result = SuperweaponValidator.validate_self_destruct(fleet, cmd.ship_ids)

        # 3. Apply
        if result.is_valid:
            order = FleetOrder(OrderType.SELF_DESTRUCT, target=cmd.ship_ids)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued SELF_DESTRUCT order for Fleet {fleet.id}")

        return result


# =============================================================================
# Mission Command Handlers (Move + Action)
# =============================================================================

class ImplodePlanetMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueImplodePlanetMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueImplodePlanetMissionCommand - queues MOVE + IMPLODE_PLANET."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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

        # 5. Queue IMPLODE_PLANET order
        action_order = FleetOrder(OrderType.IMPLODE_PLANET, target=planet)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued IMPLODE_PLANET mission for Fleet {fleet.id}")
        return ValidationResult.success()


class StellerateStarMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueStellerateStarMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueStellerateStarMissionCommand - queues MOVE + STELLERATE_STAR."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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

        # 4. Queue STELLERATE_STAR order
        action_order = FleetOrder(OrderType.STELLERATE_STAR, target=None)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued STELLERATE_STAR mission for Fleet {fleet.id}")
        return ValidationResult.success()


class OpenWarpPointMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueOpenWarpPointMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueOpenWarpPointMissionCommand - queues MOVE + OPEN_WARP_POINT."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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

        # 4. Queue OPEN_WARP_POINT order with target dict
        target_dict = {
            'target_hex': cmd.target_hex,
            'target_system_name': cmd.target_system_name
        }
        action_order = FleetOrder(OrderType.OPEN_WARP_POINT, target=target_dict)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued OPEN_WARP_POINT mission for Fleet {fleet.id}")
        return ValidationResult.success()


class CloseWarpPointMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueCloseWarpPointMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueCloseWarpPointMissionCommand - queues MOVE + CLOSE_WARP_POINT."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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
        target_dict = {
            'destination_id': cmd.warp_point_destination_id,
            'target_hex': {'q': cmd.target_hex.q, 'r': cmd.target_hex.r},
        }
        action_order = FleetOrder(OrderType.CLOSE_WARP_POINT, target=target_dict)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued CLOSE_WARP_POINT mission for Fleet {fleet.id}")
        return ValidationResult.success()


class CreateDysonSphereMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueCreateDysonSphereMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueCreateDysonSphereMissionCommand - queues MOVE + CREATE_DYSON_SPHERE."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
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

        # 4. Queue CREATE_DYSON_SPHERE order
        action_order = FleetOrder(OrderType.CREATE_DYSON_SPHERE, target=None)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued CREATE_DYSON_SPHERE mission for Fleet {fleet.id}")
        return ValidationResult.success()
