# PROJ-231: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-231` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-231 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verify & Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add edge case tests to establish safety net
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of `filter_ships` in `game/ui/screens/fleet_report_filters.py` from CC 36 to below 20 by extracting helper functions for capability and status filtering.

## Goals
- Reduce `filter_ships` CC from 36 to ≤15
- Preserve all existing behavior (pure refactoring)
- Maintain test coverage and add edge case tests
- Keep code readable and maintainable

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - Extract helpers from `filter_ships`
- `tests/unit/ui/screens/test_fleet_report_filters.py` - Add edge case tests

**Out:**
- Other functions in same file (`calculate_fleet_stats`, `sort_ships`)
- Changes to `FleetListViewModel` or other callers
- Interface changes (signature remains the same)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Special capabilities | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Summary

### Phase 1: Test Fortification
Add tests for edge cases identified by safety analysis before making any code changes.

### Phase 2: Extract Helpers
Extract five helper functions to reduce main function complexity:
- `_passes_warp_filter()`
- `_passes_spaceyard_filter()`
- `_passes_cargo_filter()`
- `_passes_special_capability_filters()`
- `_passes_status_filter()`

### Phase 3: Verify & Cleanup
Run full test suite, verify CC is below threshold, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller and interface analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk and test coverage analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed (CC < 20)
- [ ] User verified
