# Safety Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (grade F)
**Test Coverage:** Comprehensive (see below)

---

## 1. Edge Cases and Error Handling Paths

### Handled Edge Cases
1. **Empty ships list** - Returns empty list (implicit via iteration)
2. **Empty filter_state dict** - All filters default to `True` via `.get()` with defaults
3. **Missing filter keys** - `filter_state.get('show_X', True)` provides safe defaults
4. **Ships with zero cargo values** - `sum(ship.cargo_contents.values()) > 0` correctly treats `{'minerals': 0}` as no cargo
5. **Ships without cargo_contents attribute** - Would fail if `cargo_contents` is None (potential risk)

### Unhandled Edge Cases (Potential Risks)
1. **None in ships list** - Would cause AttributeError when accessing ship properties
2. **Ship missing expected attributes** - `is_alive`, `is_derelict`, `cargo_contents` assumed to exist
3. **Filter state with None values** - `filter_state.get('show_X', True)` returns None if key exists with None value

---

## 2. Invariants That Must Be Preserved During Refactoring

### Critical Invariants

1. **Filter Evaluation Order** - Filters are evaluated in this exact sequence:
   - Warp capability filter (lines 143-153)
   - Spaceyard capability filter (lines 155-164)
   - Cargo filter (lines 166-174)
   - Special capability filters (lines 176-194)
   - Destroyed filter (lines 196-201)
   - Derelict filter (lines 203-208)
   - Damaged filter (lines 210-215)
   - Undamaged (catch-all) (lines 217-220)

2. **Early Continue Pattern** - Ships are excluded via `continue` statements, not explicit exclusion. This means:
   - If no filter explicitly excludes a ship AND no filter explicitly includes it, the ship falls through to undamaged handling
   - A ship must pass ALL enabled filters to be included

3. **State Classification Priority** - A ship's state is classified exclusively as:
   - DESTROYED (checked first) - `not ship.is_alive`
   - DERELICT (checked second) - `ship.is_derelict`
   - DAMAGED (checked third) - `ship.is_damaged()`
   - UNDAMAGED (default) - none of the above

   A derelict ship is NOT also classified as damaged for filtering purposes.

4. **Both-True Optimization** - When both complementary filters are True (e.g., `show_warp_capable=True` AND `show_not_warp_capable=True`), the capability check is skipped entirely:
   ```python
   if not show_warp or not show_not_warp:
       # Only check warp capability if one filter is off
   ```

5. **Late Imports** - `FleetCapabilityCalculator` is imported inside the function body to avoid circular imports. This pattern MUST be preserved.

6. **SPECIAL_CAPABILITY_COLUMNS Mapping** - Filter keys are derived from column IDs via:
   - `show_can_destroy_planet` (has ability)
   - `show_no_destroy_planet` (lacks ability, derived by replacing `can_` with `no_`)

---

## 3. Risk Areas Where Refactoring Could Introduce Bugs

### High Risk
1. **Filter Priority/Order Changes** - The destroyed > derelict > damaged > undamaged priority chain is critical. Reordering these checks would cause ships to be classified incorrectly.

2. **Special Capability Loop Break Logic** - The `_skip` flag pattern with inner `break` statements:
   ```python
   _skip = False
   for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
       ...
       if has_ability and not show_has:
           _skip = True
           break
   if _skip:
       continue
   ```
   Extracting this to a helper must preserve the break-on-first-exclusion behavior.

3. **Cargo Contents Edge Cases** - The cargo check `bool(ship.cargo_contents) and sum(...) > 0` handles:
   - Empty dict `{}` -> False (no cargo)
   - Dict with zeros `{'a': 0}` -> False (no cargo)
   - Dict with values `{'a': 50}` -> True (has cargo)

   Simplifying this could introduce bugs.

### Medium Risk
4. **Filter Key Derivation** - The `no_key = col_id.replace('can_', 'no_', 1)` pattern is fragile. If column IDs change or new columns don't follow this pattern, filtering will silently fail (defaulting to show).

