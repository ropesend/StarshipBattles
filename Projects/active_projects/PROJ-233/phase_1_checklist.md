# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any code changes to ensure safe refactoring.

---

## Tasks

### Task 1.1: Empty List and Defaults [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "empty"`

- [ ] Add test `test_filter_empty_list_returns_empty`
  - Input: `filter_ships([], {})`
  - Expected: Returns `[]`, no exceptions
- [ ] Add test `test_filter_empty_state_shows_all_ships`
  - Input: Ships list with mixed states, `filter_state={}`
  - Expected: All ships returned (missing keys default to True)
- [ ] Add test `test_filter_partial_state_defaults_missing_keys`
  - Input: `filter_state={'show_damaged': False}` (only one key)
  - Expected: Other filters default to True

**Notes:**

---

### Task 1.2: All Filters Disabled [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "disabled"`

- [ ] Add test `test_filter_all_status_disabled_returns_empty`
  - Create ships of all 4 status types
  - Set all status filters to False
  - Expected: Empty list returned

**Notes:**

---

### Task 1.3: Multiple Filter Combinations [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "combined"`

- [ ] Add test `test_filter_combined_status_and_warp`
  - Ships: damaged+warp, damaged+no-warp, undamaged+warp, undamaged+no-warp
  - Filter: `show_damaged=True, show_undamaged=False, show_warp_capable=False, show_not_warp_capable=True`
  - Expected: Only damaged+no-warp ships pass
- [ ] Add test `test_filter_combined_cargo_and_spaceyard`
  - Ships with various cargo/spaceyard combinations
  - Verify both filters apply independently

**Notes:**

---

### Task 1.4: Status Mutual Exclusivity [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "exclusivity or mutual"`

- [ ] Add test `test_derelict_not_filtered_as_damaged`
  - Ship: `is_derelict=True` (which implies is_damaged() returns True)
  - Filter: `show_derelict=True, show_damaged=False`
  - Expected: Ship passes (evaluated as derelict, not damaged)
- [ ] Add test `test_destroyed_not_filtered_as_derelict_or_damaged`
  - Ship: `is_alive=False`
  - Filter: `show_destroyed=True, show_derelict=False, show_damaged=False`
  - Expected: Ship passes (evaluated as destroyed only)

**Notes:**

---

### Task 1.5: Missing Special Capability Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "capability"`

Reference existing `TestSpecialCapabilityFilter` class for patterns.

- [ ] Add test `test_filter_open_warp_capability`
  - Mock ship with OpenWarpPoint ability
  - Test `show_can_open_warp=False` hides ship
  - Test `show_no_open_warp=False` hides ships without ability
- [ ] Add test `test_filter_close_warp_capability`
  - Mock ship with CloseWarpPoint ability
  - Test both filter directions
- [ ] Add test `test_filter_destroy_star_capability`
  - Mock ship with DestroyStar ability
  - Test both filter directions
- [ ] Add test `test_filter_create_sphere_capability`
  - Mock ship with CreateSphereWorld ability
  - Test both filter directions

**Notes:**

---

## Verification Commands

```bash
# Run all filter_ships tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Count tests (should increase by ~10-12)
pytest tests/unit/ui/screens/test_fleet_report_filters.py --collect-only | grep "test session starts" -A 1

# Verify no regressions
pytest tests/unit/ui/screens/test_fleet_report_filters.py --tb=short
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing
- [ ] No existing tests broken
- [ ] Test count increased by ~10-12 tests
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
