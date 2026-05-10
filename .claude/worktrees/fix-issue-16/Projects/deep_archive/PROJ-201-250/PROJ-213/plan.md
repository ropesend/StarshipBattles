# PROJ-213: Build Queue Reversion Bug Fix

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-213` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-213 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Command Handler & Tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Complete
**Last Action:** Audit Cycle 1 PASSED - no issues found
**Next Action:** User verification via manual gameplay test
**Blockers:** None

## Overview
The build queue system regressed to instant "1 turn" completion behavior. The `AddToConstructionQueueCommandHandler` (PROJ-208) was creating queue items with empty `total_cost: {}`, causing the `ProductionEngine` to treat all items as free and complete them instantly. Fixed by loading design data and calculating actual costs in the handler.

## Goals
- Fix queue items being created with empty `total_cost`
- Restore tick-based continuous production (resources consumed per tick over multiple turns)
- Update tests to verify populated cost data

## Scope
**In:** Command handler cost calculation, test updates
**Out:** ProductionEngine changes (already correct), UI display changes (driven by engine data)

## Key Files
| Component | File Path |
|-----------|-----------|
| Command Handler (fixed) | `game/strategy/engine/command_handlers.py` |
| DesignCostCalculator (reused) | `game/strategy/services/design_cost_calculator.py` |
| DesignLibrary (reused) | `game/strategy/systems/design_library.py` |
| ProductionEngine (unchanged) | `game/strategy/engine/production_engine.py` |
| Tests (updated) | `tests/unit/strategy/engine/test_production_repro.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (13022 passed, 1 skipped)
- [x] Audit passed (Cycle 1 - no issues found)
- [ ] User verified
