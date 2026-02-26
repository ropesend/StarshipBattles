# Safety Analysis: filter_ships Function

**Target:** `game/ui/screens/fleet_report_filters.py::filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (Grade: F)
**Function Length:** 99 lines

## 1. Function Structure Overview

The `filter_ships` function applies multiple filters in sequence to a list of ships. Each filter is a binary filter pair (show_X / show_not_X pattern).

### Filter Stages (in evaluation order)

| Stage | Filter Pair | Lines | Dependencies |
|-------|-------------|-------|--------------|
| 1 | Warp capability | 143-153 | `ShipStatsCalculator.has_warp_capability()` |
| 2 | Spaceyard capability | 155-164 | `FleetCapabilityCalculator.ship_has_spaceyard()` |
| 3 | Cargo contents | 166-174 | Direct attribute access (`ship.cargo_contents`) |
| 4 | Special capabilities | 176-194 | `FleetCapabilityCalculator.ship_has_ability()`, `SPECIAL_CAPABILITY_COLUMNS` |
| 5 | Ship status (destroyed) | 196-201 | `ship.is_alive` |
| 6 | Ship status (derelict) | 203-208 | `ship.is_derelict` |
| 7 | Ship status (damaged) | 210-215 | `ship.is_damaged()` |
| 8 | Ship status (undamaged) | 217-220 | Implicit (else case) |

---

## 2. Critical Invariants

### 2.1 Filter Order is Semantically Important

**CRITICAL:** The ship status filters (destroyed -> derelict -> damaged -> undamaged) MUST be evaluated in this exact order because they form a **hierarchy of mutual exclusivity**:

```
destroyed (is_alive == False)
    -> derelict (is_derelict == True, implies damaged)
        -> damaged (is_damaged() == True)
            -> undamaged (else)
