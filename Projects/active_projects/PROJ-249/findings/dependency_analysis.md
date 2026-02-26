# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Analysis Date:** 2026-02-26

---

## 1. Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

**Parameters:**
- `ships: List[ShipInstance]` - List of ship instances to filter
- `filter_state: Dict[str, bool]` - Dictionary with filter flags

**Returns:**
- `List[ShipInstance]` - Filtered list of ships (new list, does not mutate input)

---

## 2. Callers

### 2.1 Production Code Caller

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`

| Location | Line | Usage |
|----------|------|-------|
| Import | 10 | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |
| `_refresh()` method | 215 | `filtered = filter_ships(self._ships, self.get_filter_state())` |

**How it's called:**
```python
# Line 215 in fleet_report_view_model.py
filtered = filter_ships(self._ships, self.get_filter_state())
```

The `FleetListViewModel` class:
1. Maintains a `_ships` list internally (set via `update_ships()` or constructor)
2. Constructs `filter_state` via `get_filter_state()` method (lines 171-199)
3. Passes the filtered result to `sort_ships()` before caching

**Filter state keys provided by view model (lines 178-198):**
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

### 2.2 Summary

**Single Caller:** The function has exactly one caller in production code - `FleetListViewModel._refresh()`.

---

## 3. Test Coverage

**Test File:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes for `filter_ships`:

| Class | Lines | Description |
|-------|-------|-------------|
| `TestFilterShips` | 195-291 | Basic status filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 345-410 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 588-669 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 672-793 | Cargo filtering |
| `TestSpecialCapabilityFilter` | 796-868 | Special abilities (DestroyPlanet, etc.) |

### Test Cases Summary:

**Basic Status Filters (5 tests):**
- `test_filter_show_all` - All filters enabled passes all ships
- `test_filter_hide_damaged` - Hide damaged ships
- `test_filter_hide_undamaged` - Hide undamaged ships
- `test_filter_hide_derelict` - Hide derelict ships
- `test_filter_hide_destroyed` - Hide destroyed ships

**Warp Capability (3 tests):**
- `test_filter_hide_warp_capable` - Hide warp-capable ships
- `test_filter_hide_not_warp_capable` - Hide non-warp-capable ships
- `test_filter_show_all_warp_states` - Both enabled passes all

**Spaceyard Capability (3 tests):**
- `test_filter_hide_has_spaceyard` - Hide ships with spaceyards
- `test_filter_hide_no_spaceyard` - Hide ships without spaceyards
- `test_filter_show_all_spaceyard_states` - Both enabled passes all

**Cargo Filtering (6 tests):**
- `test_filter_hide_has_cargo` - Hide ships with cargo
- `test_filter_hide_no_cargo` - Hide empty ships
- `test_filter_cargo_with_population` - Population counts as cargo
- `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero values = no cargo
- `test_filter_show_all_cargo_states` - Both enabled passes all

**Special Capabilities (3 tests):**
- `test_filter_hides_ships_with_ability` - Hide ships with special ability
- `test_filter_hides_ships_without_ability` - Hide ships lacking ability
- `test_filter_default_shows_all` - Default shows all ships

### Coverage Assessment

**Well Covered:**
- All filter categories have tests
- Both "show" and "hide" cases tested
- Edge cases (zero cargo, population as cargo)

**Potential Gaps:**
- No tests for combined filters (e.g., hide damaged AND hide derelict simultaneously)
- No tests for filter_state with missing keys (relies on `.get()` defaults)

---

## 4. Dependencies (Internal to Function)

### 4.1 Module-Level Imports Used

| Import | Line | Purpose |
|--------|------|---------|
| `ShipStatsCalculator` | 12 | `has_warp_capability()` static method |
| `SPECIAL_CAPABILITY_COLUMNS` | 13 | Maps column IDs to ability names |

### 4.2 Late (Conditional) Imports Inside Function

| Import | Lines | Condition |
|--------|-------|-----------|
| `FleetCapabilityCalculator` | 159 | When spaceyard filter is active (not both True) |
| `FleetCapabilityCalculator` | 185 | When special capability filter is active |

**Pattern:** Late imports are deferred to avoid circular imports and improve startup time. They only execute when the specific filter is actually in use.

### 4.3 Ship Instance API Used

The function accesses these `ShipInstance` properties/methods:

