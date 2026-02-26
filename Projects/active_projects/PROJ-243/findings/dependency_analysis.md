# Dependency Analysis: `filter_ships` Function

**Target File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of filter flags. It is a **pure function** that takes inputs and returns a new filtered list without modifying the input.

### Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

### Parameters
- `ships`: List of `ShipInstance` objects to filter
- `filter_state`: Dictionary with boolean flags for each filter category:
  - `show_damaged` - Include damaged ships
  - `show_undamaged` - Include undamaged ships
  - `show_derelict` - Include derelict ships
  - `show_destroyed` - Include destroyed ships
  - `show_warp_capable` - Include warp-capable ships
  - `show_not_warp_capable` - Include ships without warp capability
  - `show_has_spaceyard` - Include ships with spaceyard
  - `show_no_spaceyard` - Include ships without spaceyard
  - `show_has_cargo` - Include ships carrying cargo
  - `show_no_cargo` - Include ships with no cargo
  - `show_can_destroy_planet` / `show_no_destroy_planet` - Planet destruction capability filter
  - `show_can_open_warp` / `show_no_open_warp` - Warp point opening capability filter
  - `show_can_close_warp` / `show_no_close_warp` - Warp point closing capability filter
  - `show_can_destroy_star` / `show_no_destroy_star` - Star destruction capability filter
  - `show_can_create_sphere` / `show_no_create_sphere` - Sphere world creation capability filter

### Return Value
- Returns a new `List[ShipInstance]` containing only ships that pass all enabled filters.

---

## 2. Callers

### 2.1 Production Code Callers

| File | Import | Usage |
|------|--------|-------|
| `game/ui/screens/fleet_report_view_model.py` | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` | Called in `_refresh()` method |

**Usage in `FleetListViewModel._refresh()`:**
```python
def _refresh(self) -> None:
    """Refresh the filtered/sorted ship list."""
    # Apply filters
    filtered = filter_ships(self._ships, self.get_filter_state())

    # Apply sort
    self._filtered_ships = sort_ships(
        filtered,
        self.sort_column_id,
        self.sort_descending
    )
    self._needs_refresh = False
```

The view model:
1. Maintains internal filter state as instance attributes (e.g., `filter_show_damaged`)
2. Converts state to dict via `get_filter_state()` method
3. Passes ship list and state dict to `filter_ships`
4. Chains result to `sort_ships` for ordering
5. Caches result to avoid repeated filtering

### 2.2 Test File Callers

| File | Test Classes |
|------|--------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShips`, `TestFilterShipsWarp`, `TestFilterShipsSpaceyard`, `TestFilterShipsCargo`, `TestSpecialCapabilityFilter` |
| `tests/unit/ui/test_fleet_list_view_model.py` | `TestFleetListViewModel` (indirect - tests the view model which calls `filter_ships`) |

---

## 3. Dependencies (What `filter_ships` Calls)

### 3.1 Internal Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `ShipStatsCalculator.has_warp_capability(ship)` | External service | Determine if ship can perform warp jumps |
| `FleetCapabilityCalculator.ship_has_spaceyard(ship)` | External service | Determine if ship has spaceyard |
| `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` | External service | Check for special abilities |
| `SPECIAL_CAPABILITY_COLUMNS` | Module constant | Maps column IDs to ability names |

### 3.2 Ship Instance Properties/Methods Accessed

| Property/Method | Purpose |
|-----------------|---------|
| `ship.is_alive` | Check if ship is not destroyed |
| `ship.is_derelict` | Check if ship is derelict |
| `ship.is_damaged()` | Check if ship has any damage |
| `ship.cargo_contents` | Access cargo dictionary for cargo filtering |

### 3.3 Late Imports (Intentional)

The function uses late imports within the loop body to avoid circular dependencies:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

These imports happen:
- Only when the relevant filter is active (optimization)
- Inside the ship iteration loop (executed once per ship that needs capability check)

---

## 4. Side Effects and State Mutations

### 4.1 Side Effects: **NONE**

The function is a **pure function**:
- Does not modify the input `ships` list
- Does not modify the input `filter_state` dict
- Does not modify any ship objects
- Creates and returns a new list
- No I/O operations
- No global state access or modification

