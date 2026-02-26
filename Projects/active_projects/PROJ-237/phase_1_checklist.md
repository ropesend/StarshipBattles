# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-237 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 6 targeted tests to cover edge cases and invariants BEFORE any code changes.

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add TestFilterShipsEdgeCases class [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsEdgeCases -v`

- [ ] **1.1.1 test_filter_empty_list_returns_empty**
  - Assert: `filter_ships([], {'show_damaged': True}) == []`
  - Location: Add new test class after existing test classes

- [ ] **1.1.2 test_filter_empty_state_shows_all**
  - Setup: Create 2 ships (one damaged, one healthy)
  - Assert: `filter_ships(ships, {})` returns all ships (default True behavior)

- [ ] **1.1.3 test_filter_partial_state_uses_defaults**
  - Setup: Create 2 ships (one damaged, one healthy)
  - Assert: `filter_ships(ships, {'show_damaged': False})` returns only healthy ship

- [ ] **1.1.4 test_filter_all_status_disabled_returns_empty**
  - Setup: Create ship in any state
  - Filter: `{'show_damaged': False, 'show_undamaged': False, 'show_derelict': False, 'show_destroyed': False}`
  - Assert: Result is empty list

**Notes:** Use existing mock ship fixtures from the test file as reference.

---

### Task 1.2: Add TestFilterShipsStatusHierarchy class [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsStatusHierarchy -v`

- [ ] **1.2.1 test_derelict_ship_not_matched_as_damaged**
  - Setup: Create ship with `is_derelict=True` (which also makes `is_damaged()=True`)
  - Filter: `{'show_derelict': False, 'show_damaged': True, 'show_undamaged': True, 'show_destroyed': True}`
  - Assert: Ship is filtered out (not kept as damaged)
  - **CRITICAL:** This tests the status hierarchy invariant

- [ ] **1.2.2 test_combined_warp_and_status_filters**
  - Setup: Create 3 ships:
    - warp_damaged: `warp_capable=True, is_damaged=True`
    - warp_healthy: `warp_capable=True, is_damaged=False`
    - no_warp_damaged: `warp_capable=False, is_damaged=True`
  - Filter: `{'show_warp_capable': True, 'show_not_warp_capable': False, 'show_damaged': False, 'show_undamaged': True}`
  - Assert: Only `warp_healthy` in result

**Notes:** May need to mock `ShipStatsCalculator.has_warp_capability` for warp tests.

---

## Verification

```bash
# Run only the new tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsEdgeCases -v
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsStatusHierarchy -v

# Run all filter_ships tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Full suite
pytest tests/ -n 12
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6 new tests pass
- [ ] Existing 20+ tests still pass
- [ ] No code changes to `fleet_report_filters.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
