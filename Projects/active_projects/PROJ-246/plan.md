# PROJ-246: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-246` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-246 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verify & Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:30
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Start Phase 1 - Add safety tests before refactoring
**Blockers:** None

## Overview
Refactor the `filter_ships` function in `fleet_report_filters.py` to reduce its cyclomatic complexity from 36 (Grade F) to below 20. The function applies multiple binary filter patterns that can be extracted into well-named helper functions, transforming a 98-line function with nested conditionals into a clean 20-line main loop.

## Goals
- Reduce `filter_ships` cyclomatic complexity from 36 to < 20 (expect ~7)
- Improve code readability and maintainability
- Preserve exact behavior (pure refactoring, no functional changes)
- Maintain all 19+ existing tests passing

## Scope
**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Adding helper functions in the same file
- Adding safety tests for identified coverage gaps

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- Changing the function's public interface
- Modifying callers (`FleetListViewModel`)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` (lines 124-222) |
| Main Caller | `game/ui/screens/fleet_report_view_model.py` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and refactoring strategy
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller and interface analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk and test coverage analysis

## Phase Summary

### Phase 1: Test Fortification
Add safety tests for identified coverage gaps before any code changes:
- Empty input list test
- Empty filter state test
- Status priority test (derelict vs damaged)
- Combined filter interaction test

### Phase 2: Extract Helper Functions
Extract filter logic into private helper functions:
- `_check_binary_filter()` - Generic binary filter pattern
- `_passes_warp_filter()` - Warp capability check
- `_passes_spaceyard_filter()` - Spaceyard check
- `_passes_cargo_filter()` - Cargo check
- `_passes_special_capability_filters()` - Special capabilities loop
- `_get_ship_status()` - Status classification
- `_passes_status_filter()` - Status filter check

### Phase 3: Verify & Cleanup
- Measure final complexity (target: CC < 20)
- Run full test suite
- Code review and cleanup
- Update documentation

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC reduced below 20
- [ ] Audit passed
- [ ] User verified
