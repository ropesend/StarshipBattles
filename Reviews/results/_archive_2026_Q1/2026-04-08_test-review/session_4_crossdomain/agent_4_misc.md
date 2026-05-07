# Test Review Report: Misc Infrastructure

## Scope
- Source files reviewed:
  - `tests/infrastructure/deep_compare.py` (193 LOC) -- test utility
  - `tests/infrastructure/state_snapshot.py` (144 LOC) -- test utility
  - `game/core/profiling.py` -- source for profiler tests (98.8% coverage per coverage.json)
  - `game/ui/services/screenshot_manager.py` -- source for screenshot tests (100% coverage)
  - `game/ui/screens/builder/modifier_logic.py` -- source for modifier snap logic
- Test files reviewed:
  - `tests/unit/performance/reproduce_scaling.py` (41 LOC)
  - `tests/unit/performance/test_profiler_perf.py` (181 LOC)
  - `tests/unit/infrastructure/test_deep_compare.py` (265 LOC)
  - `tests/unit/infrastructure/test_state_snapshot.py` (49 LOC)
  - `tests/unit/regressions/test_bug_regressions_2026_01.py` (114 LOC)
  - `tests/unit/regressions/test_regressions.py` (97 LOC)
  - `tests/unit/regressions/test_warnings.py` (116 LOC)
  - `tests/repro_issues/test_bug_01_crew_delay.py` (113 LOC)
  - `tests/repro_issues/test_bug_02_seeker.py` (37 LOC)
  - `tests/repro_issues/test_bug_03_validation.py` (104 LOC)
  - `tests/repro_issues/test_bug_04_display.py` (101 LOC)
  - `tests/repro_issues/test_bug_05_deep_repro.py` (157 LOC)
  - `tests/repro_issues/test_bug_05_logistics.py` (108 LOC)
  - `tests/repro_issues/test_bug_05_rejected_fix.py` (91 LOC)
  - `tests/repro_issues/test_bug_06_combat_propulsion.py` (147 LOC)
  - `tests/repro_issues/test_bug_07_crash.py` (59 LOC)
  - `tests/repro_issues/test_bug_08_fuel_validation.py` (59 LOC)
  - `tests/repro_issues/test_bug_09_endurance.py` (80 LOC)
  - `tests/repro_issues/test_bug_09_hull_in_palette.py` (56 LOC)
  - `tests/repro_issues/test_bug_10_logistics_update.py` (112 LOC)
  - `tests/repro_issues/test_bug_11_dialog_size.py` (68 LOC)
  - `tests/repro_issues/test_bug_11_hull_update.py` (80 LOC)
  - `tests/repro_issues/test_bug_12_energy_gen.py` (110 LOC)
  - `tests/repro_issues/test_bug_12_hull_layer_addition.py` (52 LOC)
  - `tests/repro_issues/test_bug_13_clear_removes_hull.py` (125 LOC)
  - `tests/repro_issues/test_bug_13_weapons_report.py` (136 LOC)
  - `tests/repro_issues/test_bug_14_multi_planet_offset.py` (337 LOC)
  - `tests/repro_issues/test_bug_15_screenshot_strategy.py` (364 LOC)
  - `tests/repro_issues/test_bug_16_raw_data_button.py` (64 LOC)
  - `tests/repro_issues/test_bug_17_drag_preview.py` (62 LOC)
  - `tests/repro_issues/test_bug_27_ordertype.py` (118 LOC)
  - `tests/repro_issues/test_crash_planet_list.py` (43 LOC)
  - `tests/projects/test_extract_phase.py` (430 LOC)
  - `tests/unit/test_builder_refactor.py` (36 LOC)
  - `tests/unit/test_modifier_logic.py` (103 LOC)
  - `tests/unit/_verify_builder_imports.py` (20 LOC)
- Coverage data referenced: yes -- total project 71.9% (36045/50128 lines); `game/core/profiling.py` 98.8%; `game/ui/services/screenshot_manager.py` 100%

## Summary
- Test files reviewed: 36
- Source files reviewed: 5 (test infrastructure utilities + key source files)
- Tests flagged for removal: 21 (estimated LOC: 2399)
- Tests flagged as happy-path-only: 3
- Source files with inadequate coverage: 0 (covered sources have excellent coverage)

