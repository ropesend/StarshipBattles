# Safety Analysis: filter_ships

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (Grade F)
**Length:** 99 lines

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a filter state dictionary. It processes ships through multiple independent filter categories:

1. **Warp capability filter** (lines 143-153)
2. **Spaceyard capability filter** (lines 155-164)
3. **Cargo filter** (lines 166-174)
4. **Special capability filters** (lines 176-194) - iterates over `SPECIAL_CAPABILITY_COLUMNS`
5. **Ship status filters** (lines 196-220):
   - Destroyed ships (lines 196-201)
   - Derelict ships (lines 203-208)
   - Damaged ships (lines 210-215)
   - Undamaged ships (lines 217-220)

---

## 2. Test Coverage Analysis

### Existing Test Coverage (49 total tests in test file)

| Filter Category | Tests Present | Coverage Level |
|----------------|---------------|----------------|
| Basic status (damaged/undamaged/derelict/destroyed) | 5 tests | **Good** |
| Warp capability | 3 tests | **Good** |
| Spaceyard capability | 3 tests | **Good** |
| Cargo filter | 5 tests | **Good** |
| Special capability filters | 3 tests | **Adequate** |
| Combined filters | 0 tests | **MISSING** |
| Empty input | 0 tests | **MISSING** |
| Missing filter keys | 0 tests | **MISSING** |
| Filter order interactions | 0 tests | **MISSING** |

### Test Classes in `test_fleet_report_filters.py`:
- `TestFilterShips` - Basic status filters (4 tests)
- `TestFilterShipsWarp` - Warp capability filters (3 tests)
- `TestFilterShipsSpaceyard` - Spaceyard filters (3 tests)
- `TestFilterShipsCargo` - Cargo filters (5 tests)
- `TestSpecialCapabilityFilter` - Special abilities (3 tests)

---

## 3. Edge Cases and Error Handling

### 3.1 Edge Cases Identified

| Edge Case | Current Handling | Test Coverage |
|-----------|------------------|---------------|
| Empty ship list | Returns empty list (implicit) | **MISSING** |
| Empty filter_state dict | Uses `.get()` with True defaults | **MISSING** |
| None values in filter_state | `.get()` returns True | **MISSING** |
| Ship with None cargo_contents | Line 170: `bool(ship.cargo_contents)` handles | Partial |
| Ship with zero-sum cargo | Line 170: `sum(ship.cargo_contents.values()) > 0` handles | **Tested** |
| All filters disabled | Would return empty list | **MISSING** |

### 3.2 Defensive Coding Patterns

The function uses safe patterns:
```python
filter_state.get('show_warp_capable', True)  # Default to True (show all)
```

This ensures that missing keys in filter_state don't cause crashes - they default to "show all" behavior.

### 3.3 Implicit Assumptions

1. **Ship properties exist**: The function assumes `ship.is_alive`, `ship.is_derelict`, `ship.is_damaged()`, and `ship.cargo_contents` are always accessible
2. **cargo_contents is dict-like**: Uses `.values()` without checking type
3. **SPECIAL_CAPABILITY_COLUMNS is non-empty**: Iterates without checking

---

## 4. Invariants That Must Be Preserved

### Critical Invariants

1. **Filter evaluation order matters for status filters**
   - Destroyed check (line 197) MUST come before derelict check (line 204)
   - Derelict check (line 204) MUST come before damaged check (line 211)
   - Reason: A destroyed ship should be classified as destroyed, not derelict/damaged
   - A derelict ship should be classified as derelict, not just damaged

2. **Early continue pattern**
   - Each filter category uses `continue` to skip ships
   - The ship is only added to result at the end of the loop OR after passing a status filter

3. **Default filter values are True**
   - All `.get()` calls default to True
   - Changing defaults would break the "show all by default" behavior

4. **Capability filters use short-circuit evaluation**
   - Lines 148, 158, 169, 184: Only check capabilities if a filter is disabled
   - Pattern: `if not show_X or not show_not_X:` triggers capability check
   - This is an optimization to avoid expensive capability lookups

5. **Special capability filter key derivation**
   - Line 182: `no_key = col_id.replace('can_', 'no_', 1)`
   - This transformation must match the keys in `FleetListViewModel.get_filter_state()`

---

## 5. Risk Areas for Refactoring

### 5.1 HIGH RISK Areas

| Risk Area | Lines | Description | Mitigation |
|-----------|-------|-------------|------------|
| Status filter order | 196-220 | Order determines ship classification | Preserve exact order; add explicit tests |
| Special capability key derivation | 182 | String manipulation creates filter keys | Add tests for key derivation correctness |
| Late imports | 159, 185 | Imports inside function body | Cannot be moved to module level (circular imports) |

