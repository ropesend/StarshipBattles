# Phase 4: Test .clear() Migration - Batch 2 (NOT using fresh_registries)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove `RegistryManager.instance().clear()` from test files that don't currently use `fresh_registries`. These calls are redundant because the root conftest `reset_game_state` autouse fixture already handles clear+hydrate before every test.

---

## Tasks

### Task 4.1: Remove .clear() from workshop tests [Simple]
**Files:**
- `tests/unit/workshop/test_workshop_viewmodel.py:53`
- `tests/unit/workshop/test_workshop_data_loader.py:42,48,147,154`

**Tests:** `pytest tests/unit/workshop/ -x`

- [x] `test_workshop_viewmodel.py:53` - Remove `.clear()` from `workshop_class_setup` fixture teardown
- [x] `test_workshop_data_loader.py:42,48` - Remove `.clear()` from `data_loader_setup` fixture setup/teardown
- [x] `test_workshop_data_loader.py:147,154` - Remove `.clear()` from `real_data_loader_setup` fixture setup/teardown
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 4.2: Remove .clear() from builder tests (without fresh_registries) [Simple]
**Files:**
- `tests/unit/builder/test_builder_warning_logic.py:72`
- `tests/unit/builder/test_builder_viewmodel.py:54`
- `tests/unit/builder/test_builder_drag_drop_real.py:135`
- `tests/unit/builder/test_builder_data_loader.py:50,52,143,148`

**Tests:** `pytest tests/unit/builder/ -x`

- [x] `test_builder_warning_logic.py:72` - Remove `.clear()` from fixture teardown
- [x] `test_builder_viewmodel.py:54` - Remove `.clear()` from `pygame_and_data` fixture teardown
- [x] `test_builder_drag_drop_real.py:135` - Remove `.clear()` from `setup_builder` fixture teardown
- [x] `test_builder_data_loader.py:50,52` - Remove `.clear()` from `setup_and_teardown` fixture setup/teardown
- [x] `test_builder_data_loader.py:143,148` - Remove `.clear()` from class-scoped `setup_and_teardown` fixture
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 4.3: Remove .clear() from entity and system tests [Simple]
**Files:**
- `tests/unit/entities/test_ability_interface.py:28,32`
- `tests/unit/systems/test_main_integration.py:20`
- `tests/unit/systems/test_physics.py:15`
- `tests/unit/systems/test_spatial.py:25`

**Tests:** `pytest tests/unit/entities/ tests/unit/systems/ -x`

- [x] `test_ability_interface.py:28,32` - Remove `.clear()` from `setup` fixture setup/teardown
- [x] `test_main_integration.py:20` - Remove `.clear()` from `cleanup` fixture teardown
- [x] `test_physics.py:15` - Remove `.clear()` from `pygame_init` fixture teardown
- [x] `test_spatial.py:25` - Remove `.clear()` from `pygame_init` fixture teardown
- [x] Remove `RegistryManager` import from each file if no longer used

**Notes:**

### Task 4.4: Remove .clear() from remaining test files [Simple]
**Files:**
- `tests/unit/ui/test_theme_discovery.py:64`
- `tests/unit/test_screenshot_manager.py:23`
- `tests/unit/regressions/test_regressions.py:26`
- `tests/unit/performance/reproduce_scaling.py:14,23`

**Tests:** `pytest tests/unit/ui/test_theme_discovery.py tests/unit/test_screenshot_manager.py tests/unit/regressions/test_regressions.py tests/unit/performance/reproduce_scaling.py -x`

- [x] `test_theme_discovery.py:64` - Remove `.clear()` from `setup` fixture teardown
- [x] `test_screenshot_manager.py:23` - Remove `.clear()` from `screenshot_manager` fixture teardown
- [x] `test_regressions.py:26` - Remove `.clear()` from `pygame_setup` fixture teardown
- [x] `reproduce_scaling.py:14,23` - Remove `.clear()` from `component_environment` fixture setup/teardown
- [x] Remove `RegistryManager` import from each file if no longer used (kept where still used for data access)

**Notes:**

### Task 4.5: Update integration conftest [Simple]
**File:** `tests/integration/ai_strategy/conftest.py:37`
**Tests:** `pytest tests/integration/ -x`

- [x] Remove `RegistryManager.instance().clear()` from `setup_game_data` fixture teardown (line 37)
- [x] Keep `StrategyManager.instance().clear()` (line 38) - different singleton, still needed
- [x] Remove `RegistryManager` import if no longer used

**Notes:** Root conftest handles RegistryManager cleanup between tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - full suite passes (12373 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
