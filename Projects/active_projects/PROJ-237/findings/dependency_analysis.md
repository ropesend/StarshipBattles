# Dependency Analysis: `filter_ships` Function

**Source File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`
**Analysis Date:** 2026-02-26

---

## 1. Caller List

### Production Callers

| Location | File | Line | Usage Pattern |
|----------|------|------|---------------|
| `FleetListViewModel._refresh()` | `game/ui/screens/fleet_report_view_model.py` | 215 | Primary caller - filters ships before sorting |

**Import Statement (line 10):**
```python
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships
```

### Call Site Details

**`fleet_report_view_model.py:215`**
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

---

## 2. Interface Analysis

### Function Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Parameters Passed

**`ships` parameter:**
- Type: `List[ShipInstance]` (from `game.strategy.data.ship_instance`)
- Source: `FleetListViewModel._ships` - stored list of ships
- Immutable: The list itself is not modified; a new list is returned

**`filter_state` parameter:**
- Type: `Dict[str, bool]`
- Source: `FleetListViewModel.get_filter_state()` method
- Expected Keys (20 total):
  - Status filters: `show_damaged`, `show_undamaged`, `show_derelict`, `show_destroyed`
  - Warp filters: `show_warp_capable`, `show_not_warp_capable`
  - Spaceyard filters: `show_has_spaceyard`, `show_no_spaceyard`
  - Cargo filters: `show_has_cargo`, `show_no_cargo`
  - Special capability filters (5 pairs):
    - `show_can_destroy_planet`, `show_no_destroy_planet`
    - `show_can_open_warp`, `show_no_open_warp`
    - `show_can_close_warp`, `show_no_close_warp`
    - `show_can_destroy_star`, `show_no_destroy_star`
    - `show_can_create_sphere`, `show_no_create_sphere`

### Return Value Usage
- Returns a new `List[ShipInstance]` containing only ships that pass all filters
- Passed directly to `sort_ships()` function for subsequent sorting
- Final result stored in `FleetListViewModel._filtered_ships`

### Interface Stability Assessment

**STABLE - Interface changes require coordinated updates**

1. **Tight Coupling:** `FleetListViewModel.get_filter_state()` returns a dict with specific keys that must match what `filter_ships` expects
2. **Single Consumer:** Only one production caller (`FleetListViewModel._refresh`)
3. **Key Name Contract:** Adding/removing filter keys requires changes in:
   - `FleetListViewModel` (filter attributes and `get_filter_state()`)
   - `filter_ships()` implementation
   - Test files

**Recommendation:** Interface can be modified, but changes must update:
- `FleetListViewModel.get_filter_state()` (produces the dict)
- Test mocks and filter_state dicts in test files

---

## 3. Side Effects and State Mutations

### Side Effects: NONE (Pure Function)

The `filter_ships` function is a **pure function** with no side effects:

1. **No External State Mutation:**
   - Does not modify the input `ships` list
   - Does not modify any ship objects
   - Does not modify any global or module-level state

2. **Read-Only Operations:**
   - Reads ship attributes: `is_alive`, `is_derelict`, `cargo_contents`
   - Calls ship methods: `is_damaged()`
   - Uses `ShipStatsCalculator.has_warp_capability()` (static, read-only)
   - Uses `FleetCapabilityCalculator.ship_has_spaceyard()` (static, read-only)
   - Uses `FleetCapabilityCalculator.ship_has_ability()` (static, read-only)

3. **New List Creation:**
   - Creates and returns a new list (`result = []`)
   - Appends references to existing ship objects (not copies)

### Late Imports

The function uses intentional late imports to avoid circular dependencies:
```python
# Line 159, 185 (inside loop):
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

This is only imported when spaceyard or special capability filters are active (optimization).

---

## 4. Test Coverage Summary

### Test File
**Location:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Direct Test Classes for `filter_ships`

