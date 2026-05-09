# PROJ-394: PROJ-387 follow-up — Galaxy state public property + guard cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-394` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-394 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Doc + guard cleanup, expose public `Galaxy.state`, migrate `_state.X` callers | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1 (Complete)
**Last Action:** Phase 1 complete — `Galaxy.state` public property added, 3 production readers + 8 test files migrated from `galaxy._state.X` to `galaxy.state.X`, `GRANDFATHERED_EXTERNAL_READS` emptied, guard / `galaxy_state.py` / PROJ-387 plan docstrings + path corrected; full sharded suite 19084/19091 passed (3 failures match documented baseline, 0 new).
**Next Action:** Project verification — user review of MAJ/MIN closure, then archive.
**Blockers:** None

## Overview
PROJ-387 deleted 5 backward-compat property forwarders on `Galaxy` and migrated 3 production readers + 8 test files to access `galaxy._state.<field>` directly. The OpenCode review (req_20260508_231157_6165cf) recommended APPROVE_WITH_FOLLOW_UP with 2 MAJ + 3 MIN findings. This project closes those findings:

1. Replace `galaxy._state.<field>` access with a true public `galaxy.state: GalaxyState` property (MAJ-002).
2. Remove the now-stale `GRANDFATHERED_EXTERNAL_READS` entries that match nothing post-PROJ-387 (MAJ-001).
3. Update three out-of-date docstrings that still describe the deleted forwarders (MIN-003, MIN-004).
4. Fix the wrong file path in `Projects/active_projects/PROJ-387/plan.md:40` (MIN-005).

## Goals
- Expose `Galaxy.state` as a public `@property` returning `GalaxyState`. Migrate the 3 production readers and all test sites from `galaxy._state.X` to `galaxy.state.X`.
- Remove all 5 entries from `GRANDFATHERED_EXTERNAL_READS` in `tests/unit/strategy/data/test_galaxy_state_encapsulation.py`.
- Update docstrings in `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` (header) and `game/strategy/data/galaxy_state.py` (lines 12-16) so they describe the post-PROJ-387 architecture.
- Patch `Projects/active_projects/PROJ-387/plan.md:40` to remove the non-existent `game/strategy/data/movement.py` reference.

## Scope
**In:** PROJ-387 review findings MAJ-001, MAJ-002, MIN-003, MIN-004, MIN-005.

**Out:**
- `_next_planet_id` / `_next_fleet_id` (out of scope per PROJ-387 verification report — they have setters and are needed for serialization).
- Any rename of `Galaxy._state` itself (we add a public `state` property; we do NOT rename the underlying attribute).
- Any further encapsulation work on `Galaxy` beyond exposing `state`.

## Key Files
| Component | File Path |
|-----------|-----------|
| Add public `state` property | `game/strategy/data/galaxy.py` |
| Migrate readers (3 production files) | `game/strategy/engine/handlers/movement.py`, `game/strategy/services/fleet_navigation_service.py`, `game/ui/screens/strategy_render/hex_outlines.py` |
| Migrate test access sites (~8 test files from PROJ-387) | `tests/unit/strategy/...`, `tests/unit/ui/screens/...`, `tests/integration/strategy/test_warp_orders.py` |
| Guard cleanup + docstring | `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` |
| Docstring | `game/strategy/data/galaxy_state.py` |
| Plan path correction | `Projects/active_projects/PROJ-387/plan.md` |

## Related Documents
- [design.md](design.md) — review findings and architectural rationale
- [decisions.md](decisions.md) — full decisions log
- Source review: `Reviews/results/2026-05-08_231159_code_proj-387-galaxy-backward-compat-property-forwarder_req-req_20260508_231157_6165cf/report.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (full sharded suite; 0 NEW failures vs the existing 3-failure baseline)
- [ ] No remaining references to `galaxy._state.` in production OR tests (`grep -rn "galaxy\._state\." .`) — all migrated to `galaxy.state.`
- [ ] `GRANDFATHERED_EXTERNAL_READS` is empty
- [ ] User verified
