# PROJ-365 File Manifest

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/engine/turn_phase_registry.py` | Production (new) | 2 | `TickPhase` (frozen) + `TickContext` (mutable) + `DEFAULT_TICK_PHASE_LIST` (14 entries) |
| `game/strategy/engine/turn_engine.py` | Production (refactor) | 3 | `__init__` adds optional `tick_phases` kwarg; `_process_tick` body replaced with iteration loop. End-of-turn block (lines 571-602) untouched. Constructor and other methods untouched. |
| `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` | Test (new) | 1 | Golden phase-list characterization. Captures current order via instrumented `_time_phase`. Pins tick==1 logging gates. |
| `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` | Test (new) | 2 | `TickPhase` frozen, `TickContext` mutable, list count + order + uniqueness. |
| `tests/unit/strategy/turn_engine/test_turn_processing.py` | Test (verify or migrate) | 3 | Phase ordering test — verify still green; migrate to descriptor-list assertions if needed. |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` | Test (verify) | 3 | PROJ-320 invariant — must continue passing without modification. |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` | Test (verify) | 3 | `_time_phase` accumulator semantics — must continue passing. |

## Files referenced for context (not modified)

| File | Purpose |
|------|---------|
| `game/strategy/engine/turn_engine_config.py` | PROJ-259 engine bundle — orthogonal, untouched |
| `game/strategy/interfaces/engines.py` | 15 engine interfaces — unchanged |
| `tests/unit/strategy/mocks/mock_engines.py` | IXxx mock implementations — reused unchanged |
| `tests/unit/strategy/turn_engine/conftest.py` | `turn_engine`, `mock_empire`, `mock_galaxy`, `mock_fleet` fixtures — reused |
| `game/strategy/engine/planet_modifier_effect_engine.py` | Lazily-imported phase 1.8 engine; descriptor refactor evaluates module-level hoist (Phase 3 Task 3.5) |
| `game/strategy/engine/game_session.py:226` | Production caller of `process_turn` — unchanged |
