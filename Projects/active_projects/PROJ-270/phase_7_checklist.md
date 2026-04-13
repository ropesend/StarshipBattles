# Phase 7: Test Coverage Backfill

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial (7.1 + 7.2 + 7.4 done; 7.3/7.5 remain for future session)
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

### Task 7.3: Rewrite visual-mode UI fixture with real spec [Medium]
**File:** `tests/fixtures/test_scenarios.py`
**Tests:** `pytest tests/unit/test_lab/ tests/unit/combat_lab/services/ --testmon`

- [ ] Audit [tests/fixtures/test_scenarios.py:152-159](../../../tests/fixtures/test_scenarios.py#L152-L159) — the `create_mock_test_scenario` helper uses `empty_spec.teams = ()` as a short-circuit
- [ ] Create a new fixture (or extend the existing one) `create_realistic_test_scenario` that returns a scenario whose `to_spec()` produces a spec with:
  - 1 team with 1 task_force containing 1 squadron containing 1 `ShipSpec` (minimal non-empty)
  - Real `boundary` (e.g., `UnboundedRegion`)
  - Real `modifier_stack` (empty but valid)
  - Real end_condition
- [ ] Update tests that use `create_mock_test_scenario` for the visual path (not the ones that want the short-circuit for other reasons) to use the realistic fixture
- [ ] Specifically target [tests/unit/test_lab/test_visual_run.py](../../../tests/unit/test_lab/test_visual_run.py) and [tests/unit/test_lab/test_batch_skip.py](../../../tests/unit/test_lab/test_batch_skip.py) — ensure they now exercise `materialize_spec_ships` with non-empty data
- [ ] Run affected suites — green
- [ ] Verify: pytest --cov report shows `materialize_spec_ships` coverage is non-trivial (was ~0 before)

**Notes:** [Filled during implementation]

---

### Task 7.4: Remove stale `update_from_battle_results = MagicMock()` assignments [Simple] — COMPLETE
**File:** `tests/unit/strategy/test_engine_event_emission.py`, `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`

- [x] Removed **6 stale assignments** from `test_engine_event_emission.py` (lines 611, 618, 651, 658, 724, 731)
- [x] Removed **8 stale assignments** from `test_battle_resolver_integration.py` (lines 75, 82, 145, 150, 230, 237, 271, 278)
- [x] Run `pytest tests/unit/strategy/test_engine_event_emission.py tests/unit/strategy/conflict_resolution/` — 62/62 green

**Notes:** These were no-op setter assignments on Mock objects that outlived `FleetBattleAdapter.update_from_battle_results`. Deletion is cosmetic cleanup.

---

### Task 7.5: Rewrite stubbed test files that still have value [Medium — conditional]
**File:** `tests/unit/simulation/test_battle_config.py`, `tests/unit/simulation/test_battle_state.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

Some of the 7 stubbed test files PROJ-269 left behind may be genuinely useful to re-fill with current-surface tests (instead of just deleting them in Phase 8):

- [ ] `test_battle_config.py` — write tests for the Phase-5-trimmed `BattleConfig` surface (only operational fields)
- [ ] `test_battle_state.py` — covered elsewhere; likely just delete in Phase 8
- [ ] Others (`test_battle_mode_handlers.py`, `test_battle_factories.py`, etc.) — no current surface to test; delete in Phase 8
- [ ] For each file kept: write real tests; remove the deprecation docstring
- [ ] For each file deleted: leave in place until Phase 8.1

**Notes:** [Filled during implementation]

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
