# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-242 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage identified by safety analysis before any code changes

---

## Tasks

### Task 1.1: Add Combined Filter Interaction Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "combined" -v`

Add test for multiple filter categories working together:
- [ ] Create test class `TestFilterShipsCombined`
- [ ] Test: Ship with warp capability but no cargo, with warp=show and cargo=hide → excluded
- [ ] Test: Derelict ship with spaceyard, with derelict=show and spaceyard=hide → excluded
- [ ] Test: All filters passing → ship included
- [ ] Verify tests pass

**Notes:** Test that filter categories are ANDed together (all must pass)

---

### Task 1.2: Add Both-True Filter Pairs Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "both_true" -v`

Add explicit test that both-True filter pairs act as no-ops:
- [ ] Add test `test_filter_warp_both_true_shows_all` - both warp filters True shows all ships
- [ ] Add test `test_filter_spaceyard_both_true_shows_all` - both spaceyard filters True shows all ships
- [ ] Add test `test_filter_cargo_both_true_shows_all` - both cargo filters True shows all ships
- [ ] Verify tests pass

**Notes:** These may already be implicitly tested but should be explicit

---

### Task 1.3: Add All-False Status Filters Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "all_false" -v`

Add test for edge case where all status filters are False:
- [ ] Add test `test_filter_all_status_false_returns_empty`
- [ ] Set all 4 status filters to False (show_damaged, show_undamaged, show_derelict, show_destroyed)
- [ ] Verify empty list returned regardless of input ships
- [ ] Verify test passes

**Notes:** Edge case - should return empty list

---

### Task 1.4: Add Empty Ships List Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "empty" -v`

Add explicit test for empty input:
- [ ] Add test `test_filter_empty_ships_returns_empty`
- [ ] Call `filter_ships([], {})`
- [ ] Verify returns empty list `[]`
- [ ] Verify test passes

**Notes:** Trivial but should be explicit

---

### Task 1.5: Add Multiple Special Capability Filters Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "special" -v`

Add test for all 5 special ability filters active simultaneously:
- [ ] Add test `test_filter_multiple_special_abilities_combined`
- [ ] Create ship with subset of special abilities (e.g., has destroy_planet, has open_warp, lacks others)
- [ ] Set filters to show only ships that have destroy_planet AND lack close_warp
- [ ] Verify correct filtering behavior
- [ ] Verify test passes

**Notes:** Tests that special ability loop handles multiple active filters

---

### Task 1.6: Add Status Priority Edge Case Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "priority" -v`

Add test for status classification priority:
- [ ] Add test class `TestStatusPriority`
- [ ] Test: Destroyed ship is classified as destroyed even if is_damaged() returns True
- [ ] Test: Derelict ship is classified as derelict, not damaged
- [ ] Mock ship with `is_alive=False, is_damaged()=True` → should be destroyed, not damaged
- [ ] Verify tests pass

**Notes:** Critical for status filter refactoring - priority order must be preserved

---

### Task 1.7: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

Verify all tests pass after additions:
- [ ] Run full test suite
- [ ] Verify 6246+ tests pass (baseline + new tests)
- [ ] No regressions

**Notes:** Establishes baseline before Phase 2

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] At least 6 new test methods added
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
