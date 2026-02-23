# Phase 7: Registry DI Fallback Migration [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove RegistryManager backward-compat fallback chains from production callers, unify on `get_default_registries()` as the single service-locator pattern, and fix test infrastructure gap.

---

## Context
The DI chain flows from `game/app.py` (composition root) which calls `set_default_registries()` once at startup. Several production callers previously had backward-compat fallback chains that tried `get_default_registries()` first, then fell back to manually constructing `GameRegistries` from `RegistryManager.instance()`. These fallbacks were the actual backward-compat shims that PROJ-58 targets.

**Scope clarification:** Converting all 6 callers to strict DI (zero `get_default_registries()` calls) would require refactoring module-level instances, app.py construction sites, and GameSession. That's a separate effort (PROJ-50 continuation). PROJ-58 focuses on removing the RegistryManager fallback shims.

## Tasks

### Task 7.1: Audit All Call Sites (Verification) [Simple]
**Tests:** Research only
- [x] Verify `game/app.py:117` is the ONLY production `set_default_registries()` call
- [x] Confirm 6 production callers of `get_default_registries()`
- [x] Note: `game/simulation/entities/ship_stats.py:48` is in a docstring example only
- [x] Trace each caller's construction site to verify registries availability
- [x] Document findings: Most callers don't receive registries from constructors. Module-level instances, app.py, and GameSession would need significant refactoring for strict DI.
**Notes:** strategy_screen.py is a composition root — it's supposed to call get_default_registries().

### Task 7.2: Migrate UI Service Callers [Medium]
**Files:** `game/ui/services/ship_factory.py`, `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/ui/services/ -x`

**ship_factory.py:**
- [x] Added `__init__` with optional `registries` storage
- [x] Added `_get_registries()` helper: explicit param > stored instance > global default
- [x] Simplified `create_from_design` to use `_get_registries()` helper
- [x] Removed old RegistryManager fallback chain

**design_loader_adapter.py:**
- [x] Verified production caller (workshop_screen.py) already passes registries correctly
- [x] Left as-is — no RegistryManager fallback to remove
- [x] Tests pass

### Task 7.3: Migrate Strategy Layer Callers [Medium]
**Files:** `game/strategy/data/ship_instance.py`, `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -x`

**ship_instance.py:**
- [x] Removed `RegistryManager.instance()` fallback from `get_calculated_stats()`
- [x] Now uses direct `get_default_registries()` call (clean service locator)

**turn_engine.py:**
- [x] Removed `RegistryManager.instance()` fallback from constructor
- [x] Now uses direct `get_default_registries()` call when registries not injected
- [x] Removed unused `RegistryManager` import

### Task 7.4: Migrate UI Screen Callers [Medium]
**Files:** `game/ui/screens/workshop_context.py`, `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/builder/ -x`

**workshop_context.py:**
- [x] Removed complex create-from-loaded-data fallback in `__post_init__`
- [x] Simplified to clean try/except with `get_default_registries()` + pass on failure
- [x] Tests pass

**strategy_screen.py:**
- [x] Left as-is — this is a composition root, calling `get_default_registries()` is correct
- [x] No RegistryManager fallback to remove

### Task 7.5: Fix Test Infrastructure [Medium]
**Files:** `conftest.py` (root)
**Tests:** `pytest tests/ -x`
- [x] Discovered root conftest hydrates RegistryManager but never calls `set_default_registries()`
- [x] Added `set_default_registries()` call after hydration in `reset_game_state` fixture
- [x] Added cleanup (`_default_registries = None`) in post-test cleanup
- [x] All 6246 tests pass
**Notes:** This was the root cause of test failures when removing RegistryManager fallbacks.

### Task 7.6: Update Documentation [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -x`
- [x] Updated `_default_registries` comment (removed "transitional")
- [x] Updated `set_default_registries()` docstring (clarified composition root usage)
- [x] Updated `get_default_registries()` docstring (clarified service locator role)
- [x] Tests pass

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "All phases complete"
- [x] Zero RegistryManager backward-compat fallback chains in production code
