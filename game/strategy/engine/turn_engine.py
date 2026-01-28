"""
Turn Engine - Strategy Layer Turn Orchestration

PROJ-36: Refactored to be a lightweight orchestrator that delegates
to specialized engines.

Turn Phases:
    1. SUBTURN LOOP (100 ticks):
       - Phase 0: Per-turn resources (via ResourceManagementEngine)
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

Dependency Injection:
    TurnEngine accepts an optional IBattleResolver for combat resolution.
    Default: SimulationBattleResolver (full battle simulation)
    Testing: Mock resolvers can be injected for fast strategy tests.

Example:
    engine = TurnEngine()
    engine.process_turn(empires, galaxy, save_path="saves/game1")
"""
from game.core.validation import ValidationResult
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
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
    """

    def __init__(self, battle_resolver: Optional['IBattleResolver'] = None):
        """
        Initialize the turn engine.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
        """
        # PROJ-11: Inject battle resolver for clean layer separation
        if battle_resolver is None:
            from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
            self._battle_resolver = SimulationBattleResolver()
        else:
            self._battle_resolver = battle_resolver

        # PROJ-12 Phase 3: Lazy-initialized specialized engines
        self._movement_engine: Optional['FleetMovementEngine'] = None
        self._production_engine: Optional['ProductionEngine'] = None
        self._order_processor: Optional['FleetOrderProcessor'] = None

        # PROJ-36: Conflict resolution engine
        self._conflict_engine: Optional['ConflictResolutionEngine'] = None

        # PROJ-36: Resource management engine
        self._resource_engine: Optional['ResourceManagementEngine'] = None

    @property
    def movement_engine(self) -> 'FleetMovementEngine':
        """Lazy initialization of FleetMovementEngine."""
        if self._movement_engine is None:
            from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
            self._movement_engine = FleetMovementEngine()
        return self._movement_engine

    @property
    def production_engine(self) -> 'ProductionEngine':
        """Lazy initialization of ProductionEngine."""
        if self._production_engine is None:
            from game.strategy.engine.production_engine import ProductionEngine
            self._production_engine = ProductionEngine()
        return self._production_engine

    @property
    def order_processor(self) -> 'FleetOrderProcessor':
        """Lazy initialization of FleetOrderProcessor."""
        if self._order_processor is None:
            from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
            self._order_processor = FleetOrderProcessor()
        return self._order_processor

    @property
    def conflict_engine(self) -> 'ConflictResolutionEngine':
        """Lazy initialization of ConflictResolutionEngine."""
        if self._conflict_engine is None:
            from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
            self._conflict_engine = ConflictResolutionEngine(self._battle_resolver)
        return self._conflict_engine

    @property
    def resource_engine(self) -> 'ResourceManagementEngine':
        """Lazy initialization of ResourceManagementEngine."""
        if self._resource_engine is None:
            from game.strategy.engine.resource_management_engine import ResourceManagementEngine
            self._resource_engine = ResourceManagementEngine()
        return self._resource_engine

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

        # 3. Production Phase
        self.process_production(empires, galaxy, save_path)
        
    def validate_colonize_order(self, galaxy, fleet, target_planet) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet (or 'Any' if target_planet is None).

        PROJ-36: Delegates to ColonizeValidator.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'

        Returns:
            ValidationResult
        """
        from game.strategy.validation import ColonizeValidator
        return ColonizeValidator.validate(galaxy, fleet, target_planet)

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

        Five-phase processing:
        Phase 0: Per-turn resource consumption (1/100th of per_turn costs)
        Phase 1: Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 2: Calculate paths/next moves for all fleets (based on current positions)
        Phase 3: Apply all movements simultaneously
        Phase 4: Combat
        """

        # --- Phase 0: Per-turn Resource Consumption ---
        # PROJ-36: Delegate to ResourceManagementEngine
        self.resource_engine.process_per_turn_consumption(tick, empires)

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

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise.
        """
        return self.order_processor.process_end_turn_orders(fleet, empire, galaxy)

