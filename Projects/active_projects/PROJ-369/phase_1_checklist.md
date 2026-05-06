# Phase 1: Extract end-of-turn block to `DEFAULT_END_OF_TURN_PHASE_LIST`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-369 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** —
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_phase_registry.py` (modify)
- `game/strategy/engine/turn_engine.py` (modify — `process_turn` end-of-turn block)
- `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` (new)
- `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` (verify still green)

**Objective:** Mirror PROJ-365 for the 6 end-of-turn engines so `process_turn:587-620` becomes one descriptor iteration. The 3 locally-constructed engines (`QualityEngine`, `AtmosphereEngine`, `WaterEngine`) STAY locally constructed in this phase — the descriptor's `callable_target` resolver constructs a fresh instance per call (matches today's per-turn instantiation semantics, see `turn_phase_registry.py:152-164` for the precedent with `PlanetModifierEffectEngine`). Phase 2 makes them injectable.

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State
- [ ] Verify `turn_engine.py:587-620` (end-of-turn block) is unchanged from baseline (no other in-flight branch has touched it). Capture exact line range — code locations may have drifted.
- [ ] `pytest tests/unit/strategy/turn_engine/ -v` — capture green baseline (110+ tests per PROJ-365 final state)

---

## Tasks

### Task 1.1: Golden-list test for end-of-turn descriptors (TDD-first) [Simple]
**File:** `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` (new)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v`

- [ ] Create file with module docstring referencing PROJ-369 Phase 1 and the PROJ-284 ordering invariant (organics → happiness → population_growth)
- [ ] Test `test_end_of_turn_phase_list_pinned_order`: assert `tuple(p.phase_key for p in DEFAULT_END_OF_TURN_PHASE_LIST) == ('organics_consumption', 'happiness', 'population_growth', 'quality_improvement', 'atmosphere', 'water_modification')`
- [ ] Test `test_end_of_turn_phase_list_length_6`: assert `len(DEFAULT_END_OF_TURN_PHASE_LIST) == 6`
- [ ] Test `test_end_of_turn_phase_keys_match_phase_times_buckets`: import `TurnEngine`, instantiate, assert every `p.phase_key` (or `p.timing_bucket` when set) is a key in `engine._phase_times`
- [ ] Test `test_each_descriptor_is_frozen_TickPhase`: assert each entry is a `TickPhase` instance and immutable (raises on attribute assignment)
- [ ] Run the test; **confirm it fails** with `ImportError: cannot import name 'DEFAULT_END_OF_TURN_PHASE_LIST'`
- [ ] **Verify:** test fails for the right reason (import error, not assertion error)

**Notes:**

### Task 1.2: Add `DEFAULT_END_OF_TURN_PHASE_LIST` to registry [Medium]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v`

- [ ] Add module-level constant `DEFAULT_END_OF_TURN_PHASE_LIST: tuple[TickPhase, ...]` after the existing `DEFAULT_TICK_PHASE_LIST` (line 297)
- [ ] Six descriptors in order:
  ```python
  DEFAULT_END_OF_TURN_PHASE_LIST: tuple[TickPhase, ...] = (
      TickPhase(
          phase_key='organics_consumption',
          callable_target=lambda e: e.organics_consumption_engine.process_consumption,
          args_resolver=lambda ctx: ((ctx.empires,), {}),
      ),
      TickPhase(
          phase_key='happiness',
          callable_target=lambda e: e.happiness_engine.process_happiness,
          args_resolver=lambda ctx: ((ctx.empires, ctx.galaxy), {}),
      ),
      TickPhase(
          phase_key='population_growth',
          callable_target=lambda e: e.population_engine.process_population_growth,
          args_resolver=lambda ctx: ((ctx.empires,), {}),
      ),
      TickPhase(
          phase_key='quality_improvement',
          callable_target=_resolve_quality_engine,           # local resolver (Phase 1)
          args_resolver=lambda ctx: ((ctx.empires,), {}),
      ),
      TickPhase(
          phase_key='atmosphere',
          callable_target=_resolve_atmosphere_engine,
          args_resolver=lambda ctx: ((ctx.empires,), {}),
      ),
      TickPhase(
          phase_key='water_modification',
          callable_target=_resolve_water_engine,
          args_resolver=lambda ctx: ((ctx.empires,), {}),
      ),
  )
  ```
