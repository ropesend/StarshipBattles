# Phase 1: CAT-1 Trivial Pass

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-321 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete or convert to `pytest.skip` the 46 verified CAT-1 trivial-pass tests identified by review `2026-05-02_204633_test-review`.

---

## Tasks

### Task 1.1: `tests/integration/strategy/production/test_queue.py`
**File:** `tests/integration/strategy/production/test_queue.py`
**Tests:** `pytest tests/integration/strategy/production/test_queue.py`

- [ ] `test_production_progress` (lines 61-76, 16 LOC) - **DELETE** the test. Verification report records the body as "all comments" with zero assertions, so removal carries no production-coverage risk. _(If production path is uncovered, add a real test in a follow-up project, not in P0.)_
- [ ] Verify: `pytest tests/integration/strategy/production/test_queue.py` passes; LOC delta approximate 16

### Task 1.2: `tests/integration/test_app_integration.py`
**File:** `tests/integration/test_app_integration.py`
**Tests:** `pytest tests/integration/test_app_integration.py`

- [ ] `test_menu_ui_manager_created_on_demand` (lines 245-262, 18 LOC) - Rewrite to actually invoke the lazy-creation path and assert that menu_ui_manager becomes a real UIManager.
- [ ] Verify: `pytest tests/integration/test_app_integration.py` passes; LOC delta approximate 18

### Task 1.3: `tests/unit/systems/test_main_integration.py`
**File:** `tests/unit/systems/test_main_integration.py`
**Tests:** `pytest tests/unit/systems/test_main_integration.py`

- [ ] `test_import_main` (lines 26-35, 10 LOC) - Narrow except to ImportError; pytest.skip for non-import errors.
- [ ] Verify: `pytest tests/unit/systems/test_main_integration.py` passes; LOC delta approximate 10

### Task 1.4: `tests/integration/ui/build_queue_screen/test_crash_tooltips.py`
**File:** `tests/integration/ui/build_queue_screen/test_crash_tooltips.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_crash_tooltips.py`

- [ ] `test_apply_tooltips_crash_none_buttons` (lines 9-31, 23 LOC) - Add an assertion verifying buttons are present and tooltips applied.
- [ ] Verify: `pytest tests/integration/ui/build_queue_screen/test_crash_tooltips.py` passes; LOC delta approximate 23

### Task 1.5: `tests/unit/ai/test_ai.py`
**File:** `tests/unit/ai/test_ai.py`
**Tests:** `pytest tests/unit/ai/test_ai.py`

- [ ] `test_navigate_to_rotates_ship` (lines 124-136, 13 LOC) - Add concrete assertion on ship.angle change, or remove and mark with @pytest.mark.skip(reason='Visual verification only').
- [ ] Verify: `pytest tests/unit/ai/test_ai.py` passes; LOC delta approximate 13

### Task 1.6: `tests/unit/builder/test_builder_improvements.py`
**File:** `tests/unit/builder/test_builder_improvements.py`
**Tests:** `pytest tests/unit/builder/test_builder_improvements.py`

- [ ] `test_image_scale_factor` (lines 25-42, 18 LOC) - Add post-draw assertions or document as smoke test and pair with a behavioral test.
- [ ] Verify: `pytest tests/unit/builder/test_builder_improvements.py` passes; LOC delta approximate 18

### Task 1.7: `tests/unit/core/test_combat_types.py`
**File:** `tests/unit/core/test_combat_types.py`
**Tests:** `pytest tests/unit/core/test_combat_types.py`

