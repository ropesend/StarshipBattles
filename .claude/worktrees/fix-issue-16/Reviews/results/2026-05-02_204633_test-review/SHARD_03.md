# Shard 03 — Test Audit Report

## Summary
- Shard: 03
- Files assigned: 96
- Files actually read: 96
- Total findings: 34
- Critical: 11 | Major: 15 | Minor: 8

## Findings

### tests/unit/ui/panels/test_race_identity_panel.py (~428 LOC)

#### CAT-2: Most tests exercise no production code (bypass-init)  [CRITICAL]
- **Location**: test_race_identity_panel.py:53-428
- **Issue**: Every test in this file creates `RaceIdentityPanel.__new__(RaceIdentityPanel)` then patches `__init__` to a no-op lambda. All component refs are MagicMock. The real `RaceIdentityPanel.__init__`, `_create_content`, or any pygame_gui widget construction is never exercised. These are pure mock-exercise tests.
- **Suggestion**: Replace with integration tests that instantiate the real panel or delete if covered by integration/UI smoke tests. If keeping as unit tests, at minimum refactor SUT methods to accept deps without sketchy `__new__` + `__init__` patching.
- **LOC affected**: ~200 (multiple test methods)

#### CAT-1: test_identity_panel_creates_successfully  [CRITICAL]
- **Location**: test_race_identity_panel.py:53-64
- **Issue**: Test creates a bare `__new__` instance, sets mock attributes, then asserts `panel._faction_name_overridden is False`. This assertion cannot fail — it was just set to `False` on line 62.
- **Suggestion**: Remove or refactor to test meaningful behavior.
- **LOC affected**: 12

#### CAT-1: test_auto_generate_faction_name_override_preserved  [CRITICAL]
- **Location**: test_race_identity_panel.py:332-344
- **Issue**: Sets `panel._faction_name_overridden = True` on line 342, then asserts it is `True` on line 344. Cannot fail.
- **Suggestion**: Remove.
- **LOC affected**: 13

#### CAT-9: Repeated import + bypass-init in every test  [MINOR]
- **Location**: test_race_identity_panel.py:55-428
- **Issue**: Every test method repeats `from game.ui.panels.race_identity_panel import RaceIdentityPanel` and the identical `patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None)` pattern.
- **Suggestion**: Extract a module-level fixture or helper that sets up the bypass-init mock.
- **LOC affected**: ~180

---

### tests/unit/ui/panels/test_component_modifier_grid_panel.py (~437 LOC)

#### CAT-1: Multiple trivial store-and-assert tests  [CRITICAL]
- **Location**: test_component_modifier_grid_panel.py:38-83, 87-103
- **Issue**: Six tests (`test_panel_stores_manager`, `test_panel_stores_rect`, `test_panel_stores_event_bus`, `test_panel_current_component_starts_none`, `test_subscribes_to_selection_changed`, `test_subscribes_to_ship_updated`) create a bare panel via `__new__`, assign a MagicMock attribute, then assert the attribute is not None or equals the mock. None of these can fail — they test self-assignment.
- **Suggestion**: Remove the trivial attribute-storage tests. Keep only the behavior tests (selection change handling, draw, event handling).
- **LOC affected**: ~65

#### CAT-9: Repeated bypass-init boilerplate  [MINOR]
- **Location**: test_component_modifier_grid_panel.py:38-437
- **Issue**: Every test repeats `patch.object(ComponentModifierGridPanel, '__init__', lambda self, *a, **kw: None)` and `ComponentModifierGridPanel.__new__(ComponentModifierGridPanel)`.
- **Suggestion**: Extract into a module-level helper function.
- **LOC affected**: ~200

---

### tests/unit/ui/test_race_flag_gallery.py (~323 LOC)

#### CAT-1: Attribute existence tests  [CRITICAL]
- **Location**: test_race_flag_gallery.py:57-97
- **Issue**: Four tests (`test_race_flag_gallery_has_button_list`, `test_race_flag_gallery_has_preview_images_list`, `test_race_flag_gallery_has_scroll_container`, `test_race_flag_gallery_has_preview_panel`) create a bare `__new__` instance, assign an attribute, then assert `hasattr`. The assertions test self-assignment and cannot fail.
- **Suggestion**: Remove these trivial tests.
- **LOC affected**: ~40

