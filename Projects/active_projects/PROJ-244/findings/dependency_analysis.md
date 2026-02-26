# Dependency Analysis: `filter_ships` Function

## Overview

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
**Lines:** 124-222

## Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Parameters

1. **`ships: List[ShipInstance]`** - Input list of ship instances to filter
2. **`filter_state: Dict[str, bool]`** - Dictionary controlling which ships pass through

### Expected Filter State Keys

| Key | Purpose | Default |
|-----|---------|---------|
| `show_damaged` | Include damaged ships | True |
| `show_undamaged` | Include undamaged/healthy ships | True |
| `show_derelict` | Include derelict ships | True |
| `show_destroyed` | Include destroyed ships | False |
| `show_warp_capable` | Include warp-capable ships | True |
| `show_not_warp_capable` | Include ships without warp | True |
| `show_has_spaceyard` | Include ships with spaceyard | True |
| `show_no_spaceyard` | Include ships without spaceyard | True |
| `show_has_cargo` | Include ships carrying cargo | True |
| `show_no_cargo` | Include empty ships | True |
| `show_can_destroy_planet` | Include planet destroyers | True |
| `show_no_destroy_planet` | Include non-planet destroyers | True |
| `show_can_open_warp` | Include warp openers | True |
| `show_no_open_warp` | Include non-warp openers | True |
| `show_can_close_warp` | Include warp closers | True |
| `show_no_close_warp` | Include non-warp closers | True |
| `show_can_destroy_star` | Include star destroyers | True |
| `show_no_destroy_star` | Include non-star destroyers | True |
| `show_can_create_sphere` | Include sphere builders | True |
| `show_no_create_sphere` | Include non-sphere builders | True |

### Return Value

Returns a new `List[ShipInstance]` containing only ships that pass all active filters.

---

## Callers in Production Code

### 1. `FleetListViewModel._refresh()` (Primary Caller)

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`
**Line:** 215

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

**Usage Pattern:**
- Called internally when `_needs_refresh` is True
- Filter state comes from `get_filter_state()` which builds dict from instance attributes
- Return value is passed to `sort_ships()` then cached in `_filtered_ships`

**Coupling Points:**
- `FleetListViewModel.get_filter_state()` must return keys matching `filter_ships` expectations
- Changes to filter keys require synchronized updates in both locations

### Import Statement

**File:** `fleet_report_view_model.py`, Line 10:
```python
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
```

---

## Interface Stability Assessment

### Can the Interface Change?

**Answer: Yes, with coordination, but requires careful updates.**

**Reasons:**
1. **Single Production Caller:** Only `FleetListViewModel` calls this function
2. **Tightly Coupled Interface:** The `filter_state` dict keys are manually synchronized between:
   - `filter_ships()` implementation (checking keys with `.get()`)
   - `FleetListViewModel.get_filter_state()` (building the dict)
   - `FleetListViewModel` toggle logic and attributes
3. **All Filter Keys Have Defaults:** Uses `.get(key, True)` pattern so missing keys are safe

**Constraints:**
- Adding new filter keys: Safe (defaults to True, shows all)
- Removing filter keys: Safe (code uses `.get()` with defaults)
- Changing key names: Requires sync with `FleetListViewModel.get_filter_state()`
- Changing parameter types: Would require test updates

### Recommended Changes for Interface Improvements

If refactoring:
1. Consider a dataclass/TypedDict for `filter_state` instead of Dict[str, bool]
2. Could move filter logic to `FleetListViewModel` since it's the only consumer
3. Special capability filters iterate over `SPECIAL_CAPABILITY_COLUMNS` - this coupling is good

---

## Side Effects and State Mutations

### Analysis: Pure Function - No Side Effects

The function is **pure** with the following characteristics:

1. **No Mutation of Input:**
   - `ships` list is iterated but never modified
   - Ships are appended to a new `result` list
   - Original list order preserved for passing ships

2. **No External State Changes:**
   - Does not modify any global variables
   - Does not write to files or databases
   - Does not cache or memoize results

3. **Deterministic Output:**
   - Same inputs always produce same outputs
   - No random elements

4. **Internal Dependencies:**
   - Calls `ShipStatsCalculator.has_warp_capability(ship)` - read-only
   - Calls `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - read-only
   - Calls `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - read-only
   - Accesses `ship.cargo_contents` - read-only
   - Accesses `ship.is_alive`, `ship.is_derelict`, `ship.is_damaged()` - read-only

5. **Late Imports:**
   - `FleetCapabilityCalculator` is imported inside the function body (lines 159, 185)
   - This avoids circular import issues at module load time

---

## Test Coverage

### Test File: `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes Covering `filter_ships`:

