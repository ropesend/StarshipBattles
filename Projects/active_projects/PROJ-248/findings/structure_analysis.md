# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Complexity:** High (multiple nested conditions, repeated patterns)

---

## 1. Branches/Conditions Contributing Most to Complexity

### Primary Complexity Drivers

| Section | Lines | Complexity Contribution |
|---------|-------|------------------------|
| Warp capability filter | 144-153 | 2 conditions + 2 continue paths |
| Spaceyard capability filter | 156-164 | 2 conditions + 2 continue paths + import |
| Cargo filter | 167-174 | 2 conditions + 2 continue paths |
| Special capability loop | 176-194 | Loop + 2 conditions per iteration + flag variable |
| Status cascade | 196-220 | 4 mutually exclusive states, each with nested condition |

### Most Complex Section: Special Capability Loop (Lines 176-194)

This section is the most complex due to:
- A `for` loop iterating over `SPECIAL_CAPABILITY_COLUMNS`
- Key derivation logic with string manipulation (`col_id.replace('can_', 'no_', 1)`)
- Two filter state lookups per iteration
- Conditional import inside the loop (repeated execution risk)
- A `_skip` flag used to break out of nested context
- Two conditional breaks followed by a flag check outside the loop

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

---

## 2. Nested Conditionals That Could Be Flattened

### Pattern 1: Guard-then-check pattern repeated 4 times

Each filter section follows this pattern:
```python
if not show_X or not show_Y:
    has_capability = <expensive_check>
    if has_capability and not show_X:
        continue
    if not has_capability and not show_Y:
        continue
```

This creates 3 levels of nesting within the main loop. Could be flattened to a single predicate function.

### Pattern 2: Status cascade (Lines 196-220)

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

Each status creates a 2-level nesting. The `continue` after `result.append()` is used to implement mutual exclusion.

---

## 3. Early Returns That Could Simplify Logic

### Potential Early Return: Empty ships list

Currently the function processes an empty list through the entire loop. An early return could simplify:
```python
if not ships:
    return []
```

### Potential Early Return: All filters enabled

If all filter flags are `True` (the defaults), no filtering is needed:
```python
if all(filter_state.get(key, True) for key in ALL_FILTER_KEYS):
    return list(ships)
```

### Converting continue-chains to early returns

The function uses `continue` statements extensively. Extracting the ship-matching logic to a predicate function would convert these to early `return False` statements:

```python
def _ship_matches_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    if not _passes_warp_filter(ship, filter_state):
        return False
    if not _passes_spaceyard_filter(ship, filter_state):
        return False
    # ... etc
    return True
```

---

## 4. Repeated Patterns That Could Be Extracted

### Pattern A: Binary Capability Filter (appears 4 times)

Lines 144-153, 156-164, 167-174, and within 176-194 all follow this pattern:

```python
show_has = filter_state.get('show_has_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_X = <check_capability>
    if has_X and not show_has:
        <exclude>
    if not has_X and not show_not:
        <exclude>
```

**Extraction opportunity:**
```python
def _passes_binary_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Return True if ship passes binary capability filter."""
    if show_has and show_not:
        return True  # No filtering needed
    if has_capability:
        return show_has
    return show_not
```

### Pattern B: Conditional Import (appears 3 times)

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

This import appears at lines 159, 185. Moving it to the top of the function (or to a helper) would improve clarity and ensure single import.

### Pattern C: Status-based exclusion (appears 4 times)

```python
if <status_check>:
    if not filter_state.get('show_<status>', True):
        continue
    result.append(ship)
    continue
```

This pattern could become:
```python
def _get_ship_status_category(ship: ShipInstance) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

---

## 5. Data Transformations That Could Be Separated

### Transformation 1: Filter state normalization

The filter_state dictionary uses inconsistent key naming:
- `show_warp_capable` / `show_not_warp_capable`
- `show_has_spaceyard` / `show_no_spaceyard`
- `show_has_cargo` / `show_no_cargo`
- `show_can_X` / `show_no_X` (derived via string manipulation)

A normalization step could standardize these:
```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> FilterConfig:
    """Convert raw filter_state to structured FilterConfig."""
    return FilterConfig(
        warp=(filter_state.get('show_warp_capable', True),
              filter_state.get('show_not_warp_capable', True)),
        spaceyard=(filter_state.get('show_has_spaceyard', True),
                   filter_state.get('show_no_spaceyard', True)),
        # ... etc
    )
```

### Transformation 2: Ship capability extraction

Currently, capabilities are checked inline within filter logic. Separating capability extraction:
```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]
    status: str  # 'destroyed', 'derelict', 'damaged', 'undamaged'

def _extract_ship_capabilities(ship: ShipInstance) -> ShipCapabilities:
    """Extract all filterable capabilities from a ship."""
    ...
```

This would allow the filter logic to become pure predicate matching:
```python
def _ship_matches(caps: ShipCapabilities, filters: FilterConfig) -> bool:
    ...
```

### Transformation 3: Special capability key derivation

The string manipulation for special capability filter keys (line 182):
```python
no_key = col_id.replace('can_', 'no_', 1)
```

This could be pre-computed into a mapping:
```python
SPECIAL_CAPABILITY_FILTER_KEYS = {
    col_id: (f'show_{col_id}', f'show_{col_id.replace("can_", "no_", 1)}')
    for col_id in SPECIAL_CAPABILITY_COLUMNS
}
```

---

## Summary: Refactoring Recommendations

| Priority | Recommendation | Impact |
|----------|----------------|--------|
| High | Extract binary filter predicate | Removes ~20 lines of duplication |
| High | Extract ship status categorization | Simplifies status cascade logic |
| Medium | Move imports to function top | Cleaner code, single import |
| Medium | Add early return for no-op filter state | Performance optimization |
| Low | Create FilterConfig dataclass | Better type safety, self-documentation |
| Low | Pre-compute special capability keys | Minor clarity improvement |

### Suggested Refactored Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    if not ships:
        return []

    # Imports at top of function
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

    def passes_filters(ship: ShipInstance) -> bool:
        # Warp filter
        if not _passes_binary_filter(
            ShipStatsCalculator.has_warp_capability(ship),
            filter_state.get('show_warp_capable', True),
            filter_state.get('show_not_warp_capable', True)
        ):
            return False

        # Spaceyard filter
        if not _passes_binary_filter(
            FleetCapabilityCalculator.ship_has_spaceyard(ship),
            filter_state.get('show_has_spaceyard', True),
            filter_state.get('show_no_spaceyard', True)
        ):
            return False

        # ... other capability filters ...

        # Status filter
        status = _get_ship_status_category(ship)
        return filter_state.get(f'show_{status}', True)

    return [ship for ship in ships if passes_filters(ship)]
```

This structure:
- Reduces nesting from 3-4 levels to 1-2 levels
- Eliminates the `_skip` flag pattern
- Removes repeated inline conditionals
- Makes the filtering logic declarative rather than imperative
