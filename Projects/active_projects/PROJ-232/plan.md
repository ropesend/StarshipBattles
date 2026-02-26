# PROJ-232: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-232` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-232 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helper Functions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:15
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan written
**Next Action:** Add missing edge case tests
**Blockers:** None

## Overview
Refactor `filter_ships` function in `game/ui/screens/fleet_report_filters.py` to reduce cyclomatic complexity from 36 to below 20. The function applies multiple binary filters (warp, spaceyard, cargo, special capabilities) and status filters (destroyed, derelict, damaged, undamaged) to filter a list of ships.

The refactoring strategy extracts filter predicates into separate helper functions while preserving the critical status filter hierarchy (destroyed -> derelict -> damaged -> undamaged).

## Goals
- Reduce `filter_ships` CC from 36 to below 15
- Extract 4-5 helper functions with CC < 8 each
- Add missing edge case tests before refactoring
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - target file
- `tests/unit/ui/screens/test_fleet_report_filters.py` - test file
- Helper function extraction only

**Out:**
- No changes to `filter_ships` interface/signature
- No changes to filter_state key names
- No changes to FleetListViewModel
- No architectural changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` (lines 124-222) |
| Test File | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Filter State Source | `game/ui/screens/fleet_report_view_model.py` |
| Special Capabilities | `game/ui/screens/fleet_data_source.py` |
| Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |

## Phase Summaries

### Phase 1: Test Fortification
Add missing edge case tests identified by safety analysis before any code changes. This ensures we have a safety net for the refactoring.

**Missing tests to add:**
- Empty ship list handling
- Derelict not matched as "damaged" (hierarchy test)
- `cargo_contents = None` handling
- All filters disabled edge case

### Phase 2: Extract Helper Functions
Extract filter predicates into separate private functions:
1. `_passes_binary_filter()` - Generic binary filter checker
2. `_passes_warp_filter()` - Warp capability filter
3. `_passes_spaceyard_filter()` - Spaceyard capability filter
4. `_passes_cargo_filter()` - Cargo contents filter
5. `_passes_special_capabilities_filter()` - Special abilities filter
6. `_get_ship_status_category()` - Status determination
7. `_passes_status_filter()` - Status filter check

### Phase 3: Simplify Main Function
Refactor `filter_ships` to use extracted helpers:
- Convert to list comprehension or simplified loop
- Move late imports to function top
- Reduce main function CC to target

### Phase 4: Verify & Cleanup
- Run full test suite
- Verify CC reduction with radon
- Clean up any redundant code

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC reduced below 20
- [ ] Audit passed
- [ ] User verified
