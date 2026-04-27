# PROJ-306: Battle Simulation DI Cleanup (PROJ-274 closure)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-306` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-306 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Eliminate `battle_runner` fallback | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Eliminate `registry_loader` fallback | In Progress | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verification & Doc Update | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Phase 2 — registry_loader fallback
**Last Action:** Phase 1 complete — `_default_ship_builder_from_context` renamed to public `build_context_ship_builder(registry_provider=...)`, all 6 production callers migrated (1 surprise caller in `test_lab/screen.py` not in the original inventory), `run_battle` and `BattleController.start_from_spec` now require `registry_provider` when `ship_builder is None`. AST-based static guard in `tests/unit/simulation/test_battle_runner_di.py` passes for `battle_runner.py` (still flags `registry_loader.py` — Phase 2's job).
**Next Action:** Phase 2 Task 2.1 — survey `reload_registries_from_directory` callers (verified test-only) and migrate to required-parameter pattern.
**Blockers:** None
**Context for Next Agent:** PROJ-274 introduced `_default_ship_builder_from_context()` as a transitional fallback. Phase 1 of PROJ-306 has now eliminated it. Phase 2 will fix the second surviving global-lookup at `registry_loader.py:91`.

## Overview
Eliminate the two remaining `get_default_registry_provider()` calls in the Simulation layer. They were left in place during PROJ-274 as documented transitional fallbacks for callers that didn't yet pass `ship_builder` / `registry_provider` explicitly. PROJ-274 is now archived, so the fallbacks are no longer transitional — they're undeleted graveyard code per the System Migration Policy.

## Goals
- Delete `_default_ship_builder_from_context()` in [game/simulation/battle_runner.py](game/simulation/battle_runner.py) (lines ~170-220)
- Make `ship_builder` a required argument of `run_battle` and `BattleController.start_from_spec` (or have those callers inject the materializer explicitly)
- Eliminate the `get_default_registry_provider()` call in [game/simulation/services/registry_loader.py:91](game/simulation/services/registry_loader.py#L91)
- Keep test baseline (15389+ passing) green

## Scope
**In:**
- Remove `_default_ship_builder_from_context()` from `battle_runner.py`
- Migrate every production caller of `run_battle` / `BattleController.start_from_spec` to pass `ship_builder` explicitly (most already do — Combat Lab is documented as the explicit-pass pattern; non-CL callers may need touch-ups)
- Make `registry_loader.load_all_registries()` (or whatever the signature is — verify in Phase 2) take `registry_provider` as a required parameter; remove the line-91 fallback
- Update `docs/01_ARCHITECTURE.md` to remove any mention of the transitional fallback as legitimate

**Out:**
- The `TYPE_CHECKING` import of `RaceConfig` in `game/core/protocols.py:38` — confirmed unavoidable trade-off, not a bug
- Any DI changes outside of these two specific call sites

## Key Files
| Component | File Path | Lines |
|-----------|-----------|-------|
| battle_runner fallback | `game/simulation/battle_runner.py` | 170-220 (`_default_ship_builder_from_context`) |
| The actual offending call | `game/simulation/battle_runner.py` | 198 (`get_default_registry_provider()`) |
| registry_loader call | `game/simulation/services/registry_loader.py` | 91 (`get_default_registry_provider()`) |
| Comment marking the issue | `game/simulation/services/registry_loader.py` | 90 (`# PROJ-211: Pass registry_provider explicitly (no fallback)` — ironic given the actual code) |
| Caller sites | All callers of `run_battle` / `BattleController.start_from_spec` (find via grep) | varies |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Projects/deep_archive/PROJ-251-300/PROJ-274/](../../deep_archive/PROJ-251-300/PROJ-274/) - The original Unified ShipMaterializer project (if archived there)

## Verification
- [ ] All phase checklists complete
- [ ] `grep -rn "get_default_registry_provider" game/simulation/` returns ZERO results in production code
- [ ] `python -c "from game.simulation.battle_runner import _default_ship_builder_from_context"` raises `ImportError`
- [ ] Full sharded suite at 15389+ passing (no regressions)
- [ ] Manual smoke: launch the game, fight a battle, verify it runs to completion
- [ ] Manual smoke: launch Combat Lab, run a scenario, verify it runs
- [ ] User verified
