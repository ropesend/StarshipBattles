# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** ~36 (estimated from audit data)

---

## 1. Branches/Conditions Contributing Most to Complexity

The function uses a consistent **if/continue pattern** for each filter category. Here is a breakdown of each conditional block and its cyclomatic complexity (CC) contribution:

### Filter Block Breakdown

| Lines | Filter | CC Contribution | Pattern |
|-------|--------|-----------------|---------|
| 144-153 | Warp capability | +4 | outer if + inner if (x2) + continue (x2) |
| 156-164 | Spaceyard capability | +4 | outer if + inner if (x2) + continue (x2) |
| 167-174 | Cargo filter | +4 | outer if + inner if (x2) + continue (x2) |
| 177-194 | Special capabilities loop | +6 | for loop + outer if + inner if (x2) + break (x2) + outer if |
| 197-201 | Destroyed filter | +3 | if + nested if + continue (x2) |
| 204-208 | Derelict filter | +3 | if + nested if + continue (x2) |
| 211-215 | Damaged filter | +3 | if + nested if + continue (x2) |
| 218-220 | Undamaged filter | +2 | if + continue |

**Total estimated CC from conditionals:** ~29 (plus baseline of 1 for function entry and outer loop)

### Highest Complexity Contributors

1. **Special capabilities loop (lines 177-194):** CC +6
   - Iterates over 5 special capabilities (SPECIAL_CAPABILITY_COLUMNS)
   - Each iteration potentially adds conditional branches
   - Uses a `_skip` flag pattern with break statements

2. **Binary filter patterns (warp, spaceyard, cargo):** CC +4 each
   - Same structure repeated 3 times
   - Each has: `if not X or not Y` guard, then two inner `if/continue` checks

3. **Status filters (destroyed, derelict, damaged):** CC +3 each
   - Nested conditionals with dual-path logic (filter out OR append)

---

## 2. Nested Conditionals That Could Be Flattened

### Current Nesting Patterns

**Pattern A: Binary Filter (repeated 3 times)**
```python
# Lines 144-153, 156-164, 167-174
if not show_X or not show_Y:
    value = calculate_value(ship)
    if value and not show_X:
        continue
    if not value and not show_Y:
        continue
```
- Nesting depth: 2 levels
- Could be flattened with early calculation

**Pattern B: Status Filter with Append (repeated 3 times)**
```python
# Lines 197-201, 204-208, 211-215
if ship.some_status:
    if not filter_state.get('show_status', True):
        continue
    result.append(ship)
    continue
```
- Nesting depth: 2 levels
- Mixes filtering logic with result accumulation

**Pattern C: Special Capabilities Loop**
```python
# Lines 177-194
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    if not show_has or not show_not:
        has_ability = calculate(ship)
        if has_ability and not show_has:
            _skip = True
            break
        if not has_ability and not show_not:
            _skip = True
            break
if _skip:
    continue
```
- Nesting depth: 3 levels (for > if > if)
- Uses flag variable to signal outer loop

**Maximum Nesting Depth:** 3 levels (in special capabilities loop)

---

## 3. Early Returns That Could Simplify Logic

The function currently uses a single return at the end. Several opportunities exist for restructuring:

### Opportunity 1: Empty Input Guard
```python
# Could add at start:
if not ships:
    return []
```
This is minor but establishes the early-return pattern.

### Opportunity 2: Extract Filter Predicates
Instead of inline `continue` statements, each filter check could be a predicate function that returns `bool`. The main loop would become:

```python
for ship in ships:
    if passes_all_filters(ship, filter_state):
        result.append(ship)
```

### Opportunity 3: Status Classification Early Return
The status filters (destroyed/derelict/damaged/undamaged) form a mutually exclusive decision tree. This could be an early-return helper:

```python
def should_include_by_status(ship, filter_state) -> bool:
    if not ship.is_alive:
        return filter_state.get('show_destroyed', True)
    if ship.is_derelict:
        return filter_state.get('show_derelict', True)
    if ship.is_damaged():
        return filter_state.get('show_damaged', True)
    return filter_state.get('show_undamaged', True)
```

---

## 4. Repeated Patterns That Could Be Extracted

### Pattern 1: Binary Capability Filter (3 occurrences)

**Locations:** Lines 144-153, 156-164, 167-174

**Common structure:**
```python
show_has = filter_state.get('show_has_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

**Extractable helper:**
```python
def _passes_binary_filter(
    has_value: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Return True if ship passes the binary filter."""
    if show_has and show_not:
        return True  # No filtering needed
    if has_value:
        return show_has
    return show_not
```

### Pattern 2: Status Filter with Immediate Append (3 occurrences)

**Locations:** Lines 197-201, 204-208, 211-215

**Common structure:**
```python
if ship.status_check():
    if not filter_state.get('show_status', True):
        continue
    result.append(ship)
    continue
```

This interleaves filtering with result building. Could be separated.

### Pattern 3: Late Import Pattern (2 occurrences in filter_ships)

**Locations:** Lines 159, 185

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

The same import appears twice within the function. Could be moved to a single conditional import at function start or module level.

---

## 5. Data Transformations That Could Be Separated

### Transformation 1: Filter State Normalization

The function repeatedly calls `filter_state.get(key, True)`. A pre-processing step could normalize the filter state:

```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Fill in defaults for all filter keys."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        'show_has_spaceyard': True,
        'show_no_spaceyard': True,
        # ... etc
    }
    return {**defaults, **filter_state}
```

### Transformation 2: Ship Capability Pre-computation

Several capabilities are computed on-demand within the loop. For large fleets, pre-computing could be beneficial:

```python
@dataclass
class ShipFilterData:
    ship: ShipInstance
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_capabilities: Dict[str, bool]
    status: str  # 'destroyed', 'derelict', 'damaged', 'undamaged'
```

### Transformation 3: Status Classification

The mutually exclusive status logic (lines 197-220) determines ship category. This could be a separate function:

```python
def classify_ship_status(ship: ShipInstance) -> str:
    """Return the filter category for a ship's status."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### Transformation 4: Special Capability Filter Key Derivation

Lines 181-183 derive filter keys from column IDs:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation could be pre-computed into a mapping.

---

## Summary of Refactoring Opportunities

| Category | Opportunity | Complexity Reduction |
|----------|-------------|---------------------|
| Extract Helper | `_passes_binary_filter()` | -6 (removes 3x2 inner ifs) |
| Extract Helper | `_classify_ship_status()` | -6 (simplifies status chain) |
| Extract Helper | `_passes_special_capability_filters()` | -6 (encapsulates loop) |
| Data Transform | Pre-normalize filter_state | -0 (cleaner, not CC reduction) |
| Data Transform | Pre-compute ship capabilities | -0 (performance, not CC) |
| Consolidate | Single late import | -0 (cleanup, not CC) |

**Estimated CC Reduction Potential:** 15-18 points through helper extraction

**Recommended Approach:** Extract the three helper functions to reduce CC from ~36 to ~18-21, then consider further decomposition if needed.
