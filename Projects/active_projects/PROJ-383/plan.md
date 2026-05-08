# PROJ-383: Legacy removal — command_handlers.py shim eradication (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-383` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-383 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate callers + delete shim | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Eradicates `game/strategy/engine/command_handlers.py` — a transitional re-export shim explicitly marked "this shim is **transitional**" in its own docstring. Violates CLAUDE.md Rule 3 ("Root Cause Fixes — no compatibility shims"). Verified: 6 production import sites + 25 test import sites must be migrated to `game.strategy.engine.handlers/` before the shim file can be deleted (82 LOC).

## Goals
- Migrate all 6 production callers to import directly from `game.strategy.engine.handlers/`.
- Migrate all 25 test callers in the same change.
- Delete `game/strategy/engine/command_handlers.py` (whole-file deletion, 82 LOC).

## Scope
**In:** LEG-01-005 (the shim file itself), LEG-01-015 (4 imports in `planet_command_handlers.py`), LEG-01-016 (1 import in `superweapon_command_handlers.py`), LEG-01-018 (1 import in `game_session.py`).
**Out:** Other clusters from the same audit (siblings PROJ-384..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Shim file `[DELETE]` | `game/strategy/engine/command_handlers.py` |
| Production caller | `game/strategy/engine/planet_command_handlers.py` |
| Production caller | `game/strategy/engine/superweapon_command_handlers.py` |
| Production caller | `game/strategy/engine/game_session.py` |
| Canonical target | `game/strategy/engine/handlers/__init__.py` |
| Canonical target | `game/strategy/engine/handlers/base.py` |
| Test imports | `tests/` (25 sites — see [manifest.md](manifest.md)) |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining imports of `game.strategy.engine.command_handlers` (`grep -rn "from game.strategy.engine.command_handlers" .`)
- [ ] `command_handlers.py` file is gone
- [ ] User verified
