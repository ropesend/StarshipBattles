# Phase 3: Refactor Main Function

**Goal:** Replace `filter_ships` implementation with predicate-based list comprehension.
**File:** `game/ui/screens/fleet_report_filters.py`

## Pre-Phase Verification
- [ ] Phase 2 complete (all helpers added and tested)
- [ ] Run baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Note: All tests should pass with original `filter_ships` + new helpers

## Tasks

### T3.1: Replace `filter_ships` Implementation
**Location:** `filter_ships` function (lines 124-222)

Replace the entire function body with:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with filter boolean flags (all default to True if missing):
            - show_damaged/show_undamaged/show_derelict/show_destroyed: Status filters
            - show_warp_capable/show_not_warp_capable: Warp capability
            - show_has_spaceyard/show_no_spaceyard: Spaceyard capability
            - show_has_cargo/show_no_cargo: Cargo filter
            - show_can_X/show_no_X: Special capability filters

    Returns:
        Filtered list of ships matching all enabled filter criteria.
    """
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

- [ ] Replace function body
- [ ] Keep docstring (update if needed)
- [ ] Run tests immediately after change

### T3.2: Verify Behavior Unchanged
- [ ] Run full filter test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] All 39+ original tests pass
- [ ] All Phase 1 new tests pass
- [ ] No test failures

### T3.3: Verify CC Reduction
- [ ] Run complexity check on `filter_ships`:
  ```bash
  python -c "from radon.complexity import cc_visit; import ast; code = open('game/ui/screens/fleet_report_filters.py').read(); print([f'{c.name}: {c.complexity}' for c in cc_visit(code) if c.name == 'filter_ships'])"
  ```
- [ ] Verify `filter_ships` CC is now 6 or below
- [ ] Document actual CC in this checklist: ____

## Post-Phase Verification
- [ ] `filter_ships` refactored to list comprehension
- [ ] All tests pass
- [ ] CC reduced from 36 to target (expected: 6)
- [ ] Update phase status in plan.md

## Rollback Plan
If tests fail after T3.1:
1. Revert the function body change
2. Review which test failed
3. Compare expected vs actual behavior
4. Check if helper functions have bugs
5. Fix helpers in Phase 2 before retrying

## Test Commands
```bash
# Full filter test suite
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Quick verification
pytest tests/unit/ui/screens/test_fleet_report_filters.py::TestFilterShips::test_filter_damaged_only -v

# Integration smoke test
pytest tests/unit/ui/screens/ -v -k "fleet_report"
```
