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
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Issues | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** COMPLETE
**Last Action:** Audit cycle 1 passed - all 13 tasks verified
**Next Action:** User verification required
**Blockers:** None

### Phase 1 Summary:
- **Task 1.1-1.2:** Dead mixins (physics.py, combat.py) already deleted
- **Task 1.3:** ShipControllableAdapter documented - deferred to future PROJ
- **Task 1.4:** Module-level side effect fixed with lazy initialization
- **Task 1.5:** GameSession legacy params fixed with deprecation warnings + test updates
- **Task 1.6:** Unused ValidationResult import removed from ship.py
- **Tests:** 4563 passed, 1 skipped

### Phase 2 Summary:
- **Task 2.1:** Deleted Marked_For_Deletion folder (103 files, 45MB)
- **Task 2.2:** Deleted ship_theme.py deprecation shim
- **Task 2.3:** Removed SHIP_CLASSES alias, updated builder/main.py
- **Task 2.4:** Extracted _get_legacy_crew_requirement() and _get_total_crew_requirement() helpers
- **Task 2.5:** Added warnings for old design metadata format
- **Task 2.6:** Removed dead ValidationResult re-export
- **Task 2.7:** Fixed TYPE_CHECKING import to use canonical path
- **Tests:** 4563 passed, 1 skipped

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
- [x] All phase checklists complete
- [x] All tests passing (4563 passed, 1 skipped)
- [x] Audit passed (Cycle 1 - 2026-01-27)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | No significant issues | PASSED |

### Audit Notes
- All 13 tasks verified via grep/glob/file checks
- Lazy initialization pattern investigated - no integration issues
- Task 1.3 deferral investigated - justified (design issue, not cleanup)
- Minor observation: Task 1.3 recommends future PROJ but none created yet

### Deferred Items
| Item | Reason | Follow-up |
|------|--------|-----------|
| LPA-01: ShipControllableAdapter | Design refactor (~17 methods), not cleanup | Create PROJ-23 for IControllable Interface Migration |
