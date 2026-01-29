# Phase 5: Registry Access Consolidation (AR-02, AR-09, AR-011)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Complete DI migration and remove deprecated utility functions

---

## Prerequisites
- [ ] Phases 2A-2C complete (UI services in place)
- [ ] Phase 4 complete (TurnEngine DI)

## Background

**Deprecated Functions (PROJ-38):**
- `get_component_registry()` - DEPRECATED
- `get_modifier_registry()` - DEPRECATED
- `get_vehicle_classes()` - DEPRECATED
- `get_validator()` - DEPRECATED
- `get_resource_registry()` - DEPRECATED

**Replacement Pattern:**
```python
# Old (deprecated)
from game.core.registry import get_component_registry
components = get_component_registry()

# New (recommended)
from game.core.registry import get_default_registry_provider
provider = get_default_registry_provider()
components = provider.get_components()
```

---

## Tasks

### Task 5.1: Audit Deprecated Function Usage [Simple]
**Files:** Entire codebase
**Tests:** N/A (analysis)

- [ ] Run grep for `get_component_registry`:
  ```bash
  grep -rn "get_component_registry" game/ tests/
  ```
- [ ] Run grep for `get_modifier_registry`:
  ```bash
  grep -rn "get_modifier_registry" game/ tests/
  ```
- [ ] Run grep for `get_vehicle_classes`:
  ```bash
  grep -rn "get_vehicle_classes" game/ tests/
  ```
- [ ] Document all occurrences in findings/phase_5_audit.md
- [ ] Categorize by: game code vs test code

**Notes:**

---

### Task 5.2: Update Game Code - Component Registry [Medium]
**Files:** All game files using get_component_registry
**Tests:** `pytest tests/unit/`

- [ ] For each occurrence in game/ code:
  - Replace with `get_default_registry_provider().get_components()`
  - Or inject registry via constructor
- [ ] Verify no deprecation warnings from these files
- [ ] Run related tests

**Notes:**

---

### Task 5.3: Update Game Code - Modifier Registry [Medium]
**Files:** All game files using get_modifier_registry
**Tests:** `pytest tests/unit/`

- [ ] For each occurrence in game/ code:
  - Replace with `get_default_registry_provider().get_modifiers()`
  - Or inject registry via constructor
- [ ] Verify no deprecation warnings from these files
- [ ] Run related tests

**Notes:**

---

### Task 5.4: Update Game Code - Vehicle Classes [Medium]
**Files:** All game files using get_vehicle_classes
**Tests:** `pytest tests/unit/`

- [ ] For each occurrence in game/ code:
  - Replace with `get_default_registry_provider().get_vehicle_classes()`
  - Or inject registry via constructor
- [ ] Verify no deprecation warnings from these files
- [ ] Run related tests

**Notes:**

---

### Task 5.5: Update Test Code [Medium]
**Files:** All test files using deprecated functions
**Tests:** Self-referential

- [ ] For test files, consider:
  - Using TestRegistryProvider for isolation
  - Using get_default_registry_provider for integration tests
- [ ] Update test helpers/fixtures if needed
- [ ] Run all updated tests

**Notes:**

---

### Task 5.6: Audit Singleton .instance() Usage [Simple]
**Files:** Entire codebase
**Tests:** N/A (analysis)

- [ ] Run grep for `.instance()` pattern:
  ```bash
  grep -rn "\.instance()" game/ tests/
  ```
- [ ] Document occurrences (expect 30+ files)
- [ ] Categorize by: can be replaced vs. acceptable singleton usage
- [ ] Add to findings/phase_5_audit.md

**Notes:**

---

### Task 5.7: Remove Deprecated Functions [Medium]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py`

**Only do this AFTER all callers are updated!**

- [ ] Remove `get_component_registry()` function
- [ ] Remove `get_modifier_registry()` function
- [ ] Remove `get_vehicle_classes()` function
- [ ] Remove `get_validator()` function (if no longer used)
- [ ] Remove `get_resource_registry()` function (if no longer used)
- [ ] Update `__all__` to remove deprecated exports
- [ ] Run registry tests

**Notes:** This is a breaking change - ensure no callers remain first!

---

### Task 5.8: Verify Deprecation Warnings Reduced [Simple]
**Tests:** `pytest tests/ -W error::DeprecationWarning`

- [ ] Run test suite with deprecation warnings as errors
- [ ] Count remaining deprecation warnings
- [ ] Document reduction from baseline (28327 warnings)
- [ ] Address any new warnings found

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No game code uses deprecated registry functions
- [ ] Deprecated functions removed from registry.py
- [ ] Deprecation warnings significantly reduced
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
