# Phase 6: Conftest & Infrastructure Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate conftest.py files with singleton fixtures to DI patterns where possible

---

## Tasks

### Task 6.1: Migrate tests/unit/strategy/conftest.py [Medium]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Lines 14-20: `reset_resource_registry` — **Legitimate test isolation fixture** (clears singleton resources). Keep with comment.
- [x] Lines 44-47: `custom_resource_registry` — Uses `RegistryManager.instance()` to populate resources. Migrate: accept `fresh_registries`, populate `fresh_registries.resources` instead
- [x] Update consumers of `custom_resource_registry` if needed
- [x] Run tests

**Notes:** Added PROJ-195 comment to reset_resource_registry. Migrated custom_resource_registry to use fresh_registries parameter.

### Task 6.2: Review tests/unit/core/resources_registry/conftest.py [Simple]
**File:** `tests/unit/core/resources_registry/conftest.py`
**Tests:** `pytest tests/unit/core/resources_registry/ -v`

- [x] Lines 10-19: `clean_registry` autouse fixture — **Legitimate** (resource registry tests). Keep.
- [x] Add comment: `# PROJ-195: Legitimate — isolation fixture for singleton resource registry tests`
- [x] Run tests

**Notes:** Added PROJ-195 comment to docstring.

### Task 6.3: Migrate tests/integration/resource_system/conftest.py [Simple]
**File:** `tests/integration/resource_system/conftest.py`
**Tests:** `pytest tests/integration/resource_system/ -v`

- [x] Lines 13-22: Review `loaded_registry` fixture — **Legitimate singleton usage**
- [x] Added PROJ-195 comment explaining why: integration tests add test components to singleton, and ShipInstance.get_calculated_stats() internally uses get_default_registry_provider() which reads from singleton
- [x] Run tests

**Notes:** Cannot migrate to fresh_registries because ShipInstance internally reads from singleton via get_default_registry_provider(). These integration tests need components in the singleton. Added documentation.

### Task 6.4: Migrate test_resource_pipeline.py [Simple]
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py -v`

- [x] Line 43: Replace `RegistryManager.instance().resources.update(...)` with `registry.resources.update(...)`
- [x] Remove `from game.core.registry import RegistryManager` import (line 11)
- [x] Run tests

**Notes:** Now uses `loaded_registry` fixture instead of direct singleton access.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ tests/unit/core/resources_registry/ tests/integration/resource_system/` passes (2233 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
