# Dependency Analysis: `filter_ships` Function

## Overview

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
**Lines:** 124-222

The `filter_ships` function filters a list of ships based on various boolean filter criteria. It supports filtering by damage status, warp capability, spaceyard capability, cargo contents, and special abilities.

---

## 1. All Callers of `filter_ships`

### Production Code Callers

| File | Line | Import/Usage |
|------|------|--------------|
| `game\ui\screens\fleet_report_view_model.py` | 10 | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |
| `game\ui\screens\fleet_report_view_model.py` | 215 | `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Only ONE production caller exists:** `FleetListViewModel._refresh()` method.

The import statement at line 10 shows `filter_ships` is imported alongside `sort_ships`. The actual usage occurs in the private `_refresh()` method at line 215.

---

## 2. Parameters Passed and Return Value Usage

### Call Site: `FleetListViewModel._refresh()` (line 212-223)

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

**Parameters:**
- `ships`: `self._ships` - A `List[ShipInstance]` maintained by the view model
- `filter_state`: Result of `self.get_filter_state()` - A `Dict[str, bool]` built from the view model's filter flags

**Return Value Usage:**
- The returned filtered list is stored in local variable `filtered`
- Immediately passed to `sort_ships()` for sorting
- The sorted result is stored in `self._filtered_ships` (cached result)

### Filter State Dictionary Structure

From `FleetListViewModel.get_filter_state()` (lines 171-199):

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

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**Yes, with careful coordination.** The interface can be modified because:

1. **Single caller:** Only `FleetListViewModel._refresh()` calls this function
2. **Same module ecosystem:** Both files are in `game.ui.screens`
3. **ViewModel controls filter_state:** The filter dictionary is built by `get_filter_state()`, so the contract is already tightly coupled

### Constraints on Changes:

1. **Return type must remain `List[ShipInstance]`** - The result is immediately passed to `sort_ships()`
2. **Must accept filter_state dict** - The ViewModel builds this dict from its internal flags
3. **Filter keys are coupled to ViewModel flags** - Any new filter requires updates in both locations

### Recommended Approach for Interface Changes:

If refactoring, changes should be made to both:
- `fleet_report_filters.py::filter_ships()` - The implementation
- `fleet_report_view_model.py::FleetListViewModel` - The caller and filter state builder

---

## 4. Side Effects and State Mutations

### Direct Side Effects: NONE

The function is **pure** with respect to its inputs:
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not modify `filter_state`
- Returns a new list containing references to filtered ships

### Internal Dependencies with Potential Side Effects:

The function uses late imports to check ship capabilities:

```python
# Line 159: Spaceyard check
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)

# Line 185-186: Special ability check
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
```

These are static method calls and do not mutate state.

```python
# Line 149: Warp capability check
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
```

This also does not mutate state - it reads from `ship.get_calculated_stats()`.

### Lazy Import Pattern

The function uses **intentional late imports** to avoid circular dependencies:
- `FleetCapabilityCalculator` is imported inside the filtering loops (lines 159, 185)
- This prevents `game.ui.screens` from having a load-time dependency on `game.strategy.data`

---

## 5. Test Coverage

### Test File Location

**Primary:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes Covering `filter_ships`

| Class | Lines | Coverage Focus |
|-------|-------|----------------|
| `TestFilterShips` | 196-291 | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 346-410 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 589-669 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 673-793 | Cargo filtering (including population, zero values) |
| `TestSpecialCapabilityFilter` | 796-868 | Special abilities (DestroyPlanet, OpenWarp, etc.) |

### Specific Test Methods

**Basic Filtering Tests:**
- `test_filter_show_all` - All filters enabled shows all ships
- `test_filter_hide_damaged` - Hide damaged ships
- `test_filter_hide_undamaged` - Hide undamaged ships
- `test_filter_hide_derelict` - Hide derelict ships
- `test_filter_hide_destroyed` - Hide destroyed ships

**Warp Filtering Tests:**
- `test_filter_hide_warp_capable` - Hide warp-capable ships
- `test_filter_hide_not_warp_capable` - Hide non-warp ships
- `test_filter_show_all_warp_states` - Both filters enabled

**Spaceyard Filtering Tests:**
- `test_filter_hide_has_spaceyard` - Hide ships with yards
- `test_filter_hide_no_spaceyard` - Hide ships without yards
- `test_filter_show_all_spaceyard_states` - Both filters enabled

**Cargo Filtering Tests:**
- `test_filter_hide_has_cargo` - Hide ships with cargo
- `test_filter_hide_no_cargo` - Hide ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero-value dict = no cargo
- `test_filter_show_all_cargo_states` - Both filters enabled

**Special Capability Tests:**
- `test_filter_hides_ships_with_ability` - Hide ships with special ability
- `test_filter_hides_ships_without_ability` - Hide ships without ability
- `test_filter_default_shows_all` - Default state shows all

### Additional Test Coverage

**ViewModel integration tests in:**
`C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

Line 119 references: `"""get_filter_state returns dict for filter_ships function."""`

---

## 6. Dependencies Summary

### Import Dependencies

| Dependency | Type | Import Location |
|------------|------|-----------------|
| `ShipStatsCalculator.has_warp_capability` | Static method | `game.strategy.services.ship_stats_calculator` |
| `FleetCapabilityCalculator.ship_has_spaceyard` | Static method | `game.strategy.data.fleet_capability_calculator` |
| `FleetCapabilityCalculator.ship_has_ability` | Static method | `game.strategy.data.fleet_capability_calculator` |
| `SPECIAL_CAPABILITY_COLUMNS` | Constant dict | `game.ui.screens.fleet_data_source` |

### SPECIAL_CAPABILITY_COLUMNS Constant

Defined in `fleet_data_source.py` (lines 46-52):

```python
SPECIAL_CAPABILITY_COLUMNS = {
    "can_destroy_planet": "DestroyPlanet",
    "can_open_warp": "OpenWarpPoint",
    "can_close_warp": "CloseWarpPoint",
    "can_destroy_star": "DestroyStar",
    "can_create_sphere": "CreateSphereWorld",
}
```

Maps column IDs to ability names for filtering and sorting.

---

## 7. Complexity Observations

### Current Cyclomatic Complexity Issues

The function has high complexity due to:
1. **Sequential filter checks** with early `continue` statements
2. **Nested conditions** for paired filters (e.g., warp/not_warp, cargo/no_cargo)
3. **Loop over SPECIAL_CAPABILITY_COLUMNS** with inner conditionals
4. **Multiple ship state checks** (is_alive, is_derelict, is_damaged)

### Potential Refactoring Approaches

1. **Extract filter predicates** - Each filter type could be a separate predicate function
2. **Filter chain pattern** - Build a list of filter functions and apply them
3. **Strategy pattern** - Each filter as a pluggable strategy object
4. **Early filter optimization** - Apply simpler filters first to reduce iterations

---

## 8. Conclusions

### Key Findings

1. **Single production caller** makes interface changes safe with coordinated updates
2. **No side effects** - function is pure and does not mutate inputs
3. **Comprehensive test coverage** across all filter types
4. **Lazy imports** used to avoid circular dependencies
5. **Filter state contract** is tightly coupled to `FleetListViewModel`

### Recommendations for Refactoring

- Interface can be changed if `FleetListViewModel.get_filter_state()` is updated in tandem
- Consider extracting filter predicates to reduce function complexity
- Tests provide good coverage but use mocks extensively - ensure integration tests exist
- Keep lazy import pattern to maintain layer separation
