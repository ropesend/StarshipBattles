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
import time
import logging

from game.core.validation import ValidationResult
from game.core.registry import GameRegistries
from typing import Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

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
        registries: GameRegistries,
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
            registries: GameRegistries for DI to sub-engines (required).
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

        # PROJ-211: Store registries for passing to sub-engines (required)
        self._registries = registries

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

        # Performance timing accumulators (reset each turn in process_turn)
        self._reset_phase_times()

    def _reset_phase_times(self) -> None:
        """Reset performance timing accumulators to zero."""
        self._phase_times: dict[str, float] = {
            'harvesting': 0.0, 'maintenance': 0.0, 'resources': 0.0,
            'fuel_gen': 0.0, 'resupply': 0.0, 'production': 0.0,
            'environmental': 0.0, 'instant_orders': 0.0, 'actions': 0.0,
            'movement_calc': 0.0, 'movement_apply': 0.0, 'combat': 0.0,
        }

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
            # PROJ-211: Pass registries for ship creation DI compliance
            self._production_engine = ProductionEngine(registries=self._registries)
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
            from game.strategy.services.area_effect_manager import AreaEffectManager
            # PROJ-50: Pass registries for strict DI compliance
            # PROJ-189: Pass AreaEffectManager for storm shield interference
            self._conflict_engine = ConflictResolutionEngine(
                self._battle_resolver,
                registries=self._registries,
                area_effect_manager=AreaEffectManager()
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
            # PROJ-218: Pass registries for cost calculation
            self._maintenance_engine = MaintenanceEngine(registries=self._registries)
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

        # Performance timing accumulators
        self._reset_phase_times()

        turn_start = time.perf_counter()

        # 1. Subturn Loop (Movement, Actions & Combat)
        # PROJ-187: Action orders (COLONIZE, TRANSFER, superweapons) now processed
        # in Phase 1.5 of each tick via ActionExecutionEngine
        for tick in range(1, 101):
            self._process_tick(tick, empires, galaxy, save_path)

        # 2. Population Growth Phase (PROJ-68)
        t0 = time.perf_counter()
        self.population_engine.process_population_growth(empires)
        pop_time = time.perf_counter() - t0

        total_time = time.perf_counter() - turn_start
        logger.warning(
            "TURN PERF: total=%.3fs | harvesting=%.3fs maintenance=%.3fs "
            "resources=%.3fs fuel_gen=%.3fs resupply=%.3fs production=%.3fs "
            "environmental=%.3fs orders=%.3fs actions=%.3fs "
            "move_calc=%.3fs move_apply=%.3fs combat=%.3fs population=%.3fs",
            total_time, self._phase_times['harvesting'], self._phase_times['maintenance'],
            self._phase_times['resources'], self._phase_times['fuel_gen'],
            self._phase_times['resupply'], self._phase_times['production'],
            self._phase_times['environmental'], self._phase_times['instant_orders'],
            self._phase_times['actions'], self._phase_times['movement_calc'],
            self._phase_times['movement_apply'], self._phase_times['combat'],
            pop_time,
        )
        
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
        # GameRegistries always has components attribute
        return ColonizeValidator.validate(galaxy, fleet, target_planet, self._registries.components)

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
        t0 = time.perf_counter()
        self.harvesting_engine.process_harvesting_tick(tick, empires)
        self._phase_times['harvesting'] += time.perf_counter() - t0

        # --- Phase 0a: Maintenance (1/100th per tick, immediate scuttle) ---
        t0 = time.perf_counter()
        tick_scuttles = self.maintenance_engine.process_maintenance_tick(tick, empires)
        self._phase_times['maintenance'] += time.perf_counter() - t0
        self.last_scuttle_events.extend(tick_scuttles)

        # --- Phase 0b: Per-turn Resource Consumption ---
        t0 = time.perf_counter()
        self.resource_engine.process_per_turn_consumption(tick, empires)
        self._phase_times['resources'] += time.perf_counter() - t0

        # --- Phase 0c: Fuel generation at facilities ---
        t0 = time.perf_counter()
        self.resupply_engine.process_fuel_generation(tick, empires)
        self._phase_times['fuel_gen'] += time.perf_counter() - t0

        # --- Phase 0d: Fleet resupply from facilities ---
        t0 = time.perf_counter()
        self.resupply_engine.process_fleet_resupply(tick, empires, galaxy)
        self._phase_times['resupply'] += time.perf_counter() - t0

        # --- Phase 0e: Construction resource consumption + mid-turn completion ---
        t0 = time.perf_counter()
        self.production_engine.process_construction_tick(
            tick, empires, galaxy,
            save_path=save_path,
        )
        self._phase_times['production'] += time.perf_counter() - t0

        # --- Phase 0f: Environmental Hazards (storm damage, fuel drain) ---
        t0 = time.perf_counter()
        env_events = self.environmental_engine.process_environmental_tick(tick, empires, galaxy)
        self._phase_times['environmental'] += time.perf_counter() - t0
        self.last_environmental_events.extend(env_events)

        # --- Phase 1: Instant Orders (JOIN_FLEET) ---
        t0 = time.perf_counter()
        self.order_processor.process_instant_orders(empires)
        self._phase_times['instant_orders'] += time.perf_counter() - t0

        # --- Phase 1.5: Action Orders (COLONIZE, TRANSFER, superweapons) ---
        t0 = time.perf_counter()
        self.action_engine.process_action_ticks(
            empires, galaxy, tick,
            component_registry=self._registries.components,
            all_empires=empires
        )
        self._phase_times['actions'] += time.perf_counter() - t0

        # --- Phase 2: Calculate Moves ---
        t0 = time.perf_counter()
        move_queue = self.movement_engine.collect_movements(empires, galaxy, tick)
        self._phase_times['movement_calc'] += time.perf_counter() - t0

        # --- Phase 3: Apply Moves ---
        t0 = time.perf_counter()
        self.movement_engine.apply_movements(move_queue, galaxy)
        self._phase_times['movement_apply'] += time.perf_counter() - t0

        # --- Phase 4: Combat ---
        t0 = time.perf_counter()
        self.conflict_engine.resolve_all_conflicts(empires, galaxy=galaxy)
        self._phase_times['combat'] += time.perf_counter() - t0


def create_default_turn_engine(registries: GameRegistries) -> TurnEngine:
    """
    Factory function to create a TurnEngine with all default engines.

    PROJ-43 Phase 4: Simplifies instantiation for production code.
    PROJ-211: Requires registries parameter for strict DI.

    This factory creates a TurnEngine with all default sub-engines.
    For testing, use the TurnEngine constructor directly to inject
    mock engines.

    Args:
        registries: GameRegistries for DI to sub-engines (required).

    Returns:
        TurnEngine with default implementations of all sub-engines.

    Example:
        # Production code
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )
        engine = create_default_turn_engine(registries)
        engine.process_turn(empires, galaxy, save_path)

        # Test code - use constructor for mocking
        engine = TurnEngine(
            registries=test_registries,
            movement_engine=mock_movement,
            production_engine=mock_production
        )
    """
    return TurnEngine(registries=registries)

