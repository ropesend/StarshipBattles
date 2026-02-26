# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add edge case tests before refactoring to establish a safety net.

**Why:** Safety analysis identified test coverage gaps. Adding these tests first ensures we catch any regressions during refactoring.

---

## Pre-Conditions
- [ ] Read `tests/unit/ui/screens/test_fleet_report_filters.py` to understand existing test patterns
- [ ] Understand how mock ships are created in existing tests

---

## Tasks

### Task 1.1: Add test for empty filter_state dict [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`
**Purpose:** Verify that empty dict uses all defaults (show all ships)

```python
def test_filter_ships_empty_filter_state_shows_all():
    """Empty filter_state should use defaults and show all ships."""
    # Create ships of various statuses
    # Call filter_ships(ships, {})
    # Assert all ships are returned
```

- [ ] Add test method to `TestFilterShips` class
- [ ] Test passes with current implementation

---

### Task 1.2: Add test for all status filters disabled [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`
**Purpose:** Verify that disabling all status filters returns empty list

```python
def test_filter_ships_all_status_filters_disabled():
    """All status filters False should return empty list."""
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    # Create ships of various statuses
    # Call filter_ships(ships, filter_state)
    # Assert empty list returned
```

- [ ] Add test method to `TestFilterShips` class
- [ ] Test passes with current implementation

---

### Task 1.3: Add test for combined capability filters [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombined -v`
**Purpose:** Verify multiple capability filters work together correctly

```python
class TestFilterShipsCombined:
    """Tests for combining multiple filter types."""

    def test_filter_ships_combined_warp_and_cargo_filters(self):
        """Multiple capability filters should combine correctly."""
        # Create ships with various combinations:
        # - Ship A: warp capable, has cargo
        # - Ship B: warp capable, no cargo
        # - Ship C: not warp capable, has cargo
        # - Ship D: not warp capable, no cargo
        # Test filtering for "warp capable AND no cargo" returns only Ship B
```

- [ ] Add new test class `TestFilterShipsCombined`
- [ ] Add test for warp + cargo combination
- [ ] Test passes with current implementation

---

### Task 1.4: Run targeted tests to verify baseline [Simple]
**Command:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] All existing tests pass
- [ ] All new tests pass
- [ ] Note test count: _____ tests

**Notes:** Record baseline test count for comparison after refactoring.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] At least 3 new test methods added
- [ ] All tests in `test_fleet_report_filters.py` pass
- [ ] No changes made to production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

---

## Verification Command
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
```

## Next Phase
After all tasks complete, proceed to [phase_2_checklist.md](phase_2_checklist.md).
