# PROJ-251: Error Boundary Architecture Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-251` to see what to do next
> - Open the phase checklist file for your current phase

## Overview

The strategy layer uses broad `except Exception` blocks in three critical paths — turn processing, save/load deserialization, and design file access — that silently swallow errors and corrupt game state. The turn engine's `_time_phase()` catches all exceptions and continues processing, allowing downstream phases to operate on state that upstream phases failed to mutate. The serialization chain (Empire, Fleet, Orders) silently drops corrupt entries rather than failing loudly. The DesignLibrary collapses multiple failure domains into identical `None` returns.

This project replaces these broad catches with a formalized error boundary protocol: a custom exception for phase failures, a pre-turn state snapshot with rollback capability, strict deserialization that fails the whole load on corrupt data, and per-engine input validation.

## Goals
- Eliminate all `except Exception` blocks from the strategy engine and serialization chain
- Add `EnginePhaseError` to the exception hierarchy for turn processing failures
- Implement pre-turn state snapshot and rollback so a failed turn restores clean state
- Make save/load deserialization strict — corrupt data fails the load, not silently drops entries
- Improve DesignLibrary error discrimination (file-not-found vs file-corrupt vs schema-invalid)
- Add per-tick validation to sub-engines that currently have none
- Surface turn failures to the GameSession caller with actionable error information

## Scope

**In Scope:**
- `game/core/exceptions.py` — new exception types
- `game/core/error_codes.py` — new error codes
- `game/strategy/engine/turn_engine.py` — error boundary, snapshot, rollback
- `game/strategy/engine/game_session.py` — turn failure handling
- `game/strategy/data/fleet.py` — strict deserialization
- `game/strategy/data/empire.py` — strict deserialization
- `game/strategy/data/order_serializer.py` — strict deserialization
- `game/strategy/data/galaxy.py` — review/tighten exception handling
- `game/strategy/systems/design_library.py` — error discrimination
- All 14 sub-engines — per-tick input validation
- `docs/05_ERROR_HANDLING.md` — update with new patterns
- `docs/01_ARCHITECTURE.md` — update turn engine error model