5. **Continue vs. Append Semantics** - Each filter block either:
   - `continue` (exclude the ship and move to next)
   - `result.append(ship); continue` (include and move to next)
   - Fall through (proceed to next filter check)

   Getting these wrong would change inclusion/exclusion behavior.

### Low Risk
6. **Late Import Performance** - The function imports `FleetCapabilityCalculator` on each call. While Python caches imports, moving these outside the loop could have subtle effects on circular import scenarios.

---

## 4. Missing Test Coverage That Should Be Added BEFORE Refactoring

### Currently Missing Tests

1. **None/Empty Input Edge Cases**
   - `filter_ships(None, {...})` - Should raise or handle gracefully
   - `filter_ships([None, ship], {...})` - Ship with None in list

2. **Combined Filter Scenarios**
   - Ship that is BOTH warp-capable AND has cargo - verify both filters apply
   - Ship that is derelict AND has spaceyard - verify exclusion order
   - Ship that matches special ability filter but excluded by damaged filter

3. **All Filters Disabled**
   - `filter_ships(ships, {'show_damaged': False, 'show_undamaged': False, 'show_derelict': False, 'show_destroyed': False})` - Should return empty list

4. **Filter State with None Values**
   - `filter_state = {'show_damaged': None}` - Currently would be falsy, might not match intent

5. **Multiple Special Capabilities**
   - Ship with multiple special abilities (e.g., can destroy planet AND can open warp)
   - Filter that hides one but shows another

6. **Boundary Cases for Cargo**
   - Ship with `cargo_contents = None` (vs empty dict)
   - Ship with negative cargo values (invalid but could happen in corrupted data)

### Tests That Exist and Provide Good Coverage

| Test Class | Coverage |
|------------|----------|
| `TestFilterShips` | Basic damaged/undamaged/derelict/destroyed filtering |
| `TestFilterShipsWarp` | Warp capability filtering (show/hide both states) |
| `TestFilterShipsSpaceyard` | Spaceyard capability filtering |
| `TestFilterShipsCargo` | Cargo filtering including zero values |
| `TestSpecialCapabilityFilter` | Special ability filtering |

---

## 5. Refactorability Assessment

### Verdict: **REFACTORABLE** with caution

### Rationale

**Reasons it CAN be refactored:**
1. The function has clear, identifiable sub-filters that can be extracted as helper functions
2. Each filter follows a consistent pattern: check condition, continue if excluded
3. Test coverage is comprehensive for main use cases
4. The function is purely functional (no side effects, no state mutation)

**Recommended Refactoring Approach:**
1. Extract each filter block into a named predicate function:
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filter(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`

2. Main function becomes:
   ```python
   def filter_ships(ships, filter_state):
       return [
           ship for ship in ships
           if _passes_warp_filter(ship, filter_state)
           and _passes_spaceyard_filter(ship, filter_state)
           and _passes_cargo_filter(ship, filter_state)
           and _passes_special_capability_filter(ship, filter_state)
           and _passes_status_filter(ship, filter_state)
       ]
   ```

3. Each helper can be individually tested with clearer semantics.

**Pre-refactoring checklist:**
- [ ] Add tests for None/empty input edge cases
- [ ] Add test for all-filters-disabled scenario
- [ ] Add test for combined filter scenarios (multiple filters active)
- [ ] Verify late import pattern can be preserved in helpers
- [ ] Consider whether helpers should be module-private (underscore prefix)

**Complexity Reduction Estimate:**
- Current: 36 (single function)
- After extraction: ~10 for main function + ~5-8 per helper = total ~36 spread across functions
- Each individual function will be under 15 CC, meeting the goal

---

## Summary

| Aspect | Assessment |
|--------|------------|
| Edge Cases | Mostly handled, some None-safety gaps |
| Invariants | Well-defined, must preserve filter order and priority chain |
| Risk Level | Medium - order-dependent logic requires careful extraction |
| Test Coverage | Good (80%+), needs edge case additions |
| Refactorability | YES - extract predicate helpers |
| Skip? | NO - this function is a good refactoring candidate |

**Recommendation:** Proceed with refactoring after adding the missing edge case tests. Use the predicate extraction pattern to reduce complexity while preserving all invariants.
