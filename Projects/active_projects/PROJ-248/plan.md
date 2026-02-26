# PROJ-248: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-248` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-248 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26
**Active Phase:** Phase 1
**Last Action:** Analysis complete - refactoring plan designed
**Next Action:** Add missing test cases before any code changes
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` function from 36 to below 20 by extracting repeated filter patterns into helper predicates. The function filters ships based on multiple boolean criteria (warp capability, spaceyard, cargo, special abilities, status). The same binary filter pattern is repeated 4 times and can be extracted. Status checks must preserve their ordering invariant.

## Goals
- Reduce `filter_ships` CC from 36 to below 20
- Eliminate repeated binary filter pattern (appears 4 times)
- Remove `_skip` flag anti-pattern
- Improve readability with named predicates
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- `tests/unit/ui/screens/test_fleet_report_filters.py` - Add missing test coverage

**Out:**
- Other functions in same file (`calculate_fleet_stats`, `sort_ships`)
- `FleetListViewModel` changes (interface stays same)
- Any behavioral changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py` |
| Dependency | `game/strategy/data/fleet_capability_calculator.py` |
| Dependency | `game/strategy/services/ship_stats_calculator.py` |

## Phase Summaries

### Phase 1: Test Fortification
Add 5 critical missing test cases identified by safety analysis:
- Empty ships list
- Empty filter_state dictionary
- All filters disabled returns empty
- Destroyed ship not matched as derelict (ordering)
- Derelict ship not matched as damaged (ordering)

### Phase 2: Extract Helpers
Extract repeated patterns into helper functions:
- `_passes_binary_filter()` - generic utility
- `_passes_warp_filter()` - warp capability check
- `_passes_spaceyard_filter()` - spaceyard check
- `_passes_cargo_filter()` - cargo check
- `_passes_special_capability_filters()` - special abilities loop
- `_passes_status_filter()` - status cascade (ORDER CRITICAL)

### Phase 3: Simplify Main Function
- Create `_passes_all_filters()` composition function
- Convert main loop to list comprehension
- Remove `_skip` flag pattern
- Clean up redundant code

### Phase 4: Verify & Cleanup
- Run full test suite
- Measure final CC (must be below 20)
- Clean up any unused imports
- Final review

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
