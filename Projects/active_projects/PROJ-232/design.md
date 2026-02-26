# PROJ-232: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222 (99 lines)
**Current CC:** 36 (Grade F)
**Target CC:** Below 20, preferably below 15

The function applies multiple binary filters (warp, spaceyard, cargo, special capabilities) and status filters (destroyed, derelict, damaged, undamaged) to filter a list of ships based on a filter state dictionary.

## Swarm Findings Summary

Combined analysis from 3 parallel review agents:

### Architecture

**Function Characteristics:**
- Pure function with no side effects
- Single production caller: `FleetListViewModel._refresh()`
- Excellent test coverage (20+ tests across 5 test classes)
- Interface can change with coordinated updates

**Filter Structure:**
1. Capability filters (warp, spaceyard, cargo, special) - can skip in any order
2. Status filters (destroyed, derelict, damaged, undamaged) - MUST preserve order

**Critical Invariant:**
The status filter hierarchy MUST be preserved:
```
destroyed (is_alive == False)
    -> derelict (is_derelict == True, implies damaged)
        -> damaged (is_damaged() == True)
            -> undamaged (else)
```
A derelict ship IS damaged, so checking derelict before damaged is semantically required.

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 148-153, 158-164, 169-174` - Identical "show_has/show_not" pattern repeated 8+ times
- **Filter State Default**: `filter_state.get('key', True)` - All filters default to True (show all)
- **Late Import**: `FleetCapabilityCalculator` imported inside function to avoid circular imports

### Dependencies & Risks

1. **Status Filter Order (HIGH)** - Cannot reorder status checks without breaking semantics. Mitigation: Extract to single function that preserves order.

2. **Late Imports (MEDIUM)** - `FleetCapabilityCalculator` is imported inside conditionals. Mitigation: Move to function top, pass as parameter to helpers.

3. **Filter Key Naming (MEDIUM)** - Special capability keys derived via `col_id.replace('can_', 'no_', 1)`. Mitigation: Preserve this logic exactly.

4. **Test Updates (LOW)** - 20+ tests directly test this function. Mitigation: All helpers are private, tests call public function.

### Opportunities Discovered

- **Generic Binary Filter Helper**: All capability filters share identical structure - extract once, reuse 8+ times
- **Status Category Function**: Separate status determination from status filtering for better testability
- **Short-Circuit Optimization**: Early return when all filters enabled (show-all case)

## Refactoring Strategy

### Approach: Extract Filter Predicates

Extract filter logic into private helper functions while keeping the main loop structure:

```python
def filter_ships(ships, filter_state):
    from ... import FleetCapabilityCalculator  # Single late import

    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state, FleetCapabilityCalculator):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_special_capabilities_filter(ship, filter_state, FleetCapabilityCalculator):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Helper Functions

| Function | Purpose | Expected CC |
|----------|---------|-------------|
| `_passes_binary_capability_filter()` | Generic binary filter check | 3 |
| `_get_ship_status_category()` | Determine ship status | 4 |
| `_passes_status_filter()` | Check status filter | 2 |
| `_passes_warp_filter()` | Warp capability filter | 4 |
| `_passes_spaceyard_filter()` | Spaceyard filter | 4 |
| `_passes_cargo_filter()` | Cargo filter | 4 |
| `_passes_special_capabilities_filter()` | Special abilities loop | 7 |
| `filter_ships` (refactored) | Main function | 6-8 |

### Why Not List Comprehension?

A list comprehension would hide the filter order, making maintenance harder:
```python
# Harder to understand filter order and debug
return [s for s in ships if all(_passes_filter(s, f, filter_state) for f in FILTERS)]
```

The explicit loop with `continue` statements preserves clear filter ordering and is easier to debug.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made

1. **Extract helpers, keep main loop** - Preserves filter order clarity
2. **Pass FleetCapabilityCalculator as parameter** - Avoids repeated late imports in helpers
3. **Add tests before refactoring** - Safety net for hierarchy invariant
4. **Private helpers only** - Public interface unchanged, no test rewrites needed
