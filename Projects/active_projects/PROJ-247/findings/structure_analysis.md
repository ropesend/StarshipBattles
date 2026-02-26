# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** High (multiple branching paths)

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 5 Times)
The function uses a repeated pattern for "show_X / show_not_X" binary filters. Each instance adds 3-4 branches:

| Lines | Filter Type | Conditions Added |
|-------|-------------|------------------|
| 144-153 | Warp capability | 4 branches |
| 156-164 | Spaceyard capability | 4 branches |
| 167-174 | Cargo | 4 branches |
| 196-201 | Destroyed status | 2 branches |
| 204-208 | Derelict status | 2 branches |
| 211-215 | Damaged status | 2 branches |
| 218-220 | Undamaged status | 1 branch |

### 1.2 Special Capability Loop (Lines 177-194)
This is the highest complexity contributor:
- **Line 178:** `for` loop iterates over `SPECIAL_CAPABILITY_COLUMNS`
- **Line 184:** Outer condition `if not show_has or not show_not`
- **Lines 187-192:** Two nested conditions with `break` statements
- **Line 193:** Additional check on `_skip` flag

The loop introduces multiplicative complexity because each iteration can short-circuit differently.

### 1.3 Status Filter Cascade (Lines 196-220)
Four consecutive status checks create a waterfall of conditions:
- Destroyed check (197-201)
- Derelict check (204-208)
- Damaged check (211-215)
- Undamaged fallback (218-220)

Each block duplicates the pattern: check condition, maybe continue, maybe append and continue.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Warp Capability Filter (Lines 148-153)
```python
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```
**Issue:** Three levels of nesting. The outer guard (`if not show_warp or not show_not_warp`) wraps two inner guards.

**Flattening opportunity:** Extract to a helper function that returns `bool` for "should include ship".

### 2.2 Spaceyard Filter (Lines 158-164)
Same nested structure as warp filter.

### 2.3 Cargo Filter (Lines 169-174)
Same nested structure as warp filter.

### 2.4 Special Capabilities Loop (Lines 177-194)
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if not show_has or not show_not:
        ...
        if has_ability and not show_has:
            _skip = True
            break
        if not has_ability and not show_not:
            _skip = True
            break
if _skip:
    continue
```
**Issue:** Uses a flag variable (`_skip`) to communicate loop result to outer scope. This is a code smell that indicates the loop body should be extracted.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Empty Ships List Check
The function lacks an early return for empty input:
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    # Missing: if not ships: return []
    result = []
    for ship in ships:
        ...
```
Adding `if not ships: return []` at line 141 would skip unnecessary setup.

### 3.2 All Filters Enabled Check
If all `show_*` filters are `True` (or missing, defaulting to `True`), the function does expensive work for no filtering:
```python
# Could add at start:
if _all_filters_enabled(filter_state):
    return list(ships)
```

### 3.3 Status Filter Cascade (Lines 196-220)
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
# ... etc
```
**Issue:** Each block has redundant `result.append(ship); continue` patterns.

**Simplification:** Determine status category once, then use a single lookup:
```python
status = _get_ship_status(ship)  # Returns 'destroyed'|'derelict'|'damaged'|'undamaged'
if filter_state.get(f'show_{status}', True):
    result.append(ship)
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
This exact pattern appears 3 times (warp, spaceyard, cargo):
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_not_X', True)
if not show_has or not show_not:
    has_capability = <check_capability>(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

**Extraction candidate:**
```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    show_key: str,
    show_not_key: str,
    has_capability: bool
) -> bool:
    """Returns True if ship passes the binary filter."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(show_not_key, True)
    if show_has and show_not:
        return True  # Both enabled, always passes
    if has_capability:
        return show_has
    return show_not
```

### 4.2 Status-Based Append Pattern
Lines 200-201, 207-208, 214-215, 220 all follow:
```python
result.append(ship)
continue  # or implicit end
```

**Extraction candidate:** Move filtering logic to a predicate, use list comprehension or `filter()`.

### 4.3 Late Import Pattern
Lines 159, 185, 269, 279 all have:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
This import appears multiple times inside conditional blocks.

**Extraction candidate:** Move to module level or import once at the start of the function.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Filter State Normalization
The function repeatedly calls `filter_state.get('show_X', True)` with default `True`. This could be normalized once at the start:
```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Ensure all filter keys have explicit values."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        'show_has_spaceyard': True,
        'show_no_spaceyard': True,
        # ... etc
    }
    return {**defaults, **filter_state}
```

### 5.2 Ship Status Classification
Lines 197-220 classify ships into: destroyed, derelict, damaged, undamaged. This classification logic is duplicated in `sort_ships` (lines 251-258).

**Extraction candidate:**
```python
def _classify_ship_status(ship: ShipInstance) -> str:
    """Return ship status category: 'destroyed', 'derelict', 'damaged', or 'undamaged'."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### 5.3 Capability Check Evaluation
Each capability filter (warp, spaceyard, cargo, special abilities) evaluates a boolean predicate against the ship. These could be unified:
```python
CAPABILITY_CHECKS = {
    ('show_warp_capable', 'show_not_warp_capable'):
        lambda ship: ShipStatsCalculator.has_warp_capability(ship),
    ('show_has_spaceyard', 'show_no_spaceyard'):
        lambda ship: FleetCapabilityCalculator.ship_has_spaceyard(ship),
    ('show_has_cargo', 'show_no_cargo'):
        lambda ship: bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0,
}
```

### 5.4 Special Capability Key Derivation
Lines 181-183 derive filter keys from column IDs:
```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```
This string manipulation is fragile and could be pre-computed or defined in `SPECIAL_CAPABILITY_COLUMNS`.

---

## Summary of Refactoring Opportunities

| Priority | Finding | Lines | Impact |
|----------|---------|-------|--------|
| High | Extract binary filter pattern | 144-174 | Reduces 3 code blocks to 3 function calls |
| High | Extract ship status classification | 196-220 | Eliminates cascade, enables reuse with `sort_ships` |
| Medium | Extract special capability loop | 177-194 | Removes flag variable, clarifies intent |
| Medium | Normalize filter state once | Throughout | Removes repeated `.get()` calls with defaults |
| Low | Add early return for empty ships | 141 | Minor optimization |
| Low | Pre-compute capability filter keys | 181-183 | Removes fragile string manipulation |

---

## Recommended Refactoring Approach

1. **Extract `_passes_binary_filter()` helper** - Handles the repeated show_has/show_not pattern
2. **Extract `_classify_ship_status()` helper** - Shared with `sort_ships`
3. **Extract `_passes_capability_filters()` helper** - Consolidates all capability checks
4. **Restructure main loop** to use predicate composition:
   ```python
   def filter_ships(ships, filter_state):
       normalized = _normalize_filter_state(filter_state)
       return [
           ship for ship in ships
           if _passes_capability_filters(ship, normalized)
           and _passes_status_filter(ship, normalized)
       ]
   ```

This would reduce the function from ~100 lines to ~10 lines, with complexity distributed across focused helper functions.
