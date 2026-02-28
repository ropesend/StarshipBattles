# Correctness Review: filter_ships Refactoring

**Date:** 2026-02-27
**Reviewer:** Claude Opus 4.5
**Target Function:** `filter_ships` in `game/ui/screens/fleet_report_filters.py`
**Complexity Reduction:** 36 -> 7

---

## Summary

**VERDICT: CORRECT**

The refactoring correctly extracts filter logic into five helper functions while preserving all original behavior. Each helper function returns a boolean indicating whether the ship should be excluded, which is the exact inverse of the original inline continue/append logic. All edge cases, error paths, and return values are preserved.

---

## Extracted Helper Functions Analysis

### 1. `_should_exclude_by_warp(ship, filter_state) -> bool`

**Original Code:**
```python
show_warp = filter_state.get('show_warp_capable', True)
show_not_warp = filter_state.get('show_not_warp_capable', True)

if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Refactored Code:**
```python
show_warp = filter_state.get('show_warp_capable', True)
show_not_warp = filter_state.get('show_not_warp_capable', True)

if show_warp and show_not_warp:
    return False

is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
if is_warp_capable and not show_warp:
    return True
if not is_warp_capable and not show_not_warp:
    return True
return False
```

**Analysis:** CORRECT
- Early return optimization changed from `if not A or not B` to `if A and B: return False`, which is logically equivalent but slightly cleaner.
- The original checks `has_warp_capability` only when needed; refactored version does the same via early return.
- Both versions default filter keys to `True`.
- Return values: `True` = exclude (was `continue`), `False` = include.

---

### 2. `_should_exclude_by_spaceyard(ship, filter_state) -> bool`

**Original Code:**
```python
show_has_yard = filter_state.get('show_has_spaceyard', True)
show_no_yard = filter_state.get('show_no_spaceyard', True)
if not show_has_yard or not show_no_yard:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    if has_yard and not show_has_yard:
        continue
    if not has_yard and not show_no_yard:
        continue
```

**Refactored Code:**
```python
show_has_yard = filter_state.get('show_has_spaceyard', True)
show_no_yard = filter_state.get('show_no_spaceyard', True)

if show_has_yard and show_no_yard:
    return False

# INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
if has_yard and not show_has_yard:
    return True
if not has_yard and not show_no_yard:
    return True
return False
```

**Analysis:** CORRECT
- Late import preserved inside the function (after early return check, as in original).
- Logic is identical: only imports and checks when at least one filter is off.
- Comment added to document intentional late import.

---

### 3. `_should_exclude_by_cargo(ship, filter_state) -> bool`

**Original Code:**
```python
show_has_cargo = filter_state.get('show_has_cargo', True)
show_no_cargo = filter_state.get('show_no_cargo', True)
if not show_has_cargo or not show_no_cargo:
    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    if has_cargo and not show_has_cargo:
        continue
    if not has_cargo and not show_no_cargo:
        continue
```

**Refactored Code:**
```python
show_has_cargo = filter_state.get('show_has_cargo', True)
show_no_cargo = filter_state.get('show_no_cargo', True)

if show_has_cargo and show_no_cargo:
    return False

has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
if has_cargo and not show_has_cargo:
    return True
if not has_cargo and not show_no_cargo:
    return True
return False
```

**Analysis:** CORRECT
- Cargo check logic preserved exactly: `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`
- This handles the edge case where `cargo_contents` might be `None` or empty dict.

---

### 4. `_should_exclude_by_special_capabilities(ship, filter_state) -> bool`

**Original Code:**
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if has_ability and not show_has:
            _skip = True
            break
        if not has_ability and not show_not:
            _skip = True
            break
if _skip:
    continue
```

**Refactored Code:**
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)

    if not show_has or not show_not:
        # INTENTIONAL LATE IMPORT: Avoid circular import with strategy data
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if has_ability and not show_has:
            return True
        if not has_ability and not show_not:
            return True
return False
```

**Analysis:** CORRECT
- Loop continues until exclusion found or all columns checked.
- Original used `_skip` flag with `break`; refactored uses direct `return True`.
- **Special capability key derivation preserved exactly:** `col_id.replace('can_', 'no_', 1)`
  - This transforms `'can_destroy_planet'` to `'no_destroy_planet'`
  - The `1` parameter ensures only the first occurrence is replaced.
- Late import preserved inside conditional block.
- Import comment added for documentation.

---

### 5. `_should_exclude_by_status(ship, filter_state) -> bool`

**Original Code:**
```python
# Destroyed filter
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

