# PROJ-488: Legacy removal — MASS_EARTH alias (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-488` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-488 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 25 callers + delete alias | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1
**Last Action:** Project created from `Reviews/results/2026-05-20_210635_legacy-audit/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
`game/strategy/data/planet_physics.py:24-25` declares `MASS_EARTH = EARTH_MASS  # Backward-compatible alias` where `EARTH_MASS` is the canonical name imported from `game.core.constants`. The verifier confirmed ~25 callers across `tests/`, `Tools/`, and diagnostics — none in active `game/` production code that cannot be cleanly migrated. Migrate all callers to `EARTH_MASS` and delete the alias.

## Goals
- Migrate all `MASS_EARTH` references to the canonical `EARTH_MASS`.
- Delete the `MASS_EARTH` alias declaration and its `# Backward-compatible alias` comment.

## Scope
**In:** `MASS_EARTH` declaration at `planet_physics.py:24-25` and all ~25 caller sites.
**Out:**
- `EARTH_MASS` itself (the canonical) — kept.
- The import chain into `planet_physics.py` from `game.core.constants` — kept (other constants flow through this module).
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-489, PROJ-490.

## Key Files
| Component | File Path |
|-----------|-----------|
| `MASS_EARTH` alias [EDIT] | `game/strategy/data/planet_physics.py` |
| ~25 caller sites [EDIT] | TBD by grep — primarily under `tests/`, `Tools/`, diagnostics modules |

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
