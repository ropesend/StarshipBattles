# Phase 1: Sink wiring + ReplayStore + bootstrap-test cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Construct `ReplayStore` in `bootstrap()`; register it as the production capture sink and the production save-lifecycle store. Add autouse cleanup fixtures in BOTH bootstrap test modules so the new coordinator threads (introduced in Phase 2) don't leak between tests. Phase 0 must be complete before this phase starts.

See `plan.md` Phase 1 for context. r001 deltas: source-module monkeypatch targets, autouse cleanup, insertion-point standardization.

---

## Tasks

### Task 1.1: Failing-test-first — pin sink + store registration in bootstrap [Simple]
**File:** `tests/unit/test_app_bootstrap_invariants.py` (modify)
**Tests:** `pytest tests/unit/test_app_bootstrap_invariants.py -v`

- [ ] Read the existing module to understand the invariant-test style.
- [ ] Add `test_invariant_7_replay_store_registered_after_input_mapper`: monkeypatch the SOURCE modules — `game.simulation.replay.replay_capture.set_default_capture_sink` and `game.strategy.systems.save_game_service.set_replay_store` — to record call order; run `bootstrap()` (or its `_patched_bootstrap` helper); assert both were called exactly once AFTER `InputMapper.load(...)` and BEFORE the function returns.
- [ ] Run the test. **Expect failure** (the production code does not call them yet).
- [ ] Update phase checklist note.

**Notes:**

### Task 1.2: Construct `ReplayStore` in `bootstrap()` [Simple]
**File:** `game/app_bootstrap.py`
**Tests:** Task 1.1 should now pass.

- [ ] Add lazy imports inside `bootstrap()`'s body (NOT module-level — match the existing late-import pattern):
  - `from game.simulation.replay.replay_capture import set_default_capture_sink`
  - `from game.strategy.systems.save_game_service import set_replay_store`
  - `from game.strategy.services.replay_store import ReplayStore, load_replay_settings`
- [ ] AFTER `InputMapper.load(...)` (around line 260) and BEFORE the `dt_total` summary log, add:
  ```python
  with _timed_phase("replay.construct_store", ctx.profiler):
      replay_settings = load_replay_settings()
      replay_store = ReplayStore(settings=replay_settings)
      set_default_capture_sink(replay_store)
      set_replay_store(replay_store)
  ```
  Note: the SAME `replay_settings` instance is reused by Phase 2's coordinator construction.
- [ ] **Verify:** Task 1.1's invariant test passes.

**Notes:**

### Task 1.3: Add autouse cleanup fixture to BOTH bootstrap test modules [Simple]
**Files:** `tests/unit/test_app_bootstrap_invariants.py`, `tests/unit/test_app_bootstrap_profiling.py`
**Tests:** Both modules

- [ ] In each module, add an autouse fixture (pattern from
  `tests/unit/strategy/services/test_replay_verification_coordinator.py:93-98`):
  ```python
  @pytest.fixture(autouse=True)
  def _drain_replay_globals():
      yield
      from game.strategy.services.replay_verification_coordinator import shutdown_all_coordinators
      from game.simulation.replay.replay_capture import reset_default_capture_sink
      from game.strategy.systems.save_game_service import set_replay_store
      shutdown_all_coordinators(timeout=5.0)
      reset_default_capture_sink()
      set_replay_store(None)
  ```
- [ ] **Verify:** Both modules' existing tests still pass with the fixture in place.

**Notes:**

### Task 1.4: Confirm no regressions [Simple]
**Tests:** focused: `pytest tests/integration/replay/test_replay_store.py tests/unit/test_app_bootstrap_invariants.py tests/unit/test_app_bootstrap_profiling.py -v`

- [ ] Run the focused test files. All green.
- [ ] **Verify:** zero regressions.

**Notes:**

### Task 1.5: Update `Current State` in plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 1 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** 2
  - **Last Action:** Phase 1 complete; sink + store registered in bootstrap; autouse cleanup added to bootstrap test modules.
  - **Next Action:** Phase 2 — coordinator construction + start + run-loop shutdown + Combat Lab fallback.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Run `python Tools/test_sharded/test_sharded.py` — confirm 18287+ baseline (any new tests count up)
