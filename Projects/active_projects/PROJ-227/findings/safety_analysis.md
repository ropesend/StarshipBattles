# Safety Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (grade F)
**Analysis Date:** 2026-02-26

---

## 1. Edge Cases and Error Handling Paths

### Empty Input Handling
- **Empty ships list:** Returns empty list (line 141 initializes `result = []`, loop does nothing)
- **Empty filter_state dict:** All filters default to `True` via `.get()` calls with default values
- **None values:** NOT handled - passing `None` for ships or filter_state would raise exceptions

### Status State Priority (Critical Logic)
The function applies status filters in a specific priority order (lines 197-220):
1. **Destroyed** (`is_alive == False`) - checked first
2. **Derelict** (`is_derelict == True`) - checked before damaged
3. **Damaged** (`is_damaged() == True`) - only if not destroyed/derelict
4. **Undamaged** - catch-all for healthy ships

**Invariant:** A ship can only match ONE status category. The early-return pattern (`result.append(ship); continue`) enforces mutual exclusivity.

### Filter Defaults
All filters default to `True` (show all), which is the safe default:
- `filter_state.get('show_damaged', True)`
- `filter_state.get('show_warp_capable', True)`
- etc.

---

## 2. Invariants That Must Be Preserved During Refactoring

### 2.1 Filter Application Order
The current order matters for correctness:
1. **Capability filters first** (warp, spaceyard, cargo, special abilities)
2. **Status filters last** (destroyed, derelict, damaged, undamaged)

A ship must pass ALL capability filters before status filtering. Any refactoring must preserve this AND logic.

### 2.2 Mutual Exclusivity of Status Categories
A ship is classified into exactly ONE status:
- Destroyed ships skip damaged/derelict checks
- Derelict ships skip damaged check
- Damaged ships skip undamaged check

**Risk:** Extracting status filtering to a helper could accidentally allow ships to match multiple categories.

### 2.3 Short-Circuit Optimization
When both halves of a capability filter are enabled (e.g., `show_warp_capable=True` AND `show_not_warp_capable=True`), the expensive capability check is skipped entirely:
```python
if not show_warp or not show_not_warp:  # Only check if filtering needed
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
```
**Invariant:** Refactoring must preserve this optimization to avoid performance regression.

### 2.4 Late Import Pattern
The function uses intentional late imports for:
- `FleetCapabilityCalculator.ship_has_spaceyard()`
- `FleetCapabilityCalculator.ship_has_ability()`

**Rationale:** Avoids circular imports with strategy layer.
**Risk:** Moving code to helper functions could trigger import loops if not carefully structured.

### 2.5 Cargo Content Check Logic
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
This handles:
- `cargo_contents = None` - `bool(None) = False`
- `cargo_contents = {}` - `bool({}) = False`
- `cargo_contents = {'minerals': 0}` - `sum() = 0`, treated as no cargo

### 2.6 Special Capability Filter Key Derivation
Dynamic key generation from SPECIAL_CAPABILITY_COLUMNS:
```python
no_key = col_id.replace('can_', 'no_', 1)  # 'can_destroy_planet' -> 'no_destroy_planet'
```
**Invariant:** The naming convention MUST be consistent between fleet_report_filters.py and fleet_report_view_model.py.

---

## 3. Risk Areas Where Refactoring Could Introduce Bugs

### HIGH RISK

1. **Breaking Status Mutual Exclusivity**
   - Extracting status logic into helper functions could accidentally remove early returns
   - Must preserve the `continue` statements that enforce one-status-per-ship

2. **Changing Filter Application Order**
   - Moving capability filters after status filters would change behavior
   - Ships could be incorrectly included/excluded

3. **Import Cycles**
   - Moving capability checks to separate module could trigger circular imports
   - Must keep FleetCapabilityCalculator imports inside function scope

### MEDIUM RISK

4. **Losing Short-Circuit Optimization**
   - Naive extraction of capability checks would always compute capabilities
   - Could cause noticeable performance regression on large fleets

5. **Special Capability Loop Break Logic**
   - The `_skip` flag pattern with `break` is fragile
   - If extracted, must preserve early-exit behavior

### LOW RISK

6. **Cargo Check Edge Cases**
   - Empty dict vs None vs zero-sum dict all behave correctly now
   - Simplifying could break an edge case

