# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-246 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add safety tests for identified coverage gaps before any code changes

---

## Tasks

### Task 1.1: Add Empty Input Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "empty"`

Add tests to verify edge case behavior:

- [ ] Add `test_filter_empty_ships_list`:
  ```python
  def test_filter_empty_ships_list(self):
      """filter_ships with empty list returns empty list."""
      result = filter_ships([], {'show_damaged': True, 'show_undamaged': True})
      assert result == []
  ```
- [ ] Add `test_filter_with_empty_filter_state`:
  ```python
  def test_filter_with_empty_filter_state(self):
      """filter_ships with empty filter_state shows all ships (defaults to True)."""
      ships = [self._make_ship(), self._make_damaged_ship()]
      result = filter_ships(ships, {})
      assert len(result) == 2
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

**Notes:** [Filled during implementation]

---

### Task 1.2: Add Status Priority Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "derelict"`

Add test to verify status classification order:

- [ ] Add `test_derelict_classified_as_derelict_not_damaged`:
  ```python
  def test_derelict_classified_as_derelict_not_damaged(self):
      """A derelict ship (which is also damaged) should be classified as derelict only."""
      ship = self._make_derelict_ship()  # Note: derelict ships are inherently damaged
      # Hide derelict but show damaged - ship should NOT appear
      filter_state = {
          'show_damaged': True,
          'show_undamaged': True,
          'show_derelict': False,
          'show_destroyed': True,
      }
      result = filter_ships([ship], filter_state)
      assert len(result) == 0  # Should be excluded as derelict, not included as damaged
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

**Notes:** [Filled during implementation]

---

### Task 1.3: Add Combined Filter Test [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -k "combined"`

Add test for filter type interactions:

- [ ] Add `test_combined_status_and_capability_filter`:
  ```python
  def test_combined_status_and_capability_filter(self):
      """Filters from different types combine correctly (AND logic)."""
      # Create a damaged ship with warp capability
      ship = self._make_damaged_warp_capable_ship()

      # Test 1: Hide damaged - should exclude
      filter_state_no_damaged = {
          'show_damaged': False,
          'show_undamaged': True,
          'show_warp_capable': True,
          'show_not_warp_capable': True,
      }
      result = filter_ships([ship], filter_state_no_damaged)
      assert len(result) == 0

      # Test 2: Hide warp capable - should exclude
      filter_state_no_warp = {
          'show_damaged': True,
          'show_undamaged': True,
          'show_warp_capable': False,
          'show_not_warp_capable': True,
      }
      result = filter_ships([ship], filter_state_no_warp)
      assert len(result) == 0

      # Test 3: Show both - should include
      filter_state_show_both = {
          'show_damaged': True,
          'show_undamaged': True,
          'show_warp_capable': True,
          'show_not_warp_capable': True,
      }
      result = filter_ships([ship], filter_state_show_both)
      assert len(result) == 1
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

**Notes:** [Filled during implementation]

---

### Task 1.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify all tests pass (baseline: 6246 tests)
- [ ] No regressions from new tests

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
