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
from typing import Protocol, Dict, Any, TYPE_CHECKING

from game.core.logger import log_info
from game.core.validation import validation_result, ValidationResult

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


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
            return validation_result(False, f"Unknown command type: {command_name}")
        return handler.execute(session, command)


class ColonizeCommandHandler:
    """Handler for IssueColonizeCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueColonizeCommand."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve Data
        fleet = None
        owning_empire = None

        for emp in session.empires:
            for f in emp.fleets:
                if f.id == cmd.fleet_id:
                    fleet = f
                    owning_empire = emp
                    break
            if fleet:
                break

        if not fleet:
            return validation_result(False, "Fleet not found.")

        # Resolve Planet
        target_planet = None
        if cmd.planet_id:
            target_planet = session.galaxy.get_planet_by_id(cmd.planet_id)

        # 2. Validate
        result = session.turn_engine.validate_colonize_order(session.galaxy, fleet, target_planet)

        # 3. Apply
        if result.is_valid:
            # Auto-load population from colony at fleet's location (BUG-70)
            origin_colony = session._find_colony_at_fleet(fleet)
            if origin_colony and origin_colony.populations:
                transfer_params = {
                    'direction': 'load',
                    'cargo_type': 'passengers',
                    'amount': 0,
                    'planet_id': origin_colony.id,
                }
                load_order = FleetOrder(OrderType.TRANSFER, target=transfer_params)
                fleet.add_order(load_order)

            # Ensure we pass the OBJECT to rules
            order = FleetOrder(OrderType.COLONIZE, target=target_planet)
            fleet.add_order(order)
            log_info(f"GameSession: Issued Colonize Order for Fleet {fleet.id}")

        return result


class MoveCommandHandler:
    """Handler for IssueMoveCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueMoveCommand."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve Fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Validation / Pathfinding
        path = session.preview_fleet_path(fleet, cmd.target_hex)

        if not path:
            if fleet.location == cmd.target_hex:
                pass  # Already there - no-op
            else:
                return validation_result(False, "Target is unreachable or invalid.")

        # 3. Apply
        order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            fleet.path = path

        return validation_result(True, "Move order issued.")


class BuildShipCommandHandler:
    """Handler for IssueBuildShipCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueBuildShipCommand."""
        # 1. Resolve Planet
        planet = session._get_planet_by_id(cmd.planet_id)
        if not planet:
            return validation_result(False, "Planet not found.")

        # 2. Apply
        planet.add_production(cmd.design_name, 1)

        return validation_result(True, f"Started construction of {cmd.design_name}.")


class InterceptCommandHandler:
    """Handler for IssueInterceptCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueInterceptCommand - creates a MOVE_TO_FLEET order."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve target fleet
        target_fleet = session._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return validation_result(False, "Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        log_info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return validation_result(True, "Intercept order issued.")


class JoinCommandHandler:
    """Handler for IssueJoinFleetCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueJoinFleetCommand - creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve target fleet
        target_fleet = session._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return validation_result(False, "Target fleet not found.")

        # 3. Create MOVE_TO_FLEET order first
        move_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 4. Then create JOIN_FLEET order
        join_order = FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        log_info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return validation_result(True, "Join fleet order issued.")


class ColonizeMissionCommandHandler:
    """Handler for QueueColonizeMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueColonizeMissionCommand - queues MOVE and COLONIZE orders."""
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.data.pathfinding import find_hybrid_path

        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Resolve planet (None is valid - means "any planet")
        planet = None
        if cmd.planet_id is not None:
            planet = session._get_planet_by_id(cmd.planet_id)
            if not planet:
                return validation_result(False, "Planet not found.")

        # 3. Determine start hex (current location or last order target)
        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

        # 4. Calculate path
        path = find_hybrid_path(session.galaxy, start_hex, cmd.target_hex)
        if not path:
            return validation_result(False, "No path found to target.")

        # 5. Auto-load population from colony at fleet's current location (BUG-70)
        origin_colony = session._find_colony_at_fleet(fleet)
        if origin_colony and origin_colony.populations:
            transfer_params = {
                'direction': 'load',
                'cargo_type': 'passengers',
                'amount': 0,  # 0 = load as much as possible
                'planet_id': origin_colony.id,
            }
            load_order = FleetOrder(OrderType.TRANSFER, target=transfer_params)
            fleet.add_order(load_order)

        # 6. Queue MOVE order if not already at target
        if start_hex != cmd.target_hex:
            move_order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
            fleet.add_order(move_order)

            # Set path immediately if it's the active order (and no load order was inserted)
            if len(fleet.orders) == 1:
                # Remove start hex from path before assigning
                if path and path[0] == fleet.location:
                    path = path[1:]
                fleet.path = path

        # 7. Queue COLONIZE order (target=None means "any available planet")
        colonize_order = FleetOrder(OrderType.COLONIZE, target=planet)
        fleet.add_order(colonize_order)

        planet_name = planet.name if planet else "Any Planet"
        log_info(f"GameSession: Queued Colonize Mission for Fleet {fleet.id} -> {planet_name}")
        return validation_result(True, "Colonize mission queued.")


class ClearOrdersCommandHandler:
    """Handler for ClearFleetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle ClearFleetOrdersCommand - clears all orders from fleet."""
        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Clear orders and path
        fleet.orders = []
        fleet.path = []

        log_info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return validation_result(True, "Fleet orders cleared.")


class TransferCommandHandler:
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations."""
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.validation import TransferValidator

        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return validation_result(False, "Fleet not found.")

        # 2. Find owning empire
        owning_empire = None
        for emp in session.empires:
            if fleet in emp.fleets:
                owning_empire = emp
                break

        if not owning_empire:
            return validation_result(False, "Fleet owner not found.")

        # 3. Resolve planet
        planet = session._get_planet_by_id(cmd.planet_id)
        if not planet:
            return validation_result(False, "Planet not found.")

        # 4. Validate
        result = TransferValidator.validate(
            session.galaxy, fleet, planet, cmd.cargo_type, cmd.direction, cmd.amount, cmd.species_id
        )

        # 5. Apply
        if result.is_valid:
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
            log_info(f"GameSession: Issued TRANSFER order for Fleet {fleet.id}")

        return result


def create_default_registry() -> CommandHandlerRegistry:
    """Create a registry with all standard command handlers registered.

    Returns:
        CommandHandlerRegistry with all 8 handlers registered.
    """
    registry = CommandHandlerRegistry()
    registry.register('IssueColonizeCommand', ColonizeCommandHandler())
    registry.register('IssueMoveCommand', MoveCommandHandler())
    registry.register('IssueBuildShipCommand', BuildShipCommandHandler())
    registry.register('IssueInterceptCommand', InterceptCommandHandler())
    registry.register('IssueJoinFleetCommand', JoinCommandHandler())
    registry.register('QueueColonizeMissionCommand', ColonizeMissionCommandHandler())
    registry.register('ClearFleetOrdersCommand', ClearOrdersCommandHandler())
    registry.register('IssueTransferCommand', TransferCommandHandler())
    return registry
