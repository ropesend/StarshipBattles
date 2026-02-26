# Dependency Analysis: `filter_ships` Function

## Summary

The `filter_ships` function in `fleet_report_filters.py` is a **pure, side-effect-free** filtering function with a single caller. The interface is **internally stable** (only called by the view model within the same UI module), allowing refactoring flexibility.

---

## Function Location

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36 (high - target for refactoring)

---

## Function Signature

```python
def filter_ships(
    ships: List[ShipInstance],
    filter_state: Dict[str, bool]
) -> List[ShipInstance]:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ships` | `List[ShipInstance]` | Input list of ship instances to filter |
| `filter_state` | `Dict[str, bool]` | Dictionary of boolean filter flags |

### Return Value

Returns a new `List[ShipInstance]` containing ships that pass all filter criteria. The original list is **not modified**.

---

## Callers Analysis

### Single Caller: `FleetListViewModel._refresh()`

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`

**Import Statement (line 10):**
```python
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
```

**Call Site (line 215):**
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

### How Parameters Are Constructed

The `filter_state` dictionary is built by `FleetListViewModel.get_filter_state()` (lines 171-199):

```python
def get_filter_state(self) -> Dict[str, bool]:
    return {
        'show_damaged': self.filter_show_damaged,
        'show_undamaged': self.filter_show_undamaged,
        'show_derelict': self.filter_show_derelict,
        'show_destroyed': self.filter_show_destroyed,
        'show_warp_capable': self.filter_show_warp_capable,
        'show_not_warp_capable': self.filter_show_not_warp_capable,
        'show_has_spaceyard': self.filter_show_has_spaceyard,
        'show_no_spaceyard': self.filter_show_no_spaceyard,
        'show_has_cargo': self.filter_show_has_cargo,
        'show_no_cargo': self.filter_show_no_cargo,
        'show_can_destroy_planet': self.filter_show_can_destroy_planet,
        'show_no_destroy_planet': self.filter_show_no_destroy_planet,
        'show_can_open_warp': self.filter_show_can_open_warp,
        'show_no_open_warp': self.filter_show_no_open_warp,
        'show_can_close_warp': self.filter_show_can_close_warp,
        'show_no_close_warp': self.filter_show_no_close_warp,
        'show_can_destroy_star': self.filter_show_can_destroy_star,
        'show_no_destroy_star': self.filter_show_no_destroy_star,
        'show_can_create_sphere': self.filter_show_can_create_sphere,
        'show_no_create_sphere': self.filter_show_no_create_sphere,
    }
```

### How Return Value Is Used

The filtered list is immediately passed to `sort_ships()` and stored in `self._filtered_ships` for later access via `get_filtered_ships()`.

---

## Interface Stability Assessment

### Can the Interface Change?

**YES** - The interface can change with low risk because:

1. **Single Caller:** Only one location calls `filter_ships()` - the view model in the same module
2. **Internal API:** Both files are in `game/ui/screens/` - this is an internal module boundary
3. **Test Isolation:** Tests directly import and call `filter_ships()`, but they are unit tests that can be updated alongside implementation
4. **No External Consumers:** No other game systems depend on this function

### Recommendations for Interface Changes

If refactoring requires signature changes:
1. Update `filter_ships()` and its single call site in `FleetListViewModel` together
2. Update test imports and calls in `test_fleet_report_filters.py`
3. Consider whether `get_filter_state()` needs corresponding updates

---

## Dependencies (What `filter_ships` Imports)

| Dependency | Import Location | Purpose |
|------------|-----------------|---------|
| `ShipStatsCalculator.has_warp_capability` | `game.strategy.services.ship_stats_calculator` | Check warp capability |
| `FleetCapabilityCalculator.ship_has_spaceyard` | `game.strategy.data.fleet_capability_calculator` | Check spaceyard capability (late import) |
| `FleetCapabilityCalculator.ship_has_ability` | `game.strategy.data.fleet_capability_calculator` | Check special abilities (late import) |
| `SPECIAL_CAPABILITY_COLUMNS` | `game.ui.screens.fleet_data_source` | Mapping of column IDs to ability names |

### Special Capability Columns Constant

From `fleet_data_source.py`:
```python
SPECIAL_CAPABILITY_COLUMNS = {
    "can_destroy_planet": "DestroyPlanet",
    "can_open_warp": "OpenWarpPoint",
    "can_close_warp": "CloseWarpPoint",
    "can_destroy_star": "DestroyStar",
    "can_create_sphere": "CreateSphereWorld",
}
```

---

## Side Effects and State Mutations

### Analysis: **NONE**

The `filter_ships` function is **pure**:

1. **No State Mutation:** Does not modify the input `ships` list or any ship objects
2. **No Global State:** Does not read or write any global/module-level state
3. **No I/O:** No file system, network, or database operations
4. **Deterministic:** Same inputs always produce same outputs
5. **New List Creation:** Returns a new list via `result.append()`

### Late Imports

The function uses late imports inside conditional blocks to avoid circular imports:
- `FleetCapabilityCalculator` is imported only when spaceyard or special ability filters are active
- This is an intentional performance optimization (avoids import overhead when filters aren't active)

---

## Test Coverage

### Test File
**Path:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes for `filter_ships`

| Test Class | Line | Coverage Area |
|------------|------|---------------|
| `TestFilterShips` | 195-291 | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 345-410 | Warp capability filters |
| `TestFilterShipsSpaceyard` | 588-669 | Spaceyard capability filters |
| `TestFilterShipsCargo` | 672-793 | Cargo content filters |
| `TestSpecialCapabilityFilter` | 796-868 | Special ability filters (destroy planet, open warp, etc.) |

### Test Count Summary

- **Basic Status Filters:** 5 tests
- **Warp Capability Filters:** 3 tests
- **Spaceyard Filters:** 3 tests
- **Cargo Filters:** 6 tests
- **Special Capability Filters:** 3 tests

**Total Direct Tests:** ~20 test methods covering `filter_ships`

### Integration Tests via ViewModel

**Path:** `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

