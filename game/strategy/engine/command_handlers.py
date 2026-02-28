"""
Command Handler Registry - Strategy Command Dispatch

This module extracts command handling logic from GameSession into a registry-based
dispatch pattern. Each command type has a dedicated handler class implementing
the ICommandHandler protocol.

Extracted in PROJ-87 Phase 5 for maintainability and extensibility.

Usage:
    registry = CommandHandlerRegistry()
    registry.register('IssueColonizeCommand', ColonizeCommandHandler())
    result = registry.dispatch('IssueColonizeCommand', session, command)
"""
from typing import Protocol, Dict, Any, TYPE_CHECKING, runtime_checkable
import logging

from game.core.validation import ValidationResult
from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex
from game.strategy.data.order_types import FleetOrder, OrderType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


def add_move_order_if_needed(
    session: 'GameSession',
    fleet,
    target_hex,
    start_hex=None
) -> ValidationResult:
    """Add a MOVE order to fleet if not already at target hex.

    PROJ-204 Phase 3: Extracted from duplicate patterns in command handlers.
    PROJ-207 Phase 5: Added start_hex for chain-aware path calculation.

    Use this when a command needs to auto-queue movement before an action.

    Args:
        session: GameSession for path calculation.
        fleet: Fleet to potentially move.
        target_hex: Destination hex coordinate.
        start_hex: Optional starting hex for path calculation. If None,
                   calculates chain-aware start (last MOVE target or fleet.location).

    Returns:
        ValidationResult - invalid if no path found, valid otherwise.
    """
    # Determine start hex (chain-aware)
    if start_hex is None:
        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

    # Already at target - no move needed
    if start_hex == target_hex:
        return ValidationResult.success()

    # Calculate path from chain-aware start
    path = find_hybrid_path(session.galaxy, start_hex, target_hex)
    if not path:
        return ValidationResult.error("No path found to target.")

    # Queue MOVE order
    move_order = FleetOrder(OrderType.MOVE, target=target_hex)
    fleet.add_order(move_order)

    # Set path immediately if it's the first order and fleet is at start
    if len(fleet.orders) == 1 and fleet.location == start_hex:
        fleet.path = strip_start_hex(fleet.location, path)

    return ValidationResult.success()


def create_auto_load_population_order(origin_colony) -> 'FleetOrder':
    """Create a LOAD_POPULATION order to pick up founding population from colony.

    PROJ-207 Phase 4: Extracted from duplicate patterns in ColonizeCommandHandler
    and ColonizeMissionCommandHandler. Use this when auto-loading colonists
    from a colony at the fleet's location.

    Args:
        origin_colony: The colony to load population from.

    Returns:
        FleetOrder for LOAD_POPULATION, or None if colony has no populations.
    """
    if not origin_colony or not origin_colony.populations:
        return None

    species_id = origin_colony.populations[0].race_id if origin_colony.populations else "default"
    transfer_params = {
        'direction': 'load',
        'cargo_type': 'passengers',
        'amount': 0,  # 0 = load as much as possible
        'planet_id': origin_colony.id,
        'species_id': species_id
    }
    return FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)


@runtime_checkable
class ICommandHandler(Protocol):
    """Protocol for command handlers."""

    def execute(self, session: 'GameSession', command: Any) -> ValidationResult:
        """Execute the command using the session context.

        Args:
            session: The game session providing empires, galaxy, etc.
            command: The command object with command-specific data.

        Returns:
            ValidationResult indicating success or failure.
        """
        ...