# Derelict filter (checked before damaged since derelict implies damaged)
if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue

# Damaged filter
if ship.is_damaged():
    if not filter_state.get('show_damaged', True):
        continue
    result.append(ship)
    continue

# Undamaged (healthy) ships
if not filter_state.get('show_undamaged', True):
    continue
result.append(ship)
```

**Refactored Code:**
```python
"""
CRITICAL: Order matters. Check destroyed -> derelict -> damaged -> undamaged.
A derelict ship is also damaged, so derelict must be checked first.
"""
# Destroyed ships
if not ship.is_alive:
    return not filter_state.get('show_destroyed', True)

# Derelict ships (checked before damaged since derelict implies damaged)
if ship.is_derelict:
    return not filter_state.get('show_derelict', True)

# Damaged ships
if ship.is_damaged():
    return not filter_state.get('show_damaged', True)

# Undamaged (healthy) ships
return not filter_state.get('show_undamaged', True)
```

**Analysis:** CORRECT
- **Status filter ordering VERIFIED:** destroyed -> derelict -> damaged -> undamaged
- Docstring explicitly documents the critical ordering requirement.
- Original had append-then-continue pattern; refactored uses return-boolean pattern.
- Each status check returns the inverse of the filter value (exclude if filter is False).
- Comments document the "derelict implies damaged" ordering requirement.

---

## Critical Checks

### 1. Status Filter Ordering (CRITICAL)

**VERIFIED CORRECT**

The order is:
1. `if not ship.is_alive:` (destroyed)
2. `if ship.is_derelict:` (derelict)
3. `if ship.is_damaged():` (damaged)
4. Default case (undamaged)

This order is critical because:
- A destroyed ship must be handled first (not alive = destroyed)
- A derelict ship is also damaged, so checking derelict before damaged prevents derelict ships from being incorrectly classified as just "damaged"

### 2. Late Imports Preserved (CRITICAL)

**VERIFIED CORRECT**

All three functions that use `FleetCapabilityCalculator` have the import inside the function:
- `_should_exclude_by_spaceyard`: Line 151
- `_should_exclude_by_special_capabilities`: Line 188

The original code had the import inside the conditional block; the refactored code preserves this pattern with the import placed after the early return but before usage.

### 3. Special Capability Key Derivation (CRITICAL)

**VERIFIED CORRECT**

The key derivation `col_id.replace('can_', 'no_', 1)` is preserved exactly on line 183.

Example transformations:
- `'can_destroy_planet'` -> `'no_destroy_planet'`
- `'can_colonize'` -> `'no_colonize'`

The `1` parameter ensures only the first `'can_'` is replaced, which handles edge cases where a column ID might contain multiple `'can_'` substrings (though unlikely in practice).

---

## Edge Cases Analysis

| Edge Case | Original Behavior | Refactored Behavior | Status |
|-----------|------------------|---------------------|--------|
| Empty ship list | Returns empty list | Returns empty list | SAME |
| All filters True (default) | All ships included | All ships included | SAME |
| All filters False | Empty list | Empty list | SAME |
| Ship is both derelict and damaged | Handled by derelict filter | Handled by derelict filter | SAME |
| `cargo_contents` is None | `bool(None)` = False, no error | Same logic | SAME |
| `cargo_contents` is empty dict | `bool({})` = False | Same logic | SAME |
| Missing filter keys | Defaults to True | Defaults to True | SAME |

---

## Behavioral Differences Detected

**NONE**

The refactoring is a pure structural change. All logical paths produce identical results.

---

## Minor Observations (Non-Issues)

1. **Early return pattern change:** Original used `if not A or not B` condition to decide whether to check; refactored uses `if A and B: return False` for early exit. These are logically equivalent but the refactored version is slightly more readable.

2. **Comment additions:** The refactored code adds documentation comments explaining the late imports and critical ordering. This is an improvement, not a behavioral change.

3. **Docstrings added:** All helper functions have docstrings explaining their purpose. This is an improvement.

---

## Final Verdict

### CORRECT

The refactoring correctly preserves all original behavior while reducing cyclomatic complexity from 36 to 7. Each extracted helper function:
- Handles the same edge cases
- Uses the same default values
- Returns equivalent results
- Preserves critical ordering (status filters)
- Preserves late imports (FleetCapabilityCalculator)
- Preserves special key derivation logic

No behavioral changes or regressions were detected.
