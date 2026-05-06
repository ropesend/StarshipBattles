# Review Scope: PROJ-369 TurnEngine Decomposition

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260506_071706_deac7e
**Review mode:** normal (not lightweight — no Coverage block present)
**Branch:** feat/03c-phase-aware-execution (HEAD: 82b5cbc20)
**Parent request:** None

## Scope

Five commits on `feat/03c-phase-aware-execution`:
- `8ff9fa7b7` — Phase 1: extract end-of-turn block to `DEFAULT_END_OF_TURN_PHASE_LIST`
- `aaeb799b8` — Phase 2: make Quality/Atmosphere/Water engines injectable via `TurnEngineConfig`
- `cbc02b2e2` — Phase 3: required-kwarg injection; delete `_NullBattleResolver` + `create_default_turn_engine`; ctor 21→8 kwargs; migrate 110 construction sites
- `7d53087e3` — Phase 4: extract `_run_phases` helper; unified tick + end-of-turn loop
- `82b5cbc20` — Phase 5: AST guards + per-phase mock-context tests + docs

Files reviewed:
- `game/strategy/engine/turn_engine.py` (700 LOC)
- `game/strategy/engine/turn_engine_config.py` (201 LOC)
- `game/strategy/interfaces/engines.py` (778 LOC)
- `game/strategy/engine/turn_phase_registry.py` (379 LOC)
- `game/strategy/engine/game_session.py` (472 LOC)
- `game/strategy/engine/conflict_resolution_engine.py` (567 LOC)
- `tests/fixtures/turn_engine.py` (118 LOC)
- `tests/unit/strategy/turn_engine/` (135 tests, 20 files)
- `tests/unit/strategy/turn_engine/conftest.py` (131 LOC)
- `Projects/active_projects/PROJ-369/decisions.md`
- `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md`

## Instructions

8 focus areas in priority order (see request file for full details).

## Context

Wave B project 2 of 5. PROJ-369 completes PROJ-259's `ITickPhase` + `TurnEngineConfig` migration.
