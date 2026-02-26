# Dependency Analysis: `filter_ships`

**Function Location:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py` (lines 124-222)

**Analysis Date:** 2026-02-26

---

## Callers

### Direct Callers

| File | Caller | Usage Context |
|------|--------|---------------|
| `game/ui/screens/fleet_report_view_model.py` | `FleetListViewModel._refresh()` | Filters ships before sorting in the view model refresh cycle |

### Call Chain

```
FleetListViewModel.get_filtered_ships()
  -> FleetListViewModel._refresh()  [if _needs_refresh]
    -> filter_ships(self._ships, self.get_filter_state())
    -> sort_ships(filtered, self.sort_column_id, self.sort_descending)
```

### Caller Details

**FleetListViewModel** (line 215):
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

---

## Interface Stability

### Current Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

### Parameters

1. **`ships: List[ShipInstance]`** - List of ship instances to filter
2. **`filter_state: Dict[str, bool]`** - Dictionary of filter flags

### Filter State Keys (Expected)

The function expects these keys in `filter_state` (all default to `True` if missing):

**Core Status Filters:**
- `show_damaged` - Include damaged ships
- `show_undamaged` - Include undamaged ships
- `show_derelict` - Include derelict ships
- `show_destroyed` - Include destroyed ships

**Warp Capability Filters:**
- `show_warp_capable` - Include ships with warp capability
- `show_not_warp_capable` - Include ships without warp capability

**Spaceyard Filters:**
- `show_has_spaceyard` - Include ships with spaceyards
- `show_no_spaceyard` - Include ships without spaceyards

**Cargo Filters:**
- `show_has_cargo` - Include ships with cargo
- `show_no_cargo` - Include ships without cargo

**Special Capability Filters (derived from SPECIAL_CAPABILITY_COLUMNS):**
- `show_can_destroy_planet` / `show_no_destroy_planet`
- `show_can_open_warp` / `show_no_open_warp`
- `show_can_close_warp` / `show_no_close_warp`
- `show_can_destroy_star` / `show_no_destroy_star`
- `show_can_create_sphere` / `show_no_create_sphere`

### Interface Stability Assessment

**STABLE - Changes require coordination with FleetListViewModel**

The interface is tightly coupled to `FleetListViewModel.get_filter_state()` which produces the exact dictionary format expected. Any changes to:
- Filter key names
- New filter keys
- Return type

...require corresponding updates in `FleetListViewModel` class:
- Instance variables (`filter_show_*`)
- `toggle_filter()` method
- `get_filter_state()` method
- `get_filter_label()` method

---

## Side Effects

### External Dependencies (Late Imports)

The function performs **conditional late imports** to avoid circular dependencies:

1. **`ShipStatsCalculator.has_warp_capability()`** (line 149)
   - Used when warp filters are active
   - From: `game.strategy.services.ship_stats_calculator`

2. **`FleetCapabilityCalculator.ship_has_spaceyard()`** (lines 159-160)
   - Used when spaceyard filters are active
   - From: `game.strategy.data.fleet_capability_calculator`

3. **`FleetCapabilityCalculator.ship_has_ability()`** (lines 185-186)
   - Used when special capability filters are active
   - From: `game.strategy.data.fleet_capability_calculator`

### State Mutations

**NONE** - The function is pure:
- Does not modify input `ships` list
- Does not modify input `filter_state` dict
- Does not modify any ship instances
- Returns a new list containing filtered references

### ShipInstance Methods Called (Read-Only)

The function reads the following ship properties/methods:
- `ship.is_alive` (property)
- `ship.is_derelict` (property)
- `ship.is_damaged()` (method)
- `ship.cargo_contents` (property)

---

## Test Coverage

### Direct Tests

**File:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

| Test Class | Test Count | Coverage Area |
|------------|------------|---------------|
| `TestFilterShips` | 5 tests | Core status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 3 tests | Warp capability filters |
| `TestFilterShipsSpaceyard` | 3 tests | Spaceyard filters |
| `TestFilterShipsCargo` | 6 tests | Cargo filters (including edge cases) |
| `TestSpecialCapabilityFilter` | 3 tests | Special capability filters (BUG-83) |

**Total Direct Tests:** 20 tests

### Test Details

**Core Status Filtering:**
- `test_filter_show_all` - All filters enabled shows all ships
- `test_filter_hide_damaged` - Hide damaged ships
- `test_filter_hide_undamaged` - Hide undamaged ships
- `test_filter_hide_derelict` - Hide derelict ships
- `test_filter_hide_destroyed` - Hide destroyed ships

**Warp Capability Filtering:**
- `test_filter_hide_warp_capable` - Hide warp-capable ships
- `test_filter_hide_not_warp_capable` - Hide non-warp-capable ships
- `test_filter_show_all_warp_states` - Both warp filters enabled

**Spaceyard Filtering:**
- `test_filter_hide_has_spaceyard` - Hide ships with spaceyards
- `test_filter_hide_no_spaceyard` - Hide ships without spaceyards
- `test_filter_show_all_spaceyard_states` - Both spaceyard filters enabled

**Cargo Filtering:**
- `test_filter_hide_has_cargo` - Hide ships with cargo
- `test_filter_hide_no_cargo` - Hide ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero-value cargo treated as empty
- `test_filter_show_all_cargo_states` - Both cargo filters enabled

**Special Capability Filtering:**
- `test_filter_hides_ships_with_ability` - Hide ships with special ability
- `test_filter_hides_ships_without_ability` - Hide ships lacking special ability
- `test_filter_default_shows_all` - Default state shows all ships

### Indirect Tests

**File:** `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

Tests that exercise `filter_ships` through `FleetListViewModel`:
- `TestFleetListViewModel` - 14 tests covering filter toggling and integration
- `TestFleetListViewModelWarpFilters` - 2 tests
- `TestFleetListViewModelSpaceyardFilters` - 5 tests
- `TestFleetListViewModelCargoFilters` - 5 tests

**Total Indirect Tests:** 26 tests

### Coverage Assessment

**COMPREHENSIVE** - The function has excellent test coverage:
- All filter categories are tested
- Edge cases (zero cargo, all filters off/on) are covered
- Both direct unit tests and integration tests via ViewModel
- Mocking strategy is clean using `unittest.mock.patch`

---

## Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | Single caller: `FleetListViewModel._refresh()` |
| **Interface Stability** | Stable but coupled to ViewModel filter state |
| **Side Effects** | None - Pure function |
| **Test Coverage** | Excellent (20 direct + 26 indirect tests) |
| **Refactoring Risk** | Low - Well-tested, single caller |

### Recommendations

1. **Interface changes** require synchronizing with `FleetListViewModel.get_filter_state()` and related methods
2. **New filter types** should follow the existing pattern: add key to `get_filter_state()`, add instance variable, update `toggle_filter()`
3. **Late imports** are intentional to avoid circular dependencies - do not move to module level
4. **SPECIAL_CAPABILITY_COLUMNS** is imported from `fleet_data_source.py` and shared between filter and display logic