### 4.2 State Mutations: **NONE**

- Input list is iterated, not modified
- Input dict is read via `.get()`, not modified
- Ship properties are read-only accessed

---

## 5. Interface Stability Assessment

### 5.1 Can the Interface Change?

**Signature stability: MODERATE**

| Aspect | Assessment |
|--------|------------|
| Parameter types | Stable - `List[ShipInstance]` and `Dict[str, bool]` are fundamental |
| Parameter names | Stable - changing would break keyword args |
| Return type | Stable - `List[ShipInstance]` is expected everywhere |
| Filter keys | **Extensible** - new keys can be added without breaking callers |

### 5.2 Backward Compatibility Considerations

**Adding new filters**: SAFE
- Function uses `filter_state.get(key, True)` pattern
- Missing keys default to `True` (show all)
- Callers not aware of new filters will see all ships (expected behavior)

**Removing existing filters**: RISKY
- Callers may explicitly set removed filters
- Would cause KeyError if code doesn't use `.get()` pattern
- `FleetListViewModel` explicitly sets all known filters

**Changing filter semantics**: RISKY
- Tests verify current behavior extensively
- UI labels correspond to filter meanings

### 5.3 Recommendations for Interface Changes

1. **New filters**: Add with default `True` behavior for backward compatibility
2. **Renamed filters**: Use deprecation period - support old and new key names
3. **Remove filters**: Update all callers first, then remove from function
4. **Change behavior**: Update all tests first, then modify implementation

---

## 6. Test Coverage Analysis

### 6.1 Direct Test Coverage

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

| Test Class | Test Count | Coverage Area |
|------------|------------|---------------|
| `TestFilterShips` | 5 tests | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 3 tests | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 tests | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 6 tests | Cargo filtering including edge cases |
| `TestSpecialCapabilityFilter` | 3 tests | Special ability filtering (DestroyPlanet, etc.) |

**Total direct tests: 20**

### 6.2 Test Categories

1. **Filter show all** - All filters enabled passes all ships
2. **Filter hide specific** - Each filter type hides matching ships
3. **Default behavior** - Missing filter keys default to showing all
4. **Edge cases** - Zero-value cargo treated as no cargo

### 6.3 Indirect Test Coverage

**File:** `tests/unit/ui/test_fleet_list_view_model.py`

Tests the `FleetListViewModel` which calls `filter_ships` internally:
- `TestFleetListViewModel` - 16 tests covering filter toggling and results
- `TestFleetListViewModelWarpFilters` - 2 tests for warp filter state
- `TestFleetListViewModelSpaceyardFilters` - 5 tests for spaceyard filter state
- `TestFleetListViewModelCargoFilters` - 5 tests for cargo filter state

### 6.4 Coverage Gaps

| Gap | Risk Level | Notes |
|-----|------------|-------|
| Combined filter combinations | LOW | Individual filters tested, combinations implicit |
| Order preservation | LOW | Function iterates in order, tests verify counts |
| Performance with large lists | LOW | Pure iteration, O(n) complexity |
| Empty ship list | LOW | Would return empty list |

---

## 7. Summary

### Key Findings

1. **Single Production Caller**: `FleetListViewModel._refresh()` is the only production code caller
2. **Pure Function**: No side effects, no state mutations, returns new list
3. **Extensible Interface**: New filters can be added without breaking callers
4. **Comprehensive Tests**: 20 direct tests + 28 indirect tests cover the function well
5. **Late Imports**: Uses intentional late imports to avoid circular dependencies

### Refactoring Considerations

| Consideration | Assessment |
|---------------|------------|
| Safe to modify implementation | YES - pure function with good test coverage |
| Safe to add parameters | YES - use defaults for backward compatibility |
| Safe to change signature | MODERATE - only one caller, but update tests |
| Safe to rename | LOW - would need to update import in view model and tests |

### Complexity Indicators

- Function length: ~100 lines
- Cyclomatic complexity: HIGH (many conditional branches for each filter type)
- Nesting depth: 3 levels (for loop > if checks > continue)
- Parameter count: 2 (reasonable)

The function is a candidate for refactoring to reduce cyclomatic complexity, potentially by extracting individual filter predicates into separate functions or using a more declarative filter configuration approach.
