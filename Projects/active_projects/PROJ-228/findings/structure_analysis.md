# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cognitive Complexity:** High (multiple nested conditionals, repeated patterns)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 4 Times)
The function uses a "binary filter" pattern where two boolean flags control inclusion/exclusion. This pattern appears at:

| Lines | Filter Pair | Description |
|-------|-------------|-------------|
| 144-153 | `show_warp_capable` / `show_not_warp_capable` | Warp capability filter |
| 156-164 | `show_has_spaceyard` / `show_no_spaceyard` | Spaceyard filter |
| 167-174 | `show_has_cargo` / `show_no_cargo` | Cargo filter |
| 176-194 | Dynamic from `SPECIAL_CAPABILITY_COLUMNS` | Special capabilities loop |

Each instance follows the same structure:
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_property = check_property(ship)
    if has_property and not show_has:
        continue
    if not has_property and not show_not:
        continue
```

**Complexity Impact:** Each binary filter adds 3 conditional branches (1 outer + 2 inner). With 4 instances (3 explicit + 1 in loop), this contributes ~12 branches.

### 1.2 Status Classification Chain (Lines 196-220)
The final section classifies ships by status using a priority chain:

```
destroyed (196-201) -> derelict (204-208) -> damaged (210-215) -> undamaged (217-220)
```

Each branch follows the pattern:
```python
if condition:
    if not filter_state.get('show_X', True):
        continue
    result.append(ship)
    continue
```

**Complexity Impact:** 4 status categories x 2 conditionals each = 8 branches.

### 1.3 Special Capabilities Loop (Lines 176-194)
This loop iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 entries) and applies the binary filter pattern dynamically. It uses a `_skip` flag to break out of the inner loop and then skip in the outer loop.

**Complexity Impact:** Loop adds iteration complexity, plus the `_skip` flag pattern adds cognitive overhead.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Lines 148-153: Warp Capability Check
**Current:**
```python
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Issue:** The outer condition guards expensive computation, but the inner conditions are hard to follow.

**Refactoring Opportunity:** Extract to a helper function:
```python
def _passes_binary_filter(has_property: bool, show_has: bool, show_not: bool) -> bool:
    if has_property and not show_has:
        return False
    if not has_property and not show_not:
        return False
    return True
```

### 2.2 Lines 158-164, 169-174: Same Pattern Repeated
These are identical structural patterns to 2.1. All three could use the same helper.

### 2.3 Lines 196-220: Status Classification Nesting
**Current Structure:**
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

**Issue:** The `if-continue-append-continue` pattern is repeated 4 times with slight variations.

**Refactoring Opportunity:** Extract status determination and filter check:
```python
status = _get_ship_status(ship)  # Returns 'destroyed', 'derelict', 'damaged', 'undamaged'
if not filter_state.get(f'show_{status}', True):
    continue
result.append(ship)
```

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Empty Ships List (Missing)
**Current:** No early return for empty input list.

**Opportunity (Lines 124-125):**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    if not ships:
        return []
```

This is a minor optimization but follows the pattern in `calculate_fleet_stats`.

### 3.2 All Filters Enabled (Potential Early Return)
**Opportunity:** If all relevant filters are `True` (show everything), we could return the input list directly. However, this would require checking all filter keys upfront, which may not be worth the complexity.

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Filter Pattern (Most Significant)
**Occurrences:** Lines 144-153, 156-164, 167-174, 184-192

**Extracted Helper:**
```python
def _apply_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    show_key: str,
    no_key: str,
    property_checker: Callable[[ShipInstance], bool]
) -> Optional[bool]:
    """
    Returns:
        True if ship passes filter
        False if ship should be excluded
        None if filter is not active (both show flags are True)
    """
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(no_key, True)

    if show_has and show_not:
        return None  # Filter not active

    has_property = property_checker(ship)
    if has_property and not show_has:
        return False
    if not has_property and not show_not:
        return False
    return True
```

### 4.2 Filter State Access Pattern
**Pattern:** `filter_state.get('show_X', True)` appears 12 times.

**Consideration:** Could wrap in a helper, but the current pattern is readable. Lower priority.

### 4.3 Import-on-Demand Pattern
**Occurrences:**
- Line 159: `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator`
- Line 185: Same import (duplicated in loop!)

**Issue:** Line 185 imports inside a loop that executes up to 5 times per ship. While Python caches imports, this is still wasteful.

**Refactoring Opportunity:** Move the import to module level or to a single location before the ship loop.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Ship Status Determination
**Current:** Status is determined implicitly through the cascade of `if` statements (lines 196-220).

**Extracted Transformation:**
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Determine ship's status category for filtering."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

**Benefits:**
- Single point of truth for status classification
- Testable in isolation
- Could be reused elsewhere (e.g., sorting, display)

### 5.2 Filter Configuration Extraction
**Current:** Filter keys are strings scattered throughout the function.

**Extracted Configuration:**
```python
BINARY_FILTERS = [
    BinaryFilter(
        show_key='show_warp_capable',
        no_key='show_not_warp_capable',
        checker=lambda s: ShipStatsCalculator.has_warp_capability(s)
    ),
    BinaryFilter(
        show_key='show_has_spaceyard',
        no_key='show_no_spaceyard',
        checker=lambda s: FleetCapabilityCalculator.ship_has_spaceyard(s)
    ),
    BinaryFilter(
        show_key='show_has_cargo',
        no_key='show_no_cargo',
        checker=lambda s: bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0
    ),
]
```

**Benefits:**
- Declarative filter definitions
- Easy to add/remove filters
- Filter logic becomes data-driven

### 5.3 Special Capability Filter Key Derivation (Lines 179-183)
**Current:**
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

**Issue:** The key transformation (`can_` -> `no_`) is inline magic.

**Extracted Transformation:**
```python
def _derive_filter_keys(col_id: str) -> Tuple[str, str]:
    """Derive show/hide filter keys from column ID."""
    show_key = f'show_{col_id}'
    no_key = f'show_{col_id.replace("can_", "no_", 1)}'
    return show_key, no_key
```

---

## Summary of Refactoring Opportunities

| Priority | Location | Issue | Suggested Refactoring |
|----------|----------|-------|----------------------|
| **High** | Lines 144-194 | Binary filter pattern repeated 4x | Extract `_apply_binary_filter()` helper |
| **High** | Lines 196-220 | Status classification cascade | Extract `_get_ship_status()` helper |
| **Medium** | Line 185 | Import inside loop | Move import to line 159 (before ship loop) |
| **Medium** | Lines 176-194 | `_skip` flag pattern | Refactor to use helper with early return |
| **Low** | Lines 179-183 | Magic string transformation | Extract `_derive_filter_keys()` |
| **Low** | Module | Filter definitions scattered | Create declarative `BINARY_FILTERS` config |

---

## Recommended Refactoring Order

1. **Extract `_get_ship_status()`** - Simplest, highest impact on readability
2. **Extract `_apply_binary_filter()`** - Eliminates most repetition
3. **Fix duplicate import** - Quick win, no behavior change
4. **Refactor special capabilities loop** - Uses the new helper
5. **Consider declarative filter config** - Optional, for future extensibility

---

## Metrics

| Metric | Current | After Refactoring (Est.) |
|--------|---------|--------------------------|
| Lines of code | 98 (124-222) | ~60-70 |
| Nesting depth (max) | 4 | 2-3 |
| Repeated patterns | 4 | 0 |
| Cyclomatic complexity | High | Medium |
| Cognitive complexity | High | Low-Medium |
