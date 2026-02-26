# PROJ-233: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-233` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-233 [phase]` before stopping
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
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - refactoring plan designed
**Next Action:** Add missing test coverage before any code changes
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of `filter_ships` function from CC 36 to below 20 by extracting helper functions. The function filters ships based on multiple criteria (warp capability, spaceyard, cargo, special abilities, status) using a repeated binary filter pattern that can be consolidated.

## Goals

- Reduce `filter_ships` CC from 36 to < 20
- Maintain 100% behavioral compatibility (pure refactoring)
- Improve code maintainability by extracting reusable helpers
- Add missing test coverage to ensure safe refactoring

## Scope

**In:**
- `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Test file `tests/unit/ui/screens/test_fleet_report_filters.py`
- Helper functions extracted within the same file

**Out:**
- `sort_ships` function (different complexity target)
- `calculate_fleet_stats` function
- Changes to function signature or public interface
- Changes to `FleetListViewModel` or other callers

## Key Files
| Component | File Path |
|-----------|-----------|
| Target function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Test file | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Data source | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Summary

### Phase 1: Test Fortification
Add missing test coverage identified by safety analysis. This is MANDATORY before any code changes.

**Tests to add:**
- Empty ships list handling
- Multiple filter combinations
- Partial/empty filter_state (defaults behavior)
- All filters disabled scenario
- 4 missing special capabilities (OpenWarpPoint, CloseWarpPoint, DestroyStar, CreateSphereWorld)
- Derelict/damaged mutual exclusivity

### Phase 2: Extract Helpers
Extract helper functions to reduce complexity:

1. `_passes_binary_filter()` - Generic binary filter logic
2. `_passes_capability_filters()` - Warp, spaceyard, cargo, special abilities
3. `_passes_status_filter()` - Status priority chain

### Phase 3: Simplify Main Function
Refactor `filter_ships` to use the extracted helpers:
- Replace inline filter logic with helper calls
- Convert to list comprehension
- Verify CC is below threshold

### Phase 4: Verify & Cleanup
- Run full test suite
- Verify CC reduction with `radon cc`
- Clean up any redundant code
- Update documentation if needed

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/](findings/) - Multi-agent review analysis files

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC verified below 20
- [ ] Audit passed
- [ ] User verified