- [ ] `test_import_path` (lines 33-35, 3 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/core/test_combat_types.py` passes; LOC delta approximate 3

### Task 1.8: `tests/unit/services/llm/test_package_imports.py`
**File:** `tests/unit/services/llm/test_package_imports.py`
**Tests:** `pytest tests/unit/services/llm/test_package_imports.py`

- [ ] `test_services_package_importable` (lines 4-5, 3 LOC) - Remove — package importability is already validated by other tests.
- [ ] `test_llm_package_importable` (lines 8-9, 2 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/services/llm/test_package_imports.py` passes; LOC delta approximate 5

### Task 1.9: `tests/unit/simulation/components/abilities/test_superweapons.py`
**File:** `tests/unit/simulation/components/abilities/test_superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_superweapons.py`

- [ ] `Trivial Pass` (lines 137-143, 7 LOC) - Remove. Add zero incremental protection.
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_superweapons.py` passes; LOC delta approximate 7

### Task 1.10: `tests/unit/simulation/factories/test_ai_factory.py`
**File:** `tests/unit/simulation/factories/test_ai_factory.py`
**Tests:** `pytest tests/unit/simulation/factories/test_ai_factory.py`

- [ ] `5 existence/attribute tests` (lines 24-43, 138-141, 25 LOC) - Remove all 5 trivial tests.
- [ ] Verify: `pytest tests/unit/simulation/factories/test_ai_factory.py` passes; LOC delta approximate 25

### Task 1.11: `tests/unit/core/test_simulation_constants.py`
**File:** `tests/unit/core/test_simulation_constants.py`
**Tests:** `pytest tests/unit/core/test_simulation_constants.py`

- [ ] `test_constants_exist` (lines 12-21, 10 LOC) - Remove only the 5 hasattr trivia; keep behavioral tests.
- [ ] Verify: `pytest tests/unit/core/test_simulation_constants.py` passes; LOC delta approximate 10

### Task 1.12: `tests/unit/strategy/data/test_fleet_display_name.py`
**File:** `tests/unit/strategy/data/test_fleet_display_name.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet_display_name.py`

- [ ] `test_two_empires_have_independent_display_numbers` (lines 129, 12 LOC) - Strengthen to assert independence under interleaved increments, or accept as documentation.
- [ ] Verify: `pytest tests/unit/strategy/data/test_fleet_display_name.py` passes; LOC delta approximate 12

### Task 1.13: `tests/unit/strategy/data/test_superweapon_orders.py`
**File:** `tests/unit/strategy/data/test_superweapon_orders.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [ ] `6 test_*_order_type_exists tests` (lines 28-56, 29 LOC) - Replace with a single hasattr-loop test or remove.
- [ ] Verify: `pytest tests/unit/strategy/data/test_superweapon_orders.py` passes; LOC delta approximate 29

### Task 1.14: `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`

- [ ] `Public API contract tests` (lines 122-154, 33 LOC) - **DELETE** the trivial-pass tests in this file (CAT-1 by source severity is CRITICAL). If the file has any non-trivial tests, keep those; otherwise delete the file. _(Original verification suggested rename+document; P0 cleanup project deletes trivial-pass tests rather than preserving them under a different name. If the contract-guard pattern is needed, recreate it as a proper behavioral test in PROJ-322.)_
- [ ] Verify: `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` passes; LOC delta approximate 33

### Task 1.15: `tests/unit/strategy/generation/test_layout_scaling.py`
**File:** `tests/unit/strategy/generation/test_layout_scaling.py`
**Tests:** `pytest tests/unit/strategy/generation/test_layout_scaling.py`

- [ ] `test_galaxy_layouts_loader_exists` (lines 13-16, 4 LOC) - Delete entire file (only 22 LOC of import checks).
- [ ] `test_layout_data_has_required_fields` (lines 18-22, 5 LOC) - Delete; included in deletion of entire file.
- [ ] Verify: `pytest tests/unit/strategy/generation/test_layout_scaling.py` passes; LOC delta approximate 9

### Task 1.16: `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`
**File:** `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`

- [ ] `3 import-existence tests` (lines 13-27, 27 LOC) - Delete entire file.
- [ ] Verify: `pytest tests/unit/strategy/pathfinding/test_intercept_edge_cases.py` passes; LOC delta approximate 27

### Task 1.17: `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
**File:** `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py`

- [ ] `6 trivial store-and-assert tests` (lines 38-103, 65 LOC) - Remove the 6 trivially-passing tests or rewrite to exercise real subscription/wiring through the real constructor.
- [ ] Verify: `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py` passes; LOC delta approximate 65

### Task 1.18: `tests/unit/ui/panels/test_planet_report_panel.py`
**File:** `tests/unit/ui/panels/test_planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [ ] `test_function_exists` (lines 247-251, 5 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/ui/panels/test_planet_report_panel.py` passes; LOC delta approximate 5

### Task 1.19: `tests/unit/ui/panels/test_race_identity_panel.py`
**File:** `tests/unit/ui/panels/test_race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py`

- [ ] `test_identity_panel_creates_successfully` (lines 53-64, 12 LOC) - Remove tautological assertion or replace with real construction-path assertion.
- [ ] `test_auto_generate_faction_name_override_preserved` (lines 332-344, 13 LOC) - Remove or replace with assertion that the production override-preservation logic actually runs.
- [ ] Verify: `pytest tests/unit/ui/panels/test_race_identity_panel.py` passes; LOC delta approximate 25

### Task 1.20: `tests/unit/ui/screens/test_strategy_menu_panel.py`
**File:** `tests/unit/ui/screens/test_strategy_menu_panel.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_menu_panel.py`

- [ ] `7 TestMenuPanelConstants tests` (lines 43-79, 37 LOC) - Replace with a single smoke test verifying menu construction works end-to-end.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_menu_panel.py` passes; LOC delta approximate 37

### Task 1.21: `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`
**File:** `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [ ] `test_editor_has_no_instance_state` (lines 232-244, 13 LOC) - Remove. Alternatively rename to TestEditorStatelessProperty with explanatory docstring.
- [ ] Verify: `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` passes; LOC delta approximate 13

### Task 1.22: `tests/unit/ui/screens/battle_setup/test_view_model.py`
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [ ] `test_can_construct_without_registries_or_state` (lines 119-124, 6 LOC) - Remove or assert specific post-construction state.
- [ ] Verify: `pytest tests/unit/ui/screens/battle_setup/test_view_model.py` passes; LOC delta approximate 6

### Task 1.23: `tests/unit/ui/screens/test_battle_setup_state.py`
**File:** `tests/unit/ui/screens/test_battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py`

- [ ] `test_screen_owns_a_view_model` (lines 284-294, 11 LOC) - Remove or rewrite to verify that the real constructor wires the view_model.
- [ ] Verify: `pytest tests/unit/ui/screens/test_battle_setup_state.py` passes; LOC delta approximate 11

### Task 1.24: `tests/unit/ui/screens/test_design_selector_window.py`
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`

- [ ] `5 init attribute tests` (lines 166-208, 42 LOC) - Remove or merge into a real-construction test.
- [ ] Verify: `pytest tests/unit/ui/screens/test_design_selector_window.py` passes; LOC delta approximate 42

### Task 1.25: `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
**File:** `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [ ] `3 TestBuildQueueWindowEvents tests` (lines 69-82, 14 LOC) - Remove or consolidate into a single attribute-list test.
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` passes; LOC delta approximate 14

### Task 1.26: `tests/unit/ui/screens/test_event_log_window.py`
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] `test_module_exists` (lines 91-94, 4 LOC) - Remove.
- [ ] `test_sidebar_attr_exists` (lines 463-468, 6 LOC) - Fix to `assert hasattr(win, 'sidebar')` or remove.
- [ ] `test_sidebar_panel_attr_defined` (lines 470-473, 4 LOC) - Remove. Replace with a behavioral test that uses the constant.
- [ ] `test_update_method_exists` (lines 703-706, 4 LOC) - Remove. Behavioral update tests cover this.
- [ ] `4 constant/hasattr tests` (lines 475-478, 488-491, 381-385, 387-390, 24 LOC) - Remove or consolidate into a single import-and-attribute smoke test. _(includes facade hasattr tests at 381-385/387-390 — F07/F08 source double-count consolidated)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_event_log_window.py` passes; LOC delta approximate 42

### Task 1.27: `tests/unit/ui/screens/test_fleet_report_window.py`
**File:** `tests/unit/ui/screens/test_fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`

- [ ] `9 mock-assignment-only edge case tests` (lines 558-666, 108 LOC) - Remove. Replace with tests that exercise the real selection/edge-case behavior.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py` passes; LOC delta approximate 108

