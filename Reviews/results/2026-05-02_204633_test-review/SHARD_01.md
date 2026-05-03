# Shard 01 — Test Audit Report

## Summary
- Shard: 01
- Files assigned: 90
- Files actually read: 90
- Total findings: 20
- Critical: 3 | Major: 7 | Minor: 10

## Findings

### tests/integration/strategy/production/test_queue.py (~194 LOC)

#### CAT-1: test_production_progress  [CRITICAL]
- **Location**: test_queue.py:61-76
- **Issue**: Test body is a comment and `pass`. No assertions executed; setup creates a mock but the test never validates any production behavior.
- **Suggestion**: Remove or implement — either delete the dead test or add actual assertions validating tick-based production progress. If the workaround comment indicates refactoring is still needed, convert to a `pytest.skip("Not yet implemented")` marker.
- **LOC affected**: 16

### tests/unit/ai/test_ai.py (~315 LOC)

#### CAT-1: test_navigate_to_rotates_ship  [CRITICAL]
- **Location**: test_ai.py:124-136
- **Issue**: The test sets up a navigation call, initializes angle state, then ends with `pass` — no assertion is made. The comment says "Rotation logic verified visually in game" but the test provides zero automated regression protection.
- **Suggestion**: Add a concrete assertion on the ship.angle change, or remove the test since it provides no value. If visual-only verification is intentional, mark with `@pytest.mark.skip(reason="Visual verification only")`.
- **LOC affected**: 13

### tests/unit/ui/test_race_portrait_gallery.py (~320 LOC)

#### CAT-2: All tests use __new__ bypassing __init__ — tests nothing real  [CRITICAL]
- **Location**: test_race_portrait_gallery.py:57-320
- **Issue**: Every test method patches `RacePortraitGallery.__init__` to a no-op and constructs instances via `__new__`, then manually assembles all internal attributes. The real constructor is NEVER exercised. Any bug in `__init__` (e.g., missing attribute initialization, missing pygame_gui element creation) would pass these tests unnoticed. Zero regression protection for the actual class lifecycle. Severity downgraded to CRITICAL-only despite the blast radius being contained to this file, because the pattern invalidates every test.
- **Suggestion**: Rewrite tests to instantiate RacePortraitGallery through its normal constructor with mocked pygame_gui dependencies, or delete the class-level test file in favor of integration tests that exercise the real widget.
- **LOC affected**: 240

### tests/unit/ui/test_race_description_panel.py (~468 LOC)

#### CAT-2: All tests use __new__ bypassing __init__ — tests nothing real  [MAJOR]
- **Location**: test_race_description_panel.py:39-271
- **Issue**: Same `patch.object(RaceDescriptionPanel, '__init__', ...)` + `__new__` anti-pattern as test_race_portrait_gallery.py. The real constructor is never called. Every test manually wires internal attributes. Downgraded from CRITICAL to MAJOR because the test file does validate some business logic (char counting, config read/write) through the manually-populated mock, giving partial value — but constructor integrity and pygame_gui element creation are entirely untested.
- **Suggestion**: Rewrite tests to use real construction with mocked pygame_gui, or migrate to integration-level tests.
- **LOC affected**: 230

### tests/unit/builder/test_builder_improvements.py (~126 LOC)

#### CAT-1: test_image_scale_factor  [MAJOR]
- **Location**: test_builder_improvements.py:25-42
- **Issue**: The test only verifies that `builder.draw(window)` does not raise an exception. The try/except/fail pattern asserts nothing about correctness — it's a smoke test, not a behavioral test. If the draw method silently rendered incorrectly (wrong scale, wrong colors, empty image), this test would still pass. Downgraded from CRITICAL because it does exercise real code paths (pygame draw) and catches outright crashes.
- **Suggestion**: Either add post-draw assertions (e.g., verify surface pixel values at expected coordinates, or verify draw calls on a mocked canvas) or document as a smoke test and pair with a proper behavioral test.
- **LOC affected**: 18

