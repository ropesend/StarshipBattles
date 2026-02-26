# Safety Analysis: `filter_ships` Function

**Target:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py` (lines 124-222)

**Date:** 2026-02-26

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of filter flags. It handles 6 orthogonal filter categories:

1. **Warp Capability** - `show_warp_capable`, `show_not_warp_capable`
2. **Spaceyard Capability** - `show_has_spaceyard`, `show_no_spaceyard`
3. **Cargo Status** - `show_has_cargo`, `show_no_cargo`
4. **Special Capabilities** (5 abilities via `SPECIAL_CAPABILITY_COLUMNS`)
5. **Ship Status** - `show_destroyed`, `show_derelict`, `show_damaged`, `show_undamaged`

**Complexity Sources:**
- 99 lines spanning multiple filter categories
- Nested conditionals and early `continue` statements
- Late imports inside the loop (performance concern)
- Ship status hierarchy (destroyed > derelict > damaged > undamaged)

---

## 2. Edge Cases and Error Handling Paths

### 2.1 Missing filter_state Keys (Handled)
All filter lookups use `.get(key, True)` which defaults to showing ships when keys are missing. This is correct defensive behavior.

### 2.2 Cargo Edge Cases
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
- **Empty dict:** `{}` -> `has_cargo = False` (correct)
- **Dict with zeros:** `{'minerals': 0}` -> `has_cargo = False` (correct - tested)
- **None cargo_contents:** Would raise `TypeError` on `bool(None)` - but dataclass defaults to `{}` so safe in practice

### 2.3 Ship Status Hierarchy
The ordering of status checks is **critical** and represents an invariant:
```python
# Order: destroyed -> derelict -> damaged -> undamaged
if not ship.is_alive:  # DESTROYED
    ...
if ship.is_derelict:   # DERELICT (implies damaged)
    ...
if ship.is_damaged():  # DAMAGED
    ...
# else UNDAMAGED
```

**Invariant:** A derelict ship is always damaged (per `is_damaged()` implementation), so the derelict check must come before the damaged check to avoid double-counting.

### 2.4 Special Capability Filter Key Derivation
```python
no_key = col_id.replace('can_', 'no_', 1)
```
This transformation:
- `can_destroy_planet` -> `no_destroy_planet`
- Assumes all column IDs start with `can_` prefix

---

## 3. Invariants That Must Be Preserved

### 3.1 CRITICAL: Status Check Order
The status checks (destroyed/derelict/damaged/undamaged) are **mutually exclusive categories** and MUST be evaluated in this exact order:
1. `not ship.is_alive` (destroyed)
2. `ship.is_derelict`
3. `ship.is_damaged()`
4. Undamaged (fallback)

Reordering these checks will cause ships to be incorrectly categorized.

### 3.2 CRITICAL: Short-Circuit Behavior
Each filter category uses short-circuit logic:
```python
if not show_warp or not show_not_warp:
    # Only calculate warp capability if at least one filter is disabled
```
This is a **performance optimization** - capability checks are expensive (call external calculators). Refactoring must preserve this optimization.

### 3.3 CRITICAL: `continue` Semantics
Each filter category can exclude a ship via `continue`. The function uses early-exit semantics - if any filter fails, the ship is excluded. This is correct AND/filter behavior (all categories must pass).

### 3.4 Filter Default Behavior
All filters default to `True` (show). A ship passes a filter category if both flags are `True` OR if the ship matches the enabled flag.

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Status Hierarchy Coupling
The status checks at the end of the function form a "waterfall" pattern where ships are appended and the function continues to the next iteration. Breaking this into separate functions risks:
- Losing the mutual exclusivity guarantee
- Allowing ships to pass multiple status checks

### 4.2 MEDIUM RISK: Late Imports
The function has late imports inside the loop:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
These appear in:
- Spaceyard check (line 159)
- Special capability check (line 185)

Refactoring might be tempted to move these to module level, but they're late imports **to avoid circular dependencies**. The comment "INTENTIONAL LATE IMPORT" is missing here (present in `sort_ships`).

### 4.3 MEDIUM RISK: Boolean Flag Transformation
The special capability filter derives `show_no_*` keys from `show_can_*` via string replacement. This coupling between filter_state keys and SPECIAL_CAPABILITY_COLUMNS is fragile.

### 4.4 LOW RISK: Cargo Calculation
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
This is a subtle truthiness check - must be preserved exactly.

---

## 5. Test Coverage Analysis

### 5.1 Existing Test Coverage (GOOD)
The test file `tests/unit/ui/screens/test_fleet_report_filters.py` has comprehensive coverage:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestFilterShips` | 4 | Basic damaged/undamaged/derelict/destroyed |
| `TestFilterShipsWarp` | 3 | Warp capability filtering |
| `TestFilterShipsSpaceyard` | 3 | Spaceyard filtering |
| `TestFilterShipsCargo` | 5 | Cargo filtering including edge cases |
| `TestSpecialCapabilityFilter` | 3 | Special ability filtering |