#### CAT-9: Repeated bypass-init boilerplate  [MINOR]
- **Location**: test_race_flag_gallery.py:61-323
- **Issue**: Every test repeats the same `patch.object(RaceFlagGallery, '__init__', ...)` + `__new__` pattern.
- **Suggestion**: Extract helper fixture.
- **LOC affected**: ~200

---

### tests/unit/ui/screens/test_fleet_report_window.py (~739 LOC)

#### CAT-1: Mock-assignment-only edge case tests  [CRITICAL]
- **Location**: test_fleet_report_window.py:559-666
- **Issue**: Tests `test_selected_indices_out_of_range`, `test_none_fleet_object`, `test_ship_speed_at_zero`, `test_ship_speed_at_max`, `test_ship_at_exactly_zero_hp`, `test_ship_at_exactly_max_hp` assign mock values then assert those same values. None exercises production code (`_make_fleet_report_window` already patches `__init__` to no-op).
- **Suggestion**: Remove tests that don't exercise production behavior.
- **LOC affected**: ~80

#### CAT-8: _make_fleet_report_window is 100+ lines of mock wiring  [MAJOR]
- **Location**: test_fleet_report_window.py:48-145
- **Issue**: The helper creates ~25 mock attributes on a bypass-init window object. Setup dominates test body. Any production change to `FleetReportWindow` attribute names will silently pass these tests.
- **Suggestion**: Use real construction with mock deps where possible, or delete tests covered by integration tests.
- **LOC affected**: 98

---

### tests/unit/research/research_scene/test_callbacks.py (~323 LOC)

#### CAT-8: 5-7 nested `with patch()` blocks per test  [MAJOR]
- **Location**: test_callbacks.py:17-323
- **Issue**: Every test in this file wraps construction in 5-7 `with patch(...)` blocks for `TechTree`, `ResearchTracker`, `Camera`, `pygame_gui`, `ResearchRenderer`, `ResearchControlPanel`, `ResearchService`. Nearly all tests share identical patch setup.
- **Suggestion**: Extract the patch stack into a single `@pytest.fixture` that yields a pre-configured scene. This pattern follows the approach used in `test_builder_ui_sync.py`.
- **LOC affected**: ~250

#### CAT-9: Identical mock setup repeated across 10+ tests  [MINOR]
- **Location**: test_callbacks.py:17-323
- **Issue**: Every test body constructs the same `mock_tree`, `mock_tracker` chain with near-identical MagicMock config.
- **Suggestion**: Extract common mock construction into a fixture.
- **LOC affected**: ~200

---

### tests/unit/research/research_scene/test_initialization.py (~263 LOC)

#### CAT-8: 5-6 nested `with patch()` blocks per test  [MAJOR]
- **Location**: test_initialization.py:13-262
- **Issue**: Same high-nesting pattern as test_callbacks.py. Every test has 5-6 patches for TechTree, ResearchTracker, Camera, pygame_gui, ResearchRenderer, ResearchControlPanel.
- **Suggestion**: Same as above — extract a fixture.
- **LOC affected**: ~230

#### CAT-9: Identical mock setup across 7 tests  [MINOR]
- **Location**: test_initialization.py:13-262
- **Issue**: Same mock_tree/mock_tracker construction copied 7 times.
- **Suggestion**: Extract to fixture.
- **LOC affected**: ~150

---

### tests/unit/research/tech_tree/test_cycle_detection.py (~342 LOC)

#### CAT-9: Repeated structure for adding cycle nodes  [MINOR]
- **Location**: test_cycle_detection.py:109-182
- **Issue**: `test_two_node_cycle`, `test_three_node_cycle`, `test_cycle_with_long_chain`, `test_multiple_independent_cycles` all share identical scaffolding — create nodes, wire requirements, call `detect_cycles()`, assert error count. Could share a helper.
- **Suggestion**: Extract a `_assert_cycles(tree, expected_min_count)` helper.
- **LOC affected**: ~80

---

### tests/unit/strategy/engine/test_superweapon_command_handlers.py (~621 LOC)

#### CAT-4: Fleet-not-found tests duplicated across files  [MAJOR]
- **Location**: test_superweapon_command_handlers.py:105-118 vs test_superweapon_edge_cases.py:188-274
- **Issue**: `test_execute_fails_when_fleet_not_found` for direct handlers in command_handlers.py is structurally identical to the 5 fleet-not-found tests for mission handlers in edge_cases.py (lines 188-274). Same mock setup, same assertion format.
- **Suggestion**: Share mock setup fixture across both files; consider parametrizing the handler classes.
- **LOC affected**: ~80

