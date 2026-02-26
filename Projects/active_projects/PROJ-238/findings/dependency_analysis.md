# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## Callers

### 1. `FleetListViewModel._refresh()` in `fleet_report_view_model.py`

**Location:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`, line 215

**Call Pattern:**
```python
filtered = filter_ships(self._ships, self.get_filter_state())
```

**Parameters Passed:**
- `ships`: `self._ships` - a `List[ShipInstance]` held by the view model
- `filter_state`: Result of `self.get_filter_state()` which returns a `Dict[str, bool]` with these keys:
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
  - `show_can_destroy_planet`
  - `show_no_destroy_planet`
  - `show_can_open_warp`
  - `show_no_open_warp`
  - `show_can_close_warp`
  - `show_no_close_warp`
  - `show_can_destroy_star`
  - `show_no_destroy_star`
  - `show_can_create_sphere`
  - `show_no_create_sphere`

**Return Value Usage:**
- The result is passed to `sort_ships()` for sorting
- The sorted result is stored in `self._filtered_ships` for later access via `get_filtered_ships()`

**Import Statement:**
```python
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
```

---

## Interface Stability

### Can the Signature Change?

**Assessment: CAUTION REQUIRED - Limited changes possible**

**Current Signature:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

**Constraints:**

1. **Single Internal Caller:** Only `FleetListViewModel._refresh()` calls this function within the production codebase. This provides some flexibility for changes.

2. **Extensive Test Coverage:** The test file `test_fleet_report_filters.py` has 30+ direct calls to `filter_ships` with various filter state configurations. Any signature change requires updating all test cases.

3. **Filter State Keys:** The function uses `.get()` with default `True` for all filter keys, making it backward-compatible when new filter keys are added. However, removing existing keys would silently break filtering logic.

4. **Type Contract:**
   - Input: `List[ShipInstance]` - this is a stable type
   - Output: `List[ShipInstance]` - returns a filtered subset (new list, not modified in place)
   - Filter state: `Dict[str, bool]` - flexible dictionary allows adding new keys without breaking callers

**Recommendations:**
- **Safe to add:** New filter keys (function uses `.get()` with defaults)
- **Requires coordination:** Changing parameter types or return type
- **Breaking change:** Removing existing filter key support
- **Breaking change:** Changing the function name

---

## Side Effects

### Side Effect Analysis: NONE (Pure Function)

The `filter_ships` function is a **pure function** with no side effects:

1. **No State Mutation:**
   - Does not modify the input `ships` list
   - Does not modify any `ShipInstance` objects
   - Does not modify the `filter_state` dictionary
   - Creates and returns a new list

2. **No External Dependencies Modified:**
   - No file I/O
   - No database operations
   - No global state changes
   - No logging

3. **Late Imports:**
   - Line 159: `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator`
   - Line 185: `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator`
   - These are lazy imports for capability checks, but they only read ship data

4. **External Service Calls:**
   - `ShipStatsCalculator.has_warp_capability(ship)` - read-only check
   - `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - read-only check
   - `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - read-only check

5. **Ship Property Access (Read-Only):**
   - `ship.is_alive`
   - `ship.is_derelict`
   - `ship.is_damaged()`
   - `ship.cargo_contents`

---

## Test Coverage

### Test File: `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

**Test Classes Covering `filter_ships`:**

| Class | Tests | Description |
|-------|-------|-------------|
| `TestFilterShips` | 5 | Basic status filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 6 | Cargo presence filtering |
| `TestSpecialCapabilityFilter` | 3 | Special ability filtering (DestroyPlanet, etc.) |

**Total Direct Tests:** ~20 test methods

**Test Scenarios Covered:**

1. **Status Filters:**
   - Show all ships (all filters enabled)
   - Hide damaged ships
   - Hide undamaged ships
   - Hide derelict ships
   - Hide destroyed ships

2. **Warp Capability:**
   - Hide warp-capable ships
   - Hide non-warp-capable ships
   - Show all warp states

3. **Spaceyard Capability:**
   - Hide ships with spaceyards
   - Hide ships without spaceyards
   - Show all spaceyard states

4. **Cargo:**
   - Hide ships with cargo
   - Hide ships without cargo
   - Cargo includes population
   - Zero-value cargo treated as no cargo
   - Show all cargo states

5. **Special Capabilities:**
   - Hide ships with specific ability
   - Hide ships without specific ability
   - Default shows all ships

### Additional Related Test File: `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

**Coverage:** Tests `FleetListViewModel` integration with `filter_ships` via `get_filtered_ships()`

| Class | Tests | Description |
|-------|-------|-------------|
| `TestFleetListViewModel` | 16 | ViewModel state and filtering integration |
| `TestFleetListViewModelWarpFilters` | 2 | Warp filter toggles |
| `TestFleetListViewModelSpaceyardFilters` | 5 | Spaceyard filter toggles |
| `TestFleetListViewModelCargoFilters` | 5 | Cargo filter toggles |

**Assessment:** Test coverage is **comprehensive**. All filter types have dedicated tests, including edge cases like zero-value cargo.

---

## Dependencies Used by `filter_ships`

### Internal Dependencies (Imported):

| Dependency | Usage | Import Location |
|------------|-------|-----------------|
| `ShipStatsCalculator.has_warp_capability` | Check warp capability | Line 149 (already imported at module level) |
| `FleetCapabilityCalculator.ship_has_spaceyard` | Check spaceyard capability | Lines 159-160 (lazy import) |
| `FleetCapabilityCalculator.ship_has_ability` | Check special abilities | Lines 185-186 (lazy import) |
| `SPECIAL_CAPABILITY_COLUMNS` | Map column IDs to ability names | Line 13 (module level) |

### ShipInstance Attributes Accessed:

| Attribute/Method | Type | Purpose |
|------------------|------|---------|
| `ship.is_alive` | `bool` | Destroyed filter |
| `ship.is_derelict` | `bool` | Derelict filter |
| `ship.is_damaged()` | `method -> bool` | Damaged filter |
| `ship.cargo_contents` | `Dict[str, int]` | Cargo filter |

---

## Summary

| Aspect | Assessment |
|--------|------------|
| **Callers** | 1 production caller (`FleetListViewModel`), 30+ test calls |
| **Interface Stability** | Moderately stable - adding filter keys is safe, other changes need coordination |
| **Side Effects** | None - pure function |
| **Test Coverage** | Comprehensive - all filter types tested with edge cases |
| **Refactoring Risk** | Low - well-encapsulated, pure function with thorough tests |
