# Structure Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Function:** `filter_ships(ships, filter_state) -> List[ShipInstance]`

---

## Overview

The `filter_ships` function applies multiple filter criteria to a list of ships based on a `filter_state` dictionary. It iterates through all ships once, applying various filters with `continue` statements to skip ships that don't pass.

**Current Complexity Drivers:**
- 98 lines of code
- 6 distinct filter categories
- Multiple nested conditionals
- Repeated filter patterns
- Import statements inside the loop

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Special Capability Filter Loop (Lines 176-194) - HIGHEST COMPLEXITY

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

**Issues:**
- Nested loop inside main loop (O(n * m) complexity pattern)
- String manipulation (`col_id.replace('can_', 'no_', 1)`) to derive filter keys
- Import inside innermost scope (repeated per ship, per capability)
- `_skip` flag pattern instead of clean control flow
- Four levels of nesting

### 1.2 Status Classification Chain (Lines 196-220) - MODERATE COMPLEXITY

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

if ship.is_damaged():
    if not filter_state.get('show_damaged', True):
        continue
    result.append(ship)
    continue

if not filter_state.get('show_undamaged', True):
    continue
result.append(ship)
```

**Issues:**
- Repeated pattern: check status -> check filter -> maybe continue -> append -> continue
- Each status requires 4-5 lines of boilerplate
- Mutually exclusive states handled with cascading if-continue pattern
- `result.append(ship)` repeated 4 times

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Boolean Capability Filters (Pattern repeats 4 times)

**Current Pattern (Lines 144-153, 156-164, 167-174):**
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

**Nesting Depth:** 3 levels (main loop -> outer if -> inner if)

**Flattening Opportunity:** This pattern can be expressed as a single predicate:
```python
# Pseudocode for flattened logic
if not passes_boolean_filter(ship, 'warp', show_warp, show_not_warp):
    continue
```

### 2.2 Status Cascade (Lines 196-220)

The status filtering uses nested if statements where the state space is actually a simple enum-like categorization:
- DESTROYED (not is_alive)
- DERELICT (is_alive and is_derelict)
- DAMAGED (is_alive and not is_derelict and is_damaged())
- UNDAMAGED (everything else)

**Flattening Opportunity:** Compute status once, then lookup in filter_state.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Filter State Optimization Check

The function could exit early if all filters are enabled (nothing to filter):

```python
# Potential early return
if all(filter_state.get(key, True) for key in ALL_FILTER_KEYS):
    return list(ships)  # No filtering needed
```

### 3.2 Empty Input Check

Already handled implicitly (empty list returns empty), but explicit check would clarify intent.

### 3.3 Convert to Filter Function with Early Return

Instead of building `result` list, use a predicate function:
```python
def ship_passes_filters(ship, filter_state) -> bool:
    if not _passes_warp_filter(ship, filter_state):
        return False
    if not _passes_spaceyard_filter(ship, filter_state):
        return False
    # ... etc
    return True

return [ship for ship in ships if ship_passes_filters(ship, filter_state)]
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Boolean Capability Filter Pattern (Repeated 4 times)

**Locations:**
- Lines 144-153: Warp capability
- Lines 156-164: Spaceyard capability
- Lines 167-174: Cargo filter
- Lines 176-194: Special capabilities (in loop)

**Common Pattern:**
```python
show_has = filter_state.get('show_has_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_capability = <capability_check>(ship)
    if has_capability and not show_has:
        <skip>
    if not has_capability and not show_not:
        <skip>
```

**Extraction Opportunity:**
```python
def _passes_boolean_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Check if ship passes a binary (has/doesn't have) filter."""
    if show_has and show_not:
        return True  # No filtering
    if has_capability:
        return show_has
    return show_not
```

### 4.2 Filter Key Derivation Pattern

The special capability loop derives filter keys from column IDs:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

**Extraction Opportunity:** Pre-compute filter key mappings or use a consistent naming convention.

### 4.3 Import Statement Duplication

`FleetCapabilityCalculator` is imported twice in the function:
- Line 159 (spaceyard filter)
- Line 185 (special capabilities)

**Extraction Opportunity:** Move import to function scope or module level.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Ship Status Classification

**Current:** Status checked inline with multiple `if` statements
**Proposed:** Extract to pure function

```python
def get_ship_status_category(ship: ShipInstance) -> str:
    """Return status category: 'destroyed', 'derelict', 'damaged', 'undamaged'."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### 5.2 Capability Checks

**Current:** Capability checks mixed with filter logic
**Proposed:** Separate capability computation from filtering

```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]  # ability_name -> has_it
    status: str  # 'destroyed', 'derelict', 'damaged', 'undamaged'

def compute_ship_capabilities(ship: ShipInstance) -> ShipCapabilities:
    """Compute all filterable capabilities for a ship."""
    ...

def ship_passes_filter(caps: ShipCapabilities, filter_state: Dict) -> bool:
    """Pure function: check if capabilities pass filter state."""
    ...
```

### 5.3 Filter State Normalization

**Current:** Filter state accessed via `.get()` with `True` default throughout
**Proposed:** Normalize filter state once at function entry

```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Fill in default True values for all filter keys."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        # ... all keys
    }
    return {**defaults, **filter_state}
```

---

## Recommended Refactoring Strategy

### Priority 1: Extract Boolean Filter Predicate
Create `_passes_boolean_filter(has_capability, show_has, show_not) -> bool` to replace the repeated 6-line pattern with a 1-line call.

### Priority 2: Extract Status Determination
Create `_get_status_filter_key(ship) -> str` to map ship state to filter key, eliminating the cascading if-continue pattern.

### Priority 3: Flatten Special Capabilities Loop
Pre-compute capability check functions or use a filter specification table to eliminate the nested loop with string manipulation.

### Priority 4: Consolidate Imports
Move `FleetCapabilityCalculator` import to function scope (not inside conditionals).

### Priority 5: Consider List Comprehension with Predicate
Refactor to `[ship for ship in ships if _passes_all_filters(ship, filter_state)]` pattern for cleaner main structure.

---

## Complexity Impact Estimates

| Refactoring | Lines Removed | Nesting Reduced | Cognitive Load |
|-------------|---------------|-----------------|----------------|
| Extract boolean filter | ~20 lines | -1 level | High reduction |
| Extract status logic | ~15 lines | -1 level | Medium reduction |
| Flatten special caps | ~10 lines | -2 levels | High reduction |
| Consolidate imports | ~2 lines | 0 | Low reduction |

**Total Estimated Reduction:** 40-50% of function body, 2-3 nesting levels