#### CAT-10: Identical validation-pass / order-type / fleet-not-found tests  [MAJOR]
- **Location**: test_superweapon_command_handlers.py:73-312
- **Issue**: Direct handler tests for ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct all follow identical 3-test pattern: (1) validation passes, (2) correct order type added, (3) fleet-not-found. Could be a single parametrized class.
- **Suggestion**: Parametrize by handler class, command class, expected OrderType.
- **LOC affected**: ~200

---

### tests/unit/strategy/engine/test_superweapon_edge_cases.py (~732 LOC)

#### CAT-4: Mission handler fleet-not-found tests duplicate structure  [MAJOR]
- **Location**: test_superweapon_edge_cases.py:188-274
- **Issue**: Five tests (`test_implode_planet_mission_fleet_not_found`, `test_stellerate_mission_fleet_not_found`, `test_open_warp_point_mission_fleet_not_found`, `test_close_warp_point_mission_fleet_not_found`, `test_create_dyson_sphere_mission_fleet_not_found`) are structurally identical — set fleet to None, create command, execute handler, assert "Fleet not found".
- **Suggestion**: Parametrize by command class + handler class.
- **LOC affected**: ~90

#### CAT-4: Order processor error cases overlap with command handler tests  [MAJOR]
- **Location**: test_superweapon_edge_cases.py:281-508 vs test_superweapon_command_handlers.py:73-367
- **Issue**: The order processor error tests cover paths also exercised (indirectly or at different level) by the command handler tests. While they target different layers (processor vs handler), the mock setup and assertion patterns are near-identical.
- **Suggestion**: Consolidate shared fixtures into a conftest.
- **LOC affected**: ~250

---

### tests/unit/ui/components/table/test_data_source.py (~122 LOC)

#### CAT-2: Tests exercise only local subclass stubs  [CRITICAL]
- **Location**: test_data_source.py:7-122
- **Issue**: Every test creates a locally-defined subclass of `ITableDataSource` with in-test implementations. None imports or exercises a production `ITableDataSource` subclass from `game.*`. The tests validate the contract of the locally-defined mock class, not of any production subclass.
- **Suggestion**: Test a concrete production implementation (e.g., the data source used by BuildQueueScreen or FleetReportWindow) instead of a local stub. Or reclassify as abstract-base-class contract tests and ensure they import from at least one real subclass.
- **LOC affected**: 122

---

### tests/unit/ui/panels/test_system_tree_panel_hazard.py (~109 LOC)

#### CAT-9: Helper functions building identical dict structures  [MINOR]
- **Location**: test_system_tree_panel_hazard.py:5-17
- **Issue**: `_star_provider` and `_effect` helpers build dicts that mirror production data shapes. The tests call `_format_star_hazard_hints` which IS imported from game.*. Not CAT-2, but the helper boilerplate is notable.
- **Suggestion**: Consider extracting test data to a parametrized fixture if more hazard tests are added.
- **LOC affected**: 20

---

### tests/unit/ui/screens/test_strategy_detail_fmt.py (~1427+ LOC)

#### CAT-12: test_type_change_filtering has complex branching logic  [MAJOR]
- **Location**: test_builder_ui_sync.py:132-186
- **Issue**: The test contains `for` loops with `if`/`else` branches to dynamically discover a vehicle type, skips if none found, and then iterates dropdown options with conditional assertions. This is logic that could hide testing gaps — if the dynamic discovery picks different types in different environments, different assertions run.
- **Suggestion**: Hardcode the expected vehicle types or use a parametrized fixture that pre-populates the registry with known types.
- **LOC affected**: 55

---

### tests/unit/core/profiling/test_decorators.py (~158 LOC)

#### CAT-7: time.sleep() in test  [MAJOR]
- **Location**: test_decorators.py:142
- **Issue**: `test_context_manager_measures_time` calls `time.sleep(0.02)` to measure profiling accuracy. This makes the test non-deterministic and can flake under load.
- **Suggestion**: Mock `time.perf_counter` to return controlled values.
- **LOC affected**: 6

---

### tests/unit/core/profiling/test_persistence.py (~177 LOC)

