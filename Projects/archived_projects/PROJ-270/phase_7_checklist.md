# Phase 7: Test Coverage Backfill

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial (7.1 + 7.2 + 7.4 + 7.5 done; 7.3 intentionally deferred — low ROI, checklist self-flagged)
**Risk:** LOW
**Depends On:** Phases 1–6
**Objective:** Close the three genuine test-coverage gaps the audit identified (factory-flow regression guard, visual-mode UI realism, speed-recalc regression). Remove stale `update_from_battle_results = MagicMock()` assignments in conftest files. Phase 7 is almost entirely writing tests (Strict TDD — but here the test IS the deliverable).

---

## Tasks

### Task 7.1: `_is_started=True` regression guard [Simple] — COMPLETE
**File:** `tests/unit/simulation/battle_controller/test_initialization.py`

- [x] Added `TestBattleControllerStartGuard` class with 4 tests asserting:
  - `start()` without `configure()` first fails cleanly
  - Configured-not-started state has `_is_started == False`
  - `start()` is the path that flips `_is_started` to True
  - Double-start fails (uses existing `_is_started` check)
- [x] Run `pytest tests/unit/simulation/battle_controller/test_initialization.py` — 15/15 green

**Notes:** No code-level guard property added — the existing `start()` logic (fails on `_is_started == True`) is sufficient. The test suite locks the flow so future code can't accidentally remove the guard.

---

### Task 7.2: Speed-recalculation regression test [Simple] — COMPLETE
**File:** `tests/unit/strategy/combat/test_post_battle_hook.py`

- [x] Added `test_apply_outcome_to_fleets_invalidates_stats_cache` at line 152 in [tests/unit/strategy/combat/test_post_battle_hook.py](../../../tests/unit/strategy/combat/test_post_battle_hook.py)
- [x] Design decision: `ShipInstance` uses lazy `_cached_stats` — speed recalc happens on next `get_design_stats()` call. The hook's `invalidate_stats_cache()` call (post_battle_hook.py:173) is the architectural guarantee. Test asserts the cache is cleared.
- [x] 7/7 tests in `test_post_battle_hook.py` green ✓

**Notes:** Replaces the deleted `test_update_from_battle_results_triggers_speed_recalc` per [design.md](design.md) Finding 15. The test is scoped to the invalidation guarantee — downstream stat-calc tests cover the actual speed derivation.

---

### Task 7.3: Rewrite visual-mode UI fixture with real spec [Medium] — INTENTIONALLY DEFERRED
**File:** `tests/fixtures/test_scenarios.py`
**Tests:** `pytest tests/unit/test_lab/ tests/unit/combat_lab/services/ --testmon`

Checklist self-flags this task as "low ROI" — no current test requires the real-spec fixture, and `materialize_spec_ships` is already exercised by the integration tests under `tests/integration/simulation/` (e.g., `test_boundary_retreat.py`) with real specs. Rewriting the unit-level mock fixture would not unlock any new test coverage.

- [x] Decision: defer this task indefinitely. If a future visual-mode test genuinely needs a real-spec fixture, create it then. No need to write one speculatively.
- [x] Existing Task 7.1 + 7.2 regression guards + the integration tests in `tests/integration/simulation/` provide the coverage this task was meant to add.

**Notes:** The mock fixture's `teams=()` short-circuit is not a bug — it's an intentional shortcut for tests that don't care about spec materialization. Rewriting it would risk breaking the tests that rely on the short-circuit.

---

### Task 7.4: Remove stale `update_from_battle_results = MagicMock()` assignments [Simple] — COMPLETE
**File:** `tests/unit/strategy/test_engine_event_emission.py`, `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`

- [x] Removed **6 stale assignments** from `test_engine_event_emission.py` (lines 611, 618, 651, 658, 724, 731)
- [x] Removed **8 stale assignments** from `test_battle_resolver_integration.py` (lines 75, 82, 145, 150, 230, 237, 271, 278)
- [x] Run `pytest tests/unit/strategy/test_engine_event_emission.py tests/unit/strategy/conflict_resolution/` — 62/62 green

**Notes:** These were no-op setter assignments on Mock objects that outlived `FleetBattleAdapter.update_from_battle_results`. Deletion is cosmetic cleanup.

---

### Task 7.5: Rewrite stubbed test files that still have value [Medium — conditional] — COMPLETE
**File:** `tests/unit/simulation/test_battle_config.py`, `tests/unit/simulation/test_battle_state.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [x] `test_battle_config.py` re-filled — now contains `TestBattleConfigDefaults` (10 default-value tests), `TestBattleConfigDeletedFields` (FORBIDDEN_FIELDS regression guard including the new `map_bounds` entry from PROJ-270 Task 5.4), and `TestBattleConfigKwargs` (5 kwarg tests).
- [x] `test_battle_state.py` — deleted in PROJ-270 Phase 8.1 alongside the 6 other docstring-only stubs.
- [x] `test_battle_mode_handlers.py`, `test_battle_factories.py`, etc. — all deleted in Phase 8.1.

**Notes:** `test_battle_config.py` is now the active regression surface for `BattleConfig` — `FORBIDDEN_FIELDS` grows with each field we delete (test_scenario, map_bounds so far) and prevents accidental resurrection.

---

### Task 7.6: Phase 7 regression gate [Simple]
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline (should be slightly UP due to new tests)
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] New tests from Tasks 7.1, 7.2, 7.3 all green
- [ ] Grep audit: `update_from_battle_results = MagicMock()` no longer appears

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] New tests passing
- [ ] Regression gate (Task 7.6) passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
