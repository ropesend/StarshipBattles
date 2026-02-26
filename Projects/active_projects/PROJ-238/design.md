# PROJ-238: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Target Function
- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Cyclomatic Complexity:** 36 (grade F)
- **Goal:** Reduce to below 20

### Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

#### Structure Analysis (findings/structure_analysis.md)
The function has five main complexity contributors:
1. **Special capability loop (L176-194):** Highest impact - 3 levels of nesting, flag variable, repeated imports
2. **Binary capability filters:** Repeated 4 times (warp, spaceyard, cargo, special capabilities)
3. **Status filter chain (L196-220):** 4 sequential blocks with early returns
4. **Late imports inside conditionals:** `FleetCapabilityCalculator` imported up to 6 times per ship
5. **Control flow complexity:** 10 `continue` statements plus a `_skip` variable

#### Dependency Analysis (findings/dependency_analysis.md)
- **Single production caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- **Interface stability:** Safe to refactor - uses `.get()` with defaults, pure function
- **Side effects:** None - pure function that creates and returns a new list
- **Test coverage:** Comprehensive - 20+ direct test methods in `test_fleet_report_filters.py`

#### Safety Analysis (findings/safety_analysis.md)
- **Edge cases identified:** Empty ships list, missing filter keys, cargo with zeros
- **Critical invariant:** Status checks must maintain order (destroyed → derelict → damaged → undamaged)
- **Risk areas:** Late imports in loops, control flow complexity with `_skip` variable
- **Test gaps:** Empty filter_state, all-filters-false, destroyed+derelict precedence

## Architecture

### Refactoring Strategy: Extract Filter Predicate Functions

Transform the monolithic function into a composition of small, focused filter predicates:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    return [
        ship for ship in ships
        if _passes_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### Key Patterns to Reuse

- **Binary filter pattern**: `L148-153` - Show/hide based on capability presence
- **Status categorization**: `L196-220` - Destroyed → derelict → damaged → undamaged precedence

### Helper Functions to Extract

1. **`_passes_binary_filter(has_capability, show_has, show_not_has) -> bool`**
   - Generic helper for all binary capability filters
   - Eliminates duplication across warp, spaceyard, cargo, special capabilities

2. **`_passes_capability_filters(ship, filter_state) -> bool`**
   - Combines all capability checks (warp, spaceyard, cargo, special)
   - Moves late import to function start
   - Returns True if ship passes all capability filters

3. **`_get_ship_status(ship) -> str`**
   - Returns status category: 'destroyed', 'derelict', 'damaged', or 'undamaged'
   - Encapsulates the precedence logic

4. **`_passes_status_filter(ship, filter_state) -> bool`**
   - Uses `_get_ship_status()` to determine category
   - Single check against filter state

### Expected Complexity Reduction

| Original | After Extraction | Notes |
|----------|------------------|-------|
| CC 36 | CC ~12-15 | Main function becomes simple composition |
| 99 lines | ~20 lines | Main function dramatically simplified |
| 10 continue | 0 continue | Clean list comprehension flow |

## Dependencies & Risks

| Risk | Level | Mitigation |
|------|-------|------------|
| Behavioral regression | Low | Comprehensive existing tests; add edge case tests first |
| Status precedence broken | Medium | Extract `_get_ship_status()` preserving exact order |
| Late import issues | Low | Move to function-level, Python caches imports |
| Test failures | Low | 20+ existing tests will catch issues |

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
