# PROJ-33: UI Screens: ViewModel Layer Introduction

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-33` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-33 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit Fixes (Cycle 1) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Audit complete
**Last Action:** Audit Cycle 2 passed with no significant issues
**Next Action:** User verification required
**Blockers:** None
**Context:**
- Audit Cycle 2 verified all Phase 1 and Phase 2 fixes are complete and correct
- All direct Ship mutations in DesignWorkshopGUI now go through ViewModel methods:
  - `set_ship_name()`, `set_ship_theme()`, `set_ship_ai_strategy()`
  - `change_ship_class()` (delegates to service)
- All 18 ViewModel tests pass (6 for property setters)
- All 472 UI tests pass
- All 4711 project tests pass
- BuilderSceneGUI (legacy) is out of scope - not used in main app

## Overview
Systematic remediation of findings from review: 2026-01-27_general_self-contained-systems. Total findings selected: 1 (Critical: 1, Major: 0, Other: 0).

## Goals
- Address UI-01: Direct entity mutation by screens

## Scope
**In:**
- Complex

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| WorkshopViewModel | `game/ui/screens/workshop_viewmodel.py` |
| DesignWorkshopGUI | `game/ui/screens/workshop_screen.py` |
| WorkshopEventRouter | `game/ui/screens/workshop_event_router.py` |
| VehicleDesignService | `game/simulation/services/vehicle_design_service.py` |
| ViewModel Tests | `tests/unit/builder/test_builder_viewmodel.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing
- [x] Audit passed (Cycle 2 - no significant issues)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | 2 major issues: direct mutations in workshop_event_router.py | Added Phase 2 for fixes |
| 2 | 2026-01-27 | No significant issues | PASSED |
