# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing edge case tests before any code changes to ensure refactoring safety.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add empty filter_state test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add test `test_filter_empty_filter_state_shows_all` to `TestFilterShips` class
  - Create 2 mock ships (one damaged, one healthy)
  - Call `filter_ships(ships, {})` with empty dict
  - Assert both ships returned (default=show all)
- [ ] Verify test passes

**Notes:**

---

### Task 1.2: Add cargo_contents=None test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

- [ ] Add test `test_filter_cargo_none_treated_as_no_cargo` to `TestFilterShipsCargo` class
  - Create mock ship with `cargo_contents = None`
  - Set filter_state: `{'show_has_cargo': False, 'show_no_cargo': True}`
  - Assert ship passes filter (None = no cargo)
- [ ] Verify test passes

**Notes:**

---

### Task 1.3: Add both-filters-false test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

- [ ] Add test `test_filter_both_warp_filters_false_excludes_all` to `TestFilterShipsWarp` class
  - Create 2 ships: one warp-capable, one not
  - Set filter_state: `{'show_warp_capable': False, 'show_not_warp_capable': False}`
  - Assert empty result (all excluded)
- [ ] Verify test passes

**Notes:**

---

### Task 1.4: Add derelict+damaged precedence test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add test `test_filter_derelict_takes_precedence_over_damaged` to `TestFilterShips` class
  - Create mock ship: `is_derelict=True`, `is_damaged()=True`
  - Set filter_state: `{'show_derelict': True, 'show_damaged': False}`
  - Assert ship passes (categorized as derelict, not damaged)
- [ ] Verify test passes

**Notes:**

---

### Task 1.5: Run tests and verify baseline [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run full test file: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all new tests pass
- [ ] Verify no existing tests broken

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 4 new edge case tests added and passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
