# PROJ-415: Legacy removal — planet.py re-exports (PROJ-210/284 vestige) (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-415` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-415 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 61 caller files (64 import statements) off planet.py re-exports, then delete the block | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1 (complete)
**Last Action:** Phase 1 complete — 61 caller files migrated to canonical modules; planet.py shim block deleted (ColonySpeciesConfig retained as runtime import, PlanetaryFacility/SpeciesPopulation moved under TYPE_CHECKING); AST scan reports 0 external shim usages; full test suite passes apart from pre-existing QS Battleship _metadata case.
**Next Action:** Audit ready
**Blockers:** None

## Overview
Migrates 61 caller **files** (64 import statements) off `game/strategy/data/planet.py` re-exports of `PlanetaryFacility` and `SpeciesPopulation` to their canonical modules, then deletes the re-export block. `ColonySpeciesConfig` has zero external callers via the shim but is a runtime dependency inside `planet.py` itself (fields + constructor at lines 107, 187, 190) — its shim line is removed last, after ensuring its internal import is satisfied.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `planet_reexports (PROJ-210/284)`.

### Notable callouts
_(no special callouts)_

## Goals
- Migrate 61 caller files (64 import statements) off planet.py re-exports, then delete the block

## Scope
**In:** removal cluster `planet_reexports (PROJ-210/284)` — items LEG-02-003.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planet.py` | Production | Edit | Delete lines 19-25 re-export block |
| `<~61 caller files>` | Production+Test | Migrate-callers | Switch to canonical planetary_facility / species_population / colony_species_config modules |

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
