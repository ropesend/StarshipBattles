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
    from game.core.hex_math import HexCoord
    from game.strategy.engine.fleet_movement_engine import MovementResult
    from game.strategy.engine.conflict_resolution_engine import ConflictResult
    from game.strategy.engine.resource_management_engine import ResourceDepletion


__all__ = [
    'IMovementEngine',
    'IProductionEngine',
    'IOrderProcessor',
    'IConflictEngine',
    'IResourceEngine',
    'IPopulationEngine',
    'IResupplyEngine',
    'IHarvestingEngine',
    'IMaintenanceEngine',
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
    - Construction queue processing for colonies
    - Construction queue processing for fleets with space yards
    - Per-tick resource consumption during construction (PROJ-75)
    - Ship spawning
    - Complex spawning

    Example usage:
        engine = ProductionEngine()  # or MockProductionEngine for tests
        engine.process_construction_tick(tick, empires, galaxy)
        engine.process_production(empires, galaxy, save_path)
        engine.process_fleet_production(empires, galaxy, save_path)
    """

    @abstractmethod
    def process_construction_tick(
        self,
        tick: int,
        empires: List,
        galaxy: Any
    ) -> None:
        """
        Process per-tick resource consumption for all construction queues.

        PROJ-75 Phase 4: Called each subturn tick (1-100) to deduct resources
        from empire pools for active construction.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object
        """
        pass

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

    @abstractmethod
    def process_fleet_production(
        self,
        empires: List,
        galaxy: Any = None,
        save_path: Optional[str] = None
    ) -> None:
        """
        Process construction queues for all fleets with space yards.

        PROJ-67 Phase 3: Fleet-based production processing.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for complex spawning (planet proximity check)
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


class IResupplyEngine(ABC):
    """
    Abstract interface for fuel generation and fleet resupply processing.

    PROJ-74 Phase 3: Interface for ResupplyEngine.

    Implementations handle:
    - Fuel generation at planetary facilities with fuel synthesizers
    - Fuel transfer from facilities to fleets at the same location
    - Range equalization across fleet ships

    Example usage:
        engine = ResupplyEngine(registries=registries)
        gen_events = engine.process_fuel_generation(tick, empires)
        resupply_events = engine.process_fleet_resupply(tick, empires, galaxy)
    """

    @abstractmethod
    def process_fuel_generation(
        self,
        tick: int,
        empires: List
    ) -> List:
        """
        Process fuel generation at facilities.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResupplyEvent records
        """
        pass

    @abstractmethod
    def process_fleet_resupply(
        self,
        tick: int,
        empires: List,
        galaxy: Any
    ) -> List:
        """
        Process fuel transfer from facilities to fleets.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial lookup

        Returns:
            List of ResupplyEvent records
        """
        pass


class IHarvestingEngine(ABC):
    """
    Abstract interface for planetary resource harvesting.

    PROJ-75 Phase 2: Interface for HarvestingEngine.

    Implementations handle:
    - Scanning facilities for harvester abilities
    - Extracting planetary resources based on quality
    - Adding harvested resources to empire pool
    - Respecting storage limits and planet depletion

    Example usage:
        engine = HarvestingEngine(registries=registries)
        engine.process_harvesting(empires)
    """

    @abstractmethod
    def process_harvesting(
        self,
        empires: List
    ) -> None:
        """
        Process resource harvesting for all empires.

        Iterates through all empires, colonies, and facilities,
        extracting planetary resources to empire pools based on
        harvester abilities and planet resource quality.

        Args:
            empires: List of Empire objects to process
        """
        pass


class IMaintenanceEngine(ABC):
    """
    Abstract interface for maintenance cost processing.

    PROJ-75 Phase 5: Interface for MaintenanceEngine.

    Implementations handle:
    - Calculating maintenance costs (5% of build cost per turn)
    - Deducting maintenance from empire resource pools
    - Scuttling entities that cannot be maintained
    - Cleaning up empty fleets after ship scuttles

    Example usage:
        engine = MaintenanceEngine()
        events = engine.process_maintenance(empires)
    """

    @abstractmethod
    def process_maintenance(
        self,
        empires: List
    ) -> List:
        """
        Process maintenance for all empires.

        Deducts 5% of build cost per turn for each operational facility
        and ship. Scuttles entities that cannot be maintained.

        Args:
            empires: List of Empire objects to process

        Returns:
            List of ScuttleEvent records for scuttled entities
        """
        pass


class IPopulationEngine(ABC):
    """
    Abstract interface for population growth processing.

    Implementations handle:
    - Logistic population growth per species per colony
    - Habitability scoring affecting carrying capacity
    - Happiness modifiers on growth rate
    - Population decline when above carrying capacity

    Example usage:
        engine = PopulationEngine()  # or MockPopulationEngine for tests
        engine.process_population_growth(empires)
    """

    @abstractmethod
    def process_population_growth(
        self,
        empires: List
    ) -> None:
        """
        Process population growth for all empires.

        Iterates through all empires, colonies, and species populations,
        applying logistic growth based on habitability, happiness, and
        race aptitudes.

        Args:
            empires: List of Empire objects to process
        """
        pass
