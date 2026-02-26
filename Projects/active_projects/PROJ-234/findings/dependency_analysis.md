# Dependency Analysis: `filter_ships` Function

**Target:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Date:** 2026-02-26

---

## 1. Callers of `filter_ships`

### Production Code

| File | Line | Usage |
|------|------|-------|
| `game/ui/screens/fleet_report_view_model.py` | 10 | Import: `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |
| `game/ui/screens/fleet_report_view_model.py` | 215 | Call: `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Single Caller:** The function has exactly ONE production caller - `FleetListViewModel._refresh()`. This is a very controlled call site.

### Test Code

| File | Description |
|------|-------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Dedicated test file with extensive tests |
| `tests/unit/ui/test_fleet_list_view_model.py` | Tests the ViewModel which uses filter_ships internally |

---

## 2. Parameters and Return Values

### Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Parameters

**`ships: List[ShipInstance]`**
- Input list of ship objects
- Not mutated by the function (new list returned)
- Ships are expected to have these attributes/methods:
  - `is_alive: bool`
  - `is_derelict: bool`
  - `is_damaged() -> bool`
  - `cargo_contents: Dict`

**`filter_state: Dict[str, bool]`**
- Dictionary with filter keys, all defaulting to `True` if missing
- Keys used:
  - `show_damaged`
  - `show_undamaged`
  - `show_derelict`
  - `show_destroyed`
  - `show_warp_capable`
  - `show_not_warp_capable`
  - `show_has_spaceyard`
  - `show_no_spaceyard`
  - `show_has_cargo`
  - `show_no_cargo`
  - `show_can_destroy_planet`, `show_no_destroy_planet`
  - `show_can_open_warp`, `show_no_open_warp`
  - `show_can_close_warp`, `show_no_close_warp`
  - `show_can_destroy_star`, `show_no_destroy_star`
  - `show_can_create_sphere`, `show_no_create_sphere`

### Return Value

- Returns a NEW `List[ShipInstance]` containing filtered ships
- Original list is preserved (non-destructive operation)
- Maintains order from input list (no sorting performed)

### How Return Value is Used

In `FleetListViewModel._refresh()`:
```python
filtered = filter_ships(self._ships, self.get_filter_state())
self._filtered_ships = sort_ships(filtered, self.sort_column_id, self.sort_descending)
```

The filtered result is immediately passed to `sort_ships` - the functions form a pipeline.

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**YES - Interface can change safely** with these constraints:

1. **Single Production Caller:** Only `FleetListViewModel._refresh()` calls this function
2. **Not Exported:** Not in module's `__init__.py` - internal implementation detail
3. **Tightly Coupled:** The ViewModel's `get_filter_state()` method explicitly builds the dict that `filter_ships` expects
4. **Co-located Responsibility:** Both the caller and callee are in the same `fleet_report_*` module family

### Recommended Approach for Changes

If refactoring:
1. Update `filter_ships` signature
2. Update `FleetListViewModel.get_filter_state()` and `._refresh()` to match
3. Update test fixtures in `test_fleet_report_filters.py`

### Filter State Contract

The `filter_state` dict keys are defined in `FleetListViewModel.get_filter_state()` (lines 171-199). Any changes to filter keys must update both locations.

---

## 4. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** with respect to its inputs:
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not modify `filter_state` dict
- No global state access
- No file I/O
- No network calls

### State Reads (External Dependencies)

The function makes these external calls to check ship capabilities:

1. **`ShipStatsCalculator.has_warp_capability(ship)`** (line 149)
   - From: `game.strategy.services.ship_stats_calculator`
   - Reads: `ship.get_calculated_stats()['warp_max_tonnage']` and `['mass']`

2. **`FleetCapabilityCalculator.ship_has_spaceyard(ship)`** (line 160)
   - From: `game.strategy.data.fleet_capability_calculator`
   - Reads: Ship's component list for 'SpaceShipyard' component

