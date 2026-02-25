# Phase 7: Regression & Repro Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate remaining regression and bug repro tests

---

## Tasks

### Task 7.1: Review test_regressions.py [Simple]
**File:** `tests/unit/regressions/test_regressions.py`
**Tests:** `pytest tests/unit/regressions/test_regressions.py -v`

- [ ] Lines 36, 43, 45, 48: `test_ship_classes_update_in_place` — **Legitimate singleton test** (validates load_vehicle_classes updates singleton in-place). Keep.
- [ ] Add comment: `# PROJ-195: Legitimate — testing singleton dict identity preservation`
- [ ] Run tests

**Notes:**

### Task 7.2: Migrate test_warnings.py [Simple]
**File:** `tests/unit/regressions/test_warnings.py`
**Tests:** `pytest tests/unit/regressions/test_warnings.py -v`

- [ ] Lines 16-17: Replace `RegistryManager.instance().vehicle_classes` in `ship_with_registry` fixture with `fresh_registries.vehicle_classes` (fixture already receives `fresh_registries`)
- [ ] Remove `from game.core.registry import RegistryManager` import (line 6)
- [ ] Run tests

**Notes:**

### Task 7.3: Migrate test_bug_13_clear_removes_hull.py [Medium]
**File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_clear_removes_hull.py -v`

- [ ] Lines 44-47: `simple_ship_registry` fixture — Replace `registry = RegistryManager.instance()` / `registry.vehicle_classes.update(classes)` / `registry.components[comp_id] = ...` with populating `fresh_registries` directly
- [ ] Line 72: Replace `RegistryManager.instance().components.items()` with `fresh_registries.components`
- [ ] Remove `RegistryManager` from import on line 12 (keep `GameRegistries`)
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/regressions/ tests/repro_issues/` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
