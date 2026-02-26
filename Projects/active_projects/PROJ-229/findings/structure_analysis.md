# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222 (99 lines)
**Current Cyclomatic Complexity:** 36 (target: <10)

---

## Executive Summary

The `filter_ships` function exhibits high complexity due to **repeated boolean filter patterns** applied across multiple ship attributes. The function contains 6 distinct filter blocks, each following an identical pattern but with different ship properties. This repetition is the primary driver of complexity.

---

## Control Flow Structure

### Main Loop Structure
```
for ship in ships:
    [warp filter block]      - 4 branches
    [spaceyard filter block] - 4 branches
    [cargo filter block]     - 4 branches
    [special caps loop]      - nested loop with 4 branches per capability (5 capabilities)
    [destroyed filter]       - 2 branches
    [derelict filter]        - 2 branches
    [damaged filter]         - 2 branches
    [undamaged filter]       - 2 branches
```

### Complexity Breakdown by Section

| Section | Lines | Branches | Notes |
|---------|-------|----------|-------|
| Warp capability filter | 144-153 | 4 | Boolean pair pattern |
| Spaceyard filter | 156-164 | 4 | Boolean pair pattern |
| Cargo filter | 167-174 | 4 | Boolean pair pattern |
| Special capability loop | 177-194 | ~20 | Loop over 5 capabilities, 4 branches each |
| Status filters (destroyed/derelict/damaged/undamaged) | 196-220 | 8 | Cascading if-continue pattern |

---

## Findings

### 1. Repeated Boolean Pair Filter Pattern (HIGH IMPACT)

**Lines affected:** 144-174, 177-194

The same pattern appears 6+ times:
```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_X = <check ship property>
    if has_X and not show_X:
        continue
    if not has_X and not show_not_X:
        continue
```

**Problem:** Each instance adds 4 branches to complexity. This pattern handles the boolean pair (show/hide) for each attribute.

**Opportunity:** Extract a generic filter helper that handles boolean pair logic:
```python
def _apply_boolean_filter(has_attribute: bool, show_has: bool, show_not: bool) -> bool:
    """Returns True if ship should be included, False to exclude."""
    if show_has and show_not:
        return True  # No filtering needed
    if has_attribute and not show_has:
        return False
    if not has_attribute and not show_not:
        return False
    return True
```

### 2. Nested Loop for Special Capabilities (HIGH IMPACT)

**Lines:** 177-194

```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
        # ... 4 more branches
        if has_ability and not show_has:
            _skip = True
            break
        if not has_ability and not show_not:
            _skip = True
            break
if _skip:
    continue
```

**Problems:**
1. Nested loop inside main ship loop
2. Uses mutable `_skip` flag instead of early return
3. Late import inside loop (inefficient)
4. Complex key derivation logic (`col_id.replace('can_', 'no_', 1)`)

**Opportunity:** Extract to a dedicated function that returns a boolean:
```python
def _passes_special_capability_filters(ship, filter_state) -> bool:
    ...
```

### 3. Cascading Status Filters (MEDIUM IMPACT)

**Lines:** 196-220

```python
# Destroyed filter
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

# Derelict filter
if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue
# ... etc
```

**Problems:**
1. Multiple exit points per status category
2. Status determination logic interleaved with filter logic
3. Each block has nested conditionals

**Opportunity:** Separate status determination from filtering:
```python
def _get_ship_status(ship) -> str:
    """Returns 'destroyed', 'derelict', 'damaged', or 'undamaged'."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

# Then filtering becomes:
status = _get_ship_status(ship)
if not filter_state.get(f'show_{status}', True):
    continue
```

### 4. Late Imports Inside Loops (MINOR IMPACT)

**Lines:** 159, 185

```python
if not show_has_yard or not show_no_yard:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    ...
```

**Problem:** Import statement executes on each loop iteration when filter is active.

**Opportunity:** Move imports to module level or hoist outside loop.

### 5. Result Building Pattern

**Lines:** 141, 200, 207, 214, 220

The function builds results with `result.append()` scattered across multiple locations.

**Opportunity:** Use filter predicate pattern:
```python
def _should_include_ship(ship, filter_state) -> bool:
    ...

return [ship for ship in ships if _should_include_ship(ship, filter_state)]
```

---

## Recommended Refactoring Approach

### Phase 1: Extract Boolean Filter Helper
Extract the repeated boolean pair pattern into a reusable function. This alone would reduce ~20 branches.

### Phase 2: Extract Status Determination
Separate ship status classification from filtering logic.

### Phase 3: Extract Special Capability Filter
Move the loop over SPECIAL_CAPABILITY_COLUMNS into a dedicated function.

### Phase 4: Consolidate into Predicate Pattern
Refactor main function to use a single `_should_include_ship()` predicate.

### Estimated Complexity After Refactoring

| Refactoring | Complexity Reduction |
|-------------|---------------------|
| Boolean filter helper | -16 branches |
| Status extraction | -6 branches |
| Special capability extraction | -8 branches (moved to helper) |
| **Expected final CC** | **~8-10** |

---

## Code Smells Identified

1. **Feature Envy:** Function reaches into `filter_state` dict repeatedly with complex key derivation
2. **Long Method:** 99 lines with 7+ responsibilities
3. **Duplicate Code:** Same 4-line pattern repeated 6+ times
4. **Primitive Obsession:** Complex filter state represented as raw dict with magic string keys
5. **Control Flag:** `_skip` variable used instead of extracting to function with early return

---

## Positive Patterns Already Present

1. Early returns with `continue` prevent deep nesting
2. Comments document the priority order (derelict before damaged)
3. Default values provided for all filter keys (`True`)
4. Clear separation between capability filters and status filters
