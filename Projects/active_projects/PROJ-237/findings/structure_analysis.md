# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222

---

## Overview

The function iterates over ships and applies multiple filter categories sequentially. Each filter follows a boolean-pair pattern (show_X / show_not_X) to include/exclude ships based on capability presence.

---

## Complexity Contributors

### 1. Repeated Binary Filter Pattern (High Impact)

Lines 144-174 and 196-220 repeat the same pattern four times:

```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_capability = check_capability(ship)
    if has_capability and not show_X:
        continue
    if not has_capability and not show_not_X:
        continue
```

**Opportunity:** Extract a generic `apply_binary_filter(ship, filter_state, key_prefix, capability_checker)` helper that returns `True` if the ship should be skipped.

### 2. Late Imports Repeated Inside Loop (Medium Impact)

Lines 159 and 185 import `FleetCapabilityCalculator` inside the loop body:

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Opportunity:** Move import to top of function (after the filter check but before the loop) or use a lazy import pattern at module level.

### 3. Special Capability Loop with Break Flag (Medium Impact)

Lines 177-194 use a `_skip` flag and `break` to exit the inner loop:

```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    # ... checks ...
    if condition:
        _skip = True
        break
if _skip:
    continue
```

**Opportunity:** Extract to a helper function that returns `bool`:
```python
if _should_skip_special_capabilities(ship, filter_state):
    continue
```

### 4. Ship Status Filter Chain (Low-Medium Impact)

Lines 196-220 use a cascading if-continue pattern for mutually exclusive states:

```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

if ship.is_derelict:
    # similar pattern
```

**Opportunity:** Could be restructured as:
1. Determine ship status category (enum or string)
2. Check single filter key for that category
3. Single append at the end

---

## Specific Refactoring Opportunities

### A. Extract Binary Filter Helper

Create a helper that encapsulates the repeated pattern:

```python
def _passes_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    show_key: str,
    no_key: str,
    capability_checker: Callable[[ShipInstance], bool]
) -> bool:
    """Return True if ship passes the filter, False if it should be excluded."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(no_key, True)
    if show_has and show_not:
        return True  # No filtering needed
    has_capability = capability_checker(ship)
    if has_capability and not show_has:
        return False
    if not has_capability and not show_not:
        return False
    return True
```

### B. Create Filter Configuration List

Define filters as data rather than code:

```python
BINARY_FILTERS = [
    ('show_warp_capable', 'show_not_warp_capable', ShipStatsCalculator.has_warp_capability),
    ('show_has_spaceyard', 'show_no_spaceyard', FleetCapabilityCalculator.ship_has_spaceyard),
    ('show_has_cargo', 'show_no_cargo', lambda s: bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0),
]
```

Then iterate over this list instead of repeating the pattern.

### C. Extract Status Category Filter

```python
def _get_ship_status_category(ship: ShipInstance) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    category = _get_ship_status_category(ship)
    return filter_state.get(f'show_{category}', True)
```

### D. Use Generator with Filter Composition

Replace the imperative loop with composed filter predicates:

```python
def filter_ships(ships, filter_state):
    predicates = _build_filter_predicates(filter_state)
    return [ship for ship in ships if all(p(ship) for p in predicates)]
```

---

## Nested Conditionals to Flatten

| Lines | Current Structure | Suggested Change |
|-------|------------------|------------------|
| 148-153 | Nested if inside if | Extract to helper returning bool |
| 158-164 | Same pattern | Extract to same helper |
| 169-174 | Same pattern | Extract to same helper |
| 197-201 | if not alive -> if not show -> continue; append; continue | Use status category helper |
| 204-208 | Same nested pattern for derelict | Merge into status helper |
| 211-215 | Same nested pattern for damaged | Merge into status helper |

---

## Summary of Recommended Changes

1. **Extract `_passes_binary_filter()` helper** - Eliminates 4 repeated code blocks
2. **Extract `_should_skip_special_capabilities()` helper** - Removes flag variable and break pattern
3. **Extract `_passes_status_filter()` helper** - Simplifies cascading status checks
4. **Move late imports outside loop** - Performance and clarity improvement
5. **Consider filter composition pattern** - Makes adding new filters trivial

**Estimated complexity reduction:** Current function has ~100 lines with 6 separate filter blocks. Refactored version would be ~30-40 lines in main function plus 3-4 small helpers.
