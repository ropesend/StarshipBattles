# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Complexity:** High (nested conditionals, repeated patterns, mixed concerns)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 5 Times)
The function applies the same binary filter pattern for multiple capabilities:

| Filter Pair | Lines | Pattern |
|------------|-------|---------|
| Warp capable | 144-153 | show_X / show_not_X |
| Spaceyard | 156-164 | show_has_X / show_no_X |
| Cargo | 167-174 | show_has_X / show_no_X |
| Special capabilities | 176-194 | show_X / show_no_X (loop) |
| Status filters | 196-220 | show_destroyed/derelict/damaged/undamaged |

Each instance follows the same structure:
```python
show_positive = filter_state.get('show_X', True)
show_negative = filter_state.get('show_not_X', True)
if not show_positive or not show_negative:
    has_property = check_property(ship)
    if has_property and not show_positive:
        continue
    if not has_property and not show_negative:
        continue
```

### 1.2 Status Filter Cascade (Lines 196-220)
The status filtering uses a cascading if-else pattern with early returns that is hard to follow:
- Destroyed check (197-201)
- Derelict check (204-208)
- Damaged check (211-215)
- Undamaged fallthrough (217-220)

Each branch has similar structure: check condition, optionally skip, append and continue.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Double-Nested Filter Checks (Multiple Locations)
```python
# Lines 148-153 - Warp filter
if not show_warp or not show_not_warp:           # Outer: "are filters active?"
    is_warp_capable = ...
    if is_warp_capable and not show_warp:        # Inner: "should skip?"
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

This pattern repeats for spaceyard (158-164) and cargo (169-174).

**Flattening opportunity:** Extract to a predicate function that returns `True` if ship passes, `False` if it should be filtered out.

### 2.2 Special Capabilities Loop with Nested Checks (Lines 176-194)
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(...)
    show_not = filter_state.get(...)
    if not show_has or not show_not:             # Outer
        has_ability = ...
        if has_ability and not show_has:         # Inner
            _skip = True
            break
        if not has_ability and not show_not:     # Inner
            _skip = True
            break
if _skip:
    continue
```

**Issue:** Uses mutable `_skip` flag and breaks out of loop, then checks flag outside.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Current Pattern: `continue` Within Main Loop
The function uses `continue` statements to skip ships that don't match filters. However, the logic mixes:
- Filter evaluation
- Skip decisions
- Result accumulation

### 3.2 Suggested Simplification: Extract Filter Predicates
Instead of inline `continue` statements, extract each filter as a predicate:

```python
def passes_warp_filter(ship, filter_state) -> bool:
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if show_warp and show_not_warp:
        return True  # No filtering active
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable:
        return show_warp
    return show_not_warp
```

Then the main loop becomes:
```python
for ship in ships:
    if not passes_warp_filter(ship, filter_state):
        continue
    if not passes_spaceyard_filter(ship, filter_state):
        continue
    # ... etc
    result.append(ship)
```

### 3.3 Status Filter Simplification (Lines 196-220)
Current code appends and continues in multiple branches. Could be unified:

```python
# Current (confusing)
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

# Suggested (clearer)
if not passes_status_filter(ship, filter_state):
    continue
result.append(ship)
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
The following pattern appears 4 times (warp, spaceyard, cargo, and inside special capabilities loop):

```python
show_has = filter_state.get('show_has_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_property = compute_property(ship)
    if has_property and not show_has:
        skip
    if not has_property and not show_not:
        skip
```

**Extraction opportunity:**
```python
def _check_binary_filter(
    filter_state: Dict[str, bool],
    show_key: str,
    not_show_key: str,
    has_property: bool
) -> bool:
    """Returns True if ship passes filter, False if it should be skipped."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(not_show_key, True)
    if show_has and show_not:
        return True  # Both enabled, no filtering
    if has_property:
        return show_has
    return show_not
```

### 4.2 Late Import Pattern
The same import appears multiple times:
```python
# Line 159
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
# Line 185
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Extraction opportunity:** Move import to module level or perform once at function start.

### 4.3 Filter Key Derivation (Lines 181-183)
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This key derivation logic could be encapsulated in a helper or made more explicit through a mapping.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Capability Computation vs Filter Application
Currently, capability checks are interleaved with filter decisions:
```python
is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)  # Compute
if is_warp_capable and not show_warp:  # Filter
    continue
```

**Separation opportunity:** Pre-compute ship capabilities once, then apply filters:
```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]
    status: str  # 'destroyed', 'derelict', 'damaged', 'undamaged'

def compute_capabilities(ship: ShipInstance) -> ShipCapabilities:
    ...

def passes_filters(capabilities: ShipCapabilities, filter_state: Dict[str, bool]) -> bool:
    ...
```

### 5.2 Status Determination (Lines 196-220)
The status determination (destroyed/derelict/damaged/undamaged) is implicit in the cascade. Could be explicit:

```python
def get_ship_status(ship: ShipInstance) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

Then filter by status:
```python
status = get_ship_status(ship)
if not filter_state.get(f'show_{status}', True):
    continue
```

### 5.3 Filter State Normalization
The filter state uses inconsistent key patterns:
- `show_warp_capable` / `show_not_warp_capable`
- `show_has_spaceyard` / `show_no_spaceyard`
- `show_has_cargo` / `show_no_cargo`
- `show_can_X` / `show_no_X`
- `show_destroyed`, `show_derelict`, `show_damaged`, `show_undamaged`

**Separation opportunity:** Normalize filter keys into a consistent structure at function entry.

---

## Summary of Refactoring Opportunities

| Priority | Area | Benefit |
|----------|------|---------|
| High | Extract binary filter helper | Eliminates 4 repeated patterns, reduces ~40 lines |
| High | Extract status filter | Simplifies cascade, makes status explicit |
| Medium | Extract capability predicates | Improves testability, single responsibility |
| Medium | Consolidate imports | Minor cleanup, reduces duplication |
| Low | Normalize filter keys | Consistency, but may require caller changes |
| Low | Pre-compute capabilities | Better separation but may over-engineer |

---

## Recommended Refactoring Approach

1. **Phase 1:** Extract `_check_binary_filter()` helper for the repeated pattern
2. **Phase 2:** Extract `_get_ship_status()` and `_passes_status_filter()`
3. **Phase 3:** Extract capability-specific predicates (`passes_warp_filter`, etc.)
4. **Phase 4:** Simplify main loop to just call predicates and append

This would transform the function from ~100 lines with nested conditionals to ~20 lines calling well-named helper functions.
