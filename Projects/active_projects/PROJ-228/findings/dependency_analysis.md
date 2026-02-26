# Dependency Analysis: `filter_ships` Function

**Date:** 2026-02-26
**Target Function:** `filter_ships` in `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`

---

## 1. Summary

The `filter_ships` function is a **pure filtering function** with a stable interface. It has:
- **1 direct caller** in production code
- **3 test files** with comprehensive coverage
- **No side effects** or state mutations
- A clear contract that should remain stable

---

## 2. Files That Import or Call `filter_ships`

### 2.1 Production Code

| File | Import Statement | Usage |
|------|------------------|-------|
| `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py` | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` | Called in `_refresh()` method |

### 2.2 Test Files

| File | Import Statement |
|------|------------------|
| `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py` | `from game.ui.screens.fleet_report_filters import filter_ships` |
| `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py` | Indirect via FleetListViewModel |
| `C:\Dev\Starship Battles\tests\unit\ui\screens\test_empire_build_queue_filter_manager.py` | No direct import; tests similar filtering pattern |

---

## 3. Function Signature and Contract

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### 3.1 Parameters

**`ships: List[ShipInstance]`**
- Input list of `ShipInstance` objects
- Not mutated by the function

**`filter_state: Dict[str, bool]`**
- Dictionary of boolean flags controlling which ships to include
- Expected keys (all optional, default to `True` if missing):

| Key | Purpose |
|-----|---------|
| `show_damaged` | Include ships where `is_damaged() == True` |
| `show_undamaged` | Include ships where `is_damaged() == False` |
| `show_derelict` | Include ships where `is_derelict == True` |
| `show_destroyed` | Include ships where `is_alive == False` |
| `show_warp_capable` | Include ships with warp capability |
| `show_not_warp_capable` | Include ships without warp capability |
| `show_has_spaceyard` | Include ships with spaceyard |
| `show_no_spaceyard` | Include ships without spaceyard |
| `show_has_cargo` | Include ships with cargo |
| `show_no_cargo` | Include ships without cargo |
| `show_can_destroy_planet` | Include ships with DestroyPlanet ability |
| `show_no_destroy_planet` | Include ships without DestroyPlanet ability |
| `show_can_open_warp` | Include ships with OpenWarpPoint ability |
| `show_no_open_warp` | Include ships without OpenWarpPoint ability |
| `show_can_close_warp` | Include ships with CloseWarpPoint ability |
| `show_no_close_warp` | Include ships without CloseWarpPoint ability |
| `show_can_destroy_star` | Include ships with DestroyStar ability |
| `show_no_destroy_star` | Include ships without DestroyStar ability |
| `show_can_create_sphere` | Include ships with CreateSphereWorld ability |
| `show_no_create_sphere` | Include ships without CreateSphereWorld ability |

### 3.2 Return Value

- Returns a **new list** containing the filtered ships
- Original `ships` list is not modified
- Order is preserved from the input list

---

## 4. Usage Patterns

### 4.1 FleetListViewModel (Primary Caller)

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_view_model.py`

**Location:** `_refresh()` method (lines 212-223)

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

**How `filter_state` is constructed:**

The `FleetListViewModel.get_filter_state()` method (lines 171-199) builds the dictionary from instance attributes:

```python
def get_filter_state(self) -> Dict[str, bool]:
    return {
        'show_damaged': self.filter_show_damaged,
        'show_undamaged': self.filter_show_undamaged,
        'show_derelict': self.filter_show_derelict,
        'show_destroyed': self.filter_show_destroyed,
        'show_warp_capable': self.filter_show_warp_capable,
        'show_not_warp_capable': self.filter_show_not_warp_capable,
        # ... 14 more filter keys
    }
```

---

## 5. Dependencies of `filter_ships`

The function itself depends on:

### 5.1 External Imports (within function body - late imports)

| Import | Purpose | Location in Code |
|--------|---------|------------------|
| `FleetCapabilityCalculator.ship_has_spaceyard` | Check if ship has spaceyard | Lines 159-160 |
| `FleetCapabilityCalculator.ship_has_ability` | Check for special abilities | Lines 185-186 |
| `ShipStatsCalculator.has_warp_capability` | Check warp capability | Line 149 |

