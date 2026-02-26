# PROJ-238: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-238` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-238 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:00
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan and checklists written
**Next Action:** Start Phase 1 - add edge case tests
**Blockers:** None

## Overview
Refactor the `filter_ships` function in `fleet_report_filters.py` to reduce its cyclomatic complexity from 36 to below 20. The function filters ships based on various capability and status filters, but uses repetitive patterns and complex control flow that can be simplified through helper extraction.

## Goals
- Reduce cyclomatic complexity from 36 to below 20
- Eliminate code duplication (binary filter pattern repeated 4 times)
- Improve readability through predicate composition
- Maintain exact behavioral equivalence (pure refactoring)

## Scope
**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Adding tests to cover identified gaps
- Extracting helper functions within the same file

**Out:**
- Changes to other functions in the file
- Changes to callers (`FleetListViewModel`)
- Interface changes (signature must remain compatible)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |

## Phase Overview

### Phase 1: Test Fortification
Add edge case tests identified by safety analysis before any code changes. These tests protect against regressions during refactoring.

### Phase 2: Extract Helpers
Extract four helper functions:
1. `_passes_binary_filter()` - Generic binary capability filter
2. `_get_ship_status()` - Status categorization with precedence
3. `_passes_capability_filters()` - Combined capability checks
4. `_passes_status_filter()` - Status filter using categorization

### Phase 3: Simplify Main Function
Rewrite `filter_ships` using the extracted helpers. Convert from explicit loop with continue statements to list comprehension with predicate composition.

### Phase 4: Verify & Cleanup
Run full test suite, verify CC is below threshold, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] Audit passed
