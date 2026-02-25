# Phase 2: Migrate Deprecated Function Callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all test files that called `get_default_registries()` or `set_default_registries()` to use the provider pattern or fixtures.

---

## Tasks

### Task 2.1: Migrate simulation_tests callers of get_default_registries() [Medium]
**Files:**
- `simulation_tests/scenarios/base.py:356-361`
- `simulation_tests/tests/test_engine_physics.py:27-33`
- `simulation_tests/tests/test_smoke.py:28,41`

**Tests:** `pytest simulation_tests/ -x`

- [x] In `base.py:361`: Replace `registries = get_default_registries()` with provider pattern
- [x] Remove `get_default_registries` from import on line 356
- [x] In `test_engine_physics.py:32`: Same replacement pattern
- [x] In `test_smoke.py:28,41`: Same replacement pattern for both calls
- [x] Remove `get_default_registries` imports from all 3 files

**Notes:** All 3 files migrated to use get_default_registry_provider() + GameRegistries pattern.

### Task 2.2: Migrate test_protocols_boundary.py [Simple]
**File:** `tests/unit/core/test_protocols_boundary.py:32-34`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py -x`

- [x] Already migrated in Phase 1 expansion (uses fresh_registries fixture)

**Notes:** Completed in Phase 1 - only comment reference remains.

### Task 2.3: Migrate test_fleet_composition.py [Simple]
**File:** `tests/unit/builder/test_fleet_composition.py:28-31`
**Tests:** `pytest tests/unit/builder/test_fleet_composition.py -x`

- [x] Already migrated in Phase 1 expansion

**Notes:** Completed in Phase 1 - only comment reference remains.

### Task 2.4: Migrate test_workshop_context_di.py [Medium]
**File:** `tests/unit/builder/test_workshop_context_di.py`
**Tests:** `pytest tests/unit/builder/test_workshop_context_di.py -x`

- [x] Already migrated in Phase 1 expansion

**Notes:** Completed in Phase 1 - only comment reference remains.

### Task 2.5: Migrate test_design_loader_adapter.py [Simple]
**File:** `tests/unit/ui/services/test_design_loader_adapter.py:84-89`
**Tests:** `pytest tests/unit/ui/services/test_design_loader_adapter.py -x`

- [x] Already migrated in Phase 1 expansion

**Notes:** Completed in Phase 1 - only comment reference remains.

### Task 2.6: Delete deprecated function tests [Simple]
**File:** `tests/unit/core/registry/test_registry_features.py:298-368`
**Tests:** `pytest tests/unit/core/registry/ -x`

- [x] Already deleted in Phase 1 expansion

**Notes:** Completed in Phase 1 - TestDefaultRegistries class deleted.

### Task 2.7: Update test_deprecated_code_removed.py [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -x`

- [x] Already updated in Phase 1 expansion - tests verify functions are REMOVED

**Notes:** Completed in Phase 1.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - all tests pass (12373 passed, 1 skipped)
- [x] Run `pytest simulation_tests/tests/test_smoke.py simulation_tests/tests/test_engine_physics.py` - 8 passed
- [x] Grep: `grep -r "get_default_registries" tests/` - only comments/regression tests
- [x] Grep: `grep -r "set_default_registries" tests/` - only comments
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
