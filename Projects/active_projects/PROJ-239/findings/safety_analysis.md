# Safety Analysis: filter_ships Function Refactoring

## Executive Summary

The `filter_ships` function (lines 124-222 in `fleet_report_filters.py`) has a cyclomatic complexity of 36 due to its multiple filter categories. **This function IS refactorable** with low risk, as it follows a clear, repetitive pattern that can be extracted into helper functions without changing behavior.

---

## 1. Edge Cases and Error Handling Paths

### 1.1 Edge Cases Identified in Code

| Edge Case | Location | Current Handling | Test Coverage |
|-----------|----------|------------------|---------------|
| Empty ship list | Line 141 | Returns empty list (loop doesn't execute) | Implicit in `test_filter_show_all` |
| Empty filter_state dict | Lines 144-145 | Uses `.get()` with `True` default | **NOT TESTED** |
| `cargo_contents` is None | Line 170 | `bool(ship.cargo_contents)` handles it | **NOT TESTED** |
| `cargo_contents` with zero values | Line 170 | `sum(ship.cargo_contents.values()) > 0` check | Covered in `test_filter_cargo_zero_value_treated_as_no_cargo` |
| Ship is destroyed AND derelict | Lines 196-208 | Destroyed checked first | Implicit - but edge case possible |
| Ship is derelict AND damaged | Lines 203-215 | Derelict checked before damaged | **NOT TESTED EXPLICITLY** |

### 1.2 Error Handling Analysis

The function has **no explicit error handling** (no try/except blocks). It relies on:
1. Ship objects having the expected interface (`is_alive`, `is_derelict`, `is_damaged()`, `cargo_contents`)
2. `filter_state` being a dict-like object
3. External services (`ShipStatsCalculator`, `FleetCapabilityCalculator`) not raising exceptions

**Risk:** If any ship object is malformed or external services fail, the function will raise an unhandled exception.

---

## 2. Invariants That Must Be Preserved

### 2.1 Filter Order Invariants

The function applies filters in a **specific order that affects results**:

```
1. Warp capability filter
2. Spaceyard capability filter
3. Cargo filter
4. Special capability filters (SPECIAL_CAPABILITY_COLUMNS loop)
5. Destroyed filter (early exit with append)
6. Derelict filter (early exit with append)
7. Damaged filter (early exit with append)
8. Undamaged (default case)
```

**CRITICAL:** The status filters (destroyed, derelict, damaged, undamaged) are **mutually exclusive** with early returns. A ship can only be categorized as ONE of these. The order matters:
- Destroyed ships skip all other status checks
- Derelict ships skip damaged/undamaged checks
- Damaged ships skip undamaged check

### 2.2 Semantic Invariants

| Invariant | Description |
|-----------|-------------|
| No filter modification | Input `filter_state` dict must not be modified |
| Order preservation | Output list order should match input order (ships that pass filters) |
| Idempotency | Filtering same list twice with same state yields identical results |
| Default behavior | Missing filter keys default to `True` (show all) |

### 2.3 Filter Logic Invariants

For binary filters (e.g., warp_capable/not_warp_capable):
- If BOTH are True: all ships pass this filter
- If BOTH are False: no ships pass (empty result)
- If ONE is True: only matching ships pass

---

## 3. Risk Areas Where Refactoring Could Introduce Bugs

### 3.1 HIGH RISK: Filter Application Order

**Risk:** Extracting filter logic into separate functions and calling them in different order could change which ships pass.

**Example:** If capability filters are applied AFTER status filters instead of BEFORE, a destroyed ship with warp capability would be handled differently.

**Mitigation:** Keep all capability/ability filters as early-exit checks before the status categorization block. Or convert to a predicate-based approach where ALL predicates must pass.

### 3.2 MEDIUM RISK: Mutually Exclusive Status Categories

**Risk:** The status filters (destroyed, derelict, damaged, undamaged) use a cascading if-elif pattern with `continue` and `append` statements. Extracting this could break the mutual exclusivity.

**Current Pattern:**
```python
# Destroyed check
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue  # <-- CRITICAL: prevents further checks

# Derelict check (only reached if ship IS alive)
if ship.is_derelict:
    ...
```

**Mitigation:** Either:
1. Keep this block inline and only extract the capability filters
2. Create a `get_ship_status(ship) -> str` helper that returns one of: 'destroyed', 'derelict', 'damaged', 'undamaged'

### 3.3 MEDIUM RISK: Late Import Pattern

**Risk:** The function has intentional late imports inside conditional blocks:
- Line 149: `ShipStatsCalculator` (for warp)
- Line 159: `FleetCapabilityCalculator` (for spaceyard)
- Line 185: `FleetCapabilityCalculator` (for abilities)

**Mitigation:** If extracting helpers, ensure imports remain inside the helper or are moved to top-level (after confirming no circular import issues).

### 3.4 LOW RISK: Special Capability Filter Key Derivation

**Risk:** The special capability filter uses string manipulation:
```python
no_key = col_id.replace('can_', 'no_', 1)
```

This assumes all special capability column IDs start with `can_`. Currently true for:
- `can_destroy_planet`
- `can_open_warp`
- `can_close_warp`
- `can_destroy_star`
- `can_create_sphere`

**Mitigation:** Add assertion or guard clause if extracting this logic.

---

## 4. Missing Test Coverage That Should Be Added BEFORE Refactoring

### 4.1 Critical Missing Tests

| Test Case | Priority | Reason |
|-----------|----------|--------|
| Empty filter_state dict | HIGH | Verifies default behavior when no filters specified |
| ship.cargo_contents is None | HIGH | Runtime error if not handled |
| Both warp filters False | MEDIUM | Should return empty list for warp section |
| Both spaceyard filters False | MEDIUM | Should return empty list for yard section |
| Ship is derelict AND damaged | MEDIUM | Verify derelict takes precedence |
| All filters False | HIGH | Verify completely empty result |

### 4.2 Recommended Test Additions

```python
# 1. Empty filter state uses defaults (show all)
def test_filter_empty_filter_state_shows_all():
    ships = [make_mock_ship(), make_mock_ship()]
    result = filter_ships(ships, {})
    assert len(result) == 2

# 2. cargo_contents is None doesn't crash
def test_filter_cargo_none_treated_as_no_cargo():
    ship = make_mock_ship()
    ship.cargo_contents = None
    filter_state = {'show_has_cargo': False, 'show_no_cargo': True}
    result = filter_ships([ship], filter_state)
    assert len(result) == 1  # Should pass (no cargo)

# 3. Both warp filters off excludes all
def test_filter_both_warp_filters_false_excludes_all():
    ships = [make_mock_ship(warp_tonnage=1000), make_mock_ship(warp_tonnage=None)]
    filter_state = {'show_warp_capable': False, 'show_not_warp_capable': False}
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

# 4. Derelict ship also marked as damaged - derelict wins
def test_filter_derelict_and_damaged_categorized_as_derelict():
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {'show_derelict': True, 'show_damaged': False}
    result = filter_ships([ship], filter_state)
    assert len(result) == 1  # Passes because derelict=True, not rejected by damaged

# 5. All capability filters False gives empty result
def test_filter_all_capability_filters_false():
    ship = make_mock_ship()
    filter_state = {
        'show_has_spaceyard': False, 'show_no_spaceyard': False,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0
```

### 4.3 Integration Test Gap

The tests use `MagicMock` for `FleetCapabilityCalculator`. There's no integration test using real ships with actual component data. This is acceptable for unit tests but worth noting.

---

## 5. Refactorability Assessment

### 5.1 Conclusion: REFACTORABLE

The `filter_ships` function **IS refactorable** with moderate effort.

### 5.2 Recommended Approach

**Option A: Extract Capability Filter Predicates (Recommended)**

Convert each capability check into a predicate function:
```python
def _passes_warp_filter(ship, filter_state) -> bool:
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if show_warp and show_not_warp:
        return True
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        return False
    if not is_warp_capable and not show_not_warp:
        return False
    return True
```

Then the main function becomes:
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        # ... etc
        result.append(ship)
    return result
```

**Expected Complexity Reduction:**
- Current: 36
- After extraction: ~10-12 in main function
- Each helper: 4-6

**Option B: Predicate List Pattern**

More elegant but bigger change:
```python
def filter_ships(ships, filter_state):
    predicates = [
        lambda s: _passes_warp_filter(s, filter_state),
        lambda s: _passes_spaceyard_filter(s, filter_state),
        lambda s: _passes_cargo_filter(s, filter_state),
        # ... etc
    ]
    return [s for s in ships if all(p(s) for p in predicates)]
```

### 5.3 Risk Assessment

| Factor | Assessment |
|--------|------------|
| Test coverage | Good (48 tests in test file) |
| Function complexity | High but repetitive |
| Dependencies | External services, but well-mocked in tests |
| Refactoring difficulty | Low-Medium |
| Regression risk | Low with existing tests |

---

## 6. Pre-Refactoring Checklist

Before starting refactoring:

- [ ] Add test for empty filter_state dict
- [ ] Add test for cargo_contents=None
- [ ] Add test for both warp filters False
- [ ] Add test for derelict+damaged ship categorization
- [ ] Run full test suite and confirm baseline passes
- [ ] Create a backup/snapshot of current implementation

---

## 7. Summary

| Question | Answer |
|----------|--------|
| Is this function refactorable? | **YES** |
| What's the main complexity driver? | Multiple parallel filter categories (6+) with binary options |
| Recommended approach? | Extract capability filter predicates as helper functions |
| Risk level? | **LOW** - repetitive pattern, good test coverage |
| Blockers? | Add ~4 missing edge case tests first |
| Expected final complexity? | 10-12 (main function) |
