# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add edge case tests before any code changes to protect against regressions.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add test for empty filter_state [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Read existing test file to understand patterns and fixtures
- [ ] Add `test_filter_ships_empty_filter_state_shows_all()` to `TestFilterShips` class
- [ ] Test that passing `{}` as filter_state shows all ships (all defaults to True)
- [ ] Include mix of damaged, undamaged, derelict ships
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_ships_empty_filter_state_shows_all -v`

**Notes:** Empty filter_state should behave same as all-True state

---

### Task 1.2: Add test for all status filters False [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_filter_ships_all_status_filters_false_shows_none()` to `TestFilterShips` class
- [ ] Test filter_state with all status filters False:
  ```python
  {
      'show_damaged': False,
      'show_undamaged': False,
      'show_derelict': False,
      'show_destroyed': False,
  }
  ```
- [ ] Verify returns empty list regardless of ship states
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_ships_all_status_filters_false_shows_none -v`

**Notes:** Edge case where nothing passes the filter

---

### Task 1.3: Add test for destroyed+derelict precedence [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_filter_ships_destroyed_takes_precedence_over_derelict()` to `TestFilterShips` class
- [ ] Create mock ship with `is_alive=False` AND `is_derelict=True`
- [ ] Test with `show_destroyed=False, show_derelict=True`
- [ ] Verify ship is hidden (destroyed takes precedence)
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_ships_destroyed_takes_precedence_over_derelict -v`

**Notes:** Critical invariant - destroyed status must be checked first

---

### Task 1.4: Add test for capability filter independence [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_ships_multiple_capability_filters_combine()` to appropriate class
- [ ] Test that multiple capability filters can be combined
- [ ] Create ships with different combinations of capabilities
- [ ] Verify filters are applied independently (AND logic)
- [ ] Verify: test passes

**Notes:** Ensure no filter affects another incorrectly

---

### Task 1.5: Run full test suite [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all tests pass (existing + new)
- [ ] Record test count before/after

**Notes:** No code changes to `fleet_report_filters.py` in this phase

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 4 new test methods added and passing
- [ ] All existing tests still pass
- [ ] No code changes to `fleet_report_filters.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
