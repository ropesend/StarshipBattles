# PROJ-240: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-240` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-240 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor Main | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Finalize | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete, plan documented
**Next Action:** Add edge case tests per phase_1_checklist.md
**Blockers:** None

## Overview

Refactor `filter_ships` function in `game/ui/screens/fleet_report_filters.py` to reduce cyclomatic complexity from 36 to below 20. The function filters ships based on various capability and status filters. The high complexity comes from a repeated binary filter pattern (5 occurrences) and a status filter chain (4 blocks).

## Goals
- Reduce `filter_ships` CC from 36 to below 10
- Extract repeated patterns into helper functions
- Preserve all existing behavior (pure refactoring)
- Maintain filter evaluation order invariant

## Scope
**In:**
- Extract binary filter pattern to helper
- Extract status classification logic
- Extract per-filter-type helpers
- Add edge case tests for safety

**Out:**
- Changing function signature
- Changing filter behavior
- Refactoring other functions in the file

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Data Source | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Related Documents
- [design.md](design.md) - Architecture analysis and refactoring strategy
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Multi-agent analysis reports

## Critical Invariants
1. **Filter Order:** Warp → Spaceyard → Cargo → Special → Status
2. **Status Priority:** Destroyed → Derelict → Damaged → Undamaged
3. **Default True:** Missing filter keys default to True (show)
4. **Late Imports:** Keep FleetCapabilityCalculator imports inside helpers

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (6246+ baseline)
- [ ] `filter_ships` CC < 20
- [ ] Audit passed
- [ ] User verified
