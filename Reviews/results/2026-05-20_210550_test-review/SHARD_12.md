# Shard 12 — Test Audit Report

## Summary
- Shard: 12 | Files assigned: 94 | Files actually read: 94 | Total findings: 22 | Critical: 2 | Major: 8 | Minor: 12

## Findings

### tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py
#### CAT-1: test_phase_4_collapsed_per_decisions [CRITICAL]
- **Location**: test_planet_fleet_empire_post_436_contract.py:89-98 | **Issue**: Single assertion is `assert True` — test cannot fail regardless of code state. The docstring explains this is intentional as a documentation marker, but it is still a trivial pass. | **Suggestion**: Remove the test; replace with a doc-only marker comment in the module or a decisions.md reference. Tests with `assert True` have zero regression value. | **LOC affected**: 10

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-1: test_create_default_turn_engine_factory_not_importable [CRITICAL]
- **Location**: test_turn_engine_lazy_properties.py:313-320 | **Issue**: Test asserts `not hasattr(turn_engine_module, "create_default_turn_engine")` using `hasattr` fallback pattern. If the module import succeeds, this assertion is structurally equivalent to `assert True` — it verifies absence of a deleted symbol rather than exercising any game logic. Note: this is a valid regression guard but qualifies as trivial per CAT-1 definition. | **Suggestion**: Either reclassify as a static guard test (like `tests/static_guards/` pattern) or keep alongside the `_NullBattleResolver` removed test. The combined guards have marginal value but documentation value. | **LOC affected**: 8

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-10: 18 engine-default property tests (TestEagerDefaultEngines class) [MINOR]
- **Location**: test_turn_engine_lazy_properties.py:34-178 | **Issue**: 18 near-identical tests check `isinstance(engine.X, SomeClass)` and `engine.X is engine.X` for 18 sub-engine properties. Same 3-line body repeated 18 times with different class imports and attribute names. | **Suggestion**: Parametrize into a single test with `(attr_name, expected_class)` pairs. Would reduce ~145 LOC to ~15 LOC. | **LOC affected**: 145

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-4: test_planet_modifier_effect_engine_property_returns_cached_instance duplicates TestEagerDefaultEngines pattern [MAJOR]
- **Location**: test_turn_engine_lazy_properties.py:290-302 | **Issue**: This test has the identical structure as the 18 tests above (isinstance + identity check) but lives in a separate class `TestPlanetModifierEffectEngineLazyProperty` outside the parameterizable pattern. | **Suggestion**: Fold into the parametrized cluster alongside the 18 eager-default tests. | **LOC affected**: 13

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-6: test_conflict_engine_resolver_guard_present_at_dispatch_site [MAJOR]
- **Location**: test_turn_engine_lazy_properties.py:219-251 | **Issue**: Uses `inspect.getsource()` to read the source of a production method and asserts on string contents (`"self._battle_resolver is None" in src`). This is extremely brittle — any reformatting, comment addition, or refactoring of `_resolve_combat_at_hex` breaks the test even if the guard still works. | **Suggestion**: Replace with a behavioral test that constructs a ConflictResolutionEngine with `battle_resolver=None` and verifies the expected ValueError is raised when dispatching a battle. | **LOC affected**: 33

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-6: test_registry_module_does_not_import_planet_modifier_effect_engine [MAJOR]
- **Location**: test_turn_engine_lazy_properties.py:262-288 | **Issue**: AST-walks a production file to check import statements. Brittle to refactoring — changing import order, adding an unrelated comment, or moving the import to a different module would break this test without any behavioral regression. | **Suggestion**: This is a structural guard better suited as a linter rule or static guard script. If kept as a test, the import-guard tests should be consolidated under `tests/static_guards/`. | **LOC affected**: 27

### tests/unit/strategy/engine/test_order_processor_facade.py
#### CAT-6: test_order_processor_minimal_order_type_references [MAJOR]
- **Location**: test_order_processor_facade.py:32-57 | **Issue**: AST-parses `order_processor.py` and counts `ast.Attribute` nodes referencing `OrderType`. Brittle — refactoring the file structure (imports, helper methods) could change the count without behavioral change. | **Suggestion**: Replace with a behavioral invariant test. If the intent is to prevent new branching ladders, extract a registry-based check rather than counting AST nodes. | **LOC affected**: 26

