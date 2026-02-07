# Phase 7: Registry DI Fallback Migration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 6 production `get_default_registries()` callers to strict DI (constructor injection), then restrict the fallback function.

---

## Context
The DI chain flows from `game/app.py` (composition root) which calls `set_default_registries()` once at startup. Six production callers use `get_default_registries()` as a fallback when no registries are injected via constructor. The goal is to ensure all production callers receive registries via constructor parameters (strict DI pattern from PROJ-50).

## Tasks

### Task 7.1: Audit All Call Sites (Verification) [Simple]
**Tests:** Research only
- [ ] Verify `game/app.py:117` is the ONLY production `set_default_registries()` call
- [ ] Confirm these 6 production callers of `get_default_registries()`:
  - `game/ui/services/ship_factory.py:74` (legacy fallback branch)
  - `game/ui/services/design_loader_adapter.py:44` (parameter check fallback)
  - `game/ui/screens/workshop_context.py:78` (lazy init with fallback)
  - `game/ui/screens/strategy_screen.py:370` (direct call, no fallback)
  - `game/strategy/engine/turn_engine.py:128-134` (constructor fallback)
  - `game/strategy/data/ship_instance.py:197` (from_dict fallback)
- [ ] Note: `game/simulation/entities/ship_stats.py:48` is in a docstring example only - not an active call site
- [ ] Trace each caller's construction site to verify registries ARE available in the call chain
- [ ] Document in Notes which callers already receive registries from their constructors
**Notes:**

### Task 7.2: Migrate UI Service Callers [Medium]
**Files:** `game/ui/services/ship_factory.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/ -x`

**ship_factory.py:**
- [ ] Verify `ShipFactory.__init__` already accepts `registries` parameter
- [ ] Trace who constructs `ShipFactory` - confirm registries are always passed
- [ ] Remove the `else` branch at ~line 71-74 that calls `get_default_registries()`
- [ ] If registries are missing, raise `TypeError` (strict DI pattern) instead of falling back
- [ ] Remove `from game.core.registry import get_default_registries` import if no longer needed

**design_loader_adapter.py:**
- [ ] Verify `DesignLoaderAdapter.__init__` already accepts `registries` parameter
- [ ] Trace who constructs `DesignLoaderAdapter` - confirm registries are always passed
- [ ] Remove the `if registries is None: ... get_default_registries()` fallback at ~lines 41-45
- [ ] Make `registries` a required parameter (remove `Optional` / default `None`)
- [ ] Remove `from game.core.registry import get_default_registries` import if no longer needed
- [ ] Run tests: `pytest tests/unit/ui/services/ -x`

### Task 7.3: Migrate Strategy Layer Callers [Medium]
**Files:** `game/strategy/data/ship_instance.py`, `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -x`

**ship_instance.py:**
- [ ] Examine `Ship.from_dict()` at ~line 194-203 - this is a `@classmethod`, not a constructor
- [ ] Check if callers of `Ship.from_dict()` already pass `registries` parameter
- [ ] If so: remove the try/except fallback to `get_default_registries()` and `RegistryManager`
- [ ] If not: trace back to find where registries should be threaded through
- [ ] Run tests: `pytest tests/unit/strategy/ -x`

**turn_engine.py:**
- [ ] Verify `TurnEngine.__init__` already has `registries` parameter
- [ ] Trace who constructs `TurnEngine` - confirm registries are always passed
- [ ] Remove the `else` fallback branch at ~lines 128-134
- [ ] Make `registries` a required parameter
- [ ] Run tests: `pytest tests/unit/strategy/ tests/integration/ -x`

### Task 7.4: Migrate UI Screen Callers [Medium]
**Files:** `game/ui/screens/workshop_context.py`, `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ -x`

**workshop_context.py:**
- [ ] Examine `WorkshopContext.__getattr__` lazy init at ~line 75-84
- [ ] Verify `WorkshopContext.__init__` already accepts `registries` parameter
- [ ] Trace who constructs `WorkshopContext` - confirm registries are always passed
- [ ] Remove the `get_default_registries()` fallback in `__getattr__`
- [ ] If registries not set during init, raise `TypeError` instead
- [ ] Run tests: `pytest tests/unit/builder/ -x`

**strategy_screen.py:**
- [ ] Line 370: `SimulationDesignLoader(registries=get_default_registries())`
- [ ] Check if `strategy_screen` already has `self.registries` or `self._registries` available
- [ ] If yes: replace `get_default_registries()` with `self.registries`
- [ ] If no: thread registries from the screen's constructor (trace from `game/app.py` screen creation)
- [ ] Run tests: `pytest tests/unit/ui/ -x`

### Task 7.5: Update Test Code [Medium]
**Files:** Multiple test files
**Tests:** `pytest tests/ --testmon`
- [ ] Search for all test files calling `get_default_registries()` or `set_default_registries()`
- [ ] Update test fixtures that set up default registries:
  - `tests/unit/builder/test_fleet_composition.py` (autouse fixture)
  - `tests/unit/builder/test_workshop_context_di.py` (restoration fixture + 6 test calls)
  - `tests/unit/ui/services/test_design_loader_adapter.py` (1 test call)
  - `tests/unit/core/registry/test_registry_features.py` (2 test calls)
- [ ] Tests that test the fallback behavior itself should be updated to test strict-DI-raises-on-missing instead
- [ ] Keep `set_default_registries()` available in test fixtures that need it for integration tests
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Some tests explicitly test the backward compat behavior. These should be rewritten to test the new strict behavior (TypeError on missing registries).

### Task 7.6: Restrict get_default_registries() [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -x`
- [ ] Verify NO production code still calls `get_default_registries()` (only test code and `simulation_tests/` framework)
- [ ] Add a deprecation comment: `# Used only by test framework. Production code should use constructor injection.`
- [ ] Keep `set_default_registries()` for `app.py` composition root (still needed for test setup)
- [ ] Keep `get_default_registries()` function (needed by `simulation_tests/scenarios/base.py` and test fixtures)
- [ ] Update the docstring to reflect its restricted purpose
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** We don't delete these functions because the test framework and integration tests legitimately need global registry access. The goal is zero PRODUCTION callers.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete"
- [ ] Zero production callers of `get_default_registries()` (test code is OK)
