# Shard 02 — Test Audit Report

## Summary
- Shard: 02
- Files assigned: 94
- Files actually read: 94
- Total findings: 22
- Critical: 5 | Major: 7 | Minor: 10

## Findings

### tests/unit/builder/test_ship_loading.py (~131 LOC)
#### CAT-1: test_all_ships_match_expected_stats  [CRITICAL]
- **Location**: test_ship_loading.py:80-131
- **Issue**: Passes vacuously when `ships_dir` contains zero JSON files — the `failures` list stays empty and no assertion fires. Also passes when all ships lack `expected_stats` (line 96: `continue`).
- **Suggestion**: Add a minimum-ship-files assertion before the loop, e.g. `assert len(ship_files) >= 1`.
- **LOC affected**: 5

#### CAT-12: test_all_ships_match_expected_stats  [MINOR]
- **Location**: test_ship_loading.py:88-129
- **Issue**: Logic-heavy test body with for-loops, nested if/else checks for multiple stat types, and try/except that catches broad Exception.
- **Suggestion**: Extract per-ship validation into a helper and parametrize by design file.
- **LOC affected**: 42

### tests/unit/builder/test_bulk_add.py (~30 LOC)
#### CAT-1: test_bulk_add_success  [CRITICAL]
- **Location**: test_bulk_add.py:9-30
- **Issue**: Single assertion `assert len(ship.layers[LayerType.ARMOR].components) == 10` depends on a mocked `Component` with hardcoded `allowed_layers` removed comment (line 21). If Component constructor behavior changes, this test may silently pass with different counts.
- **Suggestion**: Verify the component was actually added to the correct layer using `assert ship.layers[LayerType.ARMOR].components[0] is comp`.
- **LOC affected**: 22

### tests/unit/strategy/services/test_empire_economy_caching.py (~83 LOC)
#### CAT-12: Logic-heavy test bodies  [MINOR]
- **Location**: test_empire_economy_caching.py:32-83
- **Issue**: Four tests all unpack `smoke_turn1_scenario` identically (`session, galaxy, empires = smoke_turn1_scenario`) and call `_build_service(fresh_registries)`. Setup pattern repeated verbatim.
- **Suggestion**: Extract into a fixture that yields `(service, session, galaxy, empires)`.
- **LOC affected**: 20

### tests/unit/modifiers/test_pipeline_unification.py (~174 LOC)
#### CAT-9: Repeated `first_component_with_ability` lookups  [MINOR]
- **Location**: test_pipeline_unification.py:46-145
- **Issue**: Six tests call `first_component_with_ability()` then `component.recalculate_stats()` and `component.add_modifier(...)`. The shape is identical across all tests; only the ability name and modifier parameters differ.
- **Suggestion**: Parametrize on ability name + modifier id + expected values.
- **LOC affected**: 90

### tests/unit/ui/screens/test_build_queue_panel_factory.py (~234 LOC)
#### CAT-6: test_every_uipanel_in_factory_uses_fast_panel_class_id  [MAJOR]
- **Location**: test_build_queue_panel_factory.py:170-206
- **Issue**: Asserts on `mock_panel.call_args_list` to verify `object_id="@fast_panel"` — binds the test to the exact internal construction order of `create_all_panels`. Adding a new UIPanel in any position will break the assertion.
- **Suggestion**: Use `assert mock_panel.assert_called_with(...)` patterns, or check that every call had `object_id="@fast_panel"` without checking call_count.
- **LOC affected**: 37

#### CAT-8: test_scoped_fast_panel_object_id fixture setup  [MINOR]
- **Location**: test_build_queue_panel_factory.py:133-168
- **Issue**: `_build_factory_for_create_all_panels` creates 12+ MagicMock attributes on the factory and patches 10+ UI primitives. Setup is >50% of the test body.
- **Suggestion**: Extract mock UI configuration into a reusable fixture.
- **LOC affected**: 35

#### CAT-12: test_theme_json_has_fast_panel_block_with_rectangle_shape  [MINOR]
- **Location**: test_build_queue_panel_factory.py:208-234
- **Issue**: Resolves repo root via five `os.path.dirname` calls and reads a real JSON file from disk. This is a filesystem dependency test, not a unit test.
- **Suggestion**: Move to integration tests or use `Paths` module for repo-root resolution.
- **LOC affected**: 27

