"""
Turn Engine - Strategy Layer Turn Orchestration

PROJ-36: Refactored to be a lightweight orchestrator that delegates
to specialized engines.

PROJ-43 Phase 4: Full constructor dependency injection for all engines.

PROJ-161: Moved harvesting and maintenance into per-tick processing.

Turn Phases:
    1. SUBTURN LOOP (100 ticks):
       - Phase 0:   Harvesting (via HarvestingEngine) - 1/100th per tick
       - Phase 0a:  Maintenance (via MaintenanceEngine) - 1/100th per tick, immediate scuttle
       - Phase 0b:  Per-turn resources (via ResourceManagementEngine)
       - Phase 0c:  Fuel generation at facilities (via ResupplyEngine)
       - Phase 0d:  Fleet resupply from facilities (via ResupplyEngine)
       - Phase 0e:  Construction resource consumption (via ProductionEngine)
       - Phase 1:   Instant orders (via FleetOrderProcessor)
       - Phase 1.5: Action orders (via ActionExecutionEngine) - COLONIZE, TRANSFER, superweapons
       - Phase 2:   Calculate moves (via FleetMovementEngine)
       - Phase 3:   Apply moves (via FleetMovementEngine)
       - Phase 4:   Combat (via ConflictResolutionEngine)
    2. POPULATION GROWTH (via PopulationEngine)

Delegated Engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - FleetOrderProcessor: Order lifecycle management (instant orders only)
    - ActionExecutionEngine: Tick-based action order execution
    - ConflictResolutionEngine: Combat detection and resolution
    - ResourceManagementEngine: Per-turn resource consumption
    - ResupplyEngine: Fuel generation and fleet resupply
    - HarvestingEngine: Planetary resource extraction to empire pool
    - MaintenanceEngine: Maintenance cost deduction and scuttling

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
from game.core.registry import GameRegistries, get_default_registry_provider
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
        IHarvestingEngine,
        IMaintenanceEngine,
        IActionExecutionEngine,
        IEnvironmentalHazardEngine,
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
        harvesting_engine: Optional['IHarvestingEngine'] = None,
        maintenance_engine: Optional['IMaintenanceEngine'] = None,
        action_engine: Optional['IActionExecutionEngine'] = None,
        environmental_engine: Optional['IEnvironmentalHazardEngine'] = None,
    ):
        """
        Initialize the turn engine.

        PROJ-43 Phase 4: All engines can be injected for testing.
        PROJ-50: Added registries parameter for DI to sub-engines.
        PROJ-75 Phase 2: Added harvesting_engine parameter.
        PROJ-75 Phase 5: Added maintenance_engine parameter.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
            registries: Optional GameRegistries for DI. Falls back to
                       get_default_registry_provider() if None.
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
            harvesting_engine: Optional harvesting engine (IHarvestingEngine).
                           If None, creates HarvestingEngine.
            maintenance_engine: Optional maintenance engine (IMaintenanceEngine).
                           If None, creates MaintenanceEngine.
            action_engine: Optional action execution engine (IActionExecutionEngine).
                           If None, creates ActionExecutionEngine.
            environmental_engine: Optional environmental hazard engine (IEnvironmentalHazardEngine).
                           If None, creates EnvironmentalHazardEngine.
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
            provider = get_default_registry_provider()
            self._registries = GameRegistries(
                components=provider.get_components(),
                modifiers=provider.get_modifiers(),
                vehicle_classes=provider.get_vehicle_classes(),
                resources=provider.get_resources(),
            )

        # PROJ-43 Phase 4: Store injected engines or None for lazy init
        self._movement_engine: Optional['IMovementEngine'] = movement_engine
        self._production_engine: Optional['IProductionEngine'] = production_engine
        self._order_processor: Optional['IOrderProcessor'] = order_processor
        self._conflict_engine: Optional['IConflictEngine'] = conflict_engine
        self._resource_engine: Optional['IResourceEngine'] = resource_engine
        self._population_engine: Optional['IPopulationEngine'] = population_engine
        self._resupply_engine: Optional['IResupplyEngine'] = resupply_engine
        self._harvesting_engine: Optional['IHarvestingEngine'] = harvesting_engine
        self._maintenance_engine: Optional['IMaintenanceEngine'] = maintenance_engine
        self._action_engine: Optional['IActionExecutionEngine'] = action_engine
        self._environmental_engine: Optional['IEnvironmentalHazardEngine'] = environmental_engine

        # PROJ-75 Phase 6: Scuttle event storage for UI notification
        self.last_scuttle_events: list = []

        # PROJ-189: Environmental event storage for UI notification
        self.last_environmental_events: list = []

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

    @property
    def harvesting_engine(self) -> 'IHarvestingEngine':
        """Return harvesting engine, lazily creating default if not injected."""
        if self._harvesting_engine is None:
            from game.strategy.engine.harvesting_engine import HarvestingEngine
            self._harvesting_engine = HarvestingEngine(registries=self._registries)
        return self._harvesting_engine

    @property
    def maintenance_engine(self) -> 'IMaintenanceEngine':
        """Return maintenance engine, lazily creating default if not injected."""
        if self._maintenance_engine is None:
            from game.strategy.engine.maintenance_engine import MaintenanceEngine
            self._maintenance_engine = MaintenanceEngine()
        return self._maintenance_engine

    @property
    def action_engine(self) -> 'IActionExecutionEngine':
        """Return action execution engine, lazily creating default if not injected."""
        if self._action_engine is None:
            from game.strategy.engine.action_execution_engine import ActionExecutionEngine
            from game.strategy.services.action_time_resolver import ActionTimeResolver
            self._action_engine = ActionExecutionEngine(
                order_processor=self.order_processor,
                action_time_resolver=ActionTimeResolver()
            )
        return self._action_engine

    @property
    def environmental_engine(self) -> 'IEnvironmentalHazardEngine':
        """Return environmental hazard engine, lazily creating default if not injected."""
        if self._environmental_engine is None:
            from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
            self._environmental_engine = EnvironmentalHazardEngine()
        return self._environmental_engine

    def process_turn(self, empires, galaxy, save_path=None):
        """
        Execute one full turn (100 sub-ticks).

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial calculations
            save_path: Path to savegame folder for loading designs during production
        """
        # Store save_path for tick processing (PROJ-79)
        self._current_save_path = save_path

        # PROJ-161: Initialize scuttle event accumulator (cleared each turn)
        self.last_scuttle_events = []

        # PROJ-189: Initialize environmental event accumulator (cleared each turn)
        self.last_environmental_events = []

        # 1. Subturn Loop (Movement, Actions & Combat)
        # PROJ-187: Action orders (COLONIZE, TRANSFER, superweapons) now processed
        # in Phase 1.5 of each tick via ActionExecutionEngine
        for tick in range(1, 101):
            self._process_tick(tick, empires, galaxy, save_path)

        # 2. Population Growth Phase (PROJ-68)
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

    def _process_tick(self, tick, empires, galaxy, save_path=None):
        """Process 1 sub-tick of movement and combat.

        PROJ-12 Phase 3: Delegates to specialized engines.
        PROJ-74 Phase 5: Added fuel generation and fleet resupply phases.
        PROJ-75 Phase 4: Added per-tick construction resource consumption.
        PROJ-79 Phase 2: Added save_path for mid-turn spawning.
        PROJ-161: Added per-tick harvesting and maintenance.

        Twelve-phase processing:
        Phase 0:   Harvesting (1/100th of per-turn extraction)
        Phase 0a:  Maintenance (1/100th of per-turn cost, immediate scuttle)
        Phase 0b:  Per-turn resource consumption (1/100th of per_turn costs)
        Phase 0c:  Fuel generation at facilities (via ResupplyEngine)
        Phase 0d:  Fleet resupply from facilities (via ResupplyEngine)
        Phase 0e:  Construction resource consumption + mid-turn completion (via ProductionEngine)
        Phase 0f:  Environmental hazards (storm damage, fuel drain) via EnvironmentalHazardEngine
        Phase 1:   Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 1.5: Execute action orders (COLONIZE, TRANSFER, superweapons) via ActionExecutionEngine
        Phase 2:   Calculate paths/next moves for all fleets (based on current positions)
        Phase 3:   Apply all movements simultaneously
        Phase 4:   Combat
        """

        # --- Phase 0: Harvesting (1/100th per tick) ---
        # PROJ-161: Spread harvesting across 100 ticks
        self.harvesting_engine.process_harvesting_tick(tick, empires)

        # --- Phase 0a: Maintenance (1/100th per tick, immediate scuttle) ---
        # PROJ-161: Spread maintenance across 100 ticks, accumulate scuttle events
        tick_scuttles = self.maintenance_engine.process_maintenance_tick(tick, empires)
        self.last_scuttle_events.extend(tick_scuttles)

        # --- Phase 0b: Per-turn Resource Consumption ---
        # PROJ-36: Delegate to ResourceManagementEngine
        self.resource_engine.process_per_turn_consumption(tick, empires)

        # --- Phase 0c: Fuel generation at facilities ---
        # PROJ-74: Generate fuel at planetary facilities with fuel synthesizers
        self.resupply_engine.process_fuel_generation(tick, empires)

        # --- Phase 0d: Fleet resupply from facilities ---
        # PROJ-74: Transfer fuel from facilities to co-located fleets
        self.resupply_engine.process_fleet_resupply(tick, empires, galaxy)

        # --- Phase 0e: Construction resource consumption + mid-turn completion ---
        # PROJ-75/79: Deduct per-tick resource costs, spawn completed items mid-turn
        self.production_engine.process_construction_tick(
            tick, empires, galaxy,
            save_path=save_path,
        )

        # --- Phase 0f: Environmental Hazards (storm damage, fuel drain) ---
        # PROJ-189: Apply storm effects to fleets in hazard hexes
        env_events = self.environmental_engine.process_environmental_tick(tick, empires, galaxy)
        self.last_environmental_events.extend(env_events)

        # --- Phase 1: Instant Orders (JOIN_FLEET) ---
        # PROJ-12: Delegate to FleetOrderProcessor
        self.order_processor.process_instant_orders(empires)

        # --- Phase 1.5: Action Orders (COLONIZE, TRANSFER, superweapons) ---
        # PROJ-187: Tick-based action execution for non-movement, non-BUILD orders
        self.action_engine.process_action_ticks(
            empires, galaxy, tick,
            component_registry=getattr(self._registries, 'components', None),
            all_empires=empires
        )

        # --- Phase 2: Calculate Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        move_queue = self.movement_engine.collect_movements(empires, galaxy, tick)

        # --- Phase 3: Apply Moves ---
        # PROJ-12: Delegate to FleetMovementEngine
        self.movement_engine.apply_movements(move_queue, galaxy)

        # --- Phase 4: Combat ---
        # PROJ-36: Delegate to ConflictResolutionEngine
        self.conflict_engine.resolve_all_conflicts(empires)


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

