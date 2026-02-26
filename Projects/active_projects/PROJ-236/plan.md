# PROJ-236: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-236` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-236 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Status Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Capability Helpers | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete, plan written
**Next Action:** Add 6 safety tests to test_fleet_report_filters.py
**Blockers:** None

## Overview
Refactor the `filter_ships` function in `fleet_report_filters.py` to reduce its cyclomatic complexity from 36 to below 20. The function filters ships based on 20 boolean filter keys across 4 categories (status, warp, spaceyard/cargo, special capabilities). The refactoring extracts repeated patterns into helper functions and replaces the cascading status checks with a status classifier.

## Goals
- Reduce `filter_ships` CC from 36 to below 20
- Maintain all existing behavior (pure refactoring)
- Improve code readability and maintainability
- Add safety tests for edge cases before refactoring

## Scope
**In:**
- `filter_ships` function (lines 124-222)
- Adding safety tests in `test_fleet_report_filters.py`
- Extracting private helper functions in same file

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- Resolving circular import issues (keep late import pattern)
- Changes to `FleetListViewModel` or other callers

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` |
| Unit Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py` |
| Data Source | `game/ui/screens/fleet_data_source.py` |

## Phase Summaries

### Phase 1: Test Fortification
Add 6 safety tests identified by safety analysis BEFORE any code changes. These tests document expected behavior and will catch regressions during refactoring.

### Phase 2: Extract Status Helpers
Extract `_get_ship_status()` classifier and `_passes_status_filter()` to replace the 25-line cascading status check. Expected CC reduction: ~8 points.

### Phase 3: Extract Capability Helpers
Extract `_passes_binary_filter()`, `_passes_capability_filters()`, and `_passes_special_capability_filters()`. Refactor main function to use list comprehension with predicates. Expected CC reduction: ~20 points.

### Phase 4: Verify & Cleanup
Verify CC is below 20, run full test suite, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Multi-agent analysis reports

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] Audit passed
