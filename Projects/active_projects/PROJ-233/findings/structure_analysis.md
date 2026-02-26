# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** High (multiple filter branches)

---

## Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter flags. It processes each ship through multiple filter categories: warp capability, spaceyard capability, cargo, special capabilities (via loop), and ship status (destroyed/derelict/damaged/undamaged).

---

## Control Flow Structure

### Main Loop Pattern
```
for ship in ships:
    [filter check 1] -> continue if filtered out
    [filter check 2] -> continue if filtered out
    ...
    [status checks with append]
    result.append(ship)
```

### Filter Categories (in order)

1. **Warp Capability Filter** (lines 143-153)
2. **Spaceyard Capability Filter** (lines 155-164)
3. **Cargo Filter** (lines 166-174)
4. **Special Capabilities Loop** (lines 176-194)
5. **Ship Status Filters** (lines 196-220)
   - Destroyed
   - Derelict
   - Damaged
   - Undamaged (default)

---

## Complexity Contributors

### 1. Repeated Binary Filter Pattern (HIGH - 4 occurrences)

The same pattern appears for warp, spaceyard, cargo, and special capabilities:

```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_property = check_property(ship)
    if has_property and not show_has:
        continue
    if not has_property and not show_not:
        continue
```

**Analysis:** This 8-line pattern is duplicated 4 times with minor variations. Each instance adds 3-4 branches to cyclomatic complexity.

### 2. Nested Conditionals in Status Section (MEDIUM)

Lines 196-220 have a cascading if-continue-append pattern:

```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue
# ... etc
```

**Analysis:** Each status check is 5 lines with nested conditionals. The pattern could be flattened.

### 3. Special Capabilities Loop with Break (MEDIUM)

Lines 176-194 iterate over `SPECIAL_CAPABILITY_COLUMNS` with an inner break:

```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    # ... check logic
    if has_ability and not show_has:
        _skip = True
        break
    if not has_ability and not show_not:
        _skip = True
        break
if _skip:
    continue
```

**Analysis:** Uses a flag variable (`_skip`) and `break` to exit the inner loop early. This is a workaround for Python's lack of labeled `continue`.

### 4. Late Imports Inside Loop (LOW complexity, HIGH performance concern)

```python
# Line 159 - inside loop!
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
# Line 185 - inside nested loop!
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Analysis:** The same import appears twice within the loop body. While Python caches imports, this adds unnecessary overhead and code noise.

---

## Nested Conditionals That Could Be Flattened

### Status Filter Chain (lines 196-220)

**Current structure:**
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

**Could become:**
```python
if not ship.is_alive:
    passes = filter_state.get('show_destroyed', True)
elif ship.is_derelict:
    passes = filter_state.get('show_derelict', True)
elif ship.is_damaged():
    passes = filter_state.get('show_damaged', True)
else:
    passes = filter_state.get('show_undamaged', True)

if passes:
    result.append(ship)
```

---

## Early Returns That Could Simplify Logic

The function doesn't use early returns, but the structure uses `continue` extensively to skip ships. The pattern is reasonable but could be inverted.

**Current:** Check if ship should be excluded, `continue` if so.
**Alternative:** Collect inclusion criteria, only append if all pass.

---

## Repeated Patterns That Could Be Extracted

### Pattern 1: Binary Capability Filter

Extract into a helper function:

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    show_key: str,
    hide_key: str,
    has_property: bool
) -> bool:
    """Return True if ship passes this binary filter."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(hide_key, True)

    if show_has and show_not:
        return True  # No filtering active

    if has_property:
        return show_has
    return show_not
```

This could consolidate all 4 binary filter checks (warp, spaceyard, cargo, special capabilities).

### Pattern 2: Status Classification

The status determination logic (destroyed > derelict > damaged > undamaged) appears in both `filter_ships` and `sort_ships`. Could extract:

```python
def _get_ship_status_category(ship: ShipInstance) -> str:
    """Return status category: 'destroyed', 'derelict', 'damaged', or 'undamaged'."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

---

## Data Transformations That Could Be Separated

### 1. Filter State Normalization

The function repeatedly accesses `filter_state.get(key, True)`. Could pre-process:

```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Return filter state with all defaults applied."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        'show_has_spaceyard': True,
        'show_no_spaceyard': True,
        # ... etc
    }
    return {**defaults, **filter_state}
```

### 2. Capability Check Pre-computation

For large ship lists, could pre-compute expensive checks:

```python
# Before filtering loop
ship_capabilities = {
    ship: {
        'warp': ShipStatsCalculator.has_warp_capability(ship),
        'spaceyard': FleetCapabilityCalculator.ship_has_spaceyard(ship),
        # ... etc
    }
    for ship in ships
}
```

However, current code already optimizes by only computing capabilities when the filter is active (`if not show_has or not show_not`).

### 3. Filter Predicate Separation

Transform the filter logic from imperative to declarative:

```python
def _build_filter_predicates(filter_state: Dict[str, bool]) -> List[Callable]:
    """Build list of filter predicate functions based on active filters."""
    predicates = []

    if not (filter_state.get('show_warp_capable', True) and
            filter_state.get('show_not_warp_capable', True)):
        predicates.append(_make_warp_filter(filter_state))

    # ... etc

    return predicates

def filter_ships(ships, filter_state):
    predicates = _build_filter_predicates(filter_state)
    return [ship for ship in ships if all(p(ship) for p in predicates)]
```

---

## Summary of Findings

| Issue | Severity | Refactoring Approach |
|-------|----------|---------------------|
| Repeated binary filter pattern (4x) | High | Extract helper function |
| Status filter cascade | Medium | Flatten to single conditional chain |
| Special capabilities loop with flag | Medium | Extract to helper or use `any()`/generator |
| Late imports inside loop | Low | Move to top of function body |
| Status classification duplication | Low | Extract shared helper (also used in sort_ships) |

### Recommended Refactoring Priority

1. **Extract binary filter helper** - Eliminates ~24 lines of duplicated code
2. **Flatten status filter chain** - Reduces nesting and improves readability
3. **Consolidate imports** - Move `FleetCapabilityCalculator` import to function top
4. **Extract status classification** - Shared with `sort_ships`, reduces duplication
