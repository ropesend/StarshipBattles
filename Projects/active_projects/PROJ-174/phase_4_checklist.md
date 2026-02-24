# Phase 4: Migrate TIER 3 Non-Composition-Root Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove direct `RegistryManager.instance()` calls from non-composition-root production code. After this phase, only app.py, conftest.py, and registry.py reference the singleton.

---

## Tasks

### Task 4.1: Migrate ship_loader.py get_or_create_validator() [Medium]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [ ] Read `get_or_create_validator()` function (lines 17-34) to understand full context
- [ ] Replace `RegistryManager.instance().get_validator()` (line 22) and `RegistryManager.instance()` (line 25) with provider-based access:
  ```python
  # BEFORE:
  def get_or_create_validator():
      val = RegistryManager.instance().get_validator()
      if val is not None:
          return val
      mgr = RegistryManager.instance()
      ...

  # AFTER: Accept optional registry parameter
  def get_or_create_validator(registry_provider=None):
      if registry_provider is None:
          from game.core.registry import get_default_registry_provider
          registry_provider = get_default_registry_provider()
      # Use registry_provider.get_components(), etc.
      ...
  ```
- [ ] Update all callers of `get_or_create_validator()` to pass provider if available
- [ ] Verify: Tests pass

**Notes:** The validator is stored ON the RegistryManager instance. This is a lifecycle concern. May need to keep RegistryManager access for validator get/set specifically, or move validator storage elsewhere. Read code carefully before deciding approach.

### Task 4.2: Migrate ship_loader.py load_vehicle_classes() [Medium]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [ ] Read `load_vehicle_classes()` function (lines 100-128) to understand full context
- [ ] Replace `RegistryManager.instance().vehicle_classes` (line 124):
  ```python
  # BEFORE:
  classes = RegistryManager.instance().vehicle_classes

  # AFTER: Accept optional registry parameter
  def load_vehicle_classes(file_path, layers_file_path=None, registry_provider=None):
      if registry_provider is None:
          from game.core.registry import get_default_registry_provider
          registry_provider = get_default_registry_provider()
      classes = registry_provider.get_vehicle_classes()
      ...
  ```
- [ ] Update callers: `game/app.py`, `game/simulation/services/registry_loader.py`, conftest patches
- [ ] Verify: Tests pass

**Notes:** This function MUTATES the registry dict in place (appends loaded classes). With DI, provider.get_vehicle_classes() returns the same underlying dict, so mutations still work. But verify this.

### Task 4.3: Grep verification [Simple]
**Tests:** N/A

- [ ] Run: `grep -r "RegistryManager.instance()" game/ --include="*.py"` — should only match:
  - `game/core/registry.py` (internal: DefaultRegistryProvider, lifecycle helpers)
  - `game/app.py` (composition root)
  - `game/simulation/services/registry_loader.py` (receives mgr as param, not a self-fetcher)
- [ ] If any other files still reference it, migrate those too

**Notes:**

### Task 4.4: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: 12,023+ passed, 0 failed
- [ ] Verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
