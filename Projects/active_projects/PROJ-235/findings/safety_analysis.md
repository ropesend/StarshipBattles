# Safety Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36
**Lines of Code:** ~99

---

## Edge Cases

### 1. Empty Input
- **Empty ship list:** Returns empty list (trivial case, line 141-142)
- **Empty filter_state dict:** All filters default to `True` via `.get()` with defaults

### 2. Ship State Edge Cases
- **Destroyed ships (`is_alive=False`):** Checked FIRST in the status hierarchy (lines 197-201)
- **Derelict ships:** Checked SECOND, before damaged (lines 203-208). Note: Derelict implies damaged
- **Damaged ships:** Only checked after ruling out destroyed/derelict (lines 210-215)
- **Undamaged (healthy) ships:** Catch-all at the end (lines 217-220)

### 3. Filter Key Edge Cases
- **Missing filter keys:** All `.get()` calls have `True` defaults - missing keys show ships
- **Both filters off:** E.g., `show_warp_capable=False` AND `show_not_warp_capable=False` hides ALL ships
- **Partial filter_state:** Only specified filters are checked; others default to True

### 4. Special Capability Filter Edge Cases
- **SPECIAL_CAPABILITY_COLUMNS iteration:** Iterates all 5 special columns even if only one filter is set
- **`_skip` flag pattern:** Uses break+flag pattern instead of early return (lines 177-194)
- **Key derivation:** `col_id.replace('can_', 'no_', 1)` - relies on columns starting with "can_"

### 5. Cargo Edge Cases
- **`cargo_contents` is `None` vs empty dict:** Code handles via `bool(ship.cargo_contents)` (line 170)
- **Zero-valued cargo:** `sum(ship.cargo_contents.values()) > 0` correctly treats zeros as no cargo

---

## Invariants That Must Be Preserved

### 1. Filter Evaluation Order
**CRITICAL:** The status check order is semantically important:
1. Destroyed (not `is_alive`) - must be checked FIRST
2. Derelict (`is_derelict`) - must be checked BEFORE damaged
3. Damaged (`is_damaged()`) - checked THIRD
4. Undamaged - catch-all LAST

**Rationale:** A derelict ship is also damaged, but should be filtered by the derelict filter, not damaged filter.

### 2. Early Return Pattern
Each filter uses `continue` to skip ships that don't match. The order of filter checks:
1. Warp capability filter (lines 143-153)
2. Spaceyard capability filter (lines 155-164)
3. Cargo filter (lines 166-174)
4. Special capability filters loop (lines 176-194)
5. Status filters - destroyed/derelict/damaged/undamaged (lines 196-220)

Ships that pass ALL filters are appended to `result`.

### 3. Default Behavior
- All filters default to `True` (show all) when keys are missing
- When both positive and negative filters are `True` for a category, no filtering occurs

### 4. Late Import Pattern
Lines 159, 185: `FleetCapabilityCalculator` is imported inside the filter checks (lazy import to avoid circular dependencies). This pattern MUST be preserved.

---

## Risk Areas

### HIGH RISK: Status Filter Ordering
The if/elif/continue chain for status (lines 196-220) is the most fragile part:
- Reordering checks could cause ships to be filtered by the wrong category
- Derelict ships would be counted as "damaged" if order is wrong
- Destroyed ships would be counted as "derelict" or "damaged" if order is wrong

### MEDIUM RISK: Special Capability Loop
The `_skip` flag pattern (lines 177-194) is error-prone:
- Easy to forget to check `_skip` after the loop
- The `break` exits the inner loop but requires the flag to skip the outer loop iteration

### MEDIUM RISK: Filter Key String Derivation
Line 182: `no_key = col_id.replace('can_', 'no_', 1)` assumes:
- All capability columns start with "can_"
- The corresponding "no" filter uses "no_" prefix

### LOW RISK: Boolean Short-Circuit Optimization
Lines 148, 158, 169, 184: The pattern `if not show_X or not show_Y` is an optimization that skips expensive checks when both filters are True. Refactoring must preserve this optimization.

