# Phase 3: Simplify Main Function

**Goal:** Refactor `filter_ships` to use the extracted helpers.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 3.1 Refactor filter_ships
- [ ] Replace `filter_ships` implementation with simplified version:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with boolean filter flags

      Returns:
          Filtered list of ships
      """
      result = []
      for ship in ships:
          # Capability filters
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_special_capability_filters(ship, filter_state):
              continue

          # Status filter (order handled internally)
          if not _passes_status_filter(ship, filter_state):
              continue

          result.append(ship)

      return result
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass

### 3.2 Verify Complexity Reduction
- [ ] Run complexity check: `radon cc game/ui/screens/fleet_report_filters.py -a -s`
- [ ] Verify `filter_ships` CC is now below 20
- [ ] Document new CC value in decisions.md

### 3.3 Full Test Suite
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All 6246+ tests pass

## Completion Criteria
- `filter_ships` refactored to use helpers
- CC reduced from 36 to target (<20)
- All tests pass
- Ready for Phase 4
