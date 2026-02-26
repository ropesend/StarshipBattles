# Phase 3: Simplify Main Function

> **Goal:** Refactor `filter_ships` to use extracted predicates and simplify `sort_ships`.

## Pre-Phase Checklist
- [ ] Phase 2 complete (all helpers added)
- [ ] All tests passing: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 3.1 Refactor `filter_ships` to Use Predicates
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 124-222 (the `filter_ships` function)

- [ ] Replace entire function body with:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with filter keys (all default to True if missing):
              - show_damaged: Include damaged ships
              - show_undamaged: Include undamaged ships
              - show_derelict: Include derelict ships
              - show_destroyed: Include destroyed ships
              - show_warp_capable: Include warp-capable ships
              - show_not_warp_capable: Include ships without warp capability
              - show_has_spaceyard: Include ships with spaceyard
              - show_no_spaceyard: Include ships without spaceyard
              - show_has_cargo: Include ships carrying cargo
              - show_no_cargo: Include ships with no cargo
              (plus special capability filters via SPECIAL_CAPABILITY_COLUMNS)

      Returns:
          Filtered list of ships
      """
      return [
          ship for ship in ships
          if _passes_warp_filter(ship, filter_state)
          and _passes_spaceyard_filter(ship, filter_state)
          and _passes_cargo_filter(ship, filter_state)
          and _passes_special_capability_filters(ship, filter_state)
          and _passes_status_filter(ship, filter_state)
      ]
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`

### 3.2 Update `sort_ships` to Use `_classify_ship_status`
**File:** `game/ui/screens/fleet_report_filters.py`
**Location:** Lines 251-258 inside `get_sort_key` in `sort_ships`

- [ ] Find the status sorting block:
  ```python
  elif sort_column == 'status':
      # Sort by severity: OK=0, DAMAGED=1, DERELICT=2, DESTROYED=3
      if not ship.is_alive:
          return 3
      elif ship.is_derelict:
          return 2
      elif ship.is_damaged():
          return 1
      return 0
  ```
- [ ] Replace with:
  ```python
  elif sort_column == 'status':
      # Sort by severity: undamaged=0, damaged=1, derelict=2, destroyed=3
      status_order = {'undamaged': 0, 'damaged': 1, 'derelict': 2, 'destroyed': 3}
      return status_order[_classify_ship_status(ship)]
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Post-Phase Checklist
- [ ] `filter_ships` simplified to list comprehension
- [ ] `sort_ships` uses shared `_classify_ship_status`
- [ ] All tests pass: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Commit: `git commit -m "[PROJ-247] Phase 3: Simplify filter_ships using extracted predicates"`
