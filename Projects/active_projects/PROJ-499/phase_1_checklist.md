# Phase 1: Strict-TDD failing test for symmetric comparator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write the failing test that pins symmetric `compare_snapshots()` behavior. Per AGENTS.md Strict TDD, no implementation in this phase.

---

## Tasks

### Task 1.1: Add comparator-strictness test file [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py` (NEW)
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py -v`

- [ ] Create the new test file at the path above.
- [ ] Add `test_extra_top_level_key_in_actual_is_reported`: pass `actual={"a": 1, "b": 2}, expected={"a": 1}`, assert returned diff list contains a message describing the extra `b` key.
- [ ] Add `test_extra_nested_dict_key_in_actual_is_reported`: simulate the real shape — `actual={"component": {"stats": {"mass_mult": 1.0, "launch_rate_mult": 1.0}}}, expected={"component": {"stats": {"mass_mult": 1.0}}}`. Assert the diff reports the extra `launch_rate_mult`.
- [ ] Add `test_extra_key_in_abilities_list_element_is_reported`: nested list case — `actual={"abilities": [{"damage": 1, "new_field": 2}]}, expected={"abilities": [{"damage": 1}]}`. Assert the diff reports the extra `new_field`.
- [ ] Run the new test file — confirm ALL three tests FAIL against the current asymmetric `compare_snapshots()`. Capture the failure output in the task notes.
- [ ] Do NOT edit `conftest.py` in this phase.

**Notes:** [Filled during execution — must include the failure output proving the tests fail under the current comparator]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 3 new tests exist and ALL FAIL on current `compare_snapshots()`
- [ ] Failure output captured in notes (proof of RED state)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
