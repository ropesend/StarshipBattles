# PROJ-252: Determinism & Global State Isolation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-252` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-252 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Per-Battle RNG Injection | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Session-Scoped Event Bus | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Eliminate Global Registry from Simulation | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Determinism Verification Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation Update | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-06
**Active Phase:** Not Started
**Next Action:** Begin Phase 1 — Per-Battle RNG Injection
**Blockers:** None
**Context for Next Agent:** Fresh project. All findings verified against current code. See "Findings Summary" below for exact file locations and line numbers.

## Overview

Three categories of global/process-level coupling in the codebase undermine testability, parallelism, and determinism:

1. **Global RNG** (Finding 12): `BattleEngine.start()` seeds the process-global `random` module. All simulation code (`damage_calculator`, `collision`, `conflict_resolution_engine`) consumes from this shared state. Determinism depends on unrelated call order — dangerous for replays, debugging, and AI simulations.

2. **Global Event Handler** (Finding 11): `GameSession.__init__` overwrites a module-level `_event_handler` in `event_logging.py`. Multiple sessions cannot coexist; events silently route to the wrong session.

3. **Hidden Global Registry** (Finding 10): `ShipComponentManager` and `ShipValidatorHelper` call `get_default_registry_provider()` inside simulation-domain code, violating the documented strict-DI contract (docs/02_PATTERNS.md:202). Makes isolated/parallel simulations harder.

## Goals
- Battle simulation is fully deterministic given a seed, independent of process-global state
- Event logging is session-scoped — no module-level mutable globals
- All simulation-domain code receives registries via DI, never via global lookup
- Existing tests continue to pass; new determinism tests prove the guarantees

## Scope

**In Scope:**
- `game/simulation/systems/battle_engine.py` — RNG injection
- `game/simulation/combat/damage_calculator.py` — accept RNG parameter
- `game/engine/collision.py` — accept RNG parameter
- `game/simulation/combat/weapon_firing_system.py` — thread RNG through
- `game/strategy/engine/conflict_resolution_engine.py` — separate strategy RNG
- `game/core/event_logging.py` — session-scoped EventBus
- `game/strategy/engine/game_session.py` — create EventBus instance
- `game/simulation/entities/ship_component_manager.py` — remove global registry calls
- `game/simulation/entities/ship_validator_helper.py` — remove global registry calls

**Out of Scope:**
- UI-layer event handling (that consumes events, doesn't produce them)
- RNG in non-simulation code (galaxy generation, etc.)
- Full `mypy`/`pyright` enforcement (that's PROJ-255)

## Findings Summary

| Finding | Files | Lines | Issue |
|---------|-------|-------|-------|
| 12 (RNG) | battle_engine.py | 242 | `random.seed()` on module-level RNG |
| 12 (RNG) | damage_calculator.py | 196 | `random.choices()` from global RNG |
| 12 (RNG) | collision.py | 121 | `random.random()` from global RNG |
| 12 (RNG) | conflict_resolution_engine.py | 222, 262 | `random.sample()`/`random.random()` at strategy layer |
| 11 (Event) | event_logging.py | 33 | Module-level `_event_handler` global |
| 11 (Event) | game_session.py | 83 | `set_event_handler()` overwrites global |
| 10 (DI) | ship_component_manager.py | 91, 96, 128, 137 | `get_default_registry_provider()` in simulation code |
| 10 (DI) | ship_validator_helper.py | 44, 55, 64 | `get_default_registry_provider()` in simulation code |

## Key Files Reference

| Component | File Path |
|-----------|-----------|
| Battle engine | `game/simulation/systems/battle_engine.py` |
| Damage calculator | `game/simulation/combat/damage_calculator.py` |
| Collision system | `game/engine/collision.py` |
| Weapon firing | `game/simulation/combat/weapon_firing_system.py` |
| Conflict resolution | `game/strategy/engine/conflict_resolution_engine.py` |
| Event logging | `game/core/event_logging.py` |
| Game session | `game/strategy/engine/game_session.py` |
| Ship component manager | `game/simulation/entities/ship_component_manager.py` |
| Ship validator helper | `game/simulation/entities/ship_validator_helper.py` |
| DI pattern docs | `docs/02_PATTERNS.md` |
| Architecture docs | `docs/01_ARCHITECTURE.md` |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Use `random.Random(seed)` instances, not global `random.seed()` | Per-instance RNG is the standard Python pattern for deterministic subsystems. Thread-safe, no cross-contamination. |
| 2026-04-06 | Keep module-level `log_event()` as deprecated convenience during migration | Many call sites use it. Incremental migration: inject EventBus where available, fall back to global, then ratchet. |
| 2026-04-06 | Extract registries from Ship (already holds them) rather than adding new constructor params | ShipComponentManager already receives Ship; Ship already holds `_registries`. No new plumbing needed. |

## Dependency Chain

```
Phase 1 (Per-Battle RNG)
    |
    +---> Phase 4 (Determinism Tests) -- needs RNG injection to verify
    |
Phase 2 (Session-Scoped Event Bus) -- independent of Phase 1
    |
Phase 3 (Global Registry Elimination) -- independent of Phases 1-2
    |
    +---> Phase 5 (Documentation) -- after all code phases
```

Phases 1, 2, 3 are independent and could be worked in parallel.

---

## Phases

### Phase 1: Per-Battle RNG Injection [Medium]
**Objective:** Replace global `random.seed()` with per-battle `random.Random(seed)` instances threaded through simulation code
**Status:** Not Started
**Estimated Size:** ~80 lines changed across 5-6 files, ~60 lines tests
**Depends On:** Nothing
See `phase_1_checklist.md`

### Phase 2: Session-Scoped Event Bus [Medium]
**Objective:** Replace module-level `_event_handler` global with session-scoped EventBus instances
**Status:** Not Started
**Estimated Size:** ~60 lines changed, ~40 lines tests
**Depends On:** Nothing
See `phase_2_checklist.md`

### Phase 3: Eliminate Global Registry from Simulation [Simple]
**Objective:** Remove all `get_default_registry_provider()` calls from `game/simulation/` and replace with DI
**Status:** Not Started
**Estimated Size:** ~30 lines changed, ~20 lines tests
**Depends On:** Nothing
See `phase_3_checklist.md`

### Phase 4: Determinism Verification Tests [Simple]
**Objective:** Add tests proving battle determinism is seed-based and independent of process state
**Status:** Not Started
**Estimated Size:** ~80 lines tests
**Depends On:** Phase 1
See `phase_4_checklist.md`

### Phase 5: Documentation Update [Simple]
**Objective:** Update architecture and pattern docs to reflect new DI, RNG, and event patterns
**Status:** Not Started
**Estimated Size:** ~40 lines docs
**Depends On:** Phases 1-4
See `phase_5_checklist.md`
