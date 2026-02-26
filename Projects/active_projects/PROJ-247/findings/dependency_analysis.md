# Dependency Analysis: `filter_ships` Function

**Location:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py` (lines 124-222)

## 1. Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Parameters
- **`ships`**: `List[ShipInstance]` - List of ship instances to filter
- **`filter_state`**: `Dict[str, bool]` - Dictionary with filter keys (all boolean values)

### Return Value
- `List[ShipInstance]` - Filtered list of ships (new list, does not mutate input)

### Filter State Keys (all optional, default to `True` if missing)
| Key | Description |
|-----|-------------|
| `show_damaged` | Include ships with damage |
| `show_undamaged` | Include healthy ships |
| `show_derelict` | Include derelict ships |
| `show_destroyed` | Include destroyed (not alive) ships |
| `show_warp_capable` | Include warp-capable ships |
| `show_not_warp_capable` | Include ships without warp |
| `show_has_spaceyard` | Include ships with spaceyard |
| `show_no_spaceyard` | Include ships without spaceyard |
| `show_has_cargo` | Include ships carrying cargo |
| `show_no_cargo` | Include ships with no cargo |
| `show_can_destroy_planet` | Include ships with DestroyPlanet ability |
| `show_no_destroy_planet` | Include ships without DestroyPlanet ability |
| `show_can_open_warp` | Include ships with OpenWarpPoint ability |
| `show_no_open_warp` | Include ships without OpenWarpPoint ability |
| `show_can_close_warp` | Include ships with CloseWarpPoint ability |
| `show_no_close_warp` | Include ships without CloseWarpPoint ability |
| `show_can_destroy_star` | Include ships with DestroyStar ability |
| `show_no_destroy_star` | Include ships without DestroyStar ability |
| `show_can_create_sphere` | Include ships with CreateSphereWorld ability |
| `show_no_create_sphere` | Include ships without CreateSphereWorld ability |

---

## 2. Callers

### Production Callers

| File | Caller | Usage |
|------|--------|-------|
| `game/ui/screens/fleet_report_view_model.py` | `FleetListViewModel._refresh()` | Line 215 |

**Caller Details:**

```python
# fleet_report_view_model.py:215
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

The `FleetListViewModel` is the **sole production caller**. It:
1. Stores ships in `self._ships`
2. Builds filter state via `get_filter_state()` (returns all 20 filter keys)
3. Passes results to `sort_ships()` for sorting
4. Caches the result in `_filtered_ships`

---

## 3. Dependencies Used by `filter_ships`

### Direct Imports (at function level - late imports)

| Module | Import | Usage |
|--------|--------|-------|
| `game.strategy.services.ship_stats_calculator` | `ShipStatsCalculator` | `has_warp_capability(ship)` |
| `game.strategy.data.fleet_capability_calculator` | `FleetCapabilityCalculator` | `ship_has_spaceyard(ship)`, `ship_has_ability(ship, ability_name)` |

### Constants Used

| Module | Constant | Purpose |
|--------|----------|---------|
| `game.ui.screens.fleet_data_source` | `SPECIAL_CAPABILITY_COLUMNS` | Maps column IDs to ability names |

**SPECIAL_CAPABILITY_COLUMNS:**
```python
SPECIAL_CAPABILITY_COLUMNS = {
    "can_destroy_planet": "DestroyPlanet",
    "can_open_warp": "OpenWarpPoint",
    "can_close_warp": "CloseWarpPoint",
    "can_destroy_star": "DestroyStar",
    "can_create_sphere": "CreateSphereWorld",
}
```

### ShipInstance Methods/Properties Accessed

| Access | Type | Purpose |
|--------|------|---------|
| `ship.is_alive` | property | Check if destroyed |
| `ship.is_derelict` | property | Check if derelict |
| `ship.is_damaged()` | method | Check if damaged |
| `ship.cargo_contents` | property | Dict of cargo type -> amount |

---

## 4. Side Effects and State Mutations

**None.** The function is pure:
- Creates a new result list
- Does not modify input `ships` list
- Does not modify any `ShipInstance` objects
- No global state changes
- No I/O operations

---

## 5. Test Coverage