#### CAT-8: test_loading_sync  [MAJOR]
- **Location**: test_builder_improvements.py:44-126
- **Issue**: The setup constructs a mock ship with ~45 attribute assignments (lines 56-108) before exercising a single load_ship flow. Over 60% of the test body is mock configuration. The test only asserts `builder.ship == mock_ship` plus a dropdown check.
- **Suggestion**: Extract mock-ship creation into a shared helper function. Reduce the test to mocking only the attributes that the SUT (`load_ship` → `_ship_io_adapter.load_ship`) actually reads.
- **LOC affected**: 83

### tests/unit/modifiers/test_seeker_multi_ability.py (~242 LOC)

#### CAT-2: test_seeker_does_not_use_direct_stats_access  [MAJOR]
- **Location**: test_seeker_multi_ability.py:66-82
- **Issue**: Uses `inspect.getsource()` to assert that certain string patterns do NOT appear in the source code of `SeekerWeaponAbility.recalculate`. Tests source text, not runtime behavior. A refactored implementation using equivalent logic with different variable names would fail this test despite being correct.
- **Suggestion**: Remove the source inspection test. The behavioral tests (test_seeker_endurance_applies_modifier_correctly etc.) already verify that `get_effective_stat` is used by checking correct output values. Source-inspection is redundant and brittle.
- **LOC affected**: 17

### tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py (~244 LOC)

#### CAT-6: test_clone_ship_calls_ship_instance_create  [MAJOR]
- **Location**: test_fleet_hierarchy_editor.py:81-98
- **Issue**: Mocks `ShipInstance.create` to assert it was called with specific kwargs. This encodes the internal call chain (`_clone_ship` → `ShipInstance.create` → specific kwargs). If the clone implementation switches to a different constructor or factory pattern, this test fails even if cloning still works correctly. This is a change-detector.
- **Suggestion**: Verify the output — assert the cloned ship has the expected name, design_data, and owner_id — rather than asserting on the internal call to `ShipInstance.create`.
- **LOC affected**: 18

### tests/unit/ai/test_ai.py (~315 LOC)

#### CAT-6: test_attack_run_transitions_to_retreat  [MINOR]
- **Location**: test_ai.py:228-237
- **Issue**: Depends on exact spatial coordinates (ship at (0,0), target at (150,0)) to trigger the `retreat` state transition. These magic numbers are coupled to the `AttackRunBehavior.approach_distance` calculation (`range * 0.3 * hysteresis`). If the behavior's distance constant changes, the test silently breaks.
- **Suggestion**: Mock the weapon_range to a known value so the approach distance is deterministic, or explicitly set the ship position relative to the calculated threshold.
- **LOC affected**: 10

### tests/unit/strategy/facade/test_system_dto.py (~432 LOC)

#### CAT-10: DTO creation + frozen tests cluster  [MINOR]
- **Location**: test_system_dto.py:26-38 (test_create_star_info), test_system_dto.py:44-54 (test_create_warp_point_info), test_system_dto.py:72-113 (test_create_basic_system_info + test_create_full_system_info), test_system_dto.py:272-306 (test_create_planet_info + test_create_colonized_planet)
- **Issue**: 6 tests across 3 classes follow the identical pattern: construct a DTO, assert that each field has the expected value. These could be one parametrized test per DTO class.
- **Suggestion**: Consolidate into `@pytest.mark.parametrize` with (field_name, expected_value) tuples.
- **LOC affected**: 80

### tests/unit/strategy/data/test_design_metadata_validation.py (~89 LOC)

#### CAT-10: Missing-field defaults cluster  [MINOR]
- **Location**: test_design_metadata_validation.py:49-77
- **Issue**: Test functions `test_missing_ship_class_uses_default`, `test_missing_vehicle_type_uses_default`, `test_missing_mass_uses_default`, `test_missing_combat_power_uses_default`, `test_missing_construction_cost_uses_default` — 5 tests with identical structure (delete a key, call from_dict, assert default value). Only the deleted key and expected default differ.
- **Suggestion**: Parametrize into a single test function: `@pytest.mark.parametrize("key,default", [("ship_class", "Unknown"), ("vehicle_type", "Ship"), ("mass", 0.0), ...])`.
- **LOC affected**: 30

### tests/unit/strategy/planet/test_planet_validation.py (~227 LOC)

