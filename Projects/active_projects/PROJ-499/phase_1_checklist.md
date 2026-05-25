# Phase 1: Strict-TDD failing test for symmetric comparator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Write the failing test that pins symmetric `compare_snapshots()` behavior. Per AGENTS.md Strict TDD, no implementation in this phase.

---

## Tasks

### Task 1.1: Add comparator-strictness test file [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py` (NEW)
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py -v`

- [x] Create the new test file at the path above.
- [x] Add `test_extra_top_level_key_in_actual_is_reported`: pass `actual={"a": 1, "b": 2}, expected={"a": 1}`, assert returned diff list contains a message describing the extra `b` key.
- [x] Add `test_extra_nested_dict_key_in_actual_is_reported`: simulate the real shape — `actual={"component": {"stats": {"mass_mult": 1.0, "launch_rate_mult": 1.0}}}, expected={"component": {"stats": {"mass_mult": 1.0}}}`. Assert the diff reports the extra `launch_rate_mult`.
- [x] Add `test_extra_key_in_abilities_list_element_is_reported`: nested list case — `actual={"abilities": [{"damage": 1, "new_field": 2}]}, expected={"abilities": [{"damage": 1}]}`. Assert the diff reports the extra `new_field`.
- [x] Run the new test file — confirm ALL three tests FAIL against the current asymmetric `compare_snapshots()`. Capture the failure output in the task notes.
- [x] Do NOT edit `conftest.py` in this phase.

**Notes:**
- All 3 tests FAIL on current asymmetric comparator (RED state, as required by strict TDD):
  - `test_extra_top_level_key_in_actual_is_reported` -> `assert []` (no diffs returned for extra `b`)
  - `test_extra_nested_dict_key_in_actual_is_reported` -> `assert []` (no diffs returned for extra `launch_rate_mult`)
  - `test_extra_key_in_abilities_list_element_is_reported` -> `assert []` (no diffs returned for extra `new_field`)
- 3 failed in 1.81s (pytest -v).
- No conftest.py edits in this phase — Phase 2 owns the comparator change.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] 3 new tests exist and ALL FAIL on current `compare_snapshots()`
- [x] Failure output captured in notes (proof of RED state)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
