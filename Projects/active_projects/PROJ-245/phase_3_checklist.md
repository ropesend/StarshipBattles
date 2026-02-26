# Phase 3: Simplify Main Function

> Convert `filter_ships` to use the extracted predicates via list comprehension.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 3.1 Replace Loop with List Comprehension
- [ ] Replace the entire for-loop body (lines 142-220) with:
```python
return [
    ship for ship in ships
    if _passes_warp_filter(ship, filter_state)
    and _passes_spaceyard_filter(ship, filter_state)
    and _passes_cargo_filter(ship, filter_state)
    and _passes_special_capability_filter(ship, filter_state)
    and _passes_status_filter(ship, filter_state)
]
```
- [ ] Remove the `result = []` initialization
- [ ] Remove the `return result` at the end
- [ ] Verify function is now ~15 lines (docstring + signature + comprehension)

### 3.2 Clean Up Imports
- [ ] Remove any imports that are now only used in helpers (if moved inside helpers)
- [ ] Verify `ShipStatsCalculator` import stays at module level (used by `_passes_warp_filter`)

### 3.3 Verify Behavior
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All tests pass (including new edge case tests from Phase 1)
- [ ] Run: `pytest tests/ --testmon`

### 3.4 Measure Complexity
- [ ] Run complexity check on `filter_ships`:
```bash
python -c "from radon.complexity import cc_visit; import ast; code=open('game/ui/screens/fleet_report_filters.py').read(); print([f'{f.name}: {f.complexity}' for f in cc_visit(code)])"
```
- [ ] Verify `filter_ships` CC is now < 5
- [ ] Verify all helpers are < 10 CC each

## Verification
```bash
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
pytest tests/ -n 12 --tb=short
```

## Exit Criteria
- [ ] `filter_ships` is now a simple list comprehension
- [ ] All tests passing
- [ ] `filter_ships` CC < 5
- [ ] All helper functions CC < 10