| Test Class | Line Range | Test Count | Coverage Area |
|------------|------------|------------|---------------|
| `TestFilterShips` | 196-291 | 5 tests | Basic status filters |
| `TestFilterShipsWarp` | 345-410 | 3 tests | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 588-669 | 3 tests | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 672-793 | 6 tests | Cargo filtering |
| `TestSpecialCapabilityFilter` | 796-868 | 3 tests | Special abilities filtering |

### Specific Test Methods:

**Basic Filters:**
- `test_filter_show_all` - All filters enabled, all ships pass
- `test_filter_hide_damaged` - Hide damaged ships
- `test_filter_hide_undamaged` - Hide undamaged ships
- `test_filter_hide_derelict` - Hide derelict ships
- `test_filter_hide_destroyed` - Hide destroyed ships

**Warp Capability:**
- `test_filter_hide_warp_capable` - Hide warp-capable ships
- `test_filter_hide_not_warp_capable` - Hide non-warp ships
- `test_filter_show_all_warp_states` - Both filters enabled

**Spaceyard:**
- `test_filter_hide_has_spaceyard` - Hide ships with yards
- `test_filter_hide_no_spaceyard` - Hide ships without yards
- `test_filter_show_all_spaceyard_states` - Both filters enabled

**Cargo:**
- `test_filter_hide_has_cargo` - Hide loaded ships
- `test_filter_hide_no_cargo` - Hide empty ships
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero-value dict is empty
- `test_filter_show_all_cargo_states` - Both filters enabled

**Special Capabilities:**
- `test_filter_hides_ships_with_ability` - Mocked ability detection
- `test_filter_hides_ships_without_ability` - Inverse filtering
- `test_filter_default_shows_all` - Default state shows all

### Test Coverage Assessment: Good

- All 20 filter keys have at least one test
- Edge cases covered (zero cargo, defaults)
- Uses `unittest.mock` to isolate capability checks
- Integration with `FleetListViewModel` tested in `TestViewModelSpecialFilters`

---

## Dependencies Graph

```
filter_ships()
    |
    +-- ShipStatsCalculator.has_warp_capability()
    |       |
    |       +-- ship.get_calculated_stats()
    |
    +-- FleetCapabilityCalculator.ship_has_spaceyard()
    |       |
    |       +-- (internal ability check)
    |
    +-- FleetCapabilityCalculator.ship_has_ability()
    |       |
    |       +-- (internal ability check)
    |
    +-- SPECIAL_CAPABILITY_COLUMNS (from fleet_data_source.py)
    |
    +-- ShipInstance attributes:
            +-- cargo_contents
            +-- is_alive
            +-- is_derelict
            +-- is_damaged()
```

---

## Summary

| Aspect | Status |
|--------|--------|
| **Callers** | 1 production caller (FleetListViewModel) |
| **Interface Stability** | Modifiable with coordination |
| **Side Effects** | None - pure function |
| **State Mutations** | None |
| **Test Coverage** | Comprehensive (20+ tests) |
| **Import Pattern** | Exported via module-level import |

### Key Findings

1. **Low Risk for Changes:** Single caller and pure function design make this safe to refactor
2. **Coupled Filter State:** The dict keys are manually synchronized - consider TypedDict
3. **Good Test Coverage:** All filter scenarios tested with mocks for external dependencies
4. **Late Imports Used:** `FleetCapabilityCalculator` imported inside function to avoid cycles
5. **No Side Effects:** Function is completely pure and deterministic
