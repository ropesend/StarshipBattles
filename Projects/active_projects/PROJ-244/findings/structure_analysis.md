# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Complexity:** High (98 lines, multiple nested conditionals, loop with break)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Repeated Binary Filter Pattern (Major Contributor)

The function contains **5 instances** of the same binary filter pattern:

```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_X = <compute capability>
    if has_X and not show_X:
        continue
    if not has_X and not show_not_X:
        continue
```

This pattern appears for:
- Warp capability (lines 144-153)
- Spaceyard capability (lines 156-164)
- Cargo (lines 167-174)
- Special capabilities loop (lines 176-194)
- Status filters (damaged/derelict/destroyed/undamaged - lines 196-220)

Each instance adds 4-6 branches, and the repetition obscures the underlying simplicity.

### 1.2 Special Capability Loop (Lines 176-194)

This loop iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 items) and applies the same binary filter pattern within a loop, adding:
- Loop iteration overhead
- Internal `_skip` flag with `break` statement
- Repeated import inside the loop

### 1.3 Status Filter Cascade (Lines 196-220)

A chain of if-statements handling mutually exclusive ship states:
- Destroyed (lines 197-201)
- Derelict (lines 204-208)
- Damaged (lines 211-215)
- Undamaged (lines 217-220)

Each branch duplicates the `result.append(ship)` and `continue` pattern.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Inner Conditionals Inside "Active Filter" Check

Each filter section has this structure:
```python
if not show_X or not show_not_X:  # Outer: "Is filter active?"
    <compute>
    if has_X and not show_X:      # Inner: "Should exclude?"
        continue
    if not has_X and not show_not_X:
        continue
```

These could be flattened by combining conditions or using a helper function that returns a boolean.

### 2.2 Status Cascade Nesting

```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

The inner `if` could be inverted to an early `continue` without the outer block controlling append.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Pre-compute All Filter States

Currently, filter states are retrieved inside the loop. Moving these outside would:
- Reduce dictionary lookups per ship
- Allow early return if all filters are enabled (no filtering needed)

```python
# Potential early return
if all(filter_state.get(key, True) for key in ALL_FILTER_KEYS):
    return list(ships)  # No filtering needed
```

### 3.2 Convert to Generator with Filter Predicates

Instead of building `result` incrementally, use a generator expression or `filter()` with a predicate function:

```python
return [ship for ship in ships if passes_all_filters(ship, filter_state)]
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter (Extract to Helper)

**Pattern appearing 4+ times:**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = <compute>
    if has_capability and not show_has:
        <exclude>
    if not has_capability and not show_not:
        <exclude>
```

**Suggested extraction:**
```python
def _passes_binary_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Return True if ship passes a binary (has/doesn't have) filter."""
    if show_has and show_not:
        return True  # Both enabled = no filtering
    if has_capability:
        return show_has
    return show_not
```

### 4.2 Import Statement Duplication

`FleetCapabilityCalculator` is imported in **3 separate locations** (lines 159, 185, and implicitly needed elsewhere). Should be imported once at module level or at function start.

### 4.3 Status Determination (Lines 196-220)

The status cascade duplicates logic from `_get_column_value()` in `fleet_data_source.py` (lines 156-164). Consider extracting ship status determination to a shared utility.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter State Normalization

Create a data class or named tuple to pre-process filter state:

```python
@dataclass
class NormalizedFilterState:
    show_warp: bool
    show_not_warp: bool
    show_spaceyard: bool
    show_no_spaceyard: bool
    # ... etc

    @classmethod
    def from_dict(cls, filter_state: Dict[str, bool]) -> "NormalizedFilterState":
        return cls(
            show_warp=filter_state.get('show_warp_capable', True),
            show_not_warp=filter_state.get('show_not_warp_capable', True),
            # ...
        )
```

### 5.2 Capability Computation Separation

Separate "compute ship capabilities" from "apply filter logic":

```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]
    status: ShipStatus  # enum: DESTROYED, DERELICT, DAMAGED, UNDAMAGED

def compute_capabilities(ship: ShipInstance) -> ShipCapabilities:
    """Pure data transformation - no filtering logic."""
    ...

def matches_filter(caps: ShipCapabilities, filters: NormalizedFilterState) -> bool:
    """Pure predicate - no capability computation."""
    ...
```

### 5.3 Filter Chain Architecture

Transform the monolithic function into a chain of independent filter predicates:

```python
FILTER_CHAIN = [
    WarpCapabilityFilter(),
    SpaceyardFilter(),
    CargoFilter(),
    SpecialAbilityFilter(),
    StatusFilter(),
]

def filter_ships(ships, filter_state):
    for ship in ships:
        if all(f.passes(ship, filter_state) for f in FILTER_CHAIN):
            yield ship
```

---

## Summary of Recommendations

| Issue | Recommendation | Impact |
|-------|---------------|--------|
| Repeated binary filter pattern | Extract `_passes_binary_filter()` helper | High - reduces 20+ lines |
| Special capability loop complexity | Extract to `_passes_special_filters()` | Medium - isolates loop |
| Status cascade duplication | Extract `_get_ship_status()` or use enum | Medium - reusable |
| Repeated imports | Move to function top or module level | Low - cleaner code |
| Mixed concerns | Separate capability computation from filtering | High - testability |
| Dictionary lookups in loop | Pre-extract filter state before loop | Low - minor performance |

## Recommended Refactoring Order

1. **Extract binary filter helper** - Immediate win, reduces repetition
2. **Extract special capability filter** - Removes loop complexity from main function
3. **Extract status filter** - Simplifies the final cascade
4. **Pre-compute filter states** - Cleaner data flow
5. **Consider filter chain pattern** - For future extensibility
