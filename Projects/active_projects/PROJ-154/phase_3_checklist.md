# Phase 3: Partial File Edits

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Surgically remove dead/duplicate/trivial tests from 8 files while preserving valuable ones (~820 lines removed)
**Priority:** Normal — requires careful editing to avoid breaking kept tests

---

## Tasks

### Task 3.1: UI-5 — Remove trivial positivity checks from test_config.py [Simple]
**File:** `tests/unit/ui/test_config.py` (213 lines)
**Tests:** `pytest tests/unit/ui/test_config.py -v`

**Tests to KEEP (valuable):**
- `TestToastDimensions::test_toast_dimensions_reasonable` (range check)
- `TestDialogDimensions::test_confirm_dialog_larger_than_toast` (relationship)
- `TestFontSizes::test_font_sizes_hierarchy` (relationship)
- `TestVisualConstants::test_panel_alpha_in_range` (range check)
- `TestVisualConstants::test_panel_alpha_mostly_opaque` (range check)
- `TestCommonDimensions::test_row_height_large_larger_than_standard` (relationship)
- `TestUIConfigAllConstantsAreIntegers::test_all_constants_are_integers` (structural)

**Remove (pure `assert X > 0`):**
- [ ] Remove `TestUIConfigConstants` class entirely (lines 8-29): `test_panel_padding_is_positive`, `test_panel_gap_is_positive`, `test_element_spacing_is_positive`, `test_indent_is_positive`
- [ ] From `TestToastDimensions`: remove `test_toast_width_is_positive`, `test_toast_height_is_positive` (keep `test_toast_dimensions_reasonable`)
- [ ] From `TestDialogDimensions`: remove `test_confirm_dialog_width_positive`, `test_confirm_dialog_height_positive` (keep `test_confirm_dialog_larger_than_toast`)
- [ ] From `TestFontSizes`: remove `test_font_title_is_positive`, `test_font_name_is_positive`, `test_font_stat_is_positive` (keep `test_font_sizes_hierarchy`)
- [ ] Remove `TestPanelDimensions` class entirely (lines 98-119)
- [ ] Remove `TestBarDimensions` class entirely (lines 122-143)
- [ ] Remove `TestBattleScreenConstants` class entirely (lines 160-171)
- [ ] From `TestCommonDimensions`: remove `test_row_height_standard_positive`, `test_row_height_large_positive`, `test_header_height_positive` (keep `test_row_height_large_larger_than_standard`)
- [ ] Clean up any empty classes (if a class has only 1 test, consider whether the class wrapper is still useful)
- [ ] Run `pytest tests/unit/ui/test_config.py -v` — verify all kept tests pass

**Notes:**

