# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)

---

## 1. Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

**Parameters:**
- `ships`: List of `ShipInstance` objects to filter
- `filter_state`: Dictionary with boolean filter flags

**Returns:** Filtered list of `ShipInstance` objects (new list, original unchanged)

---

## 2. All Callers

### Production Code Callers

| File | Line | Context |
|------|------|---------|
| `game\ui\screens\fleet_report_view_model.py` | 10 | Import statement |
| `game\ui\screens\fleet_report_view_model.py` | 215 | Called in `_refresh()` method |

**Single Caller:** The function is called from exactly one location in production code:

```python
# fleet_report_view_model.py line 215
def _refresh(self) -> None:
    """Refresh the filtered/sorted ship list."""
    filtered = filter_ships(self._ships, self.get_filter_state())
    # ...
```

### How Parameters Are Passed

The caller (`FleetListViewModel._refresh()`) constructs the `filter_state` dict via `get_filter_state()` method (lines 171-199):

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

The returned filtered list is:
1. Stored in `self._filtered_ships`
2. Subsequently sorted via `sort_ships()`
3. Accessed by callers via `get_filtered_ships()` method

---

## 3. Interface Stability Assessment

### CAN the interface change?

**YES** - The interface can be safely modified because:

1. **Single caller in production code** - Only `FleetListViewModel._refresh()` calls this function
2. **Internal to UI layer** - Not part of public API, not imported by other layers
3. **Caller and callee co-located** - Both in `game/ui/screens/` package
4. **View model controls filter_state construction** - The caller builds the dict internally

### Constraints on Changes

If changing the interface:
1. Update `FleetListViewModel.get_filter_state()` to match new filter_state keys
2. Update the toggle_filter() method if adding/removing filter types
3. Update corresponding test files

---

## 4. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** with no side effects:
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not modify the `filter_state` dict
- Returns a new list containing references to filtered ships
- No I/O operations
- No global state access

### Internal Dependencies Called

The function makes **late imports** to avoid circular dependencies:

1. `ShipStatsCalculator.has_warp_capability(ship)` - line 149
   - From: `game.strategy.services.ship_stats_calculator`
   - Purpose: Check warp capability

2. `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - line 160
   - From: `game.strategy.data.fleet_capability_calculator`
   - Purpose: Check spaceyard capability

3. `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - line 186
   - From: `game.strategy.data.fleet_capability_calculator`
   - Purpose: Check special capabilities (destroy planet, open/close warp, etc.)

### External Data Read

The function reads from `SPECIAL_CAPABILITY_COLUMNS` dict (imported from `fleet_data_source.py`):

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

## 5. Test Coverage

### Test File Location

`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes for `filter_ships`

| Test Class | Purpose | Line |
|------------|---------|------|
| `TestFilterShips` | Basic status filtering (damaged/undamaged/derelict/destroyed) | 195 |
| `TestFilterShipsWarp` | Warp capability filtering | 345 |
| `TestFilterShipsSpaceyard` | Spaceyard capability filtering | 588 |
| `TestFilterShipsCargo` | Cargo filtering | 672 |
| `TestSpecialCapabilityFilter` | Special ability filtering (BUG-83) | 796 |

### Test Cases (21 total)

**Basic Status Filtering (5 tests):**
- `test_filter_show_all` - All filters enabled, all ships pass
- `test_filter_hide_damaged` - Hide damaged ships
- `test_filter_hide_undamaged` - Hide undamaged ships
- `test_filter_hide_derelict` - Hide derelict ships
- `test_filter_hide_destroyed` - Hide destroyed ships

**Warp Capability Filtering (3 tests):**
- `test_filter_hide_warp_capable` - Hide warp-capable ships
- `test_filter_hide_not_warp_capable` - Hide non-warp-capable ships
- `test_filter_show_all_warp_states` - Both enabled shows all

**Spaceyard Filtering (3 tests):**
- `test_filter_hide_has_spaceyard` - Hide ships with spaceyards
- `test_filter_hide_no_spaceyard` - Hide ships without spaceyards
- `test_filter_show_all_spaceyard_states` - Both enabled shows all

**Cargo Filtering (5 tests):**
- `test_filter_hide_has_cargo` - Hide ships with cargo
- `test_filter_hide_no_cargo` - Hide ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero values = no cargo
- `test_filter_show_all_cargo_states` - Both enabled shows all

**Special Capability Filtering (3 tests):**
- `test_filter_hides_ships_with_ability` - Hide ships with special abilities
- `test_filter_hides_ships_without_ability` - Hide ships without special abilities
- `test_filter_default_shows_all` - Default state shows all ships

### Additional Related Tests

- `test_fleet_list_view_model.py` line 119: Tests that `get_filter_state()` returns dict for `filter_ships`

### Coverage Assessment

**GOOD COVERAGE** - The function has comprehensive test coverage:
- All filter categories tested (status, warp, spaceyard, cargo, special capabilities)
- Both positive (hide) and negative (show) cases for each filter
- Edge cases like zero cargo values
- Default behavior tested
- Uses mocking appropriately for calculator dependencies

---

## 6. Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | 1 production caller (`FleetListViewModel._refresh`) |
| **Interface Stability** | Can change - single internal caller |
| **Side Effects** | None - pure function |
| **State Mutations** | None - returns new list |
| **Test Coverage** | Comprehensive (21 test cases) |
| **Dependencies** | ShipStatsCalculator, FleetCapabilityCalculator (late imports) |

### Recommendations for Refactoring

1. **Interface changes safe** - Can modify signature since single internal caller
2. **Keep pure** - Maintain no side effects property
3. **Update tests** - Test file has comprehensive coverage; update tests if behavior changes
4. **Consider extracting filter logic** - Individual filter checks could be extracted to separate functions for testability
5. **Late imports intentional** - Keep late imports to avoid circular dependencies
