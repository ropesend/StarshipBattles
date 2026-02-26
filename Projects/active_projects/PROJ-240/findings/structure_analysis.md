# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** High (estimated 15-20 due to multiple branching paths)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 5 Times)
The dominant complexity source is the repeated "binary filter" pattern that appears for each filter type:

```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_X = <expensive_check>
    if has_X and not show_X:
        continue
    if not has_X and not show_not_X:
        continue
```

This pattern appears for:
- **Warp capability** (lines 144-153) - 3 branches
- **Spaceyard capability** (lines 156-164) - 3 branches
- **Cargo filter** (lines 167-174) - 3 branches
- **Special capabilities loop** (lines 176-194) - 3+ branches per iteration
- **Status filters** (lines 196-220) - 4 separate conditional blocks

Each instance contributes 2-3 decision points to cyclomatic complexity.

### 1.2 Status Filter Chain (Lines 196-220)
The final status filtering uses a chain of mutually exclusive conditions:
- `not ship.is_alive` (destroyed)
- `ship.is_derelict`
- `ship.is_damaged()`
- Default (undamaged)

Each block has the same structure: check condition, check filter, append or continue.

### 1.3 Special Capabilities Loop (Lines 176-194)
This is the most complex single section:
- Loops over `SPECIAL_CAPABILITY_COLUMNS.items()`
- Each iteration has the binary filter pattern
- Uses a `_skip` flag and `break` to exit early
- Requires a separate `if _skip: continue` check after the loop

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Double-Nested Filter Checks
Every binary filter has this structure:
```python
if not show_X or not show_not_X:      # Outer condition
    has_X = ...
    if has_X and not show_X:          # Nested condition 1
        continue
    if not has_X and not show_not_X:  # Nested condition 2
        continue
```

This could be flattened to a single predicate function call.

### 2.2 Status Filter Nesting
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):  # Nested
        continue
    result.append(ship)
    continue
```

The inner `if` is unnecessary nesting that could be expressed as a guard clause.

### 2.3 Special Capabilities Loop Body
```python
if not show_has or not show_not:
    from game.strategy...
    has_ability = ...
    if has_ability and not show_has:
        _skip = True
        break
    if not has_ability and not show_not:
        _skip = True
        break
```

Three levels of nesting: loop -> outer if -> inner if statements.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 No Early Return for Empty Ships
The function lacks an early return for empty input:
```python
if not ships:
    return []
```
This would avoid unnecessary loop setup.

### 3.2 No Early Return When All Filters Are Enabled
If all filters default to `True`, the function still processes every check. An early return could short-circuit:
```python
if all(filter_state.get(key, True) for key in ALL_FILTER_KEYS):
    return list(ships)
```

### 3.3 Helper Functions Could Use Early Returns
Instead of nested conditionals, helper functions with early returns would be clearer:
```python
def passes_warp_filter(ship, show_warp, show_not_warp) -> bool:
    if show_warp and show_not_warp:
        return True  # Early return - no filtering needed
    is_warp = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp:
        return show_warp
    return show_not_warp
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
The exact same logic structure appears 4 times (warp, spaceyard, cargo, special capabilities):

```python
# Pattern: Check if ship has capability, filter based on show_has/show_not flags
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_capability = <check_function>(ship)
    if has_capability and not show_has:
        continue/skip
    if not has_capability and not show_not:
        continue/skip
```

**Extraction opportunity:** A single helper function:
```python
def passes_binary_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Return True if ship passes the binary filter."""
    if show_has and show_not:
        return True
    if has_capability:
        return show_has
    return show_not
```

### 4.2 Status Filter Pattern
Lines 196-220 repeat this pattern 4 times:
```python
if <condition>:
    if not filter_state.get('show_<status>', True):
        continue
    result.append(ship)
    continue
```

**Extraction opportunity:** A status-to-filter-key mapping and single check:
```python
STATUS_FILTERS = [
    (lambda s: not s.is_alive, 'show_destroyed'),
    (lambda s: s.is_derelict, 'show_derelict'),
    (lambda s: s.is_damaged(), 'show_damaged'),
    (lambda s: True, 'show_undamaged'),  # Default
]
```

### 4.3 Late Import Pattern
The same import appears in multiple places:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

This import appears at lines 159, 185. It could be moved to a single location or the module level with a lazy import wrapper.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter State Normalization
The function repeatedly calls `filter_state.get(key, True)`. This could be pre-processed:
```python
def normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Fill in default True values for missing filter keys."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        'show_has_spaceyard': True,
        # ... etc
    }
    return {**defaults, **filter_state}
```

### 5.2 Ship Capability Extraction
The function computes capabilities on-demand inside the loop. Pre-computing a capability map would separate concerns:
```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_capabilities: Dict[str, bool]
    status: Literal['destroyed', 'derelict', 'damaged', 'undamaged']

def extract_ship_capabilities(ship: ShipInstance) -> ShipCapabilities:
    """Extract all filterable capabilities from a ship."""
    ...
```

### 5.3 Filter Key Derivation
Lines 181-183 derive filter keys from column IDs:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation is a data transformation that could be pre-computed in a mapping.

### 5.4 Status Determination
The status checking logic (destroyed -> derelict -> damaged -> undamaged) is a classification that could be extracted:
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

---

## Summary of Refactoring Opportunities

| Category | Count | Impact |
|----------|-------|--------|
| Binary filter pattern extractions | 4 | High - eliminates ~40 lines of duplication |
| Status filter consolidation | 4 blocks -> 1 | Medium - simplifies final section |
| Nested conditional flattening | 5+ locations | Medium - improves readability |
| Early returns | 2 opportunities | Low - minor improvement |
| Data transformation separation | 4 opportunities | High - enables testing and reuse |

**Recommended Priority:**
1. Extract binary filter helper function (highest duplication)
2. Separate capability extraction from filtering
3. Consolidate status filter logic
4. Normalize filter state at function entry
