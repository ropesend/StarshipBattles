# Phase 2: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-124 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (12 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: TCG-UI2-001 - UIConfig class has no dedicated test cov [Simple]
**File:** `game/ui/config.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - UIConfig has tests in tests/unit/core/test_config.py (TestUIConfig class, lines 90-119). Tests cover: import, attributes, toast dimensions, dialog dimensions, and proper location.

### Task 2.2: TCG-UI2-002 - game_renderer draw_ship lacks edge case [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - draw_ship has extensive tests in tests/unit/ui/test_rendering_logic.py covering: culling, dead ship returns early, theme image drawing, fallback to dot, zoom affects radius, camera boundary.

### Task 2.3: TCG-UI2-003 - draw_hud resource bar edge cases not tes [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The draw_hud() and draw_bar() functions referenced in the finding were DELETED as dead code in PROJ-121 Phase 3, Task 3.1. The only draw_hud now is in battle_screen.py (different module).

### Task 2.4: TCG-UI2-004 - BattleUIService projectile color mapping [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFORMATIONAL - PROJECTILE_COLORS is a simple constant dict with fallback via .get(). BattleUIService has 600+ lines of tests covering conversions. Testing constant definitions provides no value.

### Task 2.5: TCG-UI2-005 - ShipThemeManager missing scale factor bo [Simple]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - get_manual_scale() has tests in test_theme_discovery.py: test_get_manual_scale_default, test_get_manual_scale_before_discovery, test_get_manual_scale_with_value. Also in test_ship_theme_logic.py.

### Task 2.6: TCG-UI2-006 - Camera fit_objects edge case with dead t [Simple]
**File:** `game/ui/renderer/camera.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - fit_objects has tests in test_camera.py: test_fit_objects_centers_camera, test_fit_objects_adjusts_zoom, test_fit_objects_empty_list, test_fit_objects_single_object. Method works with any object having .position attribute (alive or dead).

### Task 2.7: TCG-UI2-007 - InputMapper save_user_overrides file per [Simple]
**File:** `game/ui/services/input_mapper.`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - save_user_overrides has comprehensive tests in test_input_mapper.py: test_save_user_overrides (creates file with diffs), test_save_creates_parent_directories, test_save_no_overrides_returns_true.

### Task 2.8: TCG-UI2-008 - ScreenshotManager capture_strategy_layer [Simple]
**File:** `game/ui/services/screenshot_ma`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - capture_strategy_layer has tests in test_screenshot_manager.py: test_capture_strategy_layer_disabled_does_nothing, test_capture_strategy_layer_with_ui, test_capture_strategy_layer_without_ui, test_capture_strategy_layer_with_subwindows, test_capture_strategy_layer_handles_invalid_dimensions. Also in test_bug_15_screenshot_strategy.py.

### Task 2.9: TCG-UI2-009 - BattleOrchestrator lacks tests for AI co [Simple]
**File:** `game/ui/orchestration/battle_o`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - BattleOrchestrator has comprehensive tests in test_battle_orchestrator.py: TestBattleOrchestratorCreation, TestCreateAIControllers (correct count, empty teams, enemy teams), TestCreateAIForShip, TestOrchestratorIntegration.

### Task 2.10: TCG-UI2-010 - SpriteManager thread safety tests are li [Medium]
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - SpriteManager has thread safety tests in test_sprites.py: TestSpriteManagerThreadSafety class with test_concurrent_instance_calls, test_concurrent_load_sprites_no_corruption.

### Task 2.11: TCG-UI2-011 - colors.py basic constants not tested [Simple]
**File:** `game/ui/colors.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - colors.py has tests in test_colors.py: test_all_colors_are_rgb_tuples, test_all_components_are_integers_in_range, test_colors_dict_has_expected_categories, test_no_duplicate_color_values, test_colors_dict_is_not_empty. Also test_ui_imports.py.

### Task 2.12: TCG-UI2-012 - Test organization could be improved [Complex]
**File:** `tests/unit/ui/`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFORMATIONAL - Not a test coverage issue. The tests/unit/ui/ directory is already well-organized with subdirectories for battle_state_viewer/, interfaces/, left_panel/, panels/, schematic_view/, screens/, services/, test_lab_scene/. Structure mirrors source code organization.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary
- **Tasks reviewed:** 12
- **FALSE POSITIVES:** 10 (tests already exist)
- **INFORMATIONAL:** 2 (not test coverage issues)
- **Implemented:** 0 (no code changes needed)
