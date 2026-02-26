# Structure Analysis: filter_ships Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Cyclomatic Complexity:** 36
**Target:** Below 20

---

## Executive Summary

The `filter_ships` function implements a multi-criteria filter system for ship lists. The high complexity stems from:
1. **Six distinct filter categories** each with positive/negative toggles (12 filter flags total)
2. **Repeated filter pattern** applied inconsistently across categories
3. **Nested conditionals** within loops
4. **Status filtering cascade** at the end with interleaved early returns

The function can be reduced below CC=20 by extracting the repeated filter pattern into a predicate-based helper and separating status categorization from filtering.

---

## Control Flow Structure

### Main Loop Structure
```
for ship in ships:                           # +1
    # Warp filter block
    if not show_warp or not show_not_warp:   # +1
        if is_warp and not show_warp:        # +1
            continue                          # branch
        if not is_warp and not show_not_warp: # +1
            continue                          # branch

    # Spaceyard filter block (same pattern)   # +3
    # Cargo filter block (same pattern)       # +3

    # Special capabilities loop
    for col_id, ability_name in ...:         # +1
        if not show_has or not show_not:     # +1
            if has_ability and not show_has:  # +1
                _skip = True; break
            if not has_ability and not show_not: # +1
                _skip = True; break
    if _skip: continue                        # +1

    # Status cascade
    if not ship.is_alive:                    # +1
        if not filter_state.get('show_destroyed'): # +1
            continue
        result.append(ship); continue

    if ship.is_derelict:                     # +1
        if not filter_state.get('show_derelict'): # +1
            continue
        result.append(ship); continue

    if ship.is_damaged():                    # +1
        if not filter_state.get('show_damaged'): # +1
            continue
        result.append(ship); continue

    if not filter_state.get('show_undamaged'): # +1
        continue
    result.append(ship)
```

### Complexity Breakdown by Section

| Section | Lines | Branches | Notes |
|---------|-------|----------|-------|
| Warp filter | 143-153 | 4 | Positive + negative toggle |
| Spaceyard filter | 155-164 | 4 | Same pattern |
| Cargo filter | 166-174 | 4 | Same pattern |
| Special capabilities loop | 176-194 | 6 | Loop + nested conditionals |
| Status cascade | 196-220 | 8 | Four mutually exclusive states |
| **Total** | | **26+** | Plus loop overhead |

---

## Findings

### 1. Branches Contributing Most to Complexity

**High-Impact: The Boolean Filter Pattern (repeated 4 times)**

Lines 148-153, 158-164, 169-174, 184-192 all share this pattern:
```python
show_positive = filter_state.get('show_X', True)
show_negative = filter_state.get('show_no_X', True)
if not show_positive or not show_negative:
    has_attribute = check_attribute(ship)
    if has_attribute and not show_positive:
        continue
    if not has_attribute and not show_negative:
        continue
```

Each instance adds 3-4 branches. This pattern appears 4 times = 12-16 branches.

**Medium-Impact: Status Cascade (lines 196-220)**

The status determination uses a cascade of `if` statements with interleaved early returns:
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
# ... repeated for derelict, damaged, undamaged
```

This adds 8 branches for 4 mutually exclusive states.

### 2. Nested Conditionals That Could Be Flattened

**Special Capabilities Loop (lines 176-194)**

The inner loop with nested conditionals is the worst offender:
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
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

This adds 6 branches (loop + 3 conditionals + break handling).

### 3. Early Returns That Could Simplify Logic

The status cascade (lines 196-220) uses early `continue` statements well, but the pattern could be simplified by:
1. Determining ship status ONCE into an enum/string
2. Looking up whether that status is enabled in the filter_state
3. Single branch instead of four cascaded branches

**Current (4 branches):**
```python
if not ship.is_alive: ...
if ship.is_derelict: ...
if ship.is_damaged(): ...
# else undamaged
```

**Proposed (1 branch after extraction):**
```python
status = get_ship_status(ship)  # Returns enum
if not filter_state.get(f'show_{status}', True):
    continue
```

### 4. Repeated Patterns That Could Be Extracted

**Pattern A: Binary Attribute Filter**

Used for: warp, spaceyard, cargo, and special capabilities.

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    positive_key: str,
    negative_key: str,
    has_attribute: bool
) -> bool:
    """Return True if ship passes this binary filter."""
    show_positive = filter_state.get(positive_key, True)
    show_negative = filter_state.get(negative_key, True)

    # Both enabled = pass all
    if show_positive and show_negative:
        return True

    # Check attribute against enabled filters
    if has_attribute:
        return show_positive
    return show_negative
```

This extraction would reduce 4 filter blocks (12-16 branches) to 4 function calls with the complexity isolated in a single helper (CC ~4).

