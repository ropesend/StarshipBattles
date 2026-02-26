# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`

**Function Signature:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

---

## Callers

### Production Code Callers

| File | Line | Usage |
|------|------|-------|
| `game/ui/screens/fleet_report_view_model.py` | 10, 215 | Import: `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` <br> Called in `_refresh()` method: `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Detailed Caller Analysis:**

#### `FleetListViewModel._refresh()` (fleet_report_view_model.py:212-223)

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

**Parameters Passed:**
- `ships`: `self._ships` - A `List[ShipInstance]` stored by the ViewModel
- `filter_state`: `self.get_filter_state()` - Returns a `Dict[str, bool]` with 20 filter keys

**Return Value Usage:**
- The returned list is passed directly to `sort_ships()` for further processing
- Final result stored in `self._filtered_ships` for display

### Test Code Callers

| File | Test Classes |
|------|--------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShips`, `TestFilterShipsWarp`, `TestFilterShipsSpaceyard`, `TestFilterShipsCargo`, `TestSpecialCapabilityFilter` |

**Test Count:** 18+ direct tests of `filter_ships` function

---

## Interface Stability

### Current Interface

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

**Input Parameters:**
1. `ships: List[ShipInstance]` - List of ship objects to filter
2. `filter_state: Dict[str, bool]` - Dictionary with boolean filter flags

**Expected `filter_state` Keys:**
```python
{
    # Status filters
    'show_damaged': bool,
    'show_undamaged': bool,
    'show_derelict': bool,
    'show_destroyed': bool,

    # Warp capability filters
    'show_warp_capable': bool,
    'show_not_warp_capable': bool,

    # Spaceyard filters
    'show_has_spaceyard': bool,
    'show_no_spaceyard': bool,

    # Cargo filters
    'show_has_cargo': bool,
    'show_no_cargo': bool,

    # Special capability filters (5 pairs)
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

**Return Type:** `List[ShipInstance]` - Filtered subset of input ships

### Stability Assessment

| Aspect | Can Change? | Notes |
|--------|-------------|-------|
| Function Name | **NO** | Imported by name in 1 production file and 18+ test files |
| Parameter Types | **NO** | Changing types would break `FleetListViewModel._refresh()` |
| Parameter Names | **PARTIALLY** | Could change if all callers updated |
| Return Type | **NO** | Result fed directly to `sort_ships()` |
| Adding New Filter Keys | **YES** | Uses `.get()` with defaults, new keys are backward compatible |
| Removing Filter Keys | **RISKY** | Would require updating `FleetListViewModel.get_filter_state()` |

### Contract with Callers

The function has a stable contract with `FleetListViewModel`:
1. `FleetListViewModel.get_filter_state()` produces the exact filter dict expected
2. The filter keys must stay synchronized between both files
3. Missing keys default to `True` (show everything)

---

## Side Effects

### Direct Side Effects

**None.** The function is a **pure function**:
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not write to any external state
- Returns a new list with filtered references

### Indirect Dependencies (via late imports)

The function performs **conditional late imports** for capability checks:

```python
# Line 159 - Spaceyard capability check
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

# Line 185 - Special ability check
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Import Conditions:**
- `FleetCapabilityCalculator` is only imported when:
  - Spaceyard filter is active (`show_has_spaceyard` or `show_no_spaceyard` is `False`)
  - Special capability filter is active (any `show_can_*` or `show_no_*` is `False`)

### Read-Only Data Access

The function reads the following from `ShipInstance` objects:
- `ship.is_alive` - Property
- `ship.is_derelict` - Property
- `ship.is_damaged()` - Method call
- `ship.cargo_contents` - Dict property
- Via `ShipStatsCalculator.has_warp_capability(ship)` - Reads `ship.get_calculated_stats()`
- Via `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - Reads ship abilities
- Via `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - Reads ship abilities

### External Dependencies

| Dependency | Import Location | Purpose |
|------------|-----------------|---------|
| `ShipStatsCalculator` | Module-level (line 12) | `has_warp_capability()` check |
| `FleetCapabilityCalculator` | Late import (lines 159, 185) | Spaceyard and ability checks |
| `SPECIAL_CAPABILITY_COLUMNS` | Module-level (line 13) | Maps column IDs to ability names |

---

## Test Coverage

