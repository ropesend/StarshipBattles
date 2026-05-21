# Shard 08 — Test Audit Report

## Summary
- Shard: 08 | Files assigned: 80 | Files actually read: 80 | Total findings: 9 | Critical: 0 | Major: 3 | Minor: 6

## Findings

### tests/unit/strategy/services/test_fleet_navigation_action_timing.py
#### CAT-8: Multiple 2-level nested with patch() blocks [MINOR]
- **Location**: test_fleet_navigation_action_timing.py:66-81, 124-137, 182-195, 258-270, 301-308 | **Issue**: Five test methods each contain 2-level nested `with patch(...)` blocks (patching `find_hybrid_path` then `resolve_action_time`). The file's own docstring acknowledges this is intentional but remains a readability burden. | **Suggestion**: Extract the double-patch into a helper context manager or fixture to reduce nesting per-test. | **LOC affected**: ~60

### tests/unit/ui/services/test_ship_io.py
#### CAT-10: 7 near-identical round-trip tests [MINOR]
- **Location**: test_ship_io.py:395-541 | **Issue**: `test_round_trip_preserves_ship_name`, `_ship_class`, `_team_id`, `_color`, `_component_count`, `_movement_policy`, `_recalculates_stats` all follow the identical pattern: `ship.to_dict()` → write to `tmp_path` → read back → `Ship.from_dict(data, registries=...` → assert one property. | **Suggestion**: Parametrize into one `test_round_trip_preserves_property` with `(property_name, expected_value_extractor)` pairs. | **LOC affected**: ~150

### tests/unit/simulation/test_battle_state_serialization.py
#### CAT-12: For loops with nested assertions in test_many_ships_and_projectiles [MINOR]
- **Location**: test_battle_state_serialization.py:1348-1394 | **Issue**: `test_many_ships_and_projectiles` builds 50 ships and 100 projectiles using for loops with nested list comprehensions and assertions inside the setup. | **Suggestion**: Extract ship/projectile build loops into a helper; keep the test body to invocation + length assertions. | **LOC affected**: ~47

#### CAT-5: Function-scoped heavy fixtures [MAJOR]
- **Location**: test_battle_state_serialization.py:158-282, 620-755, 904-1006 | **Issue**: `minimal_ship_state`, `ship_state_with_components`, `destroyed_ship_state`, `retreating_ship_state`, `full_battle_state`, `battle_state_with_ships`, `full_results`, `minimal_results` are all function-scoped fixtures that construct ShipState/BattleState/BattleResults objects with 15-20+ fields each. These are immutable frozen dataclass instances — no test mutates them. | **Suggestion**: Rescope to `scope="module"` or `scope="session"` for the read-only fixtures. | **LOC affected**: ~200

### tests/unit/strategy/engine/test_turn_engine_progress_callback.py
#### CAT-6: Asserts on MagicMock call_args_list exact format [MAJOR]
- **Location**: test_turn_engine_progress_callback.py:62-63 | **Issue**: `test_progress_callback_fires_on_cadence` asserts `cb.call_args_list == expected` with the full tuple format `[((tick, TICKS_PER_TURN), {}) for tick in ...]`. This pins the internal call representation of MagicMock and will break if any slight change in call signature occurs. | **Suggestion**: Assert `cb.call_count == len(_EXPECTED_CALLBACK_TICKS)` and verify individual call args via loop, or use `cb.assert_has_calls(...)` with relaxed matchers. | **LOC affected**: 3

### tests/unit/strategy/facade/test_fleet_dto.py
#### CAT-10: Duplicate tuple-immutability tests [MINOR]
- **Location**: test_fleet_dto.py:192-269 | **Issue**: `test_collection_fields_are_immutable_tuples` (lines 192-229) and `test_from_fleet_returns_tuples` (lines 231-269) verify the same invariant: that FleetInfo's `ships`, `orders`, and `projected_path` fields are tuples. The first tests direct construction, the second tests `from_fleet()`. Both assert `isinstance(field, tuple)` on the same three fields. | **Suggestion**: Merge into one parametrized test covering both construction sources. | **LOC affected**: ~80

### tests/unit/ui/panels/test_ship_detail_panel.py
#### CAT-6: Bypasses __init__ via object.__new__ then manually sets attributes [MAJOR]
- **Location**: test_ship_detail_panel.py:131-521 | **Issue**: 16 test methods in classes `TestShipDetailPanelInit`, `TestLayerExpansion`, `TestUpdateShip`, `TestClearElements`, `TestImageScaling`, `TestProcessEvent`, `TestPanelKill` each construct the panel as `panel = ShipDetailPanel.__new__(ShipDetailPanel)` then manually set `panel.expanded_layers`, `panel.ui_elements`, `panel.layer_buttons`, etc. as dicts/lists. This tests the panel's internal state machine without exercising `__init__`, meaning an `__init__` refactor that changes attribute names breaks these silently (they set the pre-refactor names). | **Suggestion**: Use `@patch.object(ShipDetailPanel, '__init__', lambda self, *a, **kw: None)` combined with `ShipDetailPanel.__new__` or create a proper lightweight constructor. At minimum, add a comment documenting the coupling. | **LOC affected**: ~200

