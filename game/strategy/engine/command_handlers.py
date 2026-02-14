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

from game.core.logger import log_info
from game.core.validation import ValidationResult

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


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
            return ValidationResult(is_valid=False, errors=[f"Unknown command type: {command_name}"])
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
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

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
                species_id = origin_colony.populations[0].race_id if origin_colony.populations else "default"
                transfer_params = {
                    'direction': 'load',
                    'cargo_type': 'passengers',
                    'amount': 0,
                    'planet_id': origin_colony.id,
                    'species_id': species_id
                }
                load_order = FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)
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
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Validation / Pathfinding
        path = session.preview_fleet_path(fleet, cmd.target_hex)

        if not path:
            if fleet.location == cmd.target_hex:
                pass  # Already there - no-op
            else:
                return ValidationResult(is_valid=False, errors=["Target is unreachable or invalid."])

        # 3. Apply
        order = FleetOrder(OrderType.MOVE, target=cmd.target_hex)
        fleet.add_order(order)

        # Optimization: Set path immediately if it's the active order
        if len(fleet.orders) == 1:
            fleet.path = path

        return ValidationResult()


class BuildShipCommandHandler:
    """Handler for IssueBuildShipCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueBuildShipCommand."""
        # 1. Resolve Planet
        planet = session._get_planet_by_id(cmd.planet_id)
        if not planet:
            return ValidationResult(is_valid=False, errors=["Planet not found."])

        # 2. Apply
        planet.add_production(cmd.design_name, 1)

        return ValidationResult()


class InterceptCommandHandler:
    """Handler for IssueInterceptCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueInterceptCommand - creates a MOVE_TO_FLEET order."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Resolve target fleet
        target_fleet = session._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return ValidationResult(is_valid=False, errors=["Target fleet not found."])

        # 3. Create MOVE_TO_FLEET order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)

        log_info(f"GameSession: Issued Intercept Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult()


class JoinCommandHandler:
    """Handler for IssueJoinFleetCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueJoinFleetCommand - creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        from game.strategy.data.fleet import FleetOrder, OrderType

        # 1. Resolve source fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Resolve target fleet
        target_fleet = session._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return ValidationResult(is_valid=False, errors=["Target fleet not found."])

        # 3. Create MOVE_TO_FLEET order first
        move_order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(move_order)

        # 4. Then create JOIN_FLEET order
        join_order = FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)
        fleet.add_order(join_order)

        log_info(f"GameSession: Issued Join Fleet Order for Fleet {fleet.id} -> Fleet {target_fleet.id}")
        return ValidationResult()


class ColonizeMissionCommandHandler:
    """Handler for QueueColonizeMissionCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle QueueColonizeMissionCommand - queues MOVE and COLONIZE orders."""
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.data.pathfinding import find_hybrid_path
        from game.strategy.validation import ColonizeValidator

        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Resolve planet (None is valid - means "any planet")
        planet = None
        if cmd.planet_id is not None:
            planet = session._get_planet_by_id(cmd.planet_id)
            if not planet:
                return ValidationResult(is_valid=False, errors=["Planet not found."])

            # PROJ-140 Phase 4: Validate pod match for specific planet targets
            # Get component registry from turn_engine
            component_registry = None
            turn_engine = getattr(session, 'turn_engine', None)
            if turn_engine is not None:
                registries = getattr(turn_engine, '_registries', None)
                if registries is not None:
                    component_registry = getattr(registries, 'components', None)

            if component_registry is not None:
                planet_type_str = planet.planet_type.name

                # Check if fleet has a matching colony pod
                ship_with_pod = ColonizeValidator.find_ship_with_colony_pod(
                    fleet, planet_type_str, component_registry
                )

                if ship_with_pod is None:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"No ship in fleet has {planet_type_str} colony pod."],
                        error_code="NO_COLONY_POD"
                    )

                # Check chain limits - ensure not over-committed
                available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
                committed = ColonizeValidator.get_committed_colony_pods(fleet)

                available_count = available.get(planet_type_str, 0)
                committed_count = committed.get(planet_type_str, 0)

                if committed_count >= available_count:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"All {planet_type_str} colony pods already assigned."],
                        error_code="COLONY_POD_EXHAUSTED"
                    )

        # 3. Determine start hex (current location or last order target)
        start_hex = fleet.location
        if fleet.orders:
            last = fleet.orders[-1]
            if last.type == OrderType.MOVE:
                start_hex = last.target

        # 4. Calculate path
        path = find_hybrid_path(session.galaxy, start_hex, cmd.target_hex)
        if not path:
            return ValidationResult(is_valid=False, errors=["No path found to target."])

        # 5. Auto-load population from colony at fleet's current location (BUG-70)
        origin_colony = session._find_colony_at_fleet(fleet)
        if origin_colony and origin_colony.populations:
            species_id = origin_colony.populations[0].race_id if origin_colony.populations else "default"
            transfer_params = {
                'direction': 'load',
                'cargo_type': 'passengers',
                'amount': 0,  # 0 = load as much as possible
                'planet_id': origin_colony.id,
                'species_id': species_id
            }
            load_order = FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)
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
        return ValidationResult()


class ClearOrdersCommandHandler:
    """Handler for ClearFleetOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle ClearFleetOrdersCommand - clears all orders from fleet."""
        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Clear orders and path
        fleet.orders = []
        fleet.path = []

        log_info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return ValidationResult()


class TransferCommandHandler:
    """Handler for IssueTransferCommand."""

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        """Handle IssueTransferCommand - creates TRANSFER order for cargo operations."""
        from game.strategy.data.fleet import FleetOrder, OrderType
        from game.strategy.validation import TransferValidator

        # 1. Resolve fleet
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])

        # 2. Find owning empire
        owning_empire = None
        for emp in session.empires:
            if fleet in emp.fleets:
                owning_empire = emp
                break

        if not owning_empire:
            return ValidationResult(is_valid=False, errors=["Fleet owner not found."])

        # 3. Resolve planet
        planet = session._get_planet_by_id(cmd.planet_id)
        if not planet:
            return ValidationResult(is_valid=False, errors=["Planet not found."])

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