### tests/unit/strategy/consumable_management_engine/conftest.py (~52 LOC)
#### CAT-1: Fixture-only file, no test functions  [CRITICAL] — downgraded to MAJOR
- **Location**: conftest.py:1-52
- **Issue**: This conftest contains only fixtures (`mock_registries`, `mock_ship`, `mock_fleet`, `mock_empire`). The sibling `test_initialization.py` duplicates `mock_registries` inline at line 12-20. The conftest fixtures are effectively dead.
- **Suggestion**: Either use the conftest fixtures in the sibling test file or remove the conftest.
- **LOC affected**: 52

### tests/unit/ui/test_theme_discovery.py (~554 LOC)
#### CAT-5: Autouse fixtures re-init pygame display per test  [MAJOR]
- **Location**: test_theme_discovery.py:26-49, 74-88, 178-185, 238-243, 278-284, 361-366, 401-406, 446-451, 528-533
- **Issue**: Eight test classes each have `autouse=True` fixtures that set `SDL_VIDEODRIVER`, call `pygame.display.set_mode()`, and initialize `ShipThemeManager`. For ~30 tests this means ~30 pygame display mode switches.
- **Suggestion**: Use class-scoped or module-scoped fixtures that share the initialized manager.
- **LOC affected**: 80

### tests/unit/ui/test_detail_panel_rendering.py (~252 LOC)
#### CAT-8: setup_method with 7 nested patch starts  [MINOR]
- **Location**: test_detail_panel_rendering.py:16-76
- **Issue**: `setup_method` starts 7 `patch()` instances, deletes a module from `sys.modules`, configures a mock manager with theme/font/rect stubs, and constructs the panel under test. Setup accounts for 60/252 lines (~24%).
- **Suggestion**: Move pygame_gui mocks to a shared fixture with class scope.
- **LOC affected**: 60

### tests/unit/ui/test_battle_panels_characterization.py (~503 LOC)
#### CAT-4: Near-duplicate draw_*_renders_*_text tests  [MAJOR]
- **Location**: test_battle_panels_characterization.py:435-468
- **Issue**: `test_draw_battle_over_team0_alive_renders_team1_wins_text`, `test_draw_battle_over_team1_alive_renders_team2_wins_text`, and `test_draw_battle_over_no_alive_renders_draw_text` have near-identical bodies differing only in team setup and expected text.
- **Suggestion**: Parametrize on `(ships_config, expected_text)`.
- **LOC affected**: 35

### tests/unit/ai/test_ai.py (~315 LOC)
#### CAT-5: Function-scoped fixtures rebuild full Ship objects per test  [MAJOR]
- **Location**: test_ai.py:17-70, 136-188
- **Issue**: `ai_setup` and `strategy_setup` fixtures are function-scoped and each creates 2+ real `Ship` objects with 4+ components, initializes `SpatialGrid`, loads component data from disk, and creates `AIController` instances. Every test in `TestAIController` and `TestAIStrategyStates` triggers a full rebuild.
- **Suggestion**: Make these class-scoped and use `copy.deepcopy()` or re-initialize only the mutable state.
- **LOC affected**: 130

### tests/unit/strategy/engine/test_engine_event_emission.py (~1045 LOC)
#### CAT-10: Repeated event assertion pattern  [MINOR]
- **Location**: test_engine_event_emission.py:108-192 (four `test_spawn_ship_*` variants), 220-268 (two fleet variants), 276-340 (three complex variants)
- **Issue**: Groups of 2-4 tests share identical structure: create engine, create mocks, call `_spawn_*`, assert `assert len(calls) == 1`, assert event kw fields. Only inputs and expected values differ.
- **Suggestion**: Parametrize by spawn method, input params, and expected event kwargs.
- **LOC affected**: 150

### tests/unit/strategy/data/test_squadron_characterization.py (~200 LOC)
#### CAT-10: Round-trip tests with identical pattern  [MINOR]
- **Location**: test_squadron_characterization.py:113-172
- **Issue**: Six `test_round_trip_*` methods all create a Squadron, call `Squadron.from_dict(original.to_dict())`, and assert field equality. Only ctor args differ.
- **Suggestion**: Parametrize on `(squadron_kwargs, assert_fn)`.
- **LOC affected**: 60

