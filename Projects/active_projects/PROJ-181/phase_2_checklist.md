# Phase 2: Migrate Deprecated Function Callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all test files that called `get_default_registries()` or `set_default_registries()` to use the provider pattern or fixtures.

---

## Tasks

### Task 2.1: Migrate simulation_tests callers of get_default_registries() [Medium]
**Files:**
- `simulation_tests/scenarios/base.py:356-361`
- `simulation_tests/tests/test_engine_physics.py:27-33`
- `simulation_tests/tests/test_smoke.py:28,41`

**Tests:** `pytest simulation_tests/ -x`

- [ ] In `base.py:361`: Replace `registries = get_default_registries()` with:
  ```python
  from game.core.registry import get_default_registry_provider, GameRegistries
  provider = get_default_registry_provider()
  registries = GameRegistries(
      components=provider.get_components(),
      modifiers=provider.get_modifiers(),
      vehicle_classes=provider.get_vehicle_classes(),
      resources=provider.get_resources(),
  )
  ```
- [ ] Remove `get_default_registries` from import on line 356
- [ ] In `test_engine_physics.py:32`: Same replacement pattern
- [ ] In `test_smoke.py:28,41`: Same replacement pattern for both calls
- [ ] Remove `get_default_registries` imports from all 3 files

**Notes:**

### Task 2.2: Migrate test_protocols_boundary.py [Simple]
**File:** `tests/unit/core/test_protocols_boundary.py:32-34`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py -x`

- [ ] Replace `get_default_registries()` with `fresh_registries` fixture parameter on the `simple_ship` fixture
- [ ] Remove deprecated import

**Notes:**

### Task 2.3: Migrate test_fleet_composition.py [Simple]
**File:** `tests/unit/builder/test_fleet_composition.py:28-31`
**Tests:** `pytest tests/unit/builder/test_fleet_composition.py -x`

- [ ] Remove `setup_default_registries` fixture that calls `set_default_registries()` (lines ~25-33)
- [ ] Verify tests pass without the fixture (root conftest already hydrates RegistryManager)
- [ ] Remove deprecated imports (`set_default_registries`, `registry` module reference)
- [ ] Remove `import warnings` if no longer needed

**Notes:**

### Task 2.4: Migrate test_workshop_context_di.py [Medium]
**File:** `tests/unit/builder/test_workshop_context_di.py`
**Tests:** `pytest tests/unit/builder/test_workshop_context_di.py -x`

- [ ] Lines 72, 83, 112, 131, 151, 161: All call `set_default_registries()` to test fallback behavior
- [ ] Verify WorkshopContext.__post_init__ uses `get_default_registry_provider()` (not deprecated getter)
- [ ] Rewrite tests to verify provider-based fallback instead of deprecated getter fallback
- [ ] Remove `restore_default_registries` fixture
- [ ] Remove `pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")`
- [ ] Remove deprecated imports

**Notes:** These tests test what happens when WorkshopContext doesn't receive registries. After this change, the fallback path uses the provider pattern, so tests should verify that path instead.

### Task 2.5: Migrate test_design_loader_adapter.py [Simple]
**File:** `tests/unit/ui/services/test_design_loader_adapter.py:84-89`
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py -x`

- [ ] Remove `set_default_registries(fresh_registries)` call (line 89)
- [ ] Remove `warnings.catch_warnings()` block (lines 86-89)
- [ ] Verify test still passes (adapter should use provider fallback, which reads from RegistryManager hydrated by root conftest)
- [ ] Remove deprecated imports

**Notes:**

### Task 2.6: Delete deprecated function tests [Simple]
**File:** `tests/unit/core/registry/test_registry_features.py:298-368`
**Tests:** `pytest tests/unit/core/registry/ -x`

- [ ] Delete `TestDefaultRegistries` class entirely (lines ~298-368)
- [ ] Remove `get_default_registries`/`set_default_registries` imports if no longer used
- [ ] Remove `@pytest.mark.filterwarnings("ignore::DeprecationWarning")` from that class

**Notes:** These tests tested the deprecated functions that no longer exist. Delete them entirely.

### Task 2.7: Update test_deprecated_code_removed.py [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -x`

- [ ] Change `test_get_default_registries_function_exists` (line 112-115) to verify function is REMOVED:
  ```python
  def test_get_default_registries_removed(self):
      """PROJ-181: get_default_registries() was fully eradicated."""
      assert not hasattr(registry_module, 'get_default_registries')
  ```
- [ ] Add similar test for `set_default_registries` removal
- [ ] Update `filterwarnings` markers if needed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` - all tests pass
- [ ] Run `pytest simulation_tests/` - all tests pass
- [ ] Grep: `grep -r "get_default_registries" tests/` returns zero hits outside comments
- [ ] Grep: `grep -r "set_default_registries" tests/` returns zero hits outside comments
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