| Test Class | Line | Test Cases | Description |
|------------|------|------------|-------------|
| `TestFilterShips` | 196 | 5 | Basic status filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 346 | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 589 | 3 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 673 | 6 | Cargo filtering including edge cases |
| `TestSpecialCapabilityFilter` | 797 | 3 | Special ability filtering (destroy planet, etc.) |

### Test Case Breakdown

**TestFilterShips (5 tests):**
1. `test_filter_show_all` - All filters enabled returns all ships
2. `test_filter_hide_damaged` - Hiding damaged ships
3. `test_filter_hide_undamaged` - Hiding undamaged ships
4. `test_filter_hide_derelict` - Hiding derelict ships
5. `test_filter_hide_destroyed` - Hiding destroyed ships

**TestFilterShipsWarp (3 tests):**
1. `test_filter_hide_warp_capable` - Hide warp-capable ships
2. `test_filter_hide_not_warp_capable` - Hide non-warp-capable ships
3. `test_filter_show_all_warp_states` - Both warp filters enabled

**TestFilterShipsSpaceyard (3 tests):**
1. `test_filter_hide_has_spaceyard` - Hide ships with spaceyards
2. `test_filter_hide_no_spaceyard` - Hide ships without spaceyards
3. `test_filter_show_all_spaceyard_states` - Both spaceyard filters enabled

**TestFilterShipsCargo (6 tests):**
1. `test_filter_hide_has_cargo` - Hide ships with cargo
2. `test_filter_hide_no_cargo` - Hide ships without cargo
3. `test_filter_cargo_with_population` - Population counts as cargo
4. `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero values = no cargo
5. `test_filter_show_all_cargo_states` - Both cargo filters enabled
6. Additional edge case tests

**TestSpecialCapabilityFilter (3 tests):**
1. `test_filter_hides_ships_with_ability` - Hide ships with special ability
2. `test_filter_hides_ships_without_ability` - Hide ships without special ability
3. `test_filter_default_shows_all` - Default shows all regardless of abilities

### Related Integration Tests

**File:** `tests/unit/ui/test_fleet_list_view_model.py`
- Tests `FleetListViewModel` which uses `filter_ships` internally
- Validates end-to-end filtering through the view model
- 30+ test methods covering filter toggles and state management

### Coverage Assessment

| Filter Type | Covered | Notes |
|-------------|---------|-------|
| Status (damaged/undamaged/derelict/destroyed) | Yes | Full coverage |
| Warp capability | Yes | Full coverage |
| Spaceyard | Yes | Uses mocks for capability check |
| Cargo | Yes | Including edge cases (zero values, population) |
| Special capabilities | Partial | Tests one ability (DestroyPlanet), relies on loop logic for others |

**Coverage Gaps:**
- No explicit tests for combination filters (e.g., warp + cargo + damaged)
- Special capability tests cover DestroyPlanet but not all 5 abilities explicitly

---

## 5. Dependencies Graph

```
filter_ships()
    |
    +-- ShipStatsCalculator.has_warp_capability() [read-only]
    |       (from game.strategy.services.ship_stats_calculator)
    |
    +-- FleetCapabilityCalculator.ship_has_spaceyard() [read-only, late import]
    |       (from game.strategy.data.fleet_capability_calculator)
    |
    +-- FleetCapabilityCalculator.ship_has_ability() [read-only, late import]
    |       (from game.strategy.data.fleet_capability_calculator)
    |
    +-- SPECIAL_CAPABILITY_COLUMNS [constant dict]
            (from game.ui.screens.fleet_data_source)
```

---

## 6. Summary

| Aspect | Assessment |
|--------|------------|
| **Caller Count** | 1 production caller (`FleetListViewModel`) |
| **Interface Stability** | STABLE but coupled to `get_filter_state()` contract |
| **Side Effects** | NONE - Pure function |
| **State Mutations** | NONE - Returns new list, doesn't modify inputs |
| **Test Coverage** | GOOD - 20+ direct tests covering all filter types |
| **Refactoring Risk** | LOW - Single caller, comprehensive tests |
| **Dependencies** | 3 external services (all read-only static methods) |
