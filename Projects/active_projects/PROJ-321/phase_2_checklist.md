# Phase 2: CAT-2 Tests Nothing Real

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-321 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete or rewrite the 26 verified CAT-2 tests-nothing-real tests identified by review `2026-05-02_204633_test-review`. Many of these are full-file deletions (e.g., `test_modifier_logic.py`, `test_testruncard_propulsion.py`); some are bypass-init UI tests where rewrites are out of scope here (handled in PROJ-322 APC-001 phase) - for those CAT-2 entries that overlap with APC-001 cluster files, mark with note `_(APC-001 cluster member - see PROJ-322 Phase 5)_` and target the specific tests not the whole file.

---

## Tasks

### Task 2.1: `tests/integration/test_app_integration.py`
**File:** `tests/integration/test_app_integration.py`
**Tests:** `pytest tests/integration/test_app_integration.py`

- [ ] `Source text scan for broken call pattern` (lines 160-189, 30 LOC) - Replace with behavioral assertion that the production call uses correct kwargs at runtime.
- [ ] `test_start_quickstart_1p_uses_helper / 2p_uses_helper` (lines 218-239, 22 LOC) - Replace with a single behavioral test that calls _start_quickstart with each player_count value.
- [ ] Verify: `pytest tests/integration/test_app_integration.py` passes; LOC delta approximate 52

### Task 2.2: `tests/unit/ai/test_controllable_adapter.py`
**File:** `tests/unit/ai/test_controllable_adapter.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter.py`

- [ ] `ABC interface tests + 130-LOC mock classes` (lines 1-213, 150 LOC) - Keep `test_cannot_instantiate_icontrollable` (line 16) and `test_all_abstract_methods_present` (line 25) as contract checks. Delete the `MockControllable` class (lines 69-163, inside the surrounding `test_mock_implementation_satisfies_interface` method at lines 66-171) and the `FullMockControllable` class (lines 176-210, inside `test_isinstance_check_with_mock` at lines 173-213). Removing both methods (and their nested classes) reclaims the bulk of the LOC; `test_concrete_subclass_must_implement_all` (lines 43-60) may be kept if you want a third small contract check, otherwise delete.
- [ ] Verify: `pytest tests/unit/ai/test_controllable_adapter.py` passes; LOC delta approximate 150

### Task 2.3: `tests/unit/data/test_test_infrastructure.py`
**File:** `tests/unit/data/test_test_infrastructure.py`
**Tests:** `pytest tests/unit/data/test_test_infrastructure.py`

- [ ] `8 test_no_duplicate_* methods` (lines 22-132, 110 LOC) - Convert each of the 8 `test_no_duplicate_*` methods to `@pytest.mark.skip(reason="Migrated to scan, see TODO")` and add an inline comment `# TODO(post-P0): convert this scan to a Tools/ linter or pre-commit hook.` _(Building the linter/hook is out of P0 scope; the skip preserves the recorded intent without expanding scope.)_
- [ ] Verify: `pytest tests/unit/data/test_test_infrastructure.py` passes; LOC delta approximate 110

### Task 2.4: `tests/unit/modifiers/test_seeker_multi_ability.py`
**File:** `tests/unit/modifiers/test_seeker_multi_ability.py`
**Tests:** `pytest tests/unit/modifiers/test_seeker_multi_ability.py`

- [ ] `test_seeker_does_not_use_direct_stats_access` (lines 66-82, 17 LOC) - Remove. Behavioral tests test_seeker_endurance_applies_modifier_correctly already verify correct output values.
- [ ] Verify: `pytest tests/unit/modifiers/test_seeker_multi_ability.py` passes; LOC delta approximate 17

### Task 2.5: `tests/unit/test_lab/test_testruncard_propulsion.py`
**File:** `tests/unit/test_lab/test_testruncard_propulsion.py`
**Tests:** `pytest tests/unit/test_lab/test_testruncard_propulsion.py`

- [ ] `Entire file` (lines 1-229, 229 LOC) - Delete entire file.
- [ ] Verify: `pytest tests/unit/test_lab/test_testruncard_propulsion.py` passes; LOC delta approximate 229

