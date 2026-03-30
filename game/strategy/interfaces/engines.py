"""
Strategy Engine Interfaces for Dependency Injection.

PROJ-43 Phase 4: Interface contracts for TurnEngine sub-engines.
PROJ-161: Harvesting and Maintenance interfaces now per-tick only.

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
    from game.strategy.engine.consumable_management_engine import ResourceDepletion
    from game.strategy.data.galaxy import Galaxy


__all__ = [
    'IMovementEngine',
    'IProductionEngine',
    'IOrderProcessor',
    'IConflictEngine',
    'IConsumableEngine',
    'IPopulationEngine',
    'IResupplyEngine',
    'IHarvestingEngine',
    'IMaintenanceEngine',
    'IActionExecutionEngine',
    'IEnvironmentalHazardEngine',
    'IPlanetEnergyEngine',
    'IPlanetActionEngine',
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

    PROJ-158: Production is now entirely tick-based via process_construction_tick().
    The old process_production() and process_fleet_production() methods have been
    removed as they were empty stubs after the PROJ-79 migration.

    Implementations handle:
    - Per-tick resource consumption during construction
    - Mid-turn completion and spawning
    - Ship spawning
    - Complex spawning

    Example usage:
        engine = ProductionEngine()  # or MockProductionEngine for tests
        engine.process_construction_tick(tick, empires, galaxy, save_path)
    """

    @abstractmethod
    def process_construction_tick(
        self,
        tick: int,
        empires: List,
        galaxy: Any,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Process per-tick resource consumption for all construction queues.

        PROJ-75 Phase 4: Called each subturn tick (1-100) to deduct resources
        from empire pools for active construction.
        PROJ-79: Handles mid-turn completion and spawning.
        PROJ-233: Removed stale harvesting_engine parameter (removed in PROJ-161).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object
            save_path: Path to savegame folder for loading designs during spawning
        """
        pass


class IOrderProcessor(ABC):
    """
    Abstract interface for fleet order processing.

    PROJ-187/PROJ-207: Order processing is split between:
    - process_instant_orders(): Called every tick for JOIN_FLEET co-location
    - execute_action_order(): Called by ActionExecutionEngine when action completes

    Implementations handle:
    - Instant order processing (JOIN_FLEET when co-located)
    - Action order execution (COLONIZE, TRANSFER, superweapons) via ActionExecutionEngine
    - Order completion and cancellation

    Example usage:
        processor = OrderProcessor()  # or MockOrderProcessor for tests
        removed = processor.process_instant_orders(empires)
        # execute_action_order called by ActionExecutionEngine, not TurnEngine
        consumed = processor.execute_action_order(fleet, empire, galaxy)
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
    def execute_action_order(
        self,
        fleet: 'Fleet',
        empire: Any,
        galaxy: Any,
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List] = None
    ) -> bool:
        """
        Execute the fleet's current action order (COLONIZE, TRANSFER, superweapons).

        PROJ-207: Renamed from process_end_turn_orders for clarity.
        Called by ActionExecutionEngine when action progress reaches action_time.

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation
            component_registry: Optional component registry for colony pod lookup.
                               When provided, only the colony ship is removed.
            empires: Optional list of all empires (for superweapons like STELLERATE_STAR)

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
        empires: List,
        galaxy: Optional['Galaxy'] = None
    ) -> 'ConflictResult':
        """
        Resolve all conflicts between empires.

        Args:
            empires: List of Empire objects to check for conflicts
            galaxy: Optional Galaxy for environmental effect lookup (PROJ-189).
                   When provided, storm effects are applied to combat.

        Returns:
            ConflictResult with combat statistics
        """
        pass


class IConsumableEngine(ABC):
    """
    Abstract interface for resource consumption processing.

    Implementations handle:
    - Spreading per-turn costs over 100 ticks
    - Detecting resource depletion
    - Auto-disabling components when resources run out

    Example usage:
        engine = ConsumableManagementEngine()
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
    PROJ-161: Per-tick harvesting only (legacy full-turn method removed).

    Implementations handle:
    - Scanning facilities for harvester abilities
    - Extracting planetary resources based on quality (1/100th per tick)
    - Adding harvested resources to empire pool
    - Respecting storage limits and planet depletion
    - Storage recalculation each tick for mid-turn changes

    Example usage:
        engine = HarvestingEngine(registries=registries)
        # Called 100 times per turn in TurnEngine._process_tick():
        engine.process_harvesting_tick(tick, empires)
    """

    @abstractmethod
    def process_harvesting_tick(
        self,
        tick: int,
        empires: List
    ) -> None:
        """
        Process resource harvesting for one tick (1/100th of turn).

        PROJ-161: Per-tick harvesting spreads resource extraction across
        100 ticks. Each call extracts 1/100th of the per-turn harvest rate.

        Storage is recalculated each tick to handle mid-turn facility
        construction/destruction.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        pass


