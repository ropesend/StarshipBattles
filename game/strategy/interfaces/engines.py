"""
Strategy Engine Interfaces for Dependency Injection.

PROJ-43 Phase 4: Interface contracts for TurnEngine sub-engines.

These interfaces enable:
- Constructor dependency injection in TurnEngine
- Unit testing with mock engines
- Alternative implementations for different scenarios
- Clean separation of concerns

Each interface defines the contract that TurnEngine depends on,
allowing the concrete implementations to be injected at construction time.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.hex_math import HexCoord
    from game.strategy.engine.fleet_movement_engine import MovementResult
    from game.strategy.engine.conflict_resolution_engine import ConflictResult
    from game.strategy.engine.resource_management_engine import ResourceDepletion


__all__ = [
    'IMovementEngine',
    'IProductionEngine',
    'IOrderProcessor',
    'IConflictEngine',
    'IResourceEngine',
]


class IMovementEngine(ABC):
    """
    Abstract interface for fleet movement processing.

    Implementations handle:
    - Movement calculation for fleets
    - Path management and recalculation
    - Movement resource consumption
    - Warp travel handling

    Example usage:
        engine = FleetMovementEngine()  # or MockMovementEngine for tests
        move_queue = engine.collect_movements(empires, galaxy, tick)
        engine.apply_movements(move_queue, galaxy)
    """

    @abstractmethod
    def collect_movements(
        self,
        empires: List,
        galaxy: Any,
        tick: int
    ) -> List[Tuple['Fleet', 'HexCoord']]:
        """
        Collect all fleet movements for this tick.

        Calculates which fleets should move based on speed and tick,
        and determines their next hex.

        Args:
            empires: List of Empire objects
            galaxy: Galaxy object for pathfinding
            tick: Current tick number (1-100)

        Returns:
            List of (fleet, next_hex) tuples for fleets that should move
        """
        pass

    @abstractmethod
    def apply_movements(
        self,
        move_queue: List[Tuple['Fleet', 'HexCoord']],
        galaxy: Any
    ) -> List['MovementResult']:
        """
        Apply all movements in the queue.

        Args:
            move_queue: List of (fleet, next_hex) tuples
            galaxy: Galaxy object

        Returns:
            List of MovementResult objects
        """
        pass

    @abstractmethod
    def calculate_next_hex(
        self,
        fleet: 'Fleet',
        galaxy: Any
    ) -> Optional['HexCoord']:
        """
        Calculate (but don't apply) the next hex for a fleet.

        Args:
            fleet: Fleet to calculate movement for
            galaxy: Galaxy object for pathfinding

        Returns:
            Next hex coordinate to move to, or None if no movement
        """
        pass


class IProductionEngine(ABC):
    """
    Abstract interface for production/construction processing.

    Implementations handle:
    - Construction queue processing
    - Ship spawning
    - Complex spawning

    Example usage:
        engine = ProductionEngine()  # or MockProductionEngine for tests
        engine.process_production(empires, galaxy, save_path)
    """

    @abstractmethod
    def process_production(
        self,
        empires: List,
        galaxy: Any = None,
        save_path: Optional[str] = None
    ) -> None:
        """
        Process construction queues for all colonies.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for fleet spawning
            save_path: Path to savegame folder for loading designs
        """
        pass


class IOrderProcessor(ABC):
    """
    Abstract interface for fleet order processing.

    Implementations handle:
    - Instant order processing (JOIN_FLEET when co-located)
    - End-of-turn order processing (COLONIZE, JOIN_FLEET)
    - Order completion and cancellation

    Example usage:
        processor = FleetOrderProcessor()  # or MockOrderProcessor for tests
        removed = processor.process_instant_orders(empires)
        consumed = processor.process_end_turn_orders(fleet, empire, galaxy)
    """

    @abstractmethod
    def process_instant_orders(
        self,
        empires: List
    ) -> List[Tuple]:
        """
        Process instant orders during tick (JOIN_FLEET when co-located).

        Args:
            empires: List of Empire objects

        Returns:
            List of (empire, fleet) tuples for removed fleets
        """
        pass

    @abstractmethod
    def process_end_turn_orders(
        self,
        fleet: 'Fleet',
        empire: Any,
        galaxy: Any,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Process static orders at end of turn (COLONIZE, JOIN_FLEET).

        PROJ-55: Added component_registry for colony pod ship removal.

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation
            component_registry: Optional component registry for colony pod lookup.
                               When provided, only the colony ship is removed.

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise
        """
        pass


class IConflictEngine(ABC):
    """
    Abstract interface for combat conflict resolution.

    Implementations handle:
    - Detection of multi-empire conflicts at hexes
    - Battle resolution via IBattleResolver interface
    - Tracking combat results

    Example usage:
        engine = ConflictResolutionEngine(battle_resolver)
        result = engine.resolve_all_conflicts(empires)
    """

    @abstractmethod
    def resolve_all_conflicts(
        self,
        empires: List
    ) -> 'ConflictResult':
        """
        Resolve all conflicts between empires.

        Args:
            empires: List of Empire objects to check for conflicts

        Returns:
            ConflictResult with combat statistics
        """
        pass


class IResourceEngine(ABC):
    """
    Abstract interface for resource consumption processing.

    Implementations handle:
    - Spreading per-turn costs over 100 ticks
    - Detecting resource depletion
    - Auto-disabling components when resources run out

    Example usage:
        engine = ResourceManagementEngine()
        depletions = engine.process_per_turn_consumption(tick, empires)
    """

    @abstractmethod
    def process_per_turn_consumption(
        self,
        tick: int,
        empires: List
    ) -> List['ResourceDepletion']:
        """
        Process per-turn resource consumption (1/100th per tick).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResourceDepletion events that occurred this tick
        """
        pass
