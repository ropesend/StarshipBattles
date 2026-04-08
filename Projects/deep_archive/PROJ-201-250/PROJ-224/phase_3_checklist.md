# PROJ-224 Phase 3: Constants & Naming Cleanup

## DUP-CEA-003 + DUP-CEA-002: Tick Rate Constants
- [x] Make `SimulationConstants.TICKS_PER_SECOND` derived from `PhysicsConfig.TICK_RATE` (or vice versa)
- [x] Remove `TICK_DURATION` class constants from AI behavior classes — use `PhysicsConfig.TICK_RATE` directly
- [x] Run tests

## DUP-CEA-005: Inline Angle Normalization
- [x] Find inline angle normalization in `game/simulation/entities/projectile.py`
- [x] Created `normalize_angle()` in `game/core/math.py`, replaced inline normalization
- [x] Run tests

## DUP-CEA-006: Raw json.load() Usage
- [x] Find `quickstart_builder.py` (in `game/strategy/`)
- [x] Replace raw `json.load()`/`json.dump()` with `load_json`/`save_json` from json_utils
- [x] Run tests

## DUP-SYS-003: BattleConfig Naming Ambiguity
- [x] Rename `BattleConfig` in `game/core/config.py` to `BattleTuning` (CombatConstants was already taken)
- [x] Update all imports and references across the codebase (5 production files, 4 test files, 1 doc)
- [x] Leave `BattleConfig` in `game/simulation/battle_config.py` as-is (it's the per-battle instance)
- [x] Run tests

## Completion
- [x] All items above checked off
- [x] Run `pytest tests/ -n 12` — all pass (13470 passed)
