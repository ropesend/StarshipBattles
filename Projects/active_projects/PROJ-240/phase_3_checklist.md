# Phase 3: Refactor Main Function

> **Goal:** Refactor `filter_ships` to use extracted helpers, reducing CC from 36 to below 10.

## Pre-Conditions
- [ ] Phase 2 complete (all helpers extracted)
- [ ] All tests passing

## Tasks

### 3.1 Refactor `filter_ships` Function
**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222 (will become much shorter)

- [ ] Replace the entire function body with:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with keys:
              - show_damaged: Include damaged ships
              - show_undamaged: Include undamaged ships
              - show_derelict: Include derelict ships
              - show_destroyed: Include destroyed ships
              - show_warp_capable: Include warp-capable ships
              - show_not_warp_capable: Include ships without warp capability
              - show_has_spaceyard: Include ships with spaceyard
              - show_no_spaceyard: Include ships without spaceyard
              - show_has_cargo: Include ships with cargo
              - show_no_cargo: Include ships without cargo

      Returns:
          Filtered list of ships
      """
      result = []
      for ship in ships:
          # Capability filters (order preserved from original)
          if not _passes_warp_filter(ship, filter_state):
              continue
          if not _passes_spaceyard_filter(ship, filter_state):
              continue
          if not _passes_cargo_filter(ship, filter_state):
              continue
          if not _passes_special_capability_filters(ship, filter_state):
              continue
          # Status filter
          if not _passes_status_filter(ship, filter_state):
              continue
          result.append(ship)
      return result
  ```

- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Verify No Behavior Change
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass

### 3.3 Clean Up Unused Code
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Remove any commented-out old code
- [ ] Ensure no duplicate imports

## Verification
```bash
# Filter tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Integration tests
pytest tests/unit/ui/test_fleet_list_view_model.py -v

# Full suite
pytest tests/ -n 12
```

## Exit Criteria
- [ ] `filter_ships` reduced to ~20 lines
- [ ] All tests pass
- [ ] Commit: `[PROJ-240] Phase 3: Refactor filter_ships to use helpers`
