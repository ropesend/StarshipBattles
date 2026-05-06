# Phase 4: Unified phase-execution loop

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-369 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_engine.py` (modify — extract `_run_phases` helper; collapse `_process_tick` body and `process_turn` end-of-turn block to single helper invocations)
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` (modify — assert all 21 buckets populated)
- `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` (verify still green)
- `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` (verify still green)

**Objective:** The 100-tick body and the end-of-turn block both iterate descriptors today (post-Phase 1). Both have nearly identical iteration logic. Extract `_run_phases(self, phases, ctx) -> None` once; call it from both places. `process_turn` becomes structurally trivial: a 100-iteration loop and one end-of-turn call.

---

## Pre-flight

- [ ] Verify Phase 3 status is `verified` (or `committed`) per `phase_dag.py status`

---

## Tasks

### Task 4.1: Extract `_run_phases` helper [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v`

- [ ] Add private method on `TurnEngine` (place near `_time_phase`, around line 305):
  ```python
  def _run_phases(
      self,
      phases: tuple['TickPhase', ...],
      ctx: 'TickContext',
  ) -> None:
      """Iterate a phase descriptor tuple, invoking each through _time_phase.

      PROJ-369 Phase 4: unified iteration shared between the per-tick body
      and the end-of-turn block. Hooks (pre_exec_hook, post_exec_hook) and
      timing buckets are honored uniformly. Accumulated env events are
      surfaced by the caller via ctx.last_environmental_events (post-tick).

      Args:
          phases: Frozen tuple of TickPhase descriptors to iterate.
          ctx: Per-iteration TickContext (mutated by hooks).

      Raises:
          EnginePhaseError: From _time_phase if any phase callable raises.
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
  ```
- [ ] **Verify:** unit tests still pass (helper is dead code at this point — no caller yet)

**Notes:**

### Task 4.2: Collapse `_process_tick` body to one `_run_phases` call [Medium]
**File:** `game/strategy/engine/turn_engine.py:691-760` (post-Phase 3 line range)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_tick_phase_list.py tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py -v`

- [ ] Replace the descriptor-iteration loop body in `_process_tick` (currently lines 745-755 of post-PROJ-365 code) with:
  ```python
  ctx = TickContext(
      tick=tick,
      empires=empires,
      galaxy=galaxy,
      component_registry=self._registries.components,
      save_path=save_path,
  )
  self._run_phases(self._tick_phases, ctx)

  # PROJ-189: surface accumulated environmental events.
  if ctx.last_environmental_events:
      self.last_environmental_events.extend(ctx.last_environmental_events)
  ```
- [ ] Keep PROJ-251 `_current_tick` assignment and Issue #7 progress callback invocation unchanged
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_default_tick_phase_list.py tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py -v` — green

**Notes:**

### Task 4.3: Collapse end-of-turn block to one `_run_phases` call [Medium]
**File:** `game/strategy/engine/turn_engine.py` (post-Phase 1 end-of-turn descriptor block)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v`

- [ ] Replace the Phase-1 inline iteration (added in Phase 1 Task 1.3) with:
  ```python
  end_of_turn_ctx = TickContext(
      tick=0,
      empires=empires,
      galaxy=galaxy,
      component_registry=self._registries.components,
      save_path=save_path,
  )
  self._run_phases(self._end_of_turn_phases, end_of_turn_ctx)
  ```
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v` — green

**Notes:**

### Task 4.4: Update phase-timing test to assert all 21 buckets [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py -v`

- [ ] Add test `test_all_21_phase_time_buckets_populated_after_process_turn`: instantiate engine via `TurnEngineConfig.create_default(...)`, run `process_turn(empires=[mock_empire], galaxy=mock_galaxy)`, assert `len(engine._phase_times) == 21` and every bucket has been hit at least once.
- [ ] **Verify:** new test passes

**Notes:**

### Task 4.5: Performance sanity check [Simple]
**Tests:** Manual — record `TURN PERF` log output before and after Phase 4

- [ ] Run a 5-turn integration test (e.g., `tests/integration/gameplay_loop/test_turn_execution.py::test_baseline_5_turns`); inspect `TURN PERF` log lines.
- [ ] Verify total turn time has not regressed by more than +5% relative to the Phase 3 baseline.
- [ ] **Verify:** no hot path slowed (the `_run_phases` indirection adds ≤21 Python calls per turn, negligible)

**Notes:**

### Task 4.6: Full focused-test pass [Medium]
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v` and `pytest tests/integration/strategy/ -v`

- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 4.7: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] **Acceptance:** zero regressions; pass count ≥ Phase 3 baseline + 1 (Task 4.4 added 1 test)

**Notes:**

### Task 4.8: Commit Phase 4 [Simple]

- [ ] Commit message: `feat(PROJ-369): Phase 4 — unify tick + end-of-turn execution loops via _run_phases helper`
- [ ] Run `phase_complete.py PROJ-369 4`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `_run_phases` helper exists; called exactly twice in `process_turn`
- [ ] `_process_tick` body collapses to ctx-build + `_run_phases` + env-events surface
- [ ] End-of-turn block collapses to ctx-build + `_run_phases`
- [ ] All 21 `_phase_times` buckets populated after `process_turn`
- [ ] Total turn time within +5% of pre-phase baseline
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