#### CAT-10: test_missing_key_raises_persistence_exception cluster  [MINOR]
- **Location**: test_planet_validation.py:64-78 (already partly parametrized via decorator) and test_planet_validation.py:94-116 (two partial parametrize blocks)
- **Issue**: The validation tests for "negative values raise" on positive-only vs non-negative fields are split across two parametrize blocks (lines 94-116) but use identical assertion patterns. Could be one parametrize block.
- **Suggestion**: Merge the two `@pytest.mark.parametrize` blocks into a single parametrize with additional `expected_field` info, or leave as-is since they are already parametrized (just split across two decorators). Minor refactoring note.
- **LOC affected**: 20

### tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py (~186 LOC)

#### CAT-2: test_get_destination_default_self_fleet_is_none  [MINOR]
- **Location**: test_fleet_navigation_mutual_pursuit.py:175-186
- **Issue**: Uses `inspect.signature()` to verify a parameter has `default=None`. Tests the code's signature text, not its behavior. If the parameter is renamed or moved, this test fails without catching a real bug. Downgraded to MINOR because it's one test in an otherwise behavioral file.
- **Suggestion**: Replace with a behavioral test that calls `get_destination()` without the `self_fleet` keyword and verifies it falls back to intercept behavior (as is already done in `test_no_self_fleet_falls_back_to_intercept` on line 152).
- **LOC affected**: 12

### tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py (~244 LOC)

#### CAT-1: test_editor_has_no_instance_state  [MINOR]
- **Location**: test_fleet_hierarchy_editor.py:232-244
- **Issue**: Creates an editor instance and asserts its `__dict__` (excluding dunders) is empty. This tests that a freshly-constructed object has no attributes set outside `__init__` — but it tests nothing about correctness. The test adds no behavioral regression value since the editor is fully stateless by design. Downgraded to MINOR because the LOC impact is tiny.
- **Suggestion**: Remove. If the stateless property is semantically important, rename `TestStateless` to `TestEditorStatelessProperty` and add a docstring explaining why no attributes is the expected contract.
- **LOC affected**: 13

### tests/repro_issues/repro_warp_bug.py (~79 LOC)

#### CAT-3: Standalone repro script for bugs already covered by proper tests  [MAJOR]
- **Location**: repro_warp_bug.py:1-79
- **Issue**: This is a standalone reproduction script with manual `print()` calls and `if __name__ == "__main__"` entry point, testing warp point creation and UI display bugs that are already covered by proper unit/integration tests (superweapon_order_processor, strategy_detail_fmt). Standalone repro scripts that duplicate existing test coverage are dead test code.
- **Suggestion**: Delete the file. If the bugs are not fully covered elsewhere, integrate the test assertions into the proper test framework (pytest, no print-based assertions).
- **LOC affected**: 79

### tests/unit/strategy/services/test_ship_stats_cargo_storage.py (~68 LOC)

#### CAT-4: Duplicates cargo_storage integration coverage from test_cargo_storage.py  [MAJOR]
- **Location**: Entire file (test_cargo_storage_populated_from_passenger_quarters, test_cargo_storage_sums_multiple_components)
- **Issue**: Both tests verify that cargo_storage aggregation works through `calculate_design_stats` — a path already exercised by `tests/unit/simulation/abilities/test_cargo_storage.py` (which tests the same component data and ability values). The two tests differ only in the number of passenger_quarters used (1 vs 2), which is already implicitly covered by the modifier scaling tests in test_cargo_storage.py. Downgraded from CRITICAL because file was explicitly created to replace deleted strategy-layer tests and validates a different pipeline stage (design stats vs. ability-level recalculate).
- **Suggestion**: Consolidate into the simulation-layer cargo storage tests, or add `@pytest.mark.parametrize` to reduce to one test. If the design-stats pipeline is a distinct concern, add a clarifying comment in both files about which pipeline phase each tests.
- **LOC affected**: 68

### tests/unit/strategy/data/test_data_layer_boundaries.py (~67 LOC)