```

A derelict ship IS damaged, so if we checked `is_damaged()` before `is_derelict`, a derelict ship would match the "damaged" category instead of "derelict".

**Risk Level:** HIGH
**Test Coverage:** Partial - Tests verify individual filters but not explicitly the hierarchy ordering.

### 2.2 Binary Filter Pairs Default to True

All filters default to `True` via `.get(key, True)`:
- This means **missing filter keys show all ships** (safe default)
- Changing this would break backward compatibility

**Risk Level:** MEDIUM
**Test Coverage:** Implicit (tested through various filter combinations)

### 2.3 Early Continue Pattern

The function uses early `continue` statements to skip ships that don't match filter criteria. The capability filters (warp, spaceyard, cargo, special) apply first and can skip ships before the status classification.

**Risk Level:** LOW (consistent pattern)
**Test Coverage:** GOOD

### 2.4 Special Capability Filter Key Derivation

The special capability filters derive their keys dynamically:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This relies on `SPECIAL_CAPABILITY_COLUMNS` keys following the pattern `can_*`.

**Risk Level:** MEDIUM (implicit contract with fleet_data_source.py)
**Test Coverage:** Tested for DestroyPlanet in `TestSpecialCapabilityFilter`

---

## 3. Edge Cases

### 3.1 Empty Ship List
- **Behavior:** Returns empty list
- **Test Coverage:** Not explicitly tested but trivially correct (loop doesn't execute)
- **Recommendation:** Add explicit test for empty input

### 3.2 Empty Filter State
- **Behavior:** All filters default to True, all ships pass
- **Test Coverage:** Partially tested via `test_filter_default_shows_all`
- **Risk:** Low

### 3.3 Cargo with Zero Values
- **Behavior:** Ships with `cargo_contents = {'minerals': 0}` treated as "no cargo"
- **Test Coverage:** GOOD - `test_filter_cargo_zero_value_treated_as_no_cargo`
- **Line:** `has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`

### 3.4 Ship with Both Derelict and Destroyed States
- **Behavior:** Undefined (could happen if `is_alive=False` and `is_derelict=True`)
- **Test Coverage:** NOT TESTED
- **Recommendation:** Add test to verify destroyed takes precedence

### 3.5 None Cargo Contents
- **Behavior:** Safe - `bool(None) == False`
- **Test Coverage:** Not explicitly tested
- **Recommendation:** Add explicit test

---

## 4. External Dependencies

### 4.1 ShipStatsCalculator.has_warp_capability(ship)
- **Location:** `game/strategy/services/ship_stats_calculator.py`
- **Import:** Module-level import
- **Test Coverage:** Well-tested in `test_warp.py` (13 tests)
- **Risk:** LOW - Stable API

### 4.2 FleetCapabilityCalculator (late imports)
- **Location:** `game/strategy/data/fleet_capability_calculator.py`
- **Import:** LATE IMPORT inside function (lines 159, 185)
- **Methods Used:**
  - `ship_has_spaceyard(ship)`
  - `ship_has_ability(ship, ability_name)`
- **Test Coverage:** Mocked in filter tests
- **Risk:** MEDIUM - Late imports could fail at runtime

### 4.3 SPECIAL_CAPABILITY_COLUMNS
- **Location:** `game/ui/screens/fleet_data_source.py`
- **Import:** Module-level import
- **Value:**
  ```python
  {
      "can_destroy_planet": "DestroyPlanet",
      "can_open_warp": "OpenWarpPoint",
      "can_close_warp": "CloseWarpPoint",
      "can_destroy_star": "DestroyStar",
      "can_create_sphere": "CreateSphereWorld",
  }
  ```
- **Risk:** LOW - Static dictionary

---

## 5. Test Coverage Analysis

### 5.1 Current Test Coverage

| Filter Category | Tests | Notes |
|-----------------|-------|-------|
| Damaged/Undamaged | 2 | `test_filter_hide_damaged`, `test_filter_hide_undamaged` |
| Derelict | 1 | `test_filter_hide_derelict` |
| Destroyed | 1 | `test_filter_hide_destroyed` |
| Warp Capable | 3 | `TestFilterShipsWarp` class |
| Spaceyard | 3 | `TestFilterShipsSpaceyard` class |
| Cargo | 5 | `TestFilterShipsCargo` class |
| Special Capabilities | 3 | `TestSpecialCapabilityFilter` class |
| Show All | 1 | `test_filter_show_all` |

### 5.2 Missing Test Coverage (MUST ADD BEFORE REFACTORING)

1. **Empty ship list**: Verify returns empty list
2. **All filters disabled**: Verify returns empty list (edge case)
3. **Filter order precedence**: Test that a derelict ship is NOT matched as "damaged"
4. **Destroyed + Derelict combination**: Test undefined state handling
5. **None cargo_contents**: Test `ship.cargo_contents = None`
6. **Multiple special capabilities on one ship**: Test interaction
7. **Combined filter interactions**:
   - Warp + Damaged filter combination
   - Spaceyard + Cargo filter combination
   - All capability filters disabled

### 5.3 Test Quality Assessment

- **Mocking Strategy:** Consistent use of `unittest.mock`
- **Isolation:** Tests are well-isolated
- **Assertion Quality:** Direct assertions on expected outcomes
- **Integration:** ViewModel tests verify filter integration

---

## 6. Refactoring Risk Areas

### 6.1 HIGH RISK: Status Filter Hierarchy

The sequential `if/elif` chain for ship status (lines 196-220) cannot be parallelized or reordered without breaking semantics.

**Recommendation:** If extracting to separate functions, preserve the evaluation order explicitly or use a status enum/priority system.

### 6.2 MEDIUM RISK: Late Imports

The late imports of `FleetCapabilityCalculator` exist to avoid circular imports. Moving code could trigger import errors.

**Recommendation:**
- Test the refactored code in isolation
- Consider dependency injection pattern

### 6.3 MEDIUM RISK: Filter Key Naming Convention

The special capability filter keys are derived dynamically using string manipulation (`col_id.replace('can_', 'no_', 1)`). Any refactoring must preserve this convention.

**Recommendation:** Add tests that verify the key derivation matches `FleetListViewModel.get_filter_state()` output.

### 6.4 LOW RISK: Boolean Short-Circuit Optimization

Lines like `if not show_warp or not show_not_warp:` use short-circuit evaluation for performance. This is an optimization, not a semantic requirement.

---

## 7. Recommendations

### Before Refactoring (REQUIRED)

1. **Add missing tests:**
   ```python
   def test_filter_empty_list_returns_empty():
       assert filter_ships([], {}) == []

   def test_derelict_not_matched_as_damaged():
       # Derelict ship should match show_derelict, NOT show_damaged
       pass

   def test_cargo_contents_none_treated_as_no_cargo():
       pass

   def test_all_filters_disabled_returns_empty():
       pass
   ```

2. **Run full test suite** before starting refactoring

3. **Create characterization tests** that capture current behavior:
   - Generate test cases with all 2^n filter combinations for small n
   - Record expected outputs

### Refactoring Strategy

**Recommended Approach:** Extract filter predicates into separate functions while preserving the main loop structure.

```python
# SAFE: Extract predicate functions
def _passes_warp_filter(ship, filter_state) -> bool:
    ...

def _passes_spaceyard_filter(ship, filter_state) -> bool:
    ...

def _passes_cargo_filter(ship, filter_state) -> bool:
    ...

def _passes_special_capability_filter(ship, filter_state) -> bool:
    ...

def _get_ship_status_category(ship) -> str:
    """Returns: 'destroyed', 'derelict', 'damaged', or 'undamaged'"""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _passes_status_filter(ship, filter_state) -> bool:
    category = _get_ship_status_category(ship)
    return filter_state.get(f'show_{category}', True)
```

This approach:
- Reduces cyclomatic complexity in `filter_ships`
- Preserves the filter order (still a single loop)
- Makes each predicate independently testable

---

## 8. Refactorability Assessment

**Verdict: SAFE TO REFACTOR** with the following conditions:

| Condition | Status |
|-----------|--------|
| Existing tests provide baseline | PARTIAL - need to add missing cases |
| No hidden dependencies | YES - dependencies are explicit |
| Behavior is deterministic | YES |
| No threading/async concerns | YES |
| No side effects | YES |

**Estimated Effort:** Medium (4-6 hours including test additions)

**Recommended Complexity Target:** CC <= 15 (split into 3-4 smaller functions)
