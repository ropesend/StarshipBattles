# Phase 7: Test Coverage Backfill

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW
**Depends On:** Phases 1–6
**Objective:** Close the three genuine test-coverage gaps the audit identified (factory-flow regression guard, visual-mode UI realism, speed-recalc regression). Remove stale `update_from_battle_results = MagicMock()` assignments in conftest files. Phase 7 is almost entirely writing tests (Strict TDD — but here the test IS the deliverable).

---

## Tasks

### Task 7.1: `_is_started=True` regression guard [Simple]
**File:** `tests/unit/simulation/battle_controller/test_initialization.py` (modify)
**Tests:** `pytest tests/unit/simulation/battle_controller/test_initialization.py --tb=short`

- [ ] Write a new test in [tests/unit/simulation/battle_controller/test_initialization.py](../../../tests/unit/simulation/battle_controller/test_initialization.py) asserting:
  - Creating a `BattleController` and setting `controller._is_started = True` externally (without calling `configure` + `start`) raises or otherwise prevents the controller from reaching a valid started state
  - Alternative form: assert that `controller.start()` is the ONLY method that flips `_is_started` to True — grep-style test that checks no public method has that side effect
- [ ] Implement the guard if Phase 4 didn't already add one (e.g., make `_is_started` a property with a guarded setter, or add an assertion in `controller.update()`)
- [ ] Run test — passes
- [ ] Verify: grep audit shows no external `_is_started = True` assignments in production code (Phase 1 + Phase 4 should have already deleted them)

**Notes:** [Filled during implementation]

---

### Task 7.2: Speed-recalculation regression test [Simple]
**File:** `tests/unit/strategy/combat/test_post_battle_hook.py` (modify)
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py --tb=short`

- [ ] Audit existing [tests/unit/strategy/combat/test_post_battle_hook.py](../../../tests/unit/strategy/combat/test_post_battle_hook.py) — confirm no existing test asserts speed recalculation after damage application
- [ ] Write a new test: `test_apply_outcome_to_fleets_recalculates_speed`
  - Given: a fleet with a ship at full HP
  - When: a `BattleOutcome` is applied where the ship's engine component took damage (reducing effective thrust)
  - Then: `ship_instance.speed` (or equivalent) reflects the recalculated value (lower than before damage)
- [ ] Run test — if it fails, either (a) `apply_outcome_to_fleets` isn't triggering speed recalc (bug) → fix the code; (b) speed recalc happens lazily via a stat calculator → update the test to read the recalculated value correctly
- [ ] Test passes
- [ ] Run `pytest tests/unit/strategy/` --testmon — baseline maintained

**Notes:** This test replaces the deleted `test_update_from_battle_results_triggers_speed_recalc` per [design.md](design.md) Finding 15.

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

### Task 7.4: Remove stale `update_from_battle_results = MagicMock()` assignments [Simple]
**File:** `tests/unit/strategy/conflict_resolution/conftest.py`, `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/ --testmon`

- [ ] Grep for the pattern:
  ```bash
  grep -rn "update_from_battle_results\s*=\s*MagicMock" --include="*.py" tests/
  ```
- [ ] For each hit: delete the assignment (it's a no-op on a Mock object after PROJ-269 removed the method)
- [ ] Run affected suites — baseline maintained

**Notes:** [Filled during implementation]

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
