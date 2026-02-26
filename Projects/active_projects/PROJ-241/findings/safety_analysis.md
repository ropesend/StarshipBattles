# Safety Analysis: filter_ships Function Refactoring

## Target Function
- **File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Cyclomatic Complexity:** 36 (grade F)
- **Length:** 99 lines

## Overview

The `filter_ships` function applies multiple independent filters to a list of ships, returning ships that match all enabled filter criteria. It handles:
1. Warp capability filter (show_warp_capable / show_not_warp_capable)
2. Spaceyard capability filter (show_has_spaceyard / show_no_spaceyard)
3. Cargo filter (show_has_cargo / show_no_cargo)
4. Special capability filters (5 abilities: DestroyPlanet, OpenWarpPoint, CloseWarpPoint, DestroyStar, CreateSphereWorld)
5. Status filters (show_destroyed / show_derelict / show_damaged / show_undamaged)

---

## Edge Cases Identified

### 1. Filter State Defaults (via `.get()`)
All filter checks use `.get(key, True)` defaulting to True when a key is missing. This means:
- An empty filter_state dict shows ALL ships (all filters default to "show")
- Partial filter_state dicts gracefully handle missing keys
- **Risk:** If any refactoring removes the default=True, ships would unexpectedly be hidden

### 2. Cargo Detection Edge Case
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
- Empty dict `{}` -> no cargo
- Dict with zero values `{'minerals': 0}` -> no cargo
- Dict with any positive value -> has cargo
- **Test coverage:** Verified in `test_filter_cargo_zero_value_treated_as_no_cargo`

### 3. Status Filter Priority Order
The function uses a specific priority order for mutually exclusive status classification:
1. **Destroyed** (checked first via `not ship.is_alive`)
2. **Derelict** (checked second via `ship.is_derelict`)
3. **Damaged** (checked third via `ship.is_damaged()`)
4. **Undamaged** (default fallthrough)

**Critical Invariant:** A ship is added to results EXACTLY ONCE through exactly ONE path. The `continue` statements after `result.append()` ensure this.

### 4. Early Exit via Continue
Capability filters (warp, spaceyard, cargo, special) all use `continue` to skip ships, but status filters use `continue` after appending. This asymmetry is intentional:
- Capability filters are pure exclusion filters
- Status filters are classification AND exclusion filters

### 5. Special Capability Filter Key Derivation
```python
show_has = filter_state.get(f'show_{col_id}', True)  # e.g., show_can_destroy_planet
no_key = col_id.replace('can_', 'no_', 1)            # e.g., no_destroy_planet
show_not = filter_state.get(f'show_{no_key}', True)  # e.g., show_no_destroy_planet
```
- Key naming convention: `can_X` becomes `no_X` for the negative filter
- **Risk:** If SPECIAL_CAPABILITY_COLUMNS keys don't follow `can_` prefix convention, the derivation breaks

---

## Invariants That Must Be Preserved

### I1. Filter Independence
Each filter category operates independently. A ship must pass ALL enabled filter checks:
- Warp filter AND Spaceyard filter AND Cargo filter AND Special filters AND Status filter
- Order of evaluation does not affect result (though order of checks can affect performance)

### I2. Binary Filter Pairs
Each filter category has two boolean toggles (show X / show not-X):
- Both True = show all ships (filter is effectively disabled)
- Both False = show NO ships for this category
- One True, One False = filter active

### I3. Mutually Exclusive Status
Each ship has exactly ONE status:
- Destroyed (is_alive = False)
- Derelict (is_alive = True, is_derelict = True)
- Damaged (is_alive = True, is_derelict = False, is_damaged() = True)
- Undamaged (is_alive = True, is_derelict = False, is_damaged() = False)

### I4. No Side Effects
The function must not modify:
- The input `ships` list
- Any ship objects
- The `filter_state` dict

### I5. Input Order Preservation
Ships in the result maintain their relative order from the input list (unless explicitly sorted afterward).

---

## Risk Areas for Refactoring

### HIGH RISK

#### R1. Status Filter Cascade Logic
The status filter section (lines 196-220) uses a careful cascade of if/continue patterns:
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue  # CRITICAL: prevents falling through to other status checks

if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue  # CRITICAL: prevents falling through to damaged check
```
**Risk:** Extracting this to a helper function could accidentally:
- Lose the early-return semantics
- Double-add ships
- Skip ships entirely

#### R2. Special Capability Loop with Break
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if has_ability and not show_has:
        _skip = True
        break
    if not has_ability and not show_not:
        _skip = True
        break
if _skip:
    continue
```
**Risk:** This pattern uses a flag + break + continue, which is fragile to refactor. Any helper extraction must handle:
- The short-circuit break behavior
- The outer continue signal

### MEDIUM RISK

#### R3. Late Imports Inside Loop
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    if not show_has or not show_not:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
The late import is inside the loop but only executes conditionally. Moving this could affect:
- Import ordering (circular import risk)
- Performance (though negligible for UI operations)