### Task 1.28: `tests/unit/ui/screens/test_menu_scene.py`
**File:** `tests/unit/ui/screens/test_menu_scene.py`
**Tests:** `pytest tests/unit/ui/screens/test_menu_scene.py`

- [ ] `test_button_config_with_3_buttons` (lines 54-68, 15 LOC) - Delete the duplicate.
- [ ] Verify: `pytest tests/unit/ui/screens/test_menu_scene.py` passes; LOC delta approximate 15

### Task 1.29: `tests/unit/ui/screens/test_strategy_screen.py`
**File:** `tests/unit/ui/screens/test_strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`

- [ ] `No session/turn_engine/galaxy property tests` (lines 40-60, 21 LOC) - Replace with a behavioral test of the protected protocol.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_screen.py` passes; LOC delta approximate 21

### Task 1.30: `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**File:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [ ] `test_can_construct_with_input_mapper_and_asset_resolver` (lines 224-244, 21 LOC) - Keep as-is (documented contract guard).
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py` passes; LOC delta approximate 21

### Task 1.31: `tests/unit/test_app_public_api.py`
**File:** `tests/unit/test_app_public_api.py`
**Tests:** `pytest tests/unit/test_app_public_api.py`

- [ ] `test_configure_logging_callable` (lines 123-128, 6 LOC) - Remove the test or replace with a meaningful contract assertion.
- [ ] Verify: `pytest tests/unit/test_app_public_api.py` passes; LOC delta approximate 6

### Task 1.32: `tests/unit/ui/test_race_flag_gallery.py`
**File:** `tests/unit/ui/test_race_flag_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_flag_gallery.py`

- [ ] `4 attribute-existence tests` (lines 57-97, 40 LOC) - Remove. Replace with real-construction tests that verify the attributes are populated by __init__.
- [ ] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py` passes; LOC delta approximate 40

