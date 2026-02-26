# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-243 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing edge case tests identified by safety analysis BEFORE any code changes.

**Why This Phase First:** The safety analysis identified that status filter ordering is HIGH RISK. Adding tests first ensures any refactoring regressions are caught immediately.

---

## Prerequisites
- [ ] Read `tests/unit/ui/screens/test_fleet_report_filters.py` to understand existing test patterns
- [ ] Run existing tests to establish baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

---

## Tasks

### Task 1.1: Add Status Classification Edge Case Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] **Add `test_destroyed_derelict_ship_classified_as_destroyed`**
  - Create a ship with `is_alive=False` AND `is_derelict=True`
  - Filter with `show_destroyed=False`, all others `True`
  - Assert ship is EXCLUDED (destroyed takes precedence)
  - Test command: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_destroyed_derelict_ship_classified_as_destroyed -v`

- [ ] **Add `test_derelict_damaged_ship_classified_as_derelict`**
  - Create a derelict ship that also returns `True` for `is_damaged()`
  - Filter with `show_damaged=False`, `show_derelict=True`
  - Assert ship is INCLUDED (derelict takes precedence over damaged)
  - Test command: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_derelict_damaged_ship_classified_as_derelict -v`

**Notes:** These tests protect the critical status ordering during refactoring.

---

### Task 1.2: Add Multi-Filter Edge Case Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] **Add `test_multiple_special_capability_filters_all_must_pass`**
  - Create ship with DestroyPlanet ability but NOT OpenWarpPoint
  - Filter with `show_can_destroy_planet=False` AND `show_can_open_warp=False`
  - Assert ship is EXCLUDED (fails destroy_planet filter)
  - Add to `TestSpecialCapabilityFilter` class
  - Test command: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter::test_multiple_special_capability_filters_all_must_pass -v`

- [ ] **Add `test_partial_filter_state_defaults_to_show_all`**
  - Call `filter_ships()` with only `{'show_damaged': False}` (other keys missing)
  - Assert undamaged ships ARE included (missing keys default to True)
  - Add to `TestFilterShips` class
  - Test command: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_partial_filter_state_defaults_to_show_all -v`

**Notes:** These tests verify filter independence and default behavior.

---

## Verification

- [ ] Run all new tests individually to verify they pass
- [ ] Run full filter test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify test count increased by 4 tests
- [ ] Run `pytest tests/ --testmon` to verify no regressions

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 4 new edge case tests added and passing
- [ ] All existing tests still passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
