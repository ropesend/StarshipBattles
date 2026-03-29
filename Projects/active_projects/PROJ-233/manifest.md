# PROJ-233 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/production_engine.py` | Production | Primary refactor target — enum, formula, spawn extraction, type hints |
| `game/strategy/engine/production_spawner.py` | Production | **New** — extracted spawn logic (~250 lines) |
| `game/strategy/engine/production_math.py` | Production | **New** — shared limiting-resource formula (~30 lines) |
| `game/strategy/engine/construction_forecast.py` | Production | Modified — use shared formula from production_math |
| `game/strategy/interfaces/engines.py` | Production | Modified — remove stale `harvesting_engine` param from IProductionEngine |
| `tests/unit/strategy/production_engine/test_spawning.py` | Test | Modified — update patch paths and call paths for spawner extraction |
| `tests/unit/strategy/test_engine_event_emission.py` | Test | Modified — update patch paths and call paths for spawner extraction |
| `tests/unit/strategy/engine/test_production_refactor.py` | Test | Modified — update mock assignments for spawner extraction |
| `tests/unit/strategy/engine/test_production_math.py` | Test | **New** — unit tests for shared formula |
| `tests/unit/strategy/mocks/mock_engines.py` | Test | Modified — remove stale `harvesting_engine` from MockProductionEngine |
| `tests/unit/strategy/interfaces/test_engine_interfaces.py` | Test | Modified — remove stale `harvesting_engine` from inline mock |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | Test | Modified — update patch.object targets for spawner extraction |
| `tests/unit/strategy/turn_engine/test_dependency_injection.py` | Test | Modified — remove stale `harvesting_engine` arg from mock call |
