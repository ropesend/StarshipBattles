# Phase 2.1: Caller Inventory for `reload_registries_from_directory`

Generated 2026-04-27.

## Production callers
**ZERO.** Verified via `grep -rn "reload_registries_from_directory(" game/ combat_lab/`.
The function is exported from `game/simulation/services/__init__.py` but never called outside of tests.

## Test callers (call sites where `registry_provider` will need to be threaded)

| Test file | Calls |
|-----------|-------|
| `tests/unit/core/test_registry_manager_reload.py` | 9 calls — all use the `fresh_registry` fixture (which calls `get_default_registry_manager()` and clears it). All pass the manager only — no provider |
| `tests/unit/simulation/services/test_registry_loader.py` | 14 calls — all use `mock_registry_manager` MagicMock; tests heavily mock `load_modifiers` / `load_components` / `load_vehicle_classes` so the provider only needs to be a non-None placeholder for these tests |

## Migration plan (Pattern A — required parameter)

1. Add `registry_provider: IRegistryProvider` (positional or keyword-only) to `reload_registries_from_directory`.
2. Replace the line-91 `provider = get_default_registry_provider()` call with the parameter.
3. Delete the `from game.core.registry import get_default_registry_provider` import.
4. Update all 23 test call sites to pass `registry_provider=...`.
   - `test_registry_manager_reload.py` — pass `get_default_registry_provider()` from the test fixture (test layer can call this)
   - `test_registry_loader.py` — pass a MagicMock or the real default provider (most tests mock the loader functions anyway)

## Caller-count vs plan estimate

Plan estimate: "limited callers" — accurate. **23 test callers, 0 production callers**, in 2 test files.
