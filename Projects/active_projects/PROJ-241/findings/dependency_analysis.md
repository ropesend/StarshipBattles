# Dependency Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Analysis Date:** 2026-02-26

---

## 1. Function Signature

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ships` | `List[ShipInstance]` | List of ship instances to filter |
| `filter_state` | `Dict[str, bool]` | Dictionary with filter boolean flags |

### Return Value

| Type | Description |
|------|-------------|
| `List[ShipInstance]` | Filtered list of ships matching the active filter criteria |

### Filter State Keys

The `filter_state` dictionary supports the following keys (all default to `True` if not present):

| Key | Purpose |
|-----|---------|
| `show_damaged` | Include damaged ships |
| `show_undamaged` | Include undamaged ships |
| `show_derelict` | Include derelict ships |
| `show_destroyed` | Include destroyed ships |
| `show_warp_capable` | Include warp-capable ships |
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

---

## 2. Callers Analysis

### Production Callers

| File | Location | Usage Pattern |
|------|----------|---------------|
| `game/ui/screens/fleet_report_view_model.py` | Line 215 | `filtered = filter_ships(self._ships, self.get_filter_state())` |

**Caller Details:**

The only production caller is `FleetListViewModel._refresh()` in `fleet_report_view_model.py`:

```python
# Line 212-223
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

The `get_filter_state()` method (lines 171-199) constructs the filter dictionary from the view model's instance variables:

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

---

## 3. Internal Dependencies

### Imports Used by `filter_ships`

| Dependency | Import Location | Purpose |
|------------|-----------------|---------|
| `ShipStatsCalculator` | `game.strategy.services.ship_stats_calculator` | Warp capability check |
| `FleetCapabilityCalculator` | `game.strategy.data.fleet_capability_calculator` | Spaceyard/ability checks |
| `SPECIAL_CAPABILITY_COLUMNS` | `game.ui.screens.fleet_data_source` | Special ability column mappings |

### Late Imports (Inside Function)

The function uses late imports to avoid circular dependencies:

```python
# Line 159-160 (inside loop)
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)

# Line 185-186 (inside loop)
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
```

### ShipInstance Interface Requirements

The function accesses the following `ShipInstance` properties and methods:

| Property/Method | Type | Used For |
|-----------------|------|----------|
| `is_alive` | `bool` | Destroyed filter |
| `is_derelict` | `bool` | Derelict filter |
| `is_damaged()` | `method -> bool` | Damaged filter |
| `cargo_contents` | `dict` | Cargo filter |

---

## 4. Test Coverage

### Test File

`C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

### Test Classes Covering `filter_ships`

| Test Class | Line | Purpose |
|------------|------|---------|
| `TestFilterShips` | 196 | Basic status filtering (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | 346 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 589 | Spaceyard capability filtering |
| `TestFilterShipsCargo` | 673 | Cargo filtering |
| `TestSpecialCapabilityFilter` | 797 | Special ability filtering (BUG-83) |

### Test Count

- **39 test methods** directly test `filter_ships` function
- Tests cover all filter state combinations
- Tests use mocked `ShipInstance` objects via `make_mock_ship()` helper

### Key Test Patterns

1. **Mock ships with `make_mock_ship()` helper:**
   ```python
   ship = make_mock_ship(is_damaged=True)
   ship = make_mock_ship(mass=1000, warp_tonnage=1500)  # warp capable
   ```

2. **Filter state dictionaries passed directly:**
   ```python
   filter_state = {
       'show_damaged': False,
       'show_undamaged': True,
       'show_derelict': True,
       'show_destroyed': True,
   }
   result = filter_ships(ships, filter_state)
   ```

3. **Mocked external dependencies:**
   ```python
   with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
       result = filter_ships(ships, filter_state)
   ```

---

## 5. Side Effects and State Mutations

### Side Effects: NONE

The `filter_ships` function is **pure** with respect to its inputs:
- Does NOT modify the input `ships` list
- Does NOT modify the `filter_state` dictionary
- Does NOT modify any `ShipInstance` objects
- Creates and returns a NEW list

### Global State Access

- Reads `SPECIAL_CAPABILITY_COLUMNS` constant (immutable)
- Calls static methods on `ShipStatsCalculator` and `FleetCapabilityCalculator`

### Thread Safety

The function is thread-safe as long as:
- The ship objects are not modified concurrently
- The calculator static methods are thread-safe (they appear to be read-only)

---

## 6. Interface Stability Assessment

### Can the Interface Change?

**Signature: STABLE - Cannot Change Easily**

| Aspect | Assessment | Reason |
|--------|------------|--------|
| Parameter types | Stable | `FleetListViewModel` depends on exact signature |
| Return type | Stable | Return value piped directly to `sort_ships` |
| Filter keys | Semi-stable | Adding new keys is safe; removing/renaming breaks `FleetListViewModel.get_filter_state()` |

### Coupling Analysis

**Tight Coupling:**
- `FleetListViewModel` constructs the exact filter state dict
- Filter keys in `filter_ships` must match keys in `get_filter_state()`
- Special capability filter keys derived from `SPECIAL_CAPABILITY_COLUMNS`

**To Change Interface Safely:**

1. **Adding new filter keys:** Safe - function uses `.get()` with defaults
2. **Removing filter keys:** Requires updating `FleetListViewModel.get_filter_state()` and related instance variables
3. **Changing parameter types:** Requires updating `FleetListViewModel._refresh()` call site
4. **Changing return type:** Would break `sort_ships()` call chain

### Recommendations for Interface Changes

If the interface must change:
1. Update `FleetListViewModel.get_filter_state()` simultaneously
2. Update all 20+ `filter_show_*` instance variables if filter keys change
3. Update `toggle_filter()` method in `FleetListViewModel`
4. Run full test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

---

## 7. Summary

| Metric | Value |
|--------|-------|
| Production Callers | 1 (`FleetListViewModel._refresh`) |
| Test Methods | 39 |
| Side Effects | None (pure function) |
| State Mutations | None |
| Late Imports | 2 (both `FleetCapabilityCalculator`) |
| Filter Keys | 20 |
| Interface Stability | High - tightly coupled to `FleetListViewModel` |

### Key Findings

1. **Single Caller Pattern:** Only `FleetListViewModel` calls this function, making it a private-like implementation detail of the view model layer.

2. **Pure Function:** No side effects, returns new list, safe for concurrent use.

3. **Extensible Design:** Uses `.get()` with defaults for all filter keys, allowing new filters to be added without breaking existing code.

4. **Tight ViewModel Coupling:** The filter state dictionary structure is tightly coupled to `FleetListViewModel` instance variables. Any changes require synchronized updates.

5. **Well-Tested:** Comprehensive test coverage with mocked dependencies.
