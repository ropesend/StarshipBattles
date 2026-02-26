# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222 (99 lines)
**Function Signature:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## Executive Summary

The `filter_ships` function applies multiple boolean filter pairs (show/hide toggles) to a list of ships. The primary complexity drivers are:

1. **Repeated binary filter pattern** - Same logic structure repeated 6+ times
2. **Loop-within-loop for special capabilities** - Lines 178-194
3. **Late imports inside the loop** - Lines 159, 185
4. **Status cascade at the end** - Four sequential if-blocks with identical structure

---

## Detailed Control Flow Analysis

### Section 1: Warp Capability Filter (Lines 143-153)

```python
show_warp = filter_state.get('show_warp_capable', True)
show_not_warp = filter_state.get('show_not_warp_capable', True)

if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Pattern:** Binary capability filter (has/doesn't have)
- Outer condition guards expensive capability check
- Two inner conditions for positive/negative case

**Complexity contribution:** Medium - 3 nesting levels, but logic is straightforward.

---

### Section 2: Spaceyard Capability Filter (Lines 155-164)

```python
show_has_yard = filter_state.get('show_has_spaceyard', True)
show_no_yard = filter_state.get('show_no_spaceyard', True)
if not show_has_yard or not show_no_yard:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
    if has_yard and not show_has_yard:
        continue
    if not has_yard and not show_no_yard:
        continue
```

**Pattern:** Identical to Section 1 - binary capability filter
**Issue:** Late import at line 159 happens inside the loop, executed per-ship when filter is active.

---

### Section 3: Cargo Filter (Lines 166-174)

```python
show_has_cargo = filter_state.get('show_has_cargo', True)
show_no_cargo = filter_state.get('show_no_cargo', True)
if not show_has_cargo or not show_no_cargo:
    has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    if has_cargo and not show_has_cargo:
        continue
    if not has_cargo and not show_no_cargo:
        continue
```

**Pattern:** Identical to Sections 1-2 - binary capability filter
**Note:** Inline cargo computation (line 170) could be extracted.

---

### Section 4: Special Capability Filters Loop (Lines 176-194)

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

**Pattern:** Loop over multiple binary capability filters
**Complexity contribution:** HIGH
- Nested loop (ship loop + capability loop)
- String manipulation to derive filter keys (lines 181-183)
- Late import at line 185 (inside nested loop!)
- Flag variable `_skip` to break out of outer loop

**Issues:**
1. Late import executed potentially many times per ship
2. `_skip` flag pattern is a workaround for Python's lack of labeled break
3. Filter key derivation (`col_id.replace('can_', 'no_', 1)`) is obscure

---

### Section 5: Status Cascade (Lines 196-220)

```python
# Destroyed filter
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

# Derelict filter
if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue

# Damaged filter
if ship.is_damaged():
    if not filter_state.get('show_damaged', True):
        continue
    result.append(ship)
    continue

# Undamaged (healthy) ships
if not filter_state.get('show_undamaged', True):
    continue
result.append(ship)
```

**Pattern:** Mutually exclusive status categories in priority order
**Complexity contribution:** Medium-High (4 sequential blocks with same structure)

**Note:** The order matters: destroyed > derelict > damaged > undamaged. This is a state machine pattern encoded as cascading if-statements.

---

## Identified Patterns

### Pattern 1: Binary Filter (Repeated 6+ times)

```python
show_positive = filter_state.get('show_X', True)
show_negative = filter_state.get('show_not_X', True)
if not show_positive or not show_negative:
    has_property = <check property>
    if has_property and not show_positive:
        continue  # or set skip flag
    if not has_property and not show_negative:
        continue  # or set skip flag
```

**Occurrences:**
- Lines 143-153 (warp)
- Lines 155-164 (spaceyard)
- Lines 166-174 (cargo)
- Lines 178-192 (special capabilities, 5 sub-filters)
- Lines 196-220 (status filters, 4 variants)

**Extraction opportunity:** A helper function like `apply_binary_filter(ship, filter_state, key, checker_fn) -> bool` could eliminate 80% of the code.

---

### Pattern 2: Late Imports Inside Loop

**Locations:**
- Line 159: `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator`
- Line 185: Same import (inside nested loop!)

**Issue:** While Python caches imports, the import lookup still has overhead. More importantly, it hurts readability - imports should be at module level or at least at function level.

---

### Pattern 3: Status State Machine

Lines 196-220 encode a priority-based state machine:

```
Ship State Priority:
1. Destroyed (!is_alive) - highest priority
2. Derelict (is_derelict)
3. Damaged (is_damaged())
4. Undamaged - default/lowest priority
```

**Extraction opportunity:** This could be a separate function `get_ship_status_category(ship) -> StatusCategory` that returns an enum, then a single filter lookup.

---

## Complexity Hotspots (Ranked)

| Rank | Lines | Description | Cyclomatic Impact |
|------|-------|-------------|-------------------|
| 1 | 178-194 | Special capabilities loop | +10 (loop + 5 capabilities x 2 conditions) |
| 2 | 196-220 | Status cascade | +8 (4 status checks x 2 paths each) |
| 3 | 143-153 | Warp filter | +3 |
| 4 | 155-164 | Spaceyard filter | +3 |
| 5 | 166-174 | Cargo filter | +3 |

---

## Recommended Refactoring Strategies

### Strategy 1: Extract Binary Filter Helper

Create a helper that encapsulates the binary filter pattern:

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    positive_key: str,
    negative_key: str,
    has_property: bool
) -> bool:
    """Return True if ship passes this binary filter."""
    show_positive = filter_state.get(positive_key, True)
    show_negative = filter_state.get(negative_key, True)

    if show_positive and show_negative:
        return True  # Both shown, always passes

    if has_property:
        return show_positive
    else:
        return show_negative
```

### Strategy 2: Extract Status Classifier

```python
def _get_status_category(ship: ShipInstance) -> str:
    """Return the ship's status category for filtering."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### Strategy 3: Move Imports to Function Level

Move the late import to the top of the function, guarded by whether any relevant filter is active:

```python
def filter_ships(ships, filter_state):
    # Determine if we need FleetCapabilityCalculator
    needs_capability_calc = _any_capability_filter_active(filter_state)
    if needs_capability_calc:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    ...
```

### Strategy 4: Data-Driven Filter Configuration

Replace hard-coded filter blocks with a configuration list:

```python
CAPABILITY_FILTERS = [
    ('show_warp_capable', 'show_not_warp_capable', lambda s: ShipStatsCalculator.has_warp_capability(s)),
    ('show_has_spaceyard', 'show_no_spaceyard', lambda s: FleetCapabilityCalculator.ship_has_spaceyard(s)),
    ('show_has_cargo', 'show_no_cargo', lambda s: _has_cargo(s)),
    # ... special capabilities
]
```

---

## Summary of Findings

| Finding | Lines | Severity | Recommendation |
|---------|-------|----------|----------------|
| Repeated binary filter pattern | 143-194 | High | Extract helper function |
| Late imports in loop | 159, 185 | Medium | Move to function top |
| Flag variable for loop break | 177, 188-192 | Low | Extract to function with early return |
| Status cascade duplication | 196-220 | Medium | Extract status classifier |
| String manipulation for keys | 181-183 | Low | Use explicit key mapping |
| Inline cargo computation | 170 | Low | Extract to helper |

**Estimated complexity reduction:** Extracting the binary filter helper and status classifier could reduce the function from ~99 lines to ~30-40 lines, with cyclomatic complexity dropping from ~27 to ~10.
