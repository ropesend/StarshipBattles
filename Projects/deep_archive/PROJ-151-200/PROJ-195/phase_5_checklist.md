# Phase 5: Core Test: Convert Impure Loader Tests to Pure [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert backward-compatibility loader tests from impure singleton tests to pure function tests. Keep "does not modify registry" tests as legitimate singleton guards.

---

## Tasks

### Task 5.1: Convert test_pure_loaders.py backward-compat tests [Medium]
**File:** `tests/unit/core/test_pure_loaders.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py -v`

- [x] Lines 55-59, 124-127, 189-192, 268-271: "does not modify registry" tests — **Keep as-is** (these are regression guards ensuring pure functions stay pure)
- [x] Lines 328-339: `test_load_components_populates_registry` — Convert to test `load_components_data()` return value. Replace `registry = RegistryManager.instance().components` / `load_components(...)` / `assert len(registry) > 0` with `result = load_components_data(...)` / `assert len(result) > 0` / `assert "bridge" in result`
- [x] Lines 343-355: `test_load_modifiers_populates_registry` — Same conversion using `load_modifiers_data()`
- [x] Remove the `TestBackwardCompatibility` class name or rename to `TestLoaderPureFunctions`
- [x] Run tests

**Notes:** Converted `TestBackwardCompatibility` to `TestLoaderPureFunctions`. Tests now call pure functions directly without singleton access. The "does not modify registry" tests are kept as guards.

### Task 5.2: Review test_registry_manager_reload.py [Simple]
**File:** `tests/unit/core/test_registry_manager_reload.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [x] Line 27: `fresh_registry` fixture returns `RegistryManager.instance()` — **Legitimate** (testing reload function)
- [x] Add comment: `# PROJ-195: Legitimate — testing reload_registries_from_directory on singleton`
- [x] Run tests

**Notes:** Added PROJ-195 comment documenting legitimate usage.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` passes (810 passed)
- [x] Legitimate usages documented with PROJ-195 comments
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
