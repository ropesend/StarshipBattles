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
       - Phase 1.7:  Component activation timers (via ComponentActivationEngine)
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
from __future__ import annotations

import time
import logging

from game.core.validation import ValidationResult
from game.core.registry import GameRegistries

from typing import Any, Callable, List, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

# Number of sub-ticks per strategy turn
TICKS_PER_TURN = 100

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.engine.turn_engine_config import TurnEngineConfig
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
        IComponentActivationEngine,
        IOrganicsConsumptionEngine,
        IHappinessEngine,
    )
    from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
    from game.strategy.engine.production_engine import ProductionEngine
    from game.strategy.engine.order_processor import OrderProcessor
    from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
    from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.engine.game_session import GameSession


class _NullBattleResolver:
    """Placeholder battle resolver that raises if actually invoked.

    Used when no ai_factory or battle_resolver is provided (e.g., in tests
    that don't trigger combat). Allows TurnEngine construction without
    requiring an AI factory for non-combat scenarios.
    """

    def resolve_battle(self, *args, **kwargs) -> Any:
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
        config: Optional['TurnEngineConfig'] = None,
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
        component_activation_engine: Optional['IComponentActivationEngine'] = None,
        organics_consumption_engine: Optional['IOrganicsConsumptionEngine'] = None,
        happiness_engine: Optional['IHappinessEngine'] = None,
        race_registry: Optional['IRaceRegistry'] = None,
        event_bus=None,
    ):
        """Initialize the turn engine.

        PROJ-259: Accepts optional TurnEngineConfig to bundle engine dependencies.
        Individual engine kwargs still work for backward compatibility — they
        take precedence over config values when both are provided.

        Args:
            battle_resolver: Optional battle resolver. If None, defaults to SimulationBattleResolver.
            registries: GameRegistries for DI to sub-engines (required).
            config: Optional TurnEngineConfig bundling all 13 engine dependencies.
                   Individual kwargs override config values.
            ai_factory: Optional AI controller factory.
            movement_engine..component_activation_engine: Individual engine overrides.
                   If None and config provides a value, config value is used.
                   If both None, lazy-initializes default implementation.
            event_bus: Optional event bus for structured logging.
        """
        from game.strategy.engine.turn_engine_config import TurnEngineConfig
        cfg = config or TurnEngineConfig()

        self._battle_resolver = battle_resolver
        self._ai_factory = ai_factory
        self._registries = registries
        self._event_bus = event_bus
        # PROJ-291 C3: optional race registry threaded into Happiness +
        # Population engines so multi-species colonies resolve each
        # species' RaceConfig correctly. None-fallback preserves the
        # legacy single-race resolver path for test callers that don't
        # supply a registry.
        self._race_registry: Optional['IRaceRegistry'] = race_registry

        # Engine fields: individual kwargs take precedence over config
        self._movement_engine: Optional['IMovementEngine'] = movement_engine or cfg.movement_engine
        self._production_engine: Optional['IProductionEngine'] = production_engine or cfg.production_engine
        self._order_processor: Optional['IOrderProcessor'] = order_processor or cfg.order_processor
        self._conflict_engine: Optional['IConflictEngine'] = conflict_engine or cfg.conflict_engine
        self._resource_engine: Optional['IConsumableEngine'] = resource_engine or cfg.resource_engine
        self._population_engine: Optional['IPopulationEngine'] = population_engine or cfg.population_engine
        self._resupply_engine: Optional['IResupplyEngine'] = resupply_engine or cfg.resupply_engine
        self._harvesting_engine: Optional['IHarvestingEngine'] = harvesting_engine or cfg.harvesting_engine
        self._action_engine: Optional['IActionExecutionEngine'] = action_engine or cfg.action_engine
        self._environmental_engine: Optional['IEnvironmentalHazardEngine'] = environmental_engine or cfg.environmental_engine
        self._planet_energy_engine: Optional['IPlanetEnergyEngine'] = planet_energy_engine or cfg.planet_energy_engine
        self._planet_action_engine: Optional['IPlanetActionEngine'] = planet_action_engine or cfg.planet_action_engine
        self._component_activation_engine: Optional['IComponentActivationEngine'] = component_activation_engine or cfg.component_activation_engine
        # PROJ-284: per-turn food consumption engine (drains configured
        # food resource, writes last_food_ratio for happiness + population)
        self._organics_consumption_engine: Optional['IOrganicsConsumptionEngine'] = (
            organics_consumption_engine or cfg.organics_consumption_engine
        )
        # PROJ-284 Phase 3: happiness = base_happiness * last_food_ratio * habitability
        self._happiness_engine: Optional['IHappinessEngine'] = (
            happiness_engine or cfg.happiness_engine
        )

        # PROJ-189: Environmental event storage for UI notification
        self.last_environmental_events: list = []

        # PROJ-251: Track current tick for error context
        self._current_tick: int = 0

        # Performance timing accumulators (reset each turn in process_turn)
        self._reset_phase_times()

    def _reset_phase_times(self) -> None:
        """Reset performance timing accumulators to zero."""
        self._phase_times: dict[str, float] = {
            'harvesting': 0.0, 'resources': 0.0,
            'fuel_gen': 0.0, 'resupply': 0.0, 'production': 0.0,
            'environmental': 0.0, 'instant_orders': 0.0, 'actions': 0.0,
            'planet_energy': 0.0, 'planet_actions': 0.0, 'activation_timers': 0.0,
            'movement_calc': 0.0, 'movement_apply': 0.0, 'combat': 0.0,
        }

    def _time_phase(self, key: str, fn, *args, **kwargs) -> Any:
        """Execute a phase function and accumulate its duration to _phase_times.

        PROJ-251: On failure, wraps the exception in EnginePhaseError and
        re-raises. The caller (process_turn) catches this and triggers rollback.

        Args:
            key: Phase timing key (must exist in _phase_times dict).
            fn: Callable to execute and time.
            *args: Positional arguments forwarded to fn.
            **kwargs: Keyword arguments forwarded to fn.

        Returns:
            Whatever fn returns (used by phases that return event lists or move queues).

        Raises:
            EnginePhaseError: If the phase function raises any exception.
        """
        from game.core.exceptions import EnginePhaseError
        from game.core.error_codes import ErrorCode

        t0 = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
        except EnginePhaseError:
            # Already wrapped — re-raise as-is
            self._phase_times[key] += time.perf_counter() - t0
            raise
        except Exception as e:
            self._phase_times[key] += time.perf_counter() - t0
            logger.error(
                "Sub-engine phase '%s' failed during tick processing",
                key, exc_info=True,
            )
            raise EnginePhaseError(
                f"Phase '{key}' failed: {e}",
                code=ErrorCode.PHASE_FAILED.value,
                context={
                    "phase_name": key,
                    "tick": self._current_tick,
                    "original_error": str(e),
                    "original_type": type(e).__name__,
                }
            ) from e
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
            self._production_engine = ProductionEngine(registries=self._registries, event_bus=self._event_bus)
        return self._production_engine

    @property
    def order_processor(self) -> 'IOrderProcessor':
        """Return order processor, lazily creating default if not injected."""
        if self._order_processor is None:
            from game.strategy.engine.order_processor import OrderProcessor
            self._order_processor = OrderProcessor(event_bus=self._event_bus)
        return self._order_processor

    @property
    def conflict_engine(self) -> 'IConflictEngine':
        """Return conflict engine, lazily creating default if not injected."""
        if self._conflict_engine is None:
            from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
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
            # PROJ-50: Pass registries for strict DI compliance.
            # PROJ-300 Phase 7: AreaEffectManager removed; sector effects are
            # now read by the engine itself via collect_sector_effects.
            self._conflict_engine = ConflictResolutionEngine(
                battle_resolver,
                registries=self._registries,
                event_bus=self._event_bus,
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
            # PROJ-291 C3: thread the race registry so multi-species
            # colonies grow each species at its own reproduction rate.
            self._population_engine = PopulationEngine(race_registry=self._race_registry)
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
            self._planet_energy_engine = PlanetEnergyEngine(registries=self._registries, event_bus=self._event_bus)
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
                event_bus=self._event_bus,
            )
        return self._planet_action_engine

    @property
    def component_activation_engine(self) -> 'IComponentActivationEngine':
        """Return component activation engine, lazily creating default if not injected."""
        if self._component_activation_engine is None:
            from game.strategy.engine.component_activation_engine import ComponentActivationEngine
            self._component_activation_engine = ComponentActivationEngine()
        return self._component_activation_engine

    @property
    def organics_consumption_engine(self) -> 'IOrganicsConsumptionEngine':
        """Return organics consumption engine, lazily creating default if not injected.

        PROJ-284 Phase 2: Drains the configured food resource per turn
        and writes `last_food_ratio` for downstream happiness / population
        reads.
        """
        if self._organics_consumption_engine is None:
            from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
            self._organics_consumption_engine = OrganicsConsumptionEngine()
        return self._organics_consumption_engine

    @property
    def happiness_engine(self) -> 'IHappinessEngine':
        """Return happiness engine, lazily creating default if not injected.

        PROJ-284 Phase 3: Derives `SpeciesPopulation.happiness` between
        consumption and population growth.
        """
        if self._happiness_engine is None:
            from game.strategy.engine.happiness_engine import HappinessEngine
            # PROJ-291 C3: thread the race registry so multi-species
            # colonies compute happiness from each species' own
            # base_happiness.
            self._happiness_engine = HappinessEngine(race_registry=self._race_registry)
        return self._happiness_engine

    def process_turn(
        self,
        empires: List['Empire'],
        galaxy: 'Galaxy',
        save_path: Optional[str] = None,
        *,
        session: Optional['GameSession'] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """
        Execute one full turn (TICKS_PER_TURN sub-ticks).

        PROJ-251: Captures pre-turn state snapshot. If any phase fails,
        rolls back state and raises EnginePhaseError.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial calculations
            save_path: Path to savegame folder for loading designs during production
            session: Optional GameSession for snapshot rollback on failure.
                If provided, state is restored from snapshot on EnginePhaseError.
            progress_callback: Optional per-tick callback invoked with
                ``(current_tick, TICKS_PER_TURN)`` from inside ``_process_tick``.
                Issue #7: lets the UI repaint the "PROCESSING TURN..." overlay
                with the current tick number while the otherwise-synchronous
                100-tick loop runs. Exceptions raised by the callback are
                logged at WARNING and suppressed so a buggy UI cannot break
                turn execution.

        Raises:
            EnginePhaseError: If any sub-engine phase fails during processing.

        Side Effects:
            Populates self.last_environmental_events (List[EnvironmentalEvent]) from storms.
            This list is cleared at turn start and readable after this method returns.
        """
        from game.core.exceptions import EnginePhaseError
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot

        # Store save_path for tick processing (PROJ-79)
        self._current_save_path = save_path

        # Issue #7: stash the per-tick progress callback for _process_tick to
        # invoke. Cleared in the outer finally so the callback never leaks
        # into a subsequent process_turn call on the same engine instance.
        self._progress_callback = progress_callback

        # PROJ-189: Initialize environmental event accumulator (cleared each turn)
        self.last_environmental_events = []

        # Performance timing accumulators
        self._reset_phase_times()

        # PROJ-251: Capture pre-turn state for rollback.
        # PROJ-343 T1.2-snapshot: a capture failure means rollback is
        # disabled for the rest of the turn. Continuing silently with
        # snapshot=None can mask the loss of state-integrity safety —
        # any later EnginePhaseError would skip rollback without warning.
        # Re-raise so the caller knows the turn is unsafe and can decide.
        snapshot = None
        if session is not None:
            try:
                snapshot = TurnStateSnapshot.capture(
                    turn_number=getattr(session, 'turn_number', 0),
                    empires=empires,
                    galaxy=galaxy,
                )
            except Exception:
                logger.error(
                    "Failed to capture pre-turn snapshot; aborting turn to "
                    "preserve state-integrity guarantees."
                )
                raise

        turn_start = time.perf_counter()

        # [BUG-109] Log resource state before turn processing
        self._log_empire_state(empires, "=== TURN START ===")

        try:
            # PROJ-285: Bump the per-turn habitability-cache key so
            # harvesting/production engines recompute multipliers at
            # each turn boundary. Safe even when engines are mocks —
            # `getattr` guards missing setters.
            turn_number = getattr(session, 'turn_number', 0) if session is not None else 0
            for _engine in (self._harvesting_engine, self._production_engine):
                if _engine is not None:
                    setter = getattr(_engine, 'set_current_turn', None)
                    if setter is not None:
                        setter(turn_number)

            # 1. Subturn Loop (Movement, Actions & Combat)
            for tick in range(1, TICKS_PER_TURN + 1):
                self._process_tick(tick, empires, galaxy, save_path)

            # [BUG-109] Log resource state after all ticks
            self._log_empire_state(empires, f"=== TURN END (after {TICKS_PER_TURN} ticks) ===")

            # PROJ-284 Phase 2: Food consumption runs BEFORE happiness
            # so `last_food_ratio` is fresh for the happiness formula.
            self.organics_consumption_engine.process_consumption(empires)

            # PROJ-284 Phase 3: Happiness = base * ratio * habitability.
            # Derived fresh each turn between consumption and population
            # growth so `pop.happiness` carries no stale value into
            # `PopulationEngine._grow_species`.
            self.happiness_engine.process_happiness(empires, galaxy)

            # 2. Population Growth Phase (PROJ-68)
            t0 = time.perf_counter()
            self.population_engine.process_population_growth(empires)
            pop_time = time.perf_counter() - t0

            # 3. Quality Improvement + Atmosphere Modification (once per turn)
            from game.strategy.engine.quality_engine import QualityEngine
            from game.strategy.engine.atmosphere_engine import AtmosphereEngine
            QualityEngine(registries=self._registries).process_quality_improvement(empires)
            AtmosphereEngine(registries=self._registries).process_atmosphere(empires)

            # 4. Water Modification (once per turn)
            from game.strategy.engine.water_engine import WaterEngine
            WaterEngine(registries=self._registries).process_water_modification(empires)

        except EnginePhaseError as e:
            # PROJ-251: Rollback state and re-raise
            logger.error(
                f"Turn failed at tick {e.context.get('tick', '?')}, "
                f"phase '{e.context.get('phase_name', '?')}'. "
                f"{'Rolling back.' if snapshot and session else 'No snapshot available.'}"
            )

            if snapshot and save_path:
                snapshot.dump_crash_snapshot(save_path, e.context)

            if snapshot and session:
                snapshot.restore(session)

            raise
        finally:
            # Issue #7: clear the per-tick callback so it doesn't leak
            # into a subsequent process_turn call on this engine instance.
            self._progress_callback = None

        total_time = time.perf_counter() - turn_start
        logger.warning(
            "TURN PERF: total=%.3fs | harvesting=%.3fs "
            "resources=%.3fs fuel_gen=%.3fs planet_energy=%.3fs resupply=%.3fs production=%.3fs "
            "environmental=%.3fs orders=%.3fs actions=%.3fs planet_actions=%.3fs "
            "activation_timers=%.3fs "
            "move_calc=%.3fs move_apply=%.3fs combat=%.3fs population=%.3fs",
            total_time, self._phase_times['harvesting'],
            self._phase_times['resources'], self._phase_times['fuel_gen'],
            self._phase_times['planet_energy'], self._phase_times['resupply'],
            self._phase_times['production'],
            self._phase_times['environmental'], self._phase_times['instant_orders'],
            self._phase_times['actions'], self._phase_times['planet_actions'],
            self._phase_times['activation_timers'],
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

    def _process_tick(self, tick: int, empires: List['Empire'], galaxy: 'Galaxy', save_path: Optional[str] = None) -> None:
        """Process 1 sub-tick of movement and combat.

        PROJ-12 Phase 3: Delegates to specialized engines.
        PROJ-74 Phase 5: Added fuel generation and fleet resupply phases.
        PROJ-75 Phase 4: Added per-tick construction resource consumption.
        PROJ-79 Phase 2: Added save_path for mid-turn spawning.
        PROJ-161: Added per-tick harvesting.
        PROJ-251: Sets _current_tick for error context in EnginePhaseError.

        Fourteen-phase processing:
        Phase 0:    Harvesting (1/100th of per-turn extraction)
        Phase 0b:   Per-turn resource consumption (1/100th of per_turn costs)
        Phase 0c:   Fuel generation at facilities (via ResupplyEngine)
        Phase 0c1:  Planet energy generation/consumption (via PlanetEnergyEngine)
        Phase 0d:   Fleet resupply from facilities (via ResupplyEngine)
        Phase 0e:   Construction resource consumption + mid-turn completion (via ProductionEngine)
        Phase 0f:   Environmental hazards (storm damage, fuel drain) via EnvironmentalHazardEngine
        Phase 1:    Execute JOIN_FLEET for any co-located fleets (instant, no movement cost)
        Phase 1.5:  Execute action orders (COLONIZE, TRANSFER, superweapons) via ActionExecutionEngine
        Phase 1.6:  Planet action orders (shield activation, etc.) via PlanetActionEngine
        Phase 1.7:  Component activation timers via ComponentActivationEngine
        Phase 2:    Calculate paths/next moves for all fleets (based on current positions)
        Phase 3:    Apply all movements simultaneously
        Phase 4:    Combat
        """

        # PROJ-251: Track current tick for error context
        self._current_tick = tick

        # Issue #7: notify the UI that a tick has started so the
        # "PROCESSING TURN..." overlay can repaint with the current tick
        # number. The callback is optional and may be None.
        cb = getattr(self, "_progress_callback", None)
        if cb is not None:
            try:
                cb(tick, TICKS_PER_TURN)
            except Exception:  # Intentional broad catch: UI callback must never break turn processing (PROJ-308)
                logger.warning("progress_callback raised; suppressing", exc_info=True)

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

        # --- Phase 1.7: Component Activation Timers ---
        self._time_phase('activation_timers',
                         self.component_activation_engine.process_activation_tick,
                         tick, empires)

        # --- Phase 1.8: Planet Modifier Effects (gravity/radiation apply/revert) ---
        from game.strategy.engine.planet_modifier_effect_engine import PlanetModifierEffectEngine
        PlanetModifierEffectEngine(registries=self._registries).process_modifier_effects_tick(tick, empires)

        # --- Phase 2: Calculate Moves ---
        move_queue = self._time_phase('movement_calc', self.movement_engine.collect_movements, empires, galaxy, tick)

        # PROJ-320: snapshot fleet locations BEFORE Phase 3 so that after
        # Phase 3 (`apply_movements`) we can compute the set of fleet ids
        # that actually moved this tick. The conflict trigger predicate
        # needs this to skip combat for fleets that successfully left a
        # contested hex on their movement-opportunity tick.
        pre_movement_locations = {
            f.id: f.location for emp in empires for f in emp.fleets
        }

        # --- Phase 3: Apply Moves ---
        self._time_phase('movement_apply', self.movement_engine.apply_movements, move_queue, galaxy)

        # PROJ-320: derive `moved_fleet_ids` from pre/post-Phase-3 location
        # diff. Cost is O(fleets) — same order as the legacy hex-map scan.
        moved_fleet_ids = {
            f.id
            for emp in empires for f in emp.fleets
            if pre_movement_locations.get(f.id) != f.location
        }

        # --- Phase 4: Combat ---
        self._time_phase(
            'combat', self.conflict_engine.resolve_all_conflicts,
            empires, galaxy=galaxy,
            tick=tick, moved_fleet_ids=moved_fleet_ids,
        )


def create_default_turn_engine(registries: GameRegistries, ai_factory=None, config=None) -> TurnEngine:
    """
    Factory function to create a TurnEngine with all default engines.

    PROJ-43 Phase 4: Simplifies instantiation for production code.
    PROJ-211: Requires registries parameter for strict DI.
    PROJ-259: Accepts optional TurnEngineConfig.

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
    return TurnEngine(registries=registries, config=config, ai_factory=ai_factory)