### Task 2.6: `tests/unit/simulation/entities/test_ship_component_manager_di.py`
**File:** `tests/unit/simulation/entities/test_ship_component_manager_di.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager_di.py`

- [ ] `Source-content scan` (lines 1-29, 29 LOC) - Keep as-is. If scan logic is duplicated, consider a shared helper.
- [ ] Verify: `pytest tests/unit/simulation/entities/test_ship_component_manager_di.py` passes; LOC delta approximate 29

### Task 2.7: `tests/unit/strategy/data/test_production_rates.py`
**File:** `tests/unit/strategy/data/test_production_rates.py`
**Tests:** `pytest tests/unit/strategy/data/test_production_rates.py`

- [ ] `3 classes reimplement turn-calculation locally` (lines 108-145, 180-237, 247-283, 133 LOC) - Rewrite to call production _get_facility_production_rates and assert against fixture data; remove local arithmetic.
- [ ] Verify: `pytest tests/unit/strategy/data/test_production_rates.py` passes; LOC delta approximate 133

### Task 2.8: `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`
**File:** `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`

- [ ] `test_get_destination_default_self_fleet_is_none` (lines 175-186, 12 LOC) - Replace with behavioral test test_no_self_fleet_falls_back_to_intercept (line 152) which verifies fallback.
- [ ] Verify: `pytest tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` passes; LOC delta approximate 12

### Task 2.9: `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`
**File:** `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`

- [ ] `test_accepts_can_warp_parameter` (lines 13-19, 7 LOC) - Replace with a behavioral test that calls find_hybrid_path with can_warp and verifies pathfinding behavior changes.
- [ ] `test_no_mock_capabilities_class_in_compute_path` (lines 47-53, 7 LOC) - Remove. Replace with behavioral test that verifies real production path does not need MockCapabilities.
- [ ] `test_can_warp_overrides_fleet_check` (lines 22-40, 19 LOC) - Rewrite to either let exceptions propagate or use a focused assertion on observable state.
- [ ] Verify: `pytest tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` passes; LOC delta approximate 33

### Task 2.10: `tests/unit/strategy/engine/test_commands.py`
**File:** `tests/unit/strategy/engine/test_commands.py`
**Tests:** `pytest tests/unit/strategy/engine/test_commands.py`

