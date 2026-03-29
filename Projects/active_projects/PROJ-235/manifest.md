# PROJ-235 File Manifest

> Generated during Protocol 01. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/turn_engine.py` | Production | Add TICKS_PER_TURN constant, _time_phase() helper, _log_empire_state() helper; refactor _process_tick() and process_turn() |
| `game/strategy/engine/production_engine.py` | Production | Replace local TICKS_PER_TURN definition with import from turn_engine (1 line change) |

## Test Files (Read-Only — Not Modified)

| File | Role |
|------|------|
| `tests/unit/strategy/turn_engine/test_turn_processing.py` | CRITICAL: phase order verification |
| `tests/unit/strategy/turn_engine/test_tick_mechanics.py` | Tick mechanics |
| `tests/unit/strategy/turn_engine/test_dependency_injection.py` | DI verification |
| `tests/unit/strategy/turn_engine/conftest.py` | Test fixtures |
| `tests/integration/strategy/turn_engine/test_basics.py` | Integration basics |
| `tests/integration/strategy/turn_engine/test_harvesting.py` | Harvesting integration |
| `tests/integration/strategy/turn_engine/test_maintenance.py` | Maintenance integration |
| `tests/integration/strategy/turn_engine/test_resources.py` | Resource integration |
| `tests/integration/strategy/turn_engine/test_resupply.py` | Resupply integration |
| `tests/integration/strategy/turn_engine/test_components.py` | Component integration |
| `tests/integration/gameplay_loop/test_turn_execution.py` | Full gameplay loop |
| `tests/unit/strategy/engine/test_production_refactor.py` | Production engine |