### tests/unit/modifiers/test_propulsion_ability_bindings.py (~186 LOC)
#### CAT-4: Duplicate test patterns across propulsion ability classes  [MAJOR]
- **Location**: test_propulsion_ability_bindings.py:13-186
- **Issue**: Three classes (`TestCombatPropulsionBindings`, `TestManeuveringThrusterBindings`, `TestStrategicMovementBindings`) each have `test_*_has_*_binding`, `test_*_get_consumed_stats`, and `test_*_recalculate` with identical pattern, swapping only the class name and attribute name.
- **Suggestion**: Parametrize on `(ability_class, stat_key, attr_name, value)`.
- **LOC affected**: 100

### tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py (~286 LOC)
#### CAT-4: Duplicate resolver-capture tests  [MAJOR]
- **Location**: test_movement_phase_collaborator.py:89-133 vs tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py:147-196
- **Issue**: `test_resolve_after_threads_registries_into_minefield_resolver` and `test_derive_moved_fleet_ids_threads_registries_to_minefield_resolver` in the sibling descriptor test file test the same contract (registries threaded to MinefieldResolver) with near-identical mocking patterns. These tests exist in two different files under the same shard.
- **Suggestion**: Consolidate one as the canonical test, or (since they test different collaborators) add cross-reference comments.
- **LOC affected**: 90

### tests/unit/simulation/entities/test_ship_physics.py (~566 LOC)
#### CAT-10: Heading/velocity tests with identical pattern  [MINOR]
- **Location**: test_ship_physics.py:356-387
- **Issue**: Four tests (`test_velocity_follows_heading_at_90_degrees`, `_at_180_degrees`, `_at_270_degrees`, and the implicit 0-degree test at 330-342) share identical bodies differing only by angle and expected velocity vector.
- **Suggestion**: Parametrize on `(angle, expected_x, expected_y)`.
- **LOC affected**: 35

### tests/unit/simulation/ship_combat_engine/test_cooldowns.py (~857 LOC)
#### CAT-10: Shield regen tests with identical pattern  [MINOR]
- **Location**: test_cooldowns.py:58-125
- **Issue**: Six shield regen tests (`test_shield_regen_applies_when_below_max`, `_does_not_exceed_max`, `_does_nothing_when_at_max`, `_does_nothing_with_zero_rate`, `_multiple_ticks_accumulate`) follow identical setup: create MagicMock ship, configure attributes, create engine, call `update_combat_cooldowns()`, assert.
- **Suggestion**: Parametrize on `(initial_shields, max, regen_rate, ticks, expected_shields)`.
- **LOC affected**: 70

### tests/unit/simulation/test_formula_exceptions.py (~173 LOC)
#### CAT-10: Formula exception tests with repeated imports  [MINOR]
- **Location**: test_formula_exceptions.py:13-81
- **Issue**: Every test in `TestFormulaExceptionRaising` re-imports `FormulaEvaluator` inside the method body (lines 15, 25, 35, 44, 54, 65, 75). Seven identical `from game.core.formula_evaluator import FormulaEvaluator` lines.
- **Suggestion**: Import once at module level.
- **LOC affected**: 7

### tests/unit/ui/screens/test_strategy_ui_tooltips.py (~60 LOC)
#### CAT-2: test_tooltip_enrichment tests depend on real keybindings file  [CRITICAL] — downgraded to MAJOR
- **Location**: test_strategy_ui_tooltips.py:34-50
- **Issue**: `test_get_tooltip_text_returns_hotkey` asserts exact string matches ("Enter", "Shift+P", "Shift+G") against a real `Paths.DEFAULT_KEYBINDINGS_FILE`. If keybindings are remapped, these tests break unconditionally.
- **Suggestion**: Test the mapping logic with injected/conftest-controlled bindings, not the production defaults file.
- **LOC affected**: 17

### tests/unit/agent_coordination/test_codex_consult_skills.py (~101 LOC)
#### CAT-2: Tests only file content, no game.* imports  [CRITICAL]
- **Location**: test_codex_consult_skills.py:1-101
- **Issue**: All three tests read `.md` and `.yaml` files from `.agents/skills/` and assert string containment. No game code is exercised. These are documentation/content tests, not code tests.
- **Suggestion**: Move to `tests/static_guards/` or `tests/projects/` directory; keep severity.
- **LOC affected**: 101

### tests/integration/strategy/test_fleet_navigation_consistency.py (~453 LOC)
#### CAT-1: test_already_at_destination_consistency  [CRITICAL]
- **Location**: test_fleet_navigation_consistency.py:308-326
- **Issue**: The fleet at `HexCoord(5, 5)` is ordered to MOVE to `HexCoord(5, 5)`. After `process_turn()`, asserts `len(fleet.orders) == 0` but this depends on the handler immediately popping the order when the fleet is already at destination — an implementation detail that could change without breaking player-facing behavior.
- **Suggestion**: Assert `fleet.location == loc` only; avoid asserting on order queue internals.
- **LOC affected**: 18

