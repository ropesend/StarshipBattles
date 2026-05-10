# Shard 04 — Test Audit Report

## Summary
- Shard: 04
- Files assigned: 76
- Files actually read: 76
- Total findings: 28
- Critical: 9 | Major: 8 | Minor: 11

## Findings

### tests/unit/core/patterns/test_layer_iterator.py (~301 LOC)
No issues found.

### tests/unit/ui/screens/test_battle_setup_state.py (~331 LOC)

#### CAT-1: test_screen_owns_a_view_model [CRITICAL]
- **Location**: test_battle_setup_state.py:284-294
- **Issue**: Constructs view model, sets it on screen, then asserts `isinstance(screen.view_model, BattleSetupViewModel)` — always True. No failure path.
- **Suggestion**: Remove or fold assertion into a real integration test.
- **LOC affected**: 11

#### CAT-9: TestScreenDelegatesViewStateToViewModel — repeated construction [MINOR]
- **Location**: test_battle_setup_state.py:276-331
- **Issue**: Three test methods (lines 284, 296, 307) repeat the exact same `object.__new__(FleetBattleSetupScreen)` + `BattleSetupViewModel()` pattern.
- **Suggestion**: Extract shared setup into a module-level helper or fixture.
- **LOC affected**: ~55

### tests/unit/strategy/production_engine/test_paused_queue.py (~280 LOC)
No issues found.

### tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py (~54 LOC)

#### CAT-1: test_accepts_can_warp_parameter [CRITICAL]
- **Location**: test_fleet_navigation_no_mock_hack.py:13-19
- **Issue**: Uses `inspect.signature` to check parameter existence — imports always succeed, cannot fail meaningfully.
- **Suggestion**: Remove. If the parameter is part of the API contract, test behavior, not signature.
- **LOC affected**: 7

#### CAT-2: test_no_mock_capabilities_class_in_compute_path [CRITICAL]
- **Location**: test_fleet_navigation_no_mock_hack.py:47-53
- **Issue**: Reads source code via `inspect.getsource()` and asserts a string is not present. Tests text, not behavior.
- **Suggestion**: Remove. If `MockCapabilities` was a hack, a unit test exercising the real SUT with proper DI is the defense.
- **LOC affected**: 7

#### CAT-2: test_can_warp_overrides_fleet_check [CRITICAL]
- **Location**: test_fleet_navigation_no_mock_hack.py:22-40
- **Issue**: Catches `Exception` with `pass` to swallow errors; MagicMock fleet is never validated against real code. The `assert_not_called` assertion is on a mock that was never called because the test swallowed all exceptions.
- **Suggestion**: Refactor to actually exercise the SUT path where `can_warp=True` skips fleet check.
- **LOC affected**: 19

### tests/unit/entities/test_bridge_requirement_removal.py (~56 LOC)
No issues found.

### tests/unit/core/test_pure_loaders.py (~339 LOC)

#### CAT-5: reset_registry autouse fixture [MAJOR]
- **Location**: test_pure_loaders.py:23-28
- **Issue**: `function`-scoped autouse fixture calls `set_default_registry_manager(RegistryManager())` before every test in the file. RegistryManager construction is non-trivial.
- **Suggestion**: Scope to `class` or `module` since tests only read the registry, never mutate it through the singleton. Each class reads different loaders independently.
- **LOC affected**: 6

### tests/unit/strategy/data/test_spatial_index.py (~227 LOC)
No issues found.

### tests/integration/save_load/test_roundtrip_fleet.py (~94 LOC)
No issues found.

### tests/unit/strategy/ship_instance/test_serialization.py (~370 LOC)
No issues found.

### tests/unit/ui/screens/test_strategy_build_queue_manager.py (~290 LOC)
No issues found.

### tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py (~96 LOC)
No issues found.

### tests/unit/strategy/generation/test_astrophysics.py (~258 LOC)

#### CAT-5: loader fixture repeated across 5 classes [MAJOR]
- **Location**: test_astrophysics.py:97-107, 134-138, 167-171, 192-196, 224-228
- **Issue**: Identical `loader` fixture (creates `AstrophysicsLoader()`, calls `loader.load()` in separate data fixtures) defined identically in `TestMassDistributions`, `TestOrbitZones`, `TestHabitableZone`, `TestAtmosphereRetention`, and `TestClassificationThresholds`. Each causes a full file load.
- **Suggestion**: Move to a single `class`- or `module`-scoped fixture.
- **LOC affected**: ~30 (deduplication)

