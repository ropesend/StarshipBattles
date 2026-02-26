# PROJ-233: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Target Function

- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Current CC:** 36 (Grade F)
- **Target CC:** < 20
- **Length:** 99 lines

---

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Structure Analysis

The `filter_ships` function processes ships through 5 filter categories in sequence:

1. **Warp capability filter** (lines 143-153)
2. **Spaceyard capability filter** (lines 155-164)
3. **Cargo filter** (lines 166-174)
4. **Special capabilities loop** (lines 176-194) - 5 ability types
5. **Ship status filters** (lines 196-220) - destroyed > derelict > damaged > undamaged

**Primary complexity sources:**

| Issue | Severity | Lines | CC Impact |
|-------|----------|-------|-----------|
| Repeated binary filter pattern (4x) | High | 143-174 | +12 |
| Status filter cascade | Medium | 196-220 | +8 |
| Special capabilities loop with `_skip` flag | Medium | 176-194 | +10 |
| Late imports inside loop | Low | 159, 185 | +0 |

### Dependency Analysis

- **Single caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py` (line 215)
- **Interface stability:** CAN change - internal module boundary, single consumer
- **Pure function:** No side effects, deterministic, returns new list
- **Filter state:** ~20 boolean keys passed from view model's `get_filter_state()`

### Safety Analysis

- **19 existing tests** - All passing across 5 test classes
- **Well-tested paths:** Basic status, warp, spaceyard, cargo, DestroyPlanet ability

**Missing test coverage (CRITICAL):**
1. Empty ships list handling
2. Multiple filter combinations
3. Partial/empty filter_state (defaults behavior)
4. All filters disabled scenario
5. 4 of 5 special capabilities untested (OpenWarpPoint, CloseWarpPoint, DestroyStar, CreateSphereWorld)
6. Derelict/damaged mutual exclusivity verification

---

## Architecture

### Key Patterns to Reuse

- **Binary filter pattern:** `filter_state.get(show_key, True)` with lazy evaluation
- **Status priority chain:** destroyed > derelict > damaged > undamaged (mutually exclusive)
- **Late imports:** `FleetCapabilityCalculator` imported inside conditionals to avoid circular imports

### Dependencies & Risks

1. **Filter order dependency (HIGH)** - Status categories must remain mutually exclusive; refactoring must preserve evaluation order
2. **Late imports (HIGH)** - `FleetCapabilityCalculator` cannot move to module level due to circular import risk
3. **`_skip` flag pattern (MEDIUM)** - Nested loop with break needs careful extraction
4. **Double-negative boolean logic (MEDIUM)** - `if not show_X or not show_not_X` pattern is error-prone

### Opportunities Discovered

- Binary filter helper can eliminate ~24 lines of duplicated code
- Status classification logic is duplicated in `sort_ships` - shared helper possible
- Filter predicates can be composed declaratively

---

## Refactoring Strategy

### Approach: Extract Helper Functions

Transform the monolithic filter function into a composition of focused helper functions:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    return [
        ship for ship in ships
        if _passes_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### Helper Function Design

1. **`_passes_binary_filter(filter_state, show_key, hide_key, has_property) -> bool`**
   - Generic helper for all binary (has/doesn't have) filter patterns
   - Eliminates 4x code duplication
   - Expected CC contribution: 3

2. **`_passes_capability_filters(ship, filter_state) -> bool`**
   - Combines warp, spaceyard, cargo, and special capability filters
   - Uses `_passes_binary_filter` internally
   - Handles late imports at function level (not module level)
   - Expected CC contribution: 8-10

3. **`_passes_status_filter(ship, filter_state) -> bool`**
   - Handles destroyed > derelict > damaged > undamaged priority
   - Flattened conditional chain with single return
   - Expected CC contribution: 5

### Expected Complexity Distribution

| Component | Current CC | After Refactor |
|-----------|------------|----------------|
| `filter_ships` | 36 | 2-3 |
| `_passes_binary_filter` | - | 3 |
| `_passes_capability_filters` | - | 8-10 |
| `_passes_status_filter` | - | 5 |
| **Total** | 36 | ~18-21 |

**All helpers will be below threshold of 20.**

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Summary

1. **Test fortification is mandatory** - Missing coverage must be added BEFORE any code changes
2. **Extract binary filter helper first** - Highest duplication reduction, lowest risk
3. **Preserve filter evaluation order** - Capability filters before status filters
4. **Keep lazy evaluation** - Only compute expensive checks when filter is active
5. **Late imports stay at function level** - Move to helper functions, not module level
