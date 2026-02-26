# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-241 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any code changes (6 scenarios from safety analysis)

---

## Pre-Phase Verification
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Note current test count (expected: 39 passing)

---

## Tasks

### Task 1.1: Add Combined Filter Interaction Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** Add new test class `TestFilterShipsCombinedFilters`

- [ ] Test: Warp-capable ship with cargo, warp filter=False, cargo filter=True -> excluded
- [ ] Test: Non-warp ship without cargo, warp filter=True, cargo filter=False -> excluded
- [ ] Test: Damaged ship with spaceyard, status=show_damaged, spaceyard=False -> excluded
- [ ] Test: Ship passing all filters -> included
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombinedFilters -v`

**Notes:**

---

### Task 1.2: Add Both-True Filter Pair Tests (No-op Verification) [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** Add tests in existing classes or new `TestFilterNoOpBehavior`

- [ ] Test: `show_warp_capable=True, show_not_warp_capable=True` -> all ships pass warp filter
- [ ] Test: `show_has_spaceyard=True, show_no_spaceyard=True` -> all ships pass spaceyard filter
- [ ] Test: `show_has_cargo=True, show_no_cargo=True` -> all ships pass cargo filter
- [ ] Verify: Tests pass

**Notes:**

---

### Task 1.3: Add All-False Status Filter Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `TestFilterShips` class

- [ ] Test: `show_damaged=False, show_undamaged=False, show_derelict=False, show_destroyed=False`
- [ ] Expected: Returns empty list regardless of input ships
- [ ] Verify: Test passes

**Notes:**

---

### Task 1.4: Add Empty Ships List Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `TestFilterShips` class

- [ ] Test: `filter_ships([], any_filter_state)` returns `[]`
- [ ] Verify: No exceptions raised, returns empty list

**Notes:**

---

### Task 1.5: Add Multiple Special Capabilities Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `TestSpecialCapabilityFilter` class

- [ ] Test: Ship with 2+ special abilities, filter only one ability type
- [ ] Test: Ship with 2+ special abilities, filter multiple ability types simultaneously
- [ ] Verify: Tests pass

**Notes:**

---

### Task 1.6: Add Status Priority Edge Case Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `TestFilterShips` class

- [ ] Test: Create mock ship where `is_alive=False` AND `is_damaged()=True`
- [ ] Apply filter `show_destroyed=True, show_damaged=False`
- [ ] Expected: Ship IS included (classified as destroyed, not damaged)
- [ ] This verifies the status priority order: destroyed > derelict > damaged > undamaged
- [ ] Verify: Test passes

**Notes:**

---

## Post-Phase Verification
- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All new tests pass (should be 45+ tests now)
- [ ] No existing tests broken

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

## Test Commands
```bash
# Run filter tests only
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Run specific new test class
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombinedFilters -v

# Run with coverage
pytest tests/unit/ui/screens/test_fleet_report_filters.py --cov=game/ui/screens/fleet_report_filters -v
```
