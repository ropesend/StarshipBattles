# Phase 2: Migrate Core Singletons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 4 Core-layer singletons to ApplicationContext: RegistryManager, Profiler, StrategyMetadataService, ComponentCacheManager. One singleton per commit.

---

## Tasks

### Task 2.1: Migrate RegistryManager [Complex]
**Singleton file:** `game/core/registry.py`
**Production .instance() call sites (9 in registry.py wrappers + 2 external):**
- `game/core/registry.py:135` -- `RegistryManager.instance()` in `hydrate()` docstring context (used by session_cache)
- `game/core/registry.py:266` -- `freeze_registry()` wrapper
- `game/core/registry.py:278` -- `set_validator()` wrapper
- `game/core/registry.py:291` -- `get_validator()` wrapper
- `game/core/registry.py:304` -- `clear_registry()` wrapper
- `game/core/registry.py:326` -- `DefaultRegistryProvider.get_components()`
- `game/core/registry.py:330` -- `DefaultRegistryProvider.get_modifiers()`
- `game/core/registry.py:334` -- `DefaultRegistryProvider.get_vehicle_classes()`
- `game/core/registry.py:338` -- `DefaultRegistryProvider.get_resources()`
- `game/app.py:122` -- `RegistryManager.instance().resources`
- `game/app.py:137` -- `RegistryManager.instance()` for GameRegistries construction
- `game/ui/screens/strategy_detail_fmt.py:272` -- `RegistryManager.instance()`

**Test files that reset RegistryManager:**
- `tests/unit/core/registry/conftest.py` -- autouse `reset_registry` fixture (save/reset/restore)
- `tests/unit/core/registry/test_singleton_and_thread.py` -- 6 `.reset()` calls
- `tests/unit/core/resources_registry/test_integration.py` -- 1 `.reset()` call
- `tests/unit/core/test_registry_provider.py` -- 4 `.reset()` calls
- `tests/unit/core/test_pure_loaders.py` -- 2 `.reset()` calls
- `tests/infrastructure/session_cache.py` -- uses `.instance()` and `.clear()`

**TDD steps:**
- [ ] Write test: RegistryManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext.create_production() provides RegistryManager
- [ ] Write test: two ApplicationContext instances have independent RegistryManager instances
- [ ] Remove `metaclass=SingletonMeta` from RegistryManager class definition
- [ ] Remove `.instance()` classmethod usage (inherited from SingletonMeta) -- it no longer exists
- [ ] Update `DefaultRegistryProvider` to accept a RegistryManager instance instead of calling `.instance()`
- [ ] Update `freeze_registry()`, `clear_registry()`, `set_validator()`, `get_validator()` module functions to accept optional RegistryManager or use a module-level reference
- [ ] Update `game/app.py` to use `ctx.registry_manager` instead of `RegistryManager.instance()`
- [ ] Update `game/ui/screens/strategy_detail_fmt.py` to receive RegistryManager via DI
- [ ] Update `game/context.py` `create_production()` to create RegistryManager directly (not `.instance()`)
- [ ] Update all test files that call `RegistryManager.reset()` to use fresh instances
- [ ] Update `tests/unit/core/registry/conftest.py` reset_registry fixture
- [ ] Run: `pytest tests/unit/core/registry/ -v` -- all pass
- [ ] Run: `pytest tests/unit/core/ -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate RegistryManager from singleton to DI via ApplicationContext"

**Notes:** This is the most complex migration because RegistryManager has the most call sites and the `DefaultRegistryProvider` wrapper pattern. The module-level functions (freeze_registry, clear_registry, etc.) need a strategy -- either accept an explicit RegistryManager parameter, or maintain a module-level reference set by ApplicationContext during startup.

---

### Task 2.2: Migrate Profiler [Medium]
**Singleton file:** `game/core/profiling.py`
**Production .instance() call sites (6):**
- `game/core/profiling.py:112` -- `profile_block()` context manager
- `game/core/profiling.py:130` -- `profile_action()` decorator
- `game/core/profiling.py:24` -- docstring example
- `game/app.py:571` -- `Profiler.instance().toggle()`
- `game/app.py:729` -- `Profiler.instance().is_active()`
- `game/app.py:769` -- `Profiler.instance().save_history()`

**Test files that reset Profiler:**
- `tests/unit/core/profiling/conftest.py` -- autouse `reset_profiler` fixture
- `tests/unit/core/profiling/test_singleton_threading.py` -- 2 `.reset()` calls
- `tests/unit/core/profiling/test_decorators.py` -- 2 `.reset()` calls
- `tests/unit/performance/test_profiler_perf.py` -- 2 `.reset()` calls
- `tests/unit/core/test_profiling_edge_cases.py` -- 2 `.reset()` calls

**TDD steps:**
- [ ] Write test: Profiler can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides Profiler instance
- [ ] Remove `metaclass=SingletonMeta` from Profiler class definition
- [ ] Update `profile_block()` and `profile_action()` to accept optional Profiler parameter (fallback to module-level reference or no-op)
- [ ] Update `game/app.py` to use `ctx.profiler` instead of `Profiler.instance()`
- [ ] Update `game/context.py` `create_production()` to create Profiler directly
- [ ] Update all test files that call `Profiler.reset()` to use fresh instances
- [ ] Update `tests/unit/core/profiling/conftest.py` reset_profiler fixture
- [ ] Run: `pytest tests/unit/core/profiling/ -v` -- all pass
- [ ] Run: `pytest tests/unit/performance/ -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate Profiler from singleton to DI via ApplicationContext"