---

## 4. Missing Test Coverage That Should Be Added BEFORE Refactoring

### Critical Missing Tests

1. **Empty Input Tests**
   ```python
   def test_filter_ships_empty_list():
       assert filter_ships([], {}) == []

   def test_filter_ships_empty_filter_state():
       # Should use defaults (show all)
   ```

2. **All Filters Disabled (Edge Case)**
   ```python
   def test_filter_hide_everything():
       # When ALL status filters are False, should return empty list
       filter_state = {
           'show_damaged': False,
           'show_undamaged': False,
           'show_derelict': False,
           'show_destroyed': False,
       }
   ```

3. **Mutually Exclusive Status Tests**
   ```python
   def test_destroyed_derelict_ship_only_counts_as_destroyed():
       # Ship with is_alive=False AND is_derelict=True
       # Should only match destroyed filter

   def test_derelict_damaged_ship_only_counts_as_derelict():
       # Ship with is_derelict=True AND is_damaged()=True
       # Should only match derelict filter
   ```

4. **Combined Capability + Status Filtering**
   ```python
   def test_filter_warp_capable_damaged_ships():
       # Verify both filters apply together (AND logic)

   def test_filter_multiple_special_abilities():
       # Ship with multiple abilities, filtering by one
   ```

5. **Filter State Missing Keys**
   ```python
   def test_filter_partial_filter_state():
       # Only some keys present, others should default to True
   ```

6. **Performance Regression Test** (if applicable)
   ```python
   def test_filter_large_fleet_performance():
       # Ensure optimization isn't lost
   ```

### Existing Coverage Assessment

| Test Category | Coverage Status |
|--------------|-----------------|
| Basic status filtering | COVERED (TestFilterShips class) |
| Warp capability filtering | COVERED (TestFilterShipsWarp) |
| Spaceyard filtering | COVERED (TestFilterShipsSpaceyard) |
| Cargo filtering | COVERED (TestFilterShipsCargo) |
| Special capability filtering | COVERED (TestSpecialCapabilityFilter) |
| Empty input handling | NOT COVERED |
| Partial filter_state | NOT COVERED |
| Status mutual exclusivity | NOT COVERED |
| Combined filter scenarios | NOT COVERED |
| Hide-all edge case | NOT COVERED |

---

## 5. Refactorability Assessment

### Recommendation: REFACTORABLE with Caution

The function is refactorable, but requires careful attention to:

1. **Preserve filter application order** (capabilities before status)
2. **Preserve status mutual exclusivity** (early returns)
3. **Preserve short-circuit optimization** (skip capability checks when both halves enabled)
4. **Keep late imports in function scope** (avoid circular imports)

### Suggested Refactoring Approach

**Strategy 1: Extract Capability Predicates (Recommended)**
```python
def _passes_warp_filter(ship, show_warp, show_not_warp) -> bool:
    if show_warp and show_not_warp:
        return True  # No filtering needed
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        return False
    if not is_warp_capable and not show_not_warp:
        return False
    return True
```

**Strategy 2: Extract Status Classification**
```python
def _get_ship_status(ship) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

Then map status to filter key: `f'show_{status}'`

### What NOT To Do

- Do NOT convert to dict-based dispatch - loses the early-return optimization
- Do NOT extract special capability loop to separate function without preserving `_skip` pattern
- Do NOT use comprehensions - they obscure the short-circuit logic

---

## 6. Pre-Refactoring Checklist

- [ ] Add test for empty ships list
- [ ] Add test for partial/missing filter_state keys
- [ ] Add test for mutually exclusive status handling
- [ ] Add test for combined capability + status filters
- [ ] Add test for all-filters-disabled edge case
- [ ] Review test mock setup matches real ShipInstance behavior
- [ ] Run full test suite to establish baseline
- [ ] Verify no other callers beyond FleetListViewModel._refresh()

---

## Summary

| Criterion | Assessment |
|-----------|------------|
| Edge cases identified | 6 categories |
| Critical invariants | 6 rules |
| High-risk refactoring areas | 3 |
| Missing test coverage | 6 test categories |
| Refactorability verdict | YES, with caution |
| Recommended approach | Extract capability predicates first, then status classification |
| Should skip? | NO - function is complex but refactorable |