### tests/unit/strategy/galaxy/test_warp_point_validation.py (~71 LOC)
No issues found.

### tests/integration/test_app_integration.py (~262 LOC)

#### CAT-1: test_start_quickstart helper tests [CRITICAL]
- **Location**: test_app_integration.py:218-239
- **Issue**: `test_start_quickstart_1p_uses_helper` and `test_start_quickstart_2p_uses_helper` are identical — both use `inspect.signature` to check parameter names. Different names, zero difference in logic.
- **Suggestion**: Delete one. Both are CAT-1; keeping either adds no value.
- **LOC affected**: 22

#### CAT-2: test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id [CRITICAL]
- **Location**: test_app_integration.py:160-189
- **Issue**: Reads `app.py` source text and asserts a broken call pattern string is absent — tests source code, not behavior.
- **Suggestion**: Replace with actual integration test that calls `start_battle()` and verifies no `TypeError`.
- **LOC affected**: 30

#### CAT-3: test_menu_ui_manager_created_on_demand [CRITICAL]
- **Location**: test_app_integration.py:245-262
- **Issue**: Creates a MagicMock app, sets `menu_ui_manager = None`, then asserts `created is True` on a local variable unconditionally set to `True`. No imports from `game.*`, zero test value.
- **Suggestion**: Remove.
- **LOC affected**: 18

### tests/unit/ai/test_target_evaluator_edge_cases.py (~523 LOC)
No issues found.

### tests/unit/simulation/combat/test_fleet_aura_unregister.py (~181 LOC)
No issues found.

### tests/unit/ui/screens/test_battle_setup_logic.py (~108 LOC)

#### CAT-5: setup_game_data autouse fixture [MAJOR]
- **Location**: test_battle_setup_logic.py:17-31
- **Issue**: `function`-scoped autouse fixture calls `pygame.init()`, `initialize_ship_data()`, `load_components()`, and `get_default_policy_manager().load_data(...)` on every test. Expensive for all 3 tests.
- **Suggestion**: Scope to `module` — tests in this file are read-only.
- **LOC affected**: 15

### tests/repro_issues/test_bug_13_clear_removes_hull.py (~125 LOC)
No issues found.

### tests/unit/simulation/systems/test_battle_logger.py (~317 LOC)
No issues found.

### tests/unit/strategy/data/test_construction_queue_paused_persistence.py (~100 LOC)

#### CAT-4: Fleet and Planet persistence duplicates [MAJOR]
- **Location**: test_construction_queue_paused_persistence.py:34-67 and 69-100
- **Issue**: `TestPlanetConstructionQueuePausedPersistence` and `TestFleetConstructionQueuePausedPersistence` classes each test the identical bool round-trip pattern (default, paused, unpaused, legacy default). Same assertions, same structure — only the entity type differs.
- **Suggestion**: Parametrize over entity type (Planet, Fleet) using a fixture that provides the entity factory. One test class instead of two.
- **LOC affected**: ~60 (half the file)

### tests/unit/strategy/test_engine_event_emission.py (~1022 LOC)

#### CAT-8: Triple-nested patching in spawn tests [MINOR]
- **Location**: test_engine_event_emission.py:102-125, 138-157, 727-741, etc.
- **Issue**: Multiple test methods in `TestShipBuiltEvent`, `TestFleetShipBuiltEvent`, and `TestProductionEventLocationEnrichment` use 3 nested `with patch(...)` blocks (`DesignLibrary`, `ShipInstance`, `Fleet`) whose mocks are always-on pass-throughs.
- **Suggestion**: Extract a `_patch_production_dependencies` context manager or fixture factory. Reduces duplication and nesting.
- **LOC affected**: ~200 (across multiple tests)

#### CAT-9: Repeated mock helper pattern [MINOR]
- **Location**: test_engine_event_emission.py:34-61
- **Issue**: `_make_mock_empire()`, `_make_mock_planet()`, `_make_mock_galaxy()` create MagicMock objects that encode internal implementation details (specific attribute names) used by 20+ tests.
- **Suggestion**: Standard mocks could be promoted to fixtures shared with a `class` scope. Mitigates maintenance churn when internal attribute names change.
- **LOC affected**: ~28

