# Dependency Analysis: `filter_ships` Function

**Date:** 2026-02-26
**Target Function:** `filter_ships` in `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Project:** PROJ-229 (Reduce complexity: filter_ships CC 36)

---

## 1. Summary

The `filter_ships` function is a **pure filtering function** with a stable interface. It has:
- **1 direct caller** in production code
- **3 test files** with comprehensive coverage (19+ test cases)
- **No side effects** or state mutations
- A clear contract that should remain stable

**Complexity Rating:** Cyclomatic Complexity 36 (Grade F)
**Goal:** Reduce to CC < 20 while preserving all behavior

---

## 2. Files That Import or Call `filter_ships`

### 2.1 Production Code

| File | Import Statement | Usage |
|------|------------------|-------|
| `game\ui\screens\fleet_report_view_model.py` | `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` | Called in `_refresh()` method |

### 2.2 Related Files (import other functions from same module)

| File | Import Statement | Notes |
|------|------------------|-------|
| `game\ui\screens\fleet_report_sidebar.py` | `from game.ui.screens.fleet_report_filters import calculate_fleet_stats` | Only imports `calculate_fleet_stats`, not `filter_ships` |

### 2.3 Test Files

| File | Test Classes | Direct Tests |
|------|--------------|--------------|
| `tests\unit\ui\screens\test_fleet_report_filters.py` | `TestFilterShips`, `TestFilterShipsWarp`, `TestFilterShipsSpaceyard`, `TestFilterShipsCargo`, `TestSpecialCapabilityFilter` | 19 tests |
| `tests\unit\ui\test_fleet_list_view_model.py` | `TestFleetListViewModel`, `TestFleetListViewModelWarpFilters`, `TestFleetListViewModelSpaceyardFilters`, `TestFleetListViewModelCargoFilters` | Indirect via FleetListViewModel |
| `tests\unit\ui\screens\test_empire_build_queue_filter_manager.py` | N/A | No direct import; tests similar filtering pattern |

---

## 3. Function Signature and Contract

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """
    Filter ships based on status filter state.

    Args:
        ships: List of ShipInstance objects
        filter_state: Dict with keys:
            - show_damaged: Include damaged ships
            - show_undamaged: Include undamaged ships
            - show_derelict: Include derelict ships
            - show_destroyed: Include destroyed ships
            - show_warp_capable: Include warp-capable ships
            - show_not_warp_capable: Include ships without warp capability

    Returns:
        Filtered list of ships
    """
```

### 3.1 Parameters

**`ships: List[ShipInstance]`**
- Input list of `ShipInstance` objects
- Not mutated by the function

**`filter_state: Dict[str, bool]`**
- Dictionary of boolean flags controlling which ships to include
- All keys are optional - missing keys default to `True` (show matching ships)

#### Filter State Keys

| Key | Purpose | Default |
|-----|---------|---------|
| `show_damaged` | Include ships where `is_damaged() == True` | `True` |
| `show_undamaged` | Include ships where `is_damaged() == False` | `True` |
| `show_derelict` | Include ships where `is_derelict == True` | `True` |
| `show_destroyed` | Include ships where `is_alive == False` | `True` |
| `show_warp_capable` | Include ships with warp capability | `True` |
| `show_not_warp_capable` | Include ships without warp capability | `True` |
| `show_has_spaceyard` | Include ships with spaceyard | `True` |
| `show_no_spaceyard` | Include ships without spaceyard | `True` |
| `show_has_cargo` | Include ships with cargo | `True` |
| `show_no_cargo` | Include ships without cargo | `True` |
| `show_can_destroy_planet` | Include ships with DestroyPlanet ability | `True` |
| `show_no_destroy_planet` | Include ships without DestroyPlanet ability | `True` |
| `show_can_open_warp` | Include ships with OpenWarpPoint ability | `True` |
| `show_no_open_warp` | Include ships without OpenWarpPoint ability | `True` |
| `show_can_close_warp` | Include ships with CloseWarpPoint ability | `True` |
| `show_no_close_warp` | Include ships without CloseWarpPoint ability | `True` |
| `show_can_destroy_star` | Include ships with DestroyStar ability | `True` |
| `show_no_destroy_star` | Include ships without DestroyStar ability | `True` |
| `show_can_create_sphere` | Include ships with CreateSphereWorld ability | `True` |
| `show_no_create_sphere` | Include ships without CreateSphereWorld ability | `True` |

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

**FleetListViewModel Default Filter States (lines 36-57):**

Most filters default to `True` (show matching ships), except:
- `filter_show_destroyed = False` (destroyed ships hidden by default)

---

## 5. Dependencies of `filter_ships`

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

**`SPECIAL_CAPABILITY_COLUMNS` definition (from `fleet_data_source.py` lines 46-52):**

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

**Short Answer:** The interface SHOULD remain stable for refactoring purposes.

**Reasons:**
1. Only one direct caller in production code (`FleetListViewModel._refresh`)
2. The `filter_state` dictionary pattern is flexible - new keys can be added without breaking existing callers
3. Tests use the same dictionary pattern, so they are also resilient to new keys
4. Comprehensive test coverage validates current behavior

