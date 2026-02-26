# PROJ-249: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Lines: 124-222 (99 lines)
- Cyclomatic Complexity: 36 (Grade F)
- Goal: Reduce CC to below 20

The function filters a list of `ShipInstance` objects through 5 filter categories using a repeated binary filter pattern. The high complexity comes from duplicated branching logic.

## Swarm Findings Summary

Combined analysis from three parallel review agents:

### Structure Analysis Findings
- **Repeated Binary Filter Pattern** (6+ occurrences): Same logic structure repeated for warp, spaceyard, cargo, special capabilities, and status filters
- **Complexity Hotspot**: Special capabilities loop (lines 178-194) contributes ~10 to CC due to nested loop
- **Status Cascade** (lines 196-220): Four sequential if-blocks implementing priority-based classification
- **Late Imports**: FleetCapabilityCalculator imported inside loops (lines 159, 185)

### Dependency Analysis Findings
- **Single Caller**: `FleetListViewModel._refresh()` in `fleet_report_view_model.py` line 215
- **Pure Function**: No side effects, no state mutations
- **Interface Stability**: CAN CHANGE safely due to single caller
- **Test Coverage**: ~20 test cases across 5 test classes

### Safety Analysis Findings
- **Test Coverage Gaps**: Missing tests for empty input, combined filters, status order
- **Critical Invariant**: Status filter order MUST be preserved (destroyed > derelict > damaged > undamaged)
- **Late Imports**: Cannot be moved to module level (circular dependency prevention)
- **Verdict**: REFACTORABLE with caution - add tests first

## Architecture

### Current Structure
```
filter_ships(ships, filter_state)
├── Warp capability filter (lines 143-153)
├── Spaceyard capability filter (lines 155-164)
├── Cargo filter (lines 166-174)
├── Special capability filters loop (lines 176-194)
└── Status cascade (lines 196-220)
    ├── Destroyed check
    ├── Derelict check
    ├── Damaged check
    └── Undamaged (default)
```

### Proposed Structure
```
filter_ships(ships, filter_state)
├── _passes_warp_filter(ship, filter_state)
├── _passes_spaceyard_filter(ship, filter_state)
├── _passes_cargo_filter(ship, filter_state)
├── _passes_special_capability_filters(ship, filter_state)
└── _passes_status_filter(ship, filter_state)
    └── _get_status_category(ship)

_passes_binary_filter(filter_state, pos_key, neg_key, has_property)  # Shared helper
```

## Key Patterns to Reuse

- **Binary Filter Pattern**: `fleet_report_filters.py:143-153` - Check positive and negative filter keys with short-circuit optimization

```python
show_positive = filter_state.get('show_X', True)
show_negative = filter_state.get('show_not_X', True)
if not show_positive or not show_negative:  # Optimization: skip check if both True
    has_property = <expensive check>
    if has_property and not show_positive: continue
    if not has_property and not show_negative: continue
```

## Dependencies & Risks

1. **Status Filter Order** - CRITICAL
   - Order MUST be: destroyed → derelict → damaged → undamaged
   - A destroyed ship that is also derelict must be classified as destroyed
   - Mitigation: Add explicit tests, preserve order in `_get_status_category`

2. **Late Imports** - Cannot change
   - `FleetCapabilityCalculator` imported inside function to avoid circular imports
   - Mitigation: Keep late imports in helper functions, document why

3. **Special Capability Key Derivation** - Fragile
   - Line 182: `col_id.replace('can_', 'no_', 1)` creates filter keys
   - Mitigation: Preserve exact logic, don't simplify

4. **Filter State Defaults** - Must remain True
   - All `.get()` calls default to True for "show all" behavior
   - Mitigation: Preserve defaults in all helper functions

## Opportunities Discovered

- **Data-Driven Filtering**: Could eventually replace hard-coded filter blocks with a configuration list (future refactoring opportunity, out of scope)
- **Typed FilterState**: Could replace `Dict[str, bool]` with a dataclass (future enhancement, out of scope)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