#### CAT-2: Architectural AST guard — no behavioral test  [MINOR]
- **Location**: test_data_layer_boundaries.py:1-67
- **Issue**: Tests parse Python source files with `ast` and check import patterns. No production code paths are exercised; no game.* imports. This is a static analysis check, not a unit test. Downgraded to MINOR because the check has real architectural value (enforcing layer boundaries), and this is the accepted pattern in the codebase for invariant enforcement.
- **Suggestion**: Keep as-is; note in file docstring that this is an AST guard, not a behavioral test. Consider moving to a `Tools/` linter or pre-commit hook.
- **LOC affected**: 67

### tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py (~67 LOC)

#### CAT-2: AST static-analysis guard — no behavioral test  [MINOR]
- **Location**: test_ability_sources_no_global_registry_access.py:1-67
- **Issue**: Same AST-scan pattern as test_data_layer_boundaries.py. No production code paths exercised. Downgraded to MINOR for same reason — architectural guard with real enforcement value.
- **Suggestion**: Keep as-is; note in file docstring that this is an AST guard.
- **LOC affected**: 67

### tests/unit/simulation/entities/test_ship_component_manager_di.py (~29 LOC)

#### CAT-2: Source-code content scan — no behavioral test  [MINOR]
- **Location**: test_ship_component_manager_di.py:1-29
- **Issue**: Opens source files and checks for string absence of `get_default_registry_provider`. No behavioral test. Downgraded to MINOR — tiny file, targeted DI enforcement.
- **Suggestion**: Keep as-is. If the scan logic is duplicated across multiple files, consider a shared helper.
- **LOC affected**: 29

### tests/unit/strategy/engine/test_colonize_mission_handler.py (~275 LOC)

