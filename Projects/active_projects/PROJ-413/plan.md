# PROJ-413: Legacy removal — stars.py + galaxy.py re-export shims (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-413` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-413 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate Spectrum + solar constant imports off stars.py, then delete shim block | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate WarpPoint/StarSystem imports off galaxy.py, then delete shim | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Complete
**Last Action:** Phase 2 complete — 51 callers migrated to `game.strategy.data.star_system` (61 import-line rewrites; mixed-import sites split correctly); WarpPoint/StarSystem re-export deleted from galaxy.py; `Galaxy.from_dict` switched to a local import; PlanetType re-export preserved as out-of-scope.
**Next Action:** Audit ready
**Blockers:** None

## Overview
Eradicates two PROJ-372 backward-compat re-export shims: `game/strategy/data/stars.py` (Spectrum + solar constants, ~20 Spectrum callers + 1 solar-constant caller) and `game/strategy/data/galaxy.py` (WarpPoint/StarSystem, 51 callers).

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 2.
Removal cluster: `stars_galaxy_reexports (PROJ-372 vestige)`.

### Notable callouts
_(no special callouts)_

## Goals
- Migrate Spectrum + solar constant imports off stars.py, then delete shim block
- Migrate WarpPoint/StarSystem imports off galaxy.py, then delete shim

## Scope
**In:** removal cluster `stars_galaxy_reexports (PROJ-372 vestige)` — items LEG-02-002, MIN-03-006.
**Out:** other clusters' contents (siblings: PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/stars.py` | Production | Edit | Delete lines 31-45 re-export block |
| `game/strategy/data/spectrum.py` | Production | Edit | Update docstring once shim is gone |
| `game/strategy/data/galaxy.py` | Production | Edit | Delete WarpPoint/StarSystem re-export |
| `game/strategy/data/star_system.py` | Production | Edit | Update docstring once shim is gone |
| `<~61 caller files across game/, tests/>` | Production+Test | Migrate-callers | Rewrite imports to canonical modules |

## Related Documents
- [design.md](design.md) — architecture analysis and design rationale
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification output
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
