# Phase 3: Integration tests (live battle → sidecar; headless-vs-visual; production materializer; no-recursion)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** End-to-end coverage proves the wired-up production composition produces correct sidecars; an equivalence test pins headless and `BattleController.start_from_spec` outcomes; a materializer test proves the production builder is the path the coordinator uses; a no-recursion assertion pins the guarantee through the wired caller. Phase 2 must be complete before this phase starts.

See `plan.md` Phase 3 for context. r001 deltas: drive production `ship_instance_lookup` snapshots (not no-snapshot path); use `wait_for_idle()` BEFORE file-existence checks; SOURCE-module monkeypatch for the materializer spy; per-PROJ-366 no-recursion assertion.

---

## Tasks

### Task 3.1: Integration test — live battle → verification queue → sidecar [Complex]
**File:** `tests/integration/replay/test_verification_queue_integration.py` (NEW)
**Tests:** Same file

- [ ] Create the file. Setup:
  - `tmp_path` for the save dir (use pytest's `tmp_path` fixture).
  - Construct `ReplayStore(settings=...)` and call `store.set_save_root(tmp_path / "save")`.
  - `set_default_capture_sink(store)` and `set_replay_store(store)`. Cleanup via `addfinalizer` or `try/finally`: `reset_default_capture_sink()`; `set_replay_store(None)`.
  - Construct `ReplayVerificationCoordinator(replay_store=store, ai_factory=AIControllerFactory(), registry_provider=provider, settings=settings, fallback_ship_builder=...)`.
  - `coordinator.start()`. Cleanup: `coordinator.shutdown(timeout=5.0)`.
- [ ] **Pass case:** drive the strategy adapter at `game/strategy/adapters/simulation_adapter.py:426-445` so the `ReplayCaptureContext` is built with a real `ship_instance_lookup` (production materializer path — `ShipInstanceSerializer.to_dict` against pre-built `ShipInstance` objects). DO NOT copy-paste from `tests/integration/replay/test_replay_playback.py:99-106` (that omits `ship_instance_lookup`, validating the fallback path). Run a small deterministic battle. Use `coordinator.wait_for_idle(timeout=30)` THEN poll for `Path(tmp_path / "save" / "replays" / f"replay_{replay_id}.verification.json").exists()` up to 30s. Assert sidecar exists; load and assert `status=="PASSED"`.
- [ ] **Skip case:** rebuild coordinator with `settings=ReplaySettings(verification_enabled=False, ...)`. Run battle. Wait for sidecar. Assert `status=="SKIPPED_DISABLED"`.
- [ ] **No-recursion assertion (per-PROJ-366):** after `coordinator.wait_for_idle()` returns in the PASSED case, assert `len(store.list()) == 1` — the verification headless replay must NOT have produced a second record.
- [ ] **Verify:** all paths green.

**Notes:**

### Task 3.2: Headless-vs-visual equivalence test [Medium]
**File:** `tests/integration/replay/test_headless_visual_equivalence.py` (NEW)
**Tests:** Same file

- [ ] Setup: build a deterministic battle via `run_battle`; capture replay record; obtain `replay_record_to_spec(record)`.
- [ ] Path A: `outcome_a = run_replay_headless(record, ai_factory=AIControllerFactory(), ship_builder=builder, registry_provider=provider)`.
- [ ] Path B: `controller = BattleController(ai_factory=AIControllerFactory()); controller.start_from_spec(replay_record_to_spec(record), config=BattleConfig(replay_mode=True), ship_builder=the_same_builder, registry_provider=provider)`. Drive with `controller.update(0.016)` until `controller.is_battle_over()`. `outcome_b = controller.get_outcome()`.
- [ ] Assert: `battle_outcome_to_dict(outcome_a) == battle_outcome_to_dict(outcome_b)`.
- [ ] Boundary: `BattleController` only — no `BattleScreen`, no Pygame UI dependency.
- [ ] **Verify:** Test passes.

**Notes:**

### Task 3.3: Production materializer test [Medium]
**File:** `tests/integration/replay/test_verification_uses_production_materializer.py` (NEW)
**Tests:** Same file

- [ ] Setup as in Task 3.1 BUT spy on `build_replay_ship_builder` via SOURCE-module monkeypatch: replace `game.strategy.services.replay_verification_coordinator.build_replay_ship_builder` (NOT a local-import shadow) with a wrapper that increments a counter then delegates to the real function.
- [ ] Run a small deterministic battle; `coordinator.wait_for_idle(timeout=30)`; check sidecar.
- [ ] Assert: spy counter ≥ 1 (the coordinator used the production materializer); sidecar `status=="PASSED"`.
- [ ] **Verify:** Test passes.

**Notes:**

### Task 3.4: Run focused tests [Simple]
**Tests:** `pytest tests/integration/replay/test_verification_queue_integration.py tests/integration/replay/test_headless_visual_equivalence.py tests/integration/replay/test_verification_uses_production_materializer.py -v`

- [ ] All three new tests green.

**Notes:**

### Task 3.5: Update `Current State` in plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 3 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** 4
  - **Last Action:** Phase 3 complete; integration tests for live-battle sidecar (with no-recursion assertion), headless-vs-visual equivalence, and production materializer all green.
  - **Next Action:** Phase 4 — Combat Lab fallback test + docs + verifier-import lint.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
- [ ] Run `python Tools/test_sharded/test_sharded.py` — confirm baseline + new tests
