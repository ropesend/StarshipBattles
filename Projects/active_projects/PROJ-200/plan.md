# PROJ-200: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-200` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-200 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verify & Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-27 03:30
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete, plan created
**Next Action:** Add missing test coverage for filter combinations
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of `filter_ships` in `game/ui/screens/fleet_report_filters.py` from 36 to below 20. The function filters ships by 5 categories (warp, spaceyard, cargo, special capabilities, status) using repetitive patterns. Refactor by extracting each filter category into a predicate helper function.

## Goals
- Reduce `filter_ships` CC from 36 to < 20
- Maintain 100% backward compatibility (same inputs → same outputs)
- Improve code readability and maintainability
- Add missing test coverage for edge cases

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- `tests/unit/ui/screens/test_fleet_report_filters.py` - add missing tests

**Out:**
- Other functions in the file (`calculate_fleet_stats`, `sort_ships`)
- UI layer changes
- Filter state key naming changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Filter state producer | `game/ui/screens/fleet_report_view_model.py` |
| Special capability columns | `game/ui/screens/fleet_data_source.py` |

## Phase Descriptions

### Phase 1: Test Fortification
Add missing test coverage before any code changes. Safety analysis identified gaps:
- No multi-filter combination tests
- Only 1 of 5 special capabilities tested
- No empty filter_state test
- No "hide all" scenario test

### Phase 2: Extract Helpers
Extract each filter category into a predicate helper function:
1. `_should_exclude_by_warp()`
2. `_should_exclude_by_spaceyard()`
3. `_should_exclude_by_cargo()`
4. `_should_exclude_by_special_capabilities()`
5. `_should_exclude_by_status()`

Refactor main `filter_ships` to use these helpers.

### Phase 3: Verify & Cleanup
- Run full test suite
- Verify CC is below threshold
- Clean up any redundant code

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure agent findings
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency agent findings
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety agent findings

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC verified below 20
- [ ] User verified