### tests/unit/strategy/ship_instance/test_component_toggles.py (~292 LOC)
No issues found.

### tests/unit/simulation/combat/test_targeting_system.py (~1110 LOC)
No issues found.

### tests/unit/simulation/components/abilities/test_weapons_integration.py (~626 LOC)
No issues found.

### tests/unit/strategy/engine/test_planet_energy_engine.py (~355 LOC)
No issues found.

### tests/integration/ui/test_event_log_replay_e2e.py (~143 LOC)
No issues found.

### tests/unit/strategy/facade/test_fleet_hierarchy_dto.py (~116 LOC)
No issues found.

### tests/integration/strategy/combat/test_storm_shield_interference.py (~395 LOC)
No issues found.

### tests/unit/strategy/engine/test_harvesting_engine.py (~824 LOC)

#### CAT-9: _make_engine helper defined 3 times identically [MINOR]
- **Location**: test_harvesting_engine.py:148-150, 517-519, 694-696
- **Issue**: `_make_engine` method defined identically in `TestHarvestingEngine`, `TestStorageAggregation`, and `TestPerTickHarvesting`.
- **Suggestion**: Move to a shared module-level helper.
- **LOC affected**: 9 (deduplication)

### tests/unit/strategy/engine/test_empire_economy_calculator.py (~1171 LOC)

#### CAT-9: _mock_race_registry fixture duplicated [MINOR]
- **Location**: test_empire_economy_calculator.py:826-835, 1064-1068
- **Issue**: Identical `_mock_race_registry` fixture defined in both `TestPopulationUpkeepAggregation` and `TestTreasuryTotalIncludesUpkeep`.
- **Suggestion**: Define once at module level.
- **LOC affected**: 15

### tests/unit/simulation/test_battle_outcome.py (~278 LOC)
No issues found.

### tests/unit/research/tech_tree/test_loading.py (~346 LOC)
No issues found.

### tests/unit/regressions/test_bug_regressions_2026_01.py (~114 LOC)
No issues found.

### tests/unit/strategy/test_fleet_order_processor.py (~571 LOC)
No issues found.

### tests/unit/research/research_scene/test_interaction.py (~330 LOC)

#### CAT-8: 6 nested patches per test [MINOR]
- **Location**: test_interaction.py:21-27, 52-57, 83-88, 129-134, 164-169, 203-207, 236-240
- **Issue**: Every test method patches 6 classes (`TechTree`, `ResearchTracker`, `Camera`, `pygame_gui`, `ResearchRenderer`, `ResearchControlPanel`). Setup exceeds 50% of each test body.
- **Suggestion**: Extract a `research_scene_deps` fixture that yields all 6 mocks in one `with` block, or use a base test class with `setup_method`.
- **LOC affected**: ~70 (boilerplate reduction)

### tests/integration/strategy/test_event_log_integration.py (~246 LOC)
No issues found.

### tests/unit/ui/widgets/test_dropdown_helper.py (~118 LOC)
No issues found.

### tests/unit/strategy/facade/test_fleet_dto_build.py (~170 LOC)
No issues found.

### tests/unit/systems/test_allowed_layers_removal.py (~88 LOC)
No issues found.

### tests/unit/core/profiling/test_recording.py (~132 LOC)
No issues found.

### tests/unit/strategy/fleet_navigation/test_data_structures.py (~259 LOC)
No issues found.

### tests/unit/simulation/combat/test_weapon_firing_system.py (~1298 LOC)
No issues found.

### tests/unit/simulation/managers/test_retreat_manager.py (~511 LOC)
No issues found.

### tests/integration/fleet_combat/test_service_integration.py (~208 LOC)
No issues found.

### tests/unit/strategy/services/test_action_time_resolver.py (~282 LOC)
No issues found.

### tests/unit/ui/widgets/test_scroll_state.py (~231 LOC)
No issues found.

### tests/integration/strategy/test_deterministic_generation.py (~193 LOC)
No issues found.

### tests/unit/research/tech_tree/test_validation.py (~258 LOC)
No issues found.

