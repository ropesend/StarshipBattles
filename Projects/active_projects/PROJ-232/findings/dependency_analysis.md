# Dependency Analysis: filter_ships Function

**Source File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Function Signature:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. All Callers of This Function

### Production Code Callers

| File | Line | Usage |
|------|------|-------|
| `game/ui/screens/fleet_report_view_model.py` | 10 | Import: `from game.ui.screens.fleet_report_filters import filter_ships, sort_ships` |
| `game/ui/screens/fleet_report_view_model.py` | 215 | Call: `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Summary:** There is exactly **ONE production caller** - the `FleetListViewModel._refresh()` method.

### Test Code Callers

| File | Test Class/Method | Usage Pattern |
|------|------------------|---------------|
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShips` (5 test methods) | Direct import and call |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsWarp` (3 test methods) | Direct import and call |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsSpaceyard` (3 test methods) | Direct import and call with mocks |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestFilterShipsCargo` (6 test methods) | Direct import and call |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | `TestSpecialCapabilityFilter` (3 test methods) | Direct import and call with mocks |

---

## 2. Parameters and Return Value Usage

### Input Parameters

**`ships: List[ShipInstance]`**
- Source: `FleetListViewModel._ships` (internal ship list)
- Populated via: `FleetListViewModel.__init__(ships)` or `FleetListViewModel.update_ships(ships)`

**`filter_state: Dict[str, bool]`**
- Source: `FleetListViewModel.get_filter_state()` (lines 171-199)
- Expected keys (all boolean, default True except `show_destroyed`):
  - `show_damaged` - Include damaged ships
  - `show_undamaged` - Include undamaged ships
  - `show_derelict` - Include derelict ships
  - `show_destroyed` - Include destroyed ships (default False)
  - `show_warp_capable` - Include warp-capable ships
  - `show_not_warp_capable` - Include ships without warp capability
  - `show_has_spaceyard` - Include ships with spaceyards
  - `show_no_spaceyard` - Include ships without spaceyards
  - `show_has_cargo` - Include ships with cargo
  - `show_no_cargo` - Include ships without cargo
  - `show_can_destroy_planet` / `show_no_destroy_planet` - Planet destroyer filter
  - `show_can_open_warp` / `show_no_open_warp` - Warp opener filter
  - `show_can_close_warp` / `show_no_close_warp` - Warp closer filter
  - `show_can_destroy_star` / `show_no_destroy_star` - Star destroyer filter
  - `show_can_create_sphere` / `show_no_create_sphere` - Sphere builder filter

### Return Value

**`List[ShipInstance]`**
- A new list containing only ships that pass all active filters
- Consumed by `FleetListViewModel._refresh()` which then passes it to `sort_ships()`
- Final sorted result stored in `_filtered_ships` and returned via `get_filtered_ships()`

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**YES, with caution.** The interface can be modified because:

1. **Single Production Caller:** Only `FleetListViewModel._refresh()` calls this function
2. **Coordinated State:** Both the caller and filter_state generation are in the same module family
3. **Internal Function:** Not part of public API (not exported from `game/ui/screens/__init__.py`)

### Constraints on Changes

1. **Return Type Must Remain `List[ShipInstance]`:** The return value feeds into `sort_ships()` which expects this type
2. **Filter Keys Are Coupled:** The `filter_state` dict keys must match what `get_filter_state()` produces
3. **Test Coverage Impact:** 20+ test methods directly test this function - changes require test updates
4. **Behavior Expectations:** Filter logic behavior is well-documented and tested

### Recommended Approach for Changes

- Modify `filter_state` dict keys? Update `FleetListViewModel.get_filter_state()` simultaneously
- Add new filter criteria? Add corresponding keys to view model filter state
- Change function signature? Only one call site to update, but many tests

---

## 4. Side Effects and State Mutations

### Side Effects: NONE

The function is **pure** - it has no side effects:

1. **No State Mutation:** Creates a new result list; does not modify input `ships` list
2. **No External State:** Does not modify any global or class-level state
3. **No I/O:** No file, network, or database operations
4. **Deterministic:** Same inputs always produce same outputs

### Dependencies with Potential Side Effects

The function imports these services lazily (inside conditionals):

1. **`ShipStatsCalculator.has_warp_capability(ship)`** (line 149)
   - Read-only calculation based on ship stats
   - No side effects

2. **`FleetCapabilityCalculator.ship_has_spaceyard(ship)`** (line 160)
   - Read-only capability check
   - No side effects
   - Imported inside conditional for lazy loading

3. **`FleetCapabilityCalculator.ship_has_ability(ship, ability_name)`** (line 186)
   - Read-only ability check
   - No side effects
   - Imported inside loop conditional

### Ship Object Access (Read-Only)

The function reads these ship attributes/methods:
- `ship.is_alive` - property
- `ship.is_derelict` - property
- `ship.is_damaged()` - method call
- `ship.cargo_contents` - property (dict)

All access is read-only.

---

## 5. Test Coverage

### Dedicated Test File

**`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`**

### Test Classes Covering filter_ships

| Test Class | Tests | Coverage Focus |
|------------|-------|----------------|
| `TestFilterShips` | 5 | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 6 | Cargo presence filtering |
| `TestSpecialCapabilityFilter` | 3 | Special ability filtering (planet destroyer, etc.) |

### Specific Test Methods for filter_ships

1. `test_filter_show_all` - All filters enabled shows all ships
2. `test_filter_hide_damaged` - Hide damaged ships
3. `test_filter_hide_undamaged` - Hide undamaged ships
4. `test_filter_hide_derelict` - Hide derelict ships
5. `test_filter_hide_destroyed` - Hide destroyed ships
6. `test_filter_hide_warp_capable` - Hide warp-capable ships
7. `test_filter_hide_not_warp_capable` - Hide non-warp-capable ships
8. `test_filter_show_all_warp_states` - Both warp filters enabled
9. `test_filter_hide_has_spaceyard` - Hide ships with spaceyards
10. `test_filter_hide_no_spaceyard` - Hide ships without spaceyards
11. `test_filter_show_all_spaceyard_states` - Both spaceyard filters enabled
12. `test_filter_hide_has_cargo` - Hide ships with cargo
13. `test_filter_hide_no_cargo` - Hide ships without cargo
14. `test_filter_cargo_with_population` - Population counts as cargo
15. `test_filter_cargo_zero_value_treated_as_no_cargo` - Zero values = no cargo
16. `test_filter_show_all_cargo_states` - Both cargo filters enabled
17. `test_filter_hides_ships_with_ability` - Hide ships with special ability
18. `test_filter_hides_ships_without_ability` - Hide ships without special ability
19. `test_filter_default_shows_all` - Default state shows all

### Integration Test Coverage

**`C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`**

Tests the `FleetListViewModel` which calls `filter_ships` internally:
- `test_get_filtered_ships_excludes_destroyed_by_default`
- `test_toggle_filter_destroyed`
- `test_toggle_filter_derelict`
- `test_filter_undamaged_only`

### Coverage Assessment

**EXCELLENT** - The function has:
- 20+ direct unit tests
- Multiple test classes organized by filter category
- Edge case coverage (zero values, defaults, all filters enabled)
- Integration tests via view model
- Mock-based isolation for external dependencies

---

## Summary

| Aspect | Status |
|--------|--------|
| **Production Callers** | 1 (FleetListViewModel._refresh) |
| **Test Callers** | 20+ test methods |
| **Interface Stability** | Modifiable with coordinated changes |
| **Side Effects** | None (pure function) |
| **Test Coverage** | Excellent |
| **External Dependencies** | 3 service calls (read-only) |