#### R4. Inconsistent Import Placement
- Warp capability import: outside loop, inside outer for-loop
- Spaceyard import: inside conditional
- FleetCapabilityCalculator for special abilities: inside nested conditional

Consolidating imports could accidentally trigger circular imports.

### LOW RISK

#### R5. Filter State Key Naming
The function relies on specific key naming conventions in filter_state dict. These are defined by `FleetListViewModel.get_filter_state()`. Any refactoring should not change expected key names.

---

## Test Coverage Analysis

### Well-Covered Areas (24+ test cases)

| Test Class | Coverage |
|------------|----------|
| `TestFilterShips` | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | Warp capability filter combinations |
| `TestFilterShipsSpaceyard` | Spaceyard filter combinations |
| `TestFilterShipsCargo` | Cargo filter including zero-value edge case |
| `TestSpecialCapabilityFilter` | Special ability filters (has/lacks ability) |

### Missing Test Coverage (SHOULD ADD BEFORE REFACTORING)

#### M1. Combined Filter Interactions
No tests verify multiple filter categories working together. For example:
- Ship with warp capability but no cargo, with mixed warp/cargo filters
- Derelict ship with special ability, mixed status and capability filters

#### M2. Both Filters Disabled (show all)
While tested implicitly, there's no explicit test for:
```python
filter_state = {'show_warp_capable': True, 'show_not_warp_capable': True, ...}
```
confirming that when BOTH are True, the filter is effectively a no-op.

#### M3. Both Filters Disabled (show none)
No test for:
```python
filter_state = {'show_damaged': False, 'show_undamaged': False,
                'show_derelict': False, 'show_destroyed': False}
```
This edge case should return an empty list.

#### M4. Empty Ships List
No explicit test that `filter_ships([], any_filter_state)` returns `[]`.

#### M5. All Special Capability Filters Together
Tests cover individual special abilities but not all 5 filtering simultaneously.

#### M6. Status Priority Edge Cases
No test explicitly verifies that a destroyed ship is NOT classified as damaged even if `is_damaged()` would return True.

---

## Refactorability Assessment

### VERDICT: REFACTORABLE WITH CAUTION

The function CAN be refactored to reduce complexity, but requires careful attention to the identified risks.

### Recommended Approach

1. **Add Missing Tests First** (items M1-M6)
2. **Extract Capability Filters** - The warp, spaceyard, cargo, and special capability checks can be extracted to helper functions that return `True` (include ship) or `False` (exclude ship).
3. **Keep Status Filter Inline** - The status classification cascade (R1) is the most delicate. Consider keeping it inline or very carefully designing a helper that preserves the mutually-exclusive single-classification invariant.
4. **Use Filter Predicate Pattern** - Consider extracting each filter category to a predicate function:
   ```python
   def _passes_warp_filter(ship, filter_state) -> bool
   def _passes_spaceyard_filter(ship, filter_state) -> bool
   def _passes_cargo_filter(ship, filter_state) -> bool
   def _passes_special_ability_filters(ship, filter_state) -> bool
   def _passes_status_filter(ship, filter_state) -> bool
   ```

### Alternative: Skip and Document

If the refactoring proves too risky after adding tests, the function could be added to a complexity skip list with documentation:
- The complexity stems from the number of independent filter categories
- Each category adds ~6 complexity points (2 booleans + conditions)
- The structure is actually quite regular and readable despite high CC score

---

## Pre-Refactoring Checklist

- [ ] Add test: combined filter interactions (M1)
- [ ] Add test: both-True filter pairs are no-ops (M2)
- [ ] Add test: all-False status filters return empty (M3)
- [ ] Add test: empty ships list input (M4)
- [ ] Add test: multiple special capability filters simultaneously (M5)
- [ ] Add test: destroyed ship is_damaged() edge case (M6)
- [ ] Run full test suite baseline: `pytest tests/ -n 12`
- [ ] Verify no other code depends on specific filter evaluation order

---

## Dependencies

### Direct Callers
- `FleetListViewModel._refresh()` in `fleet_report_view_model.py` (line 215)

### External Dependencies
- `ShipStatsCalculator.has_warp_capability()` - Strategy service
- `FleetCapabilityCalculator.ship_has_spaceyard()` - Strategy data
- `FleetCapabilityCalculator.ship_has_ability()` - Strategy data
- `SPECIAL_CAPABILITY_COLUMNS` - From `fleet_data_source.py`

### Ship Interface Expected
- `ship.is_alive` (bool property)
- `ship.is_derelict` (bool property)
- `ship.is_damaged()` (method returning bool)
- `ship.cargo_contents` (dict or None)

---

## Summary

| Category | Assessment |
|----------|------------|
| **Complexity Source** | Many independent filter categories, each with binary has/lacks pairs |
| **Risk Level** | Medium - status filter cascade is fragile |
| **Test Coverage** | Good for individual categories, weak for interactions |
| **Refactorability** | Yes, with helper extraction pattern |
| **Recommended Action** | Add missing tests, then extract filter predicates |
