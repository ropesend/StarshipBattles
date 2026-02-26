# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-230 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 8 safety tests to create a regression safety net before refactoring

---

## Tasks

### Task 1.1: Add Status Hierarchy Tests [Critical]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

These tests verify the critical mutual exclusivity invariant: each ship matches exactly ONE status category.

- [ ] Add `test_derelict_not_counted_as_damaged`:
  ```python
  def test_derelict_not_counted_as_damaged(self):
      """Ship that is derelict AND is_damaged()=True matches ONLY derelict filter."""
      # Create ship that is derelict but also returns True for is_damaged()
      # filter_state = {'show_damaged': False, 'show_derelict': True, ...}
      # Assert ship passes (not filtered by damaged)
  ```
- [ ] Add `test_destroyed_not_counted_as_derelict`:
  ```python
  def test_destroyed_not_counted_as_derelict(self):
      """Ship that is destroyed AND was derelict matches ONLY destroyed filter."""
      # Create ship that is_alive=False but is_derelict=True
      # filter_state = {'show_destroyed': True, 'show_derelict': False, ...}
      # Assert ship passes (not filtered by derelict)
  ```
- [ ] Verify: Both tests pass with current implementation

**Notes:** Add to `TestFilterShips` class

---

### Task 1.2: Add Empty Input Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

- [ ] Add `test_empty_ships_list`:
  ```python
  def test_empty_ships_list(self):
      """Empty ships list returns empty list."""
      result = filter_ships([], {'show_damaged': True, ...})
      assert result == []
  ```
- [ ] Add `test_empty_filter_state_shows_all`:
  ```python
  def test_empty_filter_state_shows_all(self):
      """Empty filter_state dict shows all ships (all defaults to True)."""
      ships = [make_mock_ship() for _ in range(3)]
      result = filter_ships(ships, {})
      assert len(result) == 3
  ```
- [ ] Verify: Both tests pass with current implementation

**Notes:** Add to `TestFilterShips` class

---

### Task 1.3: Add Invariant Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_preserves_input_order`:
  ```python
  def test_preserves_input_order(self):
      """Filtered ships maintain original relative order."""
      ships = [make_mock_ship(serial=i) for i in [5, 2, 8, 1, 9]]
      result = filter_ships(ships, {})  # Show all
      assert [s.serial for s in result] == [5, 2, 8, 1, 9]
  ```
- [ ] Add `test_does_not_mutate_input`:
  ```python
  def test_does_not_mutate_input(self):
      """filter_ships does not modify input list."""
      ships = [make_mock_ship()]
      original_len = len(ships)
      filter_ships(ships, {'show_undamaged': False})
      assert len(ships) == original_len
  ```
- [ ] Verify: Both tests pass with current implementation

**Notes:** Add to `TestFilterShips` class

---

### Task 1.4: Add Both-False Edge Case Test [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`

- [ ] Add `test_both_warp_filters_false_shows_none`:
  ```python
  def test_both_warp_filters_false_shows_none(self):
      """Both warp filters False results in empty list."""
      ships = [make_warp_capable_ship(), make_non_warp_ship()]
      filter_state = {'show_warp_capable': False, 'show_not_warp_capable': False, ...}
      result = filter_ships(ships, filter_state)
      assert len(result) == 0
  ```
- [ ] Verify: Test passes with current implementation

**Notes:** Add to `TestFilterShipsWarp` class

---

### Task 1.5: Add Missing Special Capability Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

Currently only `DestroyPlanet` is tested. Add tests for remaining 4 capabilities.

- [ ] Add test for `OpenWarpPoint` capability filter
- [ ] Add test for `CloseWarpPoint` capability filter
- [ ] Add test for `DestroyStar` capability filter
- [ ] Add test for `CreateSphereWorld` capability filter
- [ ] Verify: All 4 new tests pass with current implementation

**Notes:** Follow pattern from existing `test_filter_hides_ships_with_ability` tests

---

### Task 1.6: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Document baseline test count: _____ tests
- [ ] Verify: 0 failures, 0 errors
- [ ] Commit with message: `[PROJ-230] Phase 1: Add safety tests for filter_ships refactoring`

**Notes:** This establishes the baseline before refactoring begins

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 8 new tests passing
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
