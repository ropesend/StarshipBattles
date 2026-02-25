# Phase 3: Data Loader Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate BuilderDataLoader and WorkshopDataLoader tests from singleton to DI pattern

---

## Tasks

### Task 3.1: Migrate test_builder_data_loader.py [Medium]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [ ] Add `fresh_registries` parameter to `setup_and_teardown` fixture in TestBuilderDataLoader class
- [ ] Store as `self.registries = fresh_registries` in the fixture
- [ ] Lines 60-61, 74-75, 88-89, 102-103, 114-115: Replace `registries=RegistryManager.instance()` with `registries=self.registries`
- [ ] Line 127: Replace `registries=RegistryManager.instance()` with `registries=self.registries`
- [ ] Line 130: `patch.object(RegistryManager.instance(), 'clear')` — Restructure test to verify clear behavior without patching singleton directly
- [ ] Lines 155, 172: Replace in TestBuilderDataLoaderIntegration class (add `fresh_registries` to fixture or method)
- [ ] Remove `from game.core.registry import RegistryManager` import (line 14)
- [ ] Run tests

**Notes:**

### Task 3.2: Migrate test_workshop_data_loader.py [Medium]
**File:** `tests/unit/workshop/test_workshop_data_loader.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_data_loader.py -v`

- [ ] Add `fresh_registries` parameter to `data_loader_setup` fixture
- [ ] Yield `custom_dir, default_dir, fresh_registries` from fixture
- [ ] Lines 62, 77, 92, 107, 120: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries`
- [ ] Line 133: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries`
- [ ] Line 136: Restructure `patch.object(RegistryManager.instance(), 'clear')` same as Task 3.1
- [ ] Lines 166, 184: Add `fresh_registries` parameter to `integration_setup` fixture and replace singleton access
- [ ] Remove `from game.core.registry import RegistryManager` import (line 13)
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/builder/test_builder_data_loader.py tests/unit/workshop/test_workshop_data_loader.py` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