The `FleetListViewModel` tests exercise `filter_ships` indirectly through the view model:
- `test_get_filtered_ships_excludes_destroyed_by_default`
- `test_toggle_filter_destroyed`
- `test_toggle_filter_derelict`
- `test_filter_undamaged_only`
- `test_get_filter_state_dict`

---

## Filter Logic Summary

The function processes ships through multiple filter stages in order:

1. **Warp Capability Filter** (lines 143-153)
   - Checks `show_warp_capable` and `show_not_warp_capable`
   - Uses `ShipStatsCalculator.has_warp_capability()`

2. **Spaceyard Capability Filter** (lines 155-164)
   - Checks `show_has_spaceyard` and `show_no_spaceyard`
   - Uses `FleetCapabilityCalculator.ship_has_spaceyard()`

3. **Cargo Filter** (lines 166-174)
   - Checks `show_has_cargo` and `show_no_cargo`
   - Examines `ship.cargo_contents`

4. **Special Capability Filter Loop** (lines 176-194)
   - Iterates over `SPECIAL_CAPABILITY_COLUMNS`
   - Checks each ability via `FleetCapabilityCalculator.ship_has_ability()`
   - Uses dynamic key derivation: `can_X` -> `show_can_X` / `show_no_X`

5. **Ship Status Filters** (lines 196-220)
   - **Destroyed:** `not ship.is_alive` -> check `show_destroyed`
   - **Derelict:** `ship.is_derelict` -> check `show_derelict`
   - **Damaged:** `ship.is_damaged()` -> check `show_damaged`
   - **Undamaged:** (default) -> check `show_undamaged`

---

## Complexity Sources

The high cyclomatic complexity (36) comes from:

1. **Multiple Filter Categories:** 6 distinct filter types, each with include/exclude logic
2. **Paired Filters:** Each category has two filters (show X / show not-X)
3. **Early Exit Pattern:** Multiple `continue` statements for exclusion
4. **Nested Conditionals:** Filter state checks within iteration
5. **Special Capability Loop:** Iterating over 5 capability columns with conditional checks

### Refactoring Opportunities

1. **Extract Filter Functions:** Create separate predicate functions for each filter category
2. **Filter Composition:** Chain filters instead of single loop with all checks
3. **Filter Registry:** Dynamic filter lookup instead of hardcoded conditionals
4. **Configuration Object:** Replace dict with typed filter configuration

---

## Conclusion

`filter_ships` is a well-isolated, pure function with:
- Single caller (internal to module)
- Comprehensive test coverage
- No side effects
- Clear refactoring potential due to high complexity

The function's interface can be safely modified as part of complexity reduction efforts, provided the single call site and associated tests are updated accordingly.
