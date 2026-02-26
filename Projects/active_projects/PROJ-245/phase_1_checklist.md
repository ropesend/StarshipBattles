# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-245 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add edge case tests before any code changes to catch regressions during refactoring.

---

## Tasks

### Task 1.1: Combined Filter Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: ship that is warp-capable AND has cargo (both filters active, verify both apply)
- [ ] Add test: ship that is derelict AND has spaceyard (verify status filter still applies)
- [ ] Add test: ship matching special ability filter but excluded by damaged filter
- [ ] Add test: multiple filters active simultaneously (warp + status + cargo)
- [ ] Verify: all new tests pass

**Notes:** These tests verify that filters compose correctly (AND semantics).

---

### Task 1.2: All-Filters-Disabled Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: `filter_ships(ships, {'show_damaged': False, 'show_undamaged': False, 'show_derelict': False, 'show_destroyed': False})` returns empty list
- [ ] Verify: test passes

**Notes:** Edge case where all status filters disabled should show no ships.

---

### Task 1.3: Empty Input Edge Cases [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: `filter_ships([], {...})` returns empty list
- [ ] Add test: empty filter_state `filter_ships(ships, {})` returns all ships (defaults to True)
- [ ] Verify: both tests pass

**Notes:** Ensure graceful handling of empty inputs.

---

### Task 1.4: Multiple Special Capabilities [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add test: ship with multiple special abilities (e.g., can destroy planet AND can open warp)
- [ ] Add test: filter that hides one ability but shows another (verify correct behavior)
- [ ] Verify: tests pass

**Notes:** Special capabilities loop must handle ships with multiple abilities correctly.

---

### Task 1.5: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`

- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all new tests pass
- [ ] Run: `pytest tests/ -n 12 --tb=short` to verify no regressions
- [ ] Verify: 6246+ tests pass

**Notes:** Ensure no regressions before proceeding to code changes.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] At least 8 new test cases added
- [ ] All tests passing (including new ones)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