class BaseCommandHandler:
    """Mixin providing common resolution helpers for command handlers.

    Provides static methods for resolving fleets and planets with consistent
    error handling. Returns tuples of (object, error) where exactly one is set.

    PROJ-176 Phase 2: Extracted from duplicate resolution code in 19 handlers.
    PROJ-204 Phase 3: Added _resolve_fleet_required and _resolve_planet_optional.
    """

    @staticmethod
    def _resolve_fleet(session: 'GameSession', fleet_id: int, empire_id: int = None) -> tuple:
        """Resolve a fleet by ID with optional ownership validation.

        Args:
            session: The game session with empires and galaxy.
            fleet_id: The fleet ID to resolve.
            empire_id: Optional empire ID to validate ownership.

        Returns:
            tuple[Fleet, None] on success, tuple[None, ValidationResult] on failure.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if fleet is None:
            return (None, ValidationResult.error("Fleet not found."))

        if empire_id is not None and fleet.owner_id != empire_id:
            return (None, ValidationResult.error("Fleet does not belong to this empire."))

        return (fleet, None)

    @staticmethod
    def _resolve_fleet_required(session: 'GameSession', fleet_id: int, empire_id: int = None):
        """Resolve a fleet by ID, raising ValueError if not found.

        Use this when fleet must exist - avoids tuple unpacking boilerplate.

        Args:
            session: The game session with empires and galaxy.
            fleet_id: The fleet ID to resolve.
            empire_id: Optional empire ID to validate ownership.

        Returns:
            Fleet object if found.

        Raises:
            ValueError: If fleet not found or ownership validation fails.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if fleet is None:
            raise ValueError("Fleet not found.")

        if empire_id is not None and fleet.owner_id != empire_id:
            raise ValueError("Fleet does not belong to this empire.")

        return fleet

    @staticmethod
    def _resolve_planet(session: 'GameSession', planet_id: int) -> tuple:
        """Resolve a planet by ID.

        Args:
            session: The game session with galaxy.
            planet_id: The planet ID to resolve.

        Returns:
            tuple[Planet, None] on success, tuple[None, ValidationResult] on failure.
        """
        planet = session._get_planet_by_id(planet_id)
        if planet is None:
            return (None, ValidationResult.error("Planet not found."))

        return (planet, None)

    @staticmethod
    def _resolve_planet_optional(session: 'GameSession', planet_id: int, required: bool = True):
        """Resolve a planet by ID with configurable error handling.

        Use this when planet may or may not be required.

        Args:
            session: The game session with galaxy.
            planet_id: The planet ID to resolve.
            required: If True, raise ValueError when not found. If False, return None.

        Returns:
            Planet object if found, None if not found and required=False.

        Raises:
            ValueError: If planet not found and required=True.
        """
        planet = session._get_planet_by_id(planet_id)
        if planet is None:
            if required:
                raise ValueError("Planet not found.")
            return None

        return planet


class CommandHandlerRegistry:
    """Registry for command handlers with dispatch capability."""

    def __init__(self):
        self._handlers: Dict[str, ICommandHandler] = {}

    def register(self, command_name: str, handler: ICommandHandler) -> None:
        """Register a handler for a command type.

        Args:
            command_name: The command class name (e.g., 'IssueColonizeCommand').
            handler: Handler instance implementing ICommandHandler.
        """
        self._handlers[command_name] = handler

    def dispatch(self, command_name: str, session: 'GameSession', command: Any) -> ValidationResult:
        """Dispatch a command to its registered handler.

        Args:
            command_name: The command class name.
            session: The game session context.
            command: The command object.

        Returns:
            ValidationResult from the handler, or failure if no handler found.
        """
        handler = self._handlers.get(command_name)
        if handler is None:
            return ValidationResult.error(f"Unknown command type: {command_name}")
        return handler.execute(session, command)


class ColonizeCommandHandler(BaseCommandHandler):
    """Handler for IssueColonizeCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueColonizeCommand."""
        # 1. Resolve Fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # Resolve Planet (None is valid for colonize validation)
        target_planet = None
        if cmd.planet_id:
            target_planet = session._get_planet_by_id(cmd.planet_id)

        # 2. Validate
        result = session.turn_engine.validate_colonize_order(session.galaxy, fleet, target_planet)

        # 3. Apply
        if result.is_valid:
            # Auto-load population from colony at fleet's location (BUG-70)
            # PROJ-207 Phase 4: Use shared helper
            origin_colony = session._find_colony_at_fleet(fleet)
            load_order = create_auto_load_population_order(origin_colony)
            if load_order:
                fleet.add_order(load_order)

            # Add MOVE order to get to the target planet
            planet_global_hex = session.galaxy.get_planet_global_hex(target_planet)

            if planet_global_hex and fleet.location != planet_global_hex:
                move_order = FleetOrder(OrderType.MOVE, target=planet_global_hex)
                fleet.add_order(move_order)

            # Ensure we pass the OBJECT to rules
            order = FleetOrder(OrderType.COLONIZE, target=target_planet)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")

        return result


