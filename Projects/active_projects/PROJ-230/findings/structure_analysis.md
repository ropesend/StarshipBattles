# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Cyclomatic Complexity:** High (multiple branching paths)

---

## Overview

The `filter_ships` function iterates through ships and applies multiple boolean filter pairs (show_X / show_not_X pattern). Each filter pair checks whether a ship has a capability and excludes it based on the filter state.

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Repeated Boolean Filter Pair Pattern (High Impact)

The function has **5 distinct filter pair blocks**, each following the same pattern:

1. **Warp capability filter** (lines 144-153) - 4 branches
2. **Spaceyard capability filter** (lines 156-164) - 4 branches
3. **Cargo filter** (lines 167-174) - 4 branches
4. **Special capability loop** (lines 177-194) - Loop with 4 branches per iteration
5. **Status cascade** (lines 196-220) - 8 branches (destroyed/derelict/damaged/undamaged)

Each filter pair contributes approximately 4 decision points:
- Check if filtering is active (`not show_X or not show_not_X`)
- Compute the capability boolean
- Check `has_capability and not show_X`
- Check `not has_capability and not show_not_X`

### 1.2 Status Cascade (Lines 196-220) - Most Complex Single Block

The status filtering uses a priority-based cascade:
```python
if not ship.is_alive:           # destroyed
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

if ship.is_derelict:            # derelict
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue

if ship.is_damaged():           # damaged
    if not filter_state.get('show_damaged', True):
        continue
    result.append(ship)
    continue

# undamaged falls through
```

This contributes **8 branches** (4 states x 2 paths each).

### 1.3 Special Capability Loop (Lines 177-194) - Dynamic Complexity

```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
        # ... check and potentially break
```

This loop multiplies complexity by the number of special capabilities.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Filter-then-Check Pattern (All Filter Blocks)

Current pattern (repeated 5 times):
```python
if not show_X or not show_not_X:
    has_capability = compute_capability(ship)
    if has_capability and not show_X:
        continue
    if not has_capability and not show_not_X:
        continue
```

This creates 2 levels of nesting. Could be flattened to a single predicate function.

### 2.2 Status Cascade Nesting

The status checks have implicit nesting through early returns:
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

The `if` inside `if` could be combined with a single predicate.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 No Early Return for Empty Ships List

The function processes an empty list without short-circuiting:
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:  # Loops zero times if empty
        ...
    return result
```

While functionally correct, an explicit early return documents intent:
```python
if not ships:
    return []
```

### 3.2 No Early Return for "Show All" State

When all filters are True (show everything), the function still evaluates every condition. A check for the "show all" case could skip all logic:
```python
if all(filter_state.values()):
    return list(ships)
```

### 3.3 Status Cascade Uses Continue-After-Append

Lines 200-201, 207-208, 214-215:
```python
result.append(ship)
continue
```

This pattern means "ship passes, move to next" but requires mental parsing. An alternative would be to use a `should_include` boolean and a single append point.

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Boolean Filter Pair Pattern (5 Occurrences)

Every capability filter follows this exact pattern:
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

This could be extracted to a helper:
```python
def _passes_boolean_filter(
    ship,
    filter_state,
    show_key: str,
    show_not_key: str,
    capability_fn: Callable
) -> bool:
    ...
```

### 4.2 Repeated Import Pattern (Lines 159, 185, and implicitly throughout)

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

This import appears twice inside conditional blocks. Moving it to module level or a single lazy-load would clean this up.

### 4.3 Filter Key Derivation (Lines 181-183)

```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation for key derivation is repeated logic that could be in a shared helper or constant mapping.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter State Normalization

The function reads filter_state with `.get(key, True)` defaults throughout. A preprocessing step could normalize the filter state:
```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Ensure all filter keys have explicit boolean values."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        ...
    }
    return {**defaults, **filter_state}
```

### 5.2 Ship Status Classification

Lines 196-220 determine ship status (destroyed/derelict/damaged/undamaged). This classification logic could be extracted:
```python
def _classify_ship_status(ship) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### 5.3 Capability Detection as Separate Layer

All capability checks could be pre-computed into a ship capabilities dict:
```python
def _get_ship_capabilities(ship) -> Dict[str, bool]:
    return {
        'warp_capable': ShipStatsCalculator.has_warp_capability(ship),
        'has_spaceyard': FleetCapabilityCalculator.ship_has_spaceyard(ship),
        'has_cargo': bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0,
        'status': _classify_ship_status(ship),
        # ... special capabilities
    }
```

Then filtering becomes a simple predicate match against the capabilities dict.

---

## 6. Recommended Refactoring Strategy

### Priority 1: Extract Boolean Filter Helper
Create `_passes_filter(filter_state, show_key, show_not_key, has_capability) -> bool`

### Priority 2: Separate Capability Detection
Create `_compute_ship_capabilities(ship) -> Dict[str, Any]`

### Priority 3: Unify Status Handling
Replace the status cascade with status classification + single filter check

### Priority 4: Extract Filter Configuration
Define filter definitions as data (list of FilterSpec objects) rather than procedural code

---

## Complexity Metrics Summary

| Component | Branches | Notes |
|-----------|----------|-------|
| Warp filter | 4 | Could be 1 with helper |
| Spaceyard filter | 4 | Could be 1 with helper |
| Cargo filter | 4 | Could be 1 with helper |
| Special capabilities loop | 4 x N | N = number of special capabilities |
| Status cascade | 8 | Could be 2 with classification |
| **Total (approx)** | **24+ branches** | Target: <10 |
