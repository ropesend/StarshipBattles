# PROJ-381 File Manifest

> Generated during /claude-proj-from-error-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_game_state_manager.py` | Production | Add `except EnginePhaseError` UI boundary in `process_full_turn()` (Phase 1, B-5 CRITICAL) |
| `tests/integration/ui/test_strategy_turn_error_boundary.py` | Test (new) | Regression test exercising B-5 failure path (Phase 1) |
| `game/strategy/formulas/colony_output.py` | Production | Add canonical comment OR narrow `except` at line 85 (Phase 2, ERR-01-001) |
| `game/strategy/engine/commands/registry.py` | Production | Replace 2 `ValueError` with `ValidationException` at lines 103, 108 (Phase 2, ERR-01-002) |
| `game/assets/asset_manager.py` | Production | Narrow OR comment broad except at line 154 (Phase 2, ERR-02-001) |
| `game/strategy/data/ship_instance.py` | Production | Add canonical comment at line 69 (Phase 2, ERR-02-002) |
| `game/strategy/engine/turn_state_snapshot.py` | Production | Add canonical comment at line 56; replace `json.dump` with `save_json` at line 131 (Phase 2 ERR-02-003 + Phase 3 ERR-02-005) |
| `game/strategy/config/economy_config.py` | Production | Replace `json.load(fh)` with `load_json` at line 106 (Phase 2, ERR-02-004) |
| `game/strategy/engine/turn_engine.py` | Production | Comment at line 279; comment-or-narrow at line 518; enrich `_time_phase` context with turn_number/save_path (Phase 2 ERR-03-001/ERR-03-002 + Phase 3 B-2) |
| `game/strategy/services/design_validator.py` | Production | Comment at line 76; comment + add error to result at line 92 (Phase 2, ERR-03-003 + ERR-03-004) |
| `game/ui/screens/battle_setup/controller.py` | Production | Add canonical comment at line 123 (Phase 2, ERR-04-001) |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | Promote modifier-collection log to ERROR + enrich context (Phase 2, B-7) |
| `game/core/exceptions.py` | Production | Add `ImageUnexpectedError` class; add `TurnFailedError` and (optionally) `BattleResolutionError` / `SessionInitializationError` subclasses (Phase 2 B-10/B-11 + Phase 3 B-4/B-6) |
| `game/ui/services/image/background.py` | Production | Add broad-except wrapping as `ImageUnexpectedError`; add `_done_event` + `wait()` method (Phase 2 B-10 + Phase 3 LLM-3) |
| `docs/05_ERROR_HANDLING.md` | Doc | Update §74 image-unexpected-wrapper note now that `ImageUnexpectedError` exists (Phase 2, B-10) |
| `game/strategy/engine/game_session.py` | Production | Wrap `GameInitializer.initialize` with try/except + null-object recovery (Phase 2, B-11) |
| `game/strategy/engine/handlers/base.py` | Production | Replace 3 `ValueError` raises with `ValidationException` at lines 181, 184, 251 (Phase 3, ERR-01-003) |
| `game/simulation/battle_state.py` | Production | Wrap `json.loads` with `PersistenceException` chaining at lines 655-658 (Phase 3, ERR-01-004) |
| `game/strategy/data/galaxy_system_generator.py` | Production | Replace `json.load` with `load_json(default={})` at line 229 (Phase 3, ERR-04-003 + ERR-04-008) |
| `game/strategy/data/galaxy_warp_generator.py` | Production | Replace `json.load` with `load_json(default={})` at line 368 (Phase 3, ERR-04-004) |
| `game/ui/services/tkinter_utils.py` | Production | Normalize 4 comments to canonical `# Intentional broad catch:` at lines 142, 175, 206, 229 (Phase 3, ERR-04-006) |
| `game/strategy/data/star_generation_config.py` | Production | Remove `ValueError`, `KeyError` from catch tuple at line 192 (Phase 3, ERR-04-007 — UNCERTAIN, user-included) |
| `game/strategy/facade/strategy_session_facade.py` | Production | Wrap `session.process_turn` and re-raise as `TurnFailedError` (Phase 3, B-4) |
| `game/strategy/adapters/simulation_adapter.py` | Production | Wrap `run_battle` with battle-context enrichment (Phase 3, B-6) |
| `game/core/error_codes.py` | Production | Add `OWNERSHIP_MISMATCH` constant if not already present (Phase 3, ERR-01-003) |
| `tests/strategy/engine/test_turn_engine.py` | Test | Sibling assertions for B-2 context enrichment (Phase 3) |
| `tests/strategy/engine/test_conflict_resolution.py` | Test | Regression test for B-7 ERROR-level log + hex/empire context (Phase 2) |
| `tests/strategy/services/test_design_validator.py` | Test | Regression test for ERR-03-004 silent-swallow fix (Phase 2) |
| `tests/strategy/engine/test_game_session.py` | Test | Regression test for B-11 init failure recovery (Phase 2) |
| `tests/ui/services/image/test_background.py` | Test | Regression tests for B-10 `ImageUnexpectedError` and LLM-3 `wait()` (Phases 2 + 3) |
| `tests/strategy/data/test_star_generation_config.py` | Test | Regression test confirming malformed config now raises (Phase 3, ERR-04-007) |
| `tests/strategy/adapters/test_simulation_adapter.py` | Test | Regression test for B-6 fleet/hex context preservation (Phase 3) |
| `tests/strategy/facade/test_strategy_session_facade.py` | Test | Regression test for B-4 facade-level domain conversion (Phase 3) |
