# Shard 13 — Test Audit Report

## Summary
- Shard: 13 | Files assigned: 94 | Files actually read: 94 | Total findings: 26 | Critical: 2 | Major: 11 | Minor: 13

## Findings

### tests/unit/ui/panels/test_empire_treasury_panel.py
#### CAT-8: 4-patch-decorator repeated on 16 test methods [MINOR]
- **Location**: test_empire_treasury_panel.py:238-631 | **Issue**: Every test method (16 total) uses 4 identical @patch decorators for UI widget mocking. Setup dominates >50%25 of each test. | **Suggestion**: Extract the 4 patches into a shared context manager. | **LOC affected**: ~400

#### CAT-10: TestValueFormatting - 4 tests with identical structure [MINOR]
- **Location**: test_empire_treasury_panel.py:235-284 | **Issue**: test_format_zero, test_format_small_integers, test_format_large_integers, test_format_floats all construct panel same way, call _format_value, assert string. | **Suggestion**: Parametrize with (value, expected). | **LOC affected**: ~50

#### CAT-5: sample_snapshot fixture function-scoped for read-only usage [MAJOR]
- **Location**: test_empire_treasury_panel.py:92-99 | **Issue**: sample_snapshot is function-scoped. Only 4 tests mutate it; 12 read-only. Other fixtures already module-scoped. | **Suggestion**: Split into r/w and read-only variant. | **LOC affected**: ~93
### tests/unit/ui/test_race_summary_panel.py
#### CAT-3: TestCallbackIntegration - empty class [CRITICAL]
- **Location**: test_race_summary_panel.py:321-323 | **Issue**: Class has docstring but zero test methods. Dead code - no pytest functions found. | **Suggestion**: Delete the empty class or add test methods. | **LOC affected**: 3

#### CAT-8: _refresh_with_mocked_uilabel helper complexity [MINOR]
- **Location**: test_race_summary_panel.py:363-414 | **Issue**: 4+ nested with patch.object() blocks plus 12+ manual attribute wirings. | **Suggestion**: Extract into fixture with yield. | **LOC affected**: ~150

#### CAT-6: _refresh_with_mocked_uilabel uses __new__ to bypass init [MAJOR]
- **Location**: test_race_summary_panel.py:391 | **Issue**: Uses RaceSummaryPanel.__new__ and wires 14+ private attrs - coupled to internal implementation. | **Suggestion**: Use bypass_init from tests.fixtures.ui_widget_factory. | **LOC affected**: 30

#### CAT-5: mock_race_config fixtures function-scoped but read-only [MAJOR]
- **Location**: test_race_summary_panel.py:43-96 | **Issue**: mock_race_config/_empty/_full create real RaceConfig objects on every test. No mutation. | **Suggestion**: Scope to module. | **LOC affected**: ~60
### tests/unit/ui/screens/test_strategy_fleet_command_router.py
#### CAT-6: String-based class-name check [MAJOR]
- **Location**: test_strategy_fleet_command_router.py:430 | **Issue**: assert type(command).__name__ == expected_cmd_class_name uses string comparison instead of isinstance(). | **Suggestion**: Use isinstance(command, ActivatePlanetAbilityCommand). | **LOC affected**: 2

#### CAT-12: if/else branch in test body [MINOR]
- **Location**: test_strategy_fleet_command_router.py:76-89 | **Issue**: test_fleet_action_enters_target_mode_when_fleet_selected has if/else based on action type. | **Suggestion**: Split into two separate tests. | **LOC affected**: 14

### tests/unit/simulation/combat/test_weapon_firing_system.py
#### CAT-6: Inspects private call_args of internal subsystem [MAJOR]
- **Location**: test_weapon_firing_system.py:804 | **Issue**: Asserts on targeting.find_valid_target.call_args.args[2] - private internal args. | **Suggestion**: Test observable target selection outcome instead. | **LOC affected**: 5

#### CAT-9: Repeated ship/target mock setup across 15+ tests [MINOR]
- **Location**: test_weapon_firing_system.py:throughout | **Issue**: ~15 tests construct identical MagicMock ship with same 10 attrs. | **Suggestion**: Extract _make_basic_ship() factory. | **LOC affected**: ~300

### tests/unit/simulation/combat/test_targeting_system.py
#### CAT-6: Inspects internal call args [MAJOR]
- **Location**: test_targeting_system.py:1141 | **Issue**: Asserts on targeting.find_valid_target.call_args[0][2]. | **Suggestion**: Test target selection outcome instead. | **LOC affected**: 4

#### CAT-9: Repeated mock construction across 30+ tests [MINOR]
- **Location**: test_targeting_system.py:throughout | **Issue**: Common mock patterns repeated across ~30 tests. | **Suggestion**: Extract factory helpers. | **LOC affected**: ~400
### tests/unit/strategy/engine/test_superweapon_command_handlers.py
#### CAT-4: Duplicate validation-pass test [MAJOR]
- **Location**: test_superweapon_command_handlers.py:340-353 | **Issue**: Parametrized test at line 139 covers 5 handlers; TestSelfDestructCommandHandler duplicates same assertion. | **Suggestion**: Add SelfDestruct to parametrized list. | **LOC affected**: 14

#### CAT-10: 5 Direct handler order-type tests [MINOR]
- **Location**: test_superweapon_command_handlers.py:163-331 | **Issue**: 5 handlers each have identical test_execute_adds_correct_order_type structure. | **Suggestion**: Parametrize. | **LOC affected**: ~80

