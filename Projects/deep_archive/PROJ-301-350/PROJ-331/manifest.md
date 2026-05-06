# PROJ-331 — File Manifest

## Production files (read-only references — DO NOT MODIFY)

| Path | LOC | Role |
|---|---:|---|
| `game/simulation/battle_state.py` | 805 | Battle state serialization/deserialization (5 dataclasses: ComponentState, ShipState, ProjectileState, BattleState, BattleResults) |
| `game/simulation/battle_controller.py` | 829 | Central battle orchestrator — setup, run visual/headless, save/load, retreat, reinforcement, results |
| `game/strategy/engine/conflict_resolution_engine.py` | 556 | Strategy-layer combat dispatch — detection, hex occupation, battle resolver invocation, fleet-destruction reporting |

## Existing tests (in scope to be aware of, NOT to be modified beyond explicit phase 2 additions)

| Path | LOC | Coverage of in-scope |
|---|---:|---|
| `tests/unit/simulation/test_battle_state_serialization.py` | 1395 | to_dict / from_dict / to_json / from_json round-trips for all 5 dataclasses + many edge cases |
| `tests/unit/simulation/test_battle_state_validation.py` | 233 | from_dict validation (missing keys, invalid types, bad component skip) |
| `tests/unit/simulation/managers/test_battle_state_manager.py` | (existing) | BattleStateManager → indirect coverage of capture_state path |
| `tests/unit/core/test_component_state.py` | (existing) | ComponentState basic |
| `tests/unit/simulation/battle_controller/test_initialization.py` | 134 | __init__, configure, start guard |
| `tests/unit/simulation/battle_controller/test_state.py` | 150 | save_state, load_state happy path, get_results basic |
| `tests/unit/simulation/battle_controller/test_execution.py` | 227 | start, update, run_ticks |
| `tests/unit/simulation/battle_controller/test_mechanics.py` | 327 | add_ships, add_ships_from_state, retreat, reinforcements |
| `tests/unit/simulation/battle_controller/test_outcome_emission.py` | (existing) | get_outcome / set_spec / _extract_outcome_on_battle_end happy path |
| `tests/unit/simulation/battle_controller/test_utilities.py` | 119 | queries, callbacks, reset |
| `tests/unit/strategy/conflict_resolution/test_core.py` | 350 | __init__, ConflictResult, seed counter, conflict detection |
| `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` | 322 | resolver injection, draw, seed pass-through, resolve_all_conflicts |
| `tests/unit/strategy/engine/test_conflict_resolution_event_replay.py` | 102 | replay_id event payload threading |
| `tests/unit/strategy/engine/test_conflict_round_budget.py` | 146 | _should_trigger_combat_for_fleet (5 cases) |

## New test files to create

| Path | Estimated tests | Concerns |
|---|---:|---|
| `tests/unit/simulation/test_battle_state_live_object_bridges.py` | ~16 | `from_ship`, `to_ship`, `from_component`, `from_projectile`, `to_projectile`, `capture_from_engine`, query methods (`get_ships_by_team`, `get_alive_ships`, `get_surviving_ships`, `get_escaped_ships`, `get_destroyed_ships`, `BattleResults.get_team_survivors`, `BattleResults.get_team_losses`) |
| `tests/unit/simulation/battle_controller/test_start_from_spec.py` | ~8 | The unified spec-in entry point, registry-provider fallback, RuntimeError on missing builder, ship_id_map population, initial_state capture |
| `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py` | ~13 | `_validate_tick_inputs`, `_log_combat_result` storm-name extraction, `_lookup_environmental_effects` empty-galaxy paths, `_collect_team_modifiers` exception path, `resolve_all_conflicts` tick=None, multi-fleet-per-empire ordering, `replay_unavailable_reason` plumbing, sole-survivor shortcut |

## Existing test files to extend (minimal edits)

| Path | New tests added | Why edit instead of new file |
|---|---:|---|
| `tests/unit/simulation/battle_controller/test_state.py` | ~4 | File is 150 LOC; well under ceiling; new tests are tightly thematically grouped with existing save/load tests (load_state projectile restoration, registries gating, partial-failure batches) |

## Cross-project file-overlap verification

| Project | Production files | Test files |
|---|---|---|
| 331 (this) | battle_state.py, battle_controller.py, conflict_resolution_engine.py | tests/unit/simulation/test_battle_state_live_object_bridges.py, tests/unit/simulation/battle_controller/test_start_from_spec.py, tests/unit/simulation/battle_controller/test_state.py (edit), tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py |
| 332 | turn_engine.py | tests/unit/strategy/engine/* (different test files; no overlap with 331's test_logging_and_lookups.py) |
| 333 | production_engine.py et al. | tests/unit/strategy/engine/* (different test files) |

**Overlap check:** Zero production-file overlap across 331/332/333. Test directory `tests/unit/strategy/engine/` is shared but per-test-file overlap is zero.