### tests/unit/services/llm/test_background.py (~473 LOC)
#### CAT-7: time.sleep() in test bodies  [MAJOR]
- **Location**: test_background.py:140-149, 197-202, 195-210  (multiple locations)
- **Issue**: Several tests use `time.sleep(0.01)` or `time.sleep(0.02)` to wait for worker threads to start. These add real latency to test runs (~0.5s cumulative) and are fragile in CI.
- **Suggestion**: Use `threading.Event`-based synchronization instead of sleep.
- **LOC affected**: 8

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/integration/colonization/test_edge_cases.py | OK | 0 |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | ISSUES | CAT-6, CAT-8, CAT-12 |
| tests/unit/builder/test_ship_loading.py | ISSUES | CAT-1, CAT-12 |
| tests/unit/modifiers/test_pipeline_unification.py | ISSUES | CAT-9 |
| tests/unit/ui/test_theme_discovery.py | ISSUES | CAT-5 |
| tests/unit/strategy/services/test_empire_economy_caching.py | ISSUES | CAT-12 |
| tests/unit/strategy/consumable_management_engine/test_initialization.py | OK | 0 |
| tests/unit/strategy/data/test_construction_queue_paused_persistence.py | OK | 0 |
| tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py | OK | 0 |
| tests/unit/builder/test_bulk_add.py | ISSUES | CAT-1 |
| tests/unit/strategy/engine/order_handlers/test_launch_satellites_handler.py | OK | 0 |
| tests/unit/core/registry/test_registry_features.py | OK | 0 |
| tests/unit/strategy/facade/slices/test_facade_state.py | OK | 0 |
| tests/integration/test_fms_c_launch_in_battle_e2e.py | OK | 0 |
| tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py | OK | 0 |
| tests/unit/quickstart/test_quickstart_races.py | OK | 0 |
| tests/unit/strategy/data/test_squadron_characterization.py | ISSUES | CAT-10 |
| tests/unit/strategy/services/test_modifier_resolver.py | OK | 0 |
| tests/unit/simulation/components/test_ability_manager.py | OK | 0 |
| tests/unit/strategy/data/test_galaxy_warp_generator.py | OK | 0 |
| tests/unit/strategy/test_engine_event_emission.py | ISSUES | CAT-10 |
| tests/unit/ui/services/test_ship_factory.py | OK | 0 |
| tests/unit/strategy/engine/test_environmental_hazard_engine.py | OK | 0 |
| tests/integration/gameplay_loop/test_fleet_operations.py | OK | 0 |
| tests/unit/core/registry/conftest.py | OK | 0 |
| tests/unit/strategy/services/test_fleet_write_service.py | OK | 0 |
| tests/unit/simulation/replay/test_replay_verifier_imports.py | OK | 0 |
| tests/unit/simulation/combat/test_weapon_registry.py | OK | 0 |
| tests/unit/ui/widgets/test_scroll_state.py | OK | 0 |
| tests/integration/strategy/transfer/test_transfer_validation.py | OK | 0 |
| tests/unit/strategy/engine/test_fleet_speed_invariants.py | OK | 0 |
| tests/unit/test_lab/test_panel_manager.py | OK | 0 |
| tests/unit/simulation/test_formula_exceptions.py | ISSUES | CAT-10 |
| tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py | ISSUES | CAT-4 |
| tests/unit/ui/screens/test_strategy_ui_tooltips.py | ISSUES | CAT-2 (downgraded) |
| tests/unit/test_screen_router.py | OK | 0 |
| tests/unit/simulation/armor_mechanics/test_damage_mechanics.py | OK | 0 |
| tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py | ISSUES | CAT-4 |
| tests/unit/ui/test_detail_panel_rendering.py | ISSUES | CAT-8 |
| tests/unit/ui/test_battle_panels_characterization.py | ISSUES | CAT-4 |
| tests/unit/strategy/services/ability_sources/test_facility.py | OK | 0 |
| tests/unit/strategy/data/test_colony_species_config.py | OK | 0 |
| tests/unit/strategy/pathfinding/conftest.py | OK | 0 |
| tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py | OK | 0 |
| tests/unit/strategy/ship_instance/test_capacity_levels.py | OK | 0 |
| tests/unit/core/resources_registry/test_loading.py | OK | 0 |
| tests/unit/core/test_registry_provider.py | OK | 0 |
| tests/unit/strategy/data/test_planet_naming.py | OK | 0 |
| tests/integration/test_fms_planet_recovery.py | OK | 0 |
| tests/unit/ai/test_ai.py | ISSUES | CAT-5 |
| tests/unit/strategy/engine/test_production_refactor.py | OK | 0 |
| tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py | OK | 0 |
| tests/unit/ai/test_ai_capabilities_cache.py | OK | 0 |
| tests/unit/test_app_create_workshop_context.py | OK | 0 |
| tests/integration/save_load/test_roundtrip_designs.py | OK | 0 |
| tests/unit/modifiers/test_propulsion_ability_bindings.py | ISSUES | CAT-4 |
| tests/unit/simulation/test_battle_runner_telemetry.py | OK | 0 |
| tests/integration/ui/test_move_order_registration.py | OK | 0 |
| tests/unit/strategy/generation/test_system_blueprints.py | OK | 0 |
| tests/unit/strategy/services/test_strategic_ability_scanner.py | OK | 0 |
| tests/unit/services/llm/test_background.py | ISSUES | CAT-7 |
| tests/unit/core/test_error_codes.py | OK | 0 |
| tests/unit/ui/screens/test_viewing_empire_anchor.py | OK | 0 |
| tests/unit/simulation/entities/test_ship_physics.py | ISSUES | CAT-10 |
| tests/projects/phase_workflow/test_lifecycle_e2e.py | OK | 0 |
| tests/unit/agent_coordination/test_codex_consult_skills.py | ISSUES | CAT-2 |
| tests/integration/simulation/test_mid_battle_reinforcement.py | OK | 0 |
| tests/unit/builder/test_builder_validation.py | OK | 0 |
| tests/unit/strategy/turn_engine/test_tick_mechanics.py | OK | 0 |
| tests/unit/simulation/entities/stat_contributors/test_typed_contributor_migration.py | OK | 0 |
| tests/integration/strategy/production/test_fleet_save_load.py | OK | 0 |
| tests/integration/replay/test_verification_uses_production_materializer.py | OK | 0 |
| tests/unit/strategy/engine/test_transfer_order.py | OK | 0 |
| tests/integration/save_load/test_load_restoration.py | OK | 0 |
| tests/unit/ui/test_fleet_list_view_model.py | OK | 0 |
| tests/unit/strategy/generation/density/test_ring.py | OK | 0 |
| tests/integration/strategy/test_fleet_navigation_consistency.py | ISSUES | CAT-1 |
| tests/unit/simulation/ship_combat_engine/test_cooldowns.py | ISSUES | CAT-10 |
| tests/unit/strategy/engine/test_typed_planet_intents.py | OK | 0 |
| tests/unit/ui/screens/test_battle_setup_state.py | OK | 0 |
| tests/unit/strategy/facade/test_facade_dispatch.py | OK | 0 |
| tests/unit/simulation/entities/test_ship_stats_golden.py | OK | 0 |
| tests/unit/strategy/engine/order_handlers/test_colonize_handler.py | OK | 0 |
| tests/unit/ai/test_target_evaluator_edge_cases.py | OK | 0 |
| tests/unit/strategy/ship_instance/test_post_container_surface.py | OK | 0 |
| tests/unit/strategy/data/test_planet_habitability_cache.py | OK | 0 |
| tests/unit/strategy/test_ship_display_formatter.py | OK | 0 |
| tests/unit/strategy/engine/test_organics_consumption_engine.py | OK | 0 |
| tests/unit/simulation/combat/test_ship_death_at_zero_hp.py | OK | 0 |
| tests/unit/strategy/consumable_management_engine/conftest.py | ISSUES | CAT-1 (downgraded) |
| tests/unit/strategy/data/test_empire_fleet_registration.py | OK | 0 |
| tests/unit/ui/services/test_ship_io_adapter.py | OK | 0 |
| tests/unit/research/research_controls/test_event_routing_and_updates.py | OK | 0 |
| tests/integration/strategy/turn_engine/test_mid_turn_invariants.py | OK | 0 |

## Context Usage Estimate
Files read: 94 / 94 (~24,487 LOC). For each file, at minimum the full file was read; for files with complex mock setups (~15 files), surrounding production code was also consulted. Estimated total context: ~35,000 lines of Python/source material read.