### Test File
`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes Covering `filter_ships`

| Class | Lines | Test Count |
|-------|-------|------------|
| `TestFilterShips` | 196-291 | 5 tests |
| `TestFilterShipsWarp` | 345-410 | 3 tests |
| `TestFilterShipsSpaceyard` | 588-669 | 3 tests |
| `TestFilterShipsCargo` | 672-793 | 6 tests |
| `TestSpecialCapabilityFilter` | 796-868 | 3 tests |

### Test Cases Summary

**Basic Status Filters (`TestFilterShips`):**
- `test_filter_show_all` - All filters enabled shows all ships
- `test_filter_hide_damaged` - Hiding damaged ships
- `test_filter_hide_undamaged` - Hiding undamaged ships
- `test_filter_hide_derelict` - Hiding derelict ships
- `test_filter_hide_destroyed` - Hiding destroyed ships

**Warp Capability Filters (`TestFilterShipsWarp`):**
- `test_filter_hide_warp_capable` - Hiding warp-capable ships
- `test_filter_hide_not_warp_capable` - Hiding non-warp ships
- `test_filter_show_all_warp_states` - Both warp filters enabled

**Spaceyard Filters (`TestFilterShipsSpaceyard`):**
- `test_filter_hide_has_spaceyard` - Hiding ships with spaceyard (mocked)
- `test_filter_hide_no_spaceyard` - Hiding ships without spaceyard (mocked)
- `test_filter_show_all_spaceyard_states` - Both filters enabled

**Cargo Filters (`TestFilterShipsCargo`):**
- `test_filter_hide_has_cargo` - Hiding ships with cargo
- `test_filter_hide_no_cargo` - Hiding ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero cargo = no cargo
- `test_filter_show_all_cargo_states` - Both filters enabled

**Special Capability Filters (`TestSpecialCapabilityFilter`):**
- `test_filter_hides_ships_with_ability` - Hiding ships with special abilities
- `test_filter_hides_ships_without_ability` - Hiding ships without special abilities
- `test_filter_default_shows_all` - Default state shows all ships

### ViewModel Integration Tests
`C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`
- Indirectly tests `filter_ships` through `FleetListViewModel.get_filtered_ships()`
- Tests filter toggling and state management

---

## 6. Interface Stability Analysis

### Can the Interface Change?

**Signature Stability: MODERATE**

The function signature itself (`ships`, `filter_state` -> filtered list) is stable because:
1. Only one production caller exists (`FleetListViewModel._refresh`)
2. The caller and function are in the same module hierarchy
3. The pattern of passing a dict is flexible

**Filter State Keys: EXTENSIBLE**

Adding new filter keys is backward-compatible because:
- Missing keys default to `True` (show all)
- `FleetListViewModel.get_filter_state()` would need updating to pass new keys
- Tests use explicit filter_state dicts, would need updates

**Breaking Changes Would Require:**
1. Updating `FleetListViewModel.get_filter_state()`
2. Adding new instance variables to `FleetListViewModel`
3. Updating `toggle_filter()` and `get_filter_label()`
4. Updating ~20 test cases that construct filter_state dicts

### Recommended Approach for Refactoring

1. **Internal refactoring is safe** - Logic can be reorganized without breaking callers
2. **Adding new filters** - Add key to filter_state, update ViewModel, update tests
3. **Changing filter logic** - Update corresponding tests
4. **Signature change** - Would require coordinated update with ViewModel

---

## 7. Function Complexity Analysis

### Current Structure (lines 124-222, ~98 lines)

The function has sequential filter checks:
1. Warp capability filter (lines 143-153)
2. Spaceyard capability filter (lines 155-164)
3. Cargo filter (lines 166-174)
4. Special capability filters loop (lines 176-194)
5. Destroyed filter (lines 196-201)
6. Derelict filter (lines 203-208)
7. Damaged filter (lines 210-215)
8. Undamaged filter (lines 217-220)

### Complexity Concerns

1. **Filter order matters** - Destroyed/derelict checked before damaged
2. **Early returns with continue** - Each filter can skip to next ship
3. **Late imports inside function** - `FleetCapabilityCalculator` imported twice
4. **Mixed filter paradigms** - Some use pairs (show/hide), status filters use single flags
5. **Magic string derivation** - `no_key = col_id.replace('can_', 'no_', 1)`

### Refactoring Opportunities

1. Extract filter predicates as separate functions
2. Use a filter chain/pipeline pattern
3. Consolidate late imports
4. Create filter configuration objects instead of dict
5. Unify the filter paradigm (all pairs or all singles)

---

## 8. Summary

| Aspect | Status |
|--------|--------|
| Production Callers | 1 (`FleetListViewModel._refresh`) |
| Test Coverage | Comprehensive (~20 tests) |
| Side Effects | None (pure function) |
| Interface Stability | Moderate - internal changes safe |
| Dependencies | `ShipStatsCalculator`, `FleetCapabilityCalculator`, `SPECIAL_CAPABILITY_COLUMNS` |
| Complexity | High - 98 lines, 8 filter categories, nested conditionals |

**Refactoring Safety:** HIGH - Single caller, comprehensive tests, pure function