### 7.2 Recommended Approach for Changes

**Internal refactoring (SAFE):**
- Extract helper functions/predicates
- Restructure control flow
- Add private helper methods

**Adding new filter keys (SAFE):**
- Add new key to `FleetListViewModel.get_filter_state()` and corresponding attribute
- No changes needed to `filter_ships` signature

**Changing behavior of existing filter keys (REQUIRES TEST UPDATES):**
- Must update tests in `test_fleet_report_filters.py`
- May affect UI behavior (check `FleetListViewModel` default values)

**Changing function signature (BREAKING):**
- Would require updating `FleetListViewModel._refresh()`
- Would require updating all test cases
- **NOT RECOMMENDED for this refactoring project**

---

## 8. Test Coverage

### 8.1 Direct Tests in `test_fleet_report_filters.py`

| Test Class | Test Count | Coverage |
|------------|------------|----------|
| `TestFilterShips` | 5 | Basic status filtering (show_all, hide_damaged, hide_undamaged, hide_derelict, hide_destroyed) |
| `TestFilterShipsWarp` | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 5 | Cargo filtering (including population, zero values) |
| `TestSpecialCapabilityFilter` | 3 | Special ability filtering |

**Total: 19 direct test cases**

### 8.2 Integration Tests in `test_fleet_list_view_model.py`

| Test Class | Test Count | Coverage |
|------------|------------|----------|
| `TestFleetListViewModel` | 12 | End-to-end ViewModel tests |
| `TestFleetListViewModelWarpFilters` | 2 | Warp filter toggles |
| `TestFleetListViewModelSpaceyardFilters` | 5 | Spaceyard filter toggles |
| `TestFleetListViewModelCargoFilters` | 5 | Cargo filter toggles |

**Total: 24 integration test cases**

### 8.3 Related Tests

| Test Class | Notes |
|------------|-------|
| `TestViewModelSpecialFilters` | In `test_fleet_report_filters.py`, tests ViewModel special filter integration |
| `TestSpecialCapabilitySort` | Tests sorting by special capability columns |

---

## 9. Complexity Analysis

### 9.1 Current Complexity Metrics

**Lines:** ~99 (lines 124-222)
**Cyclomatic Complexity:** 36

**Control Flow Structure:**
1. Main loop: `for ship in ships` (1 path)
2. Warp capability filter: 4 branches
3. Spaceyard capability filter: 4 branches
4. Cargo filter: 4 branches
5. Special capability loop: `for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items()` with 4 branches per iteration (5 columns = 20 potential paths)
6. Destroyed filter: 2 branches
7. Derelict filter: 2 branches
8. Damaged filter: 2 branches
9. Undamaged filter: 1 branch

### 9.2 Sources of Complexity

1. **Multiple filter categories** - Each filter category (warp, spaceyard, cargo, special, status) adds branches
2. **Paired filters** - Each capability has show/hide variants (e.g., `show_warp_capable` AND `show_not_warp_capable`)
3. **Early continue pattern** - Multiple `continue` statements create branching
4. **Nested loop for special capabilities** - Iterates over `SPECIAL_CAPABILITY_COLUMNS`
5. **Mutually exclusive status checks** - Destroyed -> Derelict -> Damaged -> Undamaged chain

### 9.3 Potential Refactoring Strategies

1. **Extract filter predicates** - Each filter check could be a separate predicate function
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - etc.

2. **Compose filters** - Use functional composition to build a filter chain
   ```python
   predicates = [
       _warp_filter(filter_state),
       _cargo_filter(filter_state),
       _status_filter(filter_state),
   ]
   return [ship for ship in ships if all(p(ship) for p in predicates)]
   ```

3. **Filter configuration object** - Replace `Dict[str, bool]` with typed class
   - Better IDE support
   - Clearer documentation
   - **Note:** Requires interface change, NOT recommended for this project

4. **Table-driven approach** - Define filter rules in a data structure
   ```python
   FILTERS = [
       ('warp_capable', 'not_warp_capable', lambda s: has_warp_capability(s)),
       ('has_spaceyard', 'no_spaceyard', lambda s: ship_has_spaceyard(s)),
       # ...
   ]
   ```

---

## 10. Conclusions

### 10.1 Key Findings

1. **Safe to refactor internally** - Only one caller, clear contract, pure function
2. **Interface should remain stable** - Dict-based `filter_state` is flexible
3. **No side effects** - Pure function, safe for any restructuring
4. **Well tested** - 19 direct tests + 24 integration tests = comprehensive coverage
5. **Complexity is tractable** - Clear structure with identifiable patterns

### 10.2 Recommendations for PROJ-229

1. **Preserve the function signature** - `filter_ships(ships, filter_state) -> List[ShipInstance]`
2. **Extract helper predicates** - Move each filter category to its own function
3. **Run tests frequently** - All 43+ related tests should pass after each change
4. **Document any skipped complexity** - If some complexity is irreducible, document in decisions.md

### 10.3 Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing behavior | Low | Comprehensive test coverage |
| Changing public interface | None | Not changing signature |
| Introducing bugs | Low | TDD approach with existing tests |
| Over-engineering | Medium | Set clear CC target (<20), stop when reached |
