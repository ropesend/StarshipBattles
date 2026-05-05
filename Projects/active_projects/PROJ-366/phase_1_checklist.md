# Phase 1: Sink wiring + ReplayStore construction in bootstrap

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Construct `ReplayStore` in `bootstrap()`; register it as the production capture sink and the production save-lifecycle store. Existing `SaveGameService._notify_replay_store_*` hooks now route to a real store. Add bootstrap-invariant tests pinning the registration order.

See `plan.md` Phase 1 for context.

---

## Tasks

### Task 1.1: Failing-test-first — pin sink + store registration in bootstrap [Simple]
**File:** `tests/unit/test_app_bootstrap_invariants.py` (modify)
**Tests:** `pytest tests/unit/test_app_bootstrap_invariants.py -v`

- [ ] Read the existing module to understand the invariant-test style.
- [ ] Add `test_invariant_7_replay_store_registered_after_application_context`: monkeypatch `set_default_capture_sink` and `set_replay_store` to record call order; run `bootstrap()` (or its public test entry, with the existing pygame headless harness); assert both were called exactly once AFTER `ApplicationContext.create_production()` and BEFORE the function returns.
- [ ] Run the test. **Expect failure** (the production code does not call them yet).
- [ ] Update phase checklist note.

**Notes:**

### Task 1.2: Construct `ReplayStore` in `bootstrap()` [Simple]
**File:** `game/app_bootstrap.py`
**Tests:** Task 1.1 should now pass.

- [ ] Add lazy imports at the top of `bootstrap()`'s body (NOT module-level — match the existing late-import pattern):
  - `from game.simulation.replay.replay_capture import set_default_capture_sink`
  - `from game.strategy.systems.save_game_service import set_replay_store`
  - `from game.strategy.services.replay_store import ReplayStore`
- [ ] After `InputMapper.load(...)` (around line 260) and BEFORE the `dt_total` summary log, add:
  ```python
  with _timed_phase("replay.construct_store", ctx.profiler):
      replay_store = ReplayStore()
      set_default_capture_sink(replay_store)
      set_replay_store(replay_store)
  ```
- [ ] **Verify:** Task 1.1's invariant test passes.

**Notes:**

### Task 1.3: Confirm `ReplayStore`'s default constructor doesn't raise on a clean checkout [Simple]
**Tests:** focused: `pytest tests/integration/replay/test_replay_store.py -v` (existing); `pytest tests/unit/test_app_bootstrap_invariants.py -v` (modified)

- [ ] Run the focused test files. Both should be green.
- [ ] Run any existing tests that monkeypatch `set_default_capture_sink` or `set_replay_store` — confirm they still pass. The production wiring is additive; tests that override the sink should continue to do so successfully because they call the setters AFTER bootstrap.
- [ ] **Verify:** zero regressions.

**Notes:**

### Task 1.4: Update `Current State` in plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 1 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** 2
  - **Last Action:** Phase 1 complete; sink + store registered in bootstrap; invariant tests added.
  - **Next Action:** Phase 2 — coordinator construction + start + run-loop shutdown.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Run `python Tools/test_sharded/test_sharded.py` — confirm 17797+ baseline (any new tests count up)
