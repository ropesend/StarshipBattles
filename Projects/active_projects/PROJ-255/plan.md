# PROJ-255: Code Quality & Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-255` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-255 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Split AIController.update Into Stages | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Type Hints on Critical Paths | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Component Definition Flyweight (Conditional) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation Update | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-06
**Active Phase:** Not Started
**Next Action:** Begin Phase 1 — Split AIController.update
**Blockers:** None
**Context for Next Agent:** Fresh project. All findings verified against current code. Note: Finding 6 (Component class) was largely addressed by PROJ-241 (Component God Class Decomposition — Complete). Phase 3 of this project is conditional on memory profiling showing pressure.

## Overview

Three code quality issues — one high-severity method decomposition, one medium-severity type annotation gap, and one conditional optimization:

1. **AIController.update Bloat** (Finding 4 — High): `update()` method (CC ~18-22) mixes formation upkeep, target acquisition, retreat logic, and behavior dispatch in a single hot-path method. Makes AI tuning risky — changing one concern risks breaking another.

2. **Missing Type Hints** (Finding 13 — Medium): Key constructors (`AIController.__init__`, `ShipStatsCalculator.__init__`) and orchestration methods (`TurnEngine.process_turn`, `GameSession.handle_command`) lack parameter/return annotations. Reduces static analysis value in the most coupled areas.

3. **Component Definition Sharing** (Finding 6 — Low, conditional): Each Component instance deep-copies its definition data. PROJ-241 already decomposed the class into facade + 5 delegates, reducing this to a medium concern. The deepcopy is intentional for modifier isolation. Only worth addressing if memory profiling shows fleet-scale pressure.

## Goals
- AIController.update is decomposed into focused, testable stages
- Critical-path constructors and methods have full type annotations
- (Conditional) Component definitions are shared via flyweight pattern if memory profiling warrants it

## Scope

**In Scope:**
- `game/ai/controller.py` — decompose `update()` method
- `game/ai/controller.py` — add type hints to `__init__`
- `game/simulation/entities/ship_stats.py` — add type hints to `__init__`
- `game/strategy/engine/turn_engine.py` — add type hints to `process_turn`, `_process_tick`
- `game/strategy/engine/game_session.py` — add type hints to `__init__`, `handle_command`
- `game/simulation/components/component.py` — flyweight optimization (conditional on profiling)

**Out of Scope:**
- Full codebase type annotation sweep (out of scope — we annotate the 4 critical files only)
- pyright/mypy CI enforcement (future follow-up)
- Component class further decomposition (PROJ-241 already completed this)
- AI behavior logic changes (we only restructure, not change behavior)

## Findings Summary

| Finding | File | Lines | Issue |
|---------|------|-------|-------|
| 4 (Controller) | controller.py | 278-361 | CC ~18-22, mixes 5+ responsibilities |
| 13 (Types) | controller.py | 81 | `__init__` missing parameter types |
| 13 (Types) | ship_stats.py | 83 | `__init__` missing parameter types |
| 13 (Types) | turn_engine.py | 415, 540 | `process_turn`, `_process_tick` missing param types |
| 13 (Types) | game_session.py | 72, 217 | `__init__`, `handle_command` missing param types |
| 6 (Component) | component.py | 95-105 | Deep-copy per instance (intentional, but costly at scale) |

## Key Files Reference

| Component | File Path |
|-----------|-----------|
| AI controller | `game/ai/controller.py` |
| Ship stats calculator | `game/simulation/entities/ship_stats.py` |
| Turn engine | `game/strategy/engine/turn_engine.py` |
| Game session | `game/strategy/engine/game_session.py` |
| Component | `game/simulation/components/component.py` |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Extract-method refactor for AIController.update, not a full class decomposition | The method is ~84 lines with clear responsibility boundaries. Extract-method is sufficient and lower risk than introducing new classes. |
| 2026-04-06 | Type hints on 4 critical files only, not full codebase | Focused effort on the most coupled and performance-sensitive code. Full sweep would be a separate project. |
| 2026-04-06 | Phase 3 (flyweight) is conditional on memory profiling | PROJ-241 already decomposed Component. The deepcopy is intentional for isolation. Only optimize if measured pressure exists. |

## Dependency Chain

```
Phase 1 (AIController split) -- independent, highest value
    |
Phase 2 (Type hints) -- independent of Phase 1
    |
Phase 3 (Flyweight) -- CONDITIONAL, only if memory profiling warrants
    |
    +---> Phase 4 (Documentation)
```

Phases 1 and 2 are independent.

---

## Phases

### Phase 1: Split AIController.update Into Stages [Medium]
**Objective:** Decompose `update()` into focused private methods with typed inputs/outputs
**Status:** Not Started
**Estimated Size:** ~40 lines refactored (same total, better structure), ~20 lines tests
**Depends On:** Nothing
**Risk:** Very low — pure extract-method refactor, no behavior change
See `phase_1_checklist.md`

### Phase 2: Type Hints on Critical Paths [Simple]
**Objective:** Add full parameter/return annotations to constructors and hot-path methods in 4 files
**Status:** Not Started
**Estimated Size:** ~30 lines added annotations
**Depends On:** Nothing
**Risk:** Zero — adding annotations is non-breaking
See `phase_2_checklist.md`

### Phase 3: Component Definition Flyweight (Conditional) [Medium]
**Objective:** Share immutable definition data across Component instances via flyweight pattern — ONLY if memory profiling shows pressure
**Status:** Not Started (Conditional)
**Estimated Size:** ~80 lines if pursued
**Depends On:** Memory profiling results
**Risk:** Medium — changes Component construction model
See `phase_3_checklist.md`

### Phase 4: Documentation Update [Simple]
**Objective:** Update architecture docs to reflect AIController decomposition and type coverage
**Status:** Not Started
**Estimated Size:** ~20 lines docs
**Depends On:** Phases 1-2 (and 3 if pursued)
See `phase_4_checklist.md`