### Task 3.2: UI-7 — Remove duplicates from test_battle_screen_edge_cases.py [Medium]
**File:** `tests/unit/ui/screens/test_battle_screen_edge_cases.py` (408 lines)
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_edge_cases.py -v`

**Keep 6 unique tests:**
- `TestHandleEventEdgeCases::test_handle_event_unknown_event_type`
- `TestHandleEventEdgeCases::test_handle_mouse_click_none_result`
- `TestHandleEventEdgeCases::test_handle_right_click_no_clear`
- `TestKeyboardShortcutEdgeCases::test_keydown_f3_toggles_overlay`
- `TestKeyboardShortcutEdgeCases::test_keydown_comma_respects_minimum`
- `TestKeyboardShortcutEdgeCases::test_keydown_period_respects_maximum`

**Remove:**
- [ ] From `TestHandleEventEdgeCases`: remove `test_handle_mouse_click_focus_ship_result`, `test_handle_mouse_click_end_battle_result`, `test_handle_mousewheel`
- [ ] From `TestKeyboardShortcutEdgeCases`: remove `test_keydown_space_toggles_pause`, `test_keydown_comma_decreases_speed`, `test_keydown_period_increases_speed`, `test_keydown_m_resets_to_normal_speed`, `test_keydown_slash_sets_ui_pause_speed`, `test_keydown_bracket_cycles_focus`, `test_keydown_right_bracket_cycles_forward`
- [ ] Remove `TestBattleStateEdgeCases` class entirely (2 tests)
- [ ] Remove `TestResizeEdgeCases` class entirely (2 tests)
- [ ] Clean up unused imports after removal
- [ ] Run `pytest tests/unit/ui/screens/test_battle_screen_edge_cases.py -v` — verify 6 kept tests pass

**Notes:**

### Task 3.3: UI-6 — Remove 3 duplicate tests from test_battle_screen_extended.py [Simple]
**File:** `tests/unit/ui/test_battle_screen_extended.py` (130 lines)
**Tests:** `pytest tests/unit/ui/test_battle_screen_extended.py -v`

**Keep:** `test_process_beam_attack_logic` (unique beam attack test)

- [ ] Remove `test_is_battle_over_victory` (duplicate of test_battle_screen.py)
- [ ] Remove `test_update_loop_tick_counter` (duplicate of test_battle_screen_simulation.py)
- [ ] Remove `test_headless_mode_initialization` (duplicate of test_battle_screen_simulation.py)
- [ ] Clean up any fixtures/imports only used by removed tests
- [ ] Run `pytest tests/unit/ui/test_battle_screen_extended.py -v` — verify beam test passes

**Notes:**

### Task 3.4: UI-9 — Remove trivial color and font tests [Simple]
**File:** `tests/unit/ui/test_colors.py` (141 lines)
**Tests:** `pytest tests/unit/ui/test_colors.py -v`

**Keep:** `TestColorsValidation` (5 tests) + `TestColorAccessibility` (3 tests)

- [ ] Remove `TestBasicColors` class (3 tests: `test_white_is_rgb_white`, `test_black_is_rgb_black`, `test_white_and_black_are_opposite`)
- [ ] Remove `TestFontConstants` class (3 tests: `test_font_main_is_string`, `test_font_main_is_not_empty`, `test_font_main_is_common_font`)
- [ ] Run `pytest tests/unit/ui/test_colors.py -v` — verify 8 kept tests pass

**Notes:**

### Task 3.5: UI-11 — Remove TestGameSwitchScene from test_scene_protocol.py [Simple]
**File:** `tests/unit/ui/test_scene_protocol.py` (239 lines)
**Tests:** `pytest tests/unit/ui/test_scene_protocol.py -v`

**Keep:** `TestISceneProtocolCompliance` + `TestSceneCallback`

- [ ] Remove `TestGameSwitchScene` class (lines 152-192): `test_switch_scene_updates_active_scene`, `test_switch_scene_updates_game_state`. These test Python attribute assignment on MagicMock, not game code.
- [ ] Run `pytest tests/unit/ui/test_scene_protocol.py -v` — verify kept tests pass

**Notes:**

### Task 3.6: UI-13 — Remove constant positivity checks from test_game_renderer.py [Simple]
**File:** `tests/unit/ui/renderer/test_game_renderer.py` (397 lines)
**Tests:** `pytest tests/unit/ui/renderer/test_game_renderer.py -v`

**Keep from TestRenderingConstants:**
- `test_min_zoom_for_image_positive` (range check: `0 < x < 1`)
- `test_min_zoom_for_components_greater_than_image_zoom` (relationship)
- `test_image_rotation_offset_is_minus_90` (exact value check)

**Remove from TestRenderingConstants:**
- [ ] Remove `test_culling_max_radius_positive` (pure positivity)
- [ ] Remove `test_component_dot_radius_positive` (pure positivity)
- [ ] Remove `test_direction_line_offset_positive` (pure positivity)
- [ ] Remove `test_direction_line_width_positive` (pure positivity)
- [ ] Remove `test_fallback_dot_radius_positive` (pure positivity)
- [ ] Remove `test_fallback_dot_min_size_positive` (pure positivity)
- [ ] Run `pytest tests/unit/ui/renderer/test_game_renderer.py -v` — verify kept tests pass

**Notes:**

### Task 3.7: UI-14 — Remove mock-testing classes from test_strategy_detail_formatter.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py` (537 lines)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v`

- [ ] Remove `TestStrategyDetailFormatterWidgetAccessors` class (lines 71-131, 8 tests that assert `_mock_name` values)
- [ ] Remove `TestResizeSupport` class (lines 425-468, 3 tests: `test_update_screen_size`, `test_update_graph_rect`, `test_update_graphs`)
- [ ] Clean up unused imports if any
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v` — verify remaining tests pass

**Notes:**

### Task 3.8: STR-14 — Remove legacy cleanup check from test_production_refactor.py [Simple]
**File:** `tests/unit/strategy/engine/test_production_refactor.py` (134 lines)
**Tests:** `pytest tests/unit/strategy/engine/test_production_refactor.py -v`

- [ ] Remove `test_legacy_cleanup` method (lines 128-133): checks `not hasattr(engine, '_process_base_queue')` etc. One-time refactoring verification, no longer needed.
- [ ] Run `pytest tests/unit/strategy/engine/test_production_refactor.py -v` — verify remaining tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
