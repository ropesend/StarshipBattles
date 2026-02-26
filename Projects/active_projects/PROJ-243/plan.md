# PROJ-243: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-243` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-243 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Binary Filter Helper | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Status Classification | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:30
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing edge case tests before refactoring
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of the `filter_ships` function from CC 36 to below CC 20 by extracting repeated binary filter patterns into a reusable helper and separating ship status classification logic. The function has 5 filter categories with identical patterns that can be consolidated.

## Goals
- Reduce `filter_ships` CC from 36 to below 20 (target: CC 2-5)
- Extract `_passes_binary_filter()` helper to handle all capability filters (CC ~3)
- Extract `_get_ship_status()` helper to classify ship status (CC ~4)
- All existing tests must continue to pass
- No behavioral changes - pure refactoring

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- Adding edge case tests to `tests/unit/ui/screens/test_fleet_report_filters.py`
- Extracting helper functions in the same file

**Out:**
- Other functions in `fleet_report_filters.py` (`calculate_fleet_stats`, `sort_ships`)
- Changes to `FleetListViewModel` or other callers
- Any interface changes to `filter_ships` signature

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` (lines 124-222) |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| View Model (caller) | `game/ui/screens/fleet_report_view_model.py` |
| Fleet Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |
| Ship Stats Calculator | `game/strategy/services/ship_stats_calculator.py` |

## Phase Summary

### Phase 1: Test Fortification
Add missing edge case tests identified by safety analysis to ensure refactoring doesn't introduce regressions.

### Phase 2: Extract Binary Filter Helper
Create `_passes_binary_filter()` helper function and apply it to warp, spaceyard, cargo, and special capability filters. This is the primary CC reduction phase.

### Phase 3: Extract Status Classification
Create `_get_ship_status()` helper to classify ships into destroyed/derelict/damaged/undamaged categories.

### Phase 4: Verify & Cleanup
Run full test suite, verify CC reduction, clean up duplicate imports.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (including new edge case tests)
- [ ] CC below 20 for main function
- [ ] No behavioral changes verified
