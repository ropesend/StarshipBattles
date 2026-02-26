# Phase 7: Regression & Repro Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate remaining regression and bug repro tests

---

## Tasks

### Task 7.1: Review test_regressions.py [Simple]
**File:** `tests/unit/regressions/test_regressions.py`
**Tests:** `pytest tests/unit/regressions/test_regressions.py -v`

- [x] Lines 36, 43, 45, 48: `test_ship_classes_update_in_place` — **Legitimate singleton test** (validates load_vehicle_classes updates singleton in-place). Keep.
- [x] Add comment: `# PROJ-195: Legitimate — testing singleton dict identity preservation`
- [x] Run tests

**Notes:** Added PROJ-195 comment block at class level documenting why this is a legitimate singleton test.

### Task 7.2: Migrate test_warnings.py [Simple]
**File:** `tests/unit/regressions/test_warnings.py`
**Tests:** `pytest tests/unit/regressions/test_warnings.py -v`

- [x] Lines 16-17: Replace `RegistryManager.instance().vehicle_classes` in `ship_with_registry` fixture with `fresh_registries.vehicle_classes` (fixture already receives `fresh_registries`)
- [x] Remove `from game.core.registry import RegistryManager` import (line 6)
- [x] Run tests

**Notes:** Fixture now uses DI pattern exclusively.

### Task 7.3: Migrate test_bug_13_clear_removes_hull.py [Medium]
**File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_clear_removes_hull.py -v`

- [x] Lines 44-47: `simple_ship_registry` fixture — Replace `registry = RegistryManager.instance()` / `registry.vehicle_classes.update(classes)` / `registry.components[comp_id] = ...` with populating `fresh_registries` directly
- [x] Line 72: Replace `RegistryManager.instance().components.items()` with `fresh_registries.components`
- [x] Remove `RegistryManager` from import on line 12 (keep `GameRegistries`)
- [x] Run tests

**Notes:** Test now uses DI pattern exclusively. GameRegistries created from fresh_registries components.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/regressions/ tests/repro_issues/` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
