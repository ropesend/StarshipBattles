# Phase 2: Coordinator + start + run-loop shutdown + Combat Lab fallback adapter

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Construct and start the `ReplayVerificationCoordinator` in `bootstrap()`; expose both store and coordinator on `BootstrapResult`; wire `shutdown_all_coordinators(timeout=5.0)` into `RunLoop.run()` immediately after `shutdown_all_calls(timeout=5.0)` and before `pygame.quit()`. Build the Combat Lab fallback adapter (`DesignOnlyMaterializer` wrapper) at coordinator construction time. Phase 1 must be complete before this phase starts.

See `plan.md` Phase 2 for context. r001 deltas: Combat Lab fallback hoisted from Phase 4, source-module monkeypatch targets in tests, shared `replay_settings` instance.

---

## Tasks

### Task 2.1: Failing-test-first — pin coordinator presence + listener registration [Medium]
**File:** `tests/unit/test_app_bootstrap_invariants.py` (modify)
**Tests:** `pytest tests/unit/test_app_bootstrap_invariants.py -v`

- [ ] Add `test_invariant_8_replay_verification_coordinator_started`: run `bootstrap()`; assert the returned `BootstrapResult` has `replay_store` and `replay_verification_coordinator` attributes; assert `replay_verification_coordinator._worker is not None` (worker thread spawned); assert `replay_verification_coordinator._listener_registered is True`. The autouse cleanup fixture from Phase 1 handles teardown.
- [ ] Run the test. **Expect failure** (no fields on `BootstrapResult` yet).

**Notes:**

### Task 2.2: Extend `BootstrapResult` with two new fields [Simple]
**File:** `game/app_bootstrap.py`
**Tests:** Task 2.1; existing bootstrap tests

- [ ] Update the `BootstrapResult` dataclass (around lines 73-90) to add (alongside the existing fields):
  ```python
  replay_store: "ReplayStore"
  replay_verification_coordinator: "ReplayVerificationCoordinator"
  ```
  Use forward-string types so module-level imports stay minimal. Add a `TYPE_CHECKING` block for the typing-only imports.
- [ ] **Verify:** existing bootstrap tests still pass (constructor signature widened, not narrowed).

**Notes:**

### Task 2.3: Construct + start coordinator with Combat Lab fallback adapter [Medium]
**File:** `game/app_bootstrap.py`
**Tests:** Task 2.1 should now pass.

- [ ] Add lazy imports inside `bootstrap()` body (after Phase 1's imports):
  - `from game.strategy.services.replay_verification_coordinator import ReplayVerificationCoordinator`
  - `from game.ai.ai_factory import AIControllerFactory`
  - `from combat_lab.design_loader import load_combat_lab_design`
  - `from game.simulation.services.ship_materializer import DesignOnlyMaterializer`
- [ ] AFTER the Phase 1 `replay.construct_store` block, add the Combat Lab fallback adapter and coordinator construction. The fallback adapter wraps `DesignOnlyMaterializer` so the callable signature is `(ShipSpec, int) -> Ship` (the coordinator's expected `fallback_ship_builder` shape):
  ```python
  with _timed_phase("replay.start_coordinator", ctx.profiler):
      _cl_materializer = DesignOnlyMaterializer(design_loader=load_combat_lab_design)

      def _replay_combat_lab_fallback(ship_spec, team_id):
          return _cl_materializer.materialize(ship_spec, team_id, registries)

      replay_verification_coordinator = ReplayVerificationCoordinator(
          replay_store=replay_store,
          ai_factory=AIControllerFactory(),
          registry_provider=provider,  # local from earlier in bootstrap()
          settings=replay_settings,    # SAME instance shared with the store
          fallback_ship_builder=_replay_combat_lab_fallback,
      )
      replay_verification_coordinator.start()
  ```
  Reuses the `registries` local already constructed earlier in `bootstrap()` (no new `GameRegistries(...)` build).
- [ ] Update the `return BootstrapResult(...)` call at the end to include `replay_store=replay_store, replay_verification_coordinator=replay_verification_coordinator`.
- [ ] **Verify:** Task 2.1's invariant test passes; bootstrap launches cleanly under the existing pygame test harness.

**Notes:**

### Task 2.4: Failing-test-first — run-loop shutdown call ordering [Simple]
**File:** `tests/unit/test_run_loop_shutdown_ordering.py` (NEW)
**Tests:** Same file

- [ ] Create the file. Patch SOURCE modules (NOT `game.run_loop` lazy-import sites):
  - `game.services.llm.background.shutdown_all_calls`
  - `game.strategy.services.replay_verification_coordinator.shutdown_all_coordinators`
- [ ] Test name: `test_shutdown_order_llm_then_coordinator_then_pygame`. Construct a `RunLoop` with `running=False` so `run()` exits immediately after the loop body never executes; record call order; assert `shutdown_all_calls` happened BEFORE `shutdown_all_coordinators` BEFORE `pygame.quit()`.
- [ ] Run the test. **Expect failure** (`shutdown_all_coordinators` not called yet).

**Notes:**

### Task 2.5: Wire `shutdown_all_coordinators` into `RunLoop.run()` [Simple]
**File:** `game/run_loop.py`
**Tests:** Task 2.4 should now pass.

- [ ] In `RunLoop.run()` after the existing `shutdown_all_calls(timeout=5.0)` (around line 85), add:
  ```python
  from game.strategy.services.replay_verification_coordinator import shutdown_all_coordinators
  shutdown_all_coordinators(timeout=5.0)
  ```
  (Lazy import keeps the file's existing import shape; PROJ-296 used the same pattern for `shutdown_all_calls`.)
- [ ] **Verify:** Task 2.4 passes; `pygame.quit()` is the last call.

**Notes:**

### Task 2.6: Update `Current State` in plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 2 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** 3
  - **Last Action:** Phase 2 complete; coordinator constructed + started in bootstrap with Combat Lab fallback; shutdown wired in run loop.
  - **Next Action:** Phase 3 — integration tests.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
- [ ] Run `python Tools/test_sharded/test_sharded.py` — confirm baseline + new tests
