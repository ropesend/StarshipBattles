# Verification Report

Source review: `Reviews/results/2026-05-02_204633_test-review/`
Run date: 2026-05-03
Priority tier: **P1** (CAT-4, CAT-5, CAT-6, CAT-7, APC-001, APC-002, APC-003, DUP-001/002/003, HLP-001/002/003/004)

Batch summary: 111 verified, 4 needs-rework, 1 rejected, 3 out-of-scope (P1-tier categories only).

## Verified

| id | category | severity | file | test_name | suggestion |
|----|----------|----------|------|-----------|------------|
| S01-CAT6-001 | CAT-6 | MINOR | `tests/unit/ai/test_ai.py` | test_attack_run_transitions_to_retreat | Mock weapon_range to known value or set ship position relative to calculated threshold. |
| S01-CAT6-002 | CAT-6 | MAJOR | `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` | test_clone_ship_calls_ship_instance_create | Verify the output (cloned ship attributes) rather than asserting on the ShipInstance.create call. |
| S02-CAT4-001 | CAT-4 | MAJOR | `tests/unit/simulation/components/test_modifier_manager.py` | TestModifierManagerStandalone | Remove TestModifierManagerStandalone class. |
| S02-CAT5-001 | CAT-5 | MAJOR | `tests/unit/ui/test_camera.py` | 8 autouse pygame.init() fixtures | Move pygame init to a single module-scoped fixture. |
| S02-CAT5-002 | CAT-5 | MAJOR | `tests/unit/ui/services/test_ship_io.py` | 3 function-scoped Ship fixtures | Rescope to class or module level. |
| S02-CAT6-001 | CAT-6 | MAJOR | `tests/unit/ui/screens/builder/test_modifier_logic_service.py` | TestGetBaseFiringArc | Test through public API (get_initial_value, get_local_min_max) or promote _get_base_firing_arc to a public helper. |
| S02-CAT6-002 | CAT-6 | MAJOR | `tests/unit/simulation/systems/test_battle_engine_init_ship.py` | 4 _initialize_ship tests | Test through engine.start() or engine.start_teams() public APIs. |
| S02-CAT6-003 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_strategy_screen.py` | _make_strategy_screen helper | Reduce to testing public API surface (update, draw, handle_event, handle_resize, handle_click) with observable outcomes. |
| S02-CAT6-004 | CAT-6 | MINOR | `tests/unit/builder/test_multi_selection_logic.py` | setup autouse fixture uses self | Convert to standard fixtures returning values, or use a helper function. |
| S03-CAT4-001 | CAT-4 | MAJOR | `tests/unit/strategy/engine/test_superweapon_command_handlers.py` | Fleet-not-found tests duplicated across files | Parametrize or merge with edge_cases.py. |
| S03-CAT4-002 | CAT-4 | MAJOR | `tests/unit/strategy/engine/test_superweapon_edge_cases.py` | 5 fleet-not-found tests | Parametrize. |
| S03-CAT4-003 | CAT-4 | MAJOR | `tests/unit/strategy/engine/test_superweapon_edge_cases.py` | Order processor error cases overlap | Consolidate at one layer; keep handler-level tests for input validation, processor-level for orchestration. |
| S03-CAT5-001 | CAT-5 | MAJOR | `tests/integration/builder/test_builder_ui_sync.py` | setup_ui autouse fixture | Promote to module scope or split heavy setup from per-test state. |
| S03-CAT5-002 | CAT-5 | MAJOR | `tests/unit/ui/screens/test_queue_selector.py` | build_queue_screen fixture | Rescope to class or module level given it is integration setup. |
| S03-CAT6-001 | CAT-6 | MAJOR | `tests/unit/strategy/engine/test_superweapon_stabilizers.py` | call_args.args assertion | Use call_args_list comprehension that accepts either positional or kwargs, matching the documented intent. |
| S03-CAT6-001b | CAT-6 | MAJOR | `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | 3-5 nested patch blocks per fixture | Extract patch chain into helper and prefer patching at service boundary. |
| S03-CAT7-001 | CAT-7 | MINOR | `tests/unit/services/llm/test_decorators.py` | time.sleep(0.02) | Replace with mocked clock or freezegun. |
| S03-CAT7-002 | CAT-7 | MAJOR | `tests/unit/services/llm/test_persistence.py` | time.sleep(0.05) with both bounds | Replace with mocked clock. |
| S04-CAT4-001 | CAT-4 | MAJOR | `tests/unit/strategy/data/test_construction_queue_paused_persistence.py` | TestPlanetConstructionQueuePausedPersistence + Fleet variant | Parametrize via factory fixtures over Planet/Fleet variants. |
| S04-CAT5-001 | CAT-5 | MAJOR | `tests/unit/core/test_pure_loaders.py` | reset_registry autouse function-scoped | Rescope to module/session. |
| S04-CAT5-002 | CAT-5 | MAJOR | `tests/unit/strategy/generation/test_astrophysics.py` | Identical loader fixtures in 5 classes | Promote to module-scoped fixture. |
| S04-CAT5-003 | CAT-5 | MAJOR | `tests/unit/ui/screens/test_battle_setup_logic.py` | setup_game_data autouse | Module-scope the fixture. |
| S05-CAT4-001 | CAT-4 | MAJOR | `tests/unit/ui/screens/test_warp_hotkey.py` | TestWarpHotkeyModeActivation | Merge mode-activation tests into test_strategy_input_handler_hotkeys.py while retaining unique TestWarpHotkeyViaRealMapper and TestWarpClickDispatching tests. |
| S05-CAT6-001 | CAT-6 | MAJOR | `tests/unit/ui/panels/test_empire_treasury_panel.py` | test_refresh_clears_old_elements | Test through public refresh() observable behavior; do not depend on private collections. |
| S05-CAT6-002 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_build_queue_list_window.py` | _build_list patch | Patch at the boundary of pygame_gui dependencies; or promote _build_list to a public helper if independently testable. |
| S05-CAT6-003 | CAT-6 | MAJOR | `tests/unit/strategy/turn_engine/test_tick_mechanics.py` | calculate_next_hex patch | Inject a fake movement_engine via DI rather than patching internal dispatch. |
| S06-CAT4-001 | CAT-4 | MAJOR | `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` | test_mock_resolver_enables_unit_testing | Refactor to use BattleResolver public API; verify observable engine state. |
| S06-CAT4-002 | CAT-4 | MAJOR | `tests/unit/strategy/data/test_group_policies.py` | 3 hardcoded-policy-list tests | Replace with a single data-driven test loading policies from registry; assert structural invariants. |
| S06-CAT4-003 | CAT-4 | MAJOR | `tests/unit/strategy/engine/test_build_order_command_handler.py` | 2 _handlers private-dict tests | Use registry.get_handler(command_name) or similar public surface. |
| S06-CAT5-001 | CAT-5 | MAJOR | `tests/repro_issues/test_bug_11_dialog_size.py` | Real pygame display autouse | Module-scope the display fixture; keep it as a smoke regression. |
| S06-CAT6-001 | CAT-6 | MAJOR | `tests/unit/research/test_research_scene_di.py` | test_camera_import_is_direct | Remove. Behavioral DI tests already verify Camera is correctly injected. |
| S06-CAT7-001 | CAT-7 | MAJOR | `tests/unit/assets/test_component_derivatives.py` | test_regenerates_when_master_hash_changes | Use os.utime() to set mtime explicitly instead of sleeping. |
| S07-CAT5-001 | CAT-5 | MINOR | `tests/unit/ui/screens/test_race_setup_screen.py` | _make_race_setup_screen heavy bypass-init fixture | Construct the real screen with mocked pygame_gui or factor mock setup into a class-scoped fixture. |
| S08-CAT4-001 | CAT-4 | MAJOR | `tests/unit/strategy/data/test_event_validation.py` | 5 missing-key validation tests | Parametrize as @pytest.mark.parametrize('field', [...]). |
| S08-CAT4-002 | CAT-4 | MAJOR | `tests/unit/strategy/data/test_battle_state_validation.py` | TestComponentStateValidation 6 deletion tests | Parametrize. |
| S08-CAT5-001 | CAT-5 | MAJOR | `tests/unit/simulation/components/test_component_resource_manager.py` | 3 function-scoped fixtures | Rescope to class or module level. |
| S08-CAT5-002 | CAT-5 | MAJOR | `tests/unit/strategy/engine/test_resupply_engine.py` | 10 helper functions | Consolidate into shared fixtures in tests/fixtures/. |
| S08-CAT5-003 | CAT-5 | MAJOR | `tests/unit/ui/screens/test_fleet_report_filters.py` | make_mock_ship 63-line helper | Extract to shared fixture; use kwargs overrides. |
| S08-CAT6-001 | CAT-6 | MAJOR | `tests/unit/simulation/projectile/test_ccd.py` | MagicMock projectiles with 15 attrs | Extract _make_projectile helper; use real Projectile or sparse spec. |
| S08-CAT6-002 | CAT-6 | MAJOR | `tests/unit/strategy/fleet_movement_engine/test_basics.py` | test_recalculates_path_if_destination_changed | Inject path-finder via DI and pass a fake; do not patch internal modules. |
| S08-CAT6-003 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_new_game_setup_extended.py` | _make_screen bypass-init | Construct via real __init__ with mocked pygame_gui dependencies. |
| S08-CAT6-004 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_strategy_modal_window.py` | _make_modal_window | Use a real headless pygame_gui session for the test. |
| S08-CAT7-001 | CAT-7 | MAJOR | `tests/unit/strategy/data/test_auto_save.py` | time.sleep(0.01) | Use os.utime() to set mtime explicitly. |
| S08-CAT7-002 | CAT-7 | MAJOR | `tests/unit/services/llm/test_race_description_llm_controller.py` | 4 time.sleep(0.02) calls | Switch to event-based synchronization or mocked clock. |
| S08-CAT7-003 | CAT-7 | MAJOR | `tests/unit/services/llm/test_race_description_llm_controller.py` | _BlockingProvider.complete polling | Use Event/Condition or mocked time for blocking simulation. |
| S09-CAT4-001 | CAT-4 | MAJOR | `tests/unit/simulation/entities/test_ship.py` | Derelict status duplication | Keep test_ship.py version (entity-level location) and remove duplicated coverage from test_combat.py. |
| S09-CAT4-002 | CAT-4 | MAJOR | `tests/unit/modifiers/test_seeker_weapon_bindings.py` | Recalculate duplication | Remove the 4 individual tests; rely on consolidated test_weapons_isolation coverage. |
| S09-CAT4-003 | CAT-4 | MAJOR | `tests/unit/simulation/test_battle_runner_di.py` | _make_ship_spec / _make_team duplicates | Move helpers to tests/unit/simulation/conftest.py with class scope. |
| S09-CAT4-004 | CAT-4 | MAJOR | `tests/unit/strategy/fleet/test_space_yard.py` | make_ship_with_yard duplicate | Move to module-level fixture and reference from both classes. |
| S09-CAT5-001 | CAT-5 | MAJOR | `tests/unit/ui/screens/test_save_selection.py` | 3 identical setup_tmpdir fixtures | Promote to a module-level fixture or conftest helper. |
| S09-CAT6-001 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_save_selection.py` | test_buttons_enable_after_selection | Drive the selection through real pygame_gui events; assert observable button state. |
| S09-CAT6-002 | CAT-6 | MAJOR | `tests/unit/research/research_scene/test_reset_state.py` | Complex mock panel wiring | Test through observable post-reset state of a real panel; remove call-order assertions. |
| S09-CAT6-003 | CAT-6 | MAJOR | `tests/unit/modifiers/test_seeker_weapon_bindings.py` | Inline MockComponent class duplication | Replace each with MagicMock(stats={...}); also addresses CAT-4 overlap. |
| S09-CAT7-001 | CAT-7 | MAJOR | `tests/unit/ui/screens/test_save_selection.py` | time.sleep(0.1) | Use os.utime() or seeded clock to control timestamps deterministically. |
| S10-CAT4-001 | CAT-4 | MAJOR | `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` | TestProjectPathAsDicts | Keep both files; minor overlap acceptable. |
| S10-CAT5-001 | CAT-5 | MAJOR | `tests/unit/ui/panels/test_modifier_editor_panel.py` | modifier_panel function-scoped fixture | Rescope to class scope or merge into one parametrized test. |
| S10-CAT5-002 | CAT-5 | MAJOR | `tests/unit/simulation/services/test_modifier_service.py` | full_registry function-scoped | Rescope to class scope after verifying no test mutates state. |
| S10-CAT5-003 | CAT-5 | MAJOR | `tests/unit/strategy/facade/test_strategy_session_facade.py` | 7 _make_mock_* helpers across 4 classes | Create shared factories with kwargs overrides in conftest.py. |
| S10-CAT6-002 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_planet_list_window.py` | PlanetReportPanel deep mocking | Keep per project conventions; revisit when bypass-init pattern is consolidated. |
| S11-CAT4-001 | CAT-4 | MAJOR | `tests/unit/ui/screens/test_battle_panels_extended.py` | 3 copy-pasted setup_mocks | Extract a single shared module-scoped fixture/helper. |
| S11-CAT4-002 | CAT-4 | MAJOR | `tests/unit/modifiers/test_beam_weapon_bindings.py` | Duplicates test_weapon_ability_bindings.py | Merge into test_weapon_ability_bindings.py as additional parametrized cases or a child class. |
| S11-CAT5-002 | CAT-5 | MINOR | `tests/unit/simulation/combat/test_exit_policy.py` | BattleEngine recreated per test | Promote boundaries to module-level constants; share fixtures. |
| S11-CAT6-001 | CAT-6 | MAJOR | `tests/unit/ui/components/table/test_virtual_table.py` | 5x @patch decorator on every test | Move shared patches to a class-level fixture or autouse module-scoped fixture. |
| S11-CAT6-002 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_battle_panels_extended.py` | setup_mocks patches sys.modules | Use patch.object on specific pygame paths instead of replacing the module. |
| S11-CAT6-003 | CAT-6 | MAJOR | `tests/unit/simulation/services/test_validation_service.py` | Mock-delegate tests | Replace 4 delegation tests with behavioral tests that exercise the real validator chain. |
| S11-CAT6-004 | CAT-6 | MAJOR | `tests/integration/builder/test_builder_drag_drop_real.py` | Patches private _create_ui | Use real headless _create_ui or refactor to inject UI via DI. |
| S11-CAT7-001 | CAT-7 | MINOR | `tests/integration/data/test_pipeline_unification.py` | Data-driven tests | Acceptable as data-contract tests; document the coupling. |
| S12-CAT5-001 | CAT-5 | MAJOR | `tests/unit/ui/screens/test_build_queue_screen.py` | _make_build_queue_screen 88-line helper | Convert to a pytest fixture with scope='class'; create a thin per-test override path. |
| S12-CAT5-002 | CAT-5 | MINOR | `tests/unit/builder/test_workshop_viewmodel.py` | function-scoped data fixtures | Promote mock_registries to module/class scope or memoize the disk load. |
| S12-CAT6-001 | CAT-6 | MAJOR | `tests/unit/ui/screens/test_sub_window_hotkeys.py` | Constructor bypass for window classes | Use real construction with mocked pygame_gui; or refactor windows so hotkey logic lives in a separately testable module. |
| S12-CAT7-001 | CAT-7 | MINOR | `tests/unit/services/llm/test_background.py` | time.sleep polling loops | Replace polling with Event-based synchronization where feasible. |
| APC-001-F01 | APC-001 | CRITICAL | `tests/unit/ui/test_race_portrait_gallery.py` |  | Construct via real __init__ with mocked pygame_gui dependencies, or migrate to integration tests with headless pygame_gui. |
| APC-001-F02 | APC-001 | MAJOR | `tests/unit/ui/test_race_description_panel.py` |  | Construct via real __init__ with mocked pygame_gui dependencies. |
| APC-001-F03 | APC-001 | CRITICAL | `tests/unit/ui/panels/test_race_identity_panel.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F04 | APC-001 | CRITICAL | `tests/unit/ui/panels/test_component_modifier_grid_panel.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F05 | APC-001 | CRITICAL | `tests/unit/ui/test_race_flag_gallery.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F06 | APC-001 | CRITICAL | `tests/unit/ui/screens/test_fleet_report_window.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F07 | APC-001 | MAJOR | `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` |  | Patch at boundary; switch to public-API tests where possible. |
| APC-001-F08 | APC-001 | CRITICAL | `tests/unit/ui/panels/test_system_tree_panel.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F09 | APC-001 | CRITICAL | `tests/unit/ui/panels/test_design_report_panel.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F10 | APC-001 | CRITICAL | `tests/unit/ui/screens/test_workshop_screen.py` |  | Construct via real __init__ with mocked pygame_gui or migrate to integration tests. |
| APC-001-F11 | APC-001 | MINOR | `tests/unit/ui/screens/test_race_setup_screen.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F12 | APC-001 | MAJOR | `tests/unit/ui/screens/test_new_game_setup_extended.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F13 | APC-001 | CRITICAL | `tests/unit/ui/test_race_theme_gallery.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F14 | APC-001 | CRITICAL | `tests/unit/ui/test_race_summary_panel.py` |  | Construct via real __init__ with mocked pygame_gui. |
| APC-001-F15 | APC-001 | CRITICAL | `tests/unit/ui/screens/test_build_queue_screen.py` |  | Migrate to integration tests with headless pygame_gui. |
| APC-001-F16 | APC-001 | MAJOR | `tests/unit/ui/screens/test_sub_window_hotkeys.py` |  | Use real construction with mocked pygame_gui or refactor hotkey logic into a separately testable module. |
| APC-002-F01 | APC-002 | MAJOR | `tests/unit/modifiers/test_seeker_multi_ability.py` |  | Replace with behavioral test. |
| APC-002-F02 | APC-002 | MINOR | `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` |  | Replace with behavioral default-construction test. |
| APC-002-F03 | APC-002 | CRITICAL | `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` |  | Replace with behavioral tests. |
| APC-002-F04 | APC-002 | CRITICAL | `tests/integration/test_app_integration.py` |  | Replace with behavioral tests. |
| APC-002-F05 | APC-002 | CRITICAL | `tests/unit/ui/screens/battle_setup/test_view_model.py` |  | Move to pre-commit lint. |
| APC-002-F06 | APC-002 | MAJOR | `tests/unit/research/test_research_scene_di.py` |  | Remove; behavioral DI tests already cover this. |
| APC-002-F07 | APC-002 | MAJOR | `tests/unit/ui/screens/battle_setup/test_renderer.py` |  | Replace with behavioral test calling _rebuild_ui. |
| APC-002-F08 | APC-002 | MAJOR | `tests/unit/ui/screens/test_planet_selection_window.py` |  | Replace with construction tests. |
| APC-002-F09 | APC-002 | MINOR | `tests/unit/ui/test_new_game_setup.py` |  | Replace with behavioral default test. |
| APC-002-F10 | APC-002 | MAJOR | `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` |  | Replace with behavioral assertion using real registrar. |
| APC-003-F01 | APC-003 | MAJOR | `tests/unit/ui/screens/builder/test_modifier_logic_service.py` |  | Test through public API or promote helper to public. |
| APC-003-F02 | APC-003 | MAJOR | `tests/unit/simulation/systems/test_battle_engine_init_ship.py` |  | Test through engine.start() public API. |
| APC-003-F03 | APC-003 | MAJOR | `tests/unit/ui/screens/test_build_queue_list_window.py` |  | Patch at boundary; promote helper to public if independently testable. |
| APC-003-F04 | APC-003 | MAJOR | `tests/unit/strategy/turn_engine/test_tick_mechanics.py` |  | Inject fake movement engine via DI. |
| APC-003-F05 | APC-003 | MAJOR | `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` |  | Test through public BattleResolver API. |
| APC-003-F06 | APC-003 | MAJOR | `tests/unit/strategy/engine/test_build_order_command_handler.py` |  | Use registry.get_handler() public API. |
| APC-003-F07 | APC-003 | MAJOR | `tests/unit/strategy/fleet_movement_engine/test_basics.py` |  | Inject path-finder via DI. |
| APC-003-F08 | APC-003 | MAJOR | `tests/integration/builder/test_builder_drag_drop_real.py` |  | Use real headless _create_ui or refactor to inject UI via DI. |
| DUP-002 | DUP-002 | MAJOR | `tests/unit/strategy/engine/test_superweapon_command_handlers.py + tests/unit/strategy/test_command_handlers.py` |  | Extract a parametrized test: @pytest.mark.parametrize('handler_cls,cmd_kwargs', [...]). |
| DUP-003 | DUP-003 | MINOR | `tests/unit/strategy/data/test_fleet_cargo_resources.py + tests/unit/strategy/engine/test_resupply_engine.py` |  | Extract a shared make_cargo_mock_ship(cargo_capacity, cargo_contents) to tests/fixtures/. |
| HLP-001 | HLP-001 | MAJOR | `tests/unit/ui/screens/test_fleet_report_filters.py + tests/unit/strategy/data/test_fleet_cargo_resources.py + tests/unit/strategy/engine/test_resupply_engine.py + tests/unit/strategy/facade/test_strategy_session_facade.py` |  | Create shared fixtures in tests/fixtures/test_entities.py with kwargs overrides. |
| HLP-002 | HLP-002 | MAJOR | `tests/unit/simulation/test_battle_runner.py + tests/unit/simulation/test_battle_runner_di.py` |  | Move helpers to tests/unit/simulation/conftest.py with class scope. |
| HLP-003 | HLP-003 | MINOR | `tests/unit/strategy/engine/test_planetary_yard_requirement.py + tests/unit/strategy/production_engine/test_tick_consumption.py + tests/unit/strategy/fleet/test_space_yard.py` |  | Move to a shared fixture in tests/fixtures/ or a common conftest. |
| HLP-004 | HLP-004 | MINOR | `tests/unit/strategy/validation/test_colonize_validator.py + tests/unit/strategy/engine/test_resupply_engine.py + tests/unit/strategy/test_planet_specific_colonization.py` |  | Create shared make_mock_planet(**overrides) factory in tests/fixtures/. |

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S05-CAT5-001 | Module-scope the fixtures (claim: 13 test methods). | Rescope fixtures to module after verifying no test mutates shared mock state. | Adjusted method count from 12 to 17. |
| S08-CAT4-003 | Parametrize the 5 duplicate tests. | KEEP — distinct edge cases. Consider downgrading to informational note or moving to CAT-10 for parametrize discussion. | Verifier flagged tests as 5 distinct edge cases, not duplicates. |
| S10-CAT6-001 | Test through OrderProcessor.execute_action_order public boundary. | Refactor to use OrderProcessor public boundary OR document clearly why ActionExecutionEngine delegation is the correct entry point. | Verifier suggested either refactor or doc the design intent. |
| DUP-001 | Merge SHARD_07 DI validation tests into SHARD_03 test classes as additional methods or single parametrized class. | Create a parameterized fixture factory that supplies both contract variants (execution and DI) rather than merging classes; DI vs execution are different concerns. | Adjusted suggestion: don't merge classes; use parameterized fixture factory. |

## Rejected

| id | original claim | contrary evidence (file:line) | rationale |
|----|----------------|-------------------------------|-----------|
| S11-CAT5-R01 | Phase 1 claimed fixtures are 'function-scoped helpers inside a single test class'; verifier confirmed they are already module-level fixtures (lines 331-370). Recommendation already implemented. | `tests/unit/strategy/test_damage_calculator.py`:331-370 | Fixtures are already module-level (lines 331-370); recommendation already implemented. |

## Out of Scope

| id | claim | reason |
|----|-------|--------|
| S08-CAT4-OOS01 | `tests/unit/simulation/systems/test_battle_engine_end_conditions.py` - Integration smoke verifying conditions work in engine context. | intentional_integration_smoke |
| S11-CAT5-OOS01 | `tests/unit/simulation/components/test_component_decoupling.py` - Triple file I/O for components.json. Performance concern, not correctness. | legitimate_distinct_or_integration |
| APC-002-OOS01 | `tests/unit/ui/screens/test_strategy_renderer_public_api.py` - Same as S05 OOS — intentional contract pin per PROJ-309. | ast_guard_intentional |
