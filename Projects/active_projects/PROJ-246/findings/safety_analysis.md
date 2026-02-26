# Safety Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Date:** 2026-02-26

---

## Edge Cases

### 1. Empty Input List
- **Location:** Line 141-222 (entire function)
- **Behavior:** Returns empty list when `ships` is empty
- **Test Coverage:** Not explicitly tested for `filter_ships`, but behavior is implicit (loop doesn't iterate)

### 2. Missing Filter Keys
- **Location:** Lines 144-145, 156-157, 167-168, 181-183, 198, 205, 212, 218
- **Behavior:** Uses `.get()` with default `True` for all filter keys
- **Risk:** If a filter key is missing from `filter_state`, ships pass that filter (show by default)
- **Test Coverage:** Not explicitly tested for missing keys

### 3. Cargo Contents Edge Cases
- **Location:** Lines 169-174
- **Condition:** `has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`
- **Handles:**
  - `None` or empty dict: treated as no cargo
  - Dict with all zero values: treated as no cargo (explicitly tested)
- **Test Coverage:** `test_filter_cargo_zero_value_treated_as_no_cargo`

### 4. Ship State Priority (Destroyed > Derelict > Damaged > Undamaged)
- **Location:** Lines 196-220
- **Critical:** Order of checks matters! A ship can only match ONE status category:
  1. Destroyed (`not ship.is_alive`) - checked first
  2. Derelict (`ship.is_derelict`) - checked after alive
  3. Damaged (`ship.is_damaged()`) - checked after derelict
  4. Undamaged (default fallthrough)
- **Risk:** This is an invariant that must be preserved

### 5. Special Capability Filter Key Derivation
- **Location:** Lines 178-193
- **Logic:** Derives filter keys from column ID via string manipulation:
  - `show_{col_id}` for "has ability"
  - `show_{col_id.replace('can_', 'no_', 1)}` for "no ability"
- **Example:** `can_destroy_planet` -> `show_can_destroy_planet` / `show_no_destroy_planet`
- **Risk:** Key derivation is fragile; depends on naming convention

---

## Invariants

### 1. Filter Application Order Independence
Each filter type (warp, spaceyard, cargo, special capabilities, status) operates independently. A ship must pass ALL filters to be included. Order of filter checks can change without affecting results.

### 2. Ship State Mutual Exclusivity
A ship can only be in ONE status state for filtering purposes:
- Destroyed (highest priority)
- Derelict
- Damaged
- Undamaged (lowest priority)

**Must preserve:** The `continue` + `result.append` pattern after each status check.

### 3. Default Filter Behavior = Show
When a filter key is missing from `filter_state`, the default behavior is to SHOW matching ships (`True`).

### 4. Late Import Pattern
Three imports occur inside the function body to avoid circular imports:
- `FleetCapabilityCalculator` (lines 159, 185, used twice)
- These imports MUST remain inside the function

### 5. Binary Filter Pairs
Filters come in pairs (show/hide both options). When BOTH are `True`, the filter is effectively disabled (short-circuit optimization on lines 148, 158, 169, 184).

---

## Risk Areas

### 1. HIGH RISK: Ship Status Classification Logic (Lines 196-220)
**Why:** The if/elif chain with early `continue` and `result.append` is the most complex part. A refactor could easily:
- Break the mutual exclusivity invariant
- Change the priority order
- Cause ships to be double-added or missed

**Mitigation:** Comprehensive tests exist for each status filter, but there's no test for a ship that could match multiple statuses (e.g., a derelict ship that is also damaged).

### 2. MEDIUM RISK: `_skip` Flag Pattern (Lines 177-194)
**Why:** Uses a local `_skip` flag to break out of nested loop. This pattern is:
- Non-obvious to readers
- Easy to accidentally remove the `if _skip: continue` check
- Could be broken by refactoring the loop structure

**Mitigation:** Well-tested by `TestSpecialCapabilityFilter` class.

### 3. MEDIUM RISK: Late Imports
**Why:** Circular import avoidance via late imports is a code smell that could be:
- Accidentally moved to module level
- Duplicated (import happens twice for FleetCapabilityCalculator)

**Mitigation:** Comments mark these as intentional.

### 4. LOW RISK: Filter Key Naming Convention
**Why:** The string manipulation for special capability filter keys is brittle:
```python
no_key = col_id.replace('can_', 'no_', 1)
```
If a column ID doesn't follow the `can_X` convention, the `no_` variant key would be malformed.

**Mitigation:** All current special capability columns follow the convention.

---

## Test Coverage Gaps

### Missing Tests

1. **Empty ships list for `filter_ships`**
   - No explicit test that `filter_ships([], filter_state)` returns `[]`

2. **Missing filter keys**
   - No test verifying behavior when `filter_state` is missing keys
   - No test with empty `filter_state` dict: `filter_ships(ships, {})`

3. **Ship matching multiple status conditions**
   - No test for a ship where `is_derelict=True` AND `is_damaged()=True` (should be filtered as derelict)
   - No test for destroyed ship that would also be damaged

4. **All filters disabled simultaneously**
   - No test where ALL `show_X` flags are `False` (should return empty list)

5. **Interaction between filter types**
   - No test combining status filters with capability filters
   - Example: Damaged ship that also has spaceyard, with `show_damaged=False`

6. **Special capability filter edge cases**
   - No test for multiple special capabilities on same ship
   - No test for all special capability columns simultaneously

### Existing Test Quality

The existing tests in `test_fleet_report_filters.py` are well-structured:
- `TestFilterShips` - Basic status filtering (4 tests)
- `TestFilterShipsWarp` - Warp capability filtering (3 tests)
- `TestFilterShipsSpaceyard` - Spaceyard filtering (3 tests)
- `TestFilterShipsCargo` - Cargo filtering (5 tests)
- `TestSpecialCapabilityFilter` - Special ability filtering (3 tests)

**Total: 18 tests for `filter_ships`**

---

## Refactorability Assessment

### Verdict: REFACTORABLE with CAUTION

### Reasons FOR Refactoring
1. **98 lines** for a single function is long (lines 124-222)
2. **Deep nesting** - multiple levels of if/continue/append
3. **Repeated pattern** - Each filter type follows similar structure (check condition, apply both show/hide filters)
4. **Late imports duplicated** - `FleetCapabilityCalculator` imported in two places
5. **`_skip` flag** - Could be eliminated with better structure

### Reasons for CAUTION
1. **Ship status logic** (lines 196-220) is the most fragile - small changes can break behavior
2. **Order dependency** in status checks must be preserved
3. **Performance** - Current implementation short-circuits early when both filter flags are `True`
4. **Late imports** are intentional - cannot be moved to module level

### Recommended Approach
1. **Add missing tests FIRST** (see Test Coverage Gaps above)
2. **Extract filter logic** into small helper functions (e.g., `_passes_warp_filter`, `_passes_cargo_filter`)
3. **Preserve early-exit optimization** for "both True" cases
4. **Do NOT change status classification order**
5. **Consider** using a filter chain/pipeline pattern for cleaner composition

### Tests to Add Before Refactoring

```python
def test_filter_empty_ships_list():
    """filter_ships with empty list returns empty list."""
    from game.ui.screens.fleet_report_filters import filter_ships
    result = filter_ships([], {'show_damaged': True, 'show_undamaged': True})
    assert result == []

def test_filter_with_empty_filter_state():
    """filter_ships with empty filter_state shows all ships (defaults to True)."""
    from game.ui.screens.fleet_report_filters import filter_ships
    ships = [make_mock_ship(), make_mock_ship(is_damaged=True)]
    result = filter_ships(ships, {})
    assert len(result) == 2

def test_filter_all_disabled_returns_empty():
    """When all status filters disabled, no ships pass."""
    from game.ui.screens.fleet_report_filters import filter_ships
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

def test_derelict_ship_classified_as_derelict_not_damaged():
    """A derelict ship that is also damaged should be classified as derelict."""
    from game.ui.screens.fleet_report_filters import filter_ships
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    # Hide derelict but show damaged
    filter_state = {
        'show_damaged': True,
        'show_undamaged': True,
        'show_derelict': False,
        'show_destroyed': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be excluded as derelict
```

---

## Summary

| Aspect | Assessment |
|--------|------------|
| **Complexity** | High (98 lines, multiple filter types) |
| **Test Coverage** | Good (18 tests) but gaps exist |
| **Risk Level** | Medium - status logic is fragile |
| **Refactorable** | Yes, with caution |
| **Prerequisite** | Add missing tests first |
