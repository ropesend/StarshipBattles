# Safety Analysis: filter_ships Refactoring

## Target Function
- **File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Cyclomatic Complexity:** 36 (grade F)
- **Lines:** 99

## Function Behavior Summary

The `filter_ships` function filters a list of `ShipInstance` objects based on a `filter_state` dictionary. It implements multiple filter categories in sequence:

1. **Warp Capability Filter** (lines 143-153) - Filter by warp jump ability
2. **Spaceyard Capability Filter** (lines 155-164) - Filter by spaceyard presence
3. **Cargo Filter** (lines 166-174) - Filter by whether ship has cargo
4. **Special Capability Filters** (lines 176-194) - Dynamic filter for special abilities (DestroyPlanet, OpenWarpPoint, etc.)
5. **Ship Status Filters** (lines 196-220):
   - Destroyed filter (priority 1)
   - Derelict filter (priority 2)
   - Damaged filter (priority 3)
   - Undamaged filter (default)

## Critical Invariants

### 1. Filter Order / Status Priority (CRITICAL)
The ship status checks follow a **strict priority order** that MUST be preserved:
```
Destroyed > Derelict > Damaged > Undamaged
```

A ship that is destroyed is NOT also checked for derelict/damaged status. A derelict ship is NOT also checked for damaged status. This is because:
- Derelict implies damaged (see `is_damaged()` implementation)
- These are mutually exclusive display categories

**Risk:** Refactoring that changes the order of if/continue statements could cause ships to be categorized incorrectly.

### 2. Early Exit Pattern
The function uses `continue` statements for early exit after adding to result. Each status check:
1. Checks the condition
2. If filter is off, continues (skips ship)
3. If filter is on, appends to result and continues

**Risk:** Breaking the early-exit pattern could cause ships to be added multiple times or skip later filters.

### 3. Capability Filters Default to True
All capability filters (warp, spaceyard, cargo, special) default to `True` via `.get()`:
```python
filter_state.get('show_warp_capable', True)
```

**Risk:** Changing the default values would break existing usage.

### 4. Cargo Detection Logic
Cargo is detected by: `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`

This handles:
- Empty dict `{}` = no cargo
- Dict with zero values `{'minerals': 0}` = no cargo
- Dict with positive values `{'minerals': 50}` = has cargo

**Risk:** Simplifying to just `bool(ship.cargo_contents)` would incorrectly treat zero-cargo ships as having cargo.

### 5. Special Capability Filter Key Derivation
The filter keys for special capabilities are derived dynamically:
```python
show_has = filter_state.get(f'show_{col_id}', True)  # e.g., 'show_can_destroy_planet'
no_key = col_id.replace('can_', 'no_', 1)             # e.g., 'no_destroy_planet'
show_not = filter_state.get(f'show_{no_key}', True)
```

**Risk:** Changing the key derivation logic would break filter_state compatibility with FleetListViewModel.

### 6. Late Import Pattern
Several filters use intentional late imports to avoid circular dependencies:
- `FleetCapabilityCalculator` for spaceyard and special abilities
- `ShipStatsCalculator` for warp capability

**Risk:** Moving imports to top-level could introduce circular import errors.

## Test Coverage Analysis

### Well-Covered Areas
The test file `tests/unit/ui/screens/test_fleet_report_filters.py` has comprehensive coverage for:

1. **Basic status filters** (TestFilterShips class):
   - `test_filter_show_all` - All filters enabled
   - `test_filter_hide_damaged` - Hide damaged ships
   - `test_filter_hide_undamaged` - Hide undamaged ships
   - `test_filter_hide_derelict` - Hide derelict ships
   - `test_filter_hide_destroyed` - Hide destroyed ships

2. **Warp capability filters** (TestFilterShipsWarp class):
   - `test_filter_hide_warp_capable`
   - `test_filter_hide_not_warp_capable`
   - `test_filter_show_all_warp_states`

3. **Spaceyard filters** (TestFilterShipsSpaceyard class):
   - `test_filter_hide_has_spaceyard`
   - `test_filter_hide_no_spaceyard`
   - `test_filter_show_all_spaceyard_states`

4. **Cargo filters** (TestFilterShipsCargo class):
   - `test_filter_hide_has_cargo`
   - `test_filter_hide_no_cargo`
   - `test_filter_cargo_with_population`
   - `test_filter_cargo_zero_value_treated_as_no_cargo`
   - `test_filter_show_all_cargo_states`

5. **Special capability filters** (TestSpecialCapabilityFilter class):
   - `test_filter_hides_ships_with_ability`
   - `test_filter_hides_ships_without_ability`
   - `test_filter_default_shows_all`

