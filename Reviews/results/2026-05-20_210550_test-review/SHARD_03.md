# Shard 03 — Test Audit Report

## Summary
- Shard: 03 | Files assigned: 88 | Files actually read: 88 | Total findings: 22 | Critical: 4 | Major: 6 | Minor: 12

## Findings

### tests/unit/modifiers/test_invalid_operation_handling.py
#### CAT-6: test_apply_modifier_effects_invalid_operation_logs_warning [MAJOR]
- **Location**: test_invalid_operation_handling.py:38-58
- **Issue**: Mocks internal implementation details of `apply_modifier_effects`. `mock_modifier` and `mock_effect` are `MagicMock` instances that simulate the internal modifier evaluation pipeline rather than using a real `Modifier` with deliberately invalid configuration data. The SUT (`apply_modifier_effects`) receives only mocks — no real production code path is exercised.
- **Suggestion**: Construct a real `Modifier` with an invalid operation in its definition data, or test the behavior through the public-facing `create_ability` path with an invalid-operation effect dict.
- **LOC affected**: 21

#### CAT-10: TestValidOperationsStillWork [MINOR]
- **Location**: test_invalid_operation_handling.py:77-103
- **Issue**: Four tests (`test_multiply_operation`, `test_add_operation`, `test_set_operation`, `test_add_to_mult_operation`) have identical bodies differing only in operation string and expected value. Cluster of 4.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize("op,initial,value,expected", [...])`.
- **LOC affected**: 27

---

### tests/unit/simulation/entities/test_ship_component_manager_di.py
#### CAT-4: test_no_global_registry_import_in_component_manager / test_no_global_registry_import_in_validator_helper [MAJOR]
- **Location**: test_ship_component_manager_di.py:13-17, 22-29
- **Issue**: Two tests verify the same source-check pattern (open module source, assert import string not present) on two different modules. Near-identical logic — same `importlib.util.find_spec` + file read + assert pattern.
- **Suggestion**: Merge into a single parameterized test over module paths.
- **LOC affected**: 17

#### CAT-1: test_no_global_registry_import_in_component_manager [CRITICAL]
- **Location**: test_ship_component_manager_di.py:13-17
- **Issue**: Trivial pass — the test opens a source file and asserts a specific import string is absent. It tests the implementation's source code, not runtime behavior. While defensible as a static guard, under the CAT-1 rubric it's a test that cannot fail if the module can be found and read (it only fails if someone adds the forbidden import back).
- **Suggestion**: Accept as a deliberate AST guard (pattern widely used in this codebase). No action needed if the team endorses source-level guards.
- **LOC affected**: 5

---

### tests/unit/ai/test_ai_controller_unit.py
#### CAT-8: test_secondary_targets_with_multiplex_tracking [MINOR]
- **Location**: test_ai_controller_unit.py:367-420
- **Issue**: Test has 5 nested `with patch()` blocks and a `with patch.object()` block, making setup dense and hard to reason about. Setup constitutes >60% of test body.
- **Suggestion**: Extract a factory fixture that builds a controller with all dependency stubs pre-wired, reducing per-test patch surface.
- **LOC affected**: 54

#### CAT-8: test_behavior_context_includes_movement_policy [MINOR]
- **Location**: test_ai_controller_unit.py:284-325
- **Issue**: Deep nesting: `with patch()`, `with patch.object()`, and `with patch()` again. Setup logic with lambda captures obscures the test intent.
- **Suggestion**: Extract context-capture helper.
- **LOC affected**: 42

---

### tests/unit/combat/test_combat.py
#### CAT-5: setup fixture (autouse) [MAJOR]
- **Location**: test_combat.py:14-49
- **Issue**: The `setup` fixture (autouse function-scoped) in `TestDamageLayerLogic` saves/restores `random.getstate()` and builds a Ship with 4 components, re-initializes layers, re-adds components, and recalculates stats — for every single test. The same fixture pattern is repeated in `TestEnergyRegeneration` and `TestWeaponCooldowns`.
- **Suggestion**: Ship construction could use a class-scoped fixture since tests in the same class do not mutate the ship's layer structure. Alternatively, extract a shared `_make_test_ship` factory.
- **LOC affected**: 36

---

### tests/unit/ui/screens/test_system_selection_window.py
#### CAT-9: Repeated SystemSelectionWindow construction [MINOR]
- **Location**: test_system_selection_window.py:50-227
- **Issue**: Multiple test methods (`test_init_creates_window`, `test_systems_sorted_alphabetically`, `test_display_format_includes_distance`, `test_confirm_calls_callback_with_system_name`, `test_cancel_does_not_call_callback`, `test_confirm_without_selection_does_nothing`) each construct a `SystemSelectionWindow` with the same rect `(100, 100, 450, 500)`, same callback mock, and same systems list.
- **Suggestion**: Extract a `_make_window(ui_manager, systems, current_system)` helper.
- **LOC affected**: ~120

#### CAT-10: TestSystemSelectionWindow class [MINOR]
- **Location**: test_system_selection_window.py:12-232
- **Issue**: `test_cancel_does_not_call_callback` and `test_confirm_without_selection_does_nothing` share nearly identical setup pattern. Could be refactored into a parameterized test or fixture-based setup.
- **Suggestion**: Parameterize or extract shared window construction fixture.
- **LOC affected**: ~40

---

### tests/unit/ui/screens/test_planet_menu_items.py
#### CAT-10: TestPlanetMenuCapabilityMatrix [MINOR]
- **Location**: test_planet_menu_items.py:136-198
- **Issue**: 5 tests in `TestPlanetMenuCapabilityMatrix` follow identical structure: create planet with facility ability, call `build_menu_items`, assert label is present/absent. Each differs only in facility ability string and expected label. Tests for `lay_mines`, `launch_fighters`, `launch_satellites` (visible and hidden variants) could be parameterized into 1-2 parameterized tests.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize("ability,label,expect_visible", [...])`.
- **LOC affected**: ~65