### tests/unit/ui/test_race_browser_dialog.py
#### CAT-6: Multiple tests patch RaceBrowserDialog.__init__ with no-op lambda [MAJOR]
- **Location**: test_race_browser_dialog.py:78, 106, 132, 158, 172, 208, 233, 267, 290, 315, 333, 373 | **Issue**: 12 tests use `patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None)` followed by `RaceBrowserDialog.__new__(RaceBrowserDialog)`. This bypasses the constructor entirely and manually wires attributes, making tests fragile to internal refactoring. The test is testing the class methods but not the initialization flow. | **Suggestion**: Either create a proper test double or use `bypass_init` pattern (already used in other test files like `test_battle_setup_logic.py`). The existing `tests/fixtures/ui_widget_factory.py:bypass_init` helper is available. | **LOC affected**: ~200 (across 12 tests)

### tests/unit/ui/test_colors.py
#### CAT-1 adj: test_no_duplicate_color_values, test_colors_dict_is_not_empty [not flagged - constants validation]
- **Location**: test_colors.py:38-58 |
These are constants validation tests explicitly excluded from CAT-1 by the rubric.

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-12: test_turn_engine_lazy_properties.py overall [MINOR]
- **Location**: Whole file 320 lines | **Issue**: File requires `from game.strategy.engine import turn_phase_registry as _reg` and performs `Path(_reg.__file__).read_text()` + `ast.parse(src)` inside a test method, which has logic-heavy analysis (for loops, isinstance checks, conditional printing). | **Suggestion**: Split AST-guard tests into a separate static-guard file. Keep behavioral tests in this file. | **LOC affected**: 27

### tests/unit/ui/test_modifier_impact_grid.py
#### CAT-8: setup_method/teardown_method with pygame init in two test classes [MINOR]
- **Location**: test_modifier_impact_grid.py:10-18, 235-244 | **Issue**: Both `TestModifierImpactGrid` and `TestPROJ339Characterization` call `pygame.init()` + `pygame.display.set_mode()` + `pygame_gui.UIManager()` per test method via `setup_method`. 5+ nested with/patch blocks in several tests. | **Suggestion**: Use module-scoped pygame init fixture (already common in the codebase — see `tests/unit/ui/conftest.py` patterns). | **LOC affected**: ~30 (setup/teardown), ~150 (complex test bodies)

### tests/unit/ui/test_fleet_report_filters.py
#### CAT-8: make_mock_ship helper is 105 lines with deep manager wiring [MINOR]
- **Location**: test_fleet_report_filters.py:12-109 | **Issue**: The `make_mock_ship` helper is extremely complex — instantiates `ShipConsumableManager` and `ShipCargoManager`, wires closures for cargo lookups, and exposes 10+ parameters. Setup > 50% of many tests. | **Suggestion**: Extract to a shared fixture in `tests/fixtures/` with session scope or class scope. | **LOC affected**: 98

### tests/unit/ui/test_fleet_report_filters.py
#### CAT-10: Multiple parameterize clusters already done, but some remaining [MINOR]
- **Location**: test_fleet_report_filters.py:388-448 (warp filter tests), 451-628 (sort tests) | **Issue**: Warp filter tests (3 near-identical tests) and sort tests (5+ tests with same structure) could be further parametrized. Partially addressed by PROJ-323 Task 3.1 but some clusters remain. | **Suggestion**: Continue parametrization — warp YES/NO/IGNORE already parametrized. Sort tests could be parametrized by sort_key and expected order. | **LOC affected**: ~150

### tests/integration/strategy/test_deterministic_generation.py
#### CAT-10: 4 tests with identical structure verifying seed determinism for different attributes [MINOR]
- **Location**: test_deterministic_generation.py:18-127 | **Issue**: `test_same_seed_produces_identical_system_coordinates`, `test_same_seed_produces_identical_star_counts`, `test_same_seed_produces_identical_planet_counts`, `test_same_seed_produces_identical_star_types` all have the same structure: create two identical configs, create sessions, compare the attribute. | **Suggestion**: Parametrize with `(galaxy_type, seed, attribute_getter)` tuples. Would reduce ~90 LOC to ~25. | **LOC affected**: 90

### tests/unit/strategy/engine/test_order_processor_colonize.py
#### CAT-11: test_process_colonize_seeds_stockpile_from_design_initial_stockpile [MINOR]
- **Location**: test_order_processor_colonize.py:247-248 | **Issue**: Exact dict match assertion `add_calls == {"metals": 50.0, "organics": 25.0}` against `call_args_list`. If additional resources are ever added to the stockpile seeding (or order of calls changes), this exact match breaks even if behavior is correct. | **Suggestion**: Assert individual key/value pairs instead: `assert add_calls.get("metals") == 50.0` and `assert add_calls.get("organics") == 25.0`. | **LOC affected**: 2