class MoveCommandHandler(BaseCommandHandler):
    """Handler for IssueMoveCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueMoveCommand."""
        # 1. Resolve Fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validation / Pathfinding
        path = session.preview_fleet_path(fleet, cmd.target_hex)

        if not path:
            if fleet.location == cmd.target_hex:
                pass  # Already there - no-op
            else:
                return ValidationResult.error("Target is unreachable or invalid.")

        # 3. Apply
        order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            fleet.path = path

        return ValidationResult.success()


class BuildShipCommandHandler(BaseCommandHandler):
    """Handler for IssueBuildShipCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueBuildShipCommand."""
        # 1. Resolve Planet
        planet, error = self._resolve_planet(session, cmd.planet_id)
        if error:
            return error

        # 2. Apply
        planet.add_production(cmd.design_name, 1)

        return ValidationResult.success()


class InterceptCommandHandler(BaseCommandHandler):
    """Handler for IssueInterceptCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueInterceptCommand - creates a MOVE_TO_FLEET order."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        logger.info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


class JoinCommandHandler(BaseCommandHandler):
    """Handler for IssueJoinFleetCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueJoinFleetCommand - creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order first
        move_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 4. Then create JOIN_FLEET order
        join_order = FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        logger.info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


class ColonizeMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueColonizeMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueColonizeMissionCommand - queues MOVE and COLONIZE orders."""
        from game.strategy.validation import ColonizeValidator

        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve planet (None is valid - means "any planet")
        planet = None
        if cmd.planet_id is not None:
            planet, error = self._resolve_planet(session, cmd.planet_id)
            if error:
                return error

            # PROJ-140 Phase 4: Validate pod match for specific planet targets
            # Get component registry from turn_engine (always available after init)
            component_registry = session.turn_engine._registries.components

            if component_registry:
                planet_type_str = planet.planet_type.name

                # Check if fleet has a matching colony pod
                ship_with_pod = ColonizeValidator.find_ship_with_colony_pod(
                    fleet, planet_type_str, component_registry
                )

                if ship_with_pod is None:
                    return ValidationResult.error(
                        f"No ship in fleet has {planet_type_str} colony pod.",
                        code="NO_COLONY_POD"
                    )

                # Check chain limits - ensure not over-committed
                available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
                committed = ColonizeValidator.get_committed_colony_pods(fleet)

                available_count = available.get(planet_type_str, 0)
                committed_count = committed.get(planet_type_str, 0)

                if committed_count >= available_count:
                    return ValidationResult.error(
                        f"All {planet_type_str} colony pods already assigned.",
                        code="COLONY_POD_EXHAUSTED"
                    )

        # 3. Auto-load population from colony at fleet's current location (BUG-70)
        # PROJ-207 Phase 4: Use shared helper
        origin_colony = session._find_colony_at_fleet(fleet)
        load_order = create_auto_load_population_order(origin_colony)
        if load_order:
            fleet.add_order(load_order)

        # 4. Queue MOVE order if needed (chain-aware path calculation)
        # PROJ-207 Phase 5: Use shared helper with auto chain detection
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 5. Queue COLONIZE order (target=None means "any available planet")
        colonize_order = FleetOrder(OrderType.COLONIZE, target=planet)
        fleet.add_order(colonize_order)

        planet_name = planet.name if planet else "Any Planet"
        logger.info(f"GameSession: Queued Colonize Mission for Fleet {fleet.id} -> {planet_name}")
        return ValidationResult.success()


class ClearOrdersCommandHandler(BaseCommandHandler):
    """Handler for ClearFleetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle ClearFleetOrdersCommand - clears all orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Clear orders and path
        fleet.orders = []
        fleet.path = []

        logger.info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return ValidationResult.success()


