# PROJ-414: Legacy removal — pathfinding.py shim (PROJ-376) (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-414` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-414 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit + migrate + delete pathfinding shim (3 sub-tasks: 1a audit, 1b migrate, 1c delete) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-13_194106_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Executes the PROJ-376 migration sweep: migrates 19 import sites off the `game/strategy/data/pathfinding.py` shim onto `GalaxyPathfindingService` / `InterceptCalculator` directly, then deletes the 102-line shim file.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `pathfinding_shim (PROJ-376)`.

### Notable callouts
- **Guard test must be deleted:** `tests/unit/strategy/data/test_pathfinding_shim_scope.py` pins the shim's function set and explicitly states the shim is "no longer slated for deletion." Deleting `pathfinding.py` without also deleting this guard causes immediate test failure.
- **~30 patch sites, not just import sites:** In addition to ~22 import lines, there are ~30 `patch('game.strategy.data.pathfinding.X')` sites across ~9 test files. Each must be redirected to the correct new target for the migrated production code path — a blanket "move to service class" strategy is wrong.
- **`intercept_calculator.py` routes through the shim intentionally:** Lines 121 and 169 import the shim module specifically to preserve test-patch transparency. Migrating these changes test isolation semantics and must be planned per-site.
- **PROJ-377 decided not to delete this shim:** PROJ-414 supersedes that decision. Review `Projects/deep_archive/PROJ-351-400/PROJ-377/decisions.md` to understand the original reasons before implementing.

## Goals
- Migrate 19 pathfinding shim callers, then delete the shim file

## Scope
**In:** removal cluster `pathfinding_shim (PROJ-376)` — items MAJ-001.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/pathfinding.py` | Production | Delete [DELETE] | Whole file removed after caller migration |
| `<~19 caller files including fleet_navigation_service.py, superweapon_order_processor.py, strategy_superweapons.py, fleet_warp_resolution.py, handlers/base.py, game_session.py, planet_slice.py>` | Production+Test | Migrate-callers | Switch to GalaxyPathfindingService / InterceptCalculator |

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
