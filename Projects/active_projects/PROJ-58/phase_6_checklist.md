# Phase 6: Registry DI Fallback Migration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all `get_default_registries()` callers to strict DI (constructor injection).

---

## Background
`get_default_registries()` is a module-level fallback that returns a global `GameRegistries` instance. The strict DI pattern (PROJ-50) requires `registries: GameRegistries` as a constructor parameter. The fallback creates an implicit global dependency that makes testing harder and couples code to module state.

## Migration Pattern
```python
# BEFORE (fallback pattern):
class MyService:
    def __init__(self, ...):
        self._registries = get_default_registries()

# AFTER (strict DI):
class MyService:
    def __init__(self, ..., *, registries: GameRegistries):
        if registries is None:
            raise TypeError("registries is required")
        self._registries = registries
```

For callers that create these services, they must pass `registries=` from their own context.

## Tasks

### Task 6.1: Audit All get_default_registries() Call Sites [Simple]
**Tests:** Research only
- [ ] Search for all `get_default_registries()` calls in production code
- [ ] For each call site, identify: Who creates this object? Where do THEY get registries from?
- [ ] Map the injection chain: app.py → screen → service → subsystem
- [ ] Identify any sites where the caller genuinely has no access to registries
- [ ] Document complete call chain in Notes
**Notes:**

### Task 6.2: Migrate UI Service Callers [Medium]
**Files:** `game/ui/services/ship_factory.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`
- [ ] `ship_factory.py` (~line 74): Add `registries` parameter to constructor, remove fallback
- [ ] Update all places that create ShipFactory to pass registries
- [ ] `design_loader_adapter.py` (~line 44): Add `registries` parameter, remove fallback
- [ ] Update all places that create DesignLoaderAdapter to pass registries
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:**

### Task 6.3: Migrate Simulation/Strategy Callers [Medium]
**Files:** `game/simulation/entities/ship_stats.py`, `game/strategy/engine/turn_engine.py`, `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/simulation/ tests/unit/strategy/ -x`
- [ ] `ship_stats.py` (~line 48): Accept registries parameter, remove fallback
- [ ] `turn_engine.py` (~line 129): Accept registries parameter, remove fallback
- [ ] `ship_instance.py` (~line 197): Accept registries parameter, remove fallback
- [ ] Update all callers of these classes to pass registries
- [ ] Run tests: `pytest tests/unit/simulation/ tests/unit/strategy/ -x`
**Notes:**

### Task 6.4: Migrate UI Screen Callers [Medium]
**Files:** `game/ui/screens/workshop_context.py`, `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`
- [ ] `workshop_context.py` (~line 78): Remove fallback, require registries in constructor
- [ ] `strategy_screen.py` (~line 365): Remove fallback, require registries
- [ ] Update all callers to pass registries from their context
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:**

### Task 6.5: Migrate Test Code Callers [Simple]
**Files:** Multiple test files using `get_default_registries()`
**Tests:** `pytest tests/ --testmon`
- [ ] Search all test files for `get_default_registries()`
- [ ] For each test: determine if registries come from a fixture or direct call
- [ ] Update tests to use fixtures that provide registries, or pass registries explicitly
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Test code may legitimately use the fallback for convenience. Evaluate case by case.

### Task 6.6: Remove or Restrict get_default_registries() [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -x`
- [ ] Verify zero production callers remain
- [ ] If test-only callers remain: Keep function but add comment "Test utility only"
- [ ] If zero callers: Remove `get_default_registries()` and `set_default_registries()` functions
- [ ] Also remove the module-level `_default_registries` variable
- [ ] Update `game/app.py` if it calls `set_default_registries()` - remove that call
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** This is the final cleanup. May need to keep for test infrastructure.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
- [ ] No remaining `get_default_registries()` calls in production code
- [ ] All services use strict DI with `registries` parameter
