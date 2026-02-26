# PROJ-229: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-229` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-229 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add invariant tests before refactoring
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of the `filter_ships` function from CC 36 to below 20 by extracting predicate helper functions. The function filters ships based on status, capabilities, and cargo using repeated boolean pair patterns that can be consolidated into reusable helpers.

## Goals
- Reduce `filter_ships` CC from 36 to < 20
- Preserve all existing behavior (pure refactoring)
- Add safety tests for critical invariants before changes
- Improve code maintainability through helper extraction

## Scope
**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Test file `tests/unit/ui/screens/test_fleet_report_filters.py`

**Out:**
- Other functions in the same file (`calculate_fleet_stats`, `sort_ships`)
- FleetListViewModel changes
- Any behavioral modifications

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Main test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| ViewModel caller | `game/ui/screens/fleet_report_view_model.py` |
| Special caps constant | `game/ui/screens/fleet_data_source.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure review
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency review
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC reduced below 20
- [ ] Audit passed
- [ ] User verified