## A. Tests Recommended for Removal

### A1. Repro Issues -- Now Covered by Proper Unit Tests

- **File:** `tests/repro_issues/test_bug_01_crew_delay.py`
- **Test(s):** `TestBug01CrewDelay.test_crew_stat_update_on_modifier_change`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/components/abilities/test_crew_abilities.py` and `tests/unit/modifiers/test_crew_required_mass_scaling.py`
- **Confidence:** HIGH
- **Evidence:** The bug (crew_req_mult not updating after modifier change) is now tested by dedicated crew ability tests and modifier scaling tests in the unit suite. The repro test manually patches modifiers into `comp.modifiers` (lines 93-94) which is fragile and non-standard.
- **Estimated LOC saved:** 113

- **File:** `tests/repro_issues/test_bug_02_seeker.py`
- **Test(s):** `test_seeker_range_calculation`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/components/abilities/test_weapons_integration.py` and `tests/unit/entities/test_ship_stat_querier.py`
- **Confidence:** HIGH
- **Evidence:** The seeker range calculation (`speed * endurance * 0.8`) is tested in dedicated weapon ability tests. This 37-line repro uses a `MockComponent` (line 6-9) that bypasses the real ability system, making it both redundant and unreliable.
- **Estimated LOC saved:** 37

- **File:** `tests/repro_issues/test_bug_03_validation.py`
- **Test(s):** `TestBug03Validation.test_fuel_warning_persistence_with_wrong_resource`, `test_ammo_warning_persistence_with_wrong_resource`
- **Reason:** DUPLICATE_OF:`tests/unit/regressions/test_warnings.py` and `tests/unit/simulation/validation/test_ship_validator_rules.py`
- **Confidence:** HIGH
- **Evidence:** The exact same tests (wrong resource type not resolving fuel/ammo warning) exist in `test_warnings.py` lines 48-93 (fuel) and 72-93 (ammo), and in `test_ship_validator_rules.py` which tests `ResourceDependencyRule` directly. The repro file is fully redundant.
- **Estimated LOC saved:** 104

- **File:** `tests/repro_issues/test_bug_05_logistics.py`
- **Test(s):** `test_missing_logistics_details`
- **Reason:** DUPLICATE_OF:`tests/unit/ui/test_ui_stats.py` (tests `get_logistics_rows`)
- **Confidence:** HIGH
- **Evidence:** `test_ui_stats.py` tests `get_logistics_rows` comprehensively. This repro (108 LOC) manually injects ability instances (lines 38-67) rather than using the proper component creation path, making it both fragile and redundant.
- **Estimated LOC saved:** 108

- **File:** `tests/repro_issues/test_bug_05_rejected_fix.py`
- **Test(s):** `test_usage_only_visibility`, `test_max_usage_calculation`
- **Reason:** DUPLICATE_OF:`tests/unit/ui/test_ui_stats.py` and `tests/repro_issues/test_bug_05_logistics.py` (itself recommended for removal)
- **Confidence:** HIGH
- **Evidence:** Both functions test logistics row generation for energy resources. The `test_ui_stats.py` file covers the same `get_logistics_rows` logic. This file also manually injects `ability_instances` (line 29, 56-58) bypassing proper construction.
- **Estimated LOC saved:** 91

- **File:** `tests/repro_issues/test_bug_05_deep_repro.py`
- **Test(s):** `test_shield_regen_consumption`, `test_laser_cannon_consumption`
- **Reason:** DUPLICATE_OF:`tests/unit/ui/test_ui_stats.py` (logistics rows) and `tests/unit/simulation/components/abilities/test_resource_consumption.py`
- **Confidence:** HIGH
- **Evidence:** Tests energy consumption calculation for shield regen and laser cannon. These behaviors are covered by resource consumption ability tests and UI stats tests. The repro directly appends to `ship.layers[].components` (line 71) bypassing the standard `add_component` path.
- **Estimated LOC saved:** 157

