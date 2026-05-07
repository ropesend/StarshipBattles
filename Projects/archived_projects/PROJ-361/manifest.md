# PROJ-361 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/adapters/simulation_adapter.py` | Production | Modify line ~258: thread injected `registries` into `run_battle.registry_provider`; preserve default-fallback. Update PROJ-306 comment block. |
| `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` | Test (new) | Two regression tests: (1) injected registries threads through; (2) None falls back to default provider. |

## Files referenced for context (not modified)

| File | Purpose |
|------|---------|
| `game/simulation/battle_runner.py` | `run_battle` signature owner; `registry_provider` is `Optional[IRegistryProvider]` (line 255-265) |
| `game/core/protocols/registry.py` | `IRegistryProvider` Protocol (line 7-39) |
| `game/core/registry.py` | `GameRegistries` already implements the Protocol (PROJ-211, lines 66-112) — no adapter needed |
| `game/strategy/engine/conflict_resolution_engine.py` | Sole production caller of `resolve_battle`; already threads `self._registries` (line 450-457) |
| `tests/conftest.py` | Reuse `fresh_registries` (line 189-224) for marker-design fixture |
