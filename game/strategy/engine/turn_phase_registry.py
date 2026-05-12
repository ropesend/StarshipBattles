"""
PROJ-365 Phase 2 — Tick-phase descriptor registry.

This module defines the data shape used by ``TurnEngine._process_tick``
to declare its 15-phase per-tick sequence as data rather than imperative
code. Phase 3 of PROJ-365 wires ``DEFAULT_TICK_PHASE_LIST`` into
``TurnEngine`` so the tick body becomes a single iteration loop.

Design notes
------------
* ``TickPhase`` is frozen — descriptors are pure metadata and must not
  mutate at runtime.
* ``TickContext`` is mutable — phase post-exec hooks write into it (e.g.
  ``move_queue`` from movement_calc, ``pre_movement_locations`` /
  ``moved_fleet_ids`` for the PROJ-320 movement diff).
* ``callable_target`` is a *resolver* lambda that takes the
  ``TurnEngine`` instance and returns the bound engine method to call.
  This defers engine resolution until iteration time, matching
  ``TurnEngine``'s lazy-property semantics.
* ``args_resolver`` returns a ``(args, kwargs)`` tuple. Phases that take
  positional-only args use ``((...), {})``; phases that mix (e.g.
  ``actions`` passes ``component_registry`` as kwarg) use both halves.
* ``tick_gating`` is documentary metadata for now — Phase 3's dispatch
  loop reads ``ctx.tick`` directly inside hooks to decide whether to
  fire. See ``Projects/active_projects/PROJ-365/decisions.md`` for the
  rationale.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# PROJ-412 Phase 2.3: import the engine at module top so the per-tick
# resolver doesn't pay the import lookup on each of the 100 invocations.
# Aliased to a leading underscore to signal it's a private detail of
# the descriptor resolver below.
from game.strategy.engine.planet_modifier_effect_engine import (
    PlanetModifierEffectEngine as _PlanetModifierEffectEngine,
)

# Sentinel: applied to descriptors whose pre/post hooks should only fire
# on tick==1. The dispatch loop does not gate the phase call itself —
# the harvesting / production calls run on every tick. Hooks are
# expected to inspect ``ctx.tick`` themselves; this constant exists for
# readability and as a future hook point for stricter enforcement.
TICK_GATE_ONLY_TICK_1 = 'only_tick_1'


@dataclass
class TickContext:
    """Mutable per-tick context object passed to descriptors.

    Cross-phase state flows through this object instead of through
    closures or instance attributes on ``TurnEngine``. Hooks are free
    to write back any field; phases later in the iteration order read
    them via their ``args_resolver``.

    PROJ-369: ``TickContext`` is also reused for the end-of-turn
    descriptor block (``DEFAULT_END_OF_TURN_PHASE_LIST``). End-of-turn
    invocations pass ``tick=0`` as a sentinel — impossible during the
    1..100 tick loop and unambiguous as "after the tick loop completed".
    """

    tick: int
    empires: list
    galaxy: object
    component_registry: object = None
    save_path: str | None = None

    # Mid-tick scratch fields written by hooks
    move_queue: Any = None
    pre_movement_locations: dict | None = None
    moved_fleet_ids: set | None = None

    # PROJ-189: storms accumulate event lists, surfaced via
    # TurnEngine.last_environmental_events after the tick completes.
    last_environmental_events: list = field(default_factory=list)


@dataclass(frozen=True)
class TickPhase:
    """Frozen descriptor for one per-tick phase.

    Attributes:
        phase_key: Identity + default timing-bucket key. Must be unique
            across ``DEFAULT_TICK_PHASE_LIST``.
        callable_target: ``lambda engine -> bound method``. Resolves the
            target callable given the live ``TurnEngine`` instance.
        args_resolver: ``lambda ctx -> (args_tuple, kwargs_dict)``. Maps
            the per-tick context to the phase call's argument shape.
        error_policy: ``'wrap'`` (default — current behavior, raises
            ``EnginePhaseError``) or ``'barrier'`` (reserved for future
            use; treated as ``'wrap'`` today).
        tick_gating: Documentary; ``'only_tick_1'`` if hooks should only
            fire on tick==1. Hooks must enforce gating themselves.
        timing_bucket: Override for the ``_phase_times`` accumulator
            key. Defaults to ``phase_key`` when ``None``.
        pre_exec_hook: ``lambda engine, ctx -> None`` invoked before the
            phase callable runs. Used for the 'TURN START tick=1'
            empire-state log.
        post_exec_hook: ``lambda engine, ctx, result -> None`` invoked
            after the phase callable returns. Used for the
            'Tick 1 AFTER CONSTRUCTION' log, the env-events accumulator
            push, the pre-Phase-3 location snapshot, and the PROJ-320
            ``moved_fleet_ids`` derivation.
    """

    phase_key: str
    callable_target: Callable[[Any], Callable[..., Any]]
    args_resolver: Callable[[TickContext], tuple]
    error_policy: str = 'wrap'
    tick_gating: str | None = None
    timing_bucket: str | None = None
    pre_exec_hook: Callable[[Any, TickContext], None] | None = None
    post_exec_hook: Callable[[Any, TickContext, Any], None] | None = None


# ---------------------------------------------------------------------------
# Hook helpers (module-level so they keep ``TickPhase`` frozen and hashable
# without anonymous closures cluttering the registry literal below).
# ---------------------------------------------------------------------------


def _log_turn_start_tick_1(engine, ctx: TickContext) -> None:
    """Pre-hook on harvesting: only fires on tick==1."""
    if ctx.tick == 1:
        engine._log_empire_state(ctx.empires, "TURN START tick=1")


def _log_after_construction_tick_1(engine, ctx: TickContext, _result) -> None:
    """Post-hook on production: only fires on tick==1."""
    if ctx.tick == 1:
        engine._log_empire_state(ctx.empires, "Tick 1 AFTER CONSTRUCTION")


def _accumulate_env_events(engine, ctx: TickContext, result) -> None:
    """Post-hook on environmental: push returned events onto ctx."""
    if result:
        ctx.last_environmental_events.extend(result)


def _capture_move_queue(_engine, ctx: TickContext, result) -> None:
    """Post-hook on movement_calc: stash the move_queue for movement_apply.

    Also captures ``pre_movement_locations`` so the PROJ-320 diff can
    derive ``moved_fleet_ids`` after movement_apply.
    """
    ctx.move_queue = result
    ctx.pre_movement_locations = {
        f.id: f.location for emp in ctx.empires for f in emp.fleets
    }


def _derive_moved_fleet_ids(_engine, ctx: TickContext, _result) -> None:
    """Post-hook on movement_apply: PROJ-320 location-diff derivation.

    PROJ-412 Phase 5: also flips ``_booster_dirty`` on every empire whose
    fleet actually moved this tick. Fleets can carry ``ResourceHarvestBooster``
    components, so a move invalidates the harvesting engine's per-turn
    booster cache for any empire that has a moved fleet.
    """
    pre = ctx.pre_movement_locations or {}
    moved_owner_ids: set = set()
    moved_ids: set = set()
    for emp in ctx.empires:
        emp_id = getattr(emp, 'id', None)
        for f in emp.fleets:
            if pre.get(f.id) != f.location:
                moved_ids.add(f.id)
                if emp_id is not None:
                    moved_owner_ids.add(emp_id)
    ctx.moved_fleet_ids = moved_ids
    if moved_owner_ids:
        for emp in ctx.empires:
            if getattr(emp, 'id', None) in moved_owner_ids:
                emp._booster_dirty = True


def _resolve_planet_modifier_effects(engine):
    """Resolver for the locally-constructed PlanetModifierEffectEngine.

    PROJ-412 Phase 2.3: the engine is stateless per tick. The
    pre-Phase-2 implementation constructed a fresh instance + did a late
    import on every tick (100 allocations + 100 import lookups per turn).
    Lazy-cache on the TurnEngine instance instead; first call constructs,
    subsequent calls reuse the same bound method.
    """
    cached = getattr(engine, '_planet_modifier_effect_engine_cached', None)
    if cached is None:
        cached = _PlanetModifierEffectEngine(registries=engine._registries)
        engine._planet_modifier_effect_engine_cached = cached
    return cached.process_modifier_effects_tick


# ---------------------------------------------------------------------------
# PROJ-369 Phase 2: Quality / Atmosphere / Water engines are now
# injectable via TurnEngineConfig + TurnEngine lazy properties (mirror
# of the existing 15 sub-engines). The end-of-turn descriptors below
# resolve through ``e.quality_engine`` / ``e.atmosphere_engine`` /
# ``e.water_engine`` instead of constructing fresh instances per call.
# Phase 1's per-call resolver helpers are deleted.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DEFAULT_TICK_PHASE_LIST — 15 entries, in the exact order that the
# imperative ``_process_tick`` body executes them. The Phase 1 golden
# test (``test_default_tick_phase_list.py``) pins this order; any
# accidental reordering trips a test failure immediately.
# ---------------------------------------------------------------------------

DEFAULT_TICK_PHASE_LIST: tuple[TickPhase, ...] = (
    # --- Phase 0: Harvesting (1/100th per tick) ---
    TickPhase(
        phase_key='harvesting',
        callable_target=lambda e: e.harvesting_engine.process_harvesting_tick,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires, ctx.galaxy), {}),
        tick_gating=TICK_GATE_ONLY_TICK_1,  # hook-only gating
        pre_exec_hook=_log_turn_start_tick_1,
    ),
    # --- Phase 0b: Per-turn Resource Consumption ---
    TickPhase(
        phase_key='resources',
        callable_target=lambda e: e.resource_engine.process_per_turn_consumption,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires), {}),
    ),
    # --- Phase 0c: Fuel generation at facilities ---
    TickPhase(
        phase_key='fuel_gen',
        callable_target=lambda e: e.resupply_engine.process_fuel_generation,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires), {}),
    ),
    # --- Phase 0c1: Planet Energy ---
    TickPhase(
        phase_key='planet_energy',
        callable_target=lambda e: e.planet_energy_engine.process_energy_tick,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires), {}),
    ),
    # --- Phase 0d: Fleet resupply from facilities ---
    TickPhase(
        phase_key='resupply',
        callable_target=lambda e: e.resupply_engine.process_fleet_resupply,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires, ctx.galaxy), {}),
    ),
    # --- Phase 0e: Construction resource consumption ---
    TickPhase(
        phase_key='production',
        callable_target=lambda e: e.production_engine.process_construction_tick,
        args_resolver=lambda ctx: (
            (ctx.tick, ctx.empires, ctx.galaxy),
            {'save_path': ctx.save_path},
        ),
        tick_gating=TICK_GATE_ONLY_TICK_1,  # hook-only gating
        post_exec_hook=_log_after_construction_tick_1,
    ),
    # --- Phase 0f: Environmental Hazards ---
    TickPhase(
        phase_key='environmental',
        callable_target=lambda e: e.environmental_engine.process_environmental_tick,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires, ctx.galaxy), {}),
        post_exec_hook=_accumulate_env_events,
    ),
    # --- Phase 1: Instant Orders (JOIN_FLEET) ---
    TickPhase(
        phase_key='instant_orders',
        callable_target=lambda e: e.order_processor.process_instant_orders,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
    # --- Phase 1.5: Action Orders ---
    TickPhase(
        phase_key='actions',
        callable_target=lambda e: e.action_engine.process_action_ticks,
        args_resolver=lambda ctx: (
            (ctx.empires, ctx.galaxy, ctx.tick),
            {
                'component_registry': ctx.component_registry,
                'all_empires': ctx.empires,
            },
        ),
    ),
    # --- Phase 1.6: Planet Action Orders ---
    TickPhase(
        phase_key='planet_actions',
        callable_target=lambda e: e.planet_action_engine.process_planet_actions_tick,
        args_resolver=lambda ctx: (
            (ctx.tick, ctx.empires),
            {'component_registry': ctx.component_registry},
        ),
    ),
    # --- Phase 1.7: Component Activation Timers ---
    TickPhase(
        phase_key='activation_timers',
        callable_target=lambda e: e.component_activation_engine.process_activation_tick,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires), {}),
    ),
    # --- Phase 1.8: Planet Modifier Effects (gravity/radiation) ---
    # NOTE: this phase is constructed locally per tick (matching legacy
    # ``turn_engine.py:751`` behavior). The resolver returns the bound
    # ``process_modifier_effects_tick`` of a fresh instance each call.
    TickPhase(
        phase_key='planet_modifier_effects',
        callable_target=_resolve_planet_modifier_effects,
        args_resolver=lambda ctx: ((ctx.tick, ctx.empires), {}),
    ),
    # --- Phase 2: Calculate Moves ---
    TickPhase(
        phase_key='movement_calc',
        callable_target=lambda e: e.movement_engine.collect_movements,
        args_resolver=lambda ctx: ((ctx.empires, ctx.galaxy, ctx.tick), {}),
        # PROJ-320: capture move_queue + pre-Phase-3 fleet locations
        # so movement_apply has its arg and the post-apply diff can
        # derive moved_fleet_ids for combat.
        post_exec_hook=_capture_move_queue,
    ),
    # --- Phase 3: Apply Moves ---
    TickPhase(
        phase_key='movement_apply',
        callable_target=lambda e: e.movement_engine.apply_movements,
        args_resolver=lambda ctx: ((ctx.move_queue, ctx.galaxy), {}),
        post_exec_hook=_derive_moved_fleet_ids,
    ),
    # --- Phase 4: Combat ---
    TickPhase(
        phase_key='combat',
        callable_target=lambda e: e.conflict_engine.resolve_all_conflicts,
        args_resolver=lambda ctx: (
            (ctx.empires,),
            {
                'galaxy': ctx.galaxy,
                'tick': ctx.tick,
                'moved_fleet_ids': ctx.moved_fleet_ids,
            },
        ),
    ),
)


# ---------------------------------------------------------------------------
# DEFAULT_END_OF_TURN_PHASE_LIST — 6 entries (PROJ-369 Phase 1).
#
# These descriptors describe the end-of-turn block that runs ONCE per
# turn after the 100-tick loop finishes. The order is pinned by the
# PROJ-284 invariant: organics_consumption writes ``last_food_ratio``
# → happiness reads it → population_growth reads happiness. Reordering
# would silently break gameplay.
#
# All six descriptors route through ``_time_phase`` (PROJ-343
# T1.2-engines) so a raise becomes ``EnginePhaseError`` and the
# rollback site in ``process_turn`` catches it.
#
# Phase 1 keeps QualityEngine / AtmosphereEngine / WaterEngine
# locally constructed inside resolvers (matching the legacy semantics).
# Phase 2 makes them injectable; the resolver helpers below are
# replaced by inline ``lambda e: e.foo_engine.X`` accessors then.
#
# End-of-turn descriptors invoke with ``TickContext(tick=0, ...)`` —
# tick=0 is impossible during the 1..100 loop and unambiguous as
# "after the tick loop". See ``TickContext`` docstring.
# ---------------------------------------------------------------------------

DEFAULT_END_OF_TURN_PHASE_LIST: tuple[TickPhase, ...] = (
    # PROJ-284 Phase 2: Food consumption runs BEFORE happiness so
    # ``last_food_ratio`` is fresh for the happiness formula.
    TickPhase(
        phase_key='organics_consumption',
        callable_target=lambda e: e.organics_consumption_engine.process_consumption,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
    # PROJ-284 Phase 3: Happiness derives between consumption and pop
    # growth so ``pop.happiness`` carries no stale value into
    # ``PopulationEngine._grow_species``.
    TickPhase(
        phase_key='happiness',
        callable_target=lambda e: e.happiness_engine.process_happiness,
        args_resolver=lambda ctx: ((ctx.empires, ctx.galaxy), {}),
    ),
    # PROJ-68: Population growth uses freshly derived happiness.
    TickPhase(
        phase_key='population_growth',
        callable_target=lambda e: e.population_engine.process_population_growth,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
    # PROJ-369 Phase 2: Quality / Atmosphere / Water engines are now
    # injectable via TurnEngineConfig and resolved through the
    # TurnEngine lazy properties (same shape as the other 15
    # sub-engines).
    TickPhase(
        phase_key='quality_improvement',
        callable_target=lambda e: e.quality_engine.process_quality_improvement,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
    TickPhase(
        phase_key='atmosphere',
        callable_target=lambda e: e.atmosphere_engine.process_atmosphere,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
    TickPhase(
        phase_key='water_modification',
        callable_target=lambda e: e.water_engine.process_water_modification,
        args_resolver=lambda ctx: ((ctx.empires,), {}),
    ),
)
