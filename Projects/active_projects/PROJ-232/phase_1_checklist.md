# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-232 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing edge case tests before any code changes to ensure a safety net for refactoring.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add Empty Ship List Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_empty_list_returns_empty -v`

- [ ] Add test `test_filter_empty_list_returns_empty` to `TestFilterShips` class
- [ ] Test case 1: `assert filter_ships([], {}) == []`
- [ ] Test case 2: `assert filter_ships([], {'show_damaged': False}) == []`
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.2: Add Status Hierarchy Test [Medium] (CRITICAL)
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_derelict_not_matched_as_damaged -v`

- [ ] Add test `test_derelict_not_matched_as_damaged` to `TestFilterShips` class
- [ ] Create a derelict ship mock (`is_derelict=True`, `is_damaged()=True`, `is_alive=True`)
- [ ] Test: With `show_derelict=True, show_damaged=False`, derelict ship SHOULD be included
- [ ] Test: With `show_derelict=False, show_damaged=True`, derelict ship should NOT be included
- [ ] This verifies the hierarchy: derelict is checked BEFORE damaged
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.3: Add Cargo None Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo::test_filter_cargo_contents_none_treated_as_no_cargo -v`

- [ ] Add test `test_filter_cargo_contents_none_treated_as_no_cargo` to `TestFilterShipsCargo` class
- [ ] Create ship mock with `cargo_contents = None`
- [ ] Test: With `show_no_cargo=True`, ship should be included
- [ ] Test: With `show_no_cargo=False, show_has_cargo=True`, ship should NOT be included
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.4: Add All Filters Disabled Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_all_disabled_returns_empty -v`

- [ ] Add test `test_filter_all_disabled_returns_empty` to `TestFilterShips` class
- [ ] Create filter_state with ALL status filters set to False:
  ```python
  filter_state = {
      'show_damaged': False,
      'show_undamaged': False,
      'show_derelict': False,
      'show_destroyed': False,
  }
  ```
- [ ] Test: With ships of various statuses, result should be empty list
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.5: Run Full Filter Test Suite [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run full filter test suite
- [ ] Verify all tests pass (existing + new)
- [ ] Record test count: _____ tests passed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 4 new test methods added and passing
- [ ] All existing tests still pass
- [ ] No behavioral changes to production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
