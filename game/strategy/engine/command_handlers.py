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
from typing import Protocol, Dict, Any, TYPE_CHECKING, runtime_checkable, Optional
import logging

from game.core.validation import ValidationResult
from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.design_cost_calculator import DesignCostCalculator
from game.strategy.systems.design_library import DesignLibrary

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.commands import (
        Command, IssueColonizeCommand, IssueMoveCommand, IssueInterceptCommand,
        IssueJoinFleetCommand, QueueColonizeMissionCommand, ClearFleetOrdersCommand,
        IssueTransferCommand, IssueBuildOrderCommand, RemoveBuildOrderCommand,
        IssueWarpCommand, SplitFleetCommand, DeleteFleetOrderCommand,
        ReorderFleetOrderCommand, AddToConstructionQueueCommand,
        RemoveFromConstructionQueueCommand, ReorderConstructionQueueCommand,
    )


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
    # BUG-70: Find the last MOVE order (skip non-MOVE orders like LOAD_POPULATION)
    if start_hex is None:
        start_hex = fleet.location
        for order in reversed(fleet.orders):
            if order.type == OrderType.MOVE:
                start_hex = order.target
                break

    # Already at target - no move needed
    if start_hex == target_hex:
        return ValidationResult.success()

    # Calculate path from chain-aware start
    path = find_hybrid_path(session.galaxy, start_hex, target_hex)
    if not path:
        return ValidationResult.error("No path found to target.")

    # Queue MOVE order
    move_order = Order(OrderType.MOVE, target=target_hex)
    fleet.add_order(move_order)

    # Set path immediately if it's the first order and fleet is at start
    if len(fleet.orders) == 1 and fleet.location == start_hex:
        fleet.path = strip_start_hex(fleet.location, path)

    return ValidationResult.success()


def create_auto_load_population_order() -> 'Order':
    """Create a generic LOAD_POPULATION order for colonize workflows.

    BUG-70: The order is always inserted at command time. At execution time,
    the fleet order processor auto-resolves the colony at the fleet's current
    hex. If no owned colony is present, the order is a no-op.

    Returns:
        Order for LOAD_POPULATION (always returns an order, never None).
    """
    from game.strategy.engine.commands import TransferDirection
    transfer_params = {
        'direction': TransferDirection.LOAD,
        'cargo_type': 'passengers',
        'amount': 0,  # 0 = load as much as possible
    }
    return Order(OrderType.LOAD_POPULATION, target=transfer_params)