| Access | Line(s) | Purpose |
|--------|---------|---------|
| `ship.is_alive` | 197 | Check if destroyed |
| `ship.is_derelict` | 204 | Check derelict status |
| `ship.is_damaged()` | 211 | Check if damaged (method call) |
| `ship.cargo_contents` | 170 | Dict of cargo type -> amount |

### 4.4 External Service Calls

| Service | Method | Line(s) | Purpose |
|---------|--------|---------|---------|
| `ShipStatsCalculator` | `has_warp_capability(ship)` | 149 | Check warp capability |
| `FleetCapabilityCalculator` | `ship_has_spaceyard(ship)` | 160 | Check for shipyard |
| `FleetCapabilityCalculator` | `ship_has_ability(ship, ability_name)` | 186 | Check special abilities |

---

## 5. Side Effects and State Mutations

### Assessment: **PURE FUNCTION**

The `filter_ships` function:
1. **Does NOT mutate** the input `ships` list - creates new `result` list
2. **Does NOT mutate** the input `filter_state` dict
3. **Does NOT mutate** any ship objects
4. **Does NOT access** global/module state
5. **Does NOT perform** I/O operations

The function is referentially transparent - given the same inputs, it always returns the same output.

---

## 6. Interface Stability Analysis

### 6.1 Can the Function Signature Change?

**Signature:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

| Aspect | Assessment | Reason |
|--------|------------|--------|
| Parameter types | **STABLE** | Only 1 caller, uses exact types |
| Parameter count | **CAN CHANGE** | Only 1 caller to update |
| Return type | **STABLE** | Caller chains to `sort_ships()` expecting same type |
| Function name | **CAN CHANGE** | Only 1 caller, easy rename |

### 6.2 Can Filter State Keys Change?

**Risk Level:** MEDIUM

The `filter_state` dictionary keys are tightly coupled with:
1. `FleetListViewModel.get_filter_state()` - produces the dict
2. `filter_ships()` - consumes the dict

Adding new keys:
- Add to `FleetListViewModel.get_filter_state()` (produces)
- Add handling in `filter_ships()` (consumes)
- Update tests for new filter

Removing/renaming keys requires updating both locations.

### 6.3 External Dependencies That Could Break Function

| Dependency | Risk | Mitigation |
|------------|------|------------|
| `ShipInstance.is_alive` | LOW | Core ship property, stable |
| `ShipInstance.is_derelict` | LOW | Core ship property, stable |
| `ShipInstance.is_damaged()` | LOW | Core ship method, stable |
| `ShipInstance.cargo_contents` | LOW | Core ship dict, stable |
| `ShipStatsCalculator.has_warp_capability()` | MEDIUM | Static method, documented API |
| `FleetCapabilityCalculator.ship_has_spaceyard()` | MEDIUM | Static method, documented API |
| `FleetCapabilityCalculator.ship_has_ability()` | MEDIUM | Static method, documented API |
| `SPECIAL_CAPABILITY_COLUMNS` dict | LOW | Local module constant |

---

## 7. Refactoring Recommendations

### 7.1 Interface is SAFE to Modify

With only one production caller (`FleetListViewModel._refresh()`), the interface can be modified as needed. Changes require:
1. Update `filter_ships()` signature/implementation
2. Update `FleetListViewModel._refresh()` call site
3. Update corresponding tests

### 7.2 Potential Improvements

1. **Extract filter predicates** - Each filter block (warp, spaceyard, cargo, special capabilities) could be a separate predicate function for better testability

2. **Use dataclass for filter_state** - Replace `Dict[str, bool]` with a typed `FilterState` dataclass for better IDE support and validation

3. **Consolidate late imports** - The `FleetCapabilityCalculator` is imported twice (lines 159, 185); could be consolidated to a single import at function start

4. **Simplify filter application order** - The function currently short-circuits with `continue` statements; could use a predicate-based approach:
   ```python
   predicates = [
       make_warp_filter(filter_state),
       make_spaceyard_filter(filter_state),
       make_cargo_filter(filter_state),
       # etc.
   ]
   return [ship for ship in ships if all(p(ship) for p in predicates)]
   ```

---

## 8. Summary

| Aspect | Finding |
|--------|---------|
| **Callers** | 1 (FleetListViewModel._refresh) |
| **Test Coverage** | Comprehensive - 20+ test cases |
| **Side Effects** | None - pure function |
| **Interface Stability** | CAN CHANGE - single caller |
| **Dependencies** | ShipInstance properties, ShipStatsCalculator, FleetCapabilityCalculator |
| **Complexity Source** | Multiple filter categories with paired show/hide logic |
