# Phase 7: Remove Core Singleton Shims

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove `.instance()` and `.reset()` compatibility shims from the 4 Core-layer services: RegistryManager, Profiler, StrategyMetadataService, ComponentCacheManager. Replace every call site with direct construction or module-level accessor.

---

## Tasks

### Task 7.1: Remove RegistryManager shims [Complex]
**Files:** `game/core/registry.py` + ~98 test call sites
**Shim calls:** 1 production, 98 test (.instance() + .reset())

- [ ] Grep all `RegistryManager.instance()` and `RegistryManager.reset()` in tests/ — catalog every file
- [ ] Update each test file to use direct `RegistryManager()` construction or `get_default_registry_manager()`
- [ ] Update `tests/unit/core/registry/conftest.py` — replace any `.instance()` with direct construction
- [ ] Update `tests/unit/core/test_registry_provider.py` — replace `.instance()` / `.reset()` with fresh instances
- [ ] Update `tests/unit/core/test_pure_loaders.py` — replace `.reset()` / `.instance()`
- [ ] Update `tests/unit/core/test_service_injection.py` — replace `.instance()`
- [ ] Update `tests/unit/core/test_isolation.py` — replace `.instance()`
- [ ] Update `tests/unit/core/registry/test_singleton_and_thread.py` — replace `.instance()` / `.reset()`
- [ ] Update `tests/unit/core/test_registry_manager_reload.py` — replace `.instance()`
- [ ] Sweep remaining: `grep -rn "RegistryManager\.\(instance\|reset\)()" tests/` — must be zero
- [ ] Remove `instance()` and `reset()` classmethods from RegistryManager class in `game/core/registry.py`
- [ ] Keep `_default_manager`, `set_default_registry_manager()`, `get_default_registry_manager()` — used by module-level wrappers and DefaultRegistryProvider
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove RegistryManager .instance()/.reset() shims"

**Notes:** RegistryManager is special — `get_default_registry_manager()` and `set_default_registry_manager()` MUST remain because module-level wrapper functions (freeze_registry, clear_registry, etc.) and DefaultRegistryProvider use them. Only the `.instance()` / `.reset()` shims on the class are removed.

---

### Task 7.2: Remove Profiler shims [Medium]
**Files:** `game/core/profiling.py` + ~56 test call sites
**Shim calls:** 5 production (profile_action, profile_block, app.py), 56 test

- [ ] Update `game/core/profiling.py` `profile_action()` — use `_default_profiler` directly instead of `.instance()`
- [ ] Update `game/core/profiling.py` `profile_block()` — same
- [ ] Update `game/app.py` — replace `Profiler.instance()` with `self.ctx.profiler`
- [ ] Grep all `Profiler.instance()` and `Profiler.reset()` in tests/ — catalog every file
- [ ] Update `tests/unit/core/profiling/conftest.py` — replace `.reset()` with fresh construction
- [ ] Update `tests/unit/core/profiling/test_singleton_threading.py` — replace `.instance()` / `.reset()`
- [ ] Update `tests/unit/core/profiling/test_decorators.py` — replace `.reset()` / `.instance()`
- [ ] Update `tests/unit/performance/test_profiler_perf.py` — replace `.reset()` / `.instance()`
- [ ] Update `tests/unit/core/test_profiling_edge_cases.py` — replace `.reset()` / `.instance()`
- [ ] Sweep remaining: `grep -rn "Profiler\.\(instance\|reset\)()" tests/` — must be zero
- [ ] Remove `instance()` and `reset()` classmethods from Profiler
- [ ] Keep `_default_profiler` — used by profile_action/profile_block
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove Profiler .instance()/.reset() shims"

**Notes:** `profile_action()` and `profile_block()` are module-level convenience functions used as decorators. They access `_default_profiler` directly (not via ApplicationContext).

---

### Task 7.3: Remove StrategyMetadataService shims [Medium]
**Files:** `game/core/strategy_metadata.py` + ~18 test call sites
**Shim calls:** 12 production, 18 test

- [ ] Grep all `StrategyMetadataService.instance()` in game/ — catalog every file
- [ ] Update `game/ai/strategy_manager.py` — StrategyManager.clear() calls `.instance().clear()`. Use module-level reference or constructor injection.
- [ ] Update UI call sites (ship_stats_renderer, setup_renderer, setup_screen, right_panel, workshop_event_router, workshop_data_loader) — receive via context or constructor
- [ ] Grep all `StrategyMetadataService.instance()` / `.reset()` in tests/
- [ ] Update `tests/unit/core/test_strategy_metadata.py` — replace with direct construction
- [ ] Sweep remaining: `grep -rn "StrategyMetadataService\.\(instance\|reset\)()" tests/` — must be zero
- [ ] Remove `instance()` and `reset()` classmethods from StrategyMetadataService
- [ ] Decide: keep or remove `_default_service` (keep if module-level access still needed by StrategyManager)
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove StrategyMetadataService .instance()/.reset() shims"

---

### Task 7.4: Remove ComponentCacheManager shims [Simple]
**Files:** `game/simulation/components/component_loader.py` + ~16 test call sites
**Shim calls:** 2 production, 16 test

- [ ] Update `load_components()` and `load_modifiers()` in component_loader.py — use `_default_cache_manager` directly
- [ ] Update `reset_component_caches()` — reset module-level reference directly
- [ ] Update `conftest.py` — verify ComponentCacheManager usage doesn't use `.instance()`
- [ ] Grep and update all test `.instance()` / `.reset()` calls (16 sites)
- [ ] Remove `instance()` and `reset()` classmethods from ComponentCacheManager
- [ ] Keep `_default_cache_manager` — used by load functions and reset_component_caches
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove ComponentCacheManager .instance()/.reset() shims"

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "\(RegistryManager\|Profiler\|StrategyMetadataService\|ComponentCacheManager\)\.\(instance\|reset\)()" game/ tests/` — zero results
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 4 commits (one per class)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
