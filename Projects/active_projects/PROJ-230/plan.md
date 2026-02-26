# PROJ-230: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-230` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-230 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Filter Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - multi-agent review identified refactoring strategy
**Next Action:** Add 8 safety tests for critical invariants before any code changes
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` from 36 to below 20 by extracting 5 filter predicate helper functions. The function filters ships by multiple dimensions (warp, spaceyard, cargo, special abilities, status) with each dimension following an identical boolean filter pair pattern. The status filter has a critical mutual exclusivity invariant that must be preserved.

## Goals
- Reduce `filter_ships` CC from 36 to <10
- Extract 5 helper functions with CC 4-8 each
- Add 8 safety tests before refactoring
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `filter_ships` function (lines 124-222)
- Test file additions for safety coverage
- Helper function extractions

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- Interface changes to `filter_ships` signature
- Changes to `FleetListViewModel` or other callers

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure review
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency review
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC of `filter_ships` below 20
- [ ] No functions above CC 10
