# Phase 3: Extract Status Classification

**Objective:** Create `_get_ship_status()` helper to classify ships into destroyed/derelict/damaged/undamaged categories, and simplify the status filter chain.

**Expected CC Reduction:** From ~20 to ~16

---

## Prerequisites
- [ ] Phase 2 complete (binary filter helper in place)
- [ ] Run baseline tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

---

## Tasks

### 3.1 Create Status Classification Helper

**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Add BEFORE `filter_ships` function (after `_passes_binary_filter`)

- [ ] **Add `_get_ship_status()` function**
  ```python
  def _get_ship_status(ship: ShipInstance) -> str:
      """Classify ship into one of four status categories.

      CRITICAL: Order matters! A ship is classified into exactly ONE category
      using this precedence:
      1. destroyed (not is_alive) - takes precedence over all
      2. derelict - takes precedence over damaged
      3. damaged
      4. undamaged (fallthrough)

      Args:
          ship: The ship to classify

      Returns:
          One of: 'destroyed', 'derelict', 'damaged', 'undamaged'
      """
      if not ship.is_alive:
          return 'destroyed'
      if ship.is_derelict:
          return 'derelict'
      if ship.is_damaged():
          return 'damaged'
      return 'undamaged'
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Refactor Status Filter Chain

**Lines:** ~196-220 in `filter_ships` (after capability filters)

- [ ] **Replace status filter chain with helper call**

  Replace the entire block:
  ```python
  # Destroyed filter
  if not ship.is_alive:
      if not filter_state.get('show_destroyed', True):
          continue
      result.append(ship)
      continue

  # Derelict filter ...
  # Damaged filter ...
  # Undamaged ...
  ```

  With:
  ```python
  # Status filter
  status = _get_ship_status(ship)
  if not filter_state.get(f'show_{status}', True):
      continue
  result.append(ship)
  ```

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`

### 3.3 Verify Edge Cases

- [ ] Run the edge case tests added in Phase 1:
  ```
  pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_destroyed_derelict_ship_classified_as_destroyed -v
  pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_derelict_damaged_ship_classified_as_derelict -v
  ```
- [ ] Verify status classification order is preserved

---

## Verification

- [ ] Run full filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run view model tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Run `pytest tests/ --testmon` for broader regression check

---

## Completion Criteria

- [ ] `_get_ship_status()` helper created with correct ordering
- [ ] Status filter chain simplified to single lookup
- [ ] All tests passing including edge case tests
- [ ] Status classification precedence preserved
