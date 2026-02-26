# PROJ-235: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
**Current CC:** 36 (Grade F)
**Target CC:** <20 (ideally <15)
**Lines:** 124-222 (~99 lines)

The function filters a list of ships based on a dictionary of boolean filter flags. It applies 8+ filter categories, each using the same pattern of checking show_has/show_not filter pairs.

## Swarm Findings Summary

Combined analysis from three parallel review agents:

### Structure Analysis (Agent 1)

**Root Cause of High CC:** The same boolean filter pattern repeats 8+ times:
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_it = check_capability(ship)
    if has_it and not show_has: continue
    if not has_it and not show_not: continue
```

This contributes ~4 decision points per category = 32+ CC from repetition.

**Key Patterns Identified:**
1. Boolean pair filter (8+ instances)
2. Status cascade (destroyed/derelict/damaged/undamaged)
3. Loop with break and external flag (`_skip` pattern)

### Dependency Analysis (Agent 2)

**Callers:** Single caller - `FleetListViewModel._refresh()`

**Interface:** Stable but tightly coupled
- `ships: List[ShipInstance]`
- `filter_state: Dict[str, bool]` (20 distinct keys)

**Side Effects:** None - pure function

**Test Coverage:** Excellent (20 direct + 26 indirect = 46 tests)

### Safety Analysis (Agent 3)

**Verdict:** SAFE TO REFACTOR

**Critical Invariant:** Status filter order must be preserved:
1. destroyed (not `is_alive`) - checked FIRST
2. derelict (`is_derelict`) - checked SECOND
3. damaged (`is_damaged()`) - checked THIRD
4. undamaged - catch-all LAST

**Risk Areas:**
- HIGH: Status filter ordering
- MEDIUM: `_skip` flag pattern for special capabilities
- MEDIUM: Filter key string derivation assumes "can_" prefix

**Test Gaps Identified:**
1. Multiple filters combined (status + capability)
2. Both sides of filter disabled (empty result)
3. Status priority edge cases (derelict vs damaged)

## Architecture

### Current Structure
```
filter_ships(ships, filter_state)
├── for each ship:
│   ├── warp filter check (4 decisions)
│   ├── spaceyard filter check (4 decisions)
│   ├── cargo filter check (4 decisions)
│   ├── special capabilities loop (5 iterations × 4 decisions)
│   └── status cascade (destroyed/derelict/damaged/undamaged)
└── return filtered list
```

### Proposed Structure
```
filter_ships(ships, filter_state)
├── for each ship:
│   ├── _passes_capability_filters(ship, filter_state)
│   │   ├── _passes_boolean_filter() for warp
│   │   ├── _passes_boolean_filter() for spaceyard
│   │   ├── _passes_boolean_filter() for cargo
│   │   └── _passes_boolean_filter() for each special capability
│   └── _passes_status_filter(ship, filter_state)
│       └── _get_ship_status(ship)
└── return filtered list
```

### Key Patterns to Reuse

- **Boolean Filter Pattern**: Extract to `_passes_boolean_filter(has_capability, show_has, show_not) -> bool`
- **Status Determination**: Extract to `_get_ship_status(ship) -> str` returning 'destroyed'/'derelict'/'damaged'/'undamaged'
- **Lazy Import Pattern**: Keep `FleetCapabilityCalculator` imports inside filter checks to avoid circular dependencies

### Dependencies & Risks

1. **Status Filter Ordering** - Mitigation: Extract to dedicated function with clear comments, add dedicated tests
2. **Lazy Imports** - Mitigation: Keep inside `_passes_capability_filters`, not at module level
3. **Filter Key Derivation** - Mitigation: Preserve existing string manipulation in loop

### Opportunities Discovered

- The generic `_passes_boolean_filter` helper could be reused elsewhere in the codebase
- Status determination logic could be useful for other UI components
- Test fortification will improve overall test suite quality

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Decision 1: Extract Generic Boolean Filter Helper

**Choice:** Create `_passes_boolean_filter(has_capability, show_has, show_not) -> bool`

**Rationale:** This pattern appears 8+ times. A single helper reduces CC by ~28 points.

### Decision 2: Preserve Status Check Order in Dedicated Function

**Choice:** Create `_passes_status_filter` that uses `_get_ship_status` internally

**Rationale:** Encapsulating the order-sensitive logic makes the invariant explicit and testable.

### Decision 3: Keep Lazy Imports Inside Capability Filter

**Choice:** Don't move `FleetCapabilityCalculator` import to module level

**Rationale:** Circular import avoidance is intentional per code comments. The import is only needed when filters are active.

### Decision 4: Add Test Coverage Before Refactoring

**Choice:** Phase 1 adds 4+ new test scenarios

**Rationale:** Safety analysis identified gaps in combined filter testing and status priority verification.
