# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-228 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test cases identified by safety analysis BEFORE any code changes.

---

## Prerequisites
- [ ] Read `findings/safety_analysis.md` for coverage gaps
- [ ] Read existing tests in `tests/unit/ui/screens/test_fleet_report_filters.py`

## Tasks

### Task 1.1: Empty Ship List Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_empty_list_returns_empty -v`

- [ ] Add `test_filter_empty_list_returns_empty()` to `TestFilterShips` class:
  ```python
  def test_filter_empty_list_returns_empty(self):
      """Filter returns empty list for empty input."""
      result = filter_ships([], {})
      assert result == []
  ```
- [ ] Run test and verify it passes

**Notes:** Confirms behavior with edge case input.

---

### Task 1.2: Status Priority Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsStatusPriority -v`

- [ ] Create new test class `TestFilterShipsStatusPriority`

- [ ] Add `test_destroyed_takes_priority_over_derelict()`:
  - Create ship with `is_alive=False` and `is_derelict=True`
  - With `show_destroyed=True, show_derelict=False`, ship should be included
  - Verify ship is categorized as "destroyed", not "derelict"

- [ ] Add `test_derelict_takes_priority_over_damaged()`:
  - Create ship with `is_derelict=True` and `is_damaged()=True`
  - With `show_derelict=True, show_damaged=False`, ship should be included
  - Verify ship is categorized as "derelict", not "damaged"

- [ ] Run tests and verify they pass

**Notes:** Critical invariant tests - status priority chain must be preserved during refactoring.

---

### Task 1.3: Default Filter Keys Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_missing_keys_default_to_show_all -v`

- [ ] Add `test_filter_missing_keys_default_to_show_all()` to `TestFilterShips` class:
  ```python
  def test_filter_missing_keys_default_to_show_all(self):
      """Missing filter keys default to True (show all)."""
      # Create ships with various statuses
      ships = [healthy_ship, damaged_ship, derelict_ship]
      result = filter_ships(ships, {})  # Empty filter_state
      assert len(result) == 3  # All ships pass
  ```
- [ ] Run test and verify it passes

**Notes:** Confirms `.get(key, True)` default behavior.

---

### Task 1.4: Both Binary Filters Off Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp::test_filter_both_warp_filters_off_excludes_all -v`

- [ ] Add `test_filter_both_warp_filters_off_excludes_all()` to `TestFilterShipsWarp` class:
  ```python
  def test_filter_both_warp_filters_off_excludes_all(self):
      """When both warp filters are off, no ships pass."""
      ships = [warp_capable_ship, non_warp_ship]
      filter_state = {
          'show_warp_capable': False,
          'show_not_warp_capable': False,
      }
      result = filter_ships(ships, filter_state)
      assert len(result) == 0
  ```
- [ ] Run test and verify it passes

**Notes:** Documents edge case behavior when both sides of binary filter are disabled.

---

### Task 1.5: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run all tests in test file
- [ ] Verify all tests pass (old + new)
- [ ] Run: `pytest tests/ -n 12` (full suite baseline)
- [ ] Record baseline test count

**Notes:** Establishes baseline before refactoring.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 4+ new test cases added
- [ ] All new tests pass
- [ ] Full test suite passes
- [ ] Commit: `[PROJ-228] Phase 1: Test fortification for filter_ships`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
