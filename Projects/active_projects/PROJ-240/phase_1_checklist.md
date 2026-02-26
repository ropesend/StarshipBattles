# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing edge case tests BEFORE any code changes to ensure safe refactoring.

---

## Tasks

### Task 1.1: Add Empty Input Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_ships_empty_list_returns_empty`:
  ```python
  def test_filter_ships_empty_list_returns_empty():
      """Empty ships list returns empty result."""
      result = filter_ships([], {'show_damaged': True})
      assert result == []
  ```

- [ ] Add `test_filter_ships_empty_filter_state_shows_all`:
  ```python
  def test_filter_ships_empty_filter_state_shows_all():
      """Empty filter_state dict uses defaults (show all)."""
      ships = [make_healthy_ship(), make_damaged_ship()]
      result = filter_ships(ships, {})
      assert len(result) == len(ships)
  ```

- [ ] Verify: Tests pass

---

### Task 1.2: Add Combined Filter Tests [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_combined_hide_damaged_and_hide_non_warp`:
  - Create 4 ships: healthy warp, healthy non-warp, damaged warp, damaged non-warp
  - Filter with `show_damaged=False` AND `show_not_warp_capable=False`
  - Assert only healthy warp ships remain

- [ ] Add `test_filter_all_status_filters_false_returns_empty`:
  ```python
  def test_filter_all_status_filters_false_returns_empty():
      """All status filters False returns empty list."""
      ships = [make_healthy_ship(), make_damaged_ship()]
      result = filter_ships(ships, {
          'show_damaged': False,
          'show_undamaged': False,
          'show_derelict': False,
          'show_destroyed': False
      })
      assert result == []
  ```

- [ ] Verify: Tests pass

---

### Task 1.3: Add Edge Case Tests [Simple]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] Add `test_filter_unknown_keys_ignored`:
  ```python
  def test_filter_unknown_keys_ignored():
      """Unknown keys in filter_state are ignored."""
      ships = [make_healthy_ship()]
      result = filter_ships(ships, {'show_unknown_filter': False})
      assert len(result) == 1
  ```

- [ ] Add `test_filter_cargo_with_none_cargo_contents` (if cargo_contents can be None):
  - Create ship with `cargo_contents = None`
  - Filter with `show_no_cargo=True, show_has_cargo=False`
  - Assert ship passes (None treated as no cargo)

- [ ] Verify: Tests pass

---

### Task 1.4: Run Full Test Suite [Simple]
**Command:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

- [ ] All new tests pass
- [ ] All existing tests still pass
- [ ] No test regressions

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Commit: `[PROJ-240] Phase 1: Add edge case tests for filter_ships`
