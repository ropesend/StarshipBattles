# Safety Analysis: filter_ships Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (target threshold: 15)

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a `filter_state` dictionary containing boolean flags. It handles multiple filter categories:

1. **Warp capability** (show_warp_capable, show_not_warp_capable)
2. **Spaceyard capability** (show_has_spaceyard, show_no_spaceyard)
3. **Cargo presence** (show_has_cargo, show_no_cargo)
4. **Special capabilities** (5 ability types: DestroyPlanet, OpenWarpPoint, CloseWarpPoint, DestroyStar, CreateSphereWorld)
5. **Ship status** (show_destroyed, show_derelict, show_damaged, show_undamaged)

---

## 2. Test Coverage Analysis

### 2.1 Existing Test Classes

| Test Class | Tests | Coverage Area |
|------------|-------|---------------|
| `TestFilterShips` | 5 | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 5 | Cargo filtering including population and zero values |
| `TestSpecialCapabilityFilter` | 3 | Special ability filtering (DestroyPlanet) |

**Total: 19 tests** - All passing.

### 2.2 Well-Tested Paths

- Basic filter states (show_damaged=True/False, etc.)
- Warp capable vs not warp capable
- Spaceyard has/no filtering
- Cargo presence with edge case (zero values treated as no cargo)
- Special capability filtering (has ability vs doesn't have ability)
- Default filter state shows all ships

### 2.3 Missing Test Coverage (CRITICAL)

1. **Empty ships list** - No test verifies `filter_ships([], filter_state)` returns empty list.

2. **Multiple filter combinations** - No tests verify that multiple filters work correctly together (e.g., `show_damaged=False AND show_warp_capable=False`).

3. **Filter order independence** - No tests verify that the order of filter application doesn't affect results.

4. **All filters disabled** - No test for when ALL filters are False (should return empty list).

5. **Missing filter keys in state** - The function uses `.get(key, True)` defaulting to True. No tests verify behavior when filter_state is partial or empty.

6. **Special capability filters for all 5 abilities** - Only `can_destroy_planet` is tested. Missing tests for:
   - `can_open_warp` / `no_open_warp`
   - `can_close_warp` / `no_close_warp`
   - `can_destroy_star` / `no_destroy_star`
   - `can_create_sphere` / `no_create_sphere`

7. **Derelict is mutually exclusive with damaged** - The code checks derelict before damaged (line 203-208). A derelict ship never reaches the damaged check. No test verifies this mutual exclusivity.

8. **Destroyed ships skip all other status filters** - Once `is_alive=False` is detected, the ship is appended (if filter allows) and continues to next ship. No test verifies destroyed ships don't also get filtered by damaged/undamaged.

---

## 3. Invariants That Must Be Preserved

### 3.1 Filter Priority Chain (CRITICAL)

The function evaluates filters in a specific order:
```
1. Warp capability
2. Spaceyard capability
3. Cargo presence
4. Special capabilities (all 5 types)
5. Destroyed status
6. Derelict status
7. Damaged status
8. Undamaged (default path)
```

**Invariant:** A ship can only match ONE status category (destroyed > derelict > damaged > undamaged). The first match that passes its filter adds the ship to results.

### 3.2 Default Filter Behavior

**Invariant:** Missing keys in `filter_state` default to `True` (show all). This is implemented via `filter_state.get(key, True)`.

### 3.3 Early Exit on Capability Filters

**Invariant:** If warp/spaceyard/cargo/special capability filters exclude a ship, that ship never reaches the status filters. The `continue` statements skip directly to the next ship.

### 3.4 Cargo Zero-Value Handling

**Invariant:** `cargo_contents` with all zero values is treated as "no cargo" (line 170):
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```

### 3.5 Special Capability Filter Key Derivation

**Invariant:** Filter keys are derived from column IDs using string manipulation (line 182-183):
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
```
For `can_destroy_planet`, this becomes `show_can_destroy_planet` and `show_no_destroy_planet`.

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Filter Order Dependency

The mutual exclusivity of status categories (destroyed > derelict > damaged > undamaged) is implemented via the order of if-statements. Refactoring to a different structure (e.g., dictionary-based dispatch, list comprehension) must preserve this priority.

**Risk:** Breaking the priority could cause:
- Destroyed ships appearing as "damaged"
- Derelict ships being filtered twice
- Undamaged ships passing through the wrong branch

### 4.2 HIGH RISK: Late Imports

The function uses late imports inside the loop body (lines 159, 185):
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Risk:** These are performance-sensitive. Moving imports to module level could cause circular import issues. Keeping them inside the loop is intentional.

### 4.3 MEDIUM RISK: The `_skip` Flag Pattern

Lines 177-194 use a `_skip` flag and `break` statement for special capability filtering. This is fragile:
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if has_ability and not show_has:
        _skip = True
        break
if _skip:
    continue
```

**Risk:** Refactoring this nested loop incorrectly could:
- Skip checking all special capabilities
- Fail to break early when a filter excludes the ship
- Mishandle the `_skip` flag state

### 4.4 MEDIUM RISK: Boolean Logic Complexity

Each filter category follows the pattern:
```python
if not show_X or not show_not_X:
    is_X = <expensive_check>
    if is_X and not show_X:
        continue
    if not is_X and not show_not_X:
        continue
```

**Risk:** This double-negative logic is error-prone. Refactoring must preserve the "skip expensive check when both filters are True" optimization.

### 4.5 LOW RISK: SPECIAL_CAPABILITY_COLUMNS Dependency

The function imports `SPECIAL_CAPABILITY_COLUMNS` from `fleet_data_source.py`. This is a dictionary mapping column IDs to ability names. Changes to that dictionary affect filter behavior.

---

## 5. Recommendations

### 5.1 Tests to Add BEFORE Refactoring

```python
# 1. Empty list handling
def test_filter_empty_list():
    result = filter_ships([], {'show_damaged': True, ...})
    assert result == []

# 2. Multiple filter combinations
def test_filter_multiple_filters_combined():
    """Test damaged + warp_capable filters together."""
    ships = [
        make_mock_ship(is_damaged=True, warp_tonnage=1500),   # damaged, warp
        make_mock_ship(is_damaged=True, warp_tonnage=None),   # damaged, no warp
        make_mock_ship(is_damaged=False, warp_tonnage=1500),  # undamaged, warp
    ]
    filter_state = {
        'show_damaged': True,
        'show_undamaged': False,
        'show_warp_capable': False,
        'show_not_warp_capable': True,
        ...
    }
    result = filter_ships(ships, filter_state)
    # Only damaged + no warp should remain
    assert len(result) == 1

# 3. Partial filter_state (missing keys)
def test_filter_partial_state_defaults_to_show():
    ships = [make_mock_ship(is_damaged=True)]
    result = filter_ships(ships, {})  # Empty state
    assert len(result) == 1  # Should show all

# 4. All filters disabled
def test_filter_all_disabled_returns_empty():
    ships = [make_mock_ship()]
    filter_state = {k: False for k in ['show_damaged', 'show_undamaged', ...]}
    result = filter_ships(ships, filter_state)
    assert result == []

# 5. Derelict/damaged mutual exclusivity
def test_derelict_not_also_filtered_as_damaged():
    """Derelict ship should only be checked against derelict filter."""
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {
        'show_derelict': True,
        'show_damaged': False,  # Would exclude if checked
        ...
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 1  # Should pass derelict filter

# 6. Other special capability filters
def test_filter_open_warp_capability():
    """Test can_open_warp filter."""
    # Similar to test_filter_hides_ships_with_ability but for OpenWarpPoint
```

### 5.2 Refactoring Approach

**Recommended Strategy: Extract Helper Functions**

1. Extract each filter category into a separate predicate function:
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filters(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`

2. The main function becomes:
   ```python
   def filter_ships(ships, filter_state):
       return [
           ship for ship in ships
           if _passes_warp_filter(ship, filter_state)
           and _passes_spaceyard_filter(ship, filter_state)
           and _passes_cargo_filter(ship, filter_state)
           and _passes_special_capability_filters(ship, filter_state)
           and _passes_status_filter(ship, filter_state)
       ]
   ```

3. Each helper function handles its own late imports and logic.

**Benefits:**
- Each helper is testable in isolation
- Complexity distributed across smaller functions
- Main function becomes declarative
- Preserves filter order and early-exit semantics

---

## 6. Refactorability Assessment

| Criterion | Assessment |
|-----------|------------|
| Test Coverage | FAIR - 19 tests exist, but missing critical combinations |
| Complexity Source | Filter categories and boolean logic |
| Extraction Safety | MODERATE - requires careful handling of filter priority |
| Risk Level | MEDIUM - well-tested happy paths, missing edge cases |

### Verdict: REFACTORABLE WITH PREREQUISITES

**Prerequisites before refactoring:**
1. Add tests for empty list handling
2. Add tests for multiple filter combinations
3. Add tests for partial/empty filter_state
4. Add tests verifying derelict/damaged mutual exclusivity
5. Add tests for remaining 4 special capability types

**Estimated test additions:** 6-8 new test cases.

Once prerequisites are met, the function can be safely refactored using the helper function extraction approach.
