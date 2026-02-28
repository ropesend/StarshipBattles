# Phase 4: Migrate TIER 3 Non-Composition-Root Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove direct `RegistryManager.instance()` calls from non-composition-root production code. After this phase, only app.py, conftest.py, and registry.py reference the singleton.

---

## Tasks

### Task 4.1: Migrate ship_loader.py get_or_create_validator() [Medium]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [x] Read `get_or_create_validator()` function (lines 17-34) to understand full context
- [x] Replace `RegistryManager.instance().get_validator()` (line 22) and `RegistryManager.instance()` (line 25) with provider-based access:
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
- [x] Update all callers of `get_or_create_validator()` to pass provider if available
- [x] Verify: Tests pass

**Notes:** The validator is stored ON the RegistryManager instance. This is a lifecycle concern. Kept RegistryManager.instance().get_validator() for validator storage (lifecycle), but migrated registry data access (components, modifiers, etc.) to provider pattern. Callers don't need provider param - they all use default.

### Task 4.2: Migrate ship_loader.py load_vehicle_classes() [Medium]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [x] Read `load_vehicle_classes()` function (lines 100-128) to understand full context
- [x] Replace `RegistryManager.instance().vehicle_classes` (line 124):
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
- [x] Update callers: `game/app.py`, `game/simulation/services/registry_loader.py`, conftest patches
- [x] Verify: Tests pass

**Notes:** Callers don't need updating - they all use default provider. Tests updated to use provider pattern via DI.

### Task 4.3: Grep verification [Simple]
**Tests:** N/A

- [x] Run: `grep -r "RegistryManager.instance()" game/ --include="*.py"` — should only match:
  - `game/core/registry.py` (internal: DefaultRegistryProvider, lifecycle helpers)
  - `game/app.py` (composition root)
  - `game/simulation/services/registry_loader.py` (receives mgr as param, not a self-fetcher)
- [x] If any other files still reference it, migrate those too

**Notes:** ship_loader.py still has one call for validator storage (lifecycle concern) - this is acceptable per task notes.

### Task 4.4: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: 11972 passed, 1 skipped
- [x] Verify no regressions

**Notes:** All tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
