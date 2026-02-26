# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36

---

## Executive Summary

The `filter_ships` function has CC=36 due to **repeated boolean filter patterns** applied across 8 different filter categories. The core pattern is identical in each case:

1. Get two boolean filter flags (show_has, show_not)
2. If either is False, check the ship's capability
3. Skip ship if it has capability and show_has=False
4. Skip ship if it lacks capability and show_not=False

This pattern repeats **8 times** with slight variations, contributing approximately 4 decision points per filter category (32 total from repetition alone).

---

## Section 1: Complexity Contributors by Branch

| Filter Category | Lines | Decision Points | Notes |
|----------------|-------|-----------------|-------|
| Warp capability | 144-153 | 4 | `if not show_warp or not show_not_warp`, then 2 nested ifs |
| Spaceyard capability | 156-164 | 4 | Same pattern |
| Cargo filter | 167-174 | 4 | Same pattern |
| Special capabilities loop | 176-194 | ~16 | Loop over 5 items, each with same pattern + break logic |
| Destroyed filter | 197-201 | 2 | `if not ship.is_alive` + nested filter check |
| Derelict filter | 204-208 | 2 | `if ship.is_derelict` + nested filter check |
| Damaged filter | 211-215 | 2 | `if ship.is_damaged()` + nested filter check |
| Undamaged filter | 218-220 | 1 | Final fallthrough |

**Primary complexity source:** The special capabilities loop (lines 176-194) iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 entries), applying the same 4-decision pattern inside a loop with `break` statements.

---

## Section 2: Nested Conditionals That Could Be Flattened

### Pattern 1: Guard-then-check (lines 148-153, 158-164, 169-174)

```python
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

This 3-level nesting (outer if, capability check, two inner ifs) could be flattened using a helper function that returns a boolean "should include".

### Pattern 2: Loop with break and external flag (lines 176-194)

```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
        # ... check and set _skip = True, break
if _skip:
    continue
```

This could be extracted to a function returning a boolean directly.

### Pattern 3: Status cascade (lines 197-220)

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
# ... etc.
```

Each status check duplicates the "check filter, maybe skip, else append" pattern.

---

## Section 3: Early Return Opportunities

The function currently uses `continue` to skip ships. The overall structure is:

```
for ship in ships:
    # Multiple filter checks with continue
    result.append(ship)
return result
```

**Recommended transformation:** Extract a `_should_include_ship(ship, filter_state) -> bool` predicate function. This changes the main function to:

```python
def filter_ships(ships, filter_state):
    return [ship for ship in ships if _should_include_ship(ship, filter_state)]
```

Within `_should_include_ship`, each filter check becomes an early `return False`, ending with `return True`:

```python
def _should_include_ship(ship, filter_state):
    if not _passes_warp_filter(ship, filter_state):
        return False
    if not _passes_spaceyard_filter(ship, filter_state):
        return False
    # ... etc.
    return True
```

---

## Section 4: Repeated Patterns That Could Be Extracted

### Pattern A: Boolean Pair Filter (appears 4 times explicitly, 5 more in loop)

```python
show_has = filter_state.get('show_<capability>', True)
show_not = filter_state.get('show_no_<capability>', True)
if not show_has or not show_not:
    has_capability = <check_function>(ship)
    if has_capability and not show_has:
        # exclude
    if not has_capability and not show_not:
        # exclude
```

**Extraction candidate:** A generic helper:

```python
def _passes_boolean_filter(
    ship,
    filter_state,
    show_has_key: str,
    show_not_key: str,
    check_fn: Callable[[ShipInstance], bool]
) -> bool:
    show_has = filter_state.get(show_has_key, True)
    show_not = filter_state.get(show_not_key, True)
    if show_has and show_not:
        return True  # No filtering needed
    has_it = check_fn(ship)
    if has_it and not show_has:
        return False
    if not has_it and not show_not:
        return False
    return True
```

This single function could replace all 8+ instances of the pattern.

### Pattern B: Status Filter Chain (lines 197-220)

The destroyed/derelict/damaged/undamaged chain follows:

```python
if <status_check>:
    if not filter_state.get('show_<status>', True):
        continue
    result.append(ship)
    continue
```

**Extraction candidate:** Determine ship status once, then apply a single lookup:

```python
def _get_ship_status(ship) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _passes_status_filter(ship, filter_state) -> bool:
    status = _get_ship_status(ship)
    return filter_state.get(f'show_{status}', True)
```

---

## Section 5: Data Transformations That Could Be Separated

### Transformation 1: Filter Key Derivation

Lines 179-183 compute filter keys from column IDs:

```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)  # 'can_destroy_planet' -> 'no_destroy_planet'
show_not = filter_state.get(f'show_{no_key}', True)
```

This string manipulation could be pre-computed in a configuration mapping:

```python
CAPABILITY_FILTER_KEYS = {
    'can_destroy_planet': ('show_can_destroy_planet', 'show_no_destroy_planet'),
    'can_open_warp': ('show_can_open_warp', 'show_no_open_warp'),
    # ... etc.
}
```

### Transformation 2: Import Caching

The `FleetCapabilityCalculator` import appears in 3 places within the function (lines 159, 185, and conditionally on each iteration). This could be moved to module level or imported once at the start of the function.

### Transformation 3: Capability Check Functions

Rather than inline lambdas or method calls, define a registry of capability checks:

```python
CAPABILITY_CHECKS = {
    'warp': lambda ship: ShipStatsCalculator.has_warp_capability(ship),
    'spaceyard': lambda ship: FleetCapabilityCalculator.ship_has_spaceyard(ship),
    'cargo': lambda ship: bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0,
    # Special capabilities from SPECIAL_CAPABILITY_COLUMNS
    **{col_id: lambda s, name=name: FleetCapabilityCalculator.ship_has_ability(s, name)
       for col_id, name in SPECIAL_CAPABILITY_COLUMNS.items()}
}
```

---

## Recommended Refactoring Priority

1. **High Impact:** Extract `_passes_boolean_filter()` helper - reduces ~28 decision points to ~4
2. **Medium Impact:** Extract `_passes_status_filter()` helper - reduces ~6 decision points to ~2
3. **Low Impact:** Pre-compute filter key mappings - improves readability, minor complexity reduction

**Expected CC after refactoring:** 6-10 (down from 36)

---

## Code Sketch: Refactored Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    return [ship for ship in ships if _should_include_ship(ship, filter_state)]

def _should_include_ship(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    # Capability filters (warp, spaceyard, cargo, special abilities)
    if not _passes_capability_filters(ship, filter_state):
        return False

    # Status filter (destroyed, derelict, damaged, undamaged)
    if not _passes_status_filter(ship, filter_state):
        return False

    return True

def _passes_capability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    for config in FILTER_CONFIGS:
        if not _passes_boolean_filter(ship, filter_state, config):
            return False
    return True

def _passes_boolean_filter(ship, filter_state, config) -> bool:
    show_has = filter_state.get(config.show_has_key, True)
    show_not = filter_state.get(config.show_not_key, True)
    if show_has and show_not:
        return True
    has_it = config.check_fn(ship)
    return not (has_it and not show_has) and not (not has_it and not show_not)

def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    status = _get_ship_status(ship)
    return filter_state.get(f'show_{status}', True)
```

This structure reduces the main function to a simple list comprehension and distributes complexity across focused, testable helper functions.
