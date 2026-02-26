# PROJ-237: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-237` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-237 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:15
**Active Phase:** 1 - Test Fortification
**Last Action:** Analysis complete, plan written
**Next Action:** Add 6 fortification tests in `test_fleet_report_filters.py`
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` from 36 to below 20 by extracting helper functions for repeated filter patterns. The function applies 6 filter categories (warp, spaceyard, cargo, special capabilities, status) using a repeated binary show/no-show pattern.

## Goals
- Reduce CC from 36 to below 20
- Extract 4-5 helper functions for repeated patterns
- Add 6 fortification tests before refactoring
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function
- `tests/unit/ui/screens/test_fleet_report_filters.py` - Add fortification tests

**Out:**
- `calculate_fleet_stats` function (not targeted)
- `sort_ships` function (not targeted)
- FleetCapabilityCalculator or ShipStatsCalculator (external dependencies)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Imported constant | `game/ui/screens/fleet_data_source.py:SPECIAL_CAPABILITY_COLUMNS` |

## Phase Summaries

### Phase 1: Test Fortification
Add 6 targeted tests to cover edge cases and invariants before any code changes. This ensures safe refactoring.

### Phase 2: Extract Helpers
Extract 4 helper functions:
1. `_passes_binary_filter()` - Generic show/no-show pattern
2. `_passes_special_capability_filters()` - Replace loop with flag
3. `_get_ship_status_category()` - Status priority logic
4. `_passes_status_filter()` - Status filter using category

### Phase 3: Simplify Main Function
Refactor `filter_ships()` to use the extracted helpers, reducing main function to ~25-30 lines.

### Phase 4: Verification
Run full test suite, verify CC is below 20, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller and interface analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk assessment

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] User verified
