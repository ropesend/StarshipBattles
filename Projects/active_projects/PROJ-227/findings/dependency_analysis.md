# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`

**Function Signature:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

---

## 1. All Callers of `filter_ships`

### Production Code Callers

| File | Location | Usage |
|------|----------|-------|
| `game/ui/screens/fleet_report_view_model.py` | Line 10 (import), Line 215 (call) | Main consumer - the `FleetListViewModel._refresh()` method |

**Call Site Details:**

```python
# fleet_report_view_model.py line 215
filtered = filter_ships(self._ships, self.get_filter_state())
```

The `FleetListViewModel` is the **sole production caller**. It:
1. Imports `filter_ships` at module level (line 10)
2. Calls it in the private `_refresh()` method (line 215)
3. Passes the internal `_ships` list and a filter state dict built by `get_filter_state()`

### Test Code Callers

| File | Description |
|------|-------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Comprehensive direct tests of `filter_ships` |
| `tests/unit/ui/test_fleet_list_view_model.py` | Tests `FleetListViewModel` which internally uses `filter_ships` |

**Note:** `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` appeared in grep results but does NOT actually use `filter_ships` - it tests a separate `BuildQueueFilterManager` class.

---

## 2. Parameters and Return Value Usage

### Input Parameters

**`ships: List[ShipInstance]`**
- Source: `FleetListViewModel._ships` (internal list managed by the view model)
- The list is set via constructor or `update_ships()` method
- No mutation occurs - the input list is iterated, not modified

**`filter_state: Dict[str, bool]`**
- Built by `FleetListViewModel.get_filter_state()` method
- Expected keys:
  ```python
  {
      'show_damaged': bool,
      'show_undamaged': bool,
      'show_derelict': bool,
      'show_destroyed': bool,
      'show_warp_capable': bool,
      'show_not_warp_capable': bool,
      'show_has_spaceyard': bool,
      'show_no_spaceyard': bool,
      'show_has_cargo': bool,
      'show_no_cargo': bool,
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
- Missing keys are handled gracefully via `filter_state.get(key, True)` (defaults to showing)

### Return Value

**`List[ShipInstance]`**
- A NEW list (not mutating input)
- Contains ships that passed all filter criteria
- Order preserved from input list
- Used by `FleetListViewModel._refresh()` which then passes it to `sort_ships()`

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**YES, with moderate effort.** The function has a narrow, well-defined interface:

| Aspect | Stability | Notes |
|--------|-----------|-------|
| Function name | Can change | Only 1 production caller + tests |
| Return type | Stable | Must return `List[ShipInstance]` |
| Parameter types | Stable | `List[ShipInstance]` and `Dict[str, bool]` expected |
| Filter key names | Coupled | Keys must match `FleetListViewModel.get_filter_state()` |

**Coupling Points:**
1. `FleetListViewModel.get_filter_state()` must produce dict keys that match what `filter_ships` expects
2. The `SPECIAL_CAPABILITY_COLUMNS` constant from `fleet_data_source.py` defines special capability filter keys
3. Late imports inside `filter_ships` depend on:
   - `game.strategy.services.ship_stats_calculator.ShipStatsCalculator`
   - `game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator`

**Breaking Changes Would Require:**
- Update `FleetListViewModel._refresh()` (trivial - same file boundary)
- Update `FleetListViewModel.get_filter_state()` if filter keys change
- Update all tests in `test_fleet_report_filters.py`

---

## 4. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** with respect to its inputs:
- Does not modify the input `ships` list
- Does not modify the input `filter_state` dict
- Does not modify any `ShipInstance` objects
- Creates and returns a new list

### State Dependencies (Read-Only)

The function reads from `ShipInstance` objects:
- `ship.is_alive` - property
- `ship.is_derelict` - property
- `ship.is_damaged()` - method call
- `ship.cargo_contents` - dict attribute

### Late Imports (Executed Per-Call When Filters Active)

```python
# Lines 159, 185: Only imported when spaceyard/special capability filters are active
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

# Line 149: Only used when warp filters differ
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator  # (via module-level import)
```

**Performance Note:** `ShipStatsCalculator` is imported at module level (line 12), but `FleetCapabilityCalculator` is imported inside the loop when needed. This is intentional to avoid circular imports.

---

## 5. Test Coverage

### Direct Tests: `tests/unit/ui/screens/test_fleet_report_filters.py`

**Test Classes Covering `filter_ships`:**

| Class | Coverage |
|-------|----------|
| `TestFilterShips` | Basic filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | Warp capability filtering |
| `TestFilterShipsSpaceyard` | Spaceyard capability filtering |
| `TestFilterShipsCargo` | Cargo presence filtering |
| `TestSpecialCapabilityFilter` | Special abilities (destroy planet, open warp, etc.) |

**Test Count:** ~25 direct tests of `filter_ships`

### Indirect Tests: `tests/unit/ui/test_fleet_list_view_model.py`

| Class | Coverage |
|-------|----------|
| `TestFleetListViewModel` | Integration with view model |
| `TestFleetListViewModelWarpFilters` | Warp filter toggle behavior |
| `TestFleetListViewModelSpaceyardFilters` | Spaceyard filter toggle behavior |
| `TestFleetListViewModelCargoFilters` | Cargo filter toggle behavior |

**Test Count:** ~30 tests exercising `filter_ships` through the view model

### Coverage Assessment

| Filter Type | Direct Tests | Integration Tests |
|-------------|--------------|-------------------|
| Damaged/Undamaged | Yes | Yes |
| Derelict | Yes | Yes |
| Destroyed | Yes | Yes |
| Warp Capable | Yes | Yes |
| Spaceyard | Yes | Yes |
| Cargo | Yes | Yes |
| Special Capabilities | Yes | Yes |
| Default (all True) | Yes | Yes |
| Combined Filters | Partial | Yes |

**Coverage is COMPREHENSIVE** - all filter types have both unit and integration tests.

---

## 6. Summary

| Aspect | Finding |
|--------|---------|
| **Production Callers** | 1 (`FleetListViewModel._refresh()`) |
| **Test Callers** | ~55 tests across 2 test files |
| **Interface Stability** | Moderate - can change with coordinated updates |
| **Side Effects** | None - pure function |
| **State Mutations** | None |
| **Test Coverage** | Comprehensive |
| **Complexity Drivers** | Many filter types in single function (22+ filter keys), late imports, nested conditionals |

### Refactoring Recommendations

1. **Safe to refactor internally** - single production caller makes API changes feasible
2. **Filter state dict is the contract** - any changes must coordinate with `FleetListViewModel.get_filter_state()`
3. **Tests provide safety net** - comprehensive coverage enables confident refactoring
4. **Consider extracting filter predicates** - the function has high cyclomatic complexity due to many filter types; extracting individual filter functions would improve testability and maintainability