- **File:** `tests/repro_issues/test_bug_06_combat_propulsion.py`
- **Test(s):** `TestBug06CombatPropulsion.test_combat_propulsion_validation`, `test_thrust_value_is_correct`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/validation/test_ship_validator_rules.py`, `tests/unit/modifiers/test_propulsion_ability_bindings.py`, and many other CombatPropulsion test files (20+ files reference CombatPropulsion)
- **Confidence:** HIGH
- **Evidence:** CombatPropulsion detection/validation is extensively tested across the validator, modifier binding, physics, and stats calculator test suites. The repro uses manual assembly pattern (line 80-82) that no longer matches production code paths.
- **Estimated LOC saved:** 147

- **File:** `tests/repro_issues/test_bug_07_crash.py`
- **Test(s):** `TestBug07Crash.test_crash_adding_component_with_tohit_modifier`
- **Reason:** DUPLICATE_OF:`tests/unit/entities/test_ability_interface.py` and `tests/unit/entities/test_ship_stat_querier.py`
- **Confidence:** HIGH
- **Evidence:** The bug was `ToHitAttackModifier` missing `.value` when calling `get_total_sensor_score()`. The sensor score and ToHitAttackModifier are now tested in `test_ship_stat_querier.py` and `test_ability_interface.py`. The repro uses a try/except pytest.fail pattern (line 57-59) which is an anti-pattern.
- **Estimated LOC saved:** 59

- **File:** `tests/repro_issues/test_bug_08_fuel_validation.py`
- **Test(s):** `TestBug08FuelValidation.test_class_requirements_fuel_storage_failure`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/validation/test_ship_validator_rules.py` and `tests/unit/regressions/test_bug_regressions_2026_01.py`
- **Confidence:** HIGH
- **Evidence:** Tests that fuel tank provides ResourceStorage ability for `fuel`. This is tested in `test_ship_validator_rules.py` (ResourceDependencyRule tests) and `test_bug_regressions_2026_01.py` line 62-91 (bug3 validation). The comment at line 33 notes the original `requirements` field has been removed.
- **Estimated LOC saved:** 59

