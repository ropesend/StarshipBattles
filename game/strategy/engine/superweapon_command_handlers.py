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
from game.strategy.engine.command_handlers import BaseCommandHandler

logger = logging.getLogger(__name__)
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex
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
            component_registry=session.turn_engine._registries.components
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
            component_registry=session.turn_engine._registries.components
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
            component_registry=session.turn_engine._registries.components
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
            component_registry=session.turn_engine._registries.components
        )

        # 3. Apply
        if result.is_valid:
            order = FleetOrder(OrderType.CLOSE_WARP_POINT, target=cmd.warp_point_destination_id)
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
            component_registry=session.turn_engine._registries.components
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

def _setup_mission_move(session: 'GameSession', fleet, target_hex) -> ValidationResult:
    """Shared setup logic for mission commands: calculate path and queue MOVE order.

    Determines the start hex based on existing orders, calculates the path,
    and queues a MOVE order if the fleet is not already at the target.

    Args:
        session: GameSession for path calculation.
        fleet: Fleet to move.
        target_hex: Destination hex coordinate.

    Returns:
        ValidationResult - invalid if no path found, valid otherwise.
    """
    # Determine start hex from last MOVE order if any
    start_hex = fleet.location
    if fleet.orders:
        last = fleet.orders[-1]
        if last.type == OrderType.MOVE:
            start_hex = last.target

    # Calculate path
    path = find_hybrid_path(session.galaxy, start_hex, target_hex)
    if not path:
        return ValidationResult.error("No path found to target.")

    # Queue MOVE order if not already at target
    if start_hex != target_hex:
        move_order = FleetOrder(OrderType.MOVE, target=target_hex)
        fleet.add_order(move_order)

        # PROJ-204: Set path immediately if it's the first order
        if len(fleet.orders) == 1:
            fleet.path = strip_start_hex(fleet.location, path)

    return ValidationResult.success()


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
            component_registry=session.turn_engine._registries.components
        )
        if not result.is_valid:
            return result

        # 4. Setup move
        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
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
            component_registry=session.turn_engine._registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
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

        # 2. Validate ability
        result = SuperweaponValidator.validate_open_warp_point(
            session.galaxy, fleet, cmd.target_system_name,
            component_registry=session.turn_engine._registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
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

        # 2. Validate ability
        result = SuperweaponValidator.validate_close_warp_point(
            session.galaxy, fleet, cmd.warp_point_destination_id,
            component_registry=session.turn_engine._registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue CLOSE_WARP_POINT order
        action_order = FleetOrder(OrderType.CLOSE_WARP_POINT, target=cmd.warp_point_destination_id)
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
            component_registry=session.turn_engine._registries.components
        )
        if not result.is_valid:
            return result

        # 3. Setup move
        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 4. Queue CREATE_DYSON_SPHERE order
        action_order = FleetOrder(OrderType.CREATE_DYSON_SPHERE, target=None)
        fleet.add_order(action_order)

        logger.info(f"GameSession: Queued CREATE_DYSON_SPHERE mission for Fleet {fleet.id}")
        return ValidationResult.success()
