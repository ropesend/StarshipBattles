# PROJ-361: Battle resolver registry threading (PROJ-306 follow-on)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-361` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-361 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Registry threading + regression test | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Awaiting user verification
**Last Action:** Phase 1 implemented end-to-end. RED-then-GREEN TDD: new regression test `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (2 cases — threading + PROJ-306 fallback) confirmed failing on master adapter, then fixed at `game/strategy/adapters/simulation_adapter.py:258` to forward `registries` to `run_battle.registry_provider` when present. Focused adapter run: 18 passed. Wider strategy run: 3993 passed, 1 skipped.
**Next Action:** User verification, then archive.
**Blockers:** None

## Overview
The strategy-layer `SimulationBattleResolver` accepts a `registries` parameter, threads it into spec building and replay capture, but at `simulation_adapter.py:258` calls `run_battle(..., registry_provider=get_default_registry_provider())`. This silently drops the injected registries when materializing ships — weakening test isolation, mod support, and any future per-session registry work.

## Goals
- Thread injected `GameRegistries` through to `run_battle.registry_provider` when present.
- Preserve `get_default_registry_provider()` as the fallback when `registries is None` (PROJ-306 strategy-layer convention).
- Add a regression test that injects a non-default registry and asserts ship materialization reflects it.

## Scope
**In:**
- `_run_simulated_battle` in `game/strategy/adapters/simulation_adapter.py`
- One regression test under `tests/unit/strategy/adapters/`

**Out:**
- Wider DI cleanup in `GameSession._resolve_registries` (review finding #9 — separate project)
- Replay-capture context (already threads registries correctly via `_build_capture_context`)
- Any change to `run_battle` itself or its signature

## Key Files
| Component | File Path |
|-----------|-----------|
| Resolver | `game/strategy/adapters/simulation_adapter.py` |
| run_battle entry | `game/simulation/battle_runner.py` |
| Protocol | `game/core/protocols/registry.py` |
| GameRegistries impl | `game/core/registry.py` |
| New regression test | `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` |
| Existing test fixtures | `tests/conftest.py` (fresh_registries / minimal_registries) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/01_architecture.md](findings/01_architecture.md) - GameRegistries IS-A IRegistryProvider (PROJ-211)
- [findings/02_dependencies.md](findings/02_dependencies.md) - Caller graph; ConflictResolutionEngine threads registries correctly
- [findings/03_test_impact.md](findings/03_test_impact.md) - Existing test inventory and recommended marker-design test

## Verification
- [ ] Phase 1 checklist complete
- [ ] All tests passing (focused: `pytest tests/unit/strategy/adapters/`)
- [ ] Audit passed
- [ ] User verified
