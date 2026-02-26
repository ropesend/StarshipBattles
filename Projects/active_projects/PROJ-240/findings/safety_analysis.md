# Safety Analysis: filter_ships Function

**Target File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Analysis Date:** 2026-02-26

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter states. It supports filtering by:
- **Ship status:** damaged, undamaged, derelict, destroyed
- **Capabilities:** warp-capable, has spaceyard
- **Cargo:** has cargo, no cargo
- **Special abilities:** can destroy planet, can open/close warp, can destroy star, can create sphere

### Function Signature
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
```

---

## 2. Test Coverage Analysis

### Existing Test Coverage (Excellent)
Location: `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

| Test Class | Coverage |
|------------|----------|
| `TestFilterShips` | Basic filters (damaged, undamaged, derelict, destroyed, show all) |
| `TestFilterShipsWarp` | Warp capability filtering (hide warp, hide non-warp, show all) |
| `TestFilterShipsSpaceyard` | Spaceyard filtering (hide has yard, hide no yard, show all) |
| `TestFilterShipsCargo` | Cargo filtering including population, zero-value edge case |
| `TestSpecialCapabilityFilter` | Special abilities (destroy planet, etc.) |

**Total filter_ships tests:** ~20 tests covering most filter combinations.

### Integration Test Coverage
Location: `C:\Dev\Starship Battles\tests\unit\ui\test_fleet_list_view_model.py`
- Tests `FleetListViewModel.get_filtered_ships()` which calls `filter_ships`
- Covers filter toggling and combined filter scenarios

---

## 3. Edge Cases and Error Handling

### Handled Edge Cases (Good)
1. **Empty filter_state dict:** Uses `.get()` with default `True` for all filters
2. **Empty ships list:** Returns empty list (implicit via loop)
3. **Cargo with zero values:** Explicitly handled - `sum(ship.cargo_contents.values()) > 0`
4. **Derelict vs Damaged priority:** Derelict checked before damaged (lines 203-208)
5. **Destroyed before alive status:** Destroyed checked first (lines 197-201)

### Potential Edge Cases to Verify
1. **None in cargo_contents values:** `sum()` would fail if values contain None
2. **ship.cargo_contents is None:** Line 170 assumes dict exists - `bool(ship.cargo_contents)` protects this
3. **SPECIAL_CAPABILITY_COLUMNS dependency:** Relies on external module `fleet_data_source.py`

---

## 4. Invariants That Must Be Preserved

### Critical Invariants

1. **Filter Priority Order:**
   ```
   Warp filter -> Spaceyard filter -> Cargo filter -> Special abilities ->
   Destroyed -> Derelict -> Damaged -> Undamaged
   ```
   The order matters because ships can be in multiple states. A destroyed ship should not be checked for damage.

2. **Default True Behavior:**
   All filters default to `True` (show) when not specified in filter_state.
   ```python
   filter_state.get('show_xxx', True)  # Must remain True default
   ```

3. **Mutual Exclusivity of Status States:**
   - A ship is either: destroyed, derelict, damaged, or undamaged
   - The function uses `continue` to ensure a ship only falls into one category

4. **Filter Short-Circuit Logic:**
   If both positive and negative filters are True (e.g., `show_warp_capable=True` AND `show_not_warp_capable=True`), skip that filter entirely:
   ```python
   if not show_warp or not show_not_warp:  # Only check if either is False
   ```

5. **Import Location:**
   `FleetCapabilityCalculator` is imported inside the loop (late import). This is intentional to avoid circular imports.

---

## 5. External Dependencies

| Dependency | Usage | Risk |
|------------|-------|------|
| `ShipStatsCalculator.has_warp_capability(ship)` | Warp filter | Low - well-tested static method |
| `FleetCapabilityCalculator.ship_has_spaceyard(ship)` | Spaceyard filter | Low - static method |
| `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` | Special filters | Low - static method |
| `SPECIAL_CAPABILITY_COLUMNS` dict | Ability name mapping | Medium - changes here would break filter |

### ShipInstance API Contract
The function depends on these ShipInstance attributes/methods:
- `ship.is_alive` (bool property)
- `ship.is_derelict` (bool property)
- `ship.is_damaged()` (method returning bool)
- `ship.cargo_contents` (dict or None)

---

## 6. Risk Areas for Refactoring

### High Risk Areas

