# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-235 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage BEFORE any code changes to ensure safe refactoring.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Pre-Flight
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all 20 existing tests pass
- [ ] Note current test count for comparison

---

## Task 1.1: Add Combined Filter Test [Medium]

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombinedFilters -v`

**Purpose:** Test that multiple filter types work together correctly.

- [ ] Add test class `TestFilterShipsCombinedFilters`
- [ ] Add test: `test_filter_status_and_warp_combined`
  - Create ships: damaged+warp, damaged+no-warp, undamaged+warp, undamaged+no-warp
  - Filter: `show_damaged=True, show_undamaged=False, show_warp_capable=True, show_not_warp_capable=False`
  - Expect: Only damaged+warp ship in result
- [ ] Verify: Test passes

**Notes:** [Filled during implementation]

---

## Task 1.2: Add Both-Sides-Disabled Filter Tests [Simple]

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombinedFilters -v`

**Purpose:** Verify that disabling both sides of a filter category returns empty results.

- [ ] Add test: `test_filter_both_warp_filters_disabled_returns_empty`
  - Create ships: mix of warp and non-warp capable
  - Filter: `show_warp_capable=False, show_not_warp_capable=False`
  - Expect: Empty list (no ships pass)
- [ ] Add test: `test_filter_both_status_filters_disabled_returns_empty`
  - Create ships: damaged and undamaged
  - Filter: `show_damaged=False, show_undamaged=False, show_derelict=False, show_destroyed=False`
  - Expect: Empty list
- [ ] Verify: Both tests pass

**Notes:** [Filled during implementation]

---

## Task 1.3: Add Status Priority Tests [Medium]

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsStatusPriority -v`

**Purpose:** Verify the critical status filter ordering invariant.

- [ ] Add test class `TestFilterShipsStatusPriority`
- [ ] Add test: `test_derelict_ship_filtered_by_derelict_not_damaged`
  - Create a derelict ship (which is also damaged by definition)
  - Filter: `show_derelict=False, show_damaged=True`
  - Expect: Ship is EXCLUDED (derelict filter takes precedence)
- [ ] Add test: `test_destroyed_ship_filtered_by_destroyed_not_derelict`
  - Create a destroyed ship
  - Filter: `show_destroyed=False, show_derelict=True`
  - Expect: Ship is EXCLUDED (destroyed filter takes precedence)
- [ ] Verify: Both tests pass

**Notes:** [Filled during implementation]

---

## Task 1.4: Add Multiple Special Capability Filter Test [Simple]

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

**Purpose:** Test combining multiple special capability filters.

- [ ] Add test to `TestSpecialCapabilityFilter`: `test_filter_multiple_special_capabilities_combined`
  - Create ships with different capability combinations
  - Filter: hide ships WITH DestroyPlanet AND hide ships WITHOUT OpenWarpPoint
  - Verify correct ships are excluded
- [ ] Verify: Test passes

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full filter test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify new test count: should be 24+ tests (was 20)
- [ ] All tests pass
- [ ] Run targeted tests: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
