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

from game.core.exceptions import EnginePhaseError
from game.core.error_codes import ErrorCode
from game.core.validation import ValidationResult
from game.core.registry import GameRegistries
from game.strategy.engine.turn_engine_settings import load_turn_engine_settings
from game.strategy.engine.turn_phase_registry import (
    DEFAULT_END_OF_TURN_PHASE_LIST,
    DEFAULT_TICK_PHASE_LIST,
    TickContext,
    TickPhase,
)

from typing import Any, Callable, List, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

# Number of sub-ticks per strategy turn
TICKS_PER_TURN = 100

# PROJ-412 Phase 4: per-tick progress callback was measured by Probe B
# (findings/profile_baseline_cpu.md) to add ~5 ms / invocation × 100 ticks ≈
# 0.5–2 s / turn of wall-clock on the user's real game — the UI callback
# does `pygame.event.pump() + screen.draw() + display.flip()` per tick.
# Coarsening to "tick 1 + every Nth tick + tick 100" keeps both endpoints
# visible to the UI while cutting the redraw count.
#
# The interval is user-tunable via
# `output/settings/turn_engine_settings.json`; default ``5`` yields 21
# callback invocations per turn (ticks 1, 5, 10, …, 95, 100). The module-
# level constant is set at import time. Tests may monkeypatch it for
# isolated cadence assertions; the `test_turn_engine_progress_callback.py`
# suite reads through this constant rather than re-loading settings so
# overrides remain coherent.
PROGRESS_CALLBACK_INTERVAL = load_turn_engine_settings().progress_callback_interval

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
        IQualityEngine,
        IAtmosphereEngine,
        IWaterEngine,
    )
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.engine.game_session import GameSession


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
        *,
        registries: GameRegistries,
        config: 'TurnEngineConfig',
        ai_factory: Optional[Any] = None,
        race_registry: Optional['IRaceRegistry'] = None,
        event_bus=None,
        battle_resolver: Optional['IBattleResolver'] = None,
        tick_phases: Optional[tuple['TickPhase', ...]] = None,
        end_of_turn_phases: Optional[tuple['TickPhase', ...]] = None,
    ):
        """Initialize the turn engine.

        PROJ-369 Phase 3: ``config`` is REQUIRED. The 18 sub-engines are
        always read from ``config``; there is no per-engine override
        kwarg. Tests that need to swap one engine should construct the
        config via ``TurnEngineConfig.create_default(registries, ...)``
        followed by ``dataclasses.replace(cfg, foo_engine=mock_foo)``.

        The ``_NullBattleResolver`` placeholder is gone; combat with
        ``battle_resolver=None`` raises clearly from
        ``ConflictResolutionEngine`` at first attempt.

        Args:
            registries: GameRegistries for DI to sub-engines (required).
            config: TurnEngineConfig bundling all 18 engine dependencies
                (required). Build via ``TurnEngineConfig.create_default(...)``.
            ai_factory: Optional AI controller factory. Documentation
                hook only — config is expected to have already-bound
                values that used this.
            race_registry: Optional race registry. Documentation hook
                only — config is expected to have already-bound values
                that used this.
            event_bus: Optional event bus. Documentation hook only —
                config is expected to have already-bound values that
                used this.
            battle_resolver: Optional escape hatch to override the
                resolver bound to ``config.conflict_engine`` (e.g.
                tests that want to skip combat). Stored on self for
                introspection; the conflict engine itself reads
                whatever resolver was bound at construction time.
            tick_phases: Optional override for the per-tick phase
                descriptor list. Defaults to
                ``DEFAULT_TICK_PHASE_LIST`` (15 entries).
            end_of_turn_phases: Optional override for the end-of-turn
                phase descriptor list. Defaults to
                ``DEFAULT_END_OF_TURN_PHASE_LIST`` (6 entries).
        """
        self._battle_resolver = battle_resolver
        self._ai_factory = ai_factory
        self._registries = registries
        self._event_bus = event_bus
        self._race_registry: Optional['IRaceRegistry'] = race_registry

        # PROJ-369 Phase 3: every sub-engine comes straight from config.
        # `TurnEngineConfig.create_default(...)` is the only sanctioned
        # construction site. No per-property fallback init.
        self._movement_engine = config.movement_engine
        self._production_engine = config.production_engine
        self._order_processor = config.order_processor
        self._conflict_engine = config.conflict_engine
        self._resource_engine = config.resource_engine
        self._population_engine = config.population_engine
        self._resupply_engine = config.resupply_engine
        self._harvesting_engine = config.harvesting_engine
        self._action_engine = config.action_engine
        self._environmental_engine = config.environmental_engine
        self._planet_energy_engine = config.planet_energy_engine
        self._planet_action_engine = config.planet_action_engine
        self._component_activation_engine = config.component_activation_engine
        self._organics_consumption_engine = config.organics_consumption_engine
        self._happiness_engine = config.happiness_engine
        self._quality_engine = config.quality_engine
        self._atmosphere_engine = config.atmosphere_engine
        self._water_engine = config.water_engine

        # PROJ-365: Per-tick phase descriptor list. Defaults to the
        # canonical 15-phase ordering; tests may inject a custom list to
        # exercise reordering or single-phase isolation.
        self._tick_phases: tuple[TickPhase, ...] = (
            tick_phases if tick_phases is not None else DEFAULT_TICK_PHASE_LIST
        )

        # PROJ-369 Phase 1: End-of-turn phase descriptor list. Defaults
        # to the 6-phase ordering pinned by PROJ-284 (organics →
        # happiness → population_growth → quality → atmosphere →
        # water). Tests may inject a custom list for isolation.
        self._end_of_turn_phases: tuple[TickPhase, ...] = (
            end_of_turn_phases
            if end_of_turn_phases is not None
            else DEFAULT_END_OF_TURN_PHASE_LIST
        )

        # PROJ-189: Environmental event storage for UI notification
        self.last_environmental_events: list = []

        # PROJ-251: Track current tick for error context
        self._current_tick: int = 0
        # PROJ-381 Phase 3 (B-2): track turn_number for EnginePhaseError
        # context so crash dumps correlate to the saved turn.
        self._current_turn_number: int = 0
        # save_path is also threaded via _current_save_path at
        # process_turn entry; both keys are added defensively to the
        # error context so dump-and-resume tooling has the breadcrumb.
        self._current_save_path: Optional[str] = None

        # Performance timing accumulators (reset each turn in process_turn)
        self._reset_phase_times()

    def _reset_phase_times(self) -> None:
        """Reset performance timing accumulators to zero."""
        self._phase_times: dict[str, float] = {
            # Tick-loop sub-engines (15 keys).
            'harvesting': 0.0, 'resources': 0.0,
            'fuel_gen': 0.0, 'resupply': 0.0, 'production': 0.0,
            'environmental': 0.0, 'instant_orders': 0.0, 'actions': 0.0,
            'planet_energy': 0.0, 'planet_actions': 0.0, 'activation_timers': 0.0,
            # PROJ-365: planet_modifier_effects is now routed through
            # `_time_phase` like every other tick phase (the descriptor
            # registry treats all phases uniformly). Pre-PROJ-365 the
            # phase was an unwrapped local-construct call.
            'planet_modifier_effects': 0.0,
            'movement_calc': 0.0, 'movement_apply': 0.0, 'combat': 0.0,
            # PROJ-343 T1.2-engines: end-of-turn engines now route through
            # `_time_phase` for rollback safety; their timings live here too.
            'organics_consumption': 0.0, 'happiness': 0.0, 'population_growth': 0.0,
            'quality_improvement': 0.0, 'atmosphere': 0.0, 'water_modification': 0.0,
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
        t0 = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
        except EnginePhaseError:
            # Already wrapped — re-raise as-is
            self._phase_times[key] += time.perf_counter() - t0
            raise
        except Exception as e:  # Intentional broad catch: wraps unknown phase failures as EnginePhaseError(T001) and re-raises with phase_name + tick context; documented strategy-layer pattern.
            self._phase_times[key] += time.perf_counter() - t0
            logger.error(
                "Sub-engine phase '%s' failed during tick processing",
                key, exc_info=True,
            )
            # PROJ-381 Phase 3 (B-2): include turn_number + save_path so
            # crash dumps and the UI dialog can correlate the failure
            # back to the saved turn. `getattr` defensively in case the
            # attribute drifts in future refactors — context construction
            # itself must never raise a secondary error.
            raise EnginePhaseError(
                f"Phase '{key}' failed: {e}",
                code=ErrorCode.PHASE_FAILED.value,
                context={
                    "phase_name": key,
                    "tick": self._current_tick,
                    "turn_number": getattr(self, "_current_turn_number", 0),
                    "save_path": getattr(self, "_current_save_path", None),
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

    def _run_phases(
        self,
        phases: tuple['TickPhase', ...],
        ctx: 'TickContext',
    ) -> None:
        """Iterate a phase descriptor tuple, invoking each through ``_time_phase``.

        PROJ-369 Phase 4: unified iteration shared between the per-tick
        body (``_process_tick``) and the end-of-turn block
        (``process_turn``). Hooks (``pre_exec_hook`` /
        ``post_exec_hook``) and timing-bucket overrides are honored
        uniformly. Accumulated env events are surfaced by the caller
        via ``ctx.last_environmental_events`` after iteration completes.

        Args:
            phases: Frozen tuple of TickPhase descriptors to iterate.
            ctx: Per-iteration TickContext (mutated by hooks).

        Raises:
            EnginePhaseError: From ``_time_phase`` if any phase callable
                raises a non-EnginePhaseError exception (raw exceptions
                are wrapped). Already-wrapped EnginePhaseError raises
                propagate as-is.
        """
        for phase in phases:
            if phase.pre_exec_hook is not None:
                phase.pre_exec_hook(self, ctx)

            target = phase.callable_target(self)
            args, kwargs = phase.args_resolver(ctx)
            bucket = phase.timing_bucket or phase.phase_key
            result = self._time_phase(bucket, target, *args, **kwargs)

            if phase.post_exec_hook is not None:
                phase.post_exec_hook(self, ctx, result)

    # PROJ-369 Phase 3: All 18 engine properties are trivial
    # passthroughs. Construction lives in
    # ``TurnEngineConfig.create_default(...)``; tests override via
    # ``dataclasses.replace(cfg, foo_engine=mock_foo)``. The fallback
    # init that previously sat in each property body is gone; the AST
    # guard test ``test_no_lazy_fallback_init.py`` enforces that.

    @property
    def movement_engine(self) -> 'IMovementEngine':
        """Return injected movement engine."""
        return self._movement_engine

    @property
    def production_engine(self) -> 'IProductionEngine':
        """Return injected production engine."""
        return self._production_engine

    @property
    def order_processor(self) -> 'IOrderProcessor':
        """Return injected order processor."""
        return self._order_processor

    @property
    def conflict_engine(self) -> 'IConflictEngine':
        """Return injected conflict engine."""
        return self._conflict_engine

    @property
    def resource_engine(self) -> 'IConsumableEngine':
        """Return injected resource (consumable) engine."""
        return self._resource_engine

    @property
    def population_engine(self) -> 'IPopulationEngine':
        """Return injected population engine."""
        return self._population_engine

    @property
    def resupply_engine(self) -> 'IResupplyEngine':
        """Return injected resupply engine."""
        return self._resupply_engine

    @property
    def harvesting_engine(self) -> 'IHarvestingEngine':
        """Return injected harvesting engine."""
        return self._harvesting_engine

    @property
    def action_engine(self) -> 'IActionExecutionEngine':
        """Return injected action execution engine."""
        return self._action_engine

    @property
    def environmental_engine(self) -> 'IEnvironmentalHazardEngine':
        """Return injected environmental hazard engine."""
        return self._environmental_engine

    @property
    def planet_energy_engine(self) -> 'IPlanetEnergyEngine':
        """Return injected planet energy engine."""
        return self._planet_energy_engine

    @property
    def planet_action_engine(self) -> 'IPlanetActionEngine':
        """Return injected planet action engine."""
        return self._planet_action_engine

    @property
    def component_activation_engine(self) -> 'IComponentActivationEngine':
        """Return injected component activation engine."""
        return self._component_activation_engine

    @property
    def organics_consumption_engine(self) -> 'IOrganicsConsumptionEngine':
        """Return injected organics consumption engine.

        PROJ-284 Phase 2: drains the configured food resource per turn
        and writes ``last_food_ratio`` for downstream happiness /
        population reads.
        """
        return self._organics_consumption_engine

    @property
    def happiness_engine(self) -> 'IHappinessEngine':
        """Return injected happiness engine.

        PROJ-284 Phase 3: derives ``SpeciesPopulation.happiness`` between
        consumption and population growth.
        """
        return self._happiness_engine

    @property
    def quality_engine(self) -> 'IQualityEngine':
        """Return injected per-turn planet-quality engine."""
        return self._quality_engine

    @property
    def atmosphere_engine(self) -> 'IAtmosphereEngine':
        """Return injected per-turn atmosphere engine."""
        return self._atmosphere_engine

    @property
    def water_engine(self) -> 'IWaterEngine':
        """Return injected per-turn water-level engine."""
        return self._water_engine

    @property
    def planet_modifier_effect_engine(self):
        """Lazy-construct + cache the PlanetModifierEffectEngine.

        PROJ-428 Phase 1 (TD-04): the planet-modifier engine moved off
        the registry module onto TurnEngine. The TD-04 guardrail forbids
        adding a TurnEngineConfig field for this — the engine is
        stateless per tick, so a lazy property + cached instance is
        sufficient. The descriptor in DEFAULT_TICK_PHASE_LIST resolves
        through ``lambda e: e.planet_modifier_effect_engine.process_modifier_effects_tick``.

        First access constructs; subsequent accesses return the same
        bound instance.
        """
        cached = getattr(self, '_planet_modifier_effect_engine_cached', None)
        if cached is None:
            # Local import: PlanetModifierEffectEngine pulls strategy/data
            # types which would create an import cycle at module top.
            from game.strategy.engine.planet_modifier_effect_engine import (
                PlanetModifierEffectEngine,
            )

            cached = PlanetModifierEffectEngine(registries=self._registries)
            self._planet_modifier_effect_engine_cached = cached
        return cached

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
        from game.core.exceptions import EnginePhaseError, PersistenceException
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot

        # Store save_path for tick processing (PROJ-79)
        self._current_save_path = save_path
        # PROJ-381 Phase 3 (B-2): cache turn_number for EnginePhaseError
        # context. Defensive `getattr` because process_turn callers
        # sometimes pass headless sessions / mocks without turn_number.
        self._current_turn_number = (
            getattr(session, "turn_number", 0) if session is not None else 0
        )

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
            except PersistenceException:
                # PROJ-381 Phase 2 (ERR-03-002): TurnStateSnapshot.capture
                # is documented to raise PersistenceException(T003); narrow
                # the catch so any unrelated escape (e.g. a future bug in
                # session/empire lookup above) surfaces unmasked.
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

            # PROJ-343 T1.2-engines / PROJ-369 Phases 1+4: end-of-turn
            # engines route through `_time_phase` (so raw exceptions
            # become EnginePhaseError and the rollback site below
            # catches them) and iterate the
            # `DEFAULT_END_OF_TURN_PHASE_LIST` descriptor list via the
            # shared ``_run_phases`` helper — same shape as the tick
            # body. PROJ-284 ordering invariant (organics → happiness
            # → population_growth) is encoded in the registry's pinned
            # tuple.
            end_of_turn_ctx = TickContext(
                tick=0,  # sentinel: end-of-turn, not in 1..100 loop
                empires=empires,
                galaxy=galaxy,
                component_registry=self._registries.components,
                save_path=save_path,
            )
            self._run_phases(self._end_of_turn_phases, end_of_turn_ctx)

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

            # PROJ-412 Phase 5: drop per-turn caches so a retry on the same
            # turn number (after the snapshot restore) does not reuse
            # multipliers / aggregates computed against the pre-rollback
            # state. Defensive: every engine that grows a per-turn cache
            # under PROJ-412 must expose ``invalidate_turn_caches`` for
            # this hook to find.
            for engine in (self._harvesting_engine, self._production_engine):
                invalidate = getattr(engine, 'invalidate_turn_caches', None)
                if invalidate is not None:
                    try:
                        invalidate()
                    except Exception:  # Intentional broad catch: cache invalidation must not mask the original EnginePhaseError
                        logger.warning(
                            "invalidate_turn_caches raised during rollback; continuing",
                            exc_info=True,
                        )

            raise
        finally:
            # Issue #7: clear the per-tick callback so it doesn't leak
            # into a subsequent process_turn call on this engine instance.
            self._progress_callback = None

        total_time = time.perf_counter() - turn_start
        # PROJ-365 audit remediation (MAJ-001/MAJ-002): include
        # planet_modifier_effects and the five end-of-turn engines that
        # PROJ-343 routed through `_time_phase` so their timings are
        # visible in TURN PERF logs alongside the other phases.
        logger.warning(
            "TURN PERF: total=%.3fs | harvesting=%.3fs "
            "resources=%.3fs fuel_gen=%.3fs planet_energy=%.3fs resupply=%.3fs production=%.3fs "
            "environmental=%.3fs instant_orders=%.3fs actions=%.3fs planet_actions=%.3fs "
            "activation_timers=%.3fs planet_modifier_effects=%.3fs "
            "move_calc=%.3fs move_apply=%.3fs combat=%.3fs "
            "organics_consumption=%.3fs happiness=%.3fs quality_improvement=%.3fs "
            "atmosphere=%.3fs water_modification=%.3fs population=%.3fs",
            total_time, self._phase_times['harvesting'],
            self._phase_times['resources'], self._phase_times['fuel_gen'],
            self._phase_times['planet_energy'], self._phase_times['resupply'],
            self._phase_times['production'],
            self._phase_times['environmental'], self._phase_times['instant_orders'],
            self._phase_times['actions'], self._phase_times['planet_actions'],
            self._phase_times['activation_timers'],
            self._phase_times['planet_modifier_effects'],
            self._phase_times['movement_calc'],
            self._phase_times['movement_apply'], self._phase_times['combat'],
            self._phase_times['organics_consumption'], self._phase_times['happiness'],
            self._phase_times['quality_improvement'], self._phase_times['atmosphere'],
            self._phase_times['water_modification'],
            self._phase_times['population_growth'],
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

        PROJ-365: ``_process_tick`` is now a thin dispatcher that
        iterates ``self._tick_phases`` (the per-tick descriptor list).
        Phase ordering, args resolution, and cross-phase state flow are
        encoded in ``DEFAULT_TICK_PHASE_LIST`` in
        ``turn_phase_registry.py``. Per-phase timing semantics
        (``_time_phase`` / ``EnginePhaseError`` wrap) are preserved.

        Fifteen-phase ordering — see
        ``Projects/active_projects/PROJ-365/findings/01_architecture.md``
        for the canonical phase table:
        Phase 0:    harvesting
        Phase 0b:   resources
        Phase 0c:   fuel_gen
        Phase 0c1:  planet_energy
        Phase 0d:   resupply
        Phase 0e:   production
        Phase 0f:   environmental
        Phase 1:    instant_orders
        Phase 1.5:  actions
        Phase 1.6:  planet_actions
        Phase 1.7:  activation_timers
        Phase 1.8:  planet_modifier_effects
        Phase 2:    movement_calc
        Phase 3:    movement_apply
        Phase 4:    combat

        PROJ-251: Sets _current_tick for error context in EnginePhaseError.
        """

        # PROJ-251: Track current tick for error context
        self._current_tick = tick

        # Issue #7 + PROJ-412 Phase 4: notify the UI on a coarsened cadence
        # so the "PROCESSING TURN..." overlay can repaint without paying
        # the full per-tick redraw cost. The callback is optional and may
        # be None. Fire at tick 1 (overlay shows 1/100 immediately), every
        # PROGRESS_CALLBACK_INTERVAL ticks, and the final tick (overlay
        # closes on 100/100). For the default N=5 this is 21 invocations
        # per turn instead of 100.
        cb = getattr(self, "_progress_callback", None)
        if cb is not None and (
            tick == 1
            or tick == TICKS_PER_TURN
            or tick % PROGRESS_CALLBACK_INTERVAL == 0
        ):
            try:
                cb(tick, TICKS_PER_TURN)
            except Exception:  # Intentional broad catch: UI callback must never break turn processing (PROJ-308)
                logger.warning("progress_callback raised; suppressing", exc_info=True)

        # PROJ-365: Build the per-tick context, then iterate descriptors.
        # PROJ-369 Phase 4: dispatch through the shared ``_run_phases``
        # helper used by both the tick loop and the end-of-turn block.
        ctx = TickContext(
            tick=tick,
            empires=empires,
            galaxy=galaxy,
            component_registry=self._registries.components,
            save_path=save_path,
        )

        self._run_phases(self._tick_phases, ctx)

        # PROJ-189: Surface accumulated environmental events to the
        # public attribute that callers (and tests) read.
        if ctx.last_environmental_events:
            self.last_environmental_events.extend(ctx.last_environmental_events)



