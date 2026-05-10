# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter flags. It supports filtering by:

- **Status filters:** damaged, undamaged, derelict, destroyed
- **Capability filters:** warp_capable, not_warp_capable, has_spaceyard, no_spaceyard
- **Cargo filters:** has_cargo, no_cargo
- **Special capability filters:** can_destroy_planet, can_open_warp, can_close_warp, can_destroy_star, can_create_sphere (and their "no_" variants)

### Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

---

## 2. Callers Analysis

### Direct Callers

| File | Line | Usage |
|------|------|-------|
| `game\ui\screens\fleet_report_view_model.py` | 10 | Import |
| `game\ui\screens\fleet_report_view_model.py` | 215 | `filtered = filter_ships(self._ships, self.get_filter_state())` |

### Call Details

**`fleet_report_view_model.py`** is the **only caller** of `filter_ships`:

```python
# Line 215 in _refresh() method
filtered = filter_ships(self._ships, self.get_filter_state())
```

**Parameters passed:**
- `ships`: `self._ships` - a `List[ShipInstance]` stored in the view model
- `filter_state`: Result of `self.get_filter_state()` - a `Dict[str, bool]` with keys like:
  - `show_damaged`, `show_undamaged`, `show_derelict`, `show_destroyed`
  - `show_warp_capable`, `show_not_warp_capable`
  - `show_has_spaceyard`, `show_no_spaceyard`
  - `show_has_cargo`, `show_no_cargo`
  - `show_can_destroy_planet`, `show_no_destroy_planet`, etc.

**Return value usage:**
- The returned list is passed to `sort_ships()` and stored in `self._filtered_ships`
- Accessed via `get_filtered_ships()` method

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**YES - with caution.** The interface can be modified because:

1. **Single Caller:** Only `FleetListViewModel._refresh()` calls this function
2. **Internal Module:** The function is in a UI module, not a public API
3. **Coordinate with `get_filter_state()`:** The `filter_state` dict keys must match what `get_filter_state()` produces

### Constraints on Changes

| Constraint | Details |
|------------|---------|
| **Parameter Names** | Can change, but update the single call site |
| **Filter Keys** | Must coordinate with `FleetListViewModel.get_filter_state()` (lines 178-199) |
| **Return Type** | Must remain `List[ShipInstance]` - used by `sort_ships()` |
| **List Semantics** | Returns a new list (not mutated input) - caller expects this |

### Filter State Keys (from `get_filter_state()`)

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

## 4. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** with respect to side effects:

- **No state mutation:** Does not modify the input `ships` list
- **No global state:** Does not read or write module-level variables
- **No I/O:** No file, network, or database operations
- **No logging:** No print statements or logging calls

### Internal Behavior

1. Creates a new `result = []` list
2. Iterates over input ships
3. Applies filter conditions using `continue` to skip non-matching ships
4. Appends matching ships to result (reference, not copy)
5. Returns new list

### Dependencies Called Within

The function has **late imports** for strategy layer services:

| Import | Used For |
|--------|----------|
| `ShipStatsCalculator.has_warp_capability(ship)` | Warp capability check |
| `FleetCapabilityCalculator.ship_has_spaceyard(ship)` | Spaceyard check |
| `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` | Special ability checks |

These are called **only when the corresponding filter is active** (optimization).

---

## 5. Test Coverage

### Test File

`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes Covering `filter_ships`

| Test Class | Focus Area | Line Count |
|------------|------------|------------|
| `TestFilterShips` | Basic status filters (damaged, undamaged, derelict, destroyed) | Lines 195-291 |
| `TestFilterShipsWarp` | Warp capability filtering | Lines 345-410 |
| `TestFilterShipsSpaceyard` | Spaceyard capability filtering | Lines 588-669 |
| `TestFilterShipsCargo` | Cargo filtering (including population) | Lines 672-793 |
| `TestSpecialCapabilityFilter` | Special abilities (destroy planet, etc.) | Lines 796-868 |

### Test Cases Summary

**Total test methods for `filter_ships`:** 21+

| Category | Tests |
|----------|-------|
| Show all ships | `test_filter_show_all` |
| Hide damaged | `test_filter_hide_damaged` |
| Hide undamaged | `test_filter_hide_undamaged` |
| Hide derelict | `test_filter_hide_derelict` |
| Hide destroyed | `test_filter_hide_destroyed` |
| Hide warp capable | `test_filter_hide_warp_capable` |
| Hide not warp capable | `test_filter_hide_not_warp_capable` |
| Show all warp states | `test_filter_show_all_warp_states` |
| Hide has spaceyard | `test_filter_hide_has_spaceyard` |
| Hide no spaceyard | `test_filter_hide_no_spaceyard` |
| Show all spaceyard states | `test_filter_show_all_spaceyard_states` |
| Hide has cargo | `test_filter_hide_has_cargo` |
| Hide no cargo | `test_filter_hide_no_cargo` |
| Cargo with population | `test_filter_cargo_with_population` |
| Zero cargo treated as no cargo | `test_filter_cargo_zero_value_treated_as_no_cargo` |
| Show all cargo states | `test_filter_show_all_cargo_states` |
| Hide ships with ability | `test_filter_hides_ships_with_ability` |
| Hide ships without ability | `test_filter_hides_ships_without_ability` |
| Default shows all | `test_filter_default_shows_all` |

### Additional Test Coverage

`tests\unit\ui\test_fleet_list_view_model.py` tests the **integration** with `FleetListViewModel`:
- `test_get_filter_state_dict` - Verifies filter state dict format
- Various filter toggle tests that indirectly exercise `filter_ships`

---

## 6. Related Functions in Same Module

| Function | Purpose | Callers |
|----------|---------|---------|
| `calculate_fleet_stats(ships)` | Calculate summary stats for a fleet | `fleet_report_sidebar.py` |
| `sort_ships(ships, sort_column, descending)` | Sort ships by column | `fleet_report_view_model.py` |

---

## 7. Summary

### Key Findings

1. **Single Consumer:** `filter_ships` has exactly one caller (`FleetListViewModel._refresh()`)
2. **Interface Changeable:** Can modify signature/behavior with minimal impact
3. **Pure Function:** No side effects or state mutations
4. **Well Tested:** Comprehensive test coverage (21+ test cases)
5. **Late Imports:** Uses strategy layer services via late imports to avoid circular dependencies

### Refactoring Implications

- **Safe to refactor internally:** Function body can be changed freely
- **Signature changes:** Require coordinating with `FleetListViewModel`
- **Filter key changes:** Require updating both `filter_ships` and `get_filter_state()`
- **Test updates:** Any changes will likely require test updates due to comprehensive coverage