### tests/unit/research/research_scene/test_interaction.py
#### CAT-2: test_detect_cycles_called_during_init tests nothing real [MAJOR]
- **Location**: test_interaction.py:214-239 | **Issue**: `test_detect_cycles_called_during_init` creates `scene = MagicMock(spec=ResearchTreeScene)` — a mock of the SUT — then manually calls `mock_tree.detect_cycles()` on a separate mock tree. It never instantiates `ResearchTreeScene` or exercises any real code path. The assertion `mock_tree.detect_cycles.assert_called_once()` trivially passes because the test itself called it. | **Suggestion**: Replace with a test that instantiates the real `ResearchTreeScene` and verifies `detect_cycles()` is called as a side effect of initialization. | **LOC affected**: 25

### tests/unit/strategy/fleet_navigation/test_service_edge_cases.py
#### CAT-4: Duplicate edge case tests for zero/negative speed [MINOR]
- **Location**: test_service_edge_cases.py:414-424 | **Issue**: `test_project_path_zero_speed` and `test_project_path_negative_speed` are identical except input speed value (0.0 vs -5.0) and both assert `service.project_path(fleet, galaxy) == []`. | **Suggestion**: Parametrize into `@pytest.mark.parametrize("speed", [0.0, -5.0]) def test_project_path_invalid_speed_returns_empty`. | **LOC affected**: 11

## File Coverage Verification

