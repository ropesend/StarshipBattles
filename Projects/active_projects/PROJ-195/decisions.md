# PROJ-195: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Keep `conftest.py` root `reset_game_state` singleton usage | Global test isolation mechanism — equivalent of a composition root for tests |
| 2026-02-24 | Keep `session_cache.py` singleton usage | Mirrors composition root pattern for test data loading |
| 2026-02-24 | Keep `test_singleton_and_thread.py` singleton usage | Tests specifically validate singleton behavior |
| 2026-02-24 | Keep `test_registry_features.py` singleton usage | Tests validate RegistryManager's direct property access |
| 2026-02-24 | Keep `test_deprecated_code_removed.py` singleton usage | Regression guards for deprecated function removal |
| 2026-02-24 | Keep `test_registry_provider.py` DefaultRegistryProvider tests | Validate DefaultRegistryProvider delegates to singleton |
| 2026-02-24 | Keep `test_service_injection.py` singleton assertions | Verify TestRegistryProvider isolation FROM singleton |
| 2026-02-24 | Keep `test_isolation.py` singleton usage | Validate reset_game_state properly clears singleton |
| 2026-02-24 | Keep `tests/unit/core/registry/conftest.py` singleton fixture | Fixture for registry tests needing direct singleton access |
| 2026-02-24 | Migrate data loader tests to `fresh_registries` | Cleaner DI pattern than passing `RegistryManager.instance()` |
| 2026-02-24 | Fix `ship_loader.py:34` to avoid raw singleton access | Already has `get_default_registry_provider()` import — use helper functions |
| 2026-02-24 | Fix `registry_loader.py:13` docstring only | Not executable code, just update the example |
| 2026-02-24 | Test baseline: 12,718 passed, 1 skipped, 0 failures | Established before any changes |