### tests/unit/strategy/data/test_empire_fleet_registration.py (~162 LOC)
No issues found.

### tests/unit/ui/test_race_environment_panel.py (~360 LOC)
No issues found.

### tests/unit/simulation/components/abilities/test_static_value_ability.py (~221 LOC)

#### CAT-10: Positive/negative format pair [MINOR]
- **Location**: test_static_value_ability.py:166-176
- **Issue**: `test_positive_value_format` and `test_negative_value_format` in `TestToHitAttackModifierIsStaticValue` have identical bodies differing only in input value (+5 vs -3) and expected string (`'+5.0'` vs `'-3.0'`).
- **Suggestion**: Parametrize: `@pytest.mark.parametrize("value,expected", [(5, '+5.0'), (-3, '-3.0')])`.
- **LOC affected**: 11

### tests/unit/services/llm/test_defaults.py (~33 LOC)
No issues found.

### tests/unit/ui/panels/test_system_tree_panel.py (~664 LOC)

#### CAT-2: Tests bypass __init__ entirely [CRITICAL]
- **Location**: test_system_tree_panel.py:61-177, 213-282, 290-550, 558-580, 606-660
- **Issue**: 30+ test methods use `patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None)` or `patch.object(SystemTreeItem, '__init__', ...)` to bypass all real construction, then set attributes manually. The SUT's real `__init__` behavior is never tested. These test attribute assignment, not production code.
- **Suggestion**: Replace with tests that invoke real constructors. Mock only pygame_gui elements (the external dependency). The current tests verify that Python attribute assignment works — they provide zero regression protection.
- **LOC affected**: ~400 (majority of file)

#### CAT-9: __init__-patching pattern repeated 30+ times [MINOR]
- **Location**: Throughout test_system_tree_panel.py
- **Issue**: Same `with patch.object(Cls, '__init__', lambda self, *a, **kw: None):` pattern on nearly every test. If the __init__ bypass is addressed via CAT-2 above, this is moot.
- **Suggestion**: See CAT-2 above.
- **LOC affected**: ~400 (same scope as CAT-2)

### tests/integration/strategy/test_game_session_strategy.py (~33 LOC)
No issues found.

### tests/unit/simulation/services/test_ship_materializer.py (~310 LOC)
No issues found.

### tests/unit/strategy/data/test_galaxy_warp_generator.py (~54 LOC)
No issues found.

### tests/unit/core/test_exceptions.py (~403 LOC)
No issues found.

### tests/unit/data/test_test_infrastructure.py (~247 LOC)

#### CAT-2: File-existence assertions only [CRITICAL]
- **Location**: test_test_infrastructure.py:22-132
- **Issue**: 8 test methods (lines 22-132) in `TestNoDuplicateTestScripts` only assert file existence/path correctness on disk — no `game.*` imports exercised. These are repo-hygiene checks, not code tests.
- **Suggestion**: Downgrade severity rationale: blast radius is small (only asserts file layout). These are closer to lint checks than tests. Move to a `pre-commit` hook or `Tools/verify_structure.py` script.
- **LOC affected**: ~110

#### CAT-12: if/else branch in test_filter_races_by_name_returns_matches [MINOR]
- **Location**: test_test_infrastructure.py:306-314 (in test_search_filtering, actually in test_race_browser_dialog.py — wrong file for this finding, disregard)

Actually this finding belongs to test_race_browser_dialog.py:306-314. The test_test_infrastructure.py file has no CAT-12 issues beyond the CAT-2 finding above.

### tests/unit/simulation/armor_mechanics/test_damage_reduction.py (~264 LOC)
No issues found.

### tests/unit/ui/test_race_browser_dialog.py (~449 LOC)

#### CAT-12: Conditional logic in test body [MINOR]
- **Location**: test_race_browser_dialog.py:306-314
- **Issue**: `test_filter_races_by_name_returns_matches` contains `if hasattr(dialog, '_filter_races'): ... else: ...` — the else branch tests nothing useful (just checks `get_all_races()` is not None). The test's behavior depends on runtime state.
- **Suggestion**: Remove the else branch. If `_filter_races` doesn't exist, the test should `pytest.skip` or be a dedicated existence test.
- **LOC affected**: 9

### tests/unit/strategy/engine/test_colonize_population.py (~342 LOC)
No issues found.