1. **Filter Order Logic (lines 197-220):**
   The sequential `if/continue` pattern for status filtering is subtle. The order (destroyed -> derelict -> damaged -> undamaged) is critical. Refactoring this into a different structure could break the mutual exclusivity.

2. **Special Capability Loop (lines 177-194):**
   The key derivation logic is complex:
   ```python
   show_has = filter_state.get(f'show_{col_id}', True)
   no_key = col_id.replace('can_', 'no_', 1)
   show_not = filter_state.get(f'show_{no_key}', True)
   ```
   The string manipulation (`replace('can_', 'no_', 1)`) is fragile.

3. **Late Imports:**
   Two late imports exist inside the loop for `FleetCapabilityCalculator`. Moving these outside the function could cause circular import issues.

### Medium Risk Areas

1. **Cargo Detection Logic (line 170):**
   ```python
   has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
   ```
   Assumes `cargo_contents` values are always numeric.

2. **Boolean Short-Circuit Pattern:**
   The pattern `if not show_x or not show_y:` is used consistently but could be misunderstood as "if either is false, check" when it means "skip check if both are true".

---

## 7. Missing Test Coverage

### Tests That Should Be Added BEFORE Refactoring

1. **Combined Filter Tests:**
   - Test filtering with multiple filters active simultaneously (e.g., hide damaged AND hide non-warp)
   - Test all filters set to False (should return empty list for undamaged ships)

2. **Edge Case Tests:**
   ```python
   def test_filter_with_none_cargo_contents():
       """Ship with cargo_contents=None should be treated as no cargo."""
       ship = make_mock_ship()
       ship.cargo_contents = None  # Not empty dict
       # Test should pass

   def test_filter_empty_ships_list():
       """Empty ships list returns empty result."""
       result = filter_ships([], {...})
       assert result == []

   def test_filter_all_filters_disabled():
       """All status filters False returns only ships that don't match any category."""
       # This is an impossible state - every ship is one of: destroyed, derelict, damaged, undamaged
       # Should return empty list
   ```

3. **Filter State Edge Cases:**
   ```python
   def test_filter_with_empty_filter_state():
       """Empty filter_state dict uses defaults (show all)."""
       result = filter_ships(ships, {})
       assert len(result) == len(ships)

   def test_filter_with_unknown_keys():
       """Unknown keys in filter_state are ignored."""
       result = filter_ships(ships, {'show_unknown': False})
       # Should not crash, should show all ships
   ```

4. **Performance Test:**
   ```python
   def test_filter_large_fleet():
       """Filter 1000+ ships in reasonable time."""
       ships = [make_mock_ship() for _ in range(1000)]
       # Time should be < 1 second
   ```

---

## 8. Refactorability Assessment

### Complexity Metrics
- **Lines of Code:** 99 lines (including docstring)
- **Cyclomatic Complexity:** High (~15) due to nested conditionals
- **Cognitive Complexity:** High - many filter conditions with subtle interactions

### Recommended Refactoring Approach

The function CAN be refactored but requires careful approach:

1. **Safe Refactoring Options:**
   - Extract each filter type into a helper function
   - Use a filter pipeline pattern (list of filter functions)
   - Extract the special capability loop into its own function

2. **Risky Refactoring Options:**
   - Changing the status filter order
   - Removing the `continue` statements in favor of boolean flags
   - Moving late imports to module level

### Verdict: PROCEED WITH CAUTION

**Refactorable:** Yes
**Pre-conditions Required:**
1. Add the missing edge case tests listed above
2. Ensure any refactoring preserves the filter order invariant
3. Keep late imports in their current location
4. Add regression tests for combined filter scenarios

---

## 9. Summary

| Category | Status |
|----------|--------|
| Test Coverage | Good - ~20 tests exist |
| Edge Case Handling | Good - most handled |
| Documentation | Good - docstring is accurate |
| External Dependencies | Low risk - stable APIs |
| Refactoring Risk | Medium - filter order is critical |

**Recommendation:** This function is safe to refactor with the following conditions:
1. Add 4-5 edge case tests before starting
2. Preserve filter evaluation order (warp -> spaceyard -> cargo -> special -> status)
3. Preserve status priority order (destroyed -> derelict -> damaged -> undamaged)
4. Keep late imports inside the function body
5. Run full test suite after each incremental change
