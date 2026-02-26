# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Complexity:** High (multiple nested conditionals, repeated patterns)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 5+ Times)
The function repeats the same binary filter pattern for multiple capabilities:
- Warp capability (lines 144-153)
- Spaceyard capability (lines 156-164)
- Cargo filter (lines 167-174)
- Special capabilities loop (lines 176-194)
- Status filters: destroyed, derelict, damaged, undamaged (lines 196-220)

Each instance follows the pattern:
```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_X = <compute_capability>
    if has_X and not show_X:
        continue
    if not has_X and not show_not_X:
        continue
```

**Impact:** This pattern appears 5 times explicitly, plus inside a loop for special capabilities, creating high cyclomatic complexity.

### 1.2 The Special Capabilities Loop (Lines 176-194)
This loop iterates over `SPECIAL_CAPABILITY_COLUMNS` and applies the binary filter pattern to each. It uses:
- A sentinel flag `_skip` to control outer loop flow
- String manipulation to derive filter keys (`col_id.replace('can_', 'no_', 1)`)
- Repeated import inside the conditional

**Impact:** The loop with internal branching and the `_skip` flag pattern adds significant cognitive complexity.

### 1.3 Status Filter Chain (Lines 196-220)
Four mutually exclusive status checks in sequence:
1. `not ship.is_alive` -> destroyed
2. `ship.is_derelict` -> derelict
3. `ship.is_damaged()` -> damaged
4. else -> undamaged

Each branch has the same structure: check filter, potentially continue, append and continue.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Double-Nested Filter Checks
Each binary filter has this structure:
```python
if not show_X or not show_not_X:        # Level 1
    has_X = ...
    if has_X and not show_X:            # Level 2
        continue
    if not has_X and not show_not_X:    # Level 2
        continue
```

**Flattening opportunity:** Extract to a helper function that returns `True` if ship should be excluded:
```python
def _excluded_by_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
    return (has_capability and not show_has) or (not has_capability and not show_not)
```

### 2.2 Status Filter Nesting
```python
if not ship.is_alive:                      # Level 1
    if not filter_state.get(...):          # Level 2
        continue
    result.append(ship)
    continue
```

**Flattening opportunity:** Use a status categorization function and single lookup.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Missing Early Return for Empty Filter State
If all filters are `True` (default), the function still processes every check. An early optimization:
```python
if all(filter_state.get(k, True) for k in ALL_FILTER_KEYS):
    return list(ships)  # No filtering needed
```

### 3.2 Convert Loop Body to Filter Predicate
The entire loop body could be converted to a predicate function `ship_matches_filters(ship, filter_state) -> bool`, then:
```python
return [ship for ship in ships if ship_matches_filters(ship, filter_state)]
```

This eliminates the manual `result.append()` and multiple `continue` statements.

### 3.3 Status Classification Early Exit
The status checks (destroyed/derelict/damaged/undamaged) are mutually exclusive. Once determined, no further status checks needed. Currently this is handled via `continue` but could be cleaner with:
```python
status = _classify_ship_status(ship)  # Returns 'destroyed'|'derelict'|'damaged'|'undamaged'
if not filter_state.get(f'show_{status}', True):
    continue
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
**Occurrences:** 5 explicit + N in loop (for special capabilities)

**Extract to:**
```python
def _passes_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    show_key: str,
    no_key: str,
    capability_checker: Callable[[ShipInstance], bool]
) -> bool:
    """Return True if ship passes the binary filter, False if excluded."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(no_key, True)
    if show_has and show_not:
        return True  # No filtering active
    has_capability = capability_checker(ship)
    if has_capability and not show_has:
        return False
    if not has_capability and not show_not:
        return False
    return True
```

### 4.2 Filter Configuration Data Structure
Instead of hardcoded filter checks, define filter configurations:
```python
BINARY_FILTERS = [
    BinaryFilter('show_warp_capable', 'show_not_warp_capable', ShipStatsCalculator.has_warp_capability),
    BinaryFilter('show_has_spaceyard', 'show_no_spaceyard', FleetCapabilityCalculator.ship_has_spaceyard),
    BinaryFilter('show_has_cargo', 'show_no_cargo', lambda s: bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0),
]
```

### 4.3 Import Statement Repetition
`FleetCapabilityCalculator` is imported in 3 places (lines 159, 185, and in sort_ships):
- Line 159: Inside spaceyard filter
- Line 185: Inside special capabilities loop

**Extract:** Move import to top of function or module level with lazy initialization if circular imports are a concern.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Ship Status Classification
**Current:** Embedded in filter chain (lines 196-220)
**Extract:**
```python
def classify_ship_status(ship: ShipInstance) -> str:
    """Classify ship into mutually exclusive status category."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### 5.2 Capability Check Computation
**Current:** Computed inline when needed
**Extract:** Pre-compute all capabilities for a ship:
```python
def compute_ship_capabilities(ship: ShipInstance) -> Dict[str, bool]:
    """Compute all filterable capabilities for a ship."""
    return {
        'warp_capable': ShipStatsCalculator.has_warp_capability(ship),
        'has_spaceyard': FleetCapabilityCalculator.ship_has_spaceyard(ship),
        'has_cargo': bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0,
        **{col_id: FleetCapabilityCalculator.ship_has_ability(ship, ability)
           for col_id, ability in SPECIAL_CAPABILITY_COLUMNS.items()}
    }
```

### 5.3 Filter Key Derivation
**Current:** String manipulation inline (line 182)
```python
no_key = col_id.replace('can_', 'no_', 1)
```
**Extract:** Either precompute the mapping or store both keys in `SPECIAL_CAPABILITY_COLUMNS`.

---

## Summary of Refactoring Priorities

| Priority | Issue | Impact | Effort |
|----------|-------|--------|--------|
| High | Extract binary filter helper | Reduces 5+ duplicate patterns | Low |
| High | Extract ship status classifier | Simplifies status chain | Low |
| Medium | Convert to predicate-based filtering | Eliminates manual list building | Medium |
| Medium | Create filter configuration structure | Makes adding filters declarative | Medium |
| Low | Consolidate imports | Minor cleanup | Low |
| Low | Pre-compute capabilities | Performance optimization | Medium |

---

## Recommended Refactoring Approach

1. **First Pass:** Extract `_passes_binary_filter()` helper and `_classify_ship_status()` function
2. **Second Pass:** Create `_ship_matches_filters()` predicate that uses the helpers
3. **Third Pass:** Convert main loop to list comprehension using the predicate
4. **Fourth Pass:** (Optional) Create declarative filter configuration for extensibility

This staged approach allows incremental testing and keeps each change small and verifiable.
