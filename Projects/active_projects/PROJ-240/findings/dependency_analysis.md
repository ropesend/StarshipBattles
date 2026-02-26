# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36

---

## 1. Callers of `filter_ships`

### Direct Callers

| File | Location | Usage Pattern |
|------|----------|---------------|
| `game\ui\screens\fleet_report_view_model.py` | Line 215, `_refresh()` method | Single call site in production code |

### How It's Called

```python
# From FleetListViewModel._refresh()
filtered = filter_ships(self._ships, self.get_filter_state())
```

The `FleetListViewModel` class is the **only production caller** of `filter_ships`. It:
1. Stores the source ship list in `self._ships`
2. Builds the filter state dict via `get_filter_state()`
3. Calls `filter_ships()` during refresh
4. Passes the result to `sort_ships()` for ordering

---

## 2. Parameter Analysis

### Input Parameters

| Parameter | Type | Source |
|-----------|------|--------|
| `ships` | `List[ShipInstance]` | `FleetListViewModel._ships` - list of strategy layer ship objects |
| `filter_state` | `Dict[str, bool]` | `FleetListViewModel.get_filter_state()` - dict of filter flags |

### Filter State Structure

The `filter_state` dict contains boolean keys with `show_` prefix:

**Core Status Filters:**
- `show_damaged` - Include damaged ships
- `show_undamaged` - Include undamaged ships
- `show_derelict` - Include derelict ships
- `show_destroyed` - Include destroyed ships

**Capability Filters:**
- `show_warp_capable` / `show_not_warp_capable` - Warp drive filter
- `show_has_spaceyard` / `show_no_spaceyard` - Spaceyard capability
- `show_has_cargo` / `show_no_cargo` - Cargo contents filter

**Special Ability Filters (from SPECIAL_CAPABILITY_COLUMNS):**
- `show_can_destroy_planet` / `show_no_destroy_planet`
- `show_can_open_warp` / `show_no_open_warp`
- `show_can_close_warp` / `show_no_close_warp`
- `show_can_destroy_star` / `show_no_destroy_star`
- `show_can_create_sphere` / `show_no_create_sphere`

### Return Value

- **Type:** `List[ShipInstance]`
- **Usage:** Passed directly to `sort_ships()` for ordering, then stored in `_filtered_ships`
- **Consumers:** `FleetDataSource.get_row_count()`, `FleetDataSource.get_ship_at_index()`

---

## 3. Internal Dependencies

### Imports Used by `filter_ships`

| Import | Source | Usage |
|--------|--------|-------|
| `ShipStatsCalculator.has_warp_capability` | `game.strategy.services.ship_stats_calculator` | Warp capability check |
| `FleetCapabilityCalculator.ship_has_spaceyard` | `game.strategy.data.fleet_capability_calculator` | Spaceyard check (late import) |
| `FleetCapabilityCalculator.ship_has_ability` | `game.strategy.data.fleet_capability_calculator` | Special ability checks (late import) |
| `SPECIAL_CAPABILITY_COLUMNS` | `game.ui.screens.fleet_data_source` | Maps column IDs to ability names |

### ShipInstance Methods/Properties Used

| Property/Method | Type | Usage |
|----------------|------|-------|
| `ship.is_alive` | `bool` | Check if ship is destroyed |
| `ship.is_derelict` | `bool` | Check if ship is derelict |
| `ship.is_damaged()` | `method -> bool` | Check if ship has any damage |
| `ship.cargo_contents` | `Dict[str, int]` | Check if ship has cargo |

---

## 4. Interface Stability Assessment

### Can the Interface Change?

**PARTIALLY - with constraints:**

| Aspect | Stability | Reason |
|--------|-----------|--------|
| Function signature | **Stable** | Only one caller, but part of public module API |
| `ships` parameter type | **Stable** | `List[ShipInstance]` is standard |
| `filter_state` dict structure | **Flexible** | Internal to ViewModel, can evolve |
| Return type | **Stable** | `List[ShipInstance]` expected by caller |

### Breaking Change Risk

- **Low risk** - Single production caller (`FleetListViewModel`)
- The `filter_state` dict is built by `get_filter_state()` which is in the same module ecosystem
- Tests use mock ships and explicit filter_state dicts, not the ViewModel

