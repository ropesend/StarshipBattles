# PROJ-476: Facade read-path: tooling/editor screens (battle_setup, galaxy_test, race_setup) reader migration (follow-on from PROJ-472)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-476` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-476 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** Stub (deferred tail of PROJ-472)
**Last Action:** Stub created + scoped during PROJ-472 planning.
**Next Action:** Do NOT start until PROJ-472's guards land AND the live-UI scope (PROJ-475) is understood — tooling screens likely need different exemptions than the live strategy UI. Then plan per tool surface.
**Blockers:** **GATED on PROJ-472** (guards) and informed by PROJ-475 (live-vs-tooling boundary).

## Overview
Follow-on from **PROJ-472**. The tooling/editor/sandbox UI surfaces
(`battle_setup`, `galaxy_test`, `race_setup`, parts of `builder`) read
`game.strategy` types directly, but they are NOT live-gameplay strategy screens —
they construct/inspect config before a session exists or drive test/sandbox
flows. The consult flags these as likely to want **broader exemptions** than the
main strategy-screen boundary, so they are deliberately migrated last, in their
own project, after the live-UI policy (PROJ-472/475) is settled.

## Goals
- Decide per-surface whether each tooling screen needs facade migration, an
  expanded UI-safe allowlist entry, or an explicit documented exemption.
- Migrate or exempt the `battle_setup` (4 files), `galaxy_test` (3 files),
  `race_setup` (4 files), and relevant `builder` (3 files) readers under the
  PROJ-472 guards.
- Keep the guard allowlist honest: tooling exemptions are file+reason scoped, not
  blanket subpackage waivers.

## Scope
**In:** Tooling/editor/sandbox UI readers: `game/ui/screens/battle_setup/`,
`game/ui/screens/galaxy_test/`, `game/ui/screens/race_setup/`, tooling parts of
`game/ui/screens/builder/`.
**Out:** Live strategy-screen / render readers (PROJ-475); value/config allowlist
consolidation (PROJ-474); the build-queue cluster + session consumers (PROJ-472).

## Key Files
| Component | File Path |
|-----------|-----------|
| Battle setup screens (4) | `game/ui/screens/battle_setup/` |
| Galaxy test screens (3) | `game/ui/screens/galaxy_test/` |
| Race setup screens (4) | `game/ui/screens/race_setup/` |
| Builder tooling (3) | `game/ui/screens/builder/` |
| Guards (allowlist scope) | `tests/static_guards/test_facade_read_path_imports_guard.py`, `tests/static_guards/test_facade_read_path_session_guard.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
