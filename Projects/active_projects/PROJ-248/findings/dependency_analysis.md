# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Callers Analysis

### Direct Callers in `game/` Directory

| File | Usage |
|------|-------|
| `game/ui/screens/fleet_report_view_model.py` | Line 215: `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Single Caller Pattern:** The `filter_ships` function has exactly ONE caller in production code - the `FleetListViewModel._refresh()` method.

### How Parameters Are Passed

The caller (`FleetListViewModel`) constructs the `filter_state` dictionary via `get_filter_state()`:

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

The return value (filtered list) is immediately passed to `sort_ships()`:

```python
def _refresh(self) -> None:
    filtered = filter_ships(self._ships, self.get_filter_state())
    self._filtered_ships = sort_ships(filtered, self.sort_column_id, self.sort_descending)
    self._needs_refresh = False
```

---

## 2. Interface Stability Assessment

### Can the Interface Change?

**YES, with caution.** The interface CAN be modified because:

1. **Single caller** - Only `FleetListViewModel` calls this function
2. **Module-internal coupling** - Both caller and callee are in the same `game/ui/screens/` package
3. **Test coverage** - Extensive test coverage allows safe refactoring

### Current Interface

```python
def filter_ships(
    ships: List[ShipInstance],
    filter_state: Dict[str, bool]
) -> List[ShipInstance]
```

### Constraints on Changes

1. **Filter state keys are coupled** - The `filter_state` dictionary keys must match what `FleetListViewModel.get_filter_state()` produces
2. **Return type must remain `List[ShipInstance]`** - Used directly by `sort_ships()`
3. **Input list should not be mutated** - Current implementation creates a new list (good)

### Potential Breaking Changes to Avoid

- Renaming filter keys without updating `FleetListViewModel`
- Changing return type
- Adding required parameters without defaults

---

## 3. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** with respect to its inputs:
- Does NOT modify the input `ships` list
- Does NOT modify the input `filter_state` dictionary
- Does NOT modify any global state
- Does NOT perform I/O

### Late Imports (Conditional)

The function performs late imports inside the loop, which are conditionally executed:

```python
# Line 159: Only imported when spaceyard filter is active
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

# Line 185: Only imported when special capability filters are active
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

These late imports:
- Avoid circular import issues
- Are executed multiple times within the loop (performance consideration)
- Could be hoisted outside the loop for efficiency

### External Dependencies Called

| Dependency | Usage |
|------------|-------|
| `ShipStatsCalculator.has_warp_capability(ship)` | Warp filter check |
| `FleetCapabilityCalculator.ship_has_spaceyard(ship)` | Spaceyard filter check |
| `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` | Special capability filter check |
| `SPECIAL_CAPABILITY_COLUMNS` | Dictionary mapping column IDs to ability names |

### ShipInstance Methods Used

The function calls these methods/properties on `ShipInstance` objects:

| Property/Method | Purpose |
|-----------------|---------|
| `ship.is_alive` | Destroyed check |
| `ship.is_derelict` | Derelict check |
| `ship.is_damaged()` | Damaged check (method) |
| `ship.cargo_contents` | Cargo check (dictionary) |

---

## 4. Test Coverage

### Test Files

| Test File | Tests for `filter_ships` |
|-----------|--------------------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | **Primary test file** - Extensive coverage |
| `tests/unit/ui/test_fleet_list_view_model.py` | Integration tests via `FleetListViewModel` |
| `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` | Unrelated (different filter manager) |

### Test Classes in `test_fleet_report_filters.py`

| Test Class | Description |
|------------|-------------|
| `TestFilterShips` | Basic filter tests (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | Warp capability filter tests |
| `TestFilterShipsSpaceyard` | Spaceyard capability filter tests |
| `TestFilterShipsCargo` | Cargo filter tests |
| `TestSpecialCapabilityFilter` | Special ability filter tests (BUG-83) |

### Key Test Cases

1. **Show all ships** - All filters enabled passes all ships
2. **Hide damaged** - Filters out ships with `is_damaged() == True`
3. **Hide undamaged** - Filters out ships with `is_damaged() == False`
4. **Hide derelict** - Filters out ships with `is_derelict == True`
5. **Hide destroyed** - Filters out ships with `is_alive == False`
6. **Warp filters** - Show/hide by warp capability
7. **Spaceyard filters** - Show/hide by spaceyard capability
8. **Cargo filters** - Show/hide by cargo contents
9. **Special capability filters** - Show/hide by special abilities (DestroyPlanet, etc.)

### Test Coverage Quality

**HIGH** - The test suite covers:
- All basic filter types
- Combined filter scenarios
- Edge cases (zero cargo, empty dict)
- Mock-based isolation from dependencies

---

## 5. Imported Dependencies

### Direct Imports

```python
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
from game.ui.screens.fleet_data_source import SPECIAL_CAPABILITY_COLUMNS
```

### Late Imports (inside function)

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

### SPECIAL_CAPABILITY_COLUMNS Definition

Located in `game/ui/screens/fleet_data_source.py`:

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

## 6. Complexity Assessment

### Current Complexity Issues

1. **Multiple filter categories with similar patterns** - Status, warp, spaceyard, cargo, special capabilities all follow similar boolean pair patterns
2. **Repeated late imports inside loop** - `FleetCapabilityCalculator` imported multiple times per ship
3. **Complex control flow** - Multiple `continue` statements, nested conditions
4. **Long function** - ~100 lines handling all filter logic

### Filter Categories

| Category | Filter Keys | Logic Type |
|----------|------------|------------|
| Status | `show_damaged`, `show_undamaged`, `show_derelict`, `show_destroyed` | Mutually exclusive status check |
| Warp | `show_warp_capable`, `show_not_warp_capable` | Boolean pair |
| Spaceyard | `show_has_spaceyard`, `show_no_spaceyard` | Boolean pair |
| Cargo | `show_has_cargo`, `show_no_cargo` | Boolean pair |
| Special | `show_can_X`, `show_no_X` for 5 abilities | Boolean pair per ability |

---

## 7. Summary

### Key Findings

1. **Single caller** - Safe to refactor interface with coordinated changes
2. **Pure function** - No side effects, no state mutations
3. **Well-tested** - Comprehensive unit test coverage
4. **Repeated patterns** - Boolean filter pairs could be abstracted
5. **Performance opportunity** - Late imports could be hoisted

### Recommendations for Refactoring

1. **Interface is flexible** - Can be changed if `FleetListViewModel` is updated simultaneously
2. **Consider filter predicate pattern** - Each filter category could be a separate predicate
3. **Hoist late imports** - Move `FleetCapabilityCalculator` import outside the loop
4. **Consider filter class** - Could extract filter logic into a `ShipFilter` class with composable predicates