| File | Lines | Read | Has Tests |
|------|-------|------|-----------|
| tests/unit/strategy/data/test_spectrum.py | 45 | Yes | 4 test funcs |
| tests/unit/strategy/engine/test_command_registry_contract.py | 494 | Yes | 16 test funcs |
| tests/unit/strategy/facade/test_population_dtos.py | 174 | Yes | 6 test funcs |
| tests/unit/strategy/data/test_facility_activation.py | 125 | Yes | 8 test funcs |
| tests/unit/strategy/data/test_build_context.py | 193 | Yes | 16 test funcs |
| tests/unit/simulation/combat/test_damage_calculator_events.py | 204 | Yes | 9 test funcs |
| tests/unit/strategy/engine/test_turn_engine_progress_callback.py | 111 | Yes | 5 test funcs |
| tests/unit/ui/panels/test_ship_stats_renderer.py | 390 | Yes | 20 test funcs |
| tests/unit/strategy/data/test_production_resource_source_ratchet.py | 156 | Yes | 5 test funcs |
| tests/unit/strategy/services/test_fleet_navigation_action_timing.py | 594 | Yes | 12 test funcs |
| tests/integration/ui/test_strategy_turn_error_boundary.py | 445 | Yes | 9 test funcs |
| tests/unit/ui/services/test_ship_io.py | 1210 | Yes | 35 test funcs |
| tests/unit/ui/widgets/test_preference_row.py | 423 | Yes | 20 test funcs |
| tests/integration/fleet_combat/conftest.py | 109 | Yes | fixtures only |
| tests/unit/strategy/fleet_navigation/test_service_edge_cases.py | 489 | Yes | 24 test funcs |
| tests/unit/core/math_utils/test_vector2_geometry.py | 276 | Yes | 21 test funcs |
| tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py | 174 | Yes | 10 test funcs |
| tests/unit/strategy/data/test_species_population_characterization.py | 81 | Yes | 8 test funcs |
| tests/unit/strategy/data/test_fleet_consumable_aggregator.py | 893 | Yes | 37 test funcs |
| tests/unit/ui/screens/test_menu_scene.py | 250 | Yes | 13 test funcs |
| tests/unit/core/test_bug_reproduction.py | 8 | Yes | 1 test func |
| tests/unit/simulation/components/test_component_loader.py | 234 | Yes | 12 test funcs |
| tests/unit/strategy/galaxy/test_star_system_validation.py | 150 | Yes | 8 test funcs |
| tests/unit/strategy/engine/test_order_persistence_from_metadata.py | 262 | Yes | 11 test funcs |
| tests/unit/strategy/engine/test_population_engine.py | 692 | Yes | 24 test funcs |
| tests/unit/simulation/systems/test_tactical_mine_resolver.py | 436 | Yes | 11 test funcs |
| tests/unit/ui/components/filters/test_tri_state_widget.py | 132 | Yes | 9 test funcs |
| tests/integration/gameplay_loop/conftest.py | 155 | Yes | fixtures only |
| tests/fixtures/test_race_setup_ui_builders.py | 90 | Yes | 3 test funcs |
| tests/unit/ui/screens/test_strategy_superweapons.py | 592 | Yes | 21 test funcs |
| tests/unit/ui/widgets/test_scrollable_json_panel.py | 368 | Yes | 17 test funcs |
| tests/unit/strategy/services/ability_sources/test_storm.py | 106 | Yes | 11 test funcs |
| tests/integration/replay/test_combat_lab_verification.py | 250 | Yes | 2 test funcs |
| tests/unit/quickstart/test_quickstart_builder.py | 444 | Yes | 27 test funcs |
| tests/unit/core/test_config.py | 72 | Yes | 7 test funcs |
| tests/integration/strategy/test_path_projection.py | 90 | Yes | 2 test funcs |
| tests/unit/entities/test_abilities.py | 257 | Yes | 11 test funcs |
| tests/unit/strategy/facade/test_fleet_dto.py | 633 | Yes | 23 test funcs |
| tests/unit/ui/test_ship_theme_logic.py | 265 | Yes | 15 test funcs |
| tests/unit/ui/panels/test_ship_detail_panel.py | 1051 | Yes | 39 test funcs |
| tests/unit/strategy/consumable_management_engine/test_consumption.py | 97 | Yes | 7 test funcs |
| tests/integration/fleet_combat/test_component_destruction_cascade.py | 447 | Yes | 14 test funcs |
| tests/unit/simulation/test_battle_state_serialization.py | 1394 | Yes | 42 test funcs |
| tests/unit/strategy/test_advanced_fleet_orders.py | 368 | Yes | 6 test funcs |
| tests/integration/test_make_minimal_spec_smoke.py | 77 | Yes | 2 test funcs |
| tests/integration/save_load/test_live_verification.py | 95 | Yes | 9 test funcs |
| tests/integration/strategy/test_replay_capture_e2e.py | 588 | Yes | 9 test funcs |
| tests/unit/modifiers/test_crew_required_mass_scaling.py | 122 | Yes | 10 test funcs |
| tests/unit/ai/test_ai_controller_edge_cases.py | 252 | Yes | 9 test funcs |
| tests/unit/builder/test_builder_io_integration.py | 184 | Yes | 6 test funcs |
| tests/unit/simulation/components/abilities/test_static_value_ability.py | 221 | Yes | 21 test funcs |
| tests/unit/simulation/services/test_vehicle_design_service.py | 1056 | Yes | 39 test funcs |
| tests/unit/strategy/engine/test_issuer_adapter.py | 297 | Yes | 12 test funcs |
| tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py | 130 | Yes | 6 test funcs |
| tests/repro_issues/test_bug_13_weapons_report.py | 154 | Yes | 7 test funcs |
| tests/unit/core/test_registry_manager_reload.py | 205 | Yes | 14 test funcs |
| tests/integration/ui/test_planet_complexes_list.py | 331 | Yes | 7 test funcs |
| tests/unit/strategy/fleets/test_task_force_formation.py | 71 | Yes | 6 test funcs |
| tests/unit/simulation/components/abilities/test_planetary_fleet_components.py | 280 | Yes | 19 test funcs |
| tests/unit/strategy/combat/test_satellite_group_combat_join.py | 98 | Yes | 2 test funcs |
| tests/unit/research/research_scene/test_interaction.py | 259 | Yes | 8 test funcs |
| tests/unit/simulation/components/test_component_resource_manager.py | 657 | Yes | 43 test funcs |
| tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py | 248 | Yes | 16 test funcs |
| tests/unit/ui/services/image/test_defaults.py | 27 | Yes | 3 test funcs |
| tests/unit/modifiers/test_modifier_effect.py | 158 | Yes | 8 test funcs |
| tests/unit/strategy/engine/order_handlers/test_recover_satellites_handler.py | 261 | Yes | 9 test funcs |
| tests/unit/workshop/test_workshop_context.py | 177 | Yes | 19 test funcs |
| tests/unit/strategy/engine/test_planet_modifier_effect_engine.py | 239 | Yes | 13 test funcs |
| tests/unit/simulation/combat/test_fleet_aura_extended.py | 441 | Yes | 18 test funcs |
| tests/unit/strategy/test_ship_cargo_manager.py | 156 | Yes | 16 test funcs |
| tests/unit/simulation/battle_runner/test_spec_component_validation.py | 240 | Yes | 6 test funcs |
| tests/unit/strategy/engine/commands/test_order_metadata_view.py | 313 | Yes | 11 test funcs |
| tests/unit/modifiers/test_projectile_weapon_bindings.py | 71 | Yes | 4 test funcs |
| tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py | 137 | Yes | 5 test funcs |
| tests/unit/ui/screens/test_battle_state_viewer.py | 143 | Yes | 5 test funcs |
| tests/unit/services/llm/test_types.py | 154 | Yes | 12 test funcs |
| tests/unit/core/test_service_injection.py | 294 | Yes | 10 test funcs |
| tests/unit/strategy/data/test_design_role.py | 314 | Yes | 17 test funcs |
| tests/unit/strategy/generation/density/test_geometric.py | 106 | Yes | 10 test funcs |
| tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py | 359 | Yes | 8 test funcs |

## Context Usage Estimate
~60K tokens for reading all 80 files (~24,344 LOC). Report writing: ~2K tokens. Total: ~62K tokens.
