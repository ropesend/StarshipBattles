# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-27 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: CORE-01 - Singleton anti-pattern [Complete]
**File:** `game/core/registry.py`, `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
Implemented registry abstraction via IRegistryProvider protocol:

1. **IRegistryProvider Protocol** (`game/core/protocols.py`):
   - Runtime-checkable protocol defining `get_components()`, `get_modifiers()`, `get_vehicle_classes()`
   - Enables dependency injection for registry access

2. **DefaultRegistryProvider** (`game/core/registry.py`):
   - Production implementation backed by RegistryManager singleton
   - Maintains full backward compatibility

3. **TestRegistryProvider** (`game/core/registry.py`):
   - Isolated implementation for testing
   - Each instance has independent data dictionaries
   - Enables testing services without singleton pollution

4. **Factory Function** (`game/core/registry.py`):
   - `get_default_registry_provider()` returns singleton provider instance

Tests: 24 new tests in `test_registry_provider.py` covering:
- Protocol definition and runtime checkability
- DefaultRegistryProvider singleton delegation
- TestRegistryProvider isolation
- Factory function behavior


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
