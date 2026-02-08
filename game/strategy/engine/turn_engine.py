"""
Turn Engine - Strategy Layer Turn Orchestration

PROJ-36: Refactored to be a lightweight orchestrator that delegates
to specialized engines.

PROJ-43 Phase 4: Full constructor dependency injection for all engines.

Turn Phases:
    1. SUBTURN LOOP (100 ticks):
       - Phase 0: Per-turn resources (via ResourceManagementEngine)
       - Phase 0a: Fuel generation at facilities (via ResupplyEngine)
       - Phase 0b: Fleet resupply from facilities (via ResupplyEngine)
       - Phase 1: Instant orders (via FleetOrderProcessor)
       - Phase 2: Calculate moves (via FleetMovementEngine)
       - Phase 3: Apply moves (via FleetMovementEngine)
       - Phase 4: Combat (via ConflictResolutionEngine)
    2. END-OF-TURN ORDERS (via FleetOrderProcessor)
    3. PRODUCTION (via ProductionEngine)

Delegated Engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - FleetOrderProcessor: Order lifecycle management
    - ConflictResolutionEngine: Combat detection and resolution
    - ResourceManagementEngine: Per-turn resource consumption
    - ResupplyEngine: Fuel generation and fleet resupply

Dependency Injection:
    TurnEngine accepts optional engine parameters for all sub-engines.
    Default: Creates standard implementations when not provided.
    Testing: Mock engines can be injected for fast, isolated tests.

Example:
    # Default usage
    engine = TurnEngine()
    engine.process_turn(empires, galaxy, save_path="saves/game1")

    # Testing with mock engines
    engine = TurnEngine(
        movement_engine=mock_movement,
        production_engine=mock_production,
        conflict_engine=mock_conflict
    )
"""
from game.core.validation import ValidationResult
from game.core.registry import GameRegistries, get_default_registries
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
    from game.strategy.interfaces.engines import (
        IMovementEngine,
        IProductionEngine,
        IOrderProcessor,
        IConflictEngine,
        IResourceEngine,
        IPopulationEngine,
        IResupplyEngine,
    )
    from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
    from game.strategy.engine.production_engine import ProductionEngine
    from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
    from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
    from game.strategy.engine.resource_management_engine import ResourceManagementEngine