### 5.2 MEDIUM RISK Areas

| Risk Area | Lines | Description | Mitigation |
|-----------|-------|-------------|------------|
| `_skip` flag pattern | 177-194 | Uses flag to break out of nested loop | Can be refactored to helper function |
| Capability optimization | 148, 158, 169, 184 | Skips capability check when both filters are True | Preserve optimization or document performance impact |

### 5.3 LOW RISK Areas

| Risk Area | Lines | Description |
|-----------|-------|-------------|
| Warp filter logic | 143-153 | Simple boolean checks |
| Cargo filter logic | 166-174 | Simple boolean/sum checks |
| Spaceyard filter logic | 155-164 | Simple boolean checks |

---

## 6. Dependencies

### External Dependencies

```
game.strategy.services.ship_stats_calculator.ShipStatsCalculator
  - has_warp_capability(ship) -> bool

game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator
  - ship_has_spaceyard(ship) -> bool
  - ship_has_ability(ship, ability_name) -> bool

game.ui.screens.fleet_data_source.SPECIAL_CAPABILITY_COLUMNS
  - Dict[str, str] mapping column IDs to ability names
```

### Consumer (Caller)

```
game.ui.screens.fleet_report_view_model.FleetListViewModel._refresh()
  - Line 215: filtered = filter_ships(self._ships, self.get_filter_state())
```

---

## 7. Missing Test Coverage (MUST ADD BEFORE REFACTORING)

### Priority 1 - Critical Path Tests

```python
def test_empty_ship_list_returns_empty():
    """Empty input should return empty output."""
    result = filter_ships([], {})
    assert result == []

def test_empty_filter_state_uses_defaults():
    """Empty filter state should show all (defaults to True)."""
    ships = [make_mock_ship()]
    result = filter_ships(ships, {})
    assert len(result) == 1

def test_all_filters_disabled_returns_empty():
    """When all status filters are False, no ships pass."""
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0
```

### Priority 2 - Status Classification Order Tests

```python
def test_destroyed_ship_not_classified_as_derelict():
    """Destroyed ships are filtered by destroyed filter, not derelict."""
    ship = make_mock_ship(is_alive=False, is_derelict=True)
    filter_state = {
        'show_damaged': True,
        'show_undamaged': True,
        'show_derelict': True,
        'show_destroyed': False,  # Hide destroyed
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be hidden as destroyed

def test_derelict_ship_not_classified_as_damaged():
    """Derelict ships are filtered by derelict filter, not damaged."""
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {
        'show_damaged': True,
        'show_undamaged': True,
        'show_derelict': False,  # Hide derelict
        'show_destroyed': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be hidden as derelict
```

### Priority 3 - Combined Filter Tests

```python
def test_combined_warp_and_status_filters():
    """Multiple filter categories should combine correctly."""
    ships = [
        make_mock_ship(is_damaged=True, warp_tonnage=1500, mass=1000),  # Damaged, warp
        make_mock_ship(is_damaged=False, warp_tonnage=None, mass=1000),  # Healthy, no warp
    ]
    filter_state = {
        'show_damaged': False,  # Hide damaged
        'show_undamaged': True,
        'show_derelict': True,
        'show_destroyed': True,
        'show_warp_capable': True,
        'show_not_warp_capable': True,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 1
    assert not result[0].is_damaged()
```

---

## 8. Refactorability Assessment

### Verdict: REFACTORABLE with caution

### Rationale

**Favorable factors:**
1. Good existing test coverage for individual filter categories
2. Clear separation of filter logic into distinct blocks
3. Pure function with no side effects
4. Well-documented parameter contract

**Risk factors:**
1. Status filter order is critical and not explicitly tested
2. Special capability key derivation is implicit/magical
3. Late imports cannot be refactored out (circular dependency)
4. High cyclomatic complexity makes changes risky

### Recommended Refactoring Approach

1. **Add missing tests FIRST** (Priority 1 and 2 tests above)
2. **Extract helper functions** for each filter category:
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filters(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`
3. **Preserve the status filter order** within `_passes_status_filter`
4. **Keep late imports** in their current locations (document why)

### Estimated Complexity After Refactor

- Main function: CC ~5-7
- Helper functions: CC ~3-5 each
- Total: More code, but each piece is testable and understandable

---

## 9. Conclusion

| Aspect | Assessment |
|--------|------------|
| **Test Coverage** | Adequate but missing edge cases and order tests |
| **Risk Level** | MEDIUM - status filter order is critical |
| **Refactorability** | YES - with additional tests first |
| **Blocking Issues** | None - proceed after adding missing tests |

**Recommendation:** PROCEED WITH REFACTORING after adding Priority 1 and Priority 2 tests from Section 7.
