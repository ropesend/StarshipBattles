# Phase 3: Refactor Main Function

**Goal:** Refactor `filter_ships` to use the extracted helper functions.

**Target file:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 3.1 Refactor `filter_ships` to use helpers
- [ ] Replace inline filter logic with calls to helper functions
- [ ] Convert to list comprehension
- [ ] Keep docstring and type hints

**Before (99 lines):**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """..."""
    result = []
    for ship in ships:
        # ... 80+ lines of filter logic
    return result
```

**After (~15 lines):**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with filter keys (all default to True if missing)

    Returns:
        Filtered list of ships matching all active filters
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

### 3.2 Run all filter tests
- [ ] Run `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify ALL tests pass (including new edge case tests from Phase 1)
- [ ] If any fail, debug and fix

### 3.3 Run full test suite
- [ ] Run `pytest tests/ -n 12`
- [ ] Verify no regressions in other test files
- [ ] If failures, check `test_fleet_list_view_model.py` specifically

### 3.4 Verify CC reduction
- [ ] Run complexity check on `filter_ships`
- [ ] Verify main function CC is now < 10
- [ ] Document actual CC achieved

```bash
python -m radon cc game/ui/screens/fleet_report_filters.py -s -a
```

---

## Completion Criteria
- [ ] `filter_ships` refactored to use helpers
- [ ] All filter tests pass
- [ ] Full test suite passes
- [ ] CC of `filter_ships` verified < 20 (target: < 10)
- [ ] Commit: `[PROJ-234] Phase 3: Refactor filter_ships to use helper predicates`
