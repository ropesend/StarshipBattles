# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
**Lines:** 124-222

---

## Callers

### Direct Callers

| Caller File | Location | Usage Pattern |
|-------------|----------|---------------|
| `game/ui/screens/fleet_report_view_model.py` | Line 215 | `filtered = filter_ships(self._ships, self.get_filter_state())` |

### Import Statements

| File | Import |
|------|--------|
| `game/ui/screens/fleet_report_view_model.py:10` | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |

### Single Caller Analysis

The `filter_ships` function has exactly **one production caller**: `FleetListViewModel._refresh()`.

**Call Pattern:**
```python
# In FleetListViewModel._refresh() at line 212-223
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

**Parameters Passed:**
- `ships`: `self._ships` - A `List[ShipInstance]` stored in the view model
- `filter_state`: `self.get_filter_state()` - A dictionary with 20 boolean keys

**Return Value Usage:**
- Return value is passed directly to `sort_ships()` for further processing
- The sorted result is cached in `self._filtered_ships`

---

## Interface Stability

### Current Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Interface Change Assessment

**Can the interface change?** YES - with low risk.

**Reasons:**
1. **Single production caller** - Only `FleetListViewModel._refresh()` calls this function
2. **View model owns the filter_state contract** - The `get_filter_state()` method in `FleetListViewModel` constructs the dictionary, so both sides can be updated together
3. **Tests use direct imports** - Test files import and call `filter_ships` directly, so they would need updates

### Required Filter State Keys

The function expects these keys in `filter_state` (all default to `True` if missing):

**Status Filters:**
- `show_damaged`
- `show_undamaged`
- `show_derelict`
- `show_destroyed`

**Capability Filters:**
- `show_warp_capable`
- `show_not_warp_capable`
- `show_has_spaceyard`
- `show_no_spaceyard`
- `show_has_cargo`
- `show_no_cargo`

**Special Ability Filters (derived from SPECIAL_CAPABILITY_COLUMNS):**
- `show_can_destroy_planet` / `show_no_destroy_planet`
- `show_can_open_warp` / `show_no_open_warp`
- `show_can_close_warp` / `show_no_close_warp`
- `show_can_destroy_star` / `show_no_destroy_star`
- `show_can_create_sphere` / `show_no_create_sphere`

### Coordinated Files for Interface Changes

If the interface changes, update these files together:
1. `game/ui/screens/fleet_report_filters.py` - Function definition
2. `game/ui/screens/fleet_report_view_model.py` - `get_filter_state()` method
3. `tests/unit/ui/screens/test_fleet_report_filters.py` - Test filter_state dictionaries

---

## Side Effects

### Analysis

**The function is PURE - no side effects.**

**What it does:**
1. Iterates over input `ships` list (read-only)
2. Reads filter_state dictionary values (read-only)
3. Calls methods on ship objects (read-only attribute access)
4. Builds and returns a new list

**Ship Object Methods Called (Read-Only):**
- `ship.is_alive` (property)
- `ship.is_derelict` (property)
- `ship.is_damaged()` (method)
- `ship.cargo_contents` (property)

**External Service Calls (Read-Only):**
- `ShipStatsCalculator.has_warp_capability(ship)` - Static method, no mutations
- `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - Static method, no mutations
- `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - Static method, no mutations

### Lazy Imports

The function uses intentional late imports to avoid circular dependencies:
```python
# Lines 159, 185, 269, 279
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

These are imported inside conditional blocks when filters are actually applied.

---

## Test Coverage

### Test File

**Primary:** `tests/unit/ui/screens/test_fleet_report_filters.py`

### Test Classes for `filter_ships`

| Test Class | Line | Coverage Area |
|------------|------|---------------|
| `TestFilterShips` | 195-291 | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 345-410 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 588-669 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 672-793 | Cargo presence filtering |
| `TestSpecialCapabilityFilter` | 796-868 | Special ability filters (destroy planet, etc.) |

### Test Count

**Total tests for `filter_ships`:** 25+ explicit test methods

### Test Scenarios Covered

**Status Filters:**
- `test_filter_show_all` - All filters enabled passes all ships
- `test_filter_hide_damaged` - Excludes damaged ships
- `test_filter_hide_undamaged` - Excludes undamaged ships
- `test_filter_hide_derelict` - Excludes derelict ships
- `test_filter_hide_destroyed` - Excludes destroyed ships

**Warp Filters:**
- `test_filter_hide_warp_capable` - Excludes warp-capable ships
- `test_filter_hide_not_warp_capable` - Excludes non-warp ships
- `test_filter_show_all_warp_states` - Both enabled passes all

**Spaceyard Filters:**
- `test_filter_hide_has_spaceyard` - Excludes ships with spaceyards
- `test_filter_hide_no_spaceyard` - Excludes ships without spaceyards
- `test_filter_show_all_spaceyard_states` - Both enabled passes all

**Cargo Filters:**
- `test_filter_hide_has_cargo` - Excludes ships with cargo
- `test_filter_hide_no_cargo` - Excludes ships without cargo
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero cargo = no cargo
- `test_filter_show_all_cargo_states` - Both enabled passes all

**Special Ability Filters:**
- `test_filter_hides_ships_with_ability` - Excludes ships with special ability
- `test_filter_hides_ships_without_ability` - Excludes ships without ability
- `test_filter_default_shows_all` - Default state shows all ships

### Related Test Files

| File | Relevance |
|------|-----------|
| `tests/unit/ui/test_fleet_list_view_model.py` | Tests `FleetListViewModel` which calls `filter_ships` |
| `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` | Contains `test_capabilities_filter_ships_only` (different context) |

### Coverage Assessment

**Coverage Level: EXCELLENT**

The function has comprehensive test coverage:
- All filter categories have dedicated test classes
- Edge cases are tested (zero cargo, population as cargo)
- Both positive and negative filter states are tested
- Integration with view model is tested separately

---

## Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | Single production caller (`FleetListViewModel._refresh()`) |
| **Interface Stability** | Safe to modify - coordinate with view model |
| **Side Effects** | None - pure function |
| **Test Coverage** | Excellent (25+ tests across 5 test classes) |
| **Refactoring Risk** | LOW - isolated with good test coverage |

### Recommendations

1. **Safe to refactor** - The function is well-isolated with a single caller
2. **Maintain test coverage** - Ensure any changes preserve the comprehensive test suite
3. **Update view model together** - Changes to filter_state keys require coordinated updates
4. **Consider extracting filter logic** - The function is 98 lines with complex branching; individual filter predicates could be extracted for better testability