### 5.2 Module-Level Imports

| Import | Source |
|--------|--------|
| `SPECIAL_CAPABILITY_COLUMNS` | `game.ui.screens.fleet_data_source` |

**`SPECIAL_CAPABILITY_COLUMNS` definition:**
```python
SPECIAL_CAPABILITY_COLUMNS = {
    "can_destroy_planet": "DestroyPlanet",
    "can_open_warp": "OpenWarpPoint",
    "can_close_warp": "CloseWarpPoint",
    "can_destroy_star": "DestroyStar",
    "can_create_sphere": "CreateSphereWorld",
}
```

### 5.3 ShipInstance Attributes Accessed

| Attribute/Method | Type | Purpose |
|------------------|------|---------|
| `is_alive` | `bool` | Check if ship is destroyed |
| `is_derelict` | `bool` | Check if ship is derelict |
| `is_damaged()` | `method -> bool` | Check if ship has any damage |
| `cargo_contents` | `Dict[str, int]` | Check if ship has cargo |

---

## 6. Side Effects and State Mutations

**The function has NO side effects:**
- Does not modify the input `ships` list
- Does not modify any `ShipInstance` objects
- Does not modify `filter_state`
- Creates a new list for results
- All external calls (to calculators) are read-only queries

---

## 7. Interface Stability Assessment

### 7.1 Can the Interface Change?

**Short Answer:** The interface SHOULD remain stable.

**Reasons:**
1. Only one direct caller in production code (`FleetListViewModel._refresh`)
2. The `filter_state` dictionary pattern is flexible - new keys can be added without breaking existing callers
3. Tests use the same dictionary pattern, so they are also resilient to new keys

### 7.2 Recommended Approach for Changes

**Adding new filter keys:**
- Safe to add - existing callers provide full filter_state via `get_filter_state()`
- Add new key to `FleetListViewModel.get_filter_state()` and corresponding attribute

**Changing behavior of existing filter keys:**
- Requires updating tests in `test_fleet_report_filters.py`
- May affect UI behavior (check `FleetListViewModel` default values)

**Changing function signature:**
- Would require updating `FleetListViewModel._refresh()`
- Would require updating all test cases

---

## 8. Test Coverage

### 8.1 Direct Tests

**File:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

| Test Class | Tests |
|------------|-------|
| `TestFilterShips` | 5 tests (show_all, hide_damaged, hide_undamaged, hide_derelict, hide_destroyed) |
| `TestFilterShipsWarp` | 3 tests (hide warp capable, hide not warp capable, show all) |
| `TestFilterShipsSpaceyard` | 3 tests (hide has yard, hide no yard, show all) |
| `TestFilterShipsCargo` | 5 tests (hide has cargo, hide no cargo, population, zero values, show all) |
| `TestSpecialCapabilityFilter` | 3 tests (hide ships with ability, hide ships without, default shows all) |

### 8.2 Integration Tests

**File:** `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`

Tests the end-to-end flow through `FleetListViewModel` which internally calls `filter_ships`.

---

## 9. Complexity Analysis

### 9.1 Current Complexity Metrics

**Lines:** ~100 (lines 124-222)

**Control Flow:**
- Main loop: `for ship in ships`
- Multiple filter checks with early `continue`
- Nested loop for special capability columns
- Mutually exclusive status checks (destroyed -> derelict -> damaged -> undamaged)

### 9.2 Potential Refactoring Targets

1. **Extract filter predicates** - Each filter check could be a separate predicate function
2. **Filter configuration object** - Instead of Dict[str, bool], use a typed configuration class
3. **Strategy pattern** - Each filter type could be a pluggable filter strategy

---

## 10. Conclusions

1. **Safe to refactor internally** - Only one caller, clear contract
2. **Interface should remain stable** - Dict-based filter_state is flexible
3. **No side effects** - Pure function, safe for parallel use
4. **Well tested** - Comprehensive test coverage exists
5. **Complexity is manageable** - Clear structure, but could benefit from predicate extraction