### tests/unit/strategy/validation/test_superweapon_validator.py
#### CAT-10: 5 test classes with identical patterns [MINOR]
- **Location**: test_superweapon_validator.py:228-651 | **Issue**: Stellerate/OpenWarp/CloseWarp/CreateDysonSphere classes each repeat valid/missing-ability/bad-location pattern. | **Suggestion**: Systematic parametrize. | **LOC affected**: ~200

### tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py
#### CAT-6: Brittle call_args index access [MAJOR]
- **Location**: test_cargo_quick_dialog_controller_widget_purity.py:57 | **Issue**: Reads facade.handle_command.call_args[0][0] via MagicMock call tracking. | **Suggestion**: Use assert_called_once_with(command). | **LOC affected**: 2

### tests/unit/ui/screens/test_strategy_build_queue_manager.py
#### CAT-4: Duplicate on_active_player_changed tests [MAJOR]
- **Location**: test_strategy_build_queue_manager.py:469-511 and 591-645 | **Issue**: Two tests verify same empire-flip calls on_active_player_changed. | **Suggestion**: Merge or remove duplicate. | **LOC affected**: ~80

### tests/unit/modifiers/test_modifier_loader_v2.py
#### CAT-4: Duplicate hardened_mount formula test [MAJOR]
- **Location**: test_modifier_loader_v2.py:129-158 and 65-87 | **Issue**: Both test same hardened_mount formula (hp=param^2) with param=2.0. | **Suggestion**: Consolidate. | **LOC affected**: 30
### tests/unit/strategy/combat/test_post_battle_hook_builder.py
#### CAT-1: Trivial pass test [CRITICAL]
- **Location**: test_post_battle_hook_builder.py:37-54 | **Issue**: test_build_hook_threads_mine_groups_and_engine_ref only asserts callable(hook). Cannot fail if imports succeed. | **Suggestion**: Add behavioral assertions verifying the hook. | **LOC affected**: 18

### tests/unit/ai/test_carrier_controller.py
#### CAT-6: Writes to private _mass_budget_by_ability dict [MAJOR]
- **Location**: test_carrier_controller.py:285, 340 | **Issue**: Tests write ctrl._mass_budget_by_ability[TacticalFighterLaunch] directly. | **Suggestion**: Expose public set_mass_budget() method. | **LOC affected**: 4

### tests/unit/strategy/data/test_order_types_characterization.py
#### CAT-6: Monkeypatches production Planet/Fleet classes [MAJOR]
- **Location**: test_order_types_characterization.py:49-57 | **Issue**: patch_domain_classes swaps real classes with stubs at module level. | **Suggestion**: Use Protocol-based stubs or DI. | **LOC affected**: 10

### tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py
#### CAT-10: 5 stabilizer-cancellation tests identical pattern [MINOR]
- **Location**: test_superweapon_order_processor_gaps.py:118-272 | **Issue**: implode/stellerate/open_warp/close_warp/dyson each ~90% identical. | **Suggestion**: Parametrize into one test. | **LOC affected**: ~150

### tests/unit/tools/test_codex_project_config.py
#### CAT-1: Config-file assertion, not game code test [CRITICAL]
- **Location**: test_codex_project_config.py:17-22 | **Issue**: Reads .codex/config.toml and asserts model/context_window. Fails if .codex/ missing. Not a game code test. | **Suggestion**: Skip if file missing or move to CI-only check. | **LOC affected**: 6

### tests/unit/ui/screens/test_transfer_dialog.py + test_cargo_quick_dialog.py
#### CAT-9: Real pygame_gui.UIManager per function [MINOR]
- **Location**: test_transfer_dialog.py:22-23, test_cargo_quick_dialog.py:22-23 | **Issue**: mock_manager creates real UIManager per test function - expensive read-only allocation. | **Suggestion**: Scope to class. | **LOC affected**: 4

### tests/unit/ui/effects/test_hit_effects.py
#### CAT-10: Three early-return tests identical pattern [MINOR]
- **Location**: test_hit_effects.py:109-200 | **Issue**: alpha/shield/armor guard tests follow same pattern. | **Suggestion**: Parametrize (naming documents branches - valuable to keep) | **LOC affected**: ~90

### tests/unit/ui/screens/test_list_data_source_base.py
#### CAT-9: One test covers 4 cell-value paths [MINOR]
- **Location**: test_list_data_source_base.py:57-64 | **Issue**: Single test verifies func/attr/nested-attr/format paths. | **Suggestion**: Split per resolution strategy. | **LOC affected**: 8

### tests/unit/strategy/empire/test_empire_validation.py
#### CAT-10: Three missing-key tests identical [MINOR]
- **Location**: test_empire_validation.py:41-72 | **Issue**: test_missing_id/_name/_color identical bodies. | **Suggestion**: Parametrize on missing_key. | **LOC affected**: ~30

### tests/unit/strategy/engine/test_base_command_handler.py
#### CAT-10: Two resolve error tests identical [MINOR]
- **Location**: test_base_command_handler.py:18-43 | **Issue**: test_not_found and test_wrong_owner same pattern. | **Suggestion**: Parametrize. | **LOC affected**: ~25

---

## File Coverage Verification
All 94 files listed in SHARD_CONFIG.json shard 13 were read completely. See config for full list.

## Context Usage Estimate
~350K tokens consumed across 94 file reads (~24,213 LOC).
