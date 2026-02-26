# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Current Cyclomatic Complexity:** 36
**Target:** Below 20

---

## 1. Branches/Conditions Contributing Most to Complexity

The function has **five distinct filter blocks**, each contributing multiple branch points:

### 1.1 Warp Capability Filter (lines 144-153)
- 2 boolean retrievals with defaults
- 1 compound condition (`not show_warp or not show_not_warp`)
- 2 nested conditions inside
- **Contribution: ~4 decision points**

### 1.2 Spaceyard Capability Filter (lines 156-164)
- Same pattern as warp filter
- **Contribution: ~4 decision points**

### 1.3 Cargo Filter (lines 167-174)
- Same pattern
- **Contribution: ~4 decision points**

### 1.4 Special Capability Loop (lines 177-194)
- Loop over 5 items (SPECIAL_CAPABILITY_COLUMNS)
- Each iteration has the same 4-point pattern
- **Contribution: ~5 (loop) + 4 (conditions) = ~9 decision points**
- This is the **largest single contributor** to complexity

### 1.5 Status Filters (lines 196-220)
- 4 separate if-blocks for: destroyed, derelict, damaged, undamaged
- Each has nested filter check
- **Contribution: ~8 decision points**

**Total estimated: ~29-30 decision points** (plus the main for loop = ~31)

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 All Binary Capability Filters Share Identical Structure

Lines 148-153, 158-164, 169-174 all follow this pattern:
```python
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

This three-level nesting can be flattened into a single helper:
```python
def _passes_binary_filter(value: bool, show_has: bool, show_not: bool) -> bool:
    if show_has and show_not:
        return True  # No filtering needed
    if value:
        return show_has
    return show_not
```

### 2.2 Status Filter Chain (lines 196-220)

The status determination uses a chain of if-statements with nested filter checks:
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

This could be flattened by determining status first, then doing a single filter lookup.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 No Early Return for Empty Ships List

The function starts iterating immediately. Adding an early return for empty input would be cleaner:
```python
if not ships:
    return []
```

### 3.2 No Pre-check for "Show All" State

If all filters are True (show everything), the entire function could short-circuit:
```python
if _all_filters_enabled(filter_state):
    return list(ships)  # Return copy, no filtering needed
```

### 3.3 Convert `continue` to Predicate Functions

Each `continue` statement represents a failed filter. Instead of inline continues, extract predicate functions:
```python
def _ship_passes_filter(ship, filter_state) -> bool:
    if not _passes_warp_filter(ship, filter_state):
        return False
    if not _passes_spaceyard_filter(ship, filter_state):
        return False
    # ... etc
    return True

return [s for s in ships if _ship_passes_filter(s, filter_state)]
```

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Filter Pattern (Appears 4+ Times)

The "show_has/show_not" pattern is repeated for:
- Warp capability
- Spaceyard capability
- Cargo presence
- Each special capability (5 more times in the loop)

**Extract as:**
```python
def _check_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    show_key: str,
    no_key: str,
    capability_checker: Callable[[ShipInstance], bool]
) -> bool:
    """Returns True if ship passes the filter, False if it should be excluded."""
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(no_key, True)

    if show_has and show_not:
        return True  # No filtering

    has_capability = capability_checker(ship)
    if has_capability:
        return show_has
    return show_not
```

### 4.2 Filter State Retrieval with Default True

This pattern appears 12+ times:
```python
filter_state.get('show_something', True)
```

Could be simplified with a helper or by using a defaultdict.

### 4.3 Late Import Pattern

The same import appears multiple times inside the loop:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

Move this to a single conditional import at the top of the function or module level.

---

## 5. Data Transformations That Could Be Separated

### 5.1 Separate Filter Definition from Filter Application

Currently, filter logic is embedded in the main function. Split into:

1. **Filter Definition Layer** - Define what each filter means
2. **Filter Application Layer** - Apply filters to ships

```python
# Filter definitions (data)
BINARY_FILTERS = [
    BinaryFilter('warp_capable', 'not_warp_capable',
                 lambda s: ShipStatsCalculator.has_warp_capability(s)),
    BinaryFilter('has_spaceyard', 'no_spaceyard',
                 lambda s: FleetCapabilityCalculator.ship_has_spaceyard(s)),
    BinaryFilter('has_cargo', 'no_cargo',
                 lambda s: bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0),
]

# Filter application (logic)
def filter_ships(ships, filter_state):
    return [s for s in ships if all(f.passes(s, filter_state) for f in BINARY_FILTERS)]
```

### 5.2 Separate Status Determination from Status Filtering

The status determination logic (destroyed/derelict/damaged/undamaged) should be a separate function:

```python
def _get_ship_status(ship: ShipInstance) -> str:
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

### 5.3 Extract Special Capabilities Filter

The loop over SPECIAL_CAPABILITY_COLUMNS (lines 177-194) is a distinct operation that should be its own function:

```python
def _passes_special_capabilities_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool]
) -> bool:
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if show_has and show_not:
            continue  # No filtering for this capability

        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if has_ability and not show_has:
            return False
        if not has_ability and not show_not:
            return False
    return True
```

---

## Summary: Recommended Refactoring Strategy

1. **Extract `_passes_binary_filter()` helper** - Reduces 4+ repetitions to single reusable function
2. **Extract `_passes_status_filter()` helper** - Separates status logic from main loop
3. **Extract `_passes_special_capabilities_filter()` helper** - Removes loop from main function
4. **Move imports to function top** - Single import block instead of repeated late imports
5. **Convert main loop to list comprehension** - `[s for s in ships if _passes_all_filters(s, filter_state)]`

**Expected CC after refactoring:** 8-12 (main function) + 4-6 (each helper) = well under 20 for any single function.
