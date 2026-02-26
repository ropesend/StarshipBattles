# Safety Analysis: `filter_ships` Function

## Target Information
- **File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Cyclomatic Complexity:** 36 (grade F)
- **Length:** ~99 lines

---

## 1. Edge Cases and Error Handling Paths

### 1.1 Empty/Missing Inputs
- **Empty ships list:** Returns empty list (implicit - loop doesn't execute)
- **Missing filter keys:** Uses `.get()` with default `True` for all filter states
  - This is a critical invariant: missing keys = show all

### 1.2 Ship State Edge Cases
- **Derelict ships:** Checked BEFORE damaged (line 204) because derelict implies damaged
- **Destroyed ships:** Checked FIRST via `is_alive` (line 197) - exclusive category
- **Undamaged ships:** Fall-through case (line 217-220)

### 1.3 Capability Detection Edge Cases
- **Warp capability:** Calls `ShipStatsCalculator.has_warp_capability(ship)`
  - Depends on ship mass vs warp_max_tonnage comparison
  - Zero mass edge case returns False (tested)
- **Spaceyard:** Late import of `FleetCapabilityCalculator`
- **Special abilities:** Dynamic iteration over `SPECIAL_CAPABILITY_COLUMNS`
  - Filter key derivation: `can_X` -> `show_can_X` / `show_no_X`

### 1.4 Cargo Detection Edge Cases
- **Empty cargo dict:** `{}` treated as no cargo
- **Zero-value cargo:** `{'minerals': 0}` treated as no cargo (sum == 0)
- **Population as cargo:** Explicitly tested and supported

---

## 2. Invariants That Must Be Preserved

### 2.1 Filter Semantics
1. **All filters default to True** - if a filter key is missing, show all ships
2. **Both-true optimization:** When both sides of a binary filter are True (e.g., `show_warp_capable=True, show_not_warp_capable=True`), skip the capability check entirely
3. **Order of status checks matters:**
   - Destroyed -> Derelict -> Damaged -> Undamaged
   - A ship can only match ONE status category

### 2.2 Filter Independence
- Warp, spaceyard, cargo, and special capability filters are independent
- Status filters (damaged/undamaged/derelict/destroyed) are mutually exclusive
- A ship must pass ALL active filters to be included

### 2.3 Early Exit Pattern
- Each filter uses `continue` to skip ships that don't pass
- Ships are only added to `result` in the status-checking section (lines 200, 207, 214, 220)

### 2.4 Import Behavior
- `FleetCapabilityCalculator` is imported inside the loop when needed
- This is intentional to avoid circular imports
- Imports occur only when filter is active (optimization)

---

## 3. Risk Areas for Refactoring

### 3.1 HIGH RISK: Filter Evaluation Order
The current implementation checks filters in this order:
1. Warp capability
2. Spaceyard capability
3. Cargo
4. Special capabilities (loop)
5. Destroyed status
6. Derelict status
7. Damaged status
8. Undamaged (fallthrough)

**Risk:** If refactored into separate predicate functions, the order and early-exit behavior must be preserved exactly, or performance could degrade significantly.

### 3.2 MEDIUM RISK: Special Capability Loop
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
```
**Risk:** The key transformation (`can_X` -> `no_X`) is non-obvious. Any refactoring must preserve this exact mapping.

### 3.3 MEDIUM RISK: Boolean Short-Circuit Logic
```python
if not show_warp or not show_not_warp:
    # Only check capability if either filter is disabled
```
**Risk:** This optimization pattern is repeated for each filter type. If extracted, the optimization must be preserved.

### 3.4 LOW RISK: Status Categorization
The mutual exclusivity of destroyed/derelict/damaged/undamaged is implicitly enforced by check order with early returns. Making this explicit via a helper function is safer.

---

## 4. Missing Test Coverage

### 4.1 Gaps Identified

| Scenario | Current Coverage | Risk Level |
|----------|-----------------|------------|
| Both warp filters False | NOT TESTED | Medium |
| Both cargo filters False | NOT TESTED | Medium |
| Both spaceyard filters False | NOT TESTED | Medium |
| Multiple special capability filters active | NOT TESTED | Medium |
| Empty filter_state dict | NOT TESTED | Low |
| Ship that is both derelict AND destroyed | NOT TESTED | Low |
| Interaction of status + capability filters | Partial | Medium |

### 4.2 Recommended Tests Before Refactoring

1. **Test: Empty filter_state defaults to show-all**
   ```python
   def test_filter_empty_filter_state_shows_all():
       ships = [make_mock_ship(is_damaged=True), make_mock_ship()]
       result = filter_ships(ships, {})
       assert len(result) == 2
   ```

2. **Test: Both sides of binary filter False shows nothing**
   ```python
   def test_filter_both_warp_filters_false():
       ships = [make_mock_ship(warp_tonnage=1500), make_mock_ship()]
       filter_state = {'show_warp_capable': False, 'show_not_warp_capable': False, ...}
       result = filter_ships(ships, filter_state)
       assert len(result) == 0  # Nothing passes
   ```

3. **Test: Capability filter combined with status filter**
   ```python
   def test_filter_warp_and_damaged_combined():
       ships = [
           make_mock_ship(is_damaged=True, warp_tonnage=1500),
           make_mock_ship(is_damaged=False, warp_tonnage=1500),
       ]
       filter_state = {'show_damaged': False, 'show_warp_capable': True, ...}
       result = filter_ships(ships, filter_state)
       # Only undamaged warp-capable ship passes
   ```

4. **Test: Multiple special capability filters**
   ```python
   def test_filter_multiple_special_capabilities():
       # Ensure ships can be filtered by multiple abilities simultaneously
   ```

---

## 5. Refactorability Assessment

### Assessment: **REFACTORABLE**

### Rationale

**Pros:**
1. **Good test coverage:** 19 test methods specifically for `filter_ships` covering core paths
2. **Clear separation of concerns:** Each filter type is already in its own code block
3. **No external side effects:** Pure function that only reads ship state
4. **Predictable structure:** Each filter follows same pattern (check, skip, continue)

**Cons:**
1. **High cyclomatic complexity (36)** comes from independent filter checks, not tangled logic
2. **Some missing edge case tests** (see Section 4)

### Recommended Refactoring Approach

1. **Extract filter predicates:** Create small helper functions for each filter type
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filter(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`

2. **Preserve optimization:** Keep the "both-true = skip check" optimization in each helper

3. **Main function becomes:**
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

4. **Expected complexity reduction:** From 36 to approximately 5-8 per helper + 5-6 main = total ~12-15

### Pre-Refactoring Checklist
- [ ] Add test for empty filter_state
- [ ] Add test for both-false binary filters
- [ ] Add test for combined capability + status filters
- [ ] Run full test suite to establish baseline

---

## Summary

| Category | Status |
|----------|--------|
| Edge cases documented | Yes |
| Invariants identified | Yes |
| Risk areas flagged | Yes |
| Missing tests identified | Yes |
| **Refactorability** | **REFACTORABLE** |

The function is a good candidate for refactoring via helper extraction. The complexity is additive (independent filter checks) rather than multiplicative (nested conditionals), making it straightforward to decompose. Recommend adding 3-4 additional tests before proceeding with refactoring.
