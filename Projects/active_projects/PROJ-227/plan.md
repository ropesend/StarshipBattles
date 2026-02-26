# PROJ-227: Reduce complexity: filter_ships (CC 36)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-227` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-227 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Fortification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Helpers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simplify Main Function | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Verify & Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-26 01:00
**Active Phase:** Phase 1 - Test Fortification
**Last Action:** Analysis complete - plan designed
**Next Action:** Add missing edge case tests before refactoring
**Blockers:** None

## Overview

Reduce the cyclomatic complexity of the `filter_ships` function from CC=36 to below CC=20 by extracting repeated filter patterns into focused helper functions. The function handles 22+ filter flags across 6 categories (warp, spaceyard, cargo, special capabilities, and 4 status types).

## Goals
- Reduce `filter_ships` CC from 36 to < 20 (target: ~8)
- Extract reusable `_passes_binary_filter` helper for all has/lacks filters
- Extract `_get_ship_status` to separate categorization from filtering
- Preserve all 6 critical invariants identified by safety analysis
- Maintain 100% backward compatibility (pure refactoring)

## Scope
**In:**
- `game/ui/screens/fleet_report_filters.py` - `filter_ships` function (lines 124-222)
- `tests/unit/ui/screens/test_fleet_report_filters.py` - add missing edge case tests

**Out:**
- `calculate_fleet_stats` function (same file, already clean)
- `sort_ships` function (same file, not targeted)
- `FleetListViewModel` changes (caller stays unchanged)

## Key Files
| Component | File Path |
|-----------|-----------|
| Target Function | `game/ui/screens/fleet_report_filters.py` |
| Direct Tests | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| Integration Tests | `tests/unit/ui/test_fleet_list_view_model.py` |
| Data Source | `game/ui/screens/fleet_data_source.py` (SPECIAL_CAPABILITY_COLUMNS) |

## Phase Summaries

### Phase 1: Test Fortification
Add missing edge case tests identified by safety analysis before making any code changes. This ensures refactoring safety.

### Phase 2: Extract Helpers
Extract the core helper functions:
- `_passes_binary_filter` - reusable for all has/lacks filters
- `_get_ship_status` - status categorization
- `_passes_capability_filters` - special capability loop

### Phase 3: Simplify Main Function
Refactor `filter_ships` to use the extracted helpers, replacing inline code with helper calls.

### Phase 4: Verify & Cleanup
Run complexity analysis to verify CC < 20, run full test suite, clean up any redundant code.

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller and test analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Invariants and risks

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC of `filter_ships` < 20
- [ ] No helper function exceeds CC=10
- [ ] Audit passed