class TurnEngine:
    """
    Engine for processing strategy turns.

    PROJ-11 Phase 4: Supports dependency injection of IBattleResolver
    for clean separation between strategy and simulation layers.

    PROJ-12 Phase 3: Delegates to specialized engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - FleetOrderProcessor: Order lifecycle management

    PROJ-36: Additional delegation to:
    - ConflictResolutionEngine: Combat detection and resolution
    - ResourceManagementEngine: Per-turn resource consumption

    PROJ-43 Phase 4: Full constructor dependency injection for all engines.
    All engines can be injected via constructor for testing and extensibility.
    """

    def __init__(
        self,
        battle_resolver: Optional['IBattleResolver'] = None,
        *,
        registries: Optional[GameRegistries] = None,
        movement_engine: Optional['IMovementEngine'] = None,
        production_engine: Optional['IProductionEngine'] = None,
        order_processor: Optional['IOrderProcessor'] = None,
        conflict_engine: Optional['IConflictEngine'] = None,
        resource_engine: Optional['IResourceEngine'] = None,
        population_engine: Optional['IPopulationEngine'] = None,
        resupply_engine: Optional['IResupplyEngine'] = None,
    ):
        """
        Initialize the turn engine.

        PROJ-43 Phase 4: All engines can be injected for testing.
        PROJ-50: Added registries parameter for DI to sub-engines.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
            registries: Optional GameRegistries for DI. Falls back to
                       get_default_registries() if None.
            movement_engine: Optional movement engine (IMovementEngine).
                           If None, creates FleetMovementEngine.
            production_engine: Optional production engine (IProductionEngine).
                           If None, creates ProductionEngine.
            order_processor: Optional order processor (IOrderProcessor).
                           If None, creates FleetOrderProcessor.
            conflict_engine: Optional conflict engine (IConflictEngine).
                           If None, creates ConflictResolutionEngine.
            resource_engine: Optional resource engine (IResourceEngine).
                           If None, creates ResourceManagementEngine.
            population_engine: Optional population engine (IPopulationEngine).
                           If None, creates PopulationEngine.
            resupply_engine: Optional resupply engine (IResupplyEngine).
                           If None, creates ResupplyEngine.
        """
        # PROJ-11: Inject battle resolver for clean layer separation
        if battle_resolver is None:
            from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
            self._battle_resolver = SimulationBattleResolver()
        else:
            self._battle_resolver = battle_resolver

        # PROJ-50/PROJ-58: Store registries for passing to sub-engines
        if registries is not None:
            self._registries = registries
        else:
            self._registries = get_default_registries()

        # PROJ-43 Phase 4: Store injected engines or None for lazy init
        self._movement_engine: Optional['IMovementEngine'] = movement_engine
        self._production_engine: Optional['IProductionEngine'] = production_engine
        self._order_processor: Optional['IOrderProcessor'] = order_processor
        self._conflict_engine: Optional['IConflictEngine'] = conflict_engine
        self._resource_engine: Optional['IResourceEngine'] = resource_engine
        self._population_engine: Optional['IPopulationEngine'] = population_engine
        self._resupply_engine: Optional['IResupplyEngine'] = resupply_engine

    @property
    def movement_engine(self) -> 'IMovementEngine':
        """Return movement engine, lazily creating default if not injected."""
        if self._movement_engine is None:
            from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
            self._movement_engine = FleetMovementEngine()
        return self._movement_engine

    @property
    def production_engine(self) -> 'IProductionEngine':
        """Return production engine, lazily creating default if not injected."""
        if self._production_engine is None:
            from game.strategy.engine.production_engine import ProductionEngine
            self._production_engine = ProductionEngine()
        return self._production_engine

    @property
    def order_processor(self) -> 'IOrderProcessor':
        """Return order processor, lazily creating default if not injected."""
        if self._order_processor is None:
            from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
            self._order_processor = FleetOrderProcessor()
        return self._order_processor

    @property
    def conflict_engine(self) -> 'IConflictEngine':
        """Return conflict engine, lazily creating default if not injected."""
        if self._conflict_engine is None:
            from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
            # PROJ-50: Pass registries for strict DI compliance
            self._conflict_engine = ConflictResolutionEngine(
                self._battle_resolver, registries=self._registries
            )
        return self._conflict_engine

    @property
    def resource_engine(self) -> 'IResourceEngine':
        """Return resource engine, lazily creating default if not injected."""
        if self._resource_engine is None:
            from game.strategy.engine.resource_management_engine import ResourceManagementEngine
            # PROJ-50: Pass registries for strict DI
            self._resource_engine = ResourceManagementEngine(registries=self._registries)
        return self._resource_engine

    @property
    def population_engine(self) -> 'IPopulationEngine':
        """Return population engine, lazily creating default if not injected."""
        if self._population_engine is None:
            from game.strategy.engine.population_engine import PopulationEngine
            self._population_engine = PopulationEngine()
        return self._population_engine

    @property
    def resupply_engine(self) -> 'IResupplyEngine':
        """Return resupply engine, lazily creating default if not injected."""
        if self._resupply_engine is None:
            from game.strategy.engine.resupply_engine import ResupplyEngine
            self._resupply_engine = ResupplyEngine(registries=self._registries)
        return self._resupply_engine

    def process_turn(self, empires, galaxy, save_path=None):
        """
        Execute one full turn (100 sub-ticks).

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial calculations
            save_path: Path to savegame folder for loading designs during production
        """
        # 1. Subturn Loop (Movement & Combat)
        for tick in range(1, 101):
            self._process_tick(tick, empires, galaxy)

        # 2. End-of-Turn Orders (Static actions like Colonize)
        for empire in empires:
            # Iterate copy since fleets may be modified during processing
            # (e.g., colonization can remove/dissolve fleets)
            for fleet in list(empire.fleets):
                self._process_end_turn_orders(fleet, empire, galaxy)

        # 3. Production Phase (Colonies)
        self.process_production(empires, galaxy, save_path)

        # 4. Fleet Production Phase (PROJ-67)
        self.production_engine.process_fleet_production(empires, galaxy, save_path)

        # 5. Population Growth Phase (PROJ-68)
        self.population_engine.process_population_growth(empires)
        
    def validate_colonize_order(self, galaxy, fleet, target_planet) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet (or 'Any' if target_planet is None).

        PROJ-36: Delegates to ColonizeValidator.
        PROJ-55: Passes component_registry for planet-type validation.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'

        Returns:
            ValidationResult
        """
        from game.strategy.validation import ColonizeValidator
        # PROJ-55: Pass component registry for colony pod validation
        component_registry = getattr(self._registries, 'components', None)
        return ColonizeValidator.validate(galaxy, fleet, target_planet, component_registry)

    def process_production(self, empires, galaxy=None, save_path=None):
        """Process construction queues for all colonies.

        PROJ-12 Phase 3: Delegates to ProductionEngine.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for fleet spawning
            save_path: Path to savegame folder for loading designs
        """
        self.production_engine.process_production(empires, galaxy, save_path)

    def _process_tick(self, tick, empires, galaxy):
        """Process 1 sub-tick of movement and combat.

        PROJ-12 Phase 3: Delegates to specialized engines.
        PROJ-74 Phase 5: Added fuel generation and fleet resupply phases.

        Seven-phase processing:
        Phase 0: Per-turn resource consumption (1/100th of per_turn costs)
        Phase 0a: Fuel generation at facilities (via ResupplyEngine)
        Phase 0b: Fleet resupply from facilities (via ResupplyEngine)
        Phase 1: Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 2: Calculate paths/next moves for all fleets (based on current positions)
        Phase 3: Apply all movements simultaneously
        Phase 4: Combat
        """

        # --- Phase 0: Per-turn Resource Consumption ---
        # PROJ-36: Delegate to ResourceManagementEngine
        self.resource_engine.process_per_turn_consumption(tick, empires)

        # --- Phase 0a: Fuel generation at facilities ---
        # PROJ-74: Generate fuel at planetary facilities with fuel synthesizers
        self.resupply_engine.process_fuel_generation(tick, empires)

        # --- Phase 0b: Fleet resupply from facilities ---
        # PROJ-74: Transfer fuel from facilities to co-located fleets
        self.resupply_engine.process_fleet_resupply(tick, empires, galaxy)

        # --- Phase 1: Instant Orders (JOIN_FLEET) ---
        # PROJ-12: Delegate to FleetOrderProcessor
        self.order_processor.process_instant_orders(empires)

        # --- Phase 2: Calculate Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        move_queue = self.movement_engine.collect_movements(empires, galaxy, tick)

        # --- Phase 3: Apply Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        self.movement_engine.apply_movements(move_queue, galaxy)

        # --- Phase 4: Combat ---
        # PROJ-36: Delegate to ConflictResolutionEngine
        self.conflict_engine.resolve_all_conflicts(empires)

    def _process_end_turn_orders(self, fleet, empire, galaxy):
        """Process static orders like COLONIZE.

        PROJ-12 Phase 3: Delegates to FleetOrderProcessor.
        PROJ-55: Passes component_registry for colony pod ship removal.

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise.
        """
        # PROJ-55: Pass component registry for colony pod ship removal
        component_registry = getattr(self._registries, 'components', None)
        return self.order_processor.process_end_turn_orders(
            fleet, empire, galaxy, component_registry=component_registry
        )


def create_default_turn_engine() -> TurnEngine:
    """
    Factory function to create a TurnEngine with all default engines.

    PROJ-43 Phase 4: Simplifies instantiation for production code.

    This factory creates a TurnEngine with all default sub-engines.
    For testing, use the TurnEngine constructor directly to inject
    mock engines.

    Returns:
        TurnEngine with default implementations of all sub-engines.

    Example:
        # Production code
        engine = create_default_turn_engine()
        engine.process_turn(empires, galaxy, save_path)

        # Test code - use constructor for mocking
        engine = TurnEngine(
            movement_engine=mock_movement,
            production_engine=mock_production
        )
    """
    return TurnEngine()

