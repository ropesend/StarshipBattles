# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-227 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing edge case tests before refactoring to ensure safety net is complete.

---

## Pre-Phase Checklist
- [ ] Read `tests/unit/ui/screens/test_fleet_report_filters.py` to understand existing test patterns
- [ ] Run existing tests to establish baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### Task 1.1: Add Empty Input Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_ships_empty_list_returns_empty`:
  ```python
  def test_filter_ships_empty_list_returns_empty():
      result = filter_ships([], {})
      assert result == []
  ```

- [ ] Add `test_filter_ships_empty_filter_state_shows_all` (use existing mock patterns)

**Notes:** These tests verify default behavior when inputs are empty.

---

### Task 1.2: Add Partial Filter State Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_ships_partial_filter_state_defaults_to_true`:
  - Only specify `show_damaged: False` in filter_state
  - Verify undamaged ships pass (other filters default to True)

**Notes:** Verifies `.get()` defaults work correctly.

---

### Task 1.3: Add Status Mutual Exclusivity Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_destroyed_ship_only_matches_destroyed_filter`:
  - Create ship with `is_alive=False`
  - Set `show_destroyed=False, show_derelict=True`
  - Verify ship is filtered out (destroyed status takes priority)

- [ ] Add `test_derelict_ship_only_matches_derelict_filter`:
  - Create ship with `is_derelict=True` (and `is_damaged()=True`)
  - Set `show_derelict=False, show_damaged=True`
  - Verify ship is filtered out (derelict status takes priority)

**Notes:** Critical invariant - status categories are mutually exclusive.

---

### Task 1.4: Add Combined Filter Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_capability_and_status_filters_combined`:
  - Create warp-capable + damaged ship
  - Set `show_warp_capable=True, show_not_warp_capable=False, show_damaged=False`
  - Verify ship is filtered out (fails status filter even though passes capability)

**Notes:** Verifies AND logic between capability and status filters.

---

### Task 1.5: Add All-Filters-Disabled Edge Case [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_all_status_filters_disabled_returns_empty`:
  - Create ships in all 4 status categories
  - Disable all 4 status filters (`show_undamaged/damaged/derelict/destroyed=False`)
  - Verify result is empty list

**Notes:** Edge case where no ships can pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run all new tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v -k "empty or partial or mutual or combined or disabled"`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Commit: `git add -A && git commit -m "[PROJ-227] Phase 1: Add edge case tests for filter_ships"`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
