# Dependency Analysis: filter_ships

## Callers

### 1. `FleetListViewModel._refresh()` (Primary Caller)
**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`
**Line:** 215

```python
filtered = filter_ships(self._ships, self.get_filter_state())
```

**Usage Details:**
- Called internally by `_refresh()` method when `_needs_refresh` flag is True
- `get_filtered_ships()` triggers the refresh, which calls `filter_ships`
- Parameters passed:
  - `ships`: `self._ships` - List of `ShipInstance` objects from the view model
  - `filter_state`: `self.get_filter_state()` - Dict with 20 boolean filter keys
- Return value is then passed to `sort_ships()` before caching in `_filtered_ships`

**Filter State Dict Structure (from `get_filter_state()`):**
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

### 2. Import Statement
**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`
**Line:** 10

```python
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
```

## Interface Stability

### Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Stability Assessment: **INTERNAL API - Moderately Flexible**

**Constraints:**
1. **Single Caller:** Only `FleetListViewModel._refresh()` calls this function directly
2. **Coupled Interface:** The filter state dict keys must match what `FleetListViewModel.get_filter_state()` produces
3. **Return Type:** Must return `List[ShipInstance]` - output is passed to `sort_ships()`

**What CAN Change:**
- Internal implementation details (how filters are applied)
- Order of filter checks
- The function could be refactored or broken into smaller helpers
- New filter keys can be added (as long as `get_filter_state()` is updated in tandem)

**What MUST Be Preserved:**
- Function signature: `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
- All existing filter state keys must continue to work (backward compatible with existing filter dict)
- Default behavior when filter keys are missing (uses `.get(key, True)` pattern)
- Ships not matching enabled filters must be excluded
- Ships matching all enabled filters must be included

### External Dependencies Used Inside `filter_ships`:
1. `ShipStatsCalculator.has_warp_capability(ship)` - for warp filtering
2. `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - for spaceyard filtering
3. `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - for special capability filtering
4. `SPECIAL_CAPABILITY_COLUMNS` dict from `fleet_data_source.py` - maps column IDs to ability names

## Side Effects

### State Mutations: **NONE**
The function is a **pure function** with no side effects:
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not modify the `filter_state` dict
- Returns a new list containing references to filtered ships

### Lazy Imports
The function uses intentional late imports inside conditional blocks:
```python
# Line 159, 185
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
These are only imported when the relevant filter is active (not both True), avoiding circular import issues.

## Test Coverage

### Direct Tests: `TestFilterShips` class
**File:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

| Test | Lines Covered | Description |
|------|---------------|-------------|
| `test_filter_show_all` | 200-221 | All filters enabled, all ships pass |
| `test_filter_hide_damaged` | 210-215 | Damaged filter exclusion |
| `test_filter_hide_undamaged` | 217-220 | Undamaged filter exclusion |
| `test_filter_hide_derelict` | 203-208 | Derelict filter exclusion |
| `test_filter_hide_destroyed` | 196-201 | Destroyed filter exclusion |

### Warp Filter Tests: `TestFilterShipsWarp` class
| Test | Description |
|------|-------------|
| `test_filter_hide_warp_capable` | Hide warp-capable ships |
| `test_filter_hide_not_warp_capable` | Hide non-warp ships |
| `test_filter_show_all_warp_states` | Both warp filters enabled |

### Spaceyard Filter Tests: `TestFilterShipsSpaceyard` class
| Test | Description |
|------|-------------|
| `test_filter_hide_has_spaceyard` | Hide ships with spaceyards |
| `test_filter_hide_no_spaceyard` | Hide ships without spaceyards |
| `test_filter_show_all_spaceyard_states` | Both spaceyard filters enabled |

### Cargo Filter Tests: `TestFilterShipsCargo` class
| Test | Description |
|------|-------------|
| `test_filter_hide_has_cargo` | Hide ships with cargo |
| `test_filter_hide_no_cargo` | Hide ships without cargo |
| `test_filter_cargo_with_population` | Population counts as cargo |
| `test_filter_cargo_zero_value_treated_as_no_cargo` | Zero-value cargo dict = no cargo |
| `test_filter_show_all_cargo_states` | Both cargo filters enabled |

### Special Capability Filter Tests: `TestSpecialCapabilityFilter` class
| Test | Description |
|------|-------------|
| `test_filter_hides_ships_with_ability` | Hide ships with DestroyPlanet ability |
| `test_filter_hides_ships_without_ability` | Hide ships without ability |
| `test_filter_default_shows_all` | Default state shows all ships |

### Integration Tests via ViewModel: `TestFleetListViewModel` class
**File:** `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

Tests `filter_ships` indirectly through `FleetListViewModel.get_filtered_ships()`:
- `test_get_filtered_ships_excludes_destroyed_by_default`
- `test_toggle_filter_destroyed`
- `test_toggle_filter_derelict`
- `test_filter_undamaged_only`

### Coverage Gaps
1. **Edge Cases:**
   - Empty ships list (not explicitly tested for `filter_ships`, only for `calculate_fleet_stats`)
   - Filter state with missing keys (relies on `.get(key, True)` default)
   - All filters disabled (would return empty list)

2. **Combinations:**
   - Multiple filter types active simultaneously (e.g., damaged + warp + cargo)
   - Interaction between status filters and capability filters

## Refactoring Constraints

### MUST Preserve:
1. **Function signature** - `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
2. **Filter key names** - All 20 keys must continue to work identically
3. **Default behavior** - Missing keys default to `True` (show all)
4. **Pure function semantics** - No side effects, returns new list
5. **Filter priority/order semantics:**
   - Warp filters checked first (lines 144-153)
   - Spaceyard filters second (lines 156-164)
   - Cargo filters third (lines 167-174)
   - Special capability filters fourth (lines 177-194)
   - Status filters last: destroyed > derelict > damaged > undamaged (lines 196-220)

### CAN Change:
1. **Internal structure** - Can extract helper functions for each filter category
2. **Import location** - Late imports could be moved to module level if circular imports are resolved
3. **Filter logic optimization** - Could short-circuit earlier if ship is already excluded
4. **Code organization** - Could use a strategy pattern or filter chain pattern

### Recommended Refactoring Approach:
Given the function's complexity (100 lines, nested conditionals, multiple filter categories), consider:
1. Extract each filter category into a separate predicate function
2. Compose filters using a filter chain or `all()` pattern
3. Keep the public interface unchanged
4. Ensure all existing tests pass without modification

### Dependencies to Update Together:
If changing the filter state dict structure:
1. `FleetListViewModel.get_filter_state()` - must produce matching dict
2. `FleetListViewModel` instance variables (lines 36-57) - filter state storage
3. `FleetListViewModel.toggle_filter()` - filter toggle logic
4. Test fixtures in both test files