#### CAT-7: time.sleep() in test  [MAJOR]
- **Location**: test_persistence.py:96
- **Issue**: `test_timing_is_reasonably_accurate` calls `time.sleep(0.05)` followed by an assertion on the range `45 < duration < 100`. Non-deterministic; can flake on slow CI.
- **Suggestion**: Mock `time.perf_counter` for deterministic timing.
- **LOC affected**: 7

#### CAT-12: test_timing_is_reasonably_accurate uses arithmetic comparison  [MINOR]
- **Location**: test_persistence.py:89-101
- **Issue**: Assertion computes a range (45-100ms) from a 50ms sleep, introducing arithmetic that masks the actual test intent (that the profiler measures time).
- **Suggestion**: Use mocked perf_counter for exact expectations.
- **LOC affected**: 13

---

### tests/unit/ui/screens/builder/test_builder_ui_sync.py (~203 LOC)

#### CAT-5: autouse fixture with pygame init, file I/O, policy loading  [MAJOR]
- **Location**: test_builder_ui_sync.py:18-85
- **Issue**: `setup_ui` is `autouse=True`, function-scoped, and performs: pygame display init, UIManager construction, SessionRegistryCache file I/O, PolicyManager population, VehicleClassService creation, and real BuilderRightPanel construction. Every test method pays this cost. Used by 3 tests.
- **Suggestion**: Consider session-scoped fixture shared across tests, or split the setup so only the 3 tests that need it pay the cost.
- **LOC affected**: 68

---

### tests/integration/ui/build_queue_screen/test_queue_selector.py (~395 LOC)

#### CAT-5: build_queue_screen fixture creates real BuildQueueScreen  [MAJOR]
- **Location**: test_queue_selector.py:50-123
- **Issue**: `build_queue_screen` is `function`-scoped and creates a real `BuildQueueScreen` with pygame_gui UIManager, Planet creation with PlanetType lookup, Empire creation. Used by 7 tests.
- **Suggestion**: Consider module-scoped fixture if tests don't mutate state.
- **LOC affected**: 74

---

### tests/unit/strategy/engine/test_superweapon_stabilizers.py (~92 LOC)

#### CAT-6: Asserts on mock.call_args.args (implementation detail)  [MAJOR]
- **Location**: test_superweapon_stabilizers.py:89-92
- **Issue**: `test_threads_component_registry_argument` asserts `sentinel in mock_find.call_args.args`. This checks that a sentinel object appears in positional args — a brittle assertion on exact call form. If the production code switches from positional to keyword passing, the test fails even though behavior is correct.
- **Suggestion**: Assert that the sentinel value was passed as the `component_registry=` kwarg specifically, or assert functional behavior (e.g., that the mock was called with the sentinel anywhere in the call).
- **LOC affected**: 8

---

### tests/unit/ui/screens/test_fleet_report_window_multi_select.py (~457 LOC)

#### CAT-8: 3-5 nested `with patch()` blocks per fixture  [MAJOR]
- **Location**: test_fleet_report_window_multi_select.py:76-117, 148-178, 234-268, 389-427
- **Issue**: Multiple fixtures (`mock_fleet_window_init`, `window_with_ships`, `window_with_ships_and_empire`, `sidebar_with_button`) each have 3-5 nested `with patch()` blocks. The sidebar fixture patches 7 different modules and 8 widget classes.
- **Suggestion**: Consolidate patches into a single context manager helper or conftest fixture.
- **LOC affected**: ~150

---

### tests/unit/simulation/replay/test_serialization.py (~531 LOC)

#### CAT-10: Parametrize opportunity for boundary tests  [MAJOR]
- **Location**: test_serialization.py:240-255
- **Issue**: `test_roundtrip` already parametrizes 4 boundary types correctly. No issue here — this is a GOOD pattern. However, similar round-trip tests for BattleSpec, BattleOutcome, ReplayRecord each do a full-manual construction. The per-field assertions at lines 315-331 and 385-396 are fragile to dataclass field additions.
- **Suggestion**: Consider deep-equality comparison where frozen dataclass `__eq__` supports it, rather than manual field-by-field assertions.
- **LOC affected**: ~40

---

### tests/unit/ui/screens/test_planet_list_components.py (~887 LOC)