### Test File
`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes and Methods

#### `TestFilterShips` (Lines 195-291)
| Test Method | Coverage |
|-------------|----------|
| `test_filter_show_all` | All filters enabled shows all ships |
| `test_filter_hide_damaged` | `show_damaged=False` hides damaged ships |
| `test_filter_hide_undamaged` | `show_undamaged=False` hides undamaged ships |
| `test_filter_hide_derelict` | `show_derelict=False` hides derelict ships |
| `test_filter_hide_destroyed` | `show_destroyed=False` hides destroyed ships |

#### `TestFilterShipsWarp` (Lines 345-410)
| Test Method | Coverage |
|-------------|----------|
| `test_filter_hide_warp_capable` | `show_warp_capable=False` hides warp-capable ships |
| `test_filter_hide_not_warp_capable` | `show_not_warp_capable=False` hides non-warp ships |
| `test_filter_show_all_warp_states` | Both warp filters enabled shows all ships |

#### `TestFilterShipsSpaceyard` (Lines 588-669)
| Test Method | Coverage |
|-------------|----------|
| `test_filter_hide_has_spaceyard` | `show_has_spaceyard=False` hides ships with yards |
| `test_filter_hide_no_spaceyard` | `show_no_spaceyard=False` hides ships without yards |
| `test_filter_show_all_spaceyard_states` | Both spaceyard filters enabled shows all |

#### `TestFilterShipsCargo` (Lines 672-793)
| Test Method | Coverage |
|-------------|----------|
| `test_filter_hide_has_cargo` | `show_has_cargo=False` hides loaded ships |
| `test_filter_hide_no_cargo` | `show_no_cargo=False` hides empty ships |
| `test_filter_cargo_with_population` | Population counts as cargo |
| `test_filter_cargo_zero_value_treated_as_no_cargo` | Zero cargo treated as empty |
| `test_filter_show_all_cargo_states` | Both cargo filters enabled shows all |

#### `TestSpecialCapabilityFilter` (Lines 796-868)
| Test Method | Coverage |
|-------------|----------|
| `test_filter_hides_ships_with_ability` | `show_can_destroy_planet=False` works |
| `test_filter_hides_ships_without_ability` | `show_no_destroy_planet=False` works |
| `test_filter_default_shows_all` | Default state shows all ships |

### Integration Coverage

`TestFleetListViewModel` in `tests/unit/ui/test_fleet_list_view_model.py`:
- Tests the full integration chain: `FleetListViewModel` -> `filter_ships` -> `sort_ships`
- Verifies filter toggle behavior updates filtered results
- Tests default filter state (destroyed hidden by default)

### Coverage Assessment

| Filter Type | Unit Tests | Integration Tests |
|-------------|------------|-------------------|
| Status (damaged/undamaged/derelict/destroyed) | 5 tests | Yes |
| Warp capability | 3 tests | Yes |
| Spaceyard | 3 tests | Yes |
| Cargo | 5 tests | No |
| Special capabilities | 3 tests | Yes |
| **Total** | **19 tests** | Multiple |

### Coverage Gaps

1. **Edge Cases:**
   - Empty ship list (covered in `calculate_fleet_stats` but not explicitly for `filter_ships`)
   - All filters disabled (would hide everything)

2. **Filter Combinations:**
   - Complex multi-filter scenarios (e.g., damaged AND warp capable AND has cargo)
   - Tests mostly use single filter changes

3. **Error Handling:**
   - Invalid filter state keys (handled gracefully via `.get()` defaults)
   - Malformed ship objects (not tested)

---

## Summary

### Key Findings

1. **Single Production Caller:** Only `FleetListViewModel._refresh()` calls `filter_ships`, making refactoring scope manageable.

2. **Pure Function:** No side effects or state mutations; safe for parallel execution.

3. **Stable Interface:** Cannot change function signature without updating:
   - `FleetListViewModel.get_filter_state()` (filter state producer)
   - 18+ test methods

4. **Extensible Design:** Adding new filter keys is backward compatible due to `.get()` with `True` defaults.

5. **Well Tested:** 19 direct unit tests cover all filter types, though complex combinations are sparse.

### Recommendations for Interface Changes

If interface changes are needed:
1. Update `FleetListViewModel.get_filter_state()` to produce the new filter keys
2. Update all 18+ test methods that pass explicit `filter_state` dicts
3. Consider deprecation period if callers outside this codebase exist (unlikely)
