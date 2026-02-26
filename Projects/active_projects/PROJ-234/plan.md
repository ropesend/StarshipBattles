# PROJ-234: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-234` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-234 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helper Functions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:30
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan created
**Next Action:** Add edge case tests per phase_1_checklist.md
**Blockers:** None

## Overview

Refactor the `filter_ships` function in `game/ui/screens/fleet_report_filters.py` to reduce its cyclomatic complexity from 36 to below 20. The function filters ships based on multiple filter categories (damage status, warp capability, spaceyard, cargo, special abilities). The complexity is additive (independent filters) rather than tangled, making it a good candidate for extraction into helper predicates.

## Goals
- Reduce `filter_ships` CC from 36 to < 20 (target: ~6-10)
- Extract reusable helper functions for filter patterns
- Preserve all existing behavior (pure refactoring)
- Improve code readability and maintainability

## Scope
**In:**
- `filter_ships` function (lines 124-222)
- Adding edge case tests before refactoring
- Extracting helper predicate functions
- Cleaning up late imports

**Out:**
- Changes to `calculate_fleet_stats` or `sort_ships`
- Changes to external callers (`FleetListViewModel`)
- Changes to test infrastructure or fixtures

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py` |
| Capability Columns | `game/ui/screens/fleet_data_source.py` |

## Phase Summaries

### Phase 1: Test Fortification
Add edge case tests identified by safety analysis before making any code changes. This ensures regression safety.

### Phase 2: Extract Helper Functions
Create helper predicate functions for each filter category:
- `_passes_binary_filter()` - generic binary filter pattern
- `_passes_warp_filter()` - warp capability
- `_passes_spaceyard_filter()` - spaceyard capability
- `_passes_cargo_filter()` - cargo presence
- `_passes_special_capability_filters()` - special abilities
- `_passes_status_filter()` - damage status

### Phase 3: Refactor Main Function
Refactor `filter_ships` to use the extracted helpers, converting to a list comprehension.

### Phase 4: Verify & Cleanup
Run full test suite, verify CC is below threshold, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure review
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency review
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] Audit passed
