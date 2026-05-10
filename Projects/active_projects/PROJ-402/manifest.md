# PROJ-402 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/adapters/simulation_adapter.py | Production | Widen catch tuple to `(SimulationException, ValidationException)`. Add import if needed. |
| tests/unit/strategy/adapters/test_simulation_adapter.py | Test | Replace substituted-exception test with originally-required `ValidationException` injection. Keep `SimulationException` coverage too. |
| game/simulation/battle_runner.py | Production (read-only) | Source of `ValidationException` raise — context only. |
