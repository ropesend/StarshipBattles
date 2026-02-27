# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-200 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any code changes to ensure refactoring doesn't break behavior.

---

## Prerequisites
- [ ] Read `tests/unit/ui/screens/test_fleet_report_filters.py` to understand existing test patterns

## Tasks

### Task 1.1: Add Multi-Filter Combination Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: `test_filter_warp_and_damaged_combined` - Filter by warp capability AND damaged status simultaneously
- [ ] Add test: `test_filter_cargo_and_spaceyard_combined` - Filter by cargo AND spaceyard simultaneously
- [ ] Add test: `test_filter_all_categories_active` - Test with all filter categories having restrictions

**Notes:** These tests verify that filters from different categories work together correctly (AND semantics).

---

### Task 1.2: Add Remaining Special Capability Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

Existing test only covers `can_destroy_planet`. Add tests for the remaining 4 special capabilities:

- [ ] Add test: `test_filter_hides_ships_with_open_warp_ability` - Test `can_open_warp` / `show_can_open_warp` filter
- [ ] Add test: `test_filter_hides_ships_with_close_warp_ability` - Test `can_close_warp` / `show_can_close_warp` filter
- [ ] Add test: `test_filter_hides_ships_with_destroy_star_ability` - Test `can_destroy_star` / `show_can_destroy_star` filter
- [ ] Add test: `test_filter_hides_ships_with_create_sphere_ability` - Test `can_create_sphere` / `show_can_create_sphere` filter

**Notes:** Each test should mock `FleetCapabilityCalculator.ship_has_ability` to return True/False for the specific ability.

---

### Task 1.3: Add Edge Case Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: `test_filter_empty_filter_state_shows_all` - Verify `filter_ships(ships, {})` shows all ships (defaults to True)
- [ ] Add test: `test_filter_hide_all_returns_empty` - Verify setting all status filters to False returns empty list

**Notes:** These test the edge cases of empty/extreme filter states.

---

### Task 1.4: Add Status Filter Order Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add test: `test_derelict_ship_not_counted_as_damaged` - Create a derelict ship, set `show_derelict=False` and `show_damaged=True`, verify ship is NOT shown (derelict takes precedence over damaged)

**Notes:** This is a critical invariant test. A derelict ship is technically damaged, but the derelict filter should take precedence.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