### tests/unit/strategy/data/test_fleet_group_kind.py
#### CAT-3 adj: Regression guards for deleted functionality [not flagged]
- **Location**: test_fleet_group_kind.py:1-65 |
These tests verify absence of deleted symbols (`group_kind`, `_reject_if_non_fleet_group`). Per the rubric, these are valid regression guards — not dead test code. They prevent reintroduction of deleted APIs.

### tests/unit/simulation/battle_controller/test_execution.py
#### CAT-3 adj: Regression guard for deleted run_headless method [not flagged]
- **Location**: test_execution.py:149-165 |
Tests that `BattleController.run_headless` does NOT exist. Valid regression guard for deleted code — not dead test code. Protects against re-introduction.

### tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py
#### CAT-3 adj: NullBattleResolverSymbolAbsent regression guards [not flagged]
- **Location**: test_turn_engine_lazy_properties.py:305-320 |
Tests verify deleted `_NullBattleResolver` and `create_default_turn_engine` are absent. Valid regression guards.

### tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py
#### CAT-12: test_phase_4_gates_still_pass uses dynamic imports [MINOR]
- **Location**: test_order_processor_facade.py:60-75 | **Issue**: Imports two other test modules as side-effects to verify their named tests exist via `hasattr` checks. This cross-test dependency is fragile and couples test files. | **Suggestion**: Remove this meta-test. Pytest already discovers and runs those tests independently. Use `pytest --collect-only` or CI pipeline checks for structural coverage. | **LOC affected**: 16

### tests/unit/ui/screens/test_strategy_menu_actions.py
#### CAT-9: Repeated _make_strategy_screen calls across 20+ tests [MINOR]
- **Location**: test_strategy_menu_actions.py:15-40 (helper), used in nearly every test | **Issue**: Almost every test calls `_make_strategy_screen()` to create the same StrategyScreen mock. The helper is well-written but is called in 20+ locations. | **Suggestion**: Convert to a pytest fixture with function scope. Already partially addressed — the helper is clean. This is low-priority. | **LOC affected**: ~0 (minor refactor suggestion only)

### tests/unit/ui/screens/battle_setup/test_spec_compiler.py
#### CAT-12: test_compiler_does_not_mutate_ships iterates with loops and snapshots [MINOR]
- **Location**: test_spec_compiler.py:297-335 | **Issue**: Uses for loops with nested assertions to capture/compare ship attributes before and after compilation. While this is a valid test pattern, the 38-line test body has significant logic. | **Suggestion**: Consider extracting the snapshot/compare into a helper. | **LOC affected**: 39

### tests/fixtures/test_scenarios.py
#### CAT-8: create_mock_test_scenario creates 20+ attribute MagicMock [MINOR]
- **Location**: test_scenarios.py:84-171 | **Issue**: Fixture helper `create_mock_test_scenario` sets up a Mock with 20+ attributes, including an `empty_spec` with its own mocks and a real `ModifierStack.empty()`. Large mock construction for a single object. | **Suggestion**: This is a fixture utility, not a test. Acceptable complexity given it serves multiple test files. No action needed at this time. | **LOC affected**: 88

### tests/unit/ui/screens/battle_setup/test_renderer.py
#### CAT-8: test_screen_holds_renderer_instance bypasses __init__ [MINOR]
- **Location**: test_renderer.py:45-52 | **Issue**: Uses `object.__new__(FleetBattleSetupScreen)` to bypass `__init__` and manually sets `screen.renderer`. The test only verifies attribute assignment, not behavior. | **Suggestion**: This is a structural smoke test — low value but acceptable as a contract guard. No action needed. | **LOC affected**: 8

### tests/unit/test_app_public_api.py
#### CAT-8: test_game_has_required_method parametrized with 29 method names [MINOR]
- **Location**: test_app_public_api.py:50-91 | **Issue**: Single parametrized test checks 29 method names via `hasattr` + callable check. This is well-structured parametrization but checks a large number of surface-level attributes that are unlikely to regress individually. | **Suggestion**: Keep as-is. The test value lies in catching accidental method renames during refactoring. | **LOC affected**: 42

### tests/unit/test_app_public_api.py
#### CAT-6: test_game_init_signature uses inspect.signature on constructor [MINOR]
- **Location**: test_app_public_api.py:39-47 | **Issue**: Uses `inspect.signature(Game.__init__)` to assert parameter names and defaults. Brittle to parameter renames (e.g., `args` → `cli_args`). | **Suggestion**: Replace with a behavioral test — call `Game()` with no args and verify it doesn't raise. | **LOC affected**: 9

