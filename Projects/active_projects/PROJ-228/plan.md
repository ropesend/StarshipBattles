# PROJ-228: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-228` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-228 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verify & Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:00
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing test cases for edge cases
**Blockers:** None

## Overview
Reduce the cyclomatic complexity of `filter_ships` function from 36 to below 20 by extracting helper functions for repeated filter patterns. The function implements 5 filter categories using a repeated binary filter pattern that can be abstracted into reusable helpers.

## Goals
- Reduce CC from 36 to below 20
- Extract reusable helper functions for binary filter pattern
- Preserve critical status priority chain invariant
- Maintain 100% backward compatibility (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- Test fortification for edge cases
- Helper function extraction

**Out:**
- Changes to function signature or return type
- Changes to `filter_state` dictionary keys
- Refactoring of `sort_ships` or `calculate_fleet_stats`
- UI changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py` |
| Constant | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Summaries

### Phase 1: Test Fortification
Add missing test cases identified by safety analysis before making any code changes. Tests for:
- Empty ship list edge case
- Status priority interactions (destroyed vs derelict)
- Missing filter_state keys defaulting to True
- Both sides of binary filter being False

### Phase 2: Extract Helpers
Extract helper functions to reduce complexity:
1. `_passes_binary_filter()` - Generic binary filter logic
2. `_passes_warp_filter()` - Warp capability check
3. `_passes_spaceyard_filter()` - Spaceyard check
4. `_passes_cargo_filter()` - Cargo check
5. `_passes_special_capability_filters()` - Special abilities loop
6. `_get_ship_status()` - Status determination
7. `_passes_status_filter()` - Status filter check

### Phase 3: Verify & Cleanup
- Run full test suite
- Verify CC is now below 20
- Clean up any redundant code
- Final commit

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
- [ ] User verified
