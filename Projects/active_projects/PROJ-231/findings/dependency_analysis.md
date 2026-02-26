# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Callers

### Direct Callers (Production Code)

| File | Line | Usage |
|------|------|-------|
| `game/ui/screens/fleet_report_view_model.py` | 10 | Import: `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |
| `game/ui/screens/fleet_report_view_model.py` | 215 | Call: `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Summary:** There is exactly **one production caller** - `FleetListViewModel._refresh()`.

### Test Callers

| File | Test Class | Count |
|------|------------|-------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShips` | 5 tests |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsWarp` | 3 tests |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsSpaceyard` | 3 tests |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsCargo` | 6 tests |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestSpecialCapabilityFilter` | 3 tests |

**Total:** ~20 direct test invocations

---

## 2. `filter_state` Parameter Structure

The `filter_state` dictionary has the following keys, all with `bool` values:

### Core Status Filters
```python
{
    'show_damaged': bool,       # Include ships with damage
    'show_undamaged': bool,     # Include ships with full HP
    'show_derelict': bool,      # Include derelict ships
    'show_destroyed': bool,     # Include destroyed ships (default: False)
}
```

### Warp Capability Filters
```python
{
    'show_warp_capable': bool,      # Ships that can warp on their own
    'show_not_warp_capable': bool,  # Ships without warp capability
}
```

### Spaceyard Filters
```python
{
    'show_has_spaceyard': bool,  # Ships with spaceyard module
    'show_no_spaceyard': bool,   # Ships without spaceyard
}
```

### Cargo Filters
```python
{
    'show_has_cargo': bool,  # Ships with cargo > 0
    'show_no_cargo': bool,   # Ships with no cargo
}
```

### Special Capability Filters (Dynamically Generated)
Derived from `SPECIAL_CAPABILITY_COLUMNS` in `fleet_data_source.py`:
```python
{
    'show_can_destroy_planet': bool,
    'show_no_destroy_planet': bool,
    'show_can_open_warp': bool,
    'show_no_open_warp': bool,
    'show_can_close_warp': bool,
    'show_no_close_warp': bool,
    'show_can_destroy_star': bool,
    'show_no_destroy_star': bool,
    'show_can_create_sphere': bool,
    'show_no_create_sphere': bool,
}
```

### Default Behavior
- All filter keys default to `True` via `.get(key, True)` calls
- Missing keys are treated as "show all" (permissive default)
- Only `show_destroyed` defaults to `False` in `FleetListViewModel`

---

## 3. Interface Stability Assessment

### Signature Stability: **MEDIUM-LOW RISK**

**Reasons it CAN change:**
1. Only one production caller (`FleetListViewModel`)
2. The caller and callee are in the same package (`game.ui.screens`)
3. The caller controls the dictionary structure via `get_filter_state()`
4. Clear ownership - both files are part of the fleet report feature

**Reasons to be careful:**
1. ~20 tests directly call `filter_ships` with explicit dictionaries
2. Tests document the expected interface contract
3. Adding new filter keys is safe (default behavior handles missing keys)
4. Removing/renaming existing keys would break tests

### Recommended Approach for Changes

| Change Type | Risk | Action |
|-------------|------|--------|
| Add new filter key | Low | Add key to both `filter_ships` and `get_filter_state()` |
| Remove filter key | Medium | Update all tests, remove from both locations |
| Rename filter key | Medium | Update tests, `filter_ships`, and `get_filter_state()` |
| Change function signature | High | Must update `FleetListViewModel._refresh()` and all tests |
| Change return type | High | Would affect `FleetListViewModel` and sorting pipeline |

---

## 4. Side Effects Analysis

### Pure Function: **YES**

The `filter_ships` function:

1. **Does NOT mutate input list** - Creates new `result = []` list
2. **Does NOT mutate ships** - Only reads ship properties
3. **Does NOT mutate filter_state** - Only reads dictionary values
4. **No global state access** - No module-level mutable state
5. **No I/O operations** - No file, network, or database access
6. **Deterministic** - Same inputs always produce same outputs

### Internal Dependencies (Late Imports)

The function performs conditional late imports to avoid circular dependencies:

```python
# Line 159-160 (Spaceyard filter)
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
FleetCapabilityCalculator.ship_has_spaceyard(ship)

# Line 185-186 (Special capabilities)
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
```

These are **read-only** calls to external services.

### External Dependencies

| Dependency | Usage | Location |
|------------|-------|----------|
| `ShipStatsCalculator.has_warp_capability()` | Check warp ability | Line 149 |
| `FleetCapabilityCalculator.ship_has_spaceyard()` | Check spaceyard | Line 160 |
| `FleetCapabilityCalculator.ship_has_ability()` | Check special abilities | Line 186 |
| `SPECIAL_CAPABILITY_COLUMNS` | Ability mapping dict | Line 178 |

---

## 5. Test Coverage

### Test File
`tests/unit/ui/screens/test_fleet_report_filters.py`

### Coverage Summary

| Test Class | Focus Area | Tests |
|------------|------------|-------|
| `TestFilterShips` | Core status filters (damaged/undamaged/derelict/destroyed) | 5 |
| `TestFilterShipsWarp` | Warp capability filtering | 3 |
| `TestFilterShipsSpaceyard` | Spaceyard filtering (with mocks) | 3 |
| `TestFilterShipsCargo` | Cargo filtering | 6 |
| `TestSpecialCapabilityFilter` | Special ability filtering (with mocks) | 3 |

### Test Quality Assessment

**Strengths:**
- Each filter category has dedicated tests
- Tests verify both "hide" and "show" scenarios
- Edge cases covered (e.g., zero cargo treated as no cargo)
- Mocking used appropriately for external dependencies
- Tests are isolated and independent

**Gaps Identified:**
- No test for empty input list edge case
- No test for combinations of multiple filter types
- No performance/stress tests for large ship lists
- Integration with `FleetListViewModel` tested separately in `test_fleet_list_view_model.py`

### Related Tests

| File | Relevance |
|------|-----------|
| `tests/unit/ui/test_fleet_list_view_model.py` | Tests `FleetListViewModel` which calls `filter_ships` |
| `tests/unit/strategy/ship_stats/test_warp.py` | Tests warp capability calculation (dependency) |

---

## 6. Dependency Graph

```
fleet_report_view_model.py
    |
    +---> filter_ships() <--- fleet_report_filters.py
              |
              +---> ShipStatsCalculator.has_warp_capability()
              |         (game/strategy/services/ship_stats_calculator.py)
              |
              +---> FleetCapabilityCalculator.ship_has_spaceyard()
              |         (game/strategy/data/fleet_capability_calculator.py)
              |
              +---> FleetCapabilityCalculator.ship_has_ability()
              |         (game/strategy/data/fleet_capability_calculator.py)
              |
              +---> SPECIAL_CAPABILITY_COLUMNS
                        (game/ui/screens/fleet_data_source.py)
```

---

## 7. Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | 1 production caller, ~20 test calls |
| **Interface** | Dict-based config, extensible via defaults |
| **Mutability** | Pure function, no side effects |
| **Stability** | Safe to modify with coordinated updates |
| **Test Coverage** | Good coverage with minor gaps |
| **Dependencies** | 3 external service calls (read-only) |

### Refactoring Notes

1. The function is a good candidate for refactoring due to single production caller
2. Filter logic could be extracted into a `ShipFilter` class if complexity grows
3. The dynamic special capability filtering (lines 177-194) adds complexity
4. Consider breaking into smaller functions for each filter category
5. Cyclomatic complexity is moderate (~15-20) due to multiple filter branches
