# PROJ-201: Reduce complexity: FleetDataSource._get_column_value (CC 29)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-201` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-201 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract Complex Handlers | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Remaining Handlers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Implement Dispatch & Verify | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-27 04:15
**Active Phase:** Phase 1
**Last Action:** Analysis complete - plan ready for implementation
**Next Action:** Extract `_format_status(ship)` handler
**Blockers:** None

## Overview

Reduce cyclomatic complexity of `FleetDataSource._get_column_value` from CC=29 to below CC=20 by extracting handler methods for each column type. The function currently uses a 14-branch if-elif chain to format 19 different column types for the fleet report table.

## Goals
- Reduce `_get_column_value` CC from 29 to <5 (dispatch only)
- Extract 13 handler methods for column formatting
- Maintain all 30 existing tests passing
- Preserve all formatting behavior exactly

## Scope
**In:**
- Extract handler methods from `_get_column_value`
- Create dispatch dict for column routing
- Consolidate capability columns into single handler

**Out:**
- Changes to public interface (`get_cell_value`, `get_cell_image`)
- Test modifications (existing tests must pass as-is)
- Changes to column definitions or behavior

## Key Files
| Component | File Path |
|-----------|-----------|
| Target | `game/ui/screens/fleet_data_source.py` |
| Tests | `tests/unit/ui/screens/test_fleet_data_source.py` |
| Constants | `SPECIAL_CAPABILITY_COLUMNS` (lines 46-52) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/structure_analysis.md](findings/structure_analysis.md) - Control flow analysis
- [findings/dependency_analysis.md](findings/dependency_analysis.md) - Caller/dependency analysis
- [findings/safety_analysis.md](findings/safety_analysis.md) - Risk and coverage analysis

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] CC verified below 20
- [ ] User verified