### tests/unit/ui/screens/test_galaxy_test_screen.py (~96 LOC)
No issues found.

### tests/integration/gameplay_loop/test_turn_execution.py (~284 LOC)

#### CAT-12: Logic-heavy test bodies [MINOR]
- **Location**: test_turn_execution.py:75-103, 120-140, 142-205
- **Issue**: `test_turn_executes_phases_in_order` (line 75) iterates `galaxy.systems.values()` with nested planet lookups and conditional branching. `test_fleet_reaches_destination_over_turns` (line 120) has a for-loop driving turn processing with conditional break. `test_production_completes_across_turns` (line 142) has multiple if-checks and for-loops for multi-turn simulation logic.
- **Suggestion**: For `test_turn_executes_phases_in_order`, use a deterministic test galaxy (seeded) so the planet location is known upfront — removes loop-and-find logic. For multi-turn tests, the loops are inherent to the integration scenario and acceptable.
- **LOC affected**: ~80

### tests/unit/systems/test_formula_system.py (~254 LOC)
No issues found.

### tests/unit/ui/screens/test_click_gate_integration.py (~459 LOC)
No issues found.

### tests/unit/ui/widgets/test_panel_factory.py (~123 LOC)
No issues found.

### tests/integration/ai_strategy/test_commands.py (~81 LOC)
No issues found.

### tests/unit/ui/screens/test_build_queue_viewmodel.py (~382 LOC)
No issues found.

### tests/unit/strategy/facade/test_star_info_dto.py (~218 LOC)
No issues found.

### tests/unit/ui/screens/battle_setup/test_view_model.py (~124 LOC)

#### CAT-1: test_can_construct_without_registries_or_state [CRITICAL]
- **Location**: test_view_model.py:119-124
- **Issue**: Constructs `BattleSetupViewModel()` with no args and asserts `vm is not None` — always True if the import succeeds.
- **Suggestion**: Merge the import-smoke-test assertion into `test_construct_with_no_args` (line 13), which already verifies defaults.
- **LOC affected**: 6

#### CAT-2: test_no_pygame_import_in_view_model_module [CRITICAL]
- **Location**: test_view_model.py:24-39
- **Issue**: Reads source code via `inspect.getsource()` and AST-parses it to verify no pygame imports. Tests architecture convention, not behavior.
- **Suggestion**: Remove. Architecture conventions are enforced by code review and lint rules, not runtime tests.
- **LOC affected**: 16

### tests/unit/ui/components/table/test_column_manager.py (~213 LOC)
No issues found.

### tests/unit/ui/services/battle_ui_service/test_state_and_integration.py (~623 LOC)
No issues found.

### tests/unit/strategy/fleet/test_warp_resources.py (~380 LOC)
No issues found.

### tests/unit/strategy/fleet/test_basics.py (~345 LOC)
No issues found.

### tests/integration/strategy/test_planet_physics.py (~85 LOC)

#### CAT-12: Conditional assertions with physics calculations [MINOR]
- **Location**: test_planet_physics.py:31-59, 61-85
- **Issue**: `test_atmosphere_retention` has two sub-scenarios in one test with intermediate calculations before assertions. `test_greenhouse_effect` has `if press > 10000:` conditional assertion — test behavior branches at runtime on computed values.
- **Suggestion**: Split into two tests or use explicit seed-driven scenarios. Replace `if press > 10000:` with a targeted assertion on the outcome.
- **LOC affected**: ~30

