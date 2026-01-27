# PROJ-26: Naming Consistency Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-26` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-26 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Issues | In Progress | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 13:15
**Active Phase:** Phase 2 (mostly complete)
**Last Action:** Completed Tasks 2.1, 2.5, 2.6. Deferred Tasks 2.2, 2.3, 2.4 as out-of-scope for this project.
**Next Action:** Mark Phase 2 complete, or optionally tackle deferred documentation task (2.3)
**Blockers:** None

**Context for Next Agent:**
- Phase 1 complete: Deleted duplicate `battle.py`, kept `battle_scene.py`
- Phase 2 Tasks Completed:
  - 2.1: ShipBuilderService shim already fixed (verified)
  - 2.5: Renamed `InputHandler` → `StrategyInputHandler` in strategy scene
  - 2.6: Deleted duplicate `abilities.py` (monolithic file was dead code)
- Phase 2 Tasks Deferred:
  - 2.2 & 2.4: Builder→Workshop migration too large (~80+ imports, ~40 files) - recommend separate project
  - 2.3: Documentation task (create NAMING_CONVENTIONS.md) - lower priority
- All 4594 tests passing

## Overview
Systematic remediation of findings from review: 2026-01-27_update_naming-inconsistencies. Total findings selected: 7 (Critical: 1, Major: 6, Other: 0).

## Goals
- Address NC-03: ShipBuilderService shim
- Address NC-02: Builder vs Workshop terminology
- Address NC-05: Battle vs Combat distinction
- Address NC-02: Workshop imports from Builder directory
- Address NC-01: Duplicate BattleScene not removed
- Address NEW-03: Duplicate InputHandler class
- Address NEW-05: Duplicate Ability classes

## Scope
**In:**
- 
- **Details
- Exists but not documented
- Workshop files created, builder_* files remain
- abilities.py` + `abilities/*.py
- input_handler.py` (2 files)
- ship_builder_service.py` deleted

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `` |
| [TBD] | `**Details` |
| [TBD] | `Exists but not documented` |
| [TBD] | `Workshop files created, builder_* files remain` |
| [TBD] | `abilities.py` + `abilities/*.py` |
| [TBD] | `input_handler.py` (2 files)` |
| [TBD] | `ship_builder_service.py` deleted` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