**Out of Scope:**
- UI-layer error display (that's a separate project; we raise to GameSession, UI handles it)
- `except Exception` blocks in UI/platform code (tkinter, pygame, screenshots — those are justified)
- `event_bus.py` handler isolation (justified, documented)
- Save file migration (saves are disposable)
- Changing the turn phase execution order
- Changing sub-engine business logic

## Current State
**Last Updated:** 2026-04-06
**Current Phase:** Phase 6 In Progress (3/14 engines done)
**Next Action:** Phase 6 — Complete remaining 11 sub-engine validations
**Blockers:** None
**Context for Next Agent:** Phases 1-5 complete, Phase 6 partial (3/14 engines), Phase 7 docs updated. The core error boundary is fully functional: `_time_phase()` wraps exceptions in `EnginePhaseError`, `process_turn()` captures snapshots and rolls back on failure, `GameSession.process_turn()` re-raises for UI. Serialization is strict (no silent drops). DesignLibrary uses `DesignLoadResult`. 3 engines have `_validate_tick_inputs()`: HarvestingEngine, FleetMovementEngine, ConflictResolutionEngine. Remaining 11 engines need the same pattern (see phase_6_checklist.md for the list). Full suite: 14640/14641 passed (1 flaky test-ordering issue). Pre-existing issues: syntax error in strategy_session_facade.py (fixed), import error in test_build_order_command_handler.py (not fixed, unrelated).

## Key Files Reference

| Component | File Path | Line(s) |
|-----------|-----------|---------|
| Exception hierarchy | `game/core/exceptions.py` | 1-231 |
| Error codes | `game/core/error_codes.py` | all |
| Turn engine (broad catch) | `game/strategy/engine/turn_engine.py` | 239-247 |
| Turn engine (tick loop) | `game/strategy/engine/turn_engine.py` | 481-558 |
| Turn engine (process_turn) | `game/strategy/engine/turn_engine.py` | 395-459 |
| GameSession.process_turn | `game/strategy/engine/game_session.py` | 159-163 |
| GameSession.from_dict | `game/strategy/engine/game_session.py` | 259+ |
| Fleet.from_dict (broad catch) | `game/strategy/data/fleet.py` | 391-395 |
| Empire.from_dict (broad catch) | `game/strategy/data/empire.py` | 321-324 |
| OrderSerializer (broad catch) | `game/strategy/data/order_serializer.py` | 55-57 |
| Galaxy.from_dict (tuple catch) | `game/strategy/data/galaxy.py` | 637 |
| DesignLibrary.load_design_data | `game/strategy/systems/design_library.py` | 191-222 |
| DesignLibrary.scan_designs | `game/strategy/systems/design_library.py` | 67-109 |
| ValidationResult | `game/core/validation.py` | 63-196 |
| Validation helpers | `game/core/validation_helpers.py` | all |
| deserialize_list | `game/core/json_utils.py` | 209+ |
| Error handling docs | `docs/05_ERROR_HANDLING.md` | all |
| Turn engine tests | `tests/unit/strategy/turn_engine/test_turn_error_handling.py` | all |
| Fleet round-trip tests | `tests/integration/save_load/test_roundtrip_fleet.py` | all |
| Ship serializer tests | `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | all |
| Design library tests | `tests/unit/strategy/design_library/test_error_logging.py` | all |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Build on existing exception hierarchy, don't create parallel one | `SimulationException`, `PersistenceException`, `ValidationException` already exist with error codes. Only `EnginePhaseError` is genuinely new. |
| 2026-04-06 | Snapshot via `to_dict()`/`from_dict()` round-trip, not `copy.deepcopy` | Reuses existing tested serialization infrastructure. Also stress-tests the serialization path every turn. Acceptable performance for 1x per turn. |
| 2026-04-06 | Halt entire turn on any phase failure, not continue-and-skip | The cascade problem (Phase N+1 operating on state Phase N failed to mutate) is the core bug. Partial turns are worse than no turn. |
| 2026-04-06 | Strict deserialization — fail entire load on corrupt data | Saves are disposable (pre-production). Silent data loss is worse than a clear error message. Narrowly-caught specific exceptions (e.g., `PersistenceException`) are fine; broad `except Exception` is not. |
| 2026-04-06 | DesignLibrary gets error discrimination, not strict failure | Design files are user-created content on the filesystem. Corrupt designs should not crash the game. But the caller deserves to know WHY a load failed. |
| 2026-04-06 | Per-tick sub-engine validation is Phase 6 (last code phase) | Most sub-engines have zero per-tick validation. Adding it to all 14 engines is the largest work item. The error boundary (halt + rollback) provides safety even before validation is complete. |

---

## Dependency Chain

```
Phase 1 (Exceptions)
    |
    +---> Phase 2 (Serialization Strictness)
    |         |
    |         +---> Phase 4 (Turn State Snapshot) -- uses strict serialization
    |                   |
    |                   +---> Phase 5 (Turn Engine Error Boundary)
    |                              |
    |                              +---> Phase 6 (Sub-Engine Validation)
    |                                         |
    |                                         +---> Phase 7 (Documentation)
    +---> Phase 3 (DesignLibrary) -- independent, can parallel with 4-5
```

---

## Phases

### Phase 1: Exception Hierarchy & Error Codes [Simple]
**Objective:** Extend the existing exception hierarchy with strategy-layer error types
**Status:** Complete
**Estimated Size:** ~50 lines code, ~30 lines tests
See `phase_1_checklist.md`

### Phase 2: Strict Deserialization [Medium]
**Objective:** Remove all `except Exception` from the save/load chain; fail loudly on corrupt data
**Status:** Complete
**Estimated Size:** ~80 lines changed, ~120 lines tests
**Depends On:** Phase 1
See `phase_2_checklist.md`

### Phase 3: DesignLibrary Error Discrimination [Simple]
**Objective:** Distinguish file-not-found, file-corrupt, and schema-invalid in DesignLibrary
**Status:** Complete
**Estimated Size:** ~60 lines changed, ~80 lines tests
**Depends On:** Phase 1
See `phase_3_checklist.md`

### Phase 4: Turn State Snapshot & Rollback [Medium]
**Objective:** Capture pre-turn state and restore it if the turn fails
**Status:** Complete
**Estimated Size:** ~150 lines code, ~200 lines tests
**Depends On:** Phase 2 (snapshot uses serialization, must be reliable)
See `phase_4_checklist.md`

### Phase 5: Turn Engine Error Boundary [Medium]
**Objective:** Replace `_time_phase()` broad catch with halt-and-rollback behavior
**Status:** Complete
**Estimated Size:** ~100 lines changed, ~150 lines tests
**Depends On:** Phase 4 (needs snapshot to rollback)
See `phase_5_checklist.md`

### Phase 6: Sub-Engine Per-Tick Validation [Large]
**Objective:** Add input validation to all 14 sub-engines before they mutate state
**Status:** In Progress (3/14 engines done: Harvesting, FleetMovement, ConflictResolution)
**Estimated Size:** ~300 lines code, ~400 lines tests
**Depends On:** Phase 5 (error boundary catches validation failures)
See `phase_6_checklist.md`

### Phase 7: Documentation Update [Simple]
**Objective:** Update error handling docs, architecture docs, and pattern docs
**Status:** In Progress (05_ERROR_HANDLING.md updated, 01_ARCHITECTURE.md and 02_PATTERNS.md pending)
**Depends On:** All previous phases
See `phase_7_checklist.md`
