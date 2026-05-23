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
| 1. Migrate 25 callers + delete alias | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All 2 phases complete
**Last Action:** Phase 1 complete — migrated 67 `MASS_EARTH` references across 11 Python files to canonical `EARTH_MASS` from `game.core.constants`, deleted the alias declaration (and its now-unused import) in `game/strategy/data/planet_physics.py`, updated the static-guard fixture entry at `tests/static_guards/test_facade_read_path_imports_guard.py:208` from `(system_mode.py, game.strategy.data.planet_physics, MASS_EARTH)` to `(system_mode.py, game.core.constants, EARTH_MASS)`. Targeted test suite (471 tests across planet_physics / planet_gen / planet_atmosphere / static_guards / integration) passes in 3.94s. Not committed per project policy.
**Next Action:** Project ready for audit + close. (Note: `pytest tests/ --testmon` errored out with an environment-level `path is on mount '\\\\.\\nul'` ValueError in testmon itself — unrelated to this change, ran targeted suite without `--testmon` instead.)
**Blockers:** None

## Overview
`game/strategy/data/planet_physics.py:24-25` declares `MASS_EARTH = EARTH_MASS  # Backward-compatible alias` where `EARTH_MASS` is the canonical name imported from `game.core.constants`. A 2026-05-22 re-verification (post-merge `67116932d`) found **~67 references across 12 files** — substantially more than the original audit's "~25" estimate. The split is: 3 production `game/` callers (`game/strategy/data/planet_atmosphere.py`, `game/strategy/data/planet_gen_surface.py`, `game/ui/screens/galaxy_test/system_mode.py`), plus `tests/`, `Tools/`, and diagnostics. All are cleanly migratable name-rebindings. Migrate all callers to `EARTH_MASS` and delete the alias. The Phase 1 deletion must also update the static-guard fixture entry at `tests/static_guards/test_facade_read_path_imports_guard.py:208` which enshrines `MASS_EARTH` as the canonical import for `system_mode.py` — change it to `EARTH_MASS`.

## Goals
- Migrate all `MASS_EARTH` references to the canonical `EARTH_MASS`.
- Delete the `MASS_EARTH` alias declaration and its `# Backward-compatible alias` comment.

## Scope
**In:** `MASS_EARTH` declaration at `planet_physics.py:24-25`, all ~67 caller sites across 12 files, and the static-guard fixture entry at `tests/static_guards/test_facade_read_path_imports_guard.py:208`.
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
