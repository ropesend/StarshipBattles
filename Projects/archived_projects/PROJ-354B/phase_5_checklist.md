# Phase 5: Composition root wiring + integration tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire coordinator into production startup; integrate with shutdown sequence; add end-to-end integration tests; add headless-vs-visual equivalence test.

> **PREREQUISITE BLOCKER:** Tasks 5.1 and 5.2 require the production sink wiring (`set_default_capture_sink(...)` + `set_replay_store(...)` in `app_bootstrap.py` near line 157-159) to have landed. The user is handling that separately. Tasks 5.3, 5.4, 5.5 can run with manually-wired test fixtures.

See `plan.md` Phase 5 for full task details.

---

## Tasks

### Task 5.1: Wire coordinator into `app_bootstrap.py` [Medium]
**File:** `game/app_bootstrap.py`
**Tests:** Manual smoke + Phase 5.3 integration test

**BLOCKED until production sink wiring lands.**

- [ ] At appropriate location near `ApplicationContext.create_production()` (lines 157-159), AFTER prerequisite sink-wiring lines:
  - Construct `ReplayStore(...)` if not already done by prerequisite
  - Construct `ReplayVerificationCoordinator(replay_store=..., ai_factory=ctx.ai_factory_or_equivalent, registry_provider=ctx.registry_manager, settings=load_replay_settings(), fallback_ship_builder=...)`
  - Call `coordinator.start()`
  - Hold a reference somewhere persistent (alongside the store)
- [ ] Verify: game starts without errors; coordinator's worker thread is running

**Notes:**

### Task 5.2: Wire shutdown into `run_loop.py` [Simple]
**File:** `game/run_loop.py` (lines 84-85)
**Tests:** Manual smoke; verify clean shutdown

- [ ] Add `shutdown_all_coordinators(timeout=5.0)` call alongside existing `shutdown_all_calls(timeout=5.0)`, BEFORE `pygame.quit()`. Order matters.
- [ ] Verify: no thread-still-alive warnings on shutdown

**Notes:**

### Task 5.3: Integration test — live battle → verification queue → sidecar [Complex]
**File:** `tests/integration/replay/test_verification_queue_integration.py` (NEW)

- [ ] Set up `ReplayStore` + capture sink + coordinator with real AI factory and registry provider
- [ ] Run small deterministic battle via `run_battle`
- [ ] Wait for coordinator (use new `coordinator.wait_for_idle(timeout)` helper OR poll for sidecar with bounded timeout)
- [ ] Assert sidecar exists with `status=PASSED`
- [ ] Assert toggle case: `verification_enabled=False` → sidecar exists with `status=SKIPPED_DISABLED`
- [ ] Verify: both paths green

**Notes:**

### Task 5.4: Headless-vs-visual equivalence test [Medium]
**File:** `tests/integration/replay/test_headless_visual_equivalence.py` (NEW)

- [ ] Build replay record from a known battle
- [ ] Run via `run_replay_headless(...)` → outcome A
- [ ] Run via `BattleController.start_from_spec(replay_record_to_spec(record), config=BattleConfig(replay_mode=True, ...), ai_factory=..., ship_builder=the_same_production_replay_builder, registry_provider=...)`. Drive controller through `update()` until `is_battle_over()`. Get outcome B from `controller.get_outcome()`.
- [ ] Assert `battle_outcome_to_dict(A) == battle_outcome_to_dict(B)`
- [ ] Boundary is `BattleController`, NOT `BattleScreen` (no Pygame UI dependency)
- [ ] Verify: passes

**Notes:**

### Task 5.5: Production materializer test [Medium]
**File:** `tests/integration/replay/test_verification_uses_production_materializer.py` (NEW)

- [ ] Coordinator wired with `build_replay_ship_builder` (production), NOT hand-built test builder
- [ ] Run battle producing record with non-empty `instance_snapshot` blobs
- [ ] Trigger verification
- [ ] Assert `build_replay_ship_builder` was used (spy/mock) AND verification passes
- [ ] Verify: green

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
