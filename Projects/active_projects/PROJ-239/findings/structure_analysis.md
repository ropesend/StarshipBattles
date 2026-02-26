# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** High (estimated 20+)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Repeated Binary Filter Pattern (Major Contributor)

The function applies the same binary filter logic pattern **5 times** (lines 144-194), each contributing 3-4 branch points:

| Filter Block | Lines | Conditions |
|--------------|-------|------------|
| Warp capability | 148-153 | 3 (if-if-if) |
| Spaceyard capability | 158-164 | 3 (if-if-if) |
| Cargo filter | 169-174 | 3 (if-if-if) |
| Special capabilities loop | 178-194 | 4+ (for-if-if-if-if per iteration) |
| Status filters | 197-220 | 8 (4 status categories x 2 each) |

**The special capabilities loop (lines 178-194) is the worst offender** because it applies 4 conditions per iteration across 5 capability types, creating up to 20 branch points dynamically.

### 1.2 Status Filter Chain (Lines 196-220)

The cascading status checks use a mutually-exclusive pattern but implement it with repeated if-continue-append-continue blocks:

```
Line 197: if not ship.is_alive:
Line 198:   if not filter_state.get('show_destroyed', True):
Line 204: if ship.is_derelict:
Line 205:   if not filter_state.get('show_derelict', True):
Line 211: if ship.is_damaged():
Line 212:   if not filter_state.get('show_damaged', True):
Line 218: if not filter_state.get('show_undamaged', True):
```

Each status contributes 2 branch points (status check + filter check).

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Three-Level Nesting in Binary Filters (Lines 148-153, 158-164, 169-174)

**Current pattern (repeated 3 times):**
```python
if not show_X or not show_not_X:           # Level 1
    has_property = ...                      # Computation
    if has_property and not show_X:         # Level 2
        continue
    if not has_property and not show_not_X: # Level 2
        continue
```

**Could be flattened to:**
```python
# Compute only when needed, then single condition
if should_exclude_by_binary_filter(show_X, show_not_X, has_property):
    continue
```

### 2.2 Special Capabilities Loop Nesting (Lines 178-194)

**Current (4 levels):**
```python
for col_id, ability_name in ...:           # Level 1
    if not show_has or not show_not:       # Level 2
        has_ability = ...                   # Computation
        if has_ability and not show_has:   # Level 3
            _skip = True
            break
        if not has_ability and not show_not: # Level 3
            _skip = True
            break
if _skip:                                   # Level 1 (sentinel check)
    continue
```

**Could be flattened with early return pattern:**
```python
if _fails_special_capability_filters(ship, filter_state):
    continue
```

### 2.3 Status Filter Nesting (Lines 197-220)

**Current:**
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

**Could be a single expression:**
```python
if _passes_status_filter(ship, filter_state):
    result.append(ship)
```

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Missing Early Return for Empty Ships List

**Line 141-142:** The function starts building a result list without checking for empty input:
```python
result = []
for ship in ships:
```

**Recommendation:** Add early return for empty input:
```python
if not ships:
    return []
```
(Note: This is a minor optimization, not a complexity reducer)

### 3.2 Status Determination Could Use Early-Classification

**Lines 196-220:** Instead of the cascading if-continue pattern, determine ship status once and filter:

```python
# Current: Multiple checks with interleaved appends
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
# ... 3 more similar blocks

# Proposed: Classify once, then filter
status = _classify_ship_status(ship)  # Returns: 'destroyed'|'derelict'|'damaged'|'undamaged'
filter_key = f'show_{status}'
if filter_state.get(filter_key, True):
    result.append(ship)
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Filter Pattern (DRY Violation - 4 Occurrences)

**Identical pattern at lines 144-153, 156-164, 167-174:**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_property = <compute property>
    if has_property and not show_has:
        continue
    if not has_property and not show_not:
        continue
```

**Extraction opportunity:**
```python
def _apply_binary_filter(
    filter_state: Dict[str, bool],
    positive_key: str,
    negative_key: str,
    has_property: Callable[[], bool]
) -> bool:
    """Returns True if ship should be EXCLUDED by this filter."""
    show_has = filter_state.get(positive_key, True)
    show_not = filter_state.get(negative_key, True)
    if show_has and show_not:
        return False  # No filtering active
    prop_value = has_property()  # Lazy evaluation
    if prop_value and not show_has:
        return True
    if not prop_value and not show_not:
        return True
    return False
```