class TransferCommandHandler(BaseCommandHandler):
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations."""
        from game.strategy.validation import TransferValidator

        logger.info(f"DIAG TransferCommandHandler: cmd fleet_id={cmd.fleet_id}, planet_id={cmd.planet_id}, cargo_type={cmd.cargo_type}, direction={cmd.direction}, amount={cmd.amount}, species_id={cmd.species_id}")

        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            logger.info(f"DIAG TransferCommandHandler: Fleet {cmd.fleet_id} NOT FOUND")
            return error
        logger.info(f"DIAG TransferCommandHandler: Fleet found, location={fleet.location}, ships={len(fleet.ships)}")

        # 2. Find owning empire (PROJ-204: O(1) lookup via owner_id instead of O(N) loop)
        if fleet.owner_id < 0 or fleet.owner_id >= len(session.empires):
            logger.info(f"DIAG TransferCommandHandler: Fleet owner NOT FOUND")
            return ValidationResult.error("Fleet owner not found.")
        owning_empire = session.empires[fleet.owner_id]

        # 3. Resolve planet
        planet, error = self._resolve_planet(session, cmd.planet_id)
        if error:
            logger.info(f"DIAG TransferCommandHandler: Planet {cmd.planet_id} NOT FOUND")
            return error
        logger.info(f"DIAG TransferCommandHandler: Planet found: name={planet.name}, owner_id={planet.owner_id}, total_pop={planet.total_population}")

        # 4. Validate (skip location check — we'll auto-add a MOVE order)
        # Use projected cargo to account for earlier queued orders
        from game.strategy.services.fleet_cargo_projector import FleetCargoProjector
        projected = FleetCargoProjector.get_projected_cargo(fleet, cmd.cargo_type)
        capacity = fleet.get_fleet_cargo_capacity(cmd.cargo_type)
        current = fleet.get_fleet_cargo_current(cmd.cargo_type)
        logger.info(f"DIAG TransferCommandHandler: cargo capacity={capacity}, current={current}, projected={projected}")

        result = TransferValidator.validate(
            session.galaxy, fleet, planet, cmd.cargo_type, cmd.direction, cmd.amount,
            cmd.species_id, skip_location_check=True, projected_cargo=projected
        )
        # ValidationResult always has error_code attribute
        logger.info(f"DIAG TransferCommandHandler: validation result is_valid={result.is_valid}, errors={result.errors}, error_code={result.error_code}")

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
            order = FleetOrder(OrderType.TRANSFER, target=transfer_params)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued TRANSFER order for Fleet {fleet.id}, orders now={len(fleet.orders)}")
        else:
            logger.info(f"DIAG TransferCommandHandler: REJECTED - not adding order")

        return result


class BuildOrderCommandHandler(BaseCommandHandler):
    """Handler for IssueBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueBuildOrderCommand - creates BUILD order for fleet construction.

        Inserts BUILD order at position 0 (front of queue) so it executes first.
        Clears the fleet path since fleet must stay stationary to build.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Create BUILD order and insert at front
        build_order = FleetOrder(OrderType.BUILD)
        fleet.orders.insert(0, build_order)

        # 3. Clear movement path - fleet must stay stationary to build
        fleet.path = []

        logger.info(f"GameSession: Issued BUILD order for Fleet {fleet.id}")
        return ValidationResult.success()


