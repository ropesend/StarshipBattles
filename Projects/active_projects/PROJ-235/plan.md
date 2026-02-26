# PROJ-235: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-235` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-235 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helper Functions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:30
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing test coverage (4 test cases)
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` from CC=36 to below CC=20 by extracting the repeated boolean filter pattern into helper functions. The function currently applies 8+ filter categories using identical 4-decision patterns, which can be consolidated into a generic helper.

## Goals
- Reduce `filter_ships` CC from 36 to <15 (target: 10-12)
- Maintain 100% backward compatibility (pure refactoring)
- Improve code readability and testability
- Preserve the critical status filter ordering invariant

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- `tests/unit/ui/screens/test_fleet_report_filters.py` - Add missing test coverage

**Out:**
- `calculate_fleet_stats` function (CC is acceptable)
- `sort_ships` function (CC is acceptable)
- `FleetListViewModel` changes (interface is stable)
- Other files in the codebase

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` |
| Unit Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Data Source | `game/ui/screens/fleet_data_source.py` |
| View Model (Caller) | `game/ui/screens/fleet_report_view_model.py` |

## Refactoring Strategy

### Core Insight
The function has 8+ filter categories, each using the same pattern:
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_it = check_capability(ship)
    if has_it and not show_has: continue
    if not has_it and not show_not: continue
```

This pattern contributes ~4 decision points per category = 32+ CC from repetition alone.

### Solution
1. Extract a generic `_passes_boolean_filter()` helper (CC ~3)
2. Extract `_passes_status_filter()` for the status cascade (CC ~4)
3. Reduce main function to simple filter composition (CC ~5)

### Expected CC After Refactoring
- `filter_ships`: 3-5 (down from 36)
- `_passes_boolean_filter`: 3-4
- `_passes_status_filter`: 4-5
- `_passes_capability_filters`: 2-3
- Total distributed CC: ~15 across 4 functions

## Critical Invariants
1. **Status Filter Order:** destroyed -> derelict -> damaged -> undamaged (MUST preserve)
2. **Default Behavior:** Missing filter keys default to `True` (show all)
3. **Lazy Imports:** `FleetCapabilityCalculator` must remain inside filter checks
4. **Short-Circuit Optimization:** Skip expensive checks when both filters are True

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure agent findings
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency agent findings
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety agent findings

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 6246)
- [ ] CC verified below 20
- [ ] User verified