#### CAT-11: make_component_registry has duplicate key  [MINOR]
- **Location**: test_colonize_mission_handler.py:107-123
- **Issue**: The `make_component_registry()` helper defines the `'colony_pod'` key twice (lines 108-117 and 113-117 are identical). The second overwrites the first with the same value, so there's no runtime bug — but the dead duplication implies a copy-paste error that may have been meant for a different component (e.g., `ice_dwarf_colony_pod`). The test file only exercises universal pod paths that don't depend on this.
- **Suggestion**: Remove the duplicate `'colony_pod'` entry.
- **LOC affected**: 10

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/unit/builder/test_builder_logic.py | Read ✓ | 0 |
| tests/integration/strategy/test_radiation.py | Read ✓ | 0 |
| tests/integration/ai_strategy/test_response.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_design_metadata_validation.py | Read ✓ | 1 |
| tests/integration/strategy/production/test_queue.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_water_engine.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py | Read ✓ | 0 |
| tests/unit/simulation/battle_controller/test_execution.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_empire_economy_service.py | Read ✓ | 0 |
| tests/integration/strategy/test_stabilizer_blocks_superweapon.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_system_dto.py | Read ✓ | 1 |
| tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py | Read ✓ | 2 |
| tests/repro_issues/repro_warp_bug.py | Read ✓ | 1 |
| tests/unit/strategy/services/test_race_description_prompt_builder.py | Read ✓ | 0 |
| tests/repro_issues/test_bug_09_hull_in_palette.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_improvements.py | Read ✓ | 2 |
| tests/unit/modifiers/test_modifier_json_schema.py | Read ✓ | 0 |
| tests/unit/ai/test_ai.py | Read ✓ | 2 |
| tests/integration/save_load/test_roundtrip_designs.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_terraforming_abilities.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_orders.py | Read ✓ | 0 |
| tests/unit/ui/interfaces/test_battle_ui.py | Read ✓ | 0 |
| tests/unit/strategy/test_design_metadata.py | Read ✓ | 0 |
| tests/unit/simulation/projectile_guidance/test_guidance_behavior.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_transfer_order.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_stats_dirty_flag.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_system_selection_window.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_homeworld_presets.py | Read ✓ | 0 |
| tests/unit/modifiers/test_seeker_multi_ability.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py | Read ✓ | 0 |
| tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py | Read ✓ | 0 |
| tests/unit/core/test_formula_evaluator.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_data_layer_boundaries.py | Read ✓ | 1 |
| tests/unit/ai/test_behavior_units.py | Read ✓ | 0 |
| tests/unit/ui/test_structure_visibility.py | Read ✓ | 0 |
| tests/unit/ui/test_race_portrait_gallery.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_empire_build_queue_formatter.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_planet.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_race_caption_loader.py | Read ✓ | 0 |
| tests/unit/ui/test_ui_stats.py | Read ✓ | 0 |
| tests/fixtures/test_scenarios.py | Read ✓ | 0 |
| tests/unit/strategy/fleet/test_build_order.py | Read ✓ | 0 |
| tests/unit/ui/test_empire_asset_loading.py | Read ✓ | 0 |
| tests/unit/strategy/save_game_service/test_save_load_ops.py | Read ✓ | 0 |
| tests/integration/ui/test_build_queue_enhanced_planet_report.py | Read ✓ | 0 |
| tests/unit/regressions/test_regressions.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_ship_stats_cargo_storage.py | Read ✓ | 1 |
| tests/unit/core/registry/test_registry_operations.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_deployment_zone_calculator.py | Read ✓ | 0 |
| tests/unit/assets/test_asset_manager_resolutions.py | Read ✓ | 0 |
| tests/unit/simulation/abilities/test_cargo_storage.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py | Read ✓ | 1 |
| tests/unit/strategy/services/ability_sources/test_labels.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_structure_features.py | Read ✓ | 0 |
| tests/unit/ui/test_ui_config.py | Read ✓ | 0 |
| tests/unit/strategy/facade/test_facade_robust_resolution.py | Read ✓ | 0 |
| tests/unit/ui/test_race_description_panel.py | Read ✓ | 1 |
| tests/unit/modifiers/test_propulsion_ability_bindings.py | Read ✓ | 0 |
| tests/unit/simulation/ship_combat_engine/test_cooldowns.py | Read ✓ | 0 |
| tests/integration/save_load/test_roundtrip_galaxy.py | Read ✓ | 0 |
| tests/integration/strategy/test_fleet_movement.py | Read ✓ | 0 |
| tests/integration/resource_system/test_resource_pipeline.py | Read ✓ | 0 |
| tests/unit/core/profiling/test_singleton_threading.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_event_log_data_source.py | Read ✓ | 0 |
| tests/unit/core/test_math_vector2.py | Read ✓ | 0 |
| tests/unit/simulation/test_formula_exceptions.py | Read ✓ | 0 |
| tests/unit/ai/test_ai_capabilities_cache.py | Read ✓ | 0 |
| tests/integration/strategy/test_demographics_loop.py | Read ✓ | 0 |
| tests/unit/strategy/test_fleet_capability_calculator.py | Read ✓ | 0 |
| tests/unit/strategy/planet_atmosphere/test_generation.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_fleet_id_global.py | Read ✓ | 0 |
| tests/integration/fleet_combat/test_component_destruction_cascade.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py | Read ✓ | 1 |
| tests/unit/strategy/formulas/test_habitability.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_galaxy.py | Read ✓ | 0 |
| tests/unit/tools/test_test_sharded_baseline.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_empire_resources.py | Read ✓ | 0 |
| tests/unit/strategy/test_fleet_capability_calculator_di.py | Read ✓ | 0 |
| tests/unit/strategy/turn_engine/test_turn_error_handling.py | Read ✓ | 0 |
| tests/unit/simulation/battle_controller/test_mechanics.py | Read ✓ | 0 |
| tests/unit/simulation/services/test_battle_service.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_colonize_mission_handler.py | Read ✓ | 1 |
| tests/unit/entities/test_ship_di.py | Read ✓ | 0 |
| tests/unit/simulation/entities/test_ship_component_manager_di.py | Read ✓ | 1 |
| tests/integration/resource_system/test_fleet_operations.py | Read ✓ | 0 |
| tests/unit/strategy/planet/test_planet_validation.py | Read ✓ | 1 |
| tests/unit/core/test_registry_provider.py | Read ✓ | 0 |
| tests/unit/modifiers/test_invalid_operation_handling.py | Read ✓ | 0 |
| tests/integration/ui/test_fleet_build_button.py | Read ✓ | 0 |
| tests/integration/strategy/test_mutual_join_rendezvous.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~25000 (test files) + ~2000 (conftest/fixture imports and minimal production code referenced)
- Approximate headroom: Medium (200-500K)