### Task 1.33: `tests/unit/ui/test_race_summary_panel.py`
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] `test_race_summary_panel_stores_race_config` (lines 130-138, 9 LOC) - Remove. Replace with construction-path test.
- [ ] `test_on_load_race_callback_stored / test_has_load_button_reference` (lines 348-367, 20 LOC) - Remove.
- [ ] `Feat12 button callback storage tests` (lines 378-393, 16 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta approximate 45

### Task 1.34: `tests/unit/ui/test_race_theme_gallery.py`
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [ ] `Self-fulfilling assertion tests` (lines 51-70, 20 LOC) - Remove. Replace with real-construction tests.
- [ ] Verify: `pytest tests/unit/ui/test_race_theme_gallery.py` passes; LOC delta approximate 20

### Task 1.35: `tests/unit/ui/test_sprites.py`
**File:** `tests/unit/ui/test_sprites.py`
**Tests:** `pytest tests/unit/ui/test_sprites.py`

- [ ] `test_atlas_fallback_logic` (lines 54-58, 5 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/ui/test_sprites.py` passes; LOC delta approximate 5

### Task 1.36: `tests/unit/ui/test_race_asset_loader.py`
**File:** `tests/unit/ui/test_race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py`

- [ ] `test_load_portrait_full_has_correct_signature` (lines 85-93, 9 LOC) - Remove or replace with a behavioral call.
- [ ] Verify: `pytest tests/unit/ui/test_race_asset_loader.py` passes; LOC delta approximate 9

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
