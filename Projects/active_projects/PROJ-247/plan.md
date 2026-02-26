# PROJ-247: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-247` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-247 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:45
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing test cases to establish safety net
**Blockers:** None

## Overview

Refactor the `filter_ships` function in `game/ui/screens/fleet_report_filters.py` from CC 36 to below 20 using predicate extraction. The function filters ships based on 20 filter state keys across 5 categories: warp, spaceyard, cargo, special capabilities, and status.

## Goals
- Reduce `filter_ships` cyclomatic complexity from 36 to below 20
- Extract reusable helper predicates for each filter category
- Share `_classify_ship_status` helper with `sort_ships` to eliminate duplication
- Maintain all existing behavior (pure refactoring)

## Scope
**In:**
- `filter_ships` function (lines 124-222)
- Status classification shared with `sort_ships` (lines 251-258)
- Test file `tests/unit/ui/screens/test_fleet_report_filters.py`

**Out:**
- `calculate_fleet_stats` function
- `sort_ships` function (beyond status helper extraction)
- UI layer changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Constants | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Descriptions

### Phase 1: Test Fortification
Add missing test coverage before any code changes. Safety analysis identified 5 gaps:
- Empty ship list handling
- All filters disabled behavior
- Status priority (derelict vs damaged)
- Combined multi-category filters
- Partial filter_state with missing keys

### Phase 2: Extract Helpers
Extract filter logic into focused helper functions:
- `_passes_binary_filter()` - Generic binary filter logic
- `_passes_warp_filter()` - Warp capability check
- `_passes_spaceyard_filter()` - Spaceyard capability check
- `_passes_cargo_filter()` - Cargo presence check
- `_passes_special_capability_filters()` - Loop over SPECIAL_CAPABILITY_COLUMNS
- `_classify_ship_status()` - Status classification (shared with sort_ships)
- `_passes_status_filter()` - Status filter using classification

### Phase 3: Simplify Main Function
Refactor `filter_ships` to use extracted predicates:
- Replace inline logic with predicate calls
- Convert to list comprehension
- Update `sort_ships` to use shared `_classify_ship_status`

### Phase 4: Verify & Cleanup
- Run full test suite
- Verify CC is below 20
- Remove any dead code
- Final review

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Multi-agent analysis reports

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC of `filter_ships` < 20
- [ ] Audit passed