@runtime_checkable
class ICommandHandler(Protocol):
    """Protocol for command handlers."""

    def execute(self, session: 'GameSession', command: 'Command') -> ValidationResult:
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

    @staticmethod
    def _resolve_build_entity(session: 'GameSession', entity_id: int, entity_type: str):
        """Resolve a planet or fleet by ID and type.

        BUG-103: Extracted to BaseCommandHandler for shared use by all
        construction queue handlers.

        Args:
            session: Game session for lookups.
            entity_id: ID of the entity.
            entity_type: "planet" or "fleet".

        Returns:
            Planet or Fleet object, or None if not found.
        """
        if entity_type == "planet":
            return session._get_planet_by_id(entity_id)
        elif entity_type == "fleet":
            return session._get_fleet_by_id(entity_id)
        return None

    @staticmethod
    def _resolve_queue(entity, queue_id: Optional[str]) -> Optional[list]:
        """Find the correct construction queue for the entity.

        BUG-103: Extracted to BaseCommandHandler for shared use by all
        construction queue handlers. Supports multi-queue entities
        (e.g., planets with shipyard facilities).

        Args:
            entity: Planet or Fleet entity.
            queue_id: Optional queue identifier. If None, uses entity.construction_queue.

        Returns:
            The construction queue list, or None if not found.
        """
        # If no queue_id specified, use entity's main queue
        if queue_id is None:
            return getattr(entity, 'construction_queue', None)

        # For planets, check if queue_id matches a facility's instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return getattr(facility, 'construction_queue', None)

        # Check if queue_id matches base queue pattern (e.g., "planet_100_base")
        base_queue_pattern = f"planet_{getattr(entity, 'id', '')}_base"
        if queue_id == base_queue_pattern:
            return getattr(entity, 'construction_queue', None)

        # Fallback to entity's main queue
        return getattr(entity, 'construction_queue', None)

    @staticmethod
    def _build_colonize_target(planet, cmd):
        """Build COLONIZE order target — Planet or dict with amounts.

        If population_amount or cargo_amounts are specified on the command,
        wraps the planet in a dict so process_colonize() can extract the amounts.
        Otherwise returns the Planet directly for backward compatibility.
        """
        if cmd.population_amount is not None or cmd.cargo_amounts is not None:
            return {
                'planet': planet,
                'population': cmd.population_amount,
                'cargo': cmd.cargo_amounts,
            }
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

    def dispatch(self, command_name: str, session: 'GameSession', command: 'Command') -> ValidationResult:
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

    def execute(self, session: 'GameSession', cmd: 'IssueColonizeCommand') -> ValidationResult:
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
            # BUG-70: Always insert LOAD_POPULATION before MOVE/COLONIZE.
            # Colony is resolved at execution time, not command time.
            fleet.add_order(create_auto_load_population_order())
            logger.debug(f"BUG-70: Inserted LOAD_POPULATION order for fleet {fleet.id}")

            # Add MOVE order to get to the target planet
            planet_global_hex = session.galaxy.get_planet_global_hex(target_planet)

            if planet_global_hex and fleet.location != planet_global_hex:
                move_order = Order(OrderType.MOVE, target=planet_global_hex)
                fleet.add_order(move_order)

            # Build colonize target with optional population/cargo amounts
            colonize_target = self._build_colonize_target(target_planet, cmd)
            order = Order(OrderType.COLONIZE, target=colonize_target)
            fleet.add_order(order)
            logger.info(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")

        return result


class MoveCommandHandler(BaseCommandHandler):
    """Handler for IssueMoveCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueMoveCommand') -> ValidationResult:
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
        order = Order(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            fleet.path = path

        return ValidationResult.success()


# NOTE: BuildShipCommandHandler removed in PROJ-208 Phase 2 (dead code).
# Use AddToConstructionQueueCommandHandler instead for all build queue operations.


class InterceptCommandHandler(BaseCommandHandler):
    """Handler for IssueInterceptCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueInterceptCommand') -> ValidationResult:
        """Handle IssueInterceptCommand - creates a MOVE_TO_FLEET order."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. PROJ-222: Validate not self-targeting
        if fleet.id == target_fleet.id:
            return ValidationResult.error("Fleet cannot intercept itself.")

        # 4. Create MOVE_TO_FLEET order
        order = Order(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        # 5. PROJ-222: Register as pursuer
        target_fleet.pursuer_tracker.add_pursuer(fleet)

        logger.info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


class JoinCommandHandler(BaseCommandHandler):
    """Handler for IssueJoinFleetCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueJoinFleetCommand') -> ValidationResult:
        """Handle IssueJoinFleetCommand - creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        # 1. Resolve source fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve target fleet
        target_fleet, error = self._resolve_fleet(session, cmd.target_fleet_id)
        if error:
            return ValidationResult.error("Target fleet not found.")

        # 3. PROJ-222: Validate not self-targeting
        if fleet.id == target_fleet.id:
            return ValidationResult.error("Fleet cannot join itself.")

        # 4. PROJ-222: Validate same empire
        if fleet.owner_id != target_fleet.owner_id:
            return ValidationResult.error("Cannot join fleet of another empire.")

        # 5. Create MOVE_TO_FLEET order first
        move_order = Order(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 6. Then create JOIN_FLEET order
        join_order = Order(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        # 7. PROJ-222: Register as pursuer
        target_fleet.pursuer_tracker.add_pursuer(fleet)

        logger.info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult.success()


class ColonizeMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueColonizeMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueColonizeMissionCommand') -> ValidationResult:
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

            # Phase 3: Validate fleet has a drop pod
            if not ColonizeValidator.fleet_has_drop_pod(fleet):
                return ValidationResult.error(
                    "No drop pod carried by any ship in fleet.",
                    code="NO_COLONY_POD"
                )

            # Check chain limits - ensure not over-committed
            available_count = ColonizeValidator.count_drop_pods(fleet)
            committed_count = ColonizeValidator.count_committed_colonize_orders(fleet)

            if committed_count >= available_count:
                return ValidationResult.error(
                    "All drop pods already assigned to colonize orders.",
                    code="COLONY_POD_EXHAUSTED"
                )

        # 3. BUG-70: Always insert LOAD_POPULATION before MOVE/COLONIZE.
        # Colony is resolved at execution time, not command time.
        fleet.add_order(create_auto_load_population_order())
        logger.debug(f"BUG-70: Inserted LOAD_POPULATION order for fleet {fleet.id}")

        # 4. Queue MOVE order if needed (chain-aware path calculation)
        # PROJ-207 Phase 5: Use shared helper with auto chain detection
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 5. Queue COLONIZE order (target=None means "any available planet")
        colonize_target = self._build_colonize_target(planet, cmd)
        colonize_order = Order(OrderType.COLONIZE, target=colonize_target)
        fleet.add_order(colonize_order)

        planet_name = planet.name if planet else "Any Planet"
        logger.info(f"GameSession: Queued Colonize Mission for Fleet {fleet.id} -> {planet_name}")
        return ValidationResult.success()


class ClearOrdersCommandHandler(BaseCommandHandler):
    """Handler for ClearFleetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: 'ClearFleetOrdersCommand') -> ValidationResult:
        """Handle ClearFleetOrdersCommand - clears all orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Clear orders and path (PROJ-222: use Fleet API for pursuer cleanup)
        fleet.clear_orders()

        logger.info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return ValidationResult.success()


class TransferCommandHandler(BaseCommandHandler):
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: 'IssueTransferCommand') -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations."""
        from game.strategy.validation import TransferValidator

        logger.debug(f"TransferCommandHandler: fleet_id={cmd.fleet_id}, planet_id={cmd.planet_id}, cargo_type={cmd.cargo_type}, direction={cmd.direction}, amount={cmd.amount}")

        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error
        logger.debug(f"TransferCommandHandler: Fleet {fleet.id} found, location={fleet.location}, ships={len(fleet.ships)}")

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


