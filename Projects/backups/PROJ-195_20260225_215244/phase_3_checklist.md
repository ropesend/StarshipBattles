# Phase 3: Data Loader Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate BuilderDataLoader and WorkshopDataLoader tests from singleton to DI pattern

---

## Tasks

### Task 3.1: Migrate test_builder_data_loader.py [Medium]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [x] Add `fresh_registries` parameter to `setup_and_teardown` fixture in TestBuilderDataLoader class
- [x] Store as `self.registries = fresh_registries` in the fixture
- [x] Lines 60-61, 74-75, 88-89, 102-103, 114-115: Replace `registries=RegistryManager.instance()` with `registries=self.registries`
- [x] Line 127: Replace `registries=RegistryManager.instance()` with `registries=self.registries`
- [x] Line 130: `patch.object(RegistryManager.instance(), 'clear')` — Restructured to patch `game.ui.screens.workshop_data_loader.clear_registry` (where the function is imported)
- [x] Lines 155, 172: Replace in TestBuilderDataLoaderIntegration class (added `fresh_registries` to fixture)
- [x] Remove `from game.core.registry import RegistryManager` import (line 14)
- [x] Run tests — 8 passed

**Notes:** The `test_clear_registries_clears_registry_manager` test patches `clear_registry` where it's imported (in workshop_data_loader), not at the source module.

### Task 3.2: Migrate test_workshop_data_loader.py [Medium]
**File:** `tests/unit/workshop/test_workshop_data_loader.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_data_loader.py -v`

- [x] Add `fresh_registries` parameter to `data_loader_setup` fixture
- [x] Yield `custom_dir, default_dir, fresh_registries` from fixture
- [x] Lines 62, 77, 92, 107, 120: Replace `registries=RegistryManager.instance()` with `registries=registries` (from fixture)
- [x] Line 133: Replace `registries=RegistryManager.instance()` with `registries=registries`
- [x] Line 136: Restructured `patch.object` to patch `game.ui.screens.workshop_data_loader.clear_registry`
- [x] Lines 166, 184: Add `fresh_registries` parameter to `integration_setup` fixture and yield `data_dir, fresh_registries`
- [x] Remove `from game.core.registry import RegistryManager` import (line 13)
- [x] Run tests — 8 passed

**Notes:** Same pattern as Task 3.1 for the clear_registries test.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/builder/test_builder_data_loader.py tests/unit/workshop/test_workshop_data_loader.py` passes — 16 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
