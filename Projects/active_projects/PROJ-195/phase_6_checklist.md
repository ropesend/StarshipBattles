# Phase 6: Conftest & Infrastructure Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate conftest.py files with singleton fixtures to DI patterns where possible

---

## Tasks

### Task 6.1: Migrate tests/unit/strategy/conftest.py [Medium]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [ ] Lines 14-20: `reset_resource_registry` — **Legitimate test isolation fixture** (clears singleton resources). Keep with comment.
- [ ] Lines 44-47: `custom_resource_registry` — Uses `RegistryManager.instance()` to populate resources. Migrate: accept `fresh_registries`, populate `fresh_registries.resources` instead
- [ ] Update consumers of `custom_resource_registry` if needed
- [ ] Run tests

**Notes:**

### Task 6.2: Review tests/unit/core/resources_registry/conftest.py [Simple]
**File:** `tests/unit/core/resources_registry/conftest.py`
**Tests:** `pytest tests/unit/core/resources_registry/ -v`

- [ ] Lines 10-19: `clean_registry` autouse fixture — **Legitimate** (resource registry tests). Keep.
- [ ] Add comment: `# PROJ-195: Legitimate — isolation fixture for singleton resource registry tests`
- [ ] Run tests

**Notes:**

### Task 6.3: Migrate tests/integration/resource_system/conftest.py [Simple]
**File:** `tests/integration/resource_system/conftest.py`
**Tests:** `pytest tests/integration/resource_system/ -v`

- [ ] Lines 13-22: Replace `loaded_registry` fixture: return `fresh_registries` instead of `RegistryManager.instance()`
- [ ] Add `fresh_registries` parameter to fixture
- [ ] Remove `from game.core.registry import RegistryManager` import (line 9)
- [ ] Run tests

**Notes:**

### Task 6.4: Migrate test_resource_pipeline.py [Simple]
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py -v`

- [ ] Line 43: Replace `RegistryManager.instance().resources.update(...)` with `loaded_registry.resources.update(...)`
- [ ] Remove `from game.core.registry import RegistryManager` import (line 11)
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ tests/unit/core/resources_registry/ tests/integration/resource_system/` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
