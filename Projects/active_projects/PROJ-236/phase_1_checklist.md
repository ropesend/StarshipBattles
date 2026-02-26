# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-236 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 6 safety tests before any code changes to document expected behavior and catch regressions.

**File to modify:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Pre-Phase Checks
- [ ] Run existing tests to establish baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All 25+ existing tests pass

---

## Tasks

### Task 1.1: Add Empty Input Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_empty_ships_returns_empty -v`

- [ ] Add test `test_filter_empty_ships_returns_empty` to `TestFilterShips` class
- [ ] Test: `filter_ships([], {'show_damaged': True}) == []`
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.2: Add Partial Filter State Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_with_empty_filter_state_shows_all -v`

- [ ] Add test `test_filter_with_empty_filter_state_shows_all` to `TestFilterShips` class
- [ ] Test: `filter_ships([ship1, ship2], {})` returns both ships
- [ ] Verifies missing keys default to True (show all)
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.3: Add All Filters Disabled Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_all_status_filters_disabled_returns_empty -v`

- [ ] Add test `test_all_status_filters_disabled_returns_empty` to `TestFilterShips` class
- [ ] Test: With all 4 status filters False, returns empty list
- [ ] Filter state: `{'show_damaged': False, 'show_undamaged': False, 'show_derelict': False, 'show_destroyed': False}`
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.4: Add Derelict Priority Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_derelict_priority_over_damaged -v`

- [ ] Add test `test_derelict_priority_over_damaged` to `TestFilterShips` class
- [ ] Create a ship that is both derelict AND damaged (set `is_derelict=True` and mock `is_damaged()` to return True)
- [ ] Test: With `show_damaged=False, show_derelict=True`, ship passes (categorized as derelict, not damaged)
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.5: Add Order Preservation Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_preserves_order -v`

- [ ] Add test `test_filter_preserves_order` to `TestFilterShips` class
- [ ] Create 3 ships with serials [3, 1, 2]
- [ ] Test: Output order matches input order `[s.serial for s in result] == [3, 1, 2]`
- [ ] Run test and verify it passes

**Notes:**

---

### Task 1.6: Add Combined Filters Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_combined_warp_and_status_filters -v`

- [ ] Add test `test_combined_warp_and_status_filters` to `TestFilterShips` class
- [ ] Create ships: warp+damaged, warp+undamaged, no_warp+damaged
- [ ] Test: With `show_warp_capable=True, show_not_warp_capable=False, show_damaged=True, show_undamaged=False`
- [ ] Result: Only the warp+damaged ship passes
- [ ] Run test and verify it passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test file: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass (original + 6 new)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
