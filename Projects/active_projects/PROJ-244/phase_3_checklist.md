# Phase 3: Simplify Main Function

**Goal:** Clean up `filter_ships` to use extracted helpers, ensuring clear coordination logic.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 3.1 Verify Main Function Structure
After Phase 2, `filter_ships` should look approximately like:
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

- [ ] Verify the function matches this structure
- [ ] Ensure no leftover code from original implementation
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Optional: Consolidate to Capability Filter
If desired, consolidate capability filters into one call:
- [ ] Add `_passes_capability_filters()` that calls warp, spaceyard, cargo, and special:
  ```python
  def _passes_capability_filters(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all capability filters."""
      if not _passes_warp_filter(ship, filter_state):
          return False
      if not _passes_spaceyard_filter(ship, filter_state):
          return False
      if not _passes_cargo_filter(ship, filter_state):
          return False
      if not _passes_special_capability_filters(ship, filter_state):
          return False
      return True
  ```
- [ ] Simplify main function to:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      result = []
      for ship in ships:
          if not _passes_capability_filters(ship, filter_state):
              continue
          if not _passes_status_filter(ship, filter_state):
              continue
          result.append(ship)
      return result
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.3 Update Docstring
- [ ] Update `filter_ships` docstring to reflect simplified implementation
- [ ] Ensure docstring still documents all filter keys for API reference

## Completion Criteria
- [ ] Main function is clean and coordinating
- [ ] All tests passing
- [ ] Docstring updated
