# Phase 3: Simplify Main Function

**Goal:** Rewrite `filter_ships` using the extracted helpers to reduce complexity.

**File:** `game/ui/screens/fleet_report_filters.py`

## Prerequisites
- [ ] Phase 2 complete (all helpers extracted)
- [ ] All tests passing

## Tasks

### 3.1 Rewrite `filter_ships` using helpers
- [ ] Replace the entire body of `filter_ships` (lines ~141-222) with:
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

      Returns:
          Filtered list of ships
      """
      return [
          ship for ship in ships
          if _passes_capability_filters(ship, filter_state)
          and _passes_status_filter(ship, filter_state)
      ]
  ```
- [ ] Preserve the existing docstring exactly
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Verify all filter behaviors preserved
- [ ] Run all filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run view model tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Verify warp filtering works
- [ ] Verify spaceyard filtering works
- [ ] Verify cargo filtering works
- [ ] Verify special capability filtering works
- [ ] Verify status filtering works

### 3.3 Run integration tests
- [ ] Run: `pytest tests/unit/ui/ -v --tb=short`
- [ ] Check for any failures in related tests

### 3.4 Measure complexity reduction
- [ ] Run complexity check on the refactored function:
  ```bash
  python -c "
  from radon.complexity import cc_visit
  with open('game/ui/screens/fleet_report_filters.py') as f:
      code = f.read()
  for item in cc_visit(code):
      if 'filter_ships' in item.name or item.name.startswith('_passes') or item.name.startswith('_get'):
          print(f'{item.name}: CC={item.complexity}')
  "
  ```
- [ ] Verify `filter_ships` CC is below 20
- [ ] Record new CC values for all functions

## Completion Criteria
- [ ] `filter_ships` rewritten using list comprehension
- [ ] All tests pass
- [ ] CC of `filter_ships` below 20
- [ ] No behavioral changes detected

## Test Commands
```bash
# Quick check
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Broader check
pytest tests/unit/ui/ -v --tb=short

# Full suite (before committing)
pytest tests/ -n 12 --tb=short
```
