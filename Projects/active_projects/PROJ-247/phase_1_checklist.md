# Phase 1: Test Fortification

> **Goal:** Add missing test coverage before any code changes to establish a safety net.

## Pre-Phase Checklist
- [ ] Read existing tests: `tests/unit/ui/screens/test_fleet_report_filters.py`
- [ ] Understand mock patterns used in existing tests
- [ ] Run baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 1.1 Empty Ship List Test
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add to `TestFilterShips` class

- [ ] Add test `test_filter_empty_list_returns_empty`
  ```python
  def test_filter_empty_list_returns_empty(self):
      """Empty ship list should return empty list regardless of filter state."""
      result = filter_ships([], {'show_damaged': True, 'show_undamaged': True})
      assert result == []
  ```
- [ ] Run test: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_empty_list_returns_empty -v`

### 1.2 All Filters Disabled Test
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add to `TestFilterShips` class

- [ ] Add test `test_filter_all_disabled_returns_empty`
  ```python
  def test_filter_all_disabled_returns_empty(self):
      """All status filters disabled should return empty list."""
      ships = [self._create_ship(damaged=False)]  # One healthy ship
      filter_state = {
          'show_damaged': False,
          'show_undamaged': False,
          'show_derelict': False,
          'show_destroyed': False,
      }
      result = filter_ships(ships, filter_state)
      assert result == []
  ```
- [ ] Run test: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_all_disabled_returns_empty -v`

### 1.3 Status Priority Test (Derelict vs Damaged)
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add to `TestFilterShips` class

- [ ] Add test `test_derelict_not_matched_by_damaged_filter`
  ```python
  def test_derelict_not_matched_by_damaged_filter(self):
      """Derelict ships should NOT be included when show_derelict=False even if show_damaged=True.

      This tests the critical status hierarchy: destroyed > derelict > damaged > undamaged.
      A derelict ship is technically damaged, but should only match the derelict filter.
      """
      derelict_ship = self._create_ship(damaged=True, derelict=True)
      filter_state = {
          'show_damaged': True,
          'show_undamaged': True,
          'show_derelict': False,  # Hide derelict
          'show_destroyed': True,
      }
      result = filter_ships([derelict_ship], filter_state)
      assert result == []  # Derelict should be excluded, not caught by damaged filter
  ```
- [ ] Run test: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_derelict_not_matched_by_damaged_filter -v`

### 1.4 Combined Filter Test (Multiple Categories)
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add new test class `TestFilterShipsCombined`

- [ ] Add test class and test `test_combined_warp_and_status_filters`
  ```python
  class TestFilterShipsCombined:
      """Tests for combined filter behavior across multiple categories."""

      def test_combined_warp_and_status_filters(self):
          """Ship must pass ALL filter categories (AND semantics)."""
          # Create warp-capable damaged ship
          ship = MagicMock(spec=ShipInstance)
          ship.is_alive = True
          ship.is_derelict = False
          ship.is_damaged.return_value = True
          ship.cargo_contents = {}

          with patch.object(ShipStatsCalculator, 'has_warp_capability', return_value=True):
              # Hide warp-capable ships - should exclude even though damaged filter allows
              filter_state = {
                  'show_warp_capable': False,
                  'show_not_warp_capable': True,
                  'show_damaged': True,
              }
              result = filter_ships([ship], filter_state)
              assert result == []

              # Now allow warp-capable - should include
              filter_state['show_warp_capable'] = True
              result = filter_ships([ship], filter_state)
              assert len(result) == 1
  ```
- [ ] Run test: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombined -v`

### 1.5 Partial Filter State Test (Missing Keys Default to True)
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Location:** Add to `TestFilterShipsCombined` class

- [ ] Add test `test_missing_filter_keys_default_to_true`
  ```python
  def test_missing_filter_keys_default_to_true(self):
      """Missing filter_state keys should default to True (show)."""
      ship = MagicMock(spec=ShipInstance)
      ship.is_alive = True
      ship.is_derelict = False
      ship.is_damaged.return_value = False  # Healthy ship
      ship.cargo_contents = {}

      with patch.object(ShipStatsCalculator, 'has_warp_capability', return_value=True):
          # Empty filter state - all defaults to True
          result = filter_ships([ship], {})
          assert len(result) == 1

          # Partial filter state - only specify one key
          result = filter_ships([ship], {'show_damaged': True})
          assert len(result) == 1
  ```
- [ ] Run test: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCombined::test_missing_filter_keys_default_to_true -v`

## Post-Phase Checklist
- [ ] All new tests pass: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Full test suite still passes: `pytest tests/ -n 12`
- [ ] Commit: `git commit -m "[PROJ-247] Phase 1: Add test fortification for filter_ships refactoring"`

## Test Commands
```bash
# Run all filter tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Run specific test class
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v

# Run single test
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_empty_list_returns_empty -v
```