**Pattern B: Lazy Attribute Check with Filter**

Several filters only compute the attribute when needed:
```python
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    ...
```

This could be abstracted into a predicate-based filter system.

### 5. Data Transformations That Could Be Separated

**Status Categorization (lines 196-220)**

The function mixes two concerns:
1. **Categorizing** ships into status buckets (destroyed/derelict/damaged/undamaged)
2. **Filtering** based on which buckets are enabled

These could be separated:
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Categorize ship into mutually exclusive status."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

Then filtering becomes:
```python
status = _get_ship_status(ship)
if not filter_state.get(f'show_{status}', True):
    continue
result.append(ship)
```

This reduces 8 branches to 4 (inside the extracted function) + 1 (the filter check).

---

## Specific Recommendations for Extraction

### Recommendation 1: Extract `_passes_binary_filter` helper

**Impact:** Reduces ~16 branches to ~4 branches in main function

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    positive_key: str,
    negative_key: str,
    has_attribute: bool
) -> bool:
    """Check if ship passes a binary (has/lacks) filter.

    Returns True if the ship should be included based on
    the positive/negative filter toggles.
    """
    show_with = filter_state.get(positive_key, True)
    show_without = filter_state.get(negative_key, True)

    if show_with and show_without:
        return True
    if has_attribute:
        return show_with
    return show_without
```

### Recommendation 2: Extract `_get_ship_status` helper

**Impact:** Reduces 8 branches to 5 (4 in helper + 1 in caller)

```python
def _get_ship_status(ship: "ShipInstance") -> str:
    """Get the mutually exclusive status of a ship."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

### Recommendation 3: Extract `_passes_capability_filters` helper

**Impact:** Isolates loop complexity (~6 branches)

```python
def _passes_capability_filters(
    ship: "ShipInstance",
    filter_state: Dict[str, bool]
) -> bool:
    """Check if ship passes all special capability filters."""
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        show_has = filter_state.get(f'show_{col_id}', True)
        no_key = col_id.replace('can_', 'no_', 1)
        show_not = filter_state.get(f'show_{no_key}', True)

        if show_has and show_not:
            continue

        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if not _passes_binary_filter(filter_state, f'show_{col_id}', f'show_{no_key}', has_ability):
            return False
    return True
```

### Recommendation 4: Restructured filter_ships

After extractions, the main function becomes:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    result = []

    for ship in ships:
        # Binary capability filters
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_capability_filters(ship, filter_state):
            continue

        # Status filter
        status = _get_ship_status(ship)
        if not filter_state.get(f'show_{status}', True):
            continue

        result.append(ship)

    return result
```

**Estimated CC after refactoring:** ~8-12 (down from 36)

---

## Complexity Estimate After Extraction

| Component | Estimated CC |
|-----------|-------------|
| `filter_ships` (main) | 6-8 |
| `_passes_binary_filter` | 3 |
| `_get_ship_status` | 4 |
| `_passes_capability_filters` | 5-6 |
| Individual filter wrappers | 2 each |

**Total distributed complexity:** Same logic, but no single function exceeds CC=10.

---

## Alternative Approaches Considered

### Table-Driven Filters
Could define filters as a list of (key_positive, key_negative, predicate) tuples and iterate. This would reduce code but may hurt readability for this specific use case.

### Predicate Composition
Build a list of filter predicates and use `all()`. Elegant but harder to debug and may obscure the lazy evaluation optimization.

### Filter Classes
Create a Filter class hierarchy. Overkill for this module's scope.

---

## Recommended Implementation Order

1. **Extract `_get_ship_status`** - Simplest, independent, tests existing behavior
2. **Extract `_passes_binary_filter`** - Core pattern reused everywhere
3. **Apply `_passes_binary_filter` to warp/spaceyard/cargo** - Replace inline code
4. **Extract `_passes_capability_filters`** - Isolates the loop complexity
5. **Simplify main function** - Clean up with extracted helpers
6. **Verify CC < 20** - Run complexity tool to confirm

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Behavioral regression | Low | Extensive existing test coverage |
| Performance impact | Very Low | Same operations, just reorganized |
| Import changes | Low | Moved import inside helper |
| Over-extraction | Medium | Keep helpers private, co-located |

---

## Conclusion

The `filter_ships` function has CC=36 primarily due to repeated boolean filter patterns and a cascaded status check. By extracting:

1. `_passes_binary_filter` - reusable helper for all binary filters
2. `_get_ship_status` - status categorization
3. `_passes_capability_filters` - special capability loop

The main function can be reduced to CC < 10, well under the target of 20. All helpers would remain private to this module and maintain the existing lazy evaluation optimization.
