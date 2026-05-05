# Phase 2: Define TickPhase + TickContext + DEFAULT_TICK_PHASE_LIST

**Status:** Not Started
**Objective:** Land the descriptor types and the default phase list. No production behavior change yet — Phase 3 wires them in.

---

## Tasks

### Task 2.1: Create turn_phase_registry module [Medium]
**File:** `game/strategy/engine/turn_phase_registry.py` (new)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py -v`

- [ ] Module docstring referencing PROJ-365 Phase 2.
- [ ] Define `TickContext` (mutable):
  ```python
  @dataclass
  class TickContext:
      tick: int
      empires: list
      galaxy: object
      component_registry: dict | None = None
      save_path: str | None = None
      pre_movement_locations: dict | None = None    # set by phase 3 post_exec hook
      moved_fleet_ids: set | None = None            # derived after phase 3
      last_environmental_events: list = field(default_factory=list)
      progress_callback: Callable | None = None
  ```
- [ ] Define `TickPhase` (frozen):
  ```python
  @dataclass(frozen=True)
  class TickPhase:
      phase_key: str
      callable_target: Callable                       # lambda engine: engine.X.process_X_tick
      args_resolver: Callable[[TickContext], tuple]
      error_policy: str = 'wrap'
      tick_gating: str | None = None
      timing_bucket: str | None = None
      post_exec_hook: Callable | None = None          # signature: (engine, ctx, result) -> None
  ```

**Notes:** _(filled during implementation)_

### Task 2.2: Define DEFAULT_TICK_PHASE_LIST [Complex]
**File:** Same

- [ ] One TickPhase per current tick phase, in order. Examples:
  ```python
  TickPhase(
      phase_key='harvesting',
      callable_target=lambda e: e.harvesting_engine.process_harvesting_tick,
      args_resolver=lambda ctx: (ctx.tick, ctx.empires, ctx.galaxy),
      tick_gating=None,
      post_exec_hook=lambda e, ctx, _: e._log_empire_state(ctx.empires, "TURN START tick=1") if ctx.tick == 1 else None,
  ),
  # ... etc, 14 entries total
  TickPhase(
      phase_key='movement_apply',
      callable_target=lambda e: e.movement_engine.apply_movements,
      args_resolver=lambda ctx: (ctx.move_queue, ctx.galaxy),
      post_exec_hook=lambda e, ctx, _: ctx.__setattr__(
          'moved_fleet_ids',
          {f.id for emp in ctx.empires for f in emp.fleets
           if ctx.pre_movement_locations.get(f.id) != f.location}
      ),
  ),
  TickPhase(
      phase_key='combat',
      callable_target=lambda e: e.conflict_engine.resolve_all_conflicts,
      args_resolver=lambda ctx: (ctx.empires,),
      # combat needs galaxy=ctx.galaxy, tick=ctx.tick, moved_fleet_ids=ctx.moved_fleet_ids as kwargs
      # — design: args_resolver returns (positional, kwargs) tuple, OR a single callable that wraps the kwargs
  ),
  ```
- [ ] Decide args_resolver shape — leaning toward returning `(args, kwargs)` tuple to handle phases like combat which uses kwargs.
- [ ] Add `move_queue` to TickContext — phase 2 (movement_calc) sets it via post_exec_hook, phase 3 (movement_apply) reads it via args_resolver.
- [ ] For phase 2 (movement_calc): post_exec_hook captures the return value of `collect_movements` into `ctx.move_queue`.
- [ ] For phase 0e (production): args includes `save_path` from ctx.
- [ ] Pre-movement-locations snapshot: phase 2's post_exec_hook OR a "barrier" virtual phase — design choice. Recommendation: put it as a one-line `post_exec_hook` on movement_calc that snapshots `pre_movement_locations`.

**Notes:** _(filled during implementation)_

### Task 2.3: Unit tests for TickPhase and TickContext [Simple]
**File:** `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` (new)

- [ ] `test_tick_phase_is_frozen` — assignment raises FrozenInstanceError.
- [ ] `test_tick_context_mutable` — assignment succeeds; default factory for `last_environmental_events` is independent per instance.
- [ ] `test_default_phase_list_count` — `len(DEFAULT_TICK_PHASE_LIST) == 14` (or whatever count after final design).
- [ ] `test_default_phase_list_order_matches_golden` — assert `[p.phase_key for p in DEFAULT_TICK_PHASE_LIST] == GOLDEN_PHASE_ORDER` (reuse Phase 1 constant).
- [ ] `test_phase_keys_unique` — no duplicates.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] turn_phase_registry.py exists with TickPhase, TickContext, DEFAULT_TICK_PHASE_LIST
- [ ] All Phase 2 unit tests green
- [ ] Phase 1 golden-list test still green (production unchanged)
- [ ] Update plan.md phase table to `Complete`; Current State → Phase 3
