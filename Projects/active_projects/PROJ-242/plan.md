# PROJ-242: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-242` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-242 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Filter Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:30
**Active Phase:** 1 - Test Fortification
**Last Action:** Multi-agent analysis complete, plan designed
**Next Action:** Add missing test coverage (M1-M6 from safety analysis)
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` from CC=36 to below CC=20 by extracting filter predicate helper functions. The function applies multiple independent filter categories (warp, spaceyard, cargo, special abilities, status) to a list of ships. Each category follows a similar pattern that can be extracted into focused helpers.

## Goals
- Reduce `filter_ships` CC from 36 to under 20
- Distribute complexity across focused helper functions (each < CC 7)
- Improve code readability and maintainability
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Extracting helper functions within the same module
- Adding missing test coverage

**Out:**
- Changing the public interface
- Modifying other functions in the file
- Refactoring `sort_ships` or `calculate_fleet_stats`

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Capability columns | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |
| Ship stats | `game/strategy/services/ship_stats_calculator.py` |
| Fleet capabilities | `game/strategy/data/fleet_capability_calculator.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Code structure analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller and interface analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk and test coverage analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified with radon
- [ ] User verified
