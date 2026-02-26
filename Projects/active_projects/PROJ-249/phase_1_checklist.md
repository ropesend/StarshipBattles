# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-249 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any code changes to ensure safe refactoring.

---

## Tasks

### Task 1.1: Edge Case Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_filter_empty_ship_list_returns_empty`
  - Input: `ships=[]`, `filter_state={}`
  - Expected: Returns `[]`
  - Add to `TestFilterShips` class

- [ ] Add `test_filter_empty_filter_state_shows_all`
  - Input: List with 1 healthy ship, `filter_state={}`
  - Expected: Returns all ships (defaults to True)
  - Add to `TestFilterShips` class

- [ ] Add `test_filter_all_status_filters_disabled_returns_empty`
  - Input: 1 healthy ship, all status filters False
  - Filter state: `show_damaged=False, show_undamaged=False, show_derelict=False, show_destroyed=False`
  - Expected: Returns `[]`
  - Add to `TestFilterShips` class

- [ ] Verify: Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

**Notes:** [Filled during implementation]

---

### Task 1.2: Status Classification Order Tests (CRITICAL) [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestStatusFilterOrder -v`

- [ ] Create new test class `TestStatusFilterOrder`

- [ ] Add `test_destroyed_ship_classified_as_destroyed_not_derelict`
  - Create ship: `is_alive=False, is_derelict=True`
  - Filter state: `show_destroyed=False, show_derelict=True` (all others True)
  - Expected: Ship is EXCLUDED (classified as destroyed)

- [ ] Add `test_derelict_ship_classified_as_derelict_not_damaged`
  - Create ship: `is_alive=True, is_derelict=True, is_damaged()=True`
  - Filter state: `show_derelict=False, show_damaged=True` (all others True)
  - Expected: Ship is EXCLUDED (classified as derelict)

- [ ] Add `test_damaged_ship_classified_as_damaged_not_undamaged`
  - Create ship: `is_alive=True, is_derelict=False, is_damaged()=True`
  - Filter state: `show_damaged=False, show_undamaged=True` (all others True)
  - Expected: Ship is EXCLUDED (classified as damaged)

- [ ] Verify: Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestStatusFilterOrder -v`

**Notes:** These tests verify the critical invariant: destroyed > derelict > damaged > undamaged

---

### Task 1.3: Combined Filter Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestCombinedFilters -v`

- [ ] Create new test class `TestCombinedFilters`

- [ ] Add `test_combined_capability_and_status_filters`
  - Create 2 ships: damaged+warp, healthy+no-warp
  - Filter: `show_damaged=False, show_warp_capable=True, show_not_warp_capable=True`
  - Expected: Only healthy+no-warp ship passes

- [ ] Add `test_all_capability_filters_combine_correctly`
  - Create ship with: warp + spaceyard + cargo
  - Filter: `show_warp_capable=False`
  - Expected: Ship excluded despite having other capabilities

- [ ] Verify: Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestCombinedFilters -v`

**Notes:** [Filled during implementation]

---

### Task 1.4: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run targeted tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All 8 new tests pass
- [ ] No existing tests broken
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Full suite passes (6246+ tests)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 8 new tests added and passing
- [ ] Full test suite still passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