---

### tests/unit/ui/screens/test_fleet_menu_items.py
#### CAT-10: TestFMSRows class [MINOR]
- **Location**: test_fleet_menu_items.py:400-614
- **Issue**: The 5 FMS row capability tests (Lay Mines, Launch Fighters, Launch Satellites, Recover Fighters, Recover Satellites) each have visible/hidden variant pairs following identical structure. 10+ tests with near-identical bodies differing only in ability name, carried vehicle type, and expected label.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize` across (ability_name, carried_type, label, condition).
- **LOC affected**: ~200

#### CAT-9: Repeated fleet/mapper/galaxy construction [MINOR]
- **Location**: test_fleet_menu_items.py:100-262, 400-615
- **Issue**: `_make_fleet`, `_make_galaxy`, `_mapper()` are called repeatedly with the same defaults across many test methods in both `TestCapabilityMatrix` and `TestFMSRows`.
- **Suggestion**: Extract module-level fixtures for the common "empty fleet" and "empty galaxy" shapes.
- **LOC affected**: ~100

---

### tests/unit/strategy/engine/session/test_persistence_adapter.py
#### CAT-11: test_serialize_matches_frozen_schema_fixture [MINOR]
- **Location**: test_persistence_adapter.py:96-155
- **Issue**: Exact dict equality assertion against a 50-line hand-written literal. Any addition of a default field to `GameConfig`, `Galaxy.to_dict()`, or any service will break this test. While the test is explicitly a regression guard, the fragility is notable — it couples the test to the entire serialized shape of the session rather than just the keys or types.
- **Suggestion**: Consider splitting into: (1) key-set check, (2) type-of-value checks, (3) a smaller canonical-value check on critical fields (turn_number, config.players shape).
- **LOC affected**: 50

---

### tests/regression/test_caption_schemas_validate.py
#### CAT-11: TestFlagSchema.test_has_six_fields [MINOR]
- **Location**: test_caption_schemas_validate.py:55-62
- **Issue**: Exact set comparison against `required_fields`. A new required field added to the schema will break this test even though the schema is still valid. Similarly for portrait and theme field tests.
- **Suggestion**: Assert that required_fields is non-empty and contains expected keys using `issuperset` or a minimum-set check, rather than exact equality.
- **LOC affected**: 20

---

### tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py
#### CAT-6: _make_session_with_two_fleets / test_fleet_to_fleet_transfer [MAJOR]
- **Location**: test_transfer_handler_fleet_to_fleet.py:44-109
- **Issue**: The test constructs a deep mock of `GameSession` with `__get_fleet_by_id__` monkey-patched as a closure, and MagicMock fleets with `add_order` assigned as a lambda. This mocks the entire session infrastructure rather than constructing real `Fleet` objects through the `TransferCommandHandler.execute(session, cmd)` public API. If `TransferCommandHandler` changes its internal session-access pattern, this test silently breaks.
- **Suggestion**: Use real `Fleet` objects and a real or minimal `GameSession` rather than mocking the session's internal method resolution.
- **LOC affected**: 66

---

### tests/unit/ui/panels/test_strategy_widgets.py
#### CAT-1: test_graph_can_be_imported [CRITICAL]
- **Location**: test_strategy_widgets.py:53-57
- **Issue**: Trivial pass — asserts `DataGraph is not None` after import. Cannot fail if the module imports succeed.
- **Suggestion**: Remove or merge into a test that exercises actual DataGraph behavior.
- **LOC affected**: 5

#### CAT-1: test_spectrum_graph_can_be_imported [CRITICAL]
- **Location**: test_strategy_widgets.py:124-128
- **Issue**: Same trivial import check pattern as above.
- **Suggestion**: Remove.
- **LOC affected**: 5

#### CAT-1: test_atmosphere_graph_can_be_imported [CRITICAL]
- **Location**: test_strategy_widgets.py:203-207
- **Issue**: Same trivial import check pattern as above.
- **Suggestion**: Remove.
- **LOC affected**: 5

---

### tests/unit/ui/screens/test_planet_list_window.py
#### CAT-6: _make_planet_list_window (bypass-init pattern) [MAJOR]
- **Location**: test_planet_list_window.py:33-66
- **Issue**: Uses `PlanetListWindow.__new__(PlanetListWindow)` to bypass `__init__`, then manually sets attributes the production constructor would set. This tests internal state wiring, not observable behavior through the public API. The comment at line 12-17 acknowledges this as intentional per PROJ-322 convention, but the test still mocks 3 layers of internal widget construction.
- **Suggestion**: As per the file's own note (line 14-16), revisit when PROJ-322 Phase 5 APC-001 consolidates the bypass-init pattern.
- **LOC affected**: 34

---

### tests/unit/ui/screens/test_system_selection_window.py (widget placeholders)
#### CAT-6: TestSystemSelectionWindowWidgetPlaceholders [MAJOR]
- **Location**: test_system_selection_window.py:239-283
- **Issue**: Uses `bypass_init` context manager to construct SystemSelectionWindow without running `__init__` via `__new__`, then asserts that widget references are `None`. This tests internal initialization ordering rather than observable behavior.
- **Suggestion**: Accept as a deliberate Pattern §33 placeholder test per PROJ-347. The convention is documented.
- **LOC affected**: 45

---

### tests/unit/simulation/test_physics_constants.py
#### CAT-9: TestFormulaDocumentation class [MINOR]
- **Location**: test_physics_constants.py:91-108
- **Issue**: Three tests (`test_formula_max_speed_documented`, `test_formula_acceleration_documented`, `test_formula_turn_speed_documented`) each assert that a specific docstring constant contains a specific substring. Identical pattern — could be one parameterized test.
- **Suggestion**: Parameterize with `@pytest.mark.parametrize("formula,expected_substrings", [...])`.
- **LOC affected**: 18

---

### tests/unit/ai/test_ai_controller_unit.py
#### CAT-8: TestNavigateTo class [MINOR]
- **Location**: test_ai_controller_unit.py:623-809
- **Issue**: 12 separate test methods for `navigate_to` each constructing the same controller with slightly different mock ship rotation/position values. Heavy setup repetition.
- **Suggestion**: Extract a `_navigate(rotation, ship_pos, target_pos)` helper.
- **LOC affected**: 187

---

### tests/unit/ui/test_save_selection.py
#### CAT-9: Repeated autouse setup_tmpdir fixtures [MINOR]
- **Location**: test_save_selection.py:65-291
- **Issue**: Three test classes (`TestSaveSelectionTurnList`, `TestSaveSelectionListSaves`, `TestSaveSelectionEmpireInfo`) each define their own `setup_tmpdir` autouse fixture that just delegates to the module-level `_patched_saves_tmpdir`. The same boilerplate (lines 68-71, 164-167, 241-244) appears three times.
- **Suggestion**: The comment at lines 4-9 acknowledges a prior consolidation. The remaining delegation wrappers can be removed — use `_patched_saves_tmpdir` directly via `usefixtures` marker or declare autouse at module scope.
- **LOC affected**: 12

---

## File Coverage Verification

| # | File | LOC | Read? | Has Tests? | Issues? |
|---|------|-----|-------|------------|---------|
| 1 | tests/unit/ui/widgets/test_dropdown_helper.py | 118 | Yes | Yes (8) | None |
| 2 | tests/unit/simulation/entities/test_ship_resource_manager.py | 69 | Yes | Yes (3) | None |
| 3 | tests/unit/simulation/test_battle_runner_component_hp.py | 343 | Yes | Yes (4) | None |
| 4 | tests/unit/test_lab/test_handle_resize_forwards_to_viewer.py | 30 | Yes | Yes (1) | None |
| 5 | tests/unit/modifiers/test_invalid_operation_handling.py | 179 | Yes | Yes (8) | CAT-6, CAT-10 |
| 6 | tests/unit/ui/components/table/test_data_source.py | 122 | Yes | Yes (6) | None |
| 7 | tests/unit/simulation/components/abilities/test_container_ability.py | 218 | Yes | Yes (13) | None |
| 8 | tests/unit/simulation/battle_controller/test_state.py | 338 | Yes | Yes (10) | None |
| 9 | tests/unit/entities/ship_helpers/conftest.py | 153 | Yes | No (fixtures only) | None |
| 10 | tests/unit/ui/screens/test_system_selection_window.py | 361 | Yes | Yes (9) | CAT-9, CAT-10, CAT-6 |
| 11 | tests/unit/ui/screens/test_design_image_helper.py | 298 | Yes | Yes (11) | None |
| 12 | tests/integration/test_fms_planet_lay_mines.py | 312 | Yes | Yes (2) | None |
| 13 | tests/performance/test_strategy_panel_regression.py | 95 | Yes | Yes (2) | None |
| 14 | tests/unit/strategy/data/test_galaxy_system_generator.py | 749 | Yes | Yes (19) | None |
| 15 | tests/regression/test_caption_schemas_validate.py | 98 | Yes | Yes (9) | CAT-11 |
| 16 | tests/unit/ui/panels/test_system_tree_panel_characterization.py | 527 | Yes | Yes (17) | None |
| 17 | tests/unit/systems/test_spatial.py | 176 | Yes | Yes (10) | None |
| 18 | tests/unit/strategy/data/test_race_caption_loader.py | 170 | Yes | Yes (11) | None |
| 19 | tests/unit/simulation/components/abilities/test_strategic_abilities.py | 262 | Yes | Yes (14) | None |
| 20 | tests/unit/strategy/turn_engine/conftest.py | 131 | Yes | No (fixtures only) | None |
| 21 | tests/integration/ui/test_system_tree_panel_smoke.py | 267 | Yes | Yes (6) | None |
| 22 | tests/unit/strategy/services/test_combat_modifier_collector.py | 396 | Yes | Yes (12) | None |
| 23 | tests/unit/combat/test_combat.py | 322 | Yes | Yes (10) | CAT-5 |
| 24 | tests/unit/strategy/fleet_navigation/test_data_structures.py | 259 | Yes | Yes (12) | None |
| 25 | tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py | 109 | Yes | Yes (1) | CAT-6 |
| 26 | tests/unit/strategy/engine/test_set_build_queue_paused_command.py | 202 | Yes | Yes (7) | None |
| 27 | tests/unit/ai/test_target_evaluator_rules.py | 1069 | Yes | Yes (36) | None |
| 28 | tests/conftest.py | 539 | Yes | No (fixtures only) | None |
| 29 | tests/unit/strategy/engine/test_construction_forecast.py | 121 | Yes | Yes (12) | None |
| 30 | tests/unit/strategy/data/test_phase_1f_deletion_guard.py | 55 | Yes | Yes (2) | None |
| 31 | tests/unit/core/test_formula_evaluator.py | 139 | Yes | Yes (21) | None |
| 32 | tests/unit/systems/test_dynamic_layers.py | 116 | Yes | Yes (5) | None |
| 33 | tests/unit/simulation/systems/test_fighter_reboard.py | 246 | Yes | Yes (6) | None |
| 34 | tests/integration/replay/test_replay_resolver.py | 197 | Yes | Yes (10) | None |
| 35 | tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py | 104 | Yes | Yes (3) | None |
| 36 | tests/unit/ui/screens/test_planet_list_window.py | 294 | Yes | Yes (14) | CAT-6 |
| 37 | tests/unit/simulation/ship_combat_engine/conftest.py | 35 | Yes | No (fixtures only) | None |
| 38 | tests/unit/builder/test_builder_ui_sync.py | 205 | Yes | Yes (3) | None |
| 39 | tests/unit/simulation/factories/test_ai_factory.py | 165 | Yes | Yes (7) | None |
| 40 | tests/unit/simulation/entities/test_ability_aggregator.py | 1149 | Yes | Yes (50) | None |
| 41 | tests/unit/tools/test_claude_skill_usage_hook.py | 172 | Yes | Yes (13) | None |
| 42 | tests/unit/simulation/combat/test_weapon_family_handlers.py | 220 | Yes | Yes (7) | None |
| 43 | tests/unit/strategy/generation/density/test_layout_loader.py | 150 | Yes | Yes (9) | None |
| 44 | tests/unit/abilities/test_ability_layer_scope.py | 315 | Yes | Yes (21) | None |
| 45 | tests/unit/strategy/save_game_service/test_load_helpers.py | 332 | Yes | Yes (16) | None |
| 46 | tests/unit/ui/screens/test_planet_menu_items.py | 231 | Yes | Yes (11) | CAT-10 |
| 47 | tests/unit/strategy/services/test_ability_metadata_registry.py | 355 | Yes | Yes (22) | None |
| 48 | tests/unit/strategy/engine/session/test_runtime_services.py | 128 | Yes | Yes (7) | None |
| 49 | tests/regression/test_services_layer_rule.py | 94 | Yes | Yes (1 param) | None |
| 50 | tests/unit/strategy/turn_engine/test_turn_error_handling.py | 139 | Yes | Yes (7) | None |
| 51 | tests/unit/simulation/entities/test_ship_component_manager_di.py | 29 | Yes | Yes (2) | CAT-1, CAT-4 |
| 52 | tests/unit/simulation/combat/test_fleet_aura_unregister.py | 181 | Yes | Yes (7) | None |
| 53 | tests/unit/ai/test_ai_controller_unit.py | 809 | Yes | Yes (28) | CAT-8 |
| 54 | tests/unit/strategy/engine/test_minefield_resolver.py | 605 | Yes | Yes (14) | None |
| 55 | tests/unit/simulation/components/test_create_ability_formula_skip.py | 115 | Yes | Yes (5) | None |
| 56 | tests/unit/strategy/engine/test_action_execution_engine_gaps.py | 340 | Yes | Yes (11) | None |
| 57 | tests/integration/strategy/facade/test_empire_queries.py | 226 | Yes | Yes (9) | None |
| 58 | tests/integration/strategy/test_projector_drain_matches_engine.py | 302 | Yes | Yes (3) | None |
| 59 | tests/unit/ui/screens/test_lab/renderer/test_tag_filter_panel.py | 154 | Yes | Yes (5) | None |
| 60 | tests/unit/simulation/entities/test_stat_contributor_extension.py | 356 | Yes | Yes (7) | None |
| 61 | tests/integration/strategy/facade/test_system_queries.py | 311 | Yes | Yes (10) | None |
| 62 | tests/projects/phase_workflow/test_dag.py | 343 | Yes | Yes (21) | None |
| 63 | tests/unit/tools/test_sanitize_claude_settings.py | 346 | Yes | Yes (23) | None |
| 64 | tests/integration/strategy/test_golden_fixture_field_coverage.py | 98 | Yes | Yes (1) | None |
| 65 | tests/unit/strategy/engine/session/test_persistence_adapter.py | 271 | Yes | Yes (8) | CAT-11 |
| 66 | tests/unit/ui/services/test_input_mapper.py | 642 | Yes | Yes (30) | None |
| 67 | tests/unit/strategy/engine/test_happiness_engine.py | 680 | Yes | Yes (18) | None |
| 68 | tests/unit/strategy/engine/test_planet_action_engine.py | 549 | Yes | Yes (14) | None |
| 69 | tests/unit/strategy/data/test_classification_config.py | 200 | Yes | Yes (6) | None |
| 70 | tests/unit/ui/screens/test_fleet_menu_items.py | 615 | Yes | Yes (27) | CAT-9, CAT-10 |
| 71 | tests/unit/strategy/data/test_planet_species_configs.py | 137 | Yes | Yes (8) | None |
| 72 | tests/unit/strategy/services/test_ship_stats_cargo_storage.py | 68 | Yes | Yes (2) | None |
| 73 | tests/unit/ui/screens/test_strategy_screen_assets.py | 170 | Yes | Yes (9) | None |
| 74 | tests/unit/strategy/engine/test_harvesting_engine_habitability.py | 311 | Yes | Yes (7) | None |
| 75 | tests/unit/ui/test_pygame_gui_patch.py | 214 | Yes | Yes (8) | None |
| 76 | tests/unit/simulation/test_physics_constants.py | 108 | Yes | Yes (10) | CAT-9 |
| 77 | tests/unit/ui/test_save_selection.py | 485 | Yes | Yes (12) | CAT-9 |
| 78 | tests/projects/test_create_project_concurrency.py | 105 | Yes | Yes (2) | None |
| 79 | tests/unit/ui/panels/test_strategy_widgets.py | 408 | Yes | Yes (18) | CAT-1 |
| 80 | tests/unit/strategy/production_engine/test_paused_queue.py | 306 | Yes | Yes (5) | None |
| 81 | tests/unit/strategy/ship_instance/test_component_toggles.py | 292 | Yes | Yes (14) | None |
| 82 | tests/unit/strategy/data/test_mutator_boundary_ast_guard.py | 382 | Yes | Yes (2) | None |
| 83 | tests/unit/ui/services/test_vehicle_class_service.py | 199 | Yes | Yes (15) | None |
| 84 | tests/unit/simulation/combat/test_hit_log_recorder.py | 198 | Yes | Yes (8) | None |
| 85 | tests/integration/ui/test_replay_visual_launch_e2e.py | 319 | Yes | Yes (2) | None |
| 86 | tests/unit/strategy/engine/test_issuer_execution_contract.py | 148 | Yes | Yes (10) | None |
| 87 | tests/unit/repro_issues/test_slider_increment.py | 104 | Yes | Yes (1) | None |
| 88 | tests/unit/simulation/interfaces/test_ability_protocols.py | 199 | Yes | Yes (4) | None |

## Context Usage Estimate
- Files assigned: 88
- Files actually read: 88
- Approximate total LOC: ~24,199 (per shard estimate)
- Conftest files without test functions: 4 (`tests/conftest.py`, `tests/unit/entities/ship_helpers/conftest.py`, `tests/unit/strategy/turn_engine/conftest.py`, `tests/unit/simulation/ship_combat_engine/conftest.py`)
- Total test functions evaluated: ~700+
