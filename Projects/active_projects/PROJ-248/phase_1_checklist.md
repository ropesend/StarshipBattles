# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-248 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing test coverage before any refactoring

---

## Tasks

### Task 1.1: Add empty input tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_empty_ships_list_returns_empty()` - verify `filter_ships([], {...})` returns `[]`
- [ ] Add `test_filter_empty_filter_state_shows_all()` - verify `filter_ships(ships, {})` returns all ships
- [ ] Run tests to verify they pass

**Code:**
```python
def test_filter_empty_ships_list_returns_empty(self):
    """Empty ships list returns empty list."""
    result = filter_ships([], {'show_damaged': True, 'show_undamaged': True})
    assert result == []

def test_filter_empty_filter_state_shows_all(self):
    """Empty filter state shows all ships (defaults to True)."""
    ships = [self._make_ship(), self._make_ship(is_damaged=True)]
    result = filter_ships(ships, {})
    assert len(result) == 2
```

---

### Task 1.2: Add all-disabled test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_all_status_disabled_returns_empty()` - all show_* flags False returns empty
- [ ] Run tests to verify it passes

**Code:**
```python
def test_filter_all_status_disabled_returns_empty(self):
    """All status filters False returns no ships."""
    ships = [self._make_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0
```

---

### Task 1.3: Add status ordering tests [Medium] - CRITICAL
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

These tests protect the critical invariant: status checks must follow order destroyed -> derelict -> damaged -> undamaged.

- [ ] Add `test_destroyed_ship_not_matched_as_derelict()` - ship with `is_alive=False, is_derelict=True` filtered by `show_destroyed=False` should be excluded
- [ ] Add `test_derelict_ship_not_matched_as_damaged()` - ship with `is_derelict=True, is_damaged()=True` filtered by `show_derelict=False` should be excluded
- [ ] Run tests to verify they pass

**Code:**
```python
def test_destroyed_ship_not_matched_as_derelict(self):
    """Destroyed ship classified as destroyed, not derelict (ordering test)."""
    ship = self._make_ship()
    ship.is_alive = False
    ship.is_derelict = True
    filter_state = {
        'show_destroyed': False,
        'show_derelict': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be filtered as destroyed, not kept as derelict

def test_derelict_ship_not_matched_as_damaged(self):
    """Derelict ship classified as derelict, not damaged (ordering test)."""
    ship = self._make_ship()
    ship.is_derelict = True
    ship.is_damaged = Mock(return_value=True)
    filter_state = {
        'show_derelict': False,
        'show_damaged': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be filtered as derelict, not kept as damaged
```

---

### Task 1.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify all tests pass (including 5 new tests)
- [ ] No regressions

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All 5 new tests written and passing
- [ ] No changes to production code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