### Coverage Gaps (Tests to Add BEFORE Refactoring)

#### Gap 1: Status Priority Interactions
**Missing tests for the mutually exclusive status categories:**
- Ship that is both destroyed AND derelict (should be categorized as destroyed only)
- Ship that is derelict AND damaged (should be categorized as derelict only)

```python
def test_destroyed_takes_priority_over_derelict():
    """Destroyed ship is not also filtered as derelict."""
    ship = make_mock_ship(is_alive=False, is_derelict=True)
    # With both filters off, ship should be excluded
    # With destroyed filter on, ship should be included
```

#### Gap 2: Empty Ship List
**No test for empty input:**
```python
def test_filter_empty_list():
    """Filter returns empty list for empty input."""
    result = filter_ships([], {})
    assert result == []
```

#### Gap 3: Multiple Filter Combinations
**Missing tests for combining multiple filter categories:**
```python
def test_filter_warp_and_cargo_combined():
    """Test applying both warp AND cargo filters together."""
    # Ship with warp but no cargo
    # Ship without warp but with cargo
    # Ship with both
    # Ship with neither
```

#### Gap 4: Both Sides of a Filter Off
**What happens when BOTH `show_X` and `show_not_X` are False?**
```python
def test_filter_both_warp_filters_off():
    """When both warp filters are off, no ships pass warp filter."""
    filter_state = {
        'show_warp_capable': False,
        'show_not_warp_capable': False,
    }
    # Expected: No ships pass
```

This is an edge case that may or may not be intentional behavior.

#### Gap 5: Missing Keys in filter_state
**Test behavior when filter_state is missing keys:**
```python
def test_filter_missing_keys_default_to_true():
    """Missing filter keys default to True (show all)."""
    ships = [make_mock_ship(), make_mock_ship()]
    result = filter_ships(ships, {})  # Empty filter_state
    assert len(result) == 2
```

#### Gap 6: Special Capability with Multiple Abilities
**Test ship with multiple special abilities:**
```python
def test_filter_ship_with_multiple_special_abilities():
    """Ship with multiple abilities filtered correctly."""
    # Ship has both DestroyPlanet AND DestroyStar
    # Filter hides DestroyPlanet
    # Ship should be hidden even though it has DestroyStar
```

## Risk Assessment

### High Risk Areas
1. **Ship status priority chain** - Any change to the if/continue structure could categorize ships incorrectly
2. **Cargo detection boolean logic** - The `and sum() > 0` is easy to accidentally simplify incorrectly

### Medium Risk Areas
1. **Special capability loop with _skip flag** - The nested loop with break/continue is fragile
2. **Late import placement** - Moving imports could cause circular import issues

### Low Risk Areas
1. **Individual filter checks** - These are simple boolean checks that can be safely extracted
2. **Default values in .get()** - These are straightforward to preserve

## Refactoring Recommendations

### Safe Refactoring Approach
The function is **suitable for refactoring** using helper method extraction:

1. **Extract capability check helpers:**
   ```python
   def _passes_warp_filter(ship, filter_state) -> bool
   def _passes_spaceyard_filter(ship, filter_state) -> bool
   def _passes_cargo_filter(ship, filter_state) -> bool
   def _passes_special_capability_filters(ship, filter_state) -> bool
   ```

2. **Keep the status priority chain intact** - Do NOT extract status checks into separate methods that could be reordered

3. **Preserve the main loop structure:**
   ```python
   for ship in ships:
       if not _passes_warp_filter(ship, filter_state): continue
       if not _passes_spaceyard_filter(ship, filter_state): continue
       if not _passes_cargo_filter(ship, filter_state): continue
       if not _passes_special_capability_filters(ship, filter_state): continue
       # Status priority chain remains inline
       ...
   ```

### Tests to Add Before Refactoring
1. `test_filter_empty_list` - Empty input returns empty output
2. `test_destroyed_takes_priority_over_derelict` - Priority invariant
3. `test_derelict_takes_priority_over_damaged` - Priority invariant
4. `test_filter_missing_keys_default_to_true` - Default behavior
5. `test_filter_both_warp_filters_off` - Edge case documentation

## Conclusion

**Verdict: SAFE TO REFACTOR**

The function is a good candidate for refactoring because:
1. Test coverage is comprehensive (though gaps should be filled first)
2. The complexity comes from repetitive filter patterns that can be extracted
3. The critical invariants (status priority) are well-defined and can be preserved
4. No external side effects - pure filtering function

**Pre-refactoring checklist:**
- [ ] Add missing test cases for coverage gaps
- [ ] Run full test suite to establish baseline
- [ ] Extract helper methods one at a time, running tests after each
- [ ] Verify cyclomatic complexity reduction after refactoring