class BuildOrderCommandHandler(BaseCommandHandler):
    """Handler for IssueBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: 'IssueBuildOrderCommand') -> ValidationResult:
        """Handle IssueBuildOrderCommand - creates BUILD order for fleet construction.

        Inserts BUILD order at position 0 (front of queue) so it executes first.
        Clears the fleet path since fleet must stay stationary to build.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Create BUILD order and insert at front
        build_order = Order(OrderType.BUILD)
        fleet.orders.insert(0, build_order)

        # 3. Clear movement path - fleet must stay stationary to build
        fleet.path = []

        logger.info(f"GameSession: Issued BUILD order for Fleet {fleet.id}")
        return ValidationResult.success()


class RemoveBuildOrderCommandHandler(BaseCommandHandler):
    """Handler for RemoveBuildOrderCommand (PROJ-207 Phase 4)."""

    def execute(self, session: 'GameSession', cmd: 'RemoveBuildOrderCommand') -> ValidationResult:
        """Handle RemoveBuildOrderCommand - removes BUILD orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Remove all BUILD orders (PROJ-222: use Fleet API for consistency)
        fleet.remove_orders_by_type(OrderType.BUILD)

        logger.info(f"GameSession: Removed BUILD orders from Fleet {fleet.id}")
        return ValidationResult.success()


class WarpCommandHandler(BaseCommandHandler):
    """Handler for IssueWarpCommand (PROJ-187)."""

    def execute(self, session: 'GameSession', cmd: 'IssueWarpCommand') -> ValidationResult:
        """Handle IssueWarpCommand - creates WARP order with optional MOVE prefix."""
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate fleet can use warp
        if not fleet.capabilities.can_use_warp():
            limiting_ship = fleet.capabilities.get_warp_limiting_ship()
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
        warp_order = Order(OrderType.WARP, target=warp_point_hex)
        fleet.add_order(warp_order)

        logger.info(f"GameSession: Issued WARP order for Fleet {fleet.id} -> {warp_point_hex}")
        return ValidationResult.success()


# =============================================================================
# Fleet Management Command Handlers (PROJ-208)
# =============================================================================

class SplitFleetCommandHandler(BaseCommandHandler):
    """Handler for SplitFleetCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'SplitFleetCommand') -> ValidationResult:
        """Handle SplitFleetCommand - split ships into a new fleet.

        Removes specified ships from source fleet and creates a new fleet
        with those ships at the same location.
        """
        # 1. Resolve source fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ship_instance_ids
        if not cmd.ship_instance_ids:
            return ValidationResult.error("No ships specified for split.")

        # Find ships to move
        ships_to_move = []
        for instance_id in cmd.ship_instance_ids:
            found = None
            for ship in fleet.ships:
                if ship.instance_id == instance_id:
                    found = ship
                    break
            if found is None:
                return ValidationResult.error(f"Ship {instance_id} not found in fleet.")
            ships_to_move.append(found)

        # 3. Validate at least one ship remains in source fleet
        remaining_count = len(fleet.ships) - len(ships_to_move)
        if remaining_count < 1:
            return ValidationResult.error("At least one ship must remain in the source fleet.")

        # 4. Get owning empire to generate new fleet ID
        if fleet.owner_id < 0 or fleet.owner_id >= len(session.empires):
            return ValidationResult.error("Fleet owner not found.")
        empire = session.empires[fleet.owner_id]

        # 5. Create new fleet at same location
        from game.strategy.data.fleet import Fleet
        new_fleet_id = empire.get_next_fleet_id()
        new_fleet = Fleet(
            fleet_id=new_fleet_id,
            owner_id=fleet.owner_id,
            location=fleet.location,
            component_registry=fleet._component_registry
        )

        # 6. Move ships to new fleet
        for ship in ships_to_move:
            fleet.remove_ship(ship)
            new_fleet.add_ship(ship)

        # 7. Register new fleet with empire (auto-registers with galaxy via PROJ-219)
        empire.add_fleet(new_fleet)

        logger.info(f"GameSession: Split fleet {cmd.fleet_id} -> new fleet {new_fleet_id} ({len(ships_to_move)} ships)")
        return ValidationResult.success()


