# PROJ-241: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-241` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-241 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Filter Predicates | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:15
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing test coverage (6 scenarios)
**Blockers:** None

## Overview

Refactor the `filter_ships` function in `fleet_report_filters.py` to reduce cyclomatic complexity from 36 to below 20. The function applies 6 independent filter categories to ships. The complexity stems from a regular, repeating binary filter pattern that can be extracted into predicate helper functions.

## Goals
- Reduce `filter_ships` CC from 36 to below 20
- Maintain all existing behavior (pure refactoring)
- Improve code readability and maintainability
- Add test coverage for identified gaps

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function
- `tests/unit/ui/screens/test_fleet_report_filters.py` - add missing tests

**Out:**
- Other functions in the same file (`calculate_fleet_stats`, `sort_ships`)
- `FleetListViewModel` or other callers
- Any behavioral changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| View Model (caller) | `game/ui/screens/fleet_report_view_model.py` |
| Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |

## Phase Summary

### Phase 1: Test Fortification
Add 6 missing test scenarios identified by safety analysis before any code changes.

### Phase 2: Extract Filter Predicates
Create helper functions for each filter category:
- `_passes_binary_filter()` - universal binary filter logic
- `_classify_ship_status()` - ship status classification
- `_passes_warp_filter()` - warp capability filter
- `_passes_spaceyard_filter()` - spaceyard filter
- `_passes_cargo_filter()` - cargo filter
- `_passes_special_filters()` - special ability filters
- `_passes_status_filter()` - status filter

### Phase 3: Refactor Main Function
Replace `filter_ships` implementation with list comprehension using predicates.

### Phase 4: Verify & Cleanup
Run full test suite, verify CC reduction, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] `filter_ships` CC below 20
- [ ] No behavioral changes (same outputs for same inputs)
