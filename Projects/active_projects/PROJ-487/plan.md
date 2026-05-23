# PROJ-487: Legacy removal — fuel wrappers to consumable API (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-487` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-487 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate `resupply_engine.py` callers to generic consumable API | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate test callers + delete deprecated wrappers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1
**Last Action:** Project created from `Reviews/results/2026-05-20_210635_legacy-audit/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
`PlanetaryFacility` carries four fuel-specific wrappers marked `# Deprecated fuel-specific wrappers (F-A-012)` at `game/strategy/data/planetary_facility.py:209-221`: `get_fuel_storage`, `get_max_fuel_storage`, `add_fuel`, `withdraw_fuel`. They remain in active production use via `game/strategy/engine/resupply_engine.py:135, 208, 293` (`add_fuel`, `get_fuel_storage`, `withdraw_fuel`) and are exercised by 56 test call sites. The deprecation marker references ticket F-A-012 but provides no linked project or removal timeline.

This project migrates the single production consumer to the generic `*_consumable` API, migrates the test suite, then deletes the four wrappers.

## Goals
- Phase 1: Migrate the 3 call sites in `resupply_engine.py` from the fuel-specific wrappers to the generic consumable API. Production behavior unchanged.
- Phase 2: Migrate the ~56 test call sites; delete the four fuel wrappers (~16 LOC).

## Scope
**In:** the four deprecated wrappers and their production + test callers.
**Out:**
- The generic consumable API itself — assumed already present (the deprecation marker implies it). Confirm during Phase 1.
- Other `PlanetaryFacility` methods — unaffected.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-485, PROJ-486, PROJ-488, PROJ-489, PROJ-490.

## Key Files
| Component | File Path |
|-----------|-----------|
| 4 fuel wrappers [EDIT] | `game/strategy/data/planetary_facility.py` |
| 3 production callers [EDIT] | `game/strategy/engine/resupply_engine.py` |
| ~56 test callers [EDIT] | `tests/unit/strategy/data/test_facility_resource_tracking.py` and related |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/verification_report.md](findings/verification_report.md)
- [findings/source_audit.md](findings/source_audit.md)
- [findings/bundling_decisions.md](findings/bundling_decisions.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
