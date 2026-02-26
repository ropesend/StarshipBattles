# Dependency Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Current Cyclomatic Complexity:** 36

---

## 1. All Callers of filter_ships

### Direct Callers

| Caller File | Caller Class/Function | Line |
|-------------|----------------------|------|
| `game/ui/screens/fleet_report_view_model.py` | `FleetListViewModel._refresh()` | 215 |

### Call Chain

```
FleetReportWindow (UI)
  -> FleetListViewModel.get_filtered_ships()
     -> FleetListViewModel._refresh()
        -> filter_ships(ships, filter_state)
```

The function has exactly **one direct caller**: `FleetListViewModel._refresh()`.

---

## 2. Parameters and Return Values

### Function Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

### Parameters

**`ships: List[ShipInstance]`**
- Comes from `FleetListViewModel._ships` (line 215)
- Source: `FleetListViewModel.__init__()` or `update_ships()`
- List of ShipInstance objects from a fleet

**`filter_state: Dict[str, bool]`**
- Comes from `FleetListViewModel.get_filter_state()` (line 215)
- Dictionary with 20 boolean keys:
  - `show_damaged`, `show_undamaged`, `show_derelict`, `show_destroyed`
  - `show_warp_capable`, `show_not_warp_capable`
  - `show_has_spaceyard`, `show_no_spaceyard`
  - `show_has_cargo`, `show_no_cargo`
  - `show_can_destroy_planet`, `show_no_destroy_planet`
  - `show_can_open_warp`, `show_no_open_warp`
  - `show_can_close_warp`, `show_no_close_warp`
  - `show_can_destroy_star`, `show_no_destroy_star`
  - `show_can_create_sphere`, `show_no_create_sphere`

### Return Value Usage

The returned `List[ShipInstance]` is:
1. Passed to `sort_ships()` in `_refresh()` (line 218)
2. Stored in `_filtered_ships` (line 218-222)
3. Returned via `get_filtered_ships()` (line 210)
4. Used by `FleetDataSource.get_ship_at_index()` for table rendering

---

## 3. Interface Stability Analysis

### Can the Interface Change?

**YES** - the interface can change with minimal impact because:

1. **Single caller**: Only `FleetListViewModel._refresh()` calls this function
2. **Co-located code**: Caller and function are in the same `ui/screens/` package
3. **Internal implementation detail**: The function is not part of any public API
4. **Test isolation**: Tests import directly from `fleet_report_filters` and can be updated alongside

### Interface Change Considerations

| Change Type | Impact | Effort |
|-------------|--------|--------|
| Add parameter | Low - single call site | Update 1 file + tests |
| Change return type | Low - caller immediately uses result | Update 1 file + tests |
| Split into multiple functions | Low - update single call site | Update 1 file + tests |
| Extract to separate module | Medium - update imports | Update 2-3 files |

### Recommendation

The interface can be safely modified. Consider:
- Splitting filter logic into smaller functions (one per filter category)
- Keeping the same external signature while refactoring internals
- Or introducing a `FilterChain` pattern if complexity warrants

---

## 4. Side Effects and State Mutations

### Side Effects: **NONE**

The function is a **pure function**:
- Takes input parameters
- Returns a new list
- Does not modify the input `ships` list
- Does not modify any external state
- Does not call any I/O functions

### Late Imports (Deferred Dependencies)

The function uses late imports to avoid circular dependencies:
- Line 159: `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator`
- Line 185: Same import (second occurrence in special capabilities loop)

These imports happen **conditionally** only when spaceyard/special capability filters are active.

### Dependencies Called

| Dependency | Purpose | Called When |
|------------|---------|-------------|
| `ShipStatsCalculator.has_warp_capability()` | Check warp ability | Warp filters not both True |
| `FleetCapabilityCalculator.ship_has_spaceyard()` | Check spaceyard | Spaceyard filters not both True |
| `FleetCapabilityCalculator.ship_has_ability()` | Check special abilities | Special filters not both True |
| `SPECIAL_CAPABILITY_COLUMNS` (constant) | Ability name mapping | Special filter iteration |

### Ship Attributes Accessed

