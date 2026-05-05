# Phase 1: Characterization tests (TDD baseline)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-362 1`
> 2. Only proceed if PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Land 5 characterization tests in `_aggregate` so Phase 2-3 refactors are protected by green baseline. Tests should pass *against the current code* (this is characterization, not red-then-green).

---

## Tasks

### Task 1.1: Create characterization test file [Simple]
**File:** `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py -v` — must PASS against current code (this is the baseline).

- [ ] Module docstring referencing PROJ-362 Phase 1 and review finding #2.
- [ ] Reuse existing fixtures from `test_system_effects_collector.py`: `_make_facility`, `_make_planet`, `_make_system`, `_stabilizer_design`, `_harvest_booster_design`.

**Notes:** _(filled during implementation)_

### Task 1.2: get_abilities() exception path [Simple]
**File:** Same as 1.1
**Tests:** Per-test pytest

- [ ] `test_get_abilities_exception_skips_source_and_logs`:
  - Build a fake source whose `get_abilities()` raises `RuntimeError("simulated")`.
  - Call `_aggregate([fake, normal_source], ...)`.
  - Assert: exception is caught, warning is logged (use `caplog`), normal_source contributions appear in result, fake contributes nothing.

**Notes:** _(filled during implementation)_

### Task 1.3: affects_hex exception path [Simple]
**File:** Same as 1.1

- [ ] `test_affects_hex_exception_skips_source_and_logs`:
  - Fake source with `affects_hex(coord)` raising. Call `_aggregate(..., hex_coord=some_hex)`.
  - Assert exception caught, warning logged, source skipped.

**Notes:** _(filled during implementation)_

### Task 1.4: DEACTIVATING activation phase [Simple]
**File:** Same as 1.1

- [ ] `test_deactivating_ability_shows_progress_remaining`:
  - Construct a facility with one activatable ability whose activation_state is in `DEACTIVATING` phase with `progress_ticks=2, required_ticks=5`.
  - Assert provider `status == "Deactivating (3)"` and `is_active is False`.

**Notes:** _(filled during implementation)_

### Task 1.5: Mixed activation-state precedence [Medium]
**File:** Same as 1.1

- [ ] `test_any_active_overrides_activating_and_deactivating`:
  - Group with three providers: one ACTIVE, one ACTIVATING, one DEACTIVATING.
  - Assert aggregate `status == "Active"` and value uses only the ACTIVE provider's contribution.
- [ ] `test_activating_when_no_active_uses_first_activating_status`:
  - Group with two ACTIVATING (different progress) and one INACTIVE.
  - Assert aggregate uses the first ACTIVATING provider's status string (i.e. "Activating (X)").
- [ ] `test_deactivating_when_no_active_or_activating`:
  - Group with one DEACTIVATING and one INACTIVE.
  - Assert aggregate `status == "Deactivating"`.

**Notes:** _(filled during implementation)_

### Task 1.6: Owned source filtered by empire_id mismatch [Simple]
**File:** Same as 1.1

- [ ] `test_owned_source_skipped_when_empire_id_mismatches_query`:
  - Source with `owner_id=2`. Query with `empire_id=1`.
  - Assert source contributes nothing to the result.
- [ ] `test_ownerless_source_contributes_to_any_empire_query`:
  - Source with `owner_id=None`. Query with `empire_id=1` and `empire_id=2`.
  - Assert source contributes to both.

**Notes:** _(filled during implementation)_

### Task 1.7: improvement_rate field fallback [Simple]
**File:** Same as 1.1

- [ ] `test_improvement_rate_field_used_when_rate_and_multiplier_missing`:
  - Source with ability data lacking `rate` and `multiplier` but containing `improvement_rate=0.15` (legacy schema).
  - Assert value is read from `improvement_rate`.

**Notes:** _(filled during implementation)_

### Task 1.8: Run all characterization tests against current code [Simple]
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py -v`

- [ ] All tests pass against the current pre-refactor code.
- [ ] If a test fails, do NOT change production code in this phase — instead, the test was wrong (current behavior is the spec). Adjust the test to reflect actual behavior, document the deviation in the test docstring as "characterization of existing behavior", and update decisions.md.
- [ ] Verify count: 9 tests added, all green.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] 9 new tests, all green against current code
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State to point to Phase 2
