# Safety Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36 (Grade F)

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter flags. It implements 6 distinct filter categories:

1. **Warp capability filter** (lines 144-153)
2. **Spaceyard capability filter** (lines 155-164)
3. **Cargo filter** (lines 166-174)
4. **Special capability filters** (lines 176-194) - loops over 5 abilities
5. **Status filters** (lines 196-220):
   - Destroyed ships
   - Derelict ships
   - Damaged ships
   - Undamaged ships

---

## 2. Edge Cases and Error Handling

### 2.1 Default Value Handling
- All filter keys use `.get(key, True)` with default `True`, ensuring ships pass through when filter keys are missing
- This is defensive programming that prevents KeyError exceptions

### 2.2 Empty Input
- Empty `ships` list returns empty list (correct behavior via iteration)
- Empty `filter_state` dict causes all filters to default to `True` (show all)

### 2.3 Cargo Edge Case (line 170)
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
- Handles both empty dict `{}` and dict with all zero values `{'minerals': 0}`
- Test coverage: `test_filter_cargo_zero_value_treated_as_no_cargo`

### 2.4 Special Capability Key Derivation (lines 181-183)
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```
- Derives "no" variant by replacing `can_` prefix with `no_`
- Example: `can_destroy_planet` -> `no_destroy_planet`
- Risk: If a column ID doesn't start with `can_`, the replacement produces unexpected keys

### 2.5 Ship State Hierarchy (lines 196-220)
The function enforces a **priority hierarchy** for ship states:
1. **Destroyed** (checked first via `not ship.is_alive`)
2. **Derelict** (checked before damaged, since derelict implies damaged)
3. **Damaged** (via `ship.is_damaged()` method call)
4. **Undamaged** (default fallthrough)

This is a critical invariant: a ship is categorized into exactly ONE state.

---

## 3. Invariants That Must Be Preserved

### 3.1 Filter Order Independence (for capability filters)
- Warp, spaceyard, cargo, and special capability filters are independent
- A ship must pass ALL of them to proceed to status filtering
- Order of capability checks does not affect outcome

### 3.2 Status Filter Mutual Exclusivity
- Each ship falls into exactly one status category
- The `continue` and early `result.append()` pattern ensures this
- **CRITICAL:** The if-else chain must remain ordered: destroyed -> derelict -> damaged -> undamaged

### 3.3 Default-to-Show Behavior
- Missing filter keys must default to `True` (show)
- This allows partial filter states to work correctly

### 3.4 No Side Effects
- Function must not modify input `ships` list or `filter_state` dict
- Currently satisfied: builds new `result` list

### 3.5 Lazy Import Pattern (lines 159, 185)
- `FleetCapabilityCalculator` is imported inside the function
- This appears to avoid circular imports
- Must be preserved or properly refactored

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Status Filter Hierarchy
The status filter logic (lines 196-220) uses a specific ordering with early returns. Refactoring this into separate helper functions risks:
- Breaking mutual exclusivity
- Double-counting ships in multiple categories
- Missing the "derelict implies damaged" relationship

**Mitigation:** Any refactoring must preserve the sequential if-elif-else structure or use explicit state categorization.

### 4.2 MEDIUM RISK: Special Capability Loop
The loop over `SPECIAL_CAPABILITY_COLUMNS.items()` with inner `_skip` flag is fragile:
- The `_skip` flag pattern is error-prone
- The `break` and outer `continue` create complex control flow
- Filter key derivation assumes `can_` prefix

**Mitigation:** Extract to a helper function that returns True/False for whether ship passes all special capability filters.

### 4.3 MEDIUM RISK: Lazy Imports
Two conditional imports inside the function:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
If extracted to helpers, imports may need to move to module level, potentially causing circular import issues.

**Mitigation:** Test imports at module level before refactoring.

### 4.4 LOW RISK: Cargo Check Expression
The cargo check is a single expression but could be extracted:
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
Low risk because it's straightforward boolean logic with good test coverage.

---

## 5. Test Coverage Assessment

### 5.1 Existing Test Coverage
The test file `tests/unit/ui/screens/test_fleet_report_filters.py` provides **excellent coverage**:

| Filter Category | Tests | Coverage |
|----------------|-------|----------|
| Show all | `test_filter_show_all` | Basic sanity |
| Hide damaged | `test_filter_hide_damaged` | Covered |
| Hide undamaged | `test_filter_hide_undamaged` | Covered |
| Hide derelict | `test_filter_hide_derelict` | Covered |
| Hide destroyed | `test_filter_hide_destroyed` | Covered |
| Warp capable | 3 tests in `TestFilterShipsWarp` | Well covered |
| Spaceyard | 3 tests in `TestFilterShipsSpaceyard` | Well covered |
| Cargo | 5 tests in `TestFilterShipsCargo` | Well covered |
| Special abilities | 3 tests in `TestSpecialCapabilityFilter` | Covered |

### 5.2 Missing Test Coverage

**Should be added BEFORE refactoring:**

1. **Combined filter test**: No test verifies behavior when multiple filter categories are active simultaneously (e.g., warp + cargo + damaged)

2. **Filter state missing keys**: No explicit test for partial `filter_state` dict (relies on `.get()` defaults)

3. **Derelict-damaged interaction**: No test for a ship that is both derelict AND would return `True` from `is_damaged()` to verify derelict takes precedence

4. **Empty ships list**: No explicit test (though trivial)

5. **Special capability multiple abilities**: No test for ship with multiple special abilities

### 5.3 Recommendation
**Add at least 2-3 integration-style tests** before refactoring:
- Combined multi-category filter test
- Derelict/damaged precedence test
- Partial filter state test

---

## 6. Refactorability Assessment

### 6.1 Is This Function Refactorable?

**YES**, this function is refactorable with careful attention to invariants.

### 6.2 Recommended Refactoring Strategy

**Extract helper predicates** for each filter category:
```python
def _passes_warp_filter(ship, filter_state) -> bool
def _passes_spaceyard_filter(ship, filter_state) -> bool
def _passes_cargo_filter(ship, filter_state) -> bool
def _passes_special_capability_filters(ship, filter_state) -> bool
def _passes_status_filter(ship, filter_state) -> bool
```

Main function becomes:
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### 6.3 Complexity Reduction Estimate
- Current: 36 branches
- After extraction: ~6-8 in main function, ~5-7 per helper
- Each helper would be below 10, main function below 10
- **Target of CC < 20 is achievable**

### 6.4 Risks if NOT Refactored
- None immediate; function works correctly
- Long-term maintainability concern as new filters are added
- New filter types would increase complexity further

---

## 7. Conclusion

| Aspect | Assessment |
|--------|------------|
| **Refactorable?** | YES |
| **Test coverage sufficient?** | Mostly YES, recommend 2-3 additional tests |
| **High-risk areas** | Status filter hierarchy (preserve order) |
| **Recommended approach** | Extract helper predicates |
| **Estimated effort** | Low-medium (2-3 hours with tests) |
| **Should be skipped?** | NO |

**Final Recommendation:** Proceed with refactoring after adding:
1. A combined multi-filter test
2. A derelict/damaged precedence test
3. A partial filter state test

These tests will provide a safety net for the status filter hierarchy, which is the highest-risk area.
