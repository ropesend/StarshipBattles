# PROJ-281: BattleScreen Legacy Fallback Removal (migrate start(team0,team1) tests)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-281` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-281 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Build `make_minimal_spec(ships_by_team)` test helper | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit and migrate ~46 callers of `BattleScreen.start(team0, team1)` | Not Started | TBD |
| 3. Delete the `start()` shim and `_build_fallback_outcome` (~90 lines) | Not Started | TBD |
| 4. Documentation update | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Project shell created with agreed scope
**Next Action:** User approval, then Phase B deep-dive swarm review and detailed task breakdown
**Blockers:** Sequenced AFTER PROJ-280. Combat Lab work clusters together (PROJ-278/279/280); this kicks off the UI cleanup cluster

## Overview
[BattleScreen.start(team0, team1)](../../../game/ui/screens/battle_screen.py) is a deprecated 2-team test convenience shim retained for ~46 unit tests that predate the spec-in contract. It synthesizes a minimal `BattleOutcome` via `_build_fallback_outcome` (~90 lines of manual ship-outcome assembly). Per the codebase's eradicate-old-systems policy ([CLAUDE.md System Migration Policy](../../../CLAUDE.md)), this should be removed: build a small test helper that constructs a minimal `BattleSpec`, migrate all ~46 tests to the spec-in path, then delete both the shim and the fallback outcome builder.

## Goals
- One-line test helper: `make_minimal_spec(ships_by_team) -> BattleSpec`
- All ~46 callers migrated to spec-based setup
- `BattleScreen.start(team0, team1)` shim deleted
- `_build_fallback_outcome` (~90 lines) deleted
- BattleScreen has only ONE entry path: `start_battle(controller)` consuming a running BattleController
- Documentation updated to remove all references to the deprecated path

## Scope
**In:**
- New test helper `tests/helpers/battle_spec_helpers.py::make_minimal_spec(ships_by_team)` (or co-located with existing test helpers)
- Audit all callers of `BattleScreen.start(team0, team1)` — confirm count and list
- Migrate each test caller to use `make_minimal_spec` + the spec-in entry path
- Delete `BattleScreen.start(team0, team1)` and any internal compat plumbing
- Delete `_build_fallback_outcome()` and any helpers it uses exclusively
- Update [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md) to remove the "test-convenience shim" mention
- Update [combat_lab/COMBAT_LAB_DOCUMENTATION.md](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md) if it references the shim

**Out:**
- Any change to the production spec-in path (`BattleScreen.start_battle(controller)`)
- Any change to BattleController, run_battle, or BattleEngine
- Refactoring of unrelated BattleScreen behavior (panels, rendering, hit effects)

## Key Files
| Component | File Path |
|-----------|-----------|
| Legacy shim | `game/ui/screens/battle_screen.py` (`start(team0, team1)`) |
| Fallback outcome builder | `game/ui/screens/battle_screen.py` (`_build_fallback_outcome`) |
| New test helper | `tests/helpers/battle_spec_helpers.py` (NEW) |
| Existing test helpers (potential co-location) | `tests/conftest.py`, existing fixture files |
| Test files using legacy shim | ~46 files (audit in Phase 1.2) |
| Doc references | `docs/systems/combat_simulation.md` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Approach: migrate then delete (Option A) | User chose "Migrate then delete (Recommended)". Single PR, no transition state, follows the codebase's eradicate-old-systems policy. Rejected: delete-first-fix-reactively (messier middle); keep-shim-replace-fallback-only (kept dual paths) |
| 2026-04-17 | Sequencing: AFTER PROJ-280 | Lets the Combat Lab cluster (PROJ-278/279/280) close before opening the UI cleanup cluster. Independent technically, but cleaner cognitive grouping |
| 2026-04-17 | One PR (no incremental delivery within this project) | Migration + deletion in one commit means no orphaned state in `main`. Test churn happens once |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Grep for `BattleScreen.start(` returns zero hits
- [ ] Grep for `_build_fallback_outcome` returns zero hits
- [ ] User verified