**Total: 18 tests directly covering `filter_ships`**

### 5.2 Coverage Gaps (SHOULD ADD BEFORE REFACTORING)

1. **Empty ship list:** No test for `filter_ships([], filter_state)` - should return `[]`

2. **All filters disabled:** No test where all filters are `False` - should return `[]`

3. **Status priority tests:** No explicit test that a derelict ship is NOT matched by the damaged filter when `show_derelict=False, show_damaged=True`

4. **Combined filter tests:** Tests only check one filter category at a time. Need tests combining:
   - Warp + Damaged filters
   - Spaceyard + Cargo filters
   - Special capability + Status filters

5. **Multiple special capabilities:** No test with ships having multiple special abilities

6. **Missing filter_state keys:** No test verifying default behavior when filter_state is partially populated

### 5.3 Mock Quality
Tests use `MagicMock(spec=ShipInstance)` which is appropriate. However:
- `cargo_contents` is set directly on mock, not via `spec`
- `is_damaged()` is mocked as a method but actual implementation checks multiple conditions

---

## 6. Recommendation

### PROCEED WITH CAUTION

The function is refactorable, but requires careful attention to invariants.

**Recommended Refactoring Approach:**

1. **Extract filter predicates** (LOW RISK):
   ```python
   def _passes_warp_filter(ship, filter_state) -> bool
   def _passes_spaceyard_filter(ship, filter_state) -> bool
   def _passes_cargo_filter(ship, filter_state) -> bool
   def _passes_special_capability_filters(ship, filter_state) -> bool
   ```

2. **PRESERVE status waterfall as-is** (HIGH VALUE):
   The destroyed/derelict/damaged/undamaged section should NOT be extracted to a separate function. The current structure is correct and readable.

3. **Add missing tests FIRST:**
   - Empty list test
   - Combined filter test
   - Status priority test

### Pre-Refactoring Checklist

- [ ] Add test: `filter_ships([], any_state)` returns `[]`
- [ ] Add test: All filters `False` returns `[]`
- [ ] Add test: Derelict ship excluded when `show_derelict=False` but NOT by `show_damaged`
- [ ] Add test: Combined warp + status filter
- [ ] Add test: Partial filter_state with missing keys
- [ ] Run full test suite to establish baseline

### Refactoring Constraints

1. **DO NOT** reorder status checks (destroyed > derelict > damaged > undamaged)
2. **DO NOT** move late imports to module level without verifying no circular import
3. **DO NOT** change the short-circuit optimization pattern
4. **DO** preserve the default `True` behavior for missing filter keys
5. **DO** preserve the AND semantics (ship must pass ALL filter categories)

---

## 7. Verdict

**Refactorable: YES, with conditions**

The function has good test coverage and clear logic. The primary risks are:
1. Breaking the status hierarchy invariant
2. Losing the short-circuit performance optimization

If the recommended tests are added and the refactoring constraints are followed, this function can be safely refactored to improve readability by extracting filter predicates.

**Do NOT skip this function** - it is a good candidate for complexity reduction through predicate extraction.
