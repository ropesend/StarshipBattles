# Safety Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** High (multiple filter branches, nested conditionals)

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a `filter_state` dictionary. It handles multiple independent filter categories:

1. **Warp capability filter** (lines 143-153)
2. **Spaceyard capability filter** (lines 155-164)
3. **Cargo filter** (lines 166-174)
4. **Special capability filters** (lines 176-194) - iterates over `SPECIAL_CAPABILITY_COLUMNS`
5. **Status filters** (lines 196-220):
   - Destroyed (lines 196-201)
   - Derelict (lines 203-208)
   - Damaged (lines 210-215)
   - Undamaged (lines 217-220)

---

## 2. Edge Cases and Error Handling

### 2.1 Handled Edge Cases
- **Empty ships list:** Returns empty list (no explicit handling, but loop simply doesn't execute)
- **Missing filter keys:** Uses `.get()` with `True` as default throughout, so missing keys default to "show all"
- **Zero-value cargo:** Explicitly handled (line 170) - `sum(ship.cargo_contents.values()) > 0`
- **Empty cargo dict:** Handled via `bool(ship.cargo_contents)` check

### 2.2 Potential Edge Cases NOT Tested
- **`ships` is `None`:** Would raise `TypeError` when iterating - NO guard
- **`filter_state` is `None`:** Would raise `AttributeError` on `.get()` calls - NO guard
- **Ship with `cargo_contents = None`:** Line 170 would fail with `TypeError` - assumes always dict or falsy

### 2.3 Late Imports
The function uses late imports inside conditional blocks to avoid circular imports:
- `FleetCapabilityCalculator` (lines 159, 185)
- These imports are only triggered when filter is active (performance optimization)

---

## 3. Invariants That Must Be Preserved

### 3.1 Filter Priority/Order
The status filter order is **critical** and must be preserved:
```
1. Destroyed (checked first, exits early)
2. Derelict (checked second, because derelict implies damaged)
3. Damaged (checked third)
4. Undamaged (fallthrough for remaining ships)
```
**Comment on line 203 explicitly documents this:** "Derelict filter (checked before damaged since derelict implies damaged)"

### 3.2 Filter Independence
Each filter category (warp, spaceyard, cargo, special, status) operates independently. A ship must pass ALL active filters to be included.

### 3.3 Default Behavior
When a filter key is missing, default behavior is `True` (show the category). This is consistent across all filter types.

### 3.4 Early Continue Pattern
Each filter block uses `continue` to skip ships that don't match. This pattern must be preserved for correctness.

### 3.5 Special Capability Key Derivation
Lines 181-183 derive filter keys from column IDs:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```
This transformation (`can_X` -> `no_X`) is an implicit contract with the UI layer.

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Status Filter Ordering
The status checks (destroyed, derelict, damaged, undamaged) have mutual exclusivity requirements:
- A destroyed ship is NOT derelict, NOT damaged, NOT undamaged
- A derelict ship is considered damaged but NOT undamaged
- Changing the order or logic could cause ships to appear/disappear incorrectly

### 4.2 MEDIUM RISK: Special Capability Loop with `_skip` Flag
The special capability filter (lines 176-194) uses a `_skip` flag and `break` to exit early. This pattern is fragile:
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    # ... check logic ...
    if has_ability and not show_has:
        _skip = True
        break
    if not has_ability and not show_not:
        _skip = True
        break
if _skip:
    continue
```
Refactoring this to use a helper function could accidentally change break/continue semantics.

### 4.3 LOW RISK: Import Location
Late imports are inside conditional blocks. Moving them to top-level could:
- Create circular import errors
- Change performance characteristics

### 4.4 LOW RISK: Filter State Key Names
Filter keys follow naming conventions:
- `show_X` for positive filters
- `show_no_X` or `show_not_X` for negative filters
- Renaming or reorganizing could break the UI layer

---

## 5. Missing Test Coverage

### 5.1 Tests That Exist (Comprehensive)
The test file `tests\unit\ui\screens\test_fleet_report_filters.py` covers:
- All status filters (damaged, undamaged, derelict, destroyed)
- Warp capability filters (both directions)
- Spaceyard capability filters (both directions)
- Cargo filters (including zero-value edge case)
- Special capability filters (DestroyPlanet ability)
- Sort functionality

### 5.2 Missing Tests (SHOULD ADD BEFORE REFACTORING)

1. **Multiple filter combinations:**
   - Test filtering by warp AND damaged simultaneously
   - Test filtering by cargo AND spaceyard simultaneously
   - Currently each filter category is tested in isolation

2. **Filter ordering edge cases:**
   - A destroyed ship that would match warp filter (should still be hidden if show_destroyed=False)
   - A derelict ship that has cargo (verify both filters apply correctly)

3. **All special capabilities:**
   - Only `can_destroy_planet` is tested
   - Missing tests for: `can_open_warp`, `can_close_warp`, `can_destroy_star`, `can_create_sphere`

4. **Empty filter_state dict:**
   - What happens with `filter_ships(ships, {})`?
   - Expected: all ships pass (since all `.get()` calls default to `True`)

5. **Negative filter values:**
   - What happens with `filter_state = {'show_damaged': False, 'show_undamaged': False, ...}`?
   - Should return empty list (no ships match)

6. **Integration with view model:**
   - `FleetListViewModel._refresh()` calls `filter_ships` - test the integration path

---

## 6. Refactorability Assessment

### 6.1 Can This Function Be Refactored?

**YES, with caution.** The function is a good candidate for extraction into smaller helper functions:

```
Potential refactoring targets:
- _filter_by_warp(ship, filter_state) -> bool
- _filter_by_spaceyard(ship, filter_state) -> bool
- _filter_by_cargo(ship, filter_state) -> bool
- _filter_by_special_capabilities(ship, filter_state) -> bool
- _filter_by_status(ship, filter_state) -> bool
```

### 6.2 Recommended Approach

1. **Add missing tests FIRST** (see section 5.2)
2. **Extract each filter category into a predicate function**
3. **Preserve the exact filter ordering for status checks**
4. **Keep late imports inside the helper functions**
5. **Use `all()` with predicate functions for cleaner logic**

### 6.3 What NOT To Change
- The status filter ordering (destroyed -> derelict -> damaged -> undamaged)
- The default `True` behavior for missing filter keys
- The late import pattern for `FleetCapabilityCalculator`
- The special capability key derivation logic

---

## 7. Final Recommendation

### PROCEED WITH REFACTORING

**Conditions:**
1. Add comprehensive combination tests before any changes
2. Test all 5 special capability types
3. Verify empty filter_state behavior
4. Maintain backward compatibility with existing filter_state keys

**Complexity Reduction Potential:** HIGH
- Current function has 7+ independent filter branches
- Can be reduced to 5-6 small helper functions
- Main function becomes a clean composition of predicates

**Risk Level:** MEDIUM
- Status filter ordering is subtle and must be preserved
- Test coverage is good but not complete for combinations
- Late imports add complexity to extraction

**Estimated Effort:** 1-2 hours including test additions

---

## 8. Pre-Refactoring Checklist

- [ ] Add test for multiple filter combinations
- [ ] Add tests for all special capability types
- [ ] Add test for empty filter_state
- [ ] Add test for "hide all" filter scenario
- [ ] Verify existing tests pass
- [ ] Document the status filter ordering invariant in code comments
