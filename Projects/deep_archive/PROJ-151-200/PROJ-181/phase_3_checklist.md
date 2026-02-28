# Phase 3: Test .clear() Migration - Batch 1 (Already using fresh_registries)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove redundant `RegistryManager.instance().clear()` calls from test files that already use `fresh_registries` fixture. These calls are redundant because the root conftest `reset_game_state` autouse fixture already handles clear+hydrate before every test.

---

## Tasks

### Task 3.1: Remove redundant .clear() from AI tests [Simple]
**Files:**
- `tests/unit/ai/test_ai.py:72,201`
- `tests/unit/ai/test_movement_and_ai.py:54`

**Tests:** `pytest tests/unit/ai/ -x`

- [x] `test_ai.py:72` - Remove `RegistryManager.instance().clear()` from `ai_setup` fixture teardown
- [x] `test_ai.py:201` - Remove `RegistryManager.instance().clear()` from `strategy_setup` fixture teardown
- [x] `test_movement_and_ai.py:54` - Remove `RegistryManager.instance().clear()` from `movement_ai_setup` fixture teardown
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 3.2: Remove redundant .clear() from builder tests (with fresh_registries) [Simple]
**Files:**
- `tests/unit/builder/test_builder_logic.py:24`
- `tests/unit/builder/test_selection_refinements.py:60`
- `tests/unit/builder/test_multi_selection_logic.py:57`

**Tests:** `pytest tests/unit/builder/test_builder_logic.py tests/unit/builder/test_selection_refinements.py tests/unit/builder/test_multi_selection_logic.py -x`

- [x] `test_builder_logic.py:24` - Remove `.clear()` from `setup_and_teardown` fixture teardown
- [x] `test_selection_refinements.py:60` - Remove `.clear()` from `setup` fixture teardown
- [x] `test_multi_selection_logic.py:57` - Remove `.clear()` from `setup` fixture teardown
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 3.3: Remove redundant .clear() from simulation tests [Simple]
**Files:**
- `tests/unit/simulation/test_component_decoupling.py:35,102,183`
- `tests/unit/simulation/services/test_simulation_design_loader.py:39,190`

**Tests:** `pytest tests/unit/simulation/ -x`

- [x] `test_component_decoupling.py:35,102,183` - Remove `.clear()` from all 3 fixture teardowns
- [x] `test_simulation_design_loader.py:39,190` - Remove `.clear()` from both fixture teardowns
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 3.4: Remove redundant .clear() from regression and repro tests [Simple]
**Files:**
- `tests/unit/regressions/test_warnings.py:24`
- `tests/repro_issues/test_bug_13_clear_removes_hull.py:21,54`

**Tests:** `pytest tests/unit/regressions/test_warnings.py tests/repro_issues/test_bug_13_clear_removes_hull.py -x`

- [x] `test_warnings.py:24` - Remove `.clear()` from `ship_with_registry` fixture teardown
- [x] `test_bug_13_clear_removes_hull.py:21` - Remove `.clear()` from `simple_ship_registry` fixture setup
- [x] `test_bug_13_clear_removes_hull.py:54` - Remove `.clear()` from `simple_ship_registry` fixture teardown
- [x] Remove `RegistryManager` import from each file if no longer used (kept where still needed)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ai/ tests/unit/builder/ tests/unit/simulation/ tests/unit/regressions/ tests/repro_issues/ -x` - all pass (3172 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