### Recommended Approach for Refactoring

1. **Keep function signature stable:** `filter_ships(ships, filter_state) -> List[ShipInstance]`
2. **Internal refactoring is safe:** Extract helper functions, split filter logic
3. **Filter state can evolve:** Both producer (`get_filter_state`) and consumer (`filter_ships`) are in same team

---

## 5. Side Effects and State Mutations

### Side Effects: **NONE**

The function is a **pure filter** with no side effects:

| Aspect | Status |
|--------|--------|
| Modifies input `ships` list | No |
| Modifies `ShipInstance` objects | No |
| Modifies global state | No |
| I/O operations | No |
| Logging | No |
| Raises exceptions | No (defensive coding) |

### State Mutations: **NONE**

- Returns a **new list** containing references to input ships
- Does not modify any ship properties
- Late imports are for read-only queries

---

## 6. Test Coverage

### Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `tests\unit\ui\screens\test_fleet_report_filters.py` | **Primary test file** | Extensive coverage |
| `tests\unit\ui\test_fleet_list_view_model.py` | Tests ViewModel integration | Indirect coverage |

### Direct Test Coverage (test_fleet_report_filters.py)

**Class `TestFilterShips` (lines 195-291):**
- `test_filter_show_all` - All filters enabled shows all ships
- `test_filter_hide_damaged` - Damaged filter works
- `test_filter_hide_undamaged` - Undamaged filter works
- `test_filter_hide_derelict` - Derelict filter works
- `test_filter_hide_destroyed` - Destroyed filter works

**Class `TestFilterShipsWarp` (lines 345-411):**
- `test_filter_hide_warp_capable` - Hides warp-capable ships
- `test_filter_hide_not_warp_capable` - Hides non-warp ships
- `test_filter_show_all_warp_states` - Both enabled shows all

**Class `TestFilterShipsSpaceyard` (lines 588-670):**
- `test_filter_hide_has_spaceyard` - Hides ships with spaceyards
- `test_filter_hide_no_spaceyard` - Hides ships without spaceyards
- `test_filter_show_all_spaceyard_states` - Both enabled shows all

**Class `TestFilterShipsCargo` (lines 672-793):**
- `test_filter_hide_has_cargo` - Hides ships with cargo
- `test_filter_hide_no_cargo` - Hides ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero cargo edge case
- `test_filter_show_all_cargo_states` - Both enabled shows all

**Class `TestSpecialCapabilityFilter` (lines 796-868):**
- `test_filter_hides_ships_with_ability` - Special ability hide (has)
- `test_filter_hides_ships_without_ability` - Special ability hide (lacks)
- `test_filter_default_shows_all` - Default shows everything

### Test Coverage Assessment

| Filter Type | Test Coverage |
|-------------|---------------|
| Damage status (damaged/undamaged/derelict/destroyed) | **Complete** |
| Warp capability | **Complete** |
| Spaceyard capability | **Complete** |
| Cargo contents | **Complete** |
| Special abilities (destroy planet, etc.) | **Complete** |
| Combined filters | **Partial** - tests exist but not exhaustive |
| Edge cases (empty list, all filtered out) | **Partial** |

---

## 7. Refactoring Recommendations

### Safe Changes

1. **Extract filter predicates** - Each filter check can be a separate function
2. **Use filter composition** - Chain smaller predicates
3. **Create FilterPredicate protocol** - Standardize filter interface
4. **Split by filter category** - Status filters vs capability filters vs ability filters

### Preserve

1. Function signature: `filter_ships(ships, filter_state) -> List[ShipInstance]`
2. Return semantics: New list, same ship references
3. Filter key naming convention: `show_*` prefix
4. Default behavior: Missing keys default to `True` (show)

### Test Strategy for Refactoring

1. Existing tests provide regression safety
2. Add tests for any new extracted functions
3. Ensure combined filter behavior matches current implementation

---

## Summary

| Metric | Value |
|--------|-------|
| Production callers | 1 (`FleetListViewModel._refresh`) |
| Test files | 2 (1 primary, 1 indirect) |
| Direct unit tests | 15+ test methods |
| Side effects | None |
| State mutations | None |
| Interface stability | High (single caller, well-tested) |
| Safe to refactor internally | Yes |
| Safe to change signature | No (would require ViewModel update) |
