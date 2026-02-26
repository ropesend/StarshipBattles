# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-234 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add edge case tests identified by safety analysis before making any code changes.

**Test file:** `tests/unit/ui/screens/test_fleet_report_filters.py`

---

## Tasks

### Task 1.1: Add test for empty filter_state [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_filter_empty_filter_state_shows_all` to `TestFilterShips` class
- [ ] Test that passing `{}` as filter_state returns all ships
- [ ] Verify test passes with current implementation

```python
def test_filter_empty_filter_state_shows_all(self):
    """Empty filter_state should default all filters to True (show all)."""
    ships = [
        make_mock_ship(is_damaged=True),
        make_mock_ship(is_damaged=False),
    ]
    result = filter_ships(ships, {})
    assert len(result) == 2
```

**Notes:**

---

### Task 1.2: Add test for both-false warp filters [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

- [ ] Add `test_filter_both_warp_filters_false_shows_nothing` to `TestFilterShipsWarp` class
- [ ] Test that `show_warp_capable=False, show_not_warp_capable=False` returns empty list
- [ ] Verify test passes with current implementation

```python
def test_filter_both_warp_filters_false_shows_nothing(self):
    """When both warp filters are False, no ships should pass."""
    ships = [
        make_mock_ship(warp_capable=True),
        make_mock_ship(warp_capable=False),
    ]
    filter_state = self._default_filter_state()
    filter_state['show_warp_capable'] = False
    filter_state['show_not_warp_capable'] = False
    result = filter_ships(ships, filter_state)
    assert len(result) == 0
```

**Notes:**

---

### Task 1.3: Add test for both-false spaceyard filters [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`

- [ ] Add `test_filter_both_spaceyard_filters_false_shows_nothing` to `TestFilterShipsSpaceyard` class
- [ ] Test that `show_has_spaceyard=False, show_no_spaceyard=False` returns empty list
- [ ] Verify test passes with current implementation

**Notes:**

---

### Task 1.4: Add test for both-false cargo filters [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`

- [ ] Add `test_filter_both_cargo_filters_false_shows_nothing` to `TestFilterShipsCargo` class
- [ ] Test that `show_has_cargo=False, show_no_cargo=False` returns empty list
- [ ] Verify test passes with current implementation

**Notes:**

---

### Task 1.5: Add test for combined capability + status filter [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_filter_warp_and_damaged_combined` to `TestFilterShips` class
- [ ] Test ship must pass BOTH warp and status filters to be included
- [ ] Include ships with various combinations to verify AND logic

```python
def test_filter_warp_and_damaged_combined(self):
    """Ships must pass ALL filters - test warp + status combination."""
    ships = [
        make_mock_ship(is_damaged=True, warp_capable=True),   # fails: damaged hidden
        make_mock_ship(is_damaged=False, warp_capable=True),  # passes
        make_mock_ship(is_damaged=True, warp_capable=False),  # fails: both
        make_mock_ship(is_damaged=False, warp_capable=False), # fails: not warp
    ]
    filter_state = self._default_filter_state()
    filter_state['show_damaged'] = False
    filter_state['show_not_warp_capable'] = False
    result = filter_ships(ships, filter_state)
    assert len(result) == 1  # Only undamaged + warp-capable
```

**Notes:**

---

### Task 1.6: Run tests and verify baseline [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Run full test file
- [ ] Verify all new tests pass
- [ ] Record baseline test count

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 5 new tests added and passing
- [ ] No changes to production code in this phase
- [ ] Commit: `[PROJ-234] Phase 1: Add edge case tests for filter_ships`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
