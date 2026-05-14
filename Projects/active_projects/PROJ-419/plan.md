# PROJ-419: Legacy removal — light cleanup of stale comments and dead imports (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-419` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-419 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Single-PR sweep of stale comments and dead imports | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-13_194106_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Trims 4 stale comments / dead-marker artifacts and removes 3 dead `import pygame_gui` lines. All are zero-call-site fixes touching < 15 LOC total.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 5.
Removal cluster: `light_cleanup`.

### Notable callouts
- ✓ Contains 5 zero-call-site fixes — can ship as one PR.

## Goals
- Single-PR sweep of stale comments and dead imports

## Scope
**In:** removal cluster `light_cleanup` — items LEG-01-001, MIN-03-001, MIN-03-002, LEG-02-005, MIN-03-004.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/panels/race_summary_panel.py` | Production | Edit | Delete stale `# legacy` comment line 149 |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Edit | Trim stale function reference at line 379 |
| `game/strategy/engine/superweapon_handlers/open_warp_point.py` | Production | Edit | Reword temporal comment line 89 |
| `game/core/paths.py` | Production | Edit | Resolve PROJ-XX placeholder at line 98 |
| `game/screen_router.py` | Production | Edit | Delete 3 dead pygame_gui imports (lines 182, 304, 429) |

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