3. **`FleetCapabilityCalculator.ship_has_ability(ship, ability_name)`** (line 186)
   - From: `game.strategy.data.fleet_capability_calculator`
   - Reads: Ship's abilities from components

### Import Structure

Notable: Uses **late imports** inside the function body (lines 159, 185) to avoid circular dependencies:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

---

## 5. Test Coverage

### Dedicated Test Classes

| Test Class | Line | Focus |
|------------|------|-------|
| `TestFilterShips` | 195-291 | Core damage/status filtering |
| `TestFilterShipsWarp` | 345-410 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 588-669 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 672-793 | Cargo filtering |
| `TestSpecialCapabilityFilter` | 796-868 | Special ability filtering (DestroyPlanet, etc.) |

### Test Cases Summary

**Status Filtering (TestFilterShips):**
- `test_filter_show_all` - All filters enabled passes all ships
- `test_filter_hide_damaged` - Excludes damaged ships
- `test_filter_hide_undamaged` - Excludes undamaged ships
- `test_filter_hide_derelict` - Excludes derelict ships
- `test_filter_hide_destroyed` - Excludes destroyed ships

**Warp Filtering (TestFilterShipsWarp):**
- `test_filter_hide_warp_capable` - Excludes warp-capable ships
- `test_filter_hide_not_warp_capable` - Excludes non-warp ships
- `test_filter_show_all_warp_states` - Both filters on passes all

**Spaceyard Filtering (TestFilterShipsSpaceyard):**
- `test_filter_hide_has_spaceyard` - Excludes ships with yards
- `test_filter_hide_no_spaceyard` - Excludes ships without yards
- `test_filter_show_all_spaceyard_states` - Both filters on passes all

**Cargo Filtering (TestFilterShipsCargo):**
- `test_filter_hide_has_cargo` - Excludes ships with cargo
- `test_filter_hide_no_cargo` - Excludes ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Empty cargo dict
- `test_filter_show_all_cargo_states` - Both filters on passes all

**Special Capability Filtering (TestSpecialCapabilityFilter):**
- `test_filter_hides_ships_with_ability` - Excludes ships with ability
- `test_filter_hides_ships_without_ability` - Excludes ships without ability
- `test_filter_default_shows_all` - Default state shows all ships

### Coverage Assessment

**Well Covered:**
- All filter types individually
- Both positive and negative cases
- Default state behavior
- Edge cases (empty cargo, zero values)

**Test Infrastructure:**
- Uses `make_mock_ship()` helper for test fixtures
- Uses `unittest.mock.patch` for external dependencies
- Tests are isolated and don't require real ShipInstance objects

---

## 6. Complexity Observations

### Current Structure Issues

1. **Long Function:** 98 lines with multiple filter categories interleaved
2. **Repetitive Pattern:** Each filter category follows same pattern:
   - Get two filter flags from dict
   - If either is false, check the condition
   - `continue` if filtered out
3. **Late Imports:** Multiple `from ... import` statements inside loop body
4. **Mixed Concerns:** Status filters, capability filters, and special ability filters all in one function

### Refactoring Opportunities

1. **Extract Filter Functions:** Each filter category could be its own function
2. **Filter Chain Pattern:** Could use a chain of filter functions
3. **Filter Objects:** Could use strategy pattern for different filter types
4. **Move Late Imports:** Could move to module level or use dependency injection

### Dependency on `SPECIAL_CAPABILITY_COLUMNS`

```python
from game.ui.screens.fleet_data_source import SPECIAL_CAPABILITY_COLUMNS
```

This constant defines the mapping from column IDs to ability names:
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

## Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | 1 production caller (`FleetListViewModel`), extensive test coverage |
| **Interface Stability** | Can change - not public API, single caller |
| **Side Effects** | None - pure function |
| **State Mutations** | None - returns new list |
| **Test Coverage** | Excellent - 5 test classes, 20+ test cases |
| **Refactoring Risk** | Low - controlled call site, good test coverage |
