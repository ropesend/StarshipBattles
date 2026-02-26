# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Function Signature:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Branches/Conditions Contributing Most to Complexity

### High-Complexity Contributors

| Location | Condition | Nesting Level | Complexity Impact |
|----------|-----------|---------------|-------------------|
| L148-153 | Warp capability filter | 2 levels | Medium - dual boolean check with capability lookup |
| L158-164 | Spaceyard filter | 2 levels | Medium - same pattern as warp |
| L169-174 | Cargo filter | 2 levels | Medium - same pattern with computation |
| L176-194 | Special capability loop | 3 levels | **HIGH** - loop with nested conditionals and early break |
| L196-220 | Status filters (destroyed/derelict/damaged/undamaged) | 2 levels | Medium - 4 sequential filter blocks |

### The Most Complex Section: Special Capability Loop (L176-194)

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

This is the highest complexity contributor because:
1. Uses a loop to iterate over multiple capabilities
2. Has 3 levels of nesting (loop > if > if)
3. Uses a flag variable (`_skip`) to communicate across scope boundaries
4. Contains a repeated import inside the conditional

---

## 2. Nested Conditionals That Could Be Flattened

### Pattern A: Binary Capability Filter (repeated 4 times)

Current structure (L148-153 as example):
```python
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Flattening opportunity:** The outer `if not show_warp or not show_not_warp` is an optimization guard. The inner logic can be expressed as a single condition.

### Pattern B: Status Filter Chain (L196-220)

Current structure:
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
# ... and so on
```

**Flattening opportunity:** These could be unified using a status categorization followed by a single filter check.

---

## 3. Early Returns That Could Simplify Logic

### Current Early-Exit Pattern

The function uses `continue` for early exits within the loop, which is appropriate for filtering. However, there are opportunities:

### Missing Early Return: Empty Filter State

If all filters are set to `True` (show everything), the entire function could short-circuit:
```python
if all(filter_state.get(key, True) for key in KNOWN_FILTER_KEYS):
    return list(ships)  # No filtering needed
```

### Consolidation Opportunity: Status Filter Block

Lines 196-220 could use early return pattern more effectively:
```python
# Instead of 4 separate blocks with appends
status = _categorize_ship_status(ship)
if not filter_state.get(f'show_{status}', True):
    continue
result.append(ship)
```

---

## 4. Repeated Patterns That Could Be Extracted

### Pattern 1: Binary Capability Filter (appears 4 times)

**Locations:** L144-153, L156-164, L167-174, L184-192

**Current pattern:**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue  # or _skip = True; break
    if not has_capability and not show_not:
        continue  # or _skip = True; break
```

**Extraction candidate:**
```python
def _passes_binary_filter(
    has_capability: bool,
    show_has: bool,
    show_not_has: bool
) -> bool:
    """Return True if ship passes this binary filter."""
    if show_has and show_not_has:
        return True  # No filtering
    if has_capability:
        return show_has
    return show_not_has
```

### Pattern 2: Late Import Inside Loop

**Locations:** L159, L185, L269, L279

The `FleetCapabilityCalculator` import appears twice inside the loop body:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Extraction:** Move to module-level or use lazy import once at function start.

### Pattern 3: Filter Key Derivation

**Location:** L181-183
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation to derive filter keys is error-prone and could be pre-computed.

---

## 5. Data Transformations That Could Be Separated

### Transformation 1: Ship Status Categorization

**Current:** Status is determined inline through a chain of `if` statements (L196-220)

**Separation opportunity:**
```python
def _get_ship_status_category(ship: ShipInstance) -> str:
    """Return the status category for filtering purposes."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### Transformation 2: Capability Checks

**Current:** Capability checks are performed inline with late imports

**Separation opportunity:**
```python
def _get_ship_capabilities(ship: ShipInstance) -> Dict[str, bool]:
    """Pre-compute all capability flags for a ship."""
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

    caps = {
        'warp_capable': ShipStatsCalculator.has_warp_capability(ship),
        'has_spaceyard': FleetCapabilityCalculator.ship_has_spaceyard(ship),
        'has_cargo': bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0,
    }
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        caps[col_id] = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
    return caps
```

### Transformation 3: Filter State Normalization

**Current:** Filter state is accessed with `.get(key, True)` repeatedly

**Separation opportunity:**
```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Fill in defaults for all known filter keys."""
    defaults = {
        'show_damaged': True,
        'show_undamaged': True,
        'show_derelict': True,
        'show_destroyed': True,
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        # ... etc
    }
    return {**defaults, **filter_state}
```

---

## Summary of Refactoring Opportunities

| Priority | Opportunity | Complexity Reduction | Lines Affected |
|----------|-------------|---------------------|----------------|
| **High** | Extract binary capability filter helper | Reduces nesting, eliminates duplication | ~40 lines |
| **High** | Extract ship status categorization | Simplifies status filter chain | ~25 lines |
| **Medium** | Pre-compute capabilities once per ship | Removes late imports from loop | ~15 lines |
| **Medium** | Normalize filter state at function start | Removes repeated `.get(key, True)` | ~10 lines |
| **Low** | Add early return for "show all" case | Minor optimization | ~3 lines |

### Recommended Refactoring Order

1. Extract `_passes_binary_filter()` helper
2. Extract `_get_ship_status_category()` helper
3. Consolidate late imports to function start
4. Apply helpers to each filter block
5. Consider predicate-based filter composition for extensibility
