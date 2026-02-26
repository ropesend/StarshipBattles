# PROJ-239: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-239` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-239 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verify & Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 02:15
**Active Phase:** 1 - Test Fortification
**Last Action:** Analysis complete, plan written
**Next Action:** Add edge case tests identified by safety analysis
**Blockers:** None

## Overview

Reduce cyclomatic complexity of `filter_ships` function from CC 36 to below 20 by extracting repetitive binary filter patterns into helper functions. The function filters ships based on 10+ boolean criteria (warp, spaceyard, cargo, special abilities, status) using a duplicated pattern that can be consolidated.

## Goals
- Reduce `filter_ships` CC from 36 to below 20
- Improve code readability and maintainability
- Add missing edge case test coverage
- Preserve all existing behavior (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - filter_ships function (lines 124-222)
- `tests/unit/ui/screens/test_fleet_report_filters.py` - add edge case tests

**Out:**
- Other functions in fleet_report_filters.py (calculate_fleet_stats, sort_ships)
- FleetListViewModel changes (interface stays stable)
- Other complexity targets

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py:124-222` |
| Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Caller | `game/ui/screens/fleet_report_view_model.py:215` |
| Constants | `game/ui/screens/fleet_data_source.py:46-52` |

## Phase Summaries

### Phase 1: Test Fortification
Add 4 missing edge case tests identified by safety analysis before any code changes. This ensures refactoring doesn't introduce regressions in untested paths.

### Phase 2: Extract Helpers
Extract 5 helper functions from filter_ships:
- `_passes_warp_filter` - warp capability binary filter
- `_passes_spaceyard_filter` - spaceyard binary filter
- `_passes_cargo_filter` - cargo binary filter
- `_passes_capability_filters` - special ability loop
- `_get_ship_status_filter_key` - status classification

### Phase 3: Verify & Cleanup
Run full test suite, verify CC reduction, cleanup any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Structure agent findings
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Dependency agent findings
- [findings/safety_analysis.md](findings/safety_analysis.md) - Safety agent findings

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC below 20 verified
- [ ] Audit passed
