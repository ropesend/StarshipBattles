# PROJ-249: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-249` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-249 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Filter Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 03:00
**Active Phase:** 1 - Test Fortification
**Last Action:** Analysis complete - multi-agent review identified refactoring strategy
**Next Action:** Add missing test coverage for edge cases and status filter order
**Blockers:** None

## Overview
Refactor the `filter_ships` function in `game/ui/screens/fleet_report_filters.py` to reduce cyclomatic complexity from 36 to below 20. The function filters ships through 5 filter categories using a repeated binary filter pattern that can be extracted into helper functions.

## Goals
- Reduce `filter_ships` cyclomatic complexity from 36 to <20
- Extract reusable filter helper functions
- Improve code readability and maintainability
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `filter_ships` function (lines 124-222)
- New helper functions in same file
- Test additions for edge cases

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- Changes to `FleetListViewModel` or other callers
- Changes to filter_state keys or semantics

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py` |
| Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Data source | `game/ui/screens/fleet_data_source.py` |

## Refactoring Strategy

### Pattern Identified
The function uses a **repeated binary filter pattern** 6+ times:
```python
show_positive = filter_state.get('show_X', True)
show_negative = filter_state.get('show_not_X', True)
if not show_positive or not show_negative:
    has_property = <check property>
    if has_property and not show_positive:
        continue
    if not has_property and not show_negative:
        continue
```

### Extraction Plan
1. **`_passes_binary_filter(filter_state, pos_key, neg_key, has_property)`** - Generic binary filter
2. **`_get_status_category(ship)`** - Returns 'destroyed'/'derelict'/'damaged'/'undamaged'
3. **`_passes_capability_filters(ship, filter_state)`** - Warp/Spaceyard/Cargo/Special filters
4. **`_passes_status_filter(ship, filter_state)`** - Status filter with correct order

### Critical Invariants
- **Status filter order MUST be preserved:** destroyed → derelict → damaged → undamaged
- **Late imports CANNOT be moved** (circular dependency prevention)
- **Default filter values MUST remain True**

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk assessment

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC reduced below 20
- [ ] Audit passed
- [ ] User verified
