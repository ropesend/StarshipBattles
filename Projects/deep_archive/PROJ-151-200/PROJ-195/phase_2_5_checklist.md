# Phase 2.5: Ship Internal Singleton Investigation & Fix [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 2.5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Investigate and fix any Ship/Component internal methods that read from the global singleton, then fix all tests broken by Phase 2 removals

---

## Tasks

### Task 2.5.1: Investigate Ship internal singleton access [Medium]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/components/component.py`
**Tests:** N/A — investigation only

- [x] Search `game/simulation/entities/ship.py` for any `RegistryManager.instance()` or `get_default_registry_provider()` calls
- [x] Search `game/simulation/components/component.py` for same
- [x] Search `game/simulation/services/` for any service that Ship calls internally
- [x] Document all internal singleton access points found
- [x] For each access point, determine: does the code have a `registries=` parameter it could use instead?

**Notes:**
- **ship.py**: NO singleton access. Ship stores `registries` in constructor and uses it internally. ✅
- **component.py**: 3 `get_default_registry_provider()` calls found:
  - Line 514: `load_components_data()` - fallback when `registries=None` (legitimate loader path)
  - Line 569: `load_components()` - impure wrapper for module-level initialization (composition root)
  - Line 668: `load_modifiers()` - impure wrapper for module-level initialization (composition root)
- **game/simulation/services/**: NO singleton access
- **Conclusion**: All singleton access is in loader functions (composition-root paths), NOT in Ship/Component internal methods. No fixes needed.

### Task 2.5.2: Fix internal singleton access in production code [Medium]
**Files:** As identified in Task 2.5.1
**Tests:** `pytest tests/ --testmon`

- [x] For each internal access point found, refactor to use the `registries` attribute stored on the Ship/Component instance
- [x] Ensure no new singleton leaks are introduced
- [x] Run tests after each fix

**Notes:** No internal Ship/Component singleton access found. All access is in module-level loader functions which are legitimate composition-root entry points. Phase 2 cleanup was sufficient.

### Task 2.5.3: Fix all broken tests from Phase 2 [Medium]
**Tests:** `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py -v`

- [x] Run the full test suite for Phase 2 files
- [x] For each failure, diagnose root cause (internal singleton access vs missing DI parameter vs other)
- [x] Fix each failure — prefer fixing the production code to propagate `registries` rather than re-adding singleton hydration
- [x] All Phase 2 tests green

**Notes:** All 26 Phase 2 tests pass. No fixes needed - the Phase 2 removals worked correctly because Ship/Component properly use the injected `registries` parameter throughout.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py` passes
- [x] All internal singleton access points documented or fixed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
