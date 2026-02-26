# Phase 3: Simplify Main Function

**Objective:** Refactor `filter_ships` to use extracted helpers, reducing cyclomatic complexity.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 3.1 Refactor `filter_ships` to Use Helpers
- [ ] Replace lines 143-153 (warp filter) with call to `_passes_warp_filter(ship, filter_state)`
- [ ] Replace lines 155-164 (spaceyard filter) with call to `_passes_spaceyard_filter(ship, filter_state, FleetCapabilityCalculator)`
- [ ] Replace lines 166-174 (cargo filter) with call to `_passes_cargo_filter(ship, filter_state)`
- [ ] Replace lines 176-194 (special capabilities) with call to `_passes_special_capabilities_filter(ship, filter_state, FleetCapabilityCalculator)`
- [ ] Replace lines 196-220 (status filters) with call to `_passes_status_filter(ship, filter_state)`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Simplify Main Loop Structure
- [ ] Refactor main function to simplified form:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """Filter ships based on status filter state."""
      # Late import to avoid circular dependency
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

      result = []
      for ship in ships:
          # Capability filters
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state, FleetCapabilityCalculator):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_special_capabilities_filter(ship, filter_state, FleetCapabilityCalculator):
              continue

          # Status filter
          if not _passes_status_filter(ship, filter_state):
              continue

          result.append(ship)

      return result
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.3 Verify All Filter Tests Pass
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips -v`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsWarp -v`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsSpaceyard -v`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShipsCargo -v`
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestSpecialCapabilityFilter -v`

### 3.4 Verify Integration Tests
- [ ] Run: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Verify all view model tests pass

---

## Completion Criteria

- [ ] `filter_ships` function uses all helper functions
- [ ] Main function significantly simplified
- [ ] All tests pass
- [ ] No behavioral changes (pure refactoring)
