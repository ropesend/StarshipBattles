# Phase 1: Create ApplicationContext (Wrapper)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create ApplicationContext as a thin wrapper around existing singletons. All existing code continues to work via .instance(). This phase introduces the container and its tests without changing any existing behavior.

---

## Tasks

### Task 1.1: Write tests for ApplicationContext [Medium]
**File:** `tests/unit/core/test_application_context.py` (new)
**Tests:** `pytest tests/unit/core/test_application_context.py -v`

- [ ] Create test file `tests/unit/core/test_application_context.py`
- [ ] `TestApplicationContextInit`: test constructor accepts all 10 service instances
- [ ] `TestApplicationContextInit`: test all attributes are accessible (registry_manager, profiler, strategy_metadata, component_cache, strategy_manager, asset_manager, sprite_manager, ship_theme_manager, screenshot_manager, game_settings)
- [ ] `TestApplicationContextInit`: test constructor with mock objects (not real singletons)
- [ ] `TestCreateProduction`: test `create_production()` returns ApplicationContext instance
- [ ] `TestCreateProduction`: test `create_production()` populates all attributes (none are None)
- [ ] `TestCreateProduction`: test each attribute is the correct type
- [ ] `TestCreateTest`: test `create_test()` returns ApplicationContext instance
- [ ] `TestCreateTest`: test `create_test()` populates all attributes (none are None)
- [ ] `TestCreateTest`: test `create_test(**overrides)` allows overriding specific services
- [ ] `TestCreateTest`: test override replaces only the specified service, others are defaults
- [ ] `TestNotSingleton`: test two calls to `create_test()` return different instances
- [ ] `TestNotSingleton`: test two contexts have independent service instances
- [ ] Run tests -- confirm they ALL FAIL (class doesn't exist yet)

**Notes:**

---

### Task 1.2: Implement ApplicationContext class [Medium]
**File:** `game/context.py` (new)
**Tests:** `pytest tests/unit/core/test_application_context.py -v`

- [ ] Create `game/context.py` with `ApplicationContext` class
- [ ] Implement `__init__` accepting all 10 service parameters with type hints
- [ ] Implement `create_production()` classmethod using late imports and `.instance()` calls
- [ ] Implement `create_test(**overrides)` classmethod creating lightweight instances
- [ ] Add `__all__ = ['ApplicationContext']`
- [ ] Run tests -- confirm they all pass
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass, 0 failures

**Notes:**

---

### Task 1.3: Integrate ApplicationContext in app.py [Simple]
**File:** `game/app.py`
**Tests:** Full test suite (no new tests needed -- this is a composition root change)

- [ ] Import ApplicationContext in `game/app.py`
- [ ] Create `self.ctx = ApplicationContext.create_production()` in `Game.__init__()` early in initialization
- [ ] Verify: existing `.instance()` calls in app.py still work (they will, singletons still exist)
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass, 0 failures

**Notes:** This task only creates the context. It does NOT replace any .instance() calls yet. That happens in Phases 2-4.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/context.py` exists with ApplicationContext class
- [ ] `tests/unit/core/test_application_context.py` exists and all tests pass
- [ ] `game/app.py` creates an ApplicationContext instance
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
