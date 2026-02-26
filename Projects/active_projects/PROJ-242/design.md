# PROJ-242: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py` (lines 124-222)
**Current CC:** 36 (grade F)
**Goal:** Reduce to CC < 20

The function applies multiple filter categories to filter ships:
1. Warp capability filter
2. Spaceyard capability filter
3. Cargo filter
4. Special capability filters (5 abilities via loop)
5. Status filters (destroyed/derelict/damaged/undamaged)

## Swarm Findings Summary

### Structure Analysis
- Special capability loop (lines 176-194) is highest complexity contributor with 4 nesting levels
- Status classification cascade (lines 196-220) repeats 4-5 line pattern 4 times
- Boolean capability filter pattern appears 4 times (warp, spaceyard, cargo, special)
- `FleetCapabilityCalculator` imported twice inside conditionals

### Dependency Analysis
- **Single caller:** `FleetListViewModel._refresh()` (line 215)
- **Pure function:** No side effects, no state mutations
- **Interface stability:** Safe to modify - internal implementation detail
- **Test coverage:** Comprehensive (~19 dedicated tests)

### Safety Analysis
- Missing tests for combined filter interactions
- Status filter cascade uses fragile if/continue/append pattern (HIGH RISK)
- Special capability loop uses flag+break+continue pattern (HIGH RISK)
- Critical invariant: ships added to result EXACTLY ONCE through ONE path

## Architecture

### Current Structure (Problematic)
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        # Inline warp filter (6 lines, 4 branches)
        # Inline spaceyard filter (6 lines, 4 branches)
        # Inline cargo filter (6 lines, 4 branches)
        # Inline special abilities loop (18 lines, 10+ branches)
        # Inline status cascade (24 lines, 8 branches)
        result.append(ship)
    return result
```

### Target Structure (Refactored)
```python
def filter_ships(ships, filter_state):
    return [ship for ship in ships if _passes_all_filters(ship, filter_state)]

def _passes_all_filters(ship, filter_state):
    return (
        _passes_warp_filter(ship, filter_state) and
        _passes_spaceyard_filter(ship, filter_state) and
        _passes_cargo_filter(ship, filter_state) and
        _passes_special_ability_filters(ship, filter_state) and
        _passes_status_filter(ship, filter_state)
    )
```

## Key Patterns to Reuse

### Binary Filter Pattern
All capability filters follow this pattern:
```python
show_has = filter_state.get('show_has_X', True)
show_not = filter_state.get('show_no_X', True)
if show_has and show_not:
    return True  # No filtering needed
if has_capability:
    return show_has
return show_not
```

Extract to: `_passes_boolean_filter(has_capability, show_has, show_not) -> bool`

### Status Classification
Current cascade can be replaced with lookup:
```python
STATUS_FILTER_KEYS = {
    'destroyed': 'show_destroyed',
    'derelict': 'show_derelict',
    'damaged': 'show_damaged',
    'undamaged': 'show_undamaged',
}

def _get_ship_status(ship):
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _passes_status_filter(ship, filter_state):
    status = _get_ship_status(ship)
    filter_key = STATUS_FILTER_KEYS[status]
    return filter_state.get(filter_key, True)
```

## Dependencies & Risks

1. **Status cascade refactoring (HIGH)** - The if/continue/append cascade is fragile
   - Mitigation: Add explicit tests for status priority before refactoring
   - Mitigation: Use status lookup pattern instead of cascade

2. **Special abilities loop (MEDIUM)** - Uses flag+break+continue pattern
   - Mitigation: Convert to function that returns False on first failure

3. **Late imports (LOW)** - Circular import avoidance
   - Mitigation: Keep late imports at function scope, not conditionals

4. **Combined filter interactions (MEDIUM)** - Not well tested
   - Mitigation: Add combined filter tests in Phase 1

## Complexity Impact Estimate

| Component | Current CC | After | Notes |
|-----------|-----------|-------|-------|
| filter_ships | 36 | 2 | List comprehension |
| _passes_all_filters | - | 2 | AND chain |
| _passes_boolean_filter | - | 3 | Generic helper |
| _passes_warp_filter | - | 2 | Uses boolean helper |
| _passes_spaceyard_filter | - | 2 | Uses boolean helper |
| _passes_cargo_filter | - | 3 | Uses boolean helper |
| _passes_special_ability_filters | - | 6 | Loop with early return |
| _get_ship_status | - | 4 | Status classification |
| _passes_status_filter | - | 2 | Lookup pattern |
| **Total** | 36 | ~26 distributed | All functions < 7 |

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

Key decisions:
1. Use predicate pattern over filter chain pattern
2. Keep helpers as module-level private functions
3. Status uses lookup instead of cascade
4. Preserve late imports at function scope