## File Coverage Verification
| File | Read | Test Functions | Findings |
|------|------|---------------|----------|
| tests/unit/ui/screens/test_strategy_colonization.py | ✓ | 7 | 0 |
| tests/integration/strategy/test_fleet_sector_effects_end_to_end.py | ✓ | 6 | 0 |
| tests/unit/strategy/engine/test_production_repro.py | ✓ | 2 | 0 |
| tests/unit/simulation/combat/test_weapon_dispatch_golden.py | ✓ | 9 | 0 |
| tests/unit/strategy/interfaces/test_battle_resolver.py | ✓ | 9 | 0 |
| tests/unit/data/test_test_infrastructure.py | ✓ | 5 | 0 |
| tests/unit/test_lab/test_renderer_public_api.py | ✓ | 4 | 0 |
| tests/integration/save_load/test_full_roundtrip.py | ✓ | 13 | 0 |
| tests/unit/modifiers/test_defense_marker_bindings.py | ✓ | 3 | 0 |
| tests/unit/builder/test_designs.py | ✓ | 8 | 0 |
| tests/unit/ui/components/table/test_selection.py | ✓ | 21 | 0 |
| tests/unit/simulation/systems/test_add_ship_mid_battle.py | ✓ | 5 | 0 |
| tests/unit/strategy/engine/test_superweapon_handler_validation.py | ✓ | 3 | 0 |
| tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py | ✓ | 4 | 0 |
| tests/unit/services/llm/test_provider_protocol.py | ✓ | 3 | 0 |
| tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py | ✓ | 6 | CAT-1 (1) |
| tests/unit/strategy/test_design_metadata.py | ✓ | 29 | 0 |
| tests/unit/agent_coordination/test_partner_invoke.py | ✓ | 26 | 0 |
| tests/integration/resource_system/test_custom_resource_lifecycle.py | ✓ | 5 | 0 |
| tests/unit/ui/test_race_browser_dialog.py | ✓ | 13 | CAT-6 (1) |
| tests/unit/simulation/systems/test_design_stats_no_fallback.py | ✓ | 2 | 0 |
| tests/unit/ai/test_movement_and_ai.py | ✓ | 2 | 0 |
| tests/unit/strategy/fleet/test_movement_resources.py | ✓ | 14 | 0 |
| tests/unit/ui/screens/test_fleet_report_filters.py | ✓ | 26 | CAT-8, CAT-10 |
| tests/unit/ui/screens/builder/test_modifier_control_row.py | ✓ | 11 | 0 |
| tests/unit/ui/panels/test_system_tree_panel_hazard.py | ✓ | 13 | 0 |
| tests/unit/ui/screens/test_strategy_menu_actions.py | ✓ | 22 | CAT-9 |
| tests/unit/strategy/production_engine/test_resource_costs.py | ✓ | 9 | 0 |
| tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py | ✓ | 10 | 0 |
| tests/unit/strategy/data/test_containable.py | ✓ | 13 | 0 |
| tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py | ✓ | 18 | 0 |
| tests/unit/ui/screens/strategy_render/test_dyson_spheres.py | ✓ | 8 | 0 |
| tests/unit/ai/test_group_target_coordinator.py | ✓ | 22 | 0 |
| tests/unit/strategy/services/test_system_effects_collector_decomposition.py | ✓ | 10 | 0 |
| tests/unit/simulation/test_battle_runner.py | ✓ | 13 | 0 |
| tests/unit/simulation/components/test_modifier_effects.py | ✓ | 24 | 0 |
| tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py | ✓ | 21 | CAT-1, CAT-4, CAT-6 (2), CAT-10, CAT-12 |
| tests/unit/ui/screens/test_battle_setup_logic.py | ✓ | 3 | 0 |
| tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py | ✓ | 2 | 0 |
| tests/integration/strategy/test_planetary_facilities.py | ✓ | 7 | 0 |
| tests/unit/strategy/facade/test_strategy_session_facade_contract.py | ✓ | 8 | 0 |
| tests/unit/strategy/engine/test_order_processor_colonize.py | ✓ | 10 | CAT-11 |
| tests/unit/strategy/engine/test_colonize_population.py | ✓ | 8 | 0 |
| tests/integration/save_load/test_roundtrip_research.py | ✓ | 8 | 0 |
| tests/unit/strategy/data/test_fleet_group_kind.py | ✓ | 7 | 0 (regression guard) |
| tests/unit/ai/test_combat_utils.py | ✓ | 24 | 0 |
| tests/integration/strategy/turn_engine/test_resources.py | ✓ | 15 | 0 |
| tests/integration/test_process_planet_action_tick_end_to_end.py | ✓ | 5 | 0 |
| tests/unit/ui/services/image/test_factory.py | ✓ | 6 | 0 |
| tests/unit/strategy/design_repository/test_scan_designs.py | ✓ | 3 | 0 |
| tests/unit/strategy/engine/test_owned_sector_effects_filter.py | ✓ | 1 | 0 |
| tests/unit/ui/screens/battle_setup/test_renderer.py | ✓ | 5 | CAT-8 |
| tests/unit/tools/test_testcoverage_audit.py | ✓ | 5 | 0 |
| tests/unit/strategy/data/test_fleet_order_removal.py | ✓ | 4 | 0 |
| tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py | ✓ | 3 | 0 |
| tests/unit/ui/test_battle_screen_extended.py | ✓ | 1 | 0 |
| tests/unit/strategy/test_ship_consumable_manager.py | ✓ | 24 | 0 |
| tests/unit/simulation/entities/test_ship.py | ✓ | 2 | 0 |
| tests/unit/ui/screens/test_gather_planets_caching.py | ✓ | 8 | 0 |
| tests/unit/strategy/services/test_component_abilities.py | ✓ | 28 | 0 |
| tests/unit/builder/test_multi_selection_logic.py | ✓ | 3 | 0 |
| tests/unit/research/tech_tree/test_cycle_detection.py | ✓ | 20 | 0 |
| tests/integration/strategy/test_deterministic_generation.py | ✓ | 6 | CAT-10 |
| tests/unit/strategy/services/ability_sources/test_fleet.py | ✓ | 16 | 0 |
| tests/unit/ui/test_colors.py | ✓ | 10 | 0 (constants validation) |
| tests/integration/ui/build_queue_screen/conftest.py | ✓ | 0 (fixtures only) | 0 |
| tests/unit/ui/test_modifier_impact_grid.py | ✓ | 17 | CAT-8 |
| tests/integration/save_load/test_roundtrip_ships.py | ✓ | 11 | 0 |
| tests/integration/ui/test_build_queue_drag_drop.py | ✓ | 5 | 0 |
| tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py | ✓ | 2 | CAT-6, CAT-12 |
| tests/unit/strategy/data/test_fleet_id_global.py | ✓ | 11 | 0 |
| tests/integration/test_strategic_abilities.py | ✓ | 17 | 0 |
| tests/unit/test_app_public_api.py | ✓ | 5 | CAT-8, CAT-6 |
| tests/unit/strategy/facade/test_fleet_hierarchy_dto.py | ✓ | 5 | 0 |
| tests/integration/strategy/turn_engine/test_basics.py | ✓ | 5 | 0 |
| tests/integration/colonization/test_explicit_orders.py | ✓ | 5 | 0 |
| tests/unit/ui/screens/test_build_queue_viewmodel.py | ✓ | 24 | 0 |
| tests/integration/strategy/test_warp_orders.py | ✓ | 10 | 0 |
| tests/unit/strategy/conflict_resolution/test_core.py | ✓ | 17 | 0 |
| tests/unit/ui/services/battle_ui_service/test_conversion.py | ✓ | 20 | 0 |
| tests/unit/simulation/battle_controller/test_execution.py | ✓ | 16 | 0 (regression guard) |
| tests/unit/simulation/components/abilities/test_weapons_isolation.py | ✓ | 46 | 0 |
| tests/unit/strategy/data/test_galaxy_entity_registry.py | ✓ | 24 | 0 |
| tests/fixtures/test_scenarios.py | ✓ | 6 | CAT-8 |
| tests/integration/save_load/test_save_edge_cases.py | ✓ | 14 | 0 |
| tests/unit/ui/builder/test_weapons_viewmodel.py | ✓ | 22 | 0 |
| tests/unit/strategy/formulas/test_habitability.py | ✓ | 20 | 0 |
| tests/unit/strategy/data/test_planet_stockpile.py | ✓ | 22 | 0 |
| tests/unit/simulation/battle_controller/test_initialization.py | ✓ | 17 | 0 |
| tests/unit/strategy/turn_engine/test_turn_state_snapshot.py | ✓ | 13 | 0 |
| tests/unit/strategy/conftest.py | ✓ | 0 (fixtures only) | 0 |
| tests/unit/entities/test_ability_interface.py | ✓ | 16 | 0 |
| tests/unit/ui/screens/battle_setup/test_spec_compiler.py | ✓ | 27 | CAT-12 |
| tests/unit/ui/screens/builder/test_modifier_logic_service.py | ✓ | 19 | 0 |

## Context Usage Estimate
- Files assigned: 94
- Files fully read: 94
- Total LOC estimate: ~24,396
- Approximate tokens consumed: ~150,000 input tokens
