# PROJ-245: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-245` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-245 [phase]` before stopping
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
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan and checklists created
**Next Action:** Add edge case tests before refactoring
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` from 36 to below 20 by extracting repeated filter patterns into named helper predicates. The function filters ships based on multiple criteria (warp capability, spaceyard, cargo, special abilities, status) using a repeated binary filter pattern. Extracting each filter into a dedicated helper function will reduce complexity while improving testability and readability.

## Goals
- Reduce `filter_ships` cyclomatic complexity from 36 to below 20
- Maintain 100% behavioral compatibility (pure refactoring)
- Improve code readability with named helper functions
- Increase test coverage with edge case tests

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - the `filter_ships` function
- `tests/unit/ui/screens/test_fleet_report_filters.py` - related tests

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- Callers of `filter_ships` (only 1: `FleetListViewModel._refresh()`)
- Changes to the filter_state dict structure or caller

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Single Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Data Source | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Summaries

### Phase 1: Test Fortification
Add tests for edge cases identified during safety analysis before making any code changes. This ensures any behavioral changes during refactoring are caught immediately.

### Phase 2: Extract Filter Helpers
Extract each binary filter pattern into a named predicate function:
- `_passes_warp_filter()`
- `_passes_spaceyard_filter()`
- `_passes_cargo_filter()`
- `_passes_special_capability_filter()`
- `_passes_status_filter()`

### Phase 3: Simplify Main Function
Convert the main loop to use the extracted predicates, transforming the 99-line function into a simple list comprehension with filter predicate calls.

### Phase 4: Verify & Cleanup
Run full test suite, verify CC is below threshold, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Multi-agent analysis reports

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] User verified
