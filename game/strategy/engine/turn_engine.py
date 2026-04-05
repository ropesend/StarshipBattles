"""
Turn Engine - Strategy Layer Turn Orchestration

PROJ-36: Refactored to be a lightweight orchestrator that delegates
to specialized engines.

PROJ-43 Phase 4: Full constructor dependency injection for all engines.

PROJ-161: Moved harvesting into per-tick processing.

Turn Phases:
    1. SUBTURN LOOP (100 ticks):
       - Phase 0:    Harvesting (via HarvestingEngine) - 1/100th per tick
       - Phase 0b:   Per-turn resources (via ConsumableManagementEngine)
       - Phase 0c:   Fuel generation at facilities (via ResupplyEngine)
       - Phase 0c1:  Planet energy generation/consumption (via PlanetEnergyEngine)
       - Phase 0d:   Fleet resupply from facilities (via ResupplyEngine)
       - Phase 0e:   Construction resource consumption (via ProductionEngine)
       - Phase 0f:   Environmental hazards - storm damage/fuel drain (via EnvironmentalHazardEngine)
       - Phase 1:    Instant orders (via OrderProcessor)
       - Phase 1.5:  Action orders (via ActionExecutionEngine) - COLONIZE, TRANSFER, superweapons
       - Phase 1.6:  Planet action orders (via PlanetActionEngine) - shield activation, etc.
       - Phase 2:    Calculate moves (via FleetMovementEngine)
       - Phase 3:    Apply moves (via FleetMovementEngine)
       - Phase 4:    Combat (via ConflictResolutionEngine)
    2. POPULATION GROWTH (via PopulationEngine)
    3. QUALITY IMPROVEMENT (via QualityEngine) - once per turn
    4. ATMOSPHERE MODIFICATION (via AtmosphereEngine) - once per turn

Delegated Engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - OrderProcessor: Order lifecycle management (instant orders only)
    - ActionExecutionEngine: Tick-based action order execution
    - ConflictResolutionEngine: Combat detection and resolution
    - ConsumableManagementEngine: Per-turn resource consumption
    - ResupplyEngine: Fuel generation and fleet resupply
    - HarvestingEngine: Planetary resource extraction to empire pool

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
from typing import Any, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

# Number of sub-ticks per strategy turn
TICKS_PER_TURN = 100

if TYPE_CHECKING:
    from game.strategy.interfaces.battle_resolver import IBattleResolver
    from game.strategy.interfaces.engines import (
        IMovementEngine,
        IProductionEngine,
        IOrderProcessor,
        IConflictEngine,
        IConsumableEngine,
        IPopulationEngine,
        IResupplyEngine,
        IHarvestingEngine,
        IActionExecutionEngine,
        IEnvironmentalHazardEngine,
        IPlanetEnergyEngine,
        IPlanetActionEngine,
    )
    from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
    from game.strategy.engine.production_engine import ProductionEngine
    from game.strategy.engine.order_processor import OrderProcessor
    from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
    from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine


class _NullBattleResolver:
    """Placeholder battle resolver that raises if actually invoked.

    Used when no ai_factory or battle_resolver is provided (e.g., in tests
    that don't trigger combat). Allows TurnEngine construction without
    requiring an AI factory for non-combat scenarios.
    """

    def resolve_battle(self, *args, **kwargs):
        raise RuntimeError(
            "No battle resolver configured. Provide ai_factory or battle_resolver "
            "to TurnEngine when combat resolution is needed."
        )


class TurnEngine:
    """
    Engine for processing strategy turns.

    PROJ-11 Phase 4: Supports dependency injection of IBattleResolver
    for clean separation between strategy and simulation layers.

    PROJ-12 Phase 3: Delegates to specialized engines:
    - FleetMovementEngine: Movement calculation and application
    - ProductionEngine: Construction queue processing
    - OrderProcessor: Order lifecycle management

    PROJ-36: Additional delegation to:
    - ConflictResolutionEngine: Combat detection and resolution
    - ConsumableManagementEngine: Per-turn resource consumption

    PROJ-43 Phase 4: Full constructor dependency injection for all engines.
    All engines can be injected via constructor for testing and extensibility.
    """

    def __init__(
        self,
        battle_resolver: Optional['IBattleResolver'] = None,
        *,
        registries: GameRegistries,
        ai_factory: Optional[Any] = None,
        movement_engine: Optional['IMovementEngine'] = None,
        production_engine: Optional['IProductionEngine'] = None,
        order_processor: Optional['IOrderProcessor'] = None,
        conflict_engine: Optional['IConflictEngine'] = None,
        resource_engine: Optional['IConsumableEngine'] = None,
        population_engine: Optional['IPopulationEngine'] = None,
        resupply_engine: Optional['IResupplyEngine'] = None,
        harvesting_engine: Optional['IHarvestingEngine'] = None,
        action_engine: Optional['IActionExecutionEngine'] = None,
        environmental_engine: Optional['IEnvironmentalHazardEngine'] = None,
        planet_energy_engine: Optional['IPlanetEnergyEngine'] = None,
        planet_action_engine: Optional['IPlanetActionEngine'] = None,
    ):
        """
        Initialize the turn engine.

        PROJ-43 Phase 4: All engines can be injected for testing.
        PROJ-50: Added registries parameter for DI to sub-engines.
        PROJ-75 Phase 2: Added harvesting_engine parameter.

        Args:
            battle_resolver: Optional battle resolver implementation.
                           If None, defaults to SimulationBattleResolver.
            registries: GameRegistries for DI to sub-engines (required).
            movement_engine: Optional movement engine (IMovementEngine).
                           If None, creates FleetMovementEngine.
            production_engine: Optional production engine (IProductionEngine).
                           If None, creates ProductionEngine.
            order_processor: Optional order processor (IOrderProcessor).
                           If None, creates OrderProcessor.
            conflict_engine: Optional conflict engine (IConflictEngine).
                           If None, creates ConflictResolutionEngine.
            resource_engine: Optional resource engine (IConsumableEngine).
                           If None, creates ConsumableManagementEngine.
            population_engine: Optional population engine (IPopulationEngine).
                           If None, creates PopulationEngine.
            resupply_engine: Optional resupply engine (IResupplyEngine).
                           If None, creates ResupplyEngine.
            harvesting_engine: Optional harvesting engine (IHarvestingEngine).
                           If None, creates HarvestingEngine.
            action_engine: Optional action execution engine (IActionExecutionEngine).
                           If None, creates ActionExecutionEngine.
            environmental_engine: Optional environmental hazard engine (IEnvironmentalHazardEngine).
                           If None, creates EnvironmentalHazardEngine.
        """
        # PROJ-11: Inject battle resolver for clean layer separation
        # PROJ-239: Store battle_resolver and ai_factory; resolver is created lazily
        # when conflict_engine is first accessed (not at construction time).
        self._battle_resolver = battle_resolver
        self._ai_factory = ai_factory

        # PROJ-211: Store registries for passing to sub-engines (required)
        self._registries = registries

        # PROJ-43 Phase 4: Store injected engines or None for lazy init
        self._movement_engine: Optional['IMovementEngine'] = movement_engine
        self._production_engine: Optional['IProductionEngine'] = production_engine
        self._order_processor: Optional['IOrderProcessor'] = order_processor
        self._conflict_engine: Optional['IConflictEngine'] = conflict_engine
        self._resource_engine: Optional['IConsumableEngine'] = resource_engine
        self._population_engine: Optional['IPopulationEngine'] = population_engine
        self._resupply_engine: Optional['IResupplyEngine'] = resupply_engine
        self._harvesting_engine: Optional['IHarvestingEngine'] = harvesting_engine
        self._action_engine: Optional['IActionExecutionEngine'] = action_engine
        self._environmental_engine: Optional['IEnvironmentalHazardEngine'] = environmental_engine
        # PROJ-237: Planet energy and action engines
        self._planet_energy_engine: Optional['IPlanetEnergyEngine'] = planet_energy_engine
        self._planet_action_engine: Optional['IPlanetActionEngine'] = planet_action_engine

        # PROJ-189: Environmental event storage for UI notification
        self.last_environmental_events: list = []

        # Performance timing accumulators (reset each turn in process_turn)
        self._reset_phase_times()

    def _reset_phase_times(self) -> None:
        """Reset performance timing accumulators to zero."""
        self._phase_times: dict[str, float] = {
            'harvesting': 0.0, 'resources': 0.0,
            'fuel_gen': 0.0, 'resupply': 0.0, 'production': 0.0,
            'environmental': 0.0, 'instant_orders': 0.0, 'actions': 0.0,
            'planet_energy': 0.0, 'planet_actions': 0.0,
            'movement_calc': 0.0, 'movement_apply': 0.0, 'combat': 0.0,
        }

    def _time_phase(self, key: str, fn, *args, **kwargs):
        """Execute a phase function and accumulate its duration to _phase_times.

        Catches and logs exceptions from sub-engines so that a failure in one
        phase does not crash the entire turn. The failed phase is skipped and
        processing continues with the next phase.

        Args:
            key: Phase timing key (must exist in _phase_times dict).
            fn: Callable to execute and time.
            *args: Positional arguments forwarded to fn.
            **kwargs: Keyword arguments forwarded to fn.

        Returns:
            Whatever fn returns (used by phases that return event lists or move queues).
            Returns None if the phase raised an exception.
        """
        t0 = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._phase_times[key] += time.perf_counter() - t0
            logger.error(
                "Sub-engine phase '%s' failed during tick processing",
                key, exc_info=True,
            )
            return None
        self._phase_times[key] += time.perf_counter() - t0
        return result

    def _log_empire_state(self, empires, label: str) -> None:
        """Log empire resource state for debugging (BUG-109)."""
        for empire in empires:
            try:
                logger.debug(
                    f"[BUG-109] {label}: empire {empire.id} "
                    f"resource_pool={dict(empire.resource_pool)}"
                )
            except (AttributeError, TypeError):
                pass

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
            from game.strategy.engine.order_processor import OrderProcessor
            self._order_processor = OrderProcessor()
        return self._order_processor

    @property
    def conflict_engine(self) -> 'IConflictEngine':
        """Return conflict engine, lazily creating default if not injected."""
        if self._conflict_engine is None:
            from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
            from game.strategy.services.area_effect_manager import AreaEffectManager
            # PROJ-239: Lazily create battle resolver if not injected
            battle_resolver = self._battle_resolver
            if battle_resolver is None and self._ai_factory is not None:
                from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
                battle_resolver = SimulationBattleResolver(ai_factory=self._ai_factory)
                self._battle_resolver = battle_resolver
            if battle_resolver is None:
                logger.warning(
                    "TurnEngine: no battle_resolver or ai_factory provided. "
                    "Combat resolution will fail if battles occur."
                )
                battle_resolver = _NullBattleResolver()
            # PROJ-50: Pass registries for strict DI compliance
            # PROJ-189: Pass AreaEffectManager for storm shield interference
            self._conflict_engine = ConflictResolutionEngine(
                battle_resolver,
                registries=self._registries,
                area_effect_manager=AreaEffectManager()
            )
        return self._conflict_engine

    @property
    def resource_engine(self) -> 'IConsumableEngine':
        """Return resource engine, lazily creating default if not injected."""
        if self._resource_engine is None:
            from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
            # PROJ-50: Pass registries for strict DI
            self._resource_engine = ConsumableManagementEngine(registries=self._registries)
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

    @property
    def planet_energy_engine(self) -> 'IPlanetEnergyEngine':
        """Return planet energy engine, lazily creating default if not injected."""
        if self._planet_energy_engine is None:
            from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
            self._planet_energy_engine = PlanetEnergyEngine(registries=self._registries)
        return self._planet_energy_engine

    @property
    def planet_action_engine(self) -> 'IPlanetActionEngine':
        """Return planet action engine, lazily creating default if not injected."""
        if self._planet_action_engine is None:
            from game.strategy.engine.planet_action_engine import PlanetActionEngine
            from game.strategy.services.action_time_resolver import ActionTimeResolver
            self._planet_action_engine = PlanetActionEngine(
                registries=self._registries,
                action_time_resolver=ActionTimeResolver(),
            )
        return self._planet_action_engine

    def process_turn(self, empires, galaxy, save_path=None):
        """
        Execute one full turn (TICKS_PER_TURN sub-ticks).

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial calculations
            save_path: Path to savegame folder for loading designs during production

        Side Effects:
            Populates self.last_environmental_events (List[EnvironmentalEvent]) from storms.
            This list is cleared at turn start and readable after this method returns.
        """
        # Store save_path for tick processing (PROJ-79)
        self._current_save_path = save_path

        # PROJ-189: Initialize environmental event accumulator (cleared each turn)
        self.last_environmental_events = []

        # Performance timing accumulators
        self._reset_phase_times()

        turn_start = time.perf_counter()

        # [BUG-109] Log resource state before turn processing
        self._log_empire_state(empires, "=== TURN START ===")

        # 1. Subturn Loop (Movement, Actions & Combat)
        # PROJ-187: Action orders (COLONIZE, TRANSFER, superweapons) now processed
        # in Phase 1.5 of each tick via ActionExecutionEngine
        for tick in range(1, TICKS_PER_TURN + 1):
            self._process_tick(tick, empires, galaxy, save_path)

        # [BUG-109] Log resource state after all ticks
        self._log_empire_state(empires, f"=== TURN END (after {TICKS_PER_TURN} ticks) ===")

        # 2. Population Growth Phase (PROJ-68)
        t0 = time.perf_counter()
        self.population_engine.process_population_growth(empires)
        pop_time = time.perf_counter() - t0

        # 3. Quality Improvement + Atmosphere Modification (once per turn)
        from game.strategy.engine.quality_engine import QualityEngine
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine
        QualityEngine(registries=self._registries).process_quality_improvement(empires)
        AtmosphereEngine(registries=self._registries).process_atmosphere(empires)

        total_time = time.perf_counter() - turn_start
        logger.warning(
            "TURN PERF: total=%.3fs | harvesting=%.3fs "
            "resources=%.3fs fuel_gen=%.3fs planet_energy=%.3fs resupply=%.3fs production=%.3fs "
            "environmental=%.3fs orders=%.3fs actions=%.3fs planet_actions=%.3fs "
            "move_calc=%.3fs move_apply=%.3fs combat=%.3fs population=%.3fs",
            total_time, self._phase_times['harvesting'],
            self._phase_times['resources'], self._phase_times['fuel_gen'],
            self._phase_times['planet_energy'], self._phase_times['resupply'],
            self._phase_times['production'],
            self._phase_times['environmental'], self._phase_times['instant_orders'],
            self._phase_times['actions'], self._phase_times['planet_actions'],
            self._phase_times['movement_calc'],
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
        PROJ-161: Added per-tick harvesting.

        Eleven-phase processing:
        Phase 0:   Harvesting (1/100th of per-turn extraction)
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
        if tick == 1:
            self._log_empire_state(empires, "TURN START tick=1")
        self._time_phase('harvesting', self.harvesting_engine.process_harvesting_tick, tick, empires, galaxy)

        # --- Phase 0b: Per-turn Resource Consumption ---
        self._time_phase('resources', self.resource_engine.process_per_turn_consumption, tick, empires)

        # --- Phase 0c: Fuel generation at facilities ---
        self._time_phase('fuel_gen', self.resupply_engine.process_fuel_generation, tick, empires)

        # --- Phase 0c1: Planet Energy (generation, consumption, auto-deactivation) ---
        self._time_phase('planet_energy', self.planet_energy_engine.process_energy_tick, tick, empires)

        # --- Phase 0d: Fleet resupply from facilities ---
        self._time_phase('resupply', self.resupply_engine.process_fleet_resupply, tick, empires, galaxy)

        # --- Phase 0e: Construction resource consumption + mid-turn completion ---
        self._time_phase('production', self.production_engine.process_construction_tick,
                         tick, empires, galaxy, save_path=save_path)
        if tick == 1:
            self._log_empire_state(empires, "Tick 1 AFTER CONSTRUCTION")

        # --- Phase 0f: Environmental Hazards (storm damage, fuel drain) ---
        env_events = self._time_phase('environmental', self.environmental_engine.process_environmental_tick, tick, empires, galaxy)
        if env_events:
            self.last_environmental_events.extend(env_events)

        # --- Phase 1: Instant Orders (JOIN_FLEET) ---
        self._time_phase('instant_orders', self.order_processor.process_instant_orders, empires)

        # --- Phase 1.5: Action Orders (COLONIZE, TRANSFER, superweapons) ---
        self._time_phase('actions', self.action_engine.process_action_ticks,
                         empires, galaxy, tick,
                         component_registry=self._registries.components,
                         all_empires=empires)

        # --- Phase 1.6: Planet Action Orders (shield activation, etc.) ---
        self._time_phase('planet_actions', self.planet_action_engine.process_planet_actions_tick,
                         tick, empires,
                         component_registry=self._registries.components)

        # --- Phase 2: Calculate Moves ---
        move_queue = self._time_phase('movement_calc', self.movement_engine.collect_movements, empires, galaxy, tick)

        # --- Phase 3: Apply Moves ---
        self._time_phase('movement_apply', self.movement_engine.apply_movements, move_queue, galaxy)

        # --- Phase 4: Combat ---
        self._time_phase('combat', self.conflict_engine.resolve_all_conflicts, empires, galaxy=galaxy)


def create_default_turn_engine(registries: GameRegistries, ai_factory=None) -> TurnEngine:
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
    return TurnEngine(registries=registries, ai_factory=ai_factory)

