# PROJ-22: Legacy Cleanup Phase 2

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-22` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-22 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Issues | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 08:06
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-01-27_general_legacy-cleanup-verification. Total findings selected: 13 (Critical: 6, Major: 7, Other: 0).

## Goals
- Address DC-01: Marked_For_Deletion folder (103 files, 45MB)
- Address AR-01: Dead physics mixin (102 lines)
- Address AR-02: Dead combat mixin (437 lines)
- Address LPA-01: ShipControllableAdapter blocks migration
- Address LPA-02: ship_theme.py shim (0 users)
- Address LPA-03: SHIP_CLASSES alias (1 user)
- Address LDF-01: Module-level side effect
- Address LDF-02: GameSession legacy params
- Address LDF-03: CrewCapacity fallback (3x)
- Address LDF-04: Design metadata dual format
- ...and 3 more findings

## Scope
**In:**
- Root
- controllable.py
- design_metadata.py
- entities/mixins/combat.py
- entities/mixins/physics.py
- game_session.py
- ship.py
- ship_theme.py
- stats_config.py
- system.py
- validation/__init__.py
- vehicle_design_service.py

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Root` |
| [TBD] | `controllable.py` |
| [TBD] | `design_metadata.py` |
| [TBD] | `entities/mixins/combat.py` |
| [TBD] | `entities/mixins/physics.py` |
| [TBD] | `game_session.py` |
| [TBD] | `ship.py` |
| [TBD] | `ship_theme.py` |
| [TBD] | `stats_config.py` |
| [TBD] | `system.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