class IMaintenanceEngine(ABC):
    """
    Abstract interface for maintenance cost processing.

    PROJ-75 Phase 5: Interface for MaintenanceEngine.
    PROJ-161: Per-tick maintenance only (legacy full-turn method removed).

    Implementations handle:
    - Calculating maintenance costs (5% of build cost per turn, 1/100th per tick)
    - Deducting maintenance from empire resource pools
    - Scuttling entities that cannot be maintained (immediately on tick failure)
    - Cleaning up empty fleets after ship scuttles

    Example usage:
        engine = MaintenanceEngine()
        # Called 100 times per turn in TurnEngine._process_tick():
        events = engine.process_maintenance_tick(tick, empires)
    """

    @abstractmethod
    def process_maintenance_tick(
        self,
        tick: int,
        empires: List
    ) -> List:
        """
        Process maintenance for one tick (1/100th of turn).

        PROJ-161: Per-tick maintenance spreads costs across 100 ticks.
        Each call deducts 1/100th of the per-turn maintenance cost.
        Entities that cannot pay are immediately scuttled.

        Args:
            tick: Current tick number (1-100)
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


class IActionExecutionEngine(ABC):
    """
    Abstract interface for tick-based action order execution.

    PROJ-187: Strategy Orders Tick-Based Action System.

    Implementations handle:
    - Processing action orders (COLONIZE, TRANSFER, superweapons, etc.)
    - Tracking execution_progress across ticks
    - Delegating to order processor when action completes
    - Respecting fleet speed for action tick timing

    Example usage:
        engine = ActionExecutionEngine(order_processor, action_time_resolver)
        results = engine.process_action_ticks(empires, galaxy, tick, component_registry)
    """

    @abstractmethod
    def process_action_ticks(
        self,
        empires: List,
        galaxy: Any,
        tick: int,
        component_registry: Optional[Dict[str, Any]] = None,
        all_empires: Optional[List] = None
    ) -> List:
        """
        Process action ticks for all fleets with action orders.

        Iterates through all empires' fleets, increments execution_progress
        for fleets with action orders when their speed-based interval fires,
        and delegates to order processor when action completes.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for order execution
            tick: Current tick number (1-100)
            component_registry: Optional component registry for ability lookup
            all_empires: Optional list of all empires (for superweapons)

        Returns:
            List of ActionTickResult records for completed/progressed actions
        """
        pass


class IEnvironmentalHazardEngine(ABC):
    """
    Abstract interface for environmental hazard processing.

    PROJ-189: Storms Environmental Hazards.

    Implementations handle:
    - Processing storm effects (damage, fuel drain) each tick
    - Querying AreaEffectManager for effects at fleet locations
    - Applying damage and fuel drain to ships in storm hexes
    - Tracking environmental events for logging/UI

    Example usage:
        engine = EnvironmentalHazardEngine(area_effect_manager)
        events = engine.process_environmental_tick(tick, empires, galaxy)
    """

    @abstractmethod
    def process_environmental_tick(
        self,
        tick: int,
        empires: List,
        galaxy: Any
    ) -> List:
        """
        Process environmental effects for one tick.

        For each fleet in each empire, queries storm effects at the
        fleet's location and applies damage and fuel drain if in storm.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial queries

        Returns:
            List of EnvironmentalEvent records for affected fleets
        """
        pass


class IPlanetEnergyEngine(ABC):
    """
    Abstract interface for planet energy generation and consumption.

    PROJ-237: Manages per-planet energy pools.

    Implementations handle:
    - Scanning facilities for energy generator/storage abilities
    - Per-tick energy generation (1/100th of per-turn rate)
    - Per-tick energy consumption for active shields
    - Auto-deactivation of shields when energy is depleted
    - Clamping energy to [0, capacity]

    Example usage:
        engine = PlanetEnergyEngine(registries=registries)
        engine.process_energy_tick(tick, empires)
    """

    @abstractmethod
    def process_energy_tick(
        self,
        tick: int,
        empires: List
    ) -> None:
        """
        Process energy generation/consumption for one tick (1/100th of turn).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        pass


class IPlanetActionEngine(ABC):
    """
    Abstract interface for tick-based planet order execution.

    PROJ-237: Processes planet orders (shield activation, etc.)

    Implementations handle:
    - Processing planet action orders per tick
    - Tracking execution_progress across ticks
    - Executing orders when progress reaches action_time
    - Handling destroyed facilities (skip stale orders)

    Example usage:
        engine = PlanetActionEngine(registries=registries)
        results = engine.process_planet_actions_tick(tick, empires, component_registry)
    """

    @abstractmethod
    def process_planet_actions_tick(
        self,
        tick: int,
        empires: List,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> List:
        """
        Process planet action ticks for all colonies with planet orders.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            component_registry: Optional component registry for ability lookup

        Returns:
            List of result records for completed/progressed actions
        """
        pass
