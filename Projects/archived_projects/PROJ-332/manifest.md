# PROJ-332: File Manifest

## In-scope production file (no edits)

| Path | LOC | Role |
|------|-----|------|
| `game/strategy/engine/turn_engine.py` | 795 | Orchestrator: `TurnEngine` class, `_NullBattleResolver`, `create_default_turn_engine` factory, `TICKS_PER_TURN = 100` constant. |

## Existing test files in scope (inventoried, not edited)

| Path | Tests | Coverage area |
|------|-------|---------------|
| `tests/unit/strategy/turn_engine/conftest.py` | — (fixtures) | Shared `turn_engine`, `mock_empire`, `mock_galaxy`. Reused by all new files. |
| `tests/unit/strategy/turn_engine/test_turn_error_handling.py` | 8 | PROJ-251 `EnginePhaseError` contract. |
| `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py` | 8 | Snapshot capture/restore (module-level, not the engine integration). |
| `tests/unit/strategy/turn_engine/test_turn_processing.py` | 7 | `process_turn` structure + phase order + action engine integration. |
| `tests/unit/strategy/turn_engine/test_tick_mechanics.py` | ~9 | Movement + JOIN_FLEET. |
| `tests/unit/strategy/turn_engine/test_dependency_injection.py` | ~17 | DI + factory + 5 of 15 lazy properties. |
| `tests/unit/strategy/engine/test_turn_engine_progress_callback.py` | 4 | Issue #7 progress callback. |
| `tests/unit/strategy/engine/test_turn_engine_config.py` | 5 | **Out of scope** — covers `TurnEngineConfig` dataclass (D-009). |

**Total existing PROJ-332-relevant tests:** ~53.

## New test files (created in this project)

All under `tests/unit/strategy/turn_engine/`. Each file <500 LOC. One commit per file (D-006).

| File | Tests | Pins |
|------|-------|------|
| `test_turn_engine_init_precedence.py` | 4 | kwarg-overrides-config precedence, frozen-dict slot init, `race_registry` threading, `last_environmental_events` list init. |
| `test_turn_engine_lazy_properties.py` | 10 | Default-class assertion + idempotency for the 10 untested lazy properties; `SimulationBattleResolver` path when `ai_factory` present; `_NullBattleResolver` fallback when both `battle_resolver` and `ai_factory` are None (with WARNING log). |
| `test_turn_engine_phase_timing.py` | 3 | `_reset_phase_times` 14-key dict, `_time_phase` accumulates time on failure, `_time_phase` re-raises pre-wrapped `EnginePhaseError` unchanged. |
| `test_turn_engine_snapshot_integration.py` | 4 | Snapshot captured iff `session` provided; `restore` called iff snapshot+session; `dump_crash_snapshot` called iff snapshot+save_path; capture-failure swallowed and turn continues with `snapshot=None`. |
| `test_turn_engine_end_of_turn_order.py` | 3 | Call order organics → happiness → population → quality → atmosphere → water; locally-constructed Quality/Atmosphere/Water are invoked (via `patch`); end-of-turn-engine raise is NOT wrapped in `EnginePhaseError` (D-007 observation). |
| `test_turn_engine_phase_320_movement_diff.py` | 2 | `moved_fleet_ids` is the subset of fleets whose pre/post-movement location differs; empty empires → empty `moved_fleet_ids` set. |
| `test_turn_engine_validation.py` | 1 | `validate_colonize_order` delegates to `ColonizeValidator` with the right components. |

**Total new tests:** 27.

## Reference documents

- [`AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`](../../../AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md) — master plan + characterization rules.
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) — existing patterns (DI, fixtures).
- [`Projects/active_projects/PROJ-329A/plan.md`](../PROJ-329A/plan.md) — reference shape.
- [`Projects/active_projects/PROJ-251/`](../PROJ-251/) — origin of `EnginePhaseError` contract.
- [`Projects/active_projects/PROJ-320/`](../PROJ-320/) — origin of `moved_fleet_ids` derivation.
- [`Projects/active_projects/PROJ-285/`](../PROJ-285/) — origin of `set_current_turn` calls on harvest + production engines.