- [ ] Add the 3 local resolver helpers (mirror `_resolve_planet_modifier_effects` at line 152):
  ```python
  def _resolve_quality_engine(engine):
      from game.strategy.engine.quality_engine import QualityEngine
      return QualityEngine(registries=engine._registries).process_quality_improvement

  def _resolve_atmosphere_engine(engine):
      from game.strategy.engine.atmosphere_engine import AtmosphereEngine
      return AtmosphereEngine(registries=engine._registries).process_atmosphere

  def _resolve_water_engine(engine):
      from game.strategy.engine.water_engine import WaterEngine
      return WaterEngine(registries=engine._registries).process_water_modification
  ```
- [ ] Update module docstring to mention end-of-turn list
- [ ] Document `tick=0` sentinel for `TickContext` when used with end-of-turn list (add to `TickContext` docstring at line 42)
- [ ] **Verify:** Task 1.1 tests now pass

**Notes:**

### Task 1.3: Replace `process_turn` end-of-turn imperative block with descriptor iteration [Medium]
**File:** `game/strategy/engine/turn_engine.py:587-620`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py -v`

- [ ] At top of file (line 67), add import: `from game.strategy.engine.turn_phase_registry import DEFAULT_END_OF_TURN_PHASE_LIST`
- [ ] In `__init__` after the `tick_phases` field (line 228-230), add a sibling `end_of_turn_phases` field:
  ```python
  self._end_of_turn_phases: tuple[TickPhase, ...] = (
      end_of_turn_phases if end_of_turn_phases is not None else DEFAULT_END_OF_TURN_PHASE_LIST
  )
  ```
- [ ] Add `end_of_turn_phases: Optional[tuple['TickPhase', ...]] = None` to `__init__` signature (after `tick_phases`, line 168)
- [ ] In `process_turn` body, replace lines 587-620 with:
  ```python
  end_of_turn_ctx = TickContext(
      tick=0,                      # sentinel — end-of-turn, not in 1..100 loop
      empires=empires,
      galaxy=galaxy,
      component_registry=self._registries.components,
      save_path=save_path,
  )
  for phase in self._end_of_turn_phases:
      target = phase.callable_target(self)
      args, kwargs = phase.args_resolver(end_of_turn_ctx)
      bucket = phase.timing_bucket or phase.phase_key
      self._time_phase(bucket, target, *args, **kwargs)
  ```
- [ ] Verify the existing `test_turn_engine_end_of_turn_order.py:43-92` ordering test still passes (it patches the engines as mocks; descriptor iteration calls them in the same order)
- [ ] Verify the `patch('game.strategy.engine.quality_engine.QualityEngine')` patches at lines 70/110/163 of that test still resolve — the descriptor's `_resolve_quality_engine` does `from game.strategy.engine.quality_engine import QualityEngine` which is patchable at that path
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py -v` — all 3 tests pass
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py -v` — rollback tests still pass (descriptor still routes through `_time_phase`)

**Notes:**

### Task 1.4: Update `TURN PERF` log to use descriptor iteration [Simple]
**File:** `game/strategy/engine/turn_engine.py:642-669`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py -v`

- [ ] No format changes — the `_phase_times` dict already has all 21 keys (15 tick + 6 end-of-turn). The hard-coded log line is still correct.
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py -v` — phase-timing tests pass with no changes

**Notes:**

### Task 1.5: Full focused-test pass [Medium]
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v` and `pytest tests/integration/strategy/ -v`

- [ ] Run focused unit tests; assert pass count = baseline + 4 (Task 1.1 added 4 tests)
- [ ] Run strategy integration tests; assert no regressions
- [ ] **Acceptance:** zero regressions; new tests added pass

**Notes:**

### Task 1.6: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ baseline + 4
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 1.7: Commit Phase 1 [Simple]

- [ ] `git status --short` — verify only files in this checklist's "Files (planned)" appear
- [ ] Stage explicitly (no `git add -A`)
- [ ] Commit message: `feat(PROJ-369): Phase 1 — extract end-of-turn block to DEFAULT_END_OF_TURN_PHASE_LIST descriptor`
- [ ] Sign-off: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Do NOT push
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-369 1 --repo .worktrees/phases/PROJ-369/1` (or current worktree per 03c protocol)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `DEFAULT_END_OF_TURN_PHASE_LIST` exists with 6 entries in pinned order
- [ ] `process_turn` end-of-turn block is one descriptor iteration loop
- [ ] All 21 `_phase_times` keys still populated after a `process_turn` run
- [ ] Existing `test_turn_engine_end_of_turn_order.py` still green (mock patches still work)
- [ ] Update status at top of this file to `Complete (Committed)` (or `Complete (Verified)` after review)
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