```python
ship.is_alive           # Destroyed check
ship.is_derelict        # Derelict check
ship.is_damaged()       # Damaged check (method)
ship.cargo_contents     # Cargo check (dict property)
```

---

## 5. Test Coverage

### Dedicated Test File

**`tests/unit/ui/screens/test_fleet_report_filters.py`**

### Test Classes for filter_ships

| Test Class | Line | Description |
|------------|------|-------------|
| `TestFilterShips` | 195 | Basic status filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 345 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 588 | Spaceyard filtering |
| `TestFilterShipsCargo` | 672 | Cargo filtering |
| `TestSpecialCapabilityFilter` | 796 | Special ability filtering (BUG-83) |

### Test Coverage Summary

| Filter Category | Tests | Coverage |
|-----------------|-------|----------|
| Show all filters | 1 | Show all ships when all filters True |
| Hide damaged | 1 | Excludes damaged ships |
| Hide undamaged | 1 | Excludes undamaged ships |
| Hide derelict | 1 | Excludes derelict ships |
| Hide destroyed | 1 | Excludes destroyed ships |
| Warp capable | 3 | Hide warp, hide non-warp, show all |
| Spaceyard | 3 | Hide has-yard, hide no-yard, show all |
| Cargo | 5 | Hide has-cargo, hide no-cargo, population as cargo, zero value, show all |
| Special abilities | 3 | Hide with ability, hide without ability, default shows all |

**Total filter_ships tests: ~19 test methods**

### Additional ViewModel Tests

**`tests/unit/ui/test_fleet_list_view_model.py`**
- Tests `FleetListViewModel` which wraps `filter_ships`
- Tests filter toggle behavior
- Tests filter state dictionary generation
- Indirectly tests filter_ships integration

---

## 6. Complexity Breakdown

The cyclomatic complexity of 36 comes from:

| Filter Category | Branches | Complexity Source |
|-----------------|----------|-------------------|
| Warp capability | 4 | Two filters + two capability checks |
| Spaceyard | 4 | Two filters + two capability checks |
| Cargo | 4 | Two filters + two cargo checks |
| Special capabilities | ~10 | Loop over 5 abilities x 2 filter checks |
| Status (destroyed) | 2 | Filter check + append |
| Status (derelict) | 2 | Filter check + append |
| Status (damaged) | 2 | Filter check + append |
| Status (undamaged) | 2 | Filter check + append |
| Main loop | 1 | For loop |
| Empty ship check | 1 | `if not show_warp or not show_not_warp` |

### Recommended Refactoring Approach

1. **Extract filter predicates** - One predicate function per filter category
2. **Chain predicates** - Build a list of active filters, apply in sequence
3. **Use strategy pattern** - Each filter as a pluggable strategy

Example structure:
```python
def filter_ships(ships, filter_state):
    predicates = [
        _make_warp_predicate(filter_state),
        _make_spaceyard_predicate(filter_state),
        _make_cargo_predicate(filter_state),
        _make_special_predicate(filter_state),
        _make_status_predicate(filter_state),
    ]
    return [s for s in ships if all(p(s) for p in predicates if p)]
```

---

## 7. Key Findings Summary

| Aspect | Finding |
|--------|---------|
| **Callers** | Single caller: `FleetListViewModel._refresh()` |
| **Interface stability** | Safe to modify - one call site, internal function |
| **Side effects** | None - pure function |
| **Test coverage** | Comprehensive - ~19 dedicated tests + integration tests |
| **Complexity source** | Many independent filter categories with similar patterns |
| **Refactoring risk** | Low - well-tested, single caller, no side effects |

---

## 8. File References

| File | Purpose |
|------|---------|
| `game/ui/screens/fleet_report_filters.py` | Source file containing `filter_ships` |
| `game/ui/screens/fleet_report_view_model.py` | Sole caller |
| `game/ui/screens/fleet_data_source.py` | Defines `SPECIAL_CAPABILITY_COLUMNS` constant |
| `game/strategy/services/ship_stats_calculator.py` | `has_warp_capability()` dependency |
| `game/strategy/data/fleet_capability_calculator.py` | Spaceyard/ability dependencies |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Primary test file |
| `tests/unit/ui/test_fleet_list_view_model.py` | ViewModel integration tests |