- **File:** `tests/repro_issues/test_bug_09_endurance.py`
- **Test(s):** `TestBug09Endurance.test_fuel_endurance_infinite`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/entities/test_combat_endurance.py` and `tests/unit/ui/test_ui_stats.py`
- **Confidence:** HIGH
- **Evidence:** Fuel endurance calculation is now tested in `test_combat_endurance.py` (9 files reference fuel_endurance). The repro also tests the `fmt_time` UI function which is covered in `test_ui_stats.py`. The test loads full production data (line 23-24) making it slow and fragile.
- **Estimated LOC saved:** 80

- **File:** `tests/repro_issues/test_bug_10_logistics_update.py`
- **Test(s):** `test_ammo_usage_triggers_logistics_row`
- **Reason:** DUPLICATE_OF:`tests/unit/ui/test_ui_stats.py` (logistics rows for ammo/energy resources)
- **Confidence:** HIGH
- **Evidence:** Tests that adding a weapon consuming ammo triggers logistics row display. This is the same behavior tested in `test_ui_stats.py`. The repro manually injects ability_instances (line 53-56) and uses the deprecated `get_layer_key` workaround (line 14-19).
- **Estimated LOC saved:** 112

- **File:** `tests/repro_issues/test_bug_12_energy_gen.py`
- **Test(s):** `test_generator_without_crew_is_inactive`, `test_generator_with_crew_is_active`
- **Reason:** DUPLICATE_OF:`tests/unit/simulation/components/abilities/test_resource_consumption.py`, `tests/unit/modifiers/test_crew_resource_bindings.py`
- **Confidence:** MEDIUM
- **Evidence:** The "bug" turned out to be working-as-designed (comment at line 7-12). Generator requires crew to operate, and the test merely verifies this. Crew requirement deactivation is covered in crew ability tests and resource binding tests. However, this test uniquely validates the production `create_component("generator")` path with crew interaction.
- **Estimated LOC saved:** 110

- **File:** `tests/repro_issues/test_bug_14_multi_planet_offset.py`
- **Test(s):** All 4 test classes (TestMultiPlanetPositionOffset, TestSmallerPlanetPolarCoordinates, TestRendererMultiPlanetLogic, TestProportionalMoonSizing)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** All 16 tests perform pure arithmetic on local variables that never touch the actual renderer code. For example, lines 38-39 compute `group_offset_x = -largest_diameter * 0.20` then assert the result equals -20.0. No renderer function or strategy_renderer module is imported. These tests verify math constants, not behavior. No matching tests exist in `tests/unit/` for multi-planet rendering.
- **Estimated LOC saved:** 337

- **File:** `tests/repro_issues/test_bug_16_raw_data_button.py`
- **Test(s):** `TestRawDataButtonPosition.test_button_position_calculation`, `test_button_position_in_source_code`
- **Reason:** TESTS_NOTHING_REAL (first test) + OVER_MOCKED (second test uses inspect.getsource)
- **Confidence:** HIGH
- **Evidence:** `test_button_position_calculation` (line 13-41) computes `btn_x = graph_rect.right - 22` in local variables and asserts the arithmetic. It never calls any production function. `test_button_position_in_source_code` (line 43-61) reads source code as a string and checks for substring `"graph_rect.right"` -- this is a code-smell detector, not a behavioral test.
- **Estimated LOC saved:** 64

- **File:** `tests/repro_issues/test_bug_17_drag_preview.py`
- **Test(s):** All 3 tests in `TestDragPreviewIcon`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** `test_dragged_item_stores_portrait` (line 13-30) reads source code via `inspect.getsource` and asserts `"portrait" in source.lower()`. `test_draw_renders_icon_at_cursor` (line 32-48) does the same. `test_icon_size_appropriate` (line 50-62) asserts a local constant `DRAG_ICON_SIZE = 48` is between 32 and 64. None of these tests execute production code.
- **Estimated LOC saved:** 62

- **File:** `tests/repro_issues/test_crash_planet_list.py`
- **Test(s):** `test_repro_crash_fixed`
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Lines 7-22 define `MockGalaxy` and `MockPlanetListWindow` that re-implement `_gather_planets()` locally. The test verifies the local mock implementation, never touching the real `PlanetListWindow` class. The actual planet list window is tested in `tests/unit/ui/screens/test_planet_list_filters.py`.
- **Estimated LOC saved:** 43

- **File:** `tests/unit/test_builder_refactor.py`
- **Test(s):** `TestBuilderRefactor.test_imports`, `test_preset_manager`
- **Reason:** DUPLICATE_OF:`tests/unit/ui/screens/test_planet_list_components.py` (PresetManager) + TRIVIAL_CONSTANT (import test)
- **Confidence:** HIGH
- **Evidence:** `test_imports` (line 11-18) only checks that 3 modules can be imported, which is implicitly tested by every other test that imports them. `test_preset_manager` (line 25-32) tests basic save/load of PresetManager, which is also tested in `test_planet_list_components.py`. Uses `unittest.TestCase` instead of pytest, suggesting this is legacy scaffolding.
- **Estimated LOC saved:** 36

- **File:** `tests/unit/_verify_builder_imports.py`
- **Test(s):** N/A (standalone script, not a pytest test)
- **Reason:** DEAD_CODE
- **Confidence:** HIGH
- **Evidence:** This is a standalone verification script (not a test class/function) that calls `pygame.init()` at module level (line 5-6) and does `sys.exit(1)` on failure (line 17). It's not discovered by pytest and provides no value as the imports it checks (`BuilderLeftPanel`, `ComponentListItem`) are tested by hundreds of other test files.
- **Estimated LOC saved:** 20

- **File:** `tests/unit/performance/reproduce_scaling.py`
- **Test(s):** `TestComponentScaling.test_crew_scaling`, `test_life_support_scaling`
- **Reason:** DUPLICATE_OF:`tests/unit/modifiers/test_crew_required_mass_scaling.py` and `tests/unit/simulation/components/abilities/test_crew_abilities.py`
- **Confidence:** MEDIUM
- **Evidence:** Tests that CrewCapacity and LifeSupportCapacity scale linearly with the `simple_size_mount` modifier at scale 2. This is modifier ability scaling which is covered by dedicated modifier binding tests. File is in `performance/` but tests no performance characteristics (no timing, no benchmarks). Missing `__init__.py` in the directory.
- **Estimated LOC saved:** 41

### A2. Project Tests with Placeholder/Scaffold Tests

- **File:** `tests/projects/test_extract_phase.py`
- **Test(s):** `TestValidatePhaseWithExtracted` (3 methods), `TestValidateAuditReadyWithExtracted` (3 methods)
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Six test methods at lines 406-430 have `pass` bodies with docstrings only. `test_validate_phase_extracted_with_active_subproject`, `test_validate_phase_extracted_with_archived_subproject`, `test_audit_ready_with_extracted_phases`, `test_audit_ready_warns_active_subproject`, `test_audit_ready_errors_missing_subproject` all contain only `pass`. These 5 placeholder tests do nothing and should either be implemented or removed. (Note: the rest of the file -- ~400 LOC -- contains legitimate tests for the extraction tooling and should be kept.)
- **Estimated LOC saved:** 18 (just the placeholder methods; rest of file is valuable)

## B. Tests That Are Happy-Path-Only

- **File:** `tests/unit/infrastructure/test_state_snapshot.py`
- **Test(s):** `TestCompareGameStatesUnit`, `TestVerificationReport`
- **What's tested:** Basic dict comparison and VerificationReport dataclass fields
- **What's missing:** No tests for nested ignore_fields, unordered_lists, float tolerance, type mismatches, or empty dicts with ignore_fields. The `test_deep_compare.py` file covers `deep_compare` thoroughly, but `compare_game_states` (which wraps it with defaults) has only 3 trivial tests.
- **Source method(s) affected:** `tests/infrastructure/state_snapshot.py:compare_game_states`
- **Priority:** LOW (wrapper function; underlying utility is well-tested)

- **File:** `tests/unit/regressions/test_regressions.py`
- **Test(s):** `TestRegressions.test_ship_classes_update_in_place`
- **What's tested:** Only that `vehicle_classes` dict reference identity is preserved after `load_vehicle_classes`
- **What's missing:** No test for what happens when `load_vehicle_classes` fails, returns empty, or is called multiple times. No test for content correctness (only reference identity).
- **Source method(s) affected:** `game/simulation/entities/ship_loader.py:load_vehicle_classes`
- **Priority:** LOW (singleton reference identity is niche; content tested elsewhere)

- **File:** `tests/unit/test_modifier_logic.py`
- **Test(s):** `TestModifierLogic` (all methods)
- **What's tested:** Snap increment/decrement and size decrement arithmetic for turret angles and sizes
- **What's missing:** No tests for negative values, zero intervals, max_val < min_val, floating point intervals, or boundary conditions (e.g., current == min_val for decrement). Also, the tests implement the logic locally (lines 5-33) rather than importing from `game.ui.screens.builder.modifier_logic`. Proper tests exist in `tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py` and `test_modifier_logic_service.py` that test the actual production code.
- **Source method(s) affected:** `game/ui/screens/builder/modifier_logic.py`
- **Priority:** LOW (production code is tested by proper unit tests; this file tests a local reimplementation)

## C. Source Code with Inadequate Coverage

No source files in this review scope have inadequate coverage. The key source files checked:
- `game/core/profiling.py`: 98.8% (81/82 lines) -- excellent
- `game/ui/services/screenshot_manager.py`: 100% (105/105 lines) -- perfect
- `tests/infrastructure/deep_compare.py` and `tests/infrastructure/state_snapshot.py` are test utilities (not in coverage.json by design)

The multi-planet rendering logic in `game/ui/screens/strategy_renderer.py` is **not covered by the repro tests** in `test_bug_14_multi_planet_offset.py` (they only test local arithmetic). If multi-planet rendering is important, proper tests against the renderer should be written -- but that is in the UI rendering domain (session 3 scope), not this review.

## D. Cross-Domain Observations

1. **test_bug_04_display.py (UI/Builder domain):** This repro tests `BuilderRightPanel.on_ship_updated` and `DesignStatsPanel.needs_rebuild()` with heavy mocking (14 patches at lines 43-56). The behavior it verifies (stats panel rebuild + update after ship changes) should be checked by session 3 (UI tests) to confirm it's covered in `tests/unit/ui/panels/` or `tests/unit/ui/screens/builder/`.

2. **test_bug_09_hull_in_palette.py (UI/Builder domain):** Tests that hull components are filtered from the BuilderLeftPanel component palette. Only one unit test file (`tests/unit/ui/test_structure_visibility.py`) was found covering hull visibility. Session 3 should verify this regression is properly covered in builder tests.

3. **test_bug_11_dialog_size.py (UI domain):** Tests pygame_gui UIConfirmationDialog scroll behavior with specific pixel dimensions. No equivalent test exists in `tests/unit/`. This is a UI rendering concern; session 3 should assess whether this UI layout regression needs a proper test.

4. **test_bug_11_hull_update.py (Entity domain):** Tests hull component swapping when changing ship class. Covered by `tests/unit/simulation/entities/test_ship_component_manager.py` and `tests/unit/entities/ship_helpers/test_component_operations.py`. Session 1 (simulation) should verify completeness.

5. **test_bug_12_hull_layer_addition.py (Entity domain):** Tests that non-hull components cannot be added to HULL layer. No matching test found in `tests/unit/` with `add_component` + `LayerType.HULL`. Session 1 should verify this constraint is tested in `test_ship_component_manager.py` or entity tests.

6. **test_bug_13_clear_removes_hull.py (Workshop/UI domain):** Tests `DesignWorkshopScreen._clear_design` preserves hull. Covered by 6 files in `tests/unit/` referencing `clear_design` / `clear_non_hull`. Session 3 should confirm the workshop viewmodel tests cover this.

7. **test_bug_13_weapons_report.py (UI/Builder domain):** Tests `WeaponsViewModel.get_points_of_interest` and panel MVVM architecture. Covered by `tests/unit/ui/builder/test_weapons_viewmodel.py`. Session 3 should confirm completeness.

8. **test_bug_15_screenshot_strategy.py (UI services domain):** Tests screenshot manager strategy layer support, hotkeys, and build queue integration. Well-covered by `tests/unit/ui/services/test_screenshot_manager.py` (100% source coverage) and `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`. However, this 364-LOC repro file has some integration tests (BuildQueueScreen F12 handling at lines 271-364) that may not be duplicated elsewhere. Session 3 should verify.

9. **test_bug_27_ordertype.py (Strategy/UI domain):** Tests OrderType import and fleet detail report rendering with orders. OrderType is extensively tested across 20+ strategy test files. The `show_detailed_report` integration test (lines 45-77) may provide unique coverage of the StrategyUI detail formatter with fleet orders. Session 2 (strategy) should verify.

10. **test_modifier_logic.py (UI/Builder domain):** Tests snap increment/decrement logic but implements the functions locally rather than importing from production code. Proper tests exist at `tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py` and `test_modifier_logic_service.py`. This file is effectively dead since it tests its own local code, not the production module.

11. **test_extract_phase.py (Projects tooling):** Tests the `Projects/scripts/extract_phase.py` utility. This is not game code but project management tooling. The non-placeholder tests (400+ LOC) are legitimate and well-structured. The 5 placeholder tests (lines 406-430) should either be implemented or removed.

12. **Regressions directory (`tests/unit/regressions/`):** The 3 files here (327 total LOC) contain legitimate regression tests. `test_bug_regressions_2026_01.py` tests 3 specific bug fixes and is partially duplicated by repro_issues but adds unique value by testing the Component shim removal (line 107: `assert not hasattr(c, 'range')`). `test_regressions.py` tests singleton reference identity and theme persistence. `test_warnings.py` tests resource validation warnings. All 3 should be kept.

13. **Infrastructure tests (`tests/unit/infrastructure/`):** Both files test test utilities (`deep_compare.py` and `state_snapshot.py`) used by integration tests. `test_deep_compare.py` (265 LOC) is thorough and high-quality. Both should be kept.

14. **test_profiler_perf.py:** Despite being in `performance/`, this tests functional behavior (toggle, record, save_history, json_utils integration) not performance. The profiler source has 98.8% coverage. Tests overlap with `tests/unit/core/profiling/test_decorators.py` and `tests/unit/core/test_profiling_edge_cases.py`, but each file tests different aspects. Consider consolidating into the `tests/unit/core/profiling/` directory for organizational clarity, but no removal recommended.
