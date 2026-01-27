# PROJ-29: Simulation: Ship Decoupling

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-29` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-29 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Issues | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 14:30
**Active Phase:** Phase 2
**Last Action:** Completed Phase 1 - Component decoupling implemented
**Next Action:** Begin Phase 2 - Address SIM-03 BattleController concerns

**Phase 1 Summary:**
- Added context parameter to `Component.get_resource_cost()` and `Component.recalculate_stats()`
- Added resources parameter to `ResourceConsumption.update()`, `check_and_consume()`, `check_available()`
- Components can now operate without ship reference when context/resources are provided
- All existing code still works (backward compatible)
- 9 new tests added, 819 tests pass

**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-01-27_general_self-contained-systems. Total findings selected: 2 (Critical: 1, Major: 1, Other: 0).

## Goals
- ~~Address SIM-01: Bidirectional Ship coupling~~ (DONE)
- Address SIM-03: BattleController handles too many concerns

## Scope
**In:**
- Component.ship decoupling (Complex) - DONE
- BattleController refactoring (Medium)

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| Component | `game/simulation/components/component.py` |
| ResourceConsumption | `game/simulation/components/abilities/resources.py` |
| Tests | `tests/unit/simulation/test_component_decoupling.py` |
| BattleController | `game/simulation/battle_controller.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] Phase 1 checklist complete
- [ ] Phase 2 checklist complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
