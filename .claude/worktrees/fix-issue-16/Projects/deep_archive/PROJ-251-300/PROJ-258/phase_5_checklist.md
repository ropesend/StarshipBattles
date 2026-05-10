# Phase 5: Simplify conftest.py and Session Cache

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplify the test infrastructure now that all singletons are migrated. Refactor conftest.py fixtures and SessionRegistryCache to use ApplicationContext.create_test(). Remove scattered singleton reset logic.

---

## Tasks

### Task 5.1: Refactor root conftest.py [Complex]
**File:** `tests/conftest.py`
**Tests:** Full test suite

- [ ] Write test: ApplicationContext.create_test() returns context with all services
- [ ] Add `test_context` fixture (function-scoped) providing `ApplicationContext.create_test()`
- [ ] Refactor `session_registries` fixture to use ApplicationContext internally (or keep it for backward compat)
- [ ] Refactor `fresh_registries` fixture to use ApplicationContext.create_test().registry_manager
- [ ] Verify `minimal_registries` and `mock_registries` fixtures still work
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass

**Notes:** The `session_registries` and `fresh_registries` fixtures are widely used. They should continue to work, potentially backed by ApplicationContext internally. Add the new `test_context` fixture as an alternative for tests that need the full context.

---

### Task 5.2: Simplify per-directory conftest.py files [Medium]
**Files:**
- `tests/unit/core/registry/conftest.py` -- `reset_registry` autouse fixture (~60 lines)
- `tests/unit/core/profiling/conftest.py` -- `reset_profiler` autouse fixture
- `tests/integration/ai_strategy/conftest.py` -- `setup_game_data` autouse fixture
- `tests/unit/core/resources_registry/conftest.py` -- autouse fixture

- [ ] Simplify `tests/unit/core/registry/conftest.py` -- replace save/reset/restore logic with fresh RegistryManager construction
- [ ] Simplify `tests/unit/core/profiling/conftest.py` -- replace Profiler.reset() with fresh construction
- [ ] Simplify `tests/integration/ai_strategy/conftest.py` -- replace StrategyManager.instance()/clear() with fresh construction
- [ ] Review `tests/unit/core/resources_registry/conftest.py` for singleton cleanup opportunities
- [ ] Run: `pytest tests/unit/core/registry/ -v` -- all pass
- [ ] Run: `pytest tests/unit/core/profiling/ -v` -- all pass
- [ ] Run: `pytest tests/integration/ai_strategy/ -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass

**Notes:** The registry conftest.py currently has ~60 lines of save/reset/restore logic for RegistryManager. After migration, this becomes creating a fresh RegistryManager instance, which is a few lines.

---

### Task 5.3: Refactor SessionRegistryCache [Medium]
**File:** `tests/infrastructure/session_cache.py`
**Tests:** `pytest tests/ -v` (used transitively by session_registries fixture)

- [ ] Refactor SessionRegistryCache to not depend on RegistryManager.instance() or StrategyManager.instance()
- [ ] SessionRegistryCache should create its own RegistryManager and StrategyManager instances for data loading
- [ ] Or: Replace SessionRegistryCache with a simpler mechanism using ApplicationContext
- [ ] Remove the manual singleton pattern (cls._instance, cls._lock) if ApplicationContext manages the cache
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: simplify test infrastructure to use ApplicationContext"

**Notes:** SessionRegistryCache is a manual singleton (not using SingletonMeta) that loads data via RegistryManager.instance() and StrategyManager.instance(). After those singletons are migrated, SessionRegistryCache must be updated to create instances directly.

---

### Task 5.4: Remove orphaned singleton reset calls [Simple]
**Tests:** Full test suite

- [ ] Grep for remaining `.reset()` calls on migrated singletons across all test files
- [ ] Remove or replace any remaining `.reset()` calls with fresh instance construction
- [ ] Grep for remaining `.instance()` calls on migrated singletons across all files
- [ ] Remove or replace any remaining `.instance()` calls
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass

**Notes:** After the per-singleton migrations in Phases 2-4, there may be straggler `.reset()` or `.instance()` calls missed during individual migrations. This task does a comprehensive sweep.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Root conftest.py provides `test_context` fixture
- [ ] Per-directory conftest.py files simplified (no more singleton save/reset/restore)
- [ ] SessionRegistryCache no longer depends on singleton .instance() calls
- [ ] Zero `.reset()` calls on migrated singletons remain in test code
- [ ] Zero `.instance()` calls on migrated singletons remain in any code
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