### LOW RISK: Cargo Check
Line 170: `has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`
- Two conditions: non-empty dict AND positive sum
- Both must remain for correct behavior

---

## Test Coverage Gaps

### Currently Covered (37 tests in test_fleet_report_filters.py)
- Empty fleet stats
- Basic filter operations (show/hide damaged, undamaged, derelict, destroyed)
- Warp capability filtering
- Spaceyard filtering
- Cargo filtering (including zero values, population)
- Special capability filtering
- Sorting by various columns

### MISSING Test Coverage (Must Add BEFORE Refactoring)

1. **Multiple Filters Combined**
   - No tests for combining status filters with capability filters
   - E.g., "show damaged AND warp capable only"

2. **All Filters Disabled**
   - No test for `show_warp_capable=False` AND `show_not_warp_capable=False` (should return empty)
   - Same for all filter categories

3. **Filter Order Independence**
   - No tests verifying filter order doesn't affect results
   - Should add: same ships, different filter_state permutations, same results

4. **Status Priority Edge Cases**
   - No test for: derelict ship that is also marked damaged (verify derelict filter, not damaged)
   - No test for: destroyed + derelict ship (verify destroyed filter takes precedence)

5. **Special Capability Filter Combinations**
   - No test combining multiple special capability filters
   - E.g., hide DestroyPlanet AND show OpenWarpPoint

6. **Large Ship Lists**
   - No performance/stress tests with many ships

7. **Missing filter_state Keys**
   - No explicit test that missing keys default to True (behavior tested implicitly)

---

## Refactorability Assessment

### Verdict: SAFE TO REFACTOR

**Reasons:**
1. **Well-defined inputs/outputs:** Takes `(ships, filter_state)`, returns filtered list
2. **No external side effects:** Pure filtering function, no mutations
3. **Good test coverage:** 37 tests covering main paths, though gaps exist
4. **Clear invariants:** Status order is documented in code comments (lines 203, 217)
5. **Isolated function:** No inheritance, no complex state management

### Recommended Refactoring Strategy

1. **Extract Filter Functions:** Create separate functions for each filter category:
   - `_apply_warp_filter(ship, filter_state) -> bool`
   - `_apply_spaceyard_filter(ship, filter_state) -> bool`
   - `_apply_cargo_filter(ship, filter_state) -> bool`
   - `_apply_capability_filters(ship, filter_state) -> bool`
   - `_apply_status_filter(ship, filter_state) -> bool`

2. **Compose Filters:** Main function becomes:
   ```python
   for ship in ships:
       if all([
           _apply_warp_filter(ship, filter_state),
           _apply_spaceyard_filter(ship, filter_state),
           _apply_cargo_filter(ship, filter_state),
           _apply_capability_filters(ship, filter_state),
           _apply_status_filter(ship, filter_state),
       ]):
           result.append(ship)
   ```

3. **Preserve Invariants:**
   - Status filter MUST check in order: destroyed -> derelict -> damaged -> undamaged
   - Keep lazy imports inside filter functions
   - Preserve `.get()` defaults

### Pre-Refactoring Checklist

- [ ] Add test: Multiple filters combined (status + capability)
- [ ] Add test: Both sides of filter disabled (empty result)
- [ ] Add test: Derelict ship not caught by damaged filter
- [ ] Add test: Destroyed ship not caught by derelict filter
- [ ] Run full test suite to establish baseline
- [ ] Verify CC=36 measurement

---

## Summary

| Category | Assessment |
|----------|------------|
| **Refactorability** | SAFE |
| **Risk Level** | MEDIUM |
| **Test Coverage** | ADEQUATE (gaps identified) |
| **Main Risk** | Status filter ordering |
| **Blocking Issues** | None |

The function is a good candidate for refactoring. The high cyclomatic complexity comes from the linear chain of filter checks, which can be cleanly extracted into separate functions. The key invariant (status check order) is well-documented and testable.