**Notes:** `profile_block()` and `profile_action()` are module-level convenience functions used as decorators. They need a way to access the Profiler without `.instance()`. Options: accept explicit parameter, use a module-level reference set at startup, or make them no-ops when no profiler is configured.

---

### Task 2.3: Migrate StrategyMetadataService [Medium]
**Singleton file:** `game/core/strategy_metadata.py`
**Production .instance() call sites (11):**
- `game/core/strategy_metadata.py:13,18,42` -- docstring examples and internal convenience
- `game/ai/strategy_manager.py:66` -- `StrategyMetadataService.instance().clear()`
- `game/ai/strategy_manager.py:105` -- `StrategyMetadataService.instance().set_strategies()`
- `game/ui/panels/ship_stats_renderer.py:258` -- strategy name lookup
- `game/ui/screens/setup_renderer.py:113,212` -- strategy name lookup
- `game/ui/screens/setup_screen.py:86` -- strategy keys list
- `game/ui/screens/builder/right_panel.py:115,203` -- strategy dropdown data
- `game/ui/screens/workshop_event_router.py:400` -- strategy service access
- `game/ui/screens/workshop_data_loader.py:107` -- `StrategyMetadataService.instance().clear()`

**Test files that reset StrategyMetadataService:**
- `tests/unit/core/test_strategy_metadata.py` -- 3 `.reset()` calls (setup/teardown)

**TDD steps:**
- [ ] Write test: StrategyMetadataService can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides StrategyMetadataService instance
- [ ] Remove `metaclass=SingletonMeta` from StrategyMetadataService class definition
- [ ] Update `game/ai/strategy_manager.py` to accept StrategyMetadataService via DI (constructor parameter or context)
- [ ] Update UI call sites to receive StrategyMetadataService via context or constructor injection
- [ ] Update `game/context.py` `create_production()` to create StrategyMetadataService directly
- [ ] Update `tests/unit/core/test_strategy_metadata.py` to use fresh instances
- [ ] Run: `pytest tests/unit/core/test_strategy_metadata.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate StrategyMetadataService from singleton to DI via ApplicationContext"

**Notes:** StrategyMetadataService is populated by StrategyManager (AI layer) and read by UI panels. The DI chain is: ApplicationContext creates both, StrategyManager receives a reference to StrategyMetadataService.

---

### Task 2.4: Migrate ComponentCacheManager [Simple]
**Singleton file:** `game/simulation/components/component_loader.py`
**Production .instance() call sites (2):**
- `game/simulation/components/component_loader.py:133` -- in `load_components()`
- `game/simulation/components/component_loader.py:232` -- in `load_modifiers()`

**Test files that reset ComponentCacheManager:**
- `tests/unit/entities/test_component_cache.py` -- 4 `.reset()` calls

**Convenience function:**
- `game/simulation/components/component_loader.py:41` -- `reset_component_caches()` calls `ComponentCacheManager.reset()`

**TDD steps:**
- [ ] Write test: ComponentCacheManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides ComponentCacheManager instance
- [ ] Remove `metaclass=SingletonMeta` from ComponentCacheManager class definition
- [ ] Update `load_components()` and `load_modifiers()` to accept optional ComponentCacheManager parameter
- [ ] Update `reset_component_caches()` function
- [ ] Update `game/context.py` `create_production()` to create ComponentCacheManager directly
- [ ] Update `tests/unit/entities/test_component_cache.py` to use fresh instances
- [ ] Run: `pytest tests/unit/entities/test_component_cache.py -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate ComponentCacheManager from singleton to DI via ApplicationContext"

**Notes:** Simplest migration -- only 2 production call sites, both in the same file.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] RegistryManager no longer uses SingletonMeta
- [ ] Profiler no longer uses SingletonMeta
- [ ] StrategyMetadataService no longer uses SingletonMeta
- [ ] ComponentCacheManager no longer uses SingletonMeta
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 4 separate commits, one per singleton
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