### tests/unit/systems/test_formula_overflow_underflow.py (~285 LOC)
No issues found.

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/core/patterns/test_layer_iterator.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_battle_setup_state.py | Read ✓ | 2 |
| tests/unit/strategy/production_engine/test_paused_queue.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py | Read ✓ | 3 |
| tests/unit/entities/test_bridge_requirement_removal.py | Read ✓ | 0 |
| tests/unit/core/test_pure_loaders.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_spatial_index.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_fleet.py | Read ✓ | 0 |
| tests/unit/strategy/ship_instance/test_serialization.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_build_queue_manager.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py | Read ✓ | 0 |
| tests/unit/strategy/generation/test_astrophysics.py | Read ✓ | 1 |
| tests/unit/strategy/galaxy/test_warp_point_validation.py | Read ✓ | 0 |
| tests/integration/test_app_integration.py | Read ✓ | 3 |
| tests/unit/ai/test_target_evaluator_edge_cases.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_fleet_aura_unregister.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_battle_setup_logic.py | Read ✓ | 1 |
| tests/repro_issues/test_bug_13_clear_removes_hull.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_logger.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_construction_queue_paused_persistence.py | Read ✓ | 1 |
| tests/unit/strategy/test_engine_event_emission.py | Read ✓ | 2 |
| tests/unit/strategy/ship_instance/test_component_toggles.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_targeting_system.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_weapons_integration.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_planet_energy_engine.py | Read ✓ | 0 |
| tests/integration/ui/test_event_log_replay_e2e.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_fleet_hierarchy_dto.py | Read ✓ | 0 |
| tests/integration/strategy/combat/test_storm_shield_interference.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_harvesting_engine.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Read ✓ | 1 |
| tests/unit/simulation/test_battle_outcome.py | Read ✓ | 0 |
| tests/unit/research/tech_tree/test_loading.py | Read ✓ | 0 |
| tests/unit/regressions/test_bug_regressions_2026_01.py | Read ✓ | 0 |
| tests/unit/strategy/test_fleet_order_processor.py | Read ✓ | 0 |
| tests/unit/research/research_scene/test_interaction.py | Read ✓ | 1 |
| tests/integration/strategy/test_event_log_integration.py | Read ✓ | 0 |
| tests/unit/ui/widgets/test_dropdown_helper.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_fleet_dto_build.py | Read ✓ | 0 |
| tests/unit/systems/test_allowed_layers_removal.py | Read ✓ | 0 |
| tests/unit/core/profiling/test_recording.py | Read ✓ | 0 |
| tests/unit/strategy/fleet_navigation/test_data_structures.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_weapon_firing_system.py | Read ✓ | 0 |
| tests/unit/simulation/managers/test_retreat_manager.py | Read ✓ | 0 |
| tests/integration/fleet_combat/test_service_integration.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_action_time_resolver.py | Read ✓ | 0 |
| tests/unit/ui/widgets/test_scroll_state.py | Read ✓ | 0 |
| tests/integration/strategy/test_deterministic_generation.py | Read ✓ | 0 |
| tests/unit/research/tech_tree/test_validation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_empire_fleet_registration.py | Read ✓ | 0 |
| tests/unit/ui/test_race_environment_panel.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_static_value_ability.py | Read ✓ | 1 |
| tests/unit/services/llm/test_defaults.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_system_tree_panel.py | Read ✓ | 2 |
| tests/integration/strategy/test_game_session_strategy.py | Read ✓ | 0 |
| tests/unit/simulation/services/test_ship_materializer.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_galaxy_warp_generator.py | Read ✓ | 0 |
| tests/unit/core/test_exceptions.py | Read ✓ | 0 |
| tests/unit/data/test_test_infrastructure.py | Read ✓ | 1 |
| tests/unit/simulation/armor_mechanics/test_damage_reduction.py | Read ✓ | 0 |
| tests/unit/ui/test_race_browser_dialog.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_colonize_population.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_galaxy_test_screen.py | Read ✓ | 0 |
| tests/integration/gameplay_loop/test_turn_execution.py | Read ✓ | 1 |
| tests/unit/systems/test_formula_system.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_click_gate_integration.py | Read ✓ | 0 |
| tests/unit/ui/widgets/test_panel_factory.py | Read ✓ | 0 |
| tests/integration/ai_strategy/test_commands.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_build_queue_viewmodel.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_star_info_dto.py | Read ✓ | 0 |
| tests/unit/ui/screens/battle_setup/test_view_model.py | Read ✓ | 2 |
| tests/unit/ui/components/table/test_column_manager.py | Read ✓ | 0 |
| tests/unit/ui/services/battle_ui_service/test_state_and_integration.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_warp_resources.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_basics.py | Read ✓ | 0 |
| tests/integration/strategy/test_planet_physics.py | Read ✓ | 1 |
| tests/unit/systems/test_formula_overflow_underflow.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files): ~23,500
- Production code read (sampled): ~2,000
- Approximate headroom: Medium (estimated ~200-500K remaining)