class RemoveBuildOrderCommandHandler(BaseCommandHandler):
    """Handler for RemoveBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle RemoveBuildOrderCommand - removes BUILD orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Remove all BUILD orders
        fleet.orders = [o for o in fleet.orders if o.type != OrderType.BUILD]

        logger.info(f"GameSession: Removed BUILD orders from Fleet {fleet.id}")
        return ValidationResult.success()


class WarpCommandHandler(BaseCommandHandler):
    """Handler for IssueWarpCommand (PROJ-187)."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueWarpCommand - creates WARP order with optional MOVE prefix."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate fleet can use warp
        if not fleet.can_use_warp():
            limiting_ship = fleet.get_warp_limiting_ship()
            if limiting_ship:
                return ValidationResult.error(
                    f"Fleet cannot use warp - {limiting_ship.name} lacks warp capability."
                )
            return ValidationResult.error("Fleet cannot use warp points.")

        # 3. Validate warp point exists at target hex
        warp_point_hex = cmd.warp_point_hex
        source_system = session.galaxy._global_hex_warp_points.get(warp_point_hex)
        if not source_system:
            return ValidationResult.error(
                f"No warp point at {warp_point_hex}."
            )

        # 4. If fleet is not at warp point, auto-queue MOVE first (PROJ-204 Phase 3)
        orders_before = len(fleet.orders)
        move_result = add_move_order_if_needed(session, fleet, warp_point_hex)
        if not move_result.is_valid:
            return move_result
        if len(fleet.orders) > orders_before:  # Move was added
            logger.info(f"GameSession: Auto-added MOVE to warp point at {warp_point_hex}")

        # 5. Queue WARP order
        warp_order = FleetOrder(OrderType.WARP, target=warp_point_hex)
        fleet.add_order(warp_order)

        logger.info(f"GameSession: Issued WARP order for Fleet {fleet.id} -> {warp_point_hex}")
        return ValidationResult.success()


def create_default_registry() -> CommandHandlerRegistry:
    """Create a registry with all standard command handlers registered.

    Returns:
        CommandHandlerRegistry with all handlers registered.
    """
    from game.strategy.engine.superweapon_command_handlers import (
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
    )

    registry = CommandHandlerRegistry()

    # Core handlers
    registry.register('IssueColonizeCommand', ColonizeCommandHandler())
    registry.register('IssueMoveCommand', MoveCommandHandler())
    registry.register('IssueBuildShipCommand', BuildShipCommandHandler())
    registry.register('IssueInterceptCommand', InterceptCommandHandler())
    registry.register('IssueJoinFleetCommand', JoinCommandHandler())
    registry.register('QueueColonizeMissionCommand', ColonizeMissionCommandHandler())
    registry.register('ClearFleetOrdersCommand', ClearOrdersCommandHandler())
    registry.register('IssueTransferCommand', TransferCommandHandler())
    registry.register('IssueWarpCommand', WarpCommandHandler())  # PROJ-187

    # Build order handlers (PROJ-207 Phase 4)
    registry.register('IssueBuildOrderCommand', BuildOrderCommandHandler())
    registry.register('RemoveBuildOrderCommand', RemoveBuildOrderCommandHandler())

    # Superweapon direct handlers (PROJ-102)
    registry.register('IssueImplodePlanetCommand', ImplodePlanetCommandHandler())
    registry.register('IssueStellerateStarCommand', StellerateStarCommandHandler())
    registry.register('IssueOpenWarpPointCommand', OpenWarpPointCommandHandler())
    registry.register('IssueCloseWarpPointCommand', CloseWarpPointCommandHandler())
    registry.register('IssueCreateDysonSphereCommand', CreateDysonSphereCommandHandler())
    registry.register('IssueSelfDestructCommand', SelfDestructCommandHandler())

    # Superweapon mission handlers (PROJ-102)
    registry.register('QueueImplodePlanetMissionCommand', ImplodePlanetMissionCommandHandler())
    registry.register('QueueStellerateStarMissionCommand', StellerateStarMissionCommandHandler())
    registry.register('QueueOpenWarpPointMissionCommand', OpenWarpPointMissionCommandHandler())
    registry.register('QueueCloseWarpPointMissionCommand', CloseWarpPointMissionCommandHandler())
    registry.register('QueueCreateDysonSphereMissionCommand', CreateDysonSphereMissionCommandHandler())

    return registry