- [ ] `test_command_name_property` (lines 41-44, 4 LOC) - Remove.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_commands.py` passes; LOC delta approximate 4

### Task 2.11: `tests/unit/test_modifier_logic.py`
**File:** `tests/unit/test_modifier_logic.py`
**Tests:** `pytest tests/unit/test_modifier_logic.py`

- [ ] `Entire file` (lines 1-103, 103 LOC) - Remove entire file.
- [ ] Verify: `pytest tests/unit/test_modifier_logic.py` passes; LOC delta approximate 103

### Task 2.12: `tests/unit/ui/components/table/test_data_source.py`
**File:** `tests/unit/ui/components/table/test_data_source.py`
**Tests:** `pytest tests/unit/ui/components/table/test_data_source.py`

- [ ] `All non-trivial tests use local subclass stubs` (lines 7-122, 115 LOC) - Add tests for concrete production subclasses (e.g., FleetReportDataSource) in addition to the ABC contract tests. _(verification adjusted from review's "Test concrete production subclasses through the ABC interface, not local in-test..." - see verification_report.md)_
- [ ] Verify: `pytest tests/unit/ui/components/table/test_data_source.py` passes; LOC delta approximate 115

### Task 2.13: `tests/unit/ui/panels/test_race_identity_panel.py`
**File:** `tests/unit/ui/panels/test_race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py`

- [ ] `Most tests bypass-init` (lines 53-428, 375 LOC) - Rewrite to construct through real __init__ with mocked pygame_gui, or migrate to integration tests. _(APC-001 cluster member - see PROJ-322 Phase 5)_
- [ ] Verify: `pytest tests/unit/ui/panels/test_race_identity_panel.py` passes; LOC delta approximate 375

### Task 2.14: `tests/unit/ui/panels/test_ship_detail_panel.py`
**File:** `tests/unit/ui/panels/test_ship_detail_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_ship_detail_panel.py`

- [ ] `Init/state tests use bypass` (lines 130-521, 380 LOC) - Remove tautological TestShipDetailPanelInit; for behavioral classes, switch to real construction with mocked deps. _(APC-001 cluster member - see PROJ-322 Phase 5)_
- [ ] Verify: `pytest tests/unit/ui/panels/test_ship_detail_panel.py` passes; LOC delta approximate 380

### Task 2.15: `tests/unit/ui/panels/test_system_tree_panel.py`
**File:** `tests/unit/ui/panels/test_system_tree_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_system_tree_panel.py`

- [ ] `30+ tests use patch.object(cls, '__init__', ...)` (lines 61-660, 400 LOC) - Construct widgets through real __init__ with mocked pygame_gui or migrate to integration tests.
- [ ] Verify: `pytest tests/unit/ui/panels/test_system_tree_panel.py` passes; LOC delta approximate 400

### Task 2.16: `tests/unit/ui/screens/battle_setup/test_renderer.py`
**File:** `tests/unit/ui/screens/battle_setup/test_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_renderer.py`

- [ ] `test_rebuild_ui_calls_renderer_rebuild` (lines 54-64, 11 LOC) - Replace with a behavioral test that calls _rebuild_ui and asserts renderer.rebuild was called.
- [ ] Verify: `pytest tests/unit/ui/screens/battle_setup/test_renderer.py` passes; LOC delta approximate 11

### Task 2.17: `tests/unit/ui/screens/battle_setup/test_view_model.py`
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [ ] `test_no_pygame_import_in_view_model_module` (lines 24-39, 16 LOC) - Move to Tools/ linter or pre-commit hook.
- [ ] Verify: `pytest tests/unit/ui/screens/battle_setup/test_view_model.py` passes; LOC delta approximate 16

### Task 2.18: `tests/unit/ui/screens/test_build_queue_screen.py`
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] `Entire file uses bypass-init` (lines 1-580, 580 LOC) - Migrate to integration tests with headless pygame_gui setup; remove bypass-init unit tests. _(APC-001 cluster member - see PROJ-322 Phase 5)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen.py` passes; LOC delta approximate 580

### Task 2.19: `tests/unit/ui/screens/test_planet_selection_window.py`
**File:** `tests/unit/ui/screens/test_planet_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_selection_window.py`

- [ ] `Signature-only tests` (lines 28-62, 35 LOC) - Replace with behavioral tests that construct PlanetSelectionWindow with each parameter combination.
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_selection_window.py` passes; LOC delta approximate 35

### Task 2.20: `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**File:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [ ] `TestModalSlotCleanupContract` (lines 405-433, 7 LOC) - Replace source-inspection with behavioral assertion; keep the _on_closed slot-clearing test.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py` passes; LOC delta approximate 7

### Task 2.21: `tests/unit/ui/test_race_description_panel.py`
**File:** `tests/unit/ui/test_race_description_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_description_panel.py`

- [ ] `All RaceDescriptionPanel tests` (lines 39-271, 230 LOC) - Rewrite to use real construction with mocked pygame_gui, or migrate to integration tests. _(APC-001 cluster member - see PROJ-322 Phase 5)_
- [ ] Verify: `pytest tests/unit/ui/test_race_description_panel.py` passes; LOC delta approximate 230

### Task 2.22: `tests/unit/ui/test_race_portrait_gallery.py`
**File:** `tests/unit/ui/test_race_portrait_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py`

- [ ] `All RacePortraitGallery tests` (lines 57-305, 240 LOC) - Rewrite tests to instantiate through normal constructor with mocked pygame_gui dependencies, or migrate to integration tests. _(APC-001 cluster member - see PROJ-322 Phase 5)_
- [ ] Verify: `pytest tests/unit/ui/test_race_portrait_gallery.py` passes; LOC delta approximate 240

### Task 2.23: `tests/unit/simulation/test_unified_entry_guard.py`
**File:** `tests/unit/simulation/test_unified_entry_guard.py`
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py`

- [ ] `21 source-scan tests` (lines 1-741, 420 LOC) - Move scan-based tests to a CI/lint step; keep only runtime behavioral tests in pytest.
- [ ] Verify: `pytest tests/unit/simulation/test_unified_entry_guard.py` passes; LOC delta approximate 420

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
