# Phase 5: Core Test: Convert Impure Loader Tests to Pure [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert backward-compatibility loader tests from impure singleton tests to pure function tests. Keep "does not modify registry" tests as legitimate singleton guards.

---

## Tasks

### Task 5.1: Convert test_pure_loaders.py backward-compat tests [Medium]
**File:** `tests/unit/core/test_pure_loaders.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py -v`

- [ ] Lines 55-59, 124-127, 189-192, 268-271: "does not modify registry" tests — **Keep as-is** (these are regression guards ensuring pure functions stay pure)
- [ ] Lines 328-339: `test_load_components_populates_registry` — Convert to test `load_components_data()` return value. Replace `registry = RegistryManager.instance().components` / `load_components(...)` / `assert len(registry) > 0` with `result = load_components_data(...)` / `assert len(result) > 0` / `assert "bridge" in result`
- [ ] Lines 343-355: `test_load_modifiers_populates_registry` — Same conversion using `load_modifiers_data()`
- [ ] Remove the `TestBackwardCompatibility` class name or rename to `TestLoaderPureFunctions`
- [ ] Run tests

**Notes:** The "does not modify registry" tests are the canonical guards that pure functions stay side-effect free — keep them. The "populates registry" tests are what we convert to pure. Converting improves portability to C#/C++/Rust where global singletons are not idiomatic.

### Task 5.2: Review test_registry_manager_reload.py [Simple]
**File:** `tests/unit/core/test_registry_manager_reload.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`

- [ ] Line 27: `fresh_registry` fixture returns `RegistryManager.instance()` — **Legitimate** (testing reload function)
- [ ] Add comment: `# PROJ-195: Legitimate — testing reload_registries_from_directory on singleton`
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/core/` passes
- [ ] Legitimate usages documented with PROJ-195 comments
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
