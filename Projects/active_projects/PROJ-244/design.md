# PROJ-244: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Target Function
- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Current CC:** 36 (Grade F)
- **Goal:** Reduce to CC < 20

### Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

#### Structure Analysis
The function contains a **repeated binary filter pattern** appearing 5 times:
1. Warp capability filter (lines 144-153)
2. Spaceyard capability filter (lines 156-164)
3. Cargo filter (lines 167-174)
4. Special capabilities loop (lines 176-194)
5. Status filters cascade (lines 196-220)

Each instance adds 4-6 branches. The special capability loop iterates over 5 ability types with an inner `_skip` flag pattern.

#### Dependency Analysis
- **Single caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- **Pure function:** No side effects, no state mutations
- **Interface:** `Dict[str, bool]` with 20 possible filter keys, all defaulting to `True`
- **Late imports:** `FleetCapabilityCalculator` imported inside function to avoid circular imports

#### Safety Analysis
- **Well-tested:** 20+ tests across 5 test classes
- **Critical invariant:** Status filter hierarchy (destroyed > derelict > damaged > undamaged)
- **Risk areas:** Status filter ordering, special capability loop control flow
- **Gap:** No tests for combined multi-category filtering

### Architecture

The `filter_ships` function is a pure filtering function used by the Fleet Report UI. It implements 6 distinct filter categories with binary has/doesn't-have semantics.

### Key Patterns to Reuse
- **Binary filter pattern**: Lines 144-153 - check both "show_X" and "show_not_X" flags
- **Status hierarchy**: Lines 196-220 - destroyed > derelict > damaged > undamaged
- **Lazy import**: Lines 159, 185 - import `FleetCapabilityCalculator` inside function

### Dependencies & Risks
1. **Status filter ordering** - must preserve destroyed > derelict > damaged > undamaged hierarchy
2. **Circular imports** - `FleetCapabilityCalculator` imported lazily to avoid cycles
3. **Special capability loop** - `_skip` flag pattern is fragile, extract to helper

### Opportunities Discovered
- Generic `_passes_binary_filter()` helper can eliminate 80% of repeated code
- Status filter can be isolated as a single focused helper
- Function could eventually use filter chain pattern for extensibility

## Refactoring Strategy

### Approach: Extract Helper Predicates

Transform the monolithic function into a coordinator that delegates to focused helper functions:

```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        if not _passes_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Helper Functions to Extract

| Helper | Responsibility | Est. CC |
|--------|---------------|---------|
| `_passes_binary_filter()` | Generic binary has/doesn't-have logic | 3 |
| `_passes_warp_filter()` | Warp capability check | 3-4 |
| `_passes_spaceyard_filter()` | Spaceyard capability check | 3-4 |
| `_passes_cargo_filter()` | Cargo presence check | 3-4 |
| `_passes_special_capability_filters()` | Loop over 5 special abilities | 8-10 |
| `_passes_status_filter()` | Status hierarchy (destroyed/derelict/damaged/undamaged) | 8-10 |

### Expected Complexity After Refactoring

- **Main function:** CC ~6 (just coordination)
- **Each helper:** CC 3-10
- **Total reduction:** From 36 to max ~10 in any single function

## Risk Assessment

### High Risk: Status Filter Hierarchy
The status filters (lines 196-220) implement mutual exclusivity with specific ordering. A derelict ship is also damaged, but should only match "derelict" filter.

**Mitigation:** Extract to a single helper that preserves the exact if-elif-else chain.

### Medium Risk: Lazy Imports
`FleetCapabilityCalculator` is imported inside the function body to avoid circular imports.

**Mitigation:** Test module-level import first. If circular, keep lazy import in relevant helpers.

### Medium Risk: Special Capability Loop
The `_skip` flag with `break`/`continue` is fragile.

**Mitigation:** Extract to helper that returns boolean, eliminating the flag pattern.

### Low Risk
- Cargo check expression (straightforward boolean logic)
- Warp/spaceyard filters (standard binary pattern)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