class DeleteFleetOrderCommandHandler(BaseCommandHandler):
    """Handler for DeleteFleetOrderCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'DeleteFleetOrderCommand') -> ValidationResult:
        """Handle DeleteFleetOrderCommand - remove an order from the queue.

        If the active order (index 0) is deleted, the fleet's path is invalidated.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate order_index
        if cmd.order_index < 0 or cmd.order_index >= len(fleet.orders):
            return ValidationResult.error(f"Invalid order index: {cmd.order_index}")

        # 3. Remove the order (PROJ-222: use Fleet API for pursuer cleanup)
        fleet.remove_order_at(cmd.order_index)

        logger.info(f"GameSession: Deleted order {cmd.order_index} from fleet {cmd.fleet_id}")
        return ValidationResult.success()


class ReorderFleetOrderCommandHandler(BaseCommandHandler):
    """Handler for ReorderFleetOrderCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'ReorderFleetOrderCommand') -> ValidationResult:
        """Handle ReorderFleetOrderCommand - swap order positions.

        If the active order (index 0) is affected, the fleet's path is invalidated.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate order_index
        if cmd.order_index < 0 or cmd.order_index >= len(fleet.orders):
            return ValidationResult.error(f"Invalid order index: {cmd.order_index}")

        # 3. Validate direction
        if cmd.direction not in (-1, 1):
            return ValidationResult.error(f"Invalid direction: {cmd.direction} (must be -1 or 1)")

        # 4. Validate target index
        target_index = cmd.order_index + cmd.direction
        if target_index < 0 or target_index >= len(fleet.orders):
            return ValidationResult.error(f"Cannot move order {cmd.order_index} in direction {cmd.direction}")

        # 5. Swap orders
        fleet.orders[cmd.order_index], fleet.orders[target_index] = \
            fleet.orders[target_index], fleet.orders[cmd.order_index]

        # 6. If active order (index 0) was affected, invalidate path
        if cmd.order_index == 0 or target_index == 0:
            fleet.path = []

        logger.info(f"GameSession: Reordered fleet {cmd.fleet_id} order {cmd.order_index} -> {target_index}")
        return ValidationResult.success()


# =============================================================================
# Construction Queue Command Handlers (PROJ-208 Phase 2)
# =============================================================================

class AddToConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for AddToConstructionQueueCommand (PROJ-208 Phase 2)."""

    def execute(self, session: 'GameSession', cmd: 'AddToConstructionQueueCommand') -> ValidationResult:
        """Handle AddToConstructionQueueCommand - add item to construction queue.

        Creates a queue item dict with design_id, type, turns_remaining, and
        cost tracking fields, then inserts or appends to the entity's queue.
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue - may be entity.construction_queue or a facility queue
        queue = self._resolve_queue(entity, cmd.queue_id)
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate index if specified
        if cmd.index is not None:
            if cmd.index < 0 or cmd.index > len(queue):
                return ValidationResult.error(f"Invalid queue index: {cmd.index}")

        # 4. Check design validity (mass budget)
        design_valid = self._check_design_valid(session, entity, cmd.design_id)
        if not design_valid:
            return ValidationResult.error("Design exceeds mass budget and cannot be built.")

        # 5. Calculate design cost (PROJ-213: fix empty total_cost bug)
        total_cost = self._load_design_cost(session, entity, cmd.design_id)

        # 5. Pre-calculate initial turns estimate (BUG-96)
        from game.strategy.data.build_queue_source import (
            get_production_rate_for_queue, estimate_build_turns,
        )
        production_rate = get_production_rate_for_queue(entity, cmd.queue_id)
        initial_turns = estimate_build_turns(total_cost, production_rate)

        # 6. Create queue item
        queue_item = {
            "design_id": cmd.design_id,
            "type": cmd.category,
            "turns_remaining": initial_turns,
            "total_cost": total_cost,
            "resources_consumed": {res: 0.0 for res in total_cost},
        }

        # 7. Add target_planet_id for complexes if specified
        if cmd.target_planet_id is not None:
            queue_item["target_planet_id"] = cmd.target_planet_id

        # 8. Insert or append
        if cmd.index is not None:
            queue.insert(cmd.index, queue_item)
            logger.info(f"GameSession: Inserted {cmd.design_id} into {cmd.entity_type} {cmd.entity_id} queue at {cmd.index}")
        else:
            queue.append(queue_item)
            logger.info(f"GameSession: Appended {cmd.design_id} to {cmd.entity_type} {cmd.entity_id} queue")

        return ValidationResult.success()

    def _check_design_valid(self, session: 'GameSession', entity, design_id: str) -> bool:
        """Check if a design is valid for construction (within mass budget).

        Args:
            session: Game session for save_path.
            entity: Planet or Fleet with owner_id.
            design_id: ID of the design to check.

        Returns:
            True if the design is valid, False if it exceeds mass budget.
        """
        try:
            empire_id = getattr(entity, 'owner_id', 0)
            library = DesignLibrary(session.save_path, empire_id)
            design_data = library.load_design_data(design_id)
            if design_data is None:
                return True  # Can't validate, allow by default
            expected_stats = design_data.get('expected_stats', {})
            return expected_stats.get('mass_valid', True)
        except (OSError, ValueError, KeyError):
            return True  # Can't validate, allow by default

    def _load_design_cost(self, session: 'GameSession', entity, design_id: str) -> Dict[str, float]:
        """Load design data and calculate total resource cost.

        PROJ-213: Populates queue items with actual build costs so
        ProductionEngine can process tick-based resource consumption.

        Args:
            session: Game session for save_path.
            entity: Planet or Fleet with owner_id.
            design_id: ID of the design to get cost for.

        Returns:
            Dict mapping resource type to cost amount, empty dict on failure.
        """
        try:
            empire_id = getattr(entity, 'owner_id', 0)
            library = DesignLibrary(session.save_path, empire_id)
            design_data = library.load_design_data(design_id)
            if design_data is None:
                logger.warning(f"Could not load design data for {design_id}")
                return {}
            # PROJ-218: Pass registries for Ship-loading cost calculation
            return DesignCostCalculator.calculate_total_cost(design_data, session.registries)
        except (OSError, ValueError, KeyError) as e:
            logger.warning(f"Failed to calculate design cost for {design_id}: {e}")
            return {}

class RemoveFromConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for RemoveFromConstructionQueueCommand (PROJ-208 Phase 2).

    BUG-103: Updated to use _resolve_queue() from BaseCommandHandler for
    multi-queue entity support (facility queues).
    """

    def execute(self, session: 'GameSession', cmd: 'RemoveFromConstructionQueueCommand') -> ValidationResult:
        """Handle RemoveFromConstructionQueueCommand - remove item from queue.

        For fleets, if the queue becomes empty, may need BUILD order cleanup
        (handled by separate RemoveBuildOrderCommand if needed).
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue (BUG-103: supports facility queues via queue_id)
        queue = self._resolve_queue(entity, getattr(cmd, 'queue_id', None))
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate index
        if cmd.item_index < 0 or cmd.item_index >= len(queue):
            return ValidationResult.error(f"Invalid queue index: {cmd.item_index}")

        # 4. Remove item
        removed_item = queue.pop(cmd.item_index)
        logger.info(f"GameSession: Removed item {cmd.item_index} from {cmd.entity_type} {cmd.entity_id} queue")

        return ValidationResult.success()


class ReorderConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for ReorderConstructionQueueCommand (PROJ-208 Phase 2).

    BUG-103: Updated to use _resolve_queue() from BaseCommandHandler for
    multi-queue entity support (facility queues).
    """

    def execute(self, session: 'GameSession', cmd: 'ReorderConstructionQueueCommand') -> ValidationResult:
        """Handle ReorderConstructionQueueCommand - move item to new position.

        Performs atomic pop + insert to move item from from_index to to_index.
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue (BUG-103: supports facility queues via queue_id)
        queue = self._resolve_queue(entity, getattr(cmd, 'queue_id', None))
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate indices
        if cmd.from_index < 0 or cmd.from_index >= len(queue):
            return ValidationResult.error(f"Invalid from_index: {cmd.from_index}")
        if cmd.to_index < 0 or cmd.to_index >= len(queue):
            return ValidationResult.error(f"Invalid to_index: {cmd.to_index}")

        # 4. Perform atomic reorder (pop + insert)
        item = queue.pop(cmd.from_index)
        queue.insert(cmd.to_index, item)

        logger.info(f"GameSession: Reordered {cmd.entity_type} {cmd.entity_id} queue {cmd.from_index} -> {cmd.to_index}")
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
    # NOTE: IssueBuildShipCommand removed (PROJ-208) - use AddToConstructionQueueCommand
    registry.register('IssueInterceptCommand', InterceptCommandHandler())
    registry.register('IssueJoinFleetCommand', JoinCommandHandler())
    registry.register('QueueColonizeMissionCommand', ColonizeMissionCommandHandler())
    registry.register('ClearOrdersCommand', ClearOrdersCommandHandler())
    registry.register('ClearFleetOrdersCommand', ClearOrdersCommandHandler())  # PROJ-238: compat alias
    registry.register('IssueTransferCommand', TransferCommandHandler())
    registry.register('IssueWarpCommand', WarpCommandHandler())  # PROJ-187

    # Build order handlers (PROJ-207 Phase 4)
    registry.register('IssueBuildOrderCommand', BuildOrderCommandHandler())
    registry.register('RemoveBuildOrderCommand', RemoveBuildOrderCommandHandler())

    # Fleet management handlers (PROJ-208 Phase 1)
    registry.register('SplitFleetCommand', SplitFleetCommandHandler())
    registry.register('DeleteOrderCommand', DeleteFleetOrderCommandHandler())
    registry.register('DeleteFleetOrderCommand', DeleteFleetOrderCommandHandler())  # PROJ-238: compat
    registry.register('ReorderOrderCommand', ReorderFleetOrderCommandHandler())
    registry.register('ReorderFleetOrderCommand', ReorderFleetOrderCommandHandler())  # PROJ-238: compat

    # Construction queue handlers (PROJ-208 Phase 2)
    registry.register('AddToConstructionQueueCommand', AddToConstructionQueueCommandHandler())
    registry.register('RemoveFromConstructionQueueCommand', RemoveFromConstructionQueueCommandHandler())
    registry.register('ReorderConstructionQueueCommand', ReorderConstructionQueueCommandHandler())

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

    # PROJ-237: Planet order command handlers
    from game.strategy.engine.planet_command_handlers import (
        IssuePlanetOrderCommandHandler,
        ClearPlanetOrdersCommandHandler,
        DeletePlanetOrderCommandHandler,
        SetAtmosphereTargetCommandHandler,
    )
    registry.register('IssuePlanetOrderCommand', IssuePlanetOrderCommandHandler())
    registry.register('ClearPlanetOrdersCommand', ClearPlanetOrdersCommandHandler())
    registry.register('DeletePlanetOrderCommand', DeletePlanetOrderCommandHandler())
    registry.register('SetAtmosphereTargetCommand', SetAtmosphereTargetCommandHandler())

    return registry
