# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-229 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing invariant and edge case tests BEFORE any code changes.

**Why:** Safety analysis identified critical invariants (status hierarchy, order preservation) that lack explicit test coverage. These tests will catch regressions during refactoring.

---

## Pre-Phase
- [ ] Run existing tests to establish baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Note current test count (expected: ~19 direct tests)

## Tasks

### Task 1.1: Add Empty Input Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add new test class `TestFilterShipsInvariants`

- [ ] Add `test_empty_ships_list_returns_empty`:
  ```python
  def test_empty_ships_list_returns_empty(self):
      """Empty input list returns empty output list."""
      result = filter_ships([], {'show_damaged': True})
      assert result == []
  ```

- [ ] Add `test_empty_filter_state_shows_all_ships`:
  ```python
  def test_empty_filter_state_shows_all_ships(self):
      """Empty filter_state dict defaults all filters to True (show all)."""
      ships = [create_ship_instance(...)]  # Use existing fixture pattern
      result = filter_ships(ships, {})
      assert len(result) == len(ships)
  ```

**Notes:** Use existing fixture patterns from `TestFilterShips` class

---

### Task 1.2: Add Status Hierarchy Invariant Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** `TestFilterShipsInvariants` class

- [ ] Add `test_derelict_not_counted_as_damaged`:
  ```python
  def test_derelict_not_counted_as_damaged(self):
      """Derelict ship matches derelict filter, NOT damaged filter."""
      # Create derelict ship (is_derelict=True, is_damaged()=True)
      # With show_damaged=False, show_derelict=True
      # Ship should PASS (counted as derelict, not damaged)
  ```

- [ ] Add `test_destroyed_not_counted_as_derelict`:
  ```python
  def test_destroyed_not_counted_as_derelict(self):
      """Destroyed ship matches destroyed filter, NOT derelict filter."""
      # Create destroyed ship (is_alive=False)
      # With show_derelict=False, show_destroyed=True
      # Ship should PASS (counted as destroyed, not derelict)
  ```

**Notes:** These tests document the critical status hierarchy invariant

---

### Task 1.3: Add Edge Case Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** `TestFilterShipsInvariants` class

- [ ] Add `test_both_filter_pairs_false_excludes_all`:
  ```python
  def test_both_filter_pairs_false_excludes_all(self):
      """When both sides of a filter pair are False, no ships pass."""
      ships = [warp_ship, non_warp_ship]
      result = filter_ships(ships, {
          'show_warp_capable': False,
          'show_not_warp_capable': False
      })
      assert result == []
  ```

- [ ] Add `test_preserves_input_order`:
  ```python
  def test_preserves_input_order(self):
      """Filtered ships maintain original relative order."""
      ships = [ship_a, ship_b, ship_c]  # All pass filter
      result = filter_ships(ships, {})
      assert result == [ship_a, ship_b, ship_c]
  ```

- [ ] Add `test_does_not_mutate_input`:
  ```python
  def test_does_not_mutate_input(self):
      """Input list and ships are not modified."""
      ships = [ship1, ship2]
      original_list = ships.copy()
      filter_ships(ships, {'show_damaged': False})
      assert ships == original_list
  ```

**Notes:** These edge cases protect against common refactoring mistakes

---

### Task 1.4: Run Tests [Simple]
- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all new tests PASS (confirming current behavior)
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass
- [ ] No existing tests broken
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Commit: `[PROJ-229] Phase 1: Add invariant tests for filter_ships - Automated`

## Test Commands
```bash
# Run filter tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Run with coverage
pytest tests/unit/ui/screens/test_fleet_report_filters.py --cov=game.ui.screens.fleet_report_filters -v

# Full suite
pytest tests/ -n 12
```