### 4.2 Import Inside Loop (Performance Issue)

**Lines 159, 185:** The same import is performed potentially N*M times (N ships * M capabilities):
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Recommendation:** Move import to module level or compute once outside the loop.

### 4.3 Status Filter Pattern (4 Occurrences)

**Lines 197-220:** Four nearly identical blocks:
```python
if <status_check>:
    if not filter_state.get('<filter_key>', True):
        continue
    result.append(ship)
    continue
```

**Extraction opportunity:**
```python
STATUS_FILTERS = [
    (lambda s: not s.is_alive, 'show_destroyed'),
    (lambda s: s.is_derelict, 'show_derelict'),
    (lambda s: s.is_damaged(), 'show_damaged'),
    (lambda s: True, 'show_undamaged'),  # Fallback for healthy ships
]
```

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter Configuration Parsing (Lines 144-183)

The function mixes two concerns:
1. **Parsing filter state** (extracting show_X/show_not_X pairs)
2. **Applying filter logic** (checking ship properties)

**Separation opportunity:**
```python
@dataclass
class BinaryFilterSpec:
    positive_key: str
    negative_key: str
    property_checker: Callable[[ShipInstance], bool]

def _get_active_binary_filters(filter_state: Dict) -> List[BinaryFilterSpec]:
    """Parse filter_state into active filter specifications."""
    ...

def _ship_passes_binary_filters(ship, active_filters) -> bool:
    """Apply pre-parsed filters to a ship."""
    ...
```

### 5.2 Ship Status Classification (Lines 196-220)

**Current:** Inline status determination with filtering interleaved.

**Separation opportunity:**
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Classify ship into one of: destroyed, derelict, damaged, undamaged."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _status_filter_key(status: str) -> str:
    """Map status to filter_state key."""
    return f'show_{status}'
```

### 5.3 Special Capability Filter Keys (Lines 181-183)

**Current:** Inline string manipulation:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

**Separation opportunity:** Pre-compute filter key mappings:
```python
CAPABILITY_FILTER_KEYS = {
    'can_destroy_planet': ('show_can_destroy_planet', 'show_no_destroy_planet'),
    'can_open_warp': ('show_can_open_warp', 'show_no_open_warp'),
    # ...
}
```

---

## Summary of Recommendations

| Priority | Recommendation | Lines Affected | Complexity Reduction |
|----------|----------------|----------------|----------------------|
| High | Extract binary filter helper function | 144-174, 178-194 | -12 to -15 |
| High | Extract status classification | 196-220 | -6 to -8 |
| Medium | Move import outside loop | 159, 185 | Performance fix |
| Medium | Extract special capability filter logic | 176-194 | -4 to -6 |
| Low | Add early return for empty input | 141 | -1 |
| Low | Pre-compute capability filter keys | 181-183 | Readability |

**Estimated Total Complexity Reduction:** 15-20 branch points (from ~25 to ~5-10)

---

## Proposed Refactored Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    if not ships:
        return []

    # Pre-parse active binary filters (only compute what's needed)
    binary_filters = _get_active_binary_filters(filter_state)
    capability_filters = _get_active_capability_filters(filter_state)

    return [
        ship for ship in ships
        if _passes_all_filters(ship, binary_filters, capability_filters, filter_state)
    ]

def _passes_all_filters(ship, binary_filters, capability_filters, filter_state) -> bool:
    """Check if ship passes all active filters."""
    # Binary filters (warp, spaceyard, cargo)
    if not _passes_binary_filters(ship, binary_filters):
        return False

    # Special capability filters
    if not _passes_capability_filters(ship, capability_filters):
        return False

    # Status filter
    return _passes_status_filter(ship, filter_state)
```

This refactoring would:
1. Reduce cyclomatic complexity from ~25 to ~8
2. Eliminate code duplication
3. Improve testability (each helper can be unit tested)
4. Improve readability (clear separation of concerns)
5. Fix the repeated import performance issue
