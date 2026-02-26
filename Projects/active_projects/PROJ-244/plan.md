# PROJ-244: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-244` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-244 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helper Functions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:25
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan written
**Next Action:** Add safety tests for combined filtering, derelict precedence, and partial filter state
**Blockers:** None

## Overview
Refactor the `filter_ships` function (CC 36) to reduce cyclomatic complexity below 20. The function implements 6 distinct filter categories with repeated binary filter patterns. The approach is to extract helper predicate functions for each filter category while preserving the critical status filter hierarchy invariant.

## Goals
- Reduce `filter_ships` cyclomatic complexity from 36 to < 20
- Preserve all existing behavior (pure refactoring)
- Maintain test coverage throughout
- Improve code maintainability via extracted helpers

## Scope
**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Test file `tests/unit/ui/screens/test_fleet_report_filters.py`
- Extracting helper functions within the same file

**Out:**
- Other functions in the same file (`calculate_fleet_stats`, `sort_ships`)
- Changes to the function interface
- Changes to callers (`FleetListViewModel`)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Data source | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure review
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency review
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC of `filter_ships` < 20
- [ ] User verified
