# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-244 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add safety tests before any code changes to catch regressions in high-risk areas.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add Combined Multi-Category Filter Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombined -v`

- [ ] Create test class `TestFilterShipsCombined`
- [ ] Add test `test_combined_warp_and_cargo_filter`
  - Create ships: warp+cargo, warp+no-cargo, no-warp+cargo, no-warp+no-cargo
  - Filter with `show_warp_capable=True, show_not_warp_capable=False, show_has_cargo=True, show_no_cargo=False`
  - Assert only warp+cargo ship passes
- [ ] Add test `test_combined_status_and_capability_filter`
  - Create ships: damaged+warp, damaged+no-warp, undamaged+warp, undamaged+no-warp
  - Filter with `show_damaged=False, show_not_warp_capable=False`
  - Assert only undamaged+warp ship passes
- [ ] Verify: Run test class and confirm both tests pass

**Notes:**

---

### Task 1.2: Add Derelict/Damaged Precedence Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add test `test_derelict_takes_precedence_over_damaged` to `TestFilterShips`
  - Create a derelict ship (which also returns True for `is_damaged()`)
  - Filter with `show_derelict=True, show_damaged=False`
  - Assert derelict ship IS included (categorized as derelict, not damaged)
- [ ] Add test `test_derelict_excluded_when_derelict_filter_off`
  - Same ship, filter with `show_derelict=False, show_damaged=True`
  - Assert derelict ship is NOT included
- [ ] Verify: Run tests and confirm precedence behavior is correct

**Notes:**

---

### Task 1.3: Add Partial Filter State Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add test `test_partial_filter_state_defaults_to_show` to `TestFilterShips`
  - Create mixed ships (damaged, undamaged, warp, no-warp)
  - Pass empty `filter_state={}`
  - Assert all ships pass (missing keys default to True)
- [ ] Add test `test_filter_state_missing_some_keys`
  - Pass filter_state with only `{'show_damaged': False}`
  - Assert other filters still work (undamaged, warp, etc. still pass)
- [ ] Verify: Run tests and confirm default behavior works

**Notes:**

---

### Task 1.4: Verify All Tests Pass [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run full test suite for file
- [ ] Verify no regressions: all existing tests + new tests pass
- [ ] Record test count (should be original + 6 new tests)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 6 new tests added and passing
- [ ] All existing tests still passing
- [ ] No changes to production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