#### CAT-12: Non-trivial setup in multiple tests with loops and branching  [MAJOR]
- **Location**: test_planet_list_components.py:331-365
- **Issue**: `test_applies_owner_filters_updates_buttons` creates per-button mocks, asserts on each individually (`.select.assert_called_once()`, `.unselect.assert_called_once()`). The logic mirrors production code's button-wiring logic rather than testing functional outcome.
- **Suggestion**: Test the end state (which buttons are selected/unselected) rather than the exact call sequence.
- **LOC affected**: 35

---

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/ui/panels/test_race_identity_panel.py | Read | CAT-1, CAT-2, CAT-9 |
| tests/repro_issues/test_bug_27_ordertype.py | Read | Clean |
| tests/unit/ui/services/battle_ui_service/test_conversion.py | Read | Clean |
| tests/regression/modifier_ability_snapshots/test_utility_modifiers.py | Read | Clean |
| tests/unit/strategy/galaxy/test_star_system_validation.py | Read | Clean |
| tests/unit/research/test_research_service.py | Read | Clean |
| tests/unit/ai/test_movement_and_ai.py | Read | Clean |
| tests/unit/strategy/data/test_planet_active_abilities.py | Read | Clean |
| tests/unit/ui/screens/test_race_setup_screen_public_api.py | Read | Clean |
| tests/unit/strategy/consumable_management_engine/test_consumption.py | Read | Clean |
| tests/unit/simulation/components/test_component_loader.py | Read | Clean |
| tests/unit/simulation/components/abilities/test_strategic_abilities.py | Read | Clean |
| tests/integration/ui/build_queue_screen/test_queue_selector.py | Read | CAT-5 |
| tests/unit/strategy/systems/test_race_library.py | Read | Clean |
| tests/unit/simulation/components/abilities/test_ability_scope_extensions.py | Read | Clean |
| tests/unit/ui/screens/test_fleet_report_window_multi_select.py | Read | CAT-8 |
| tests/unit/ui/panels/test_component_modifier_grid_panel.py | Read | CAT-1, CAT-9 |
| tests/unit/research/research_scene/test_callbacks.py | Read | CAT-8, CAT-9 |
| tests/unit/simulation/entities/test_ship_loader.py | Read | Clean |
| tests/integration/save_load/test_resupply_persistence.py | Read | Clean |
| tests/unit/simulation/replay/test_serialization.py | Read | CAT-11 |
| tests/integration/gameplay_loop/test_fleet_operations.py | Read | Clean |
| tests/unit/strategy/engine/test_superweapon_stabilizers.py | Read | CAT-6 |
| tests/projects/test_extract_phase.py | Read | Clean |
| tests/unit/strategy/combat/test_spec_compiler.py | Read | Clean |
| tests/unit/fixtures/test_component_fixtures.py | Read | Clean |
| tests/unit/ui/screens/test_strategy_renderer_animation.py | Read | Clean |
| tests/unit/strategy/galaxy/test_galaxy_validation.py | Read | Clean |
| tests/unit/ui/test_config.py | Read | Clean |
| tests/unit/research/test_research_renderer.py | Read | Clean |
| tests/unit/core/profiling/test_decorators.py | Read | CAT-7 |
| tests/unit/research/tech_tree/test_cycle_detection.py | Read | CAT-9 |
| tests/unit/strategy/facade/test_facade_system_proximity.py | Read | Clean |
| tests/unit/simulation/battle_controller/test_initialization.py | Read | Clean |
| tests/unit/simulation/battle_controller/test_state.py | Read | Clean |
| tests/unit/ui/screens/test_design_image_helper.py | Read | Clean |
| tests/integration/quickstart/test_quickstart_flow.py | Read | Clean |
| tests/unit/simulation/projectile_guidance/test_guidance_core.py | Read | Clean |
| tests/unit/strategy/services/ability_sources/test_storm.py | Read | Clean |
| tests/unit/simulation/validation/test_mass_placement_allowed.py | Read | Clean |
| tests/unit/ui/screens/test_strategy_ui_tooltips.py | Read | Clean |
| tests/unit/ui/panels/test_system_tree_panel_hazard.py | Read | Clean |
| tests/integration/strategy/test_fleet_registration_wiring.py | Read | Clean |
| tests/unit/strategy/design_library/test_design_load_result.py | Read | Clean |
| tests/integration/strategy/test_growth_rate_equivalence.py | Read | Clean |
| tests/unit/builder/test_builder_ui_sync.py | Read | CAT-5, CAT-12 |
| tests/unit/simulation/combat/test_formation_defaults.py | Read | Clean |
| tests/unit/ui/screens/test_planet_list_components.py | Read | CAT-12 |
| tests/unit/strategy/stars/test_star_validation.py | Read | Clean |
| tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py | Read | Clean |
| tests/unit/ui/screens/test_fleet_report_window.py | Read | CAT-1, CAT-8 |
| tests/unit/ui/test_race_flag_gallery.py | Read | CAT-1, CAT-9 |
| tests/unit/strategy/engine/test_superweapon_command_handlers.py | Read | CAT-4, CAT-10 |
| tests/integration/save_load/test_roundtrip_research.py | Read | Clean |
| tests/integration/resource_system/test_custom_resource_lifecycle.py | Read | Clean |
| tests/unit/builder/test_ship_validator_di.py | Read | Clean |
| tests/unit/strategy/services/ability_sources/test_warp_point.py | Read | Clean |
| tests/unit/systems/test_physics_edge_cases.py | Read | Clean |
| tests/unit/strategy/ship_instance/test_cost_queries.py | Read | Clean |
| tests/unit/strategy/stars/test_spectrum_validation.py | Read | Clean |
| tests/unit/core/test_resource_catalog.py | Read | Clean |
| tests/unit/strategy/ship_instance/test_registries_di.py | Read | Clean |
| tests/unit/strategy/services/ability_sources/test_dual_scope_validation.py | Read | Clean |
| tests/unit/ui/services/image/test_openai_provider.py | Read | Clean |
| tests/unit/ui/components/table/test_data_source.py | Read | CAT-2 |
| tests/integration/test_strategic_abilities.py | Read | Clean |
| tests/integration/research_workflow/test_persistence.py | Read | Clean |
| tests/unit/ui/screens/test_strategy_detail_fmt.py | Read | Clean |
| tests/unit/strategy/services/test_design_cost_calculator.py | Read | Clean |
| tests/unit/core/test_paths_config.py | Read | Clean |
| tests/unit/simulation/combat/test_modifier_stack.py | Read | Clean |
| tests/unit/strategy/engine/test_production_spawner_staging_yard.py | Read | Clean |
| tests/unit/test_lab/test_viewmodel.py | Read | Clean |
| tests/unit/test_lab/test_batch_skip.py | Read | Clean |
| tests/unit/test_lab/test_test_run_details_public_api.py | Read | Clean |
| tests/integration/data/test_intrinsic_registries_coverage.py | Read | Clean |
| tests/unit/ui/screens/test_food_allocation_editor.py | Read | Clean |
| tests/unit/research/research_scene/test_initialization.py | Read | CAT-8, CAT-9 |
| tests/unit/strategy/ship_instance/test_convenience_methods.py | Read | Clean |
| tests/integration/strategy/test_event_log_empire_filter.py | Read | Clean |
| tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py | Read | Clean |
| tests/unit/modifiers/test_crew_required_mass_scaling.py | Read | Clean |
| tests/unit/core/profiling/test_persistence.py | Read | CAT-7, CAT-12 |
| tests/unit/ui/services/image/test_provider.py | Read | Clean |
| tests/unit/strategy/validation/test_transfer_drop_pod.py | Read | Clean |
| tests/unit/simulation/combat/test_damage_calculator_events.py | Read | Clean |
| tests/unit/ui/services/test_tkinter_utils.py | Read | Clean |
| tests/unit/strategy/generation/density/test_linear.py | Read | Clean |
| tests/unit/simulation/test_battle_runner_telemetry.py | Read | Clean |
| tests/unit/strategy/engine/test_superweapon_edge_cases.py | Read | CAT-4 |
| tests/unit/ui/screens/test_strategy_panel_manager.py | Read | Clean |
| tests/unit/ui/screens/test_setup_data_io.py | Read | Clean |
| tests/unit/simulation/systems/test_ship_design_stats.py | Read | Clean |
| tests/unit/ui/screens/test_cargo_quick_dialog.py | Read | Clean |
| tests/unit/strategy/data/test_planet_physics.py | Read | Clean |
| tests/unit/strategy/combat/test_spec_compiler_formation.py | Read | Clean |

## Context Usage Estimate
- Total LOC read: ~23,668 (all 96 files)
- Approximate headroom: Low (files were read in large parallel batches; context was saturated)
