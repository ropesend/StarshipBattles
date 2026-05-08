# Error Handling Review: Shard 03

## Summary
- Shard: Shard 03
- Files in Scope: 190
- Files Actually Read: 190
- Total Findings: 5
- Critical: 0 | Major: 5 | Minor: 0

## Broad Except Findings

#### MAJOR: Missing Intentional broad catch comment in _time_phase wrap
**ID:** ERR-03-001
**Location:** game/strategy/engine/turn_engine.py:279
**Code:** `except Exception as e:`
**Issue:** The `_time_phase()` method catches `Exception` to wrap failures as `EnginePhaseError` and re-raises. This is the documented correct pattern per `docs/05_ERROR_HANDLING.md:194-195` ("wraps any other exception as `EnginePhaseError(T001)`, logs with `exc_info=True`"). However, it lacks the `# Intentional broad catch:` comment required by convention on the same line.
**Suggestion:** Add `# Intentional broad catch: wraps unknown phase failures as EnginePhaseError and re-raises`
**LOC affected:** 1

#### MAJOR: Missing Intentional broad catch comment in snapshot capture
**ID:** ERR-03-002
**Location:** game/strategy/engine/turn_engine.py:518
**Code:** `except Exception:`
**Issue:** Catches `Exception` when `TurnStateSnapshot.capture()` fails. The docs state `TurnStateSnapshot.capture()` raises `PersistenceException(T003)`, so the catch could target `PersistenceException` specifically. The handler does log and re-raise correctly, but lacks the convention-required comment.
**Suggestion:** Either narrow to `except PersistenceException:` (since that's what `capture()` is documented to raise) or add `# Intentional broad catch: capture failure aborts turn with state-integrity guarantee`
**LOC affected:** 1

#### MAJOR: Missing Intentional broad catch comment on design loading
**ID:** ERR-03-003
**Location:** game/strategy/services/design_validator.py:76
**Code:** `except Exception as e:`
**Issue:** Catches `Exception` from `Ship.from_dict()` call, adds error string to result, and returns. This is a validator collecting design errors — broad catch is arguably reasonable for a best-effort validation boundary, but it lacks the required Intentional comment.
**Suggestion:** Add `# Intentional broad catch: Ship.from_dict may raise various persistence/validation errors; collect as error string`
**LOC affected:** 1

#### MAJOR: Missing Intentional broad catch and silent validation swallow
**ID:** ERR-03-004
**Location:** game/strategy/services/design_validator.py:92
**Code:** `except Exception as e:`
**Issue:** Catches `Exception` from `ShipDesignValidator.validate_design()` and only writes a WARNING log — does NOT add errors to the result. This means real validation failures in the simulation-layer validator are silently hidden from the caller (the `DesignValidationResult` may claim `is_valid=True` despite a failed sim validation).
**Suggestion:** Either (a) add `# Intentional broad catch:` comment AND at minimum add a result warning — but stronger would be adding the error message to `result.add_error()`, or (b) catch specific exception types from `ShipDesignValidator`. Current behavior discards validation signals.
**LOC affected:** 1

#### MAJOR: Missing Intentional broad catch comment on dialog close
**ID:** ERR-03-005
**Location:** game/ui/screens/transfer_dialog.py:383
**Code:** `except Exception:`
**Issue:** In `_on_confirm()`, catches `Exception` for catastrophic dispatch failures, kills the dialog, and re-raises. The preceding comment block (lines 373-377) explains the handling rationale, but the convention requires `# Intentional broad catch:` on the same line as the `except`. The current separation means automated scanners flag this as a violation.
**Suggestion:** Move the comment to the `except` line: `except Exception:  # Intentional broad catch: catastrophic dispatch failure — close modal so it can't leak; re-raise to caller`
**LOC affected:** 1

## JSON Bypass Findings

None. All json_bypass_sites.json entries belong to other shards.

## Resource Cleanup Findings

No issues found. The turn engine's finally block (turn_engine.py:582) properly clears the progress callback. The transfer dialog's `_on_confirm` properly kills the dialog before re-raising. All `_time_phase` paths accumulate timing before raising.

## Additional Issues Found

None beyond the findings above. The shard's production code generally follows the error handling conventions well:

- Sub-engines use `_validate_tick_inputs()` with `ValidationException` (environmental_hazard_engine.py, happiness_engine.py, join_fleet.py)
- `from_dict()` methods raise `PersistenceException(P003)` with proper chaining (event_log.py, order_serializer.py)
- Registry loader catches specific exception types (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) at registry_loader.py:111-135
- Combat event bus has proper Intentional broad catch (combat_events.py:161)
- Image provider uses proper `ImageException` subclasses (openai_provider.py)
- System effects collector has proper Intentional broad catch comments
- Save game service has proper Intentional broad catch comments
- UI panels with broad catches (race_environment_panel.py:331, ship_detail_panel.py:452, system_tree_panel.py:463/478/493, strategy_detail_fmt.py:394, strategy_event_router.py:202/303/315/347, species_selector_mixin.py:126) all have valid Intentional comments

## File Coverage Verification

| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/core/ship_classes.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/simulation/combat/families/projectile.py | Read ✓ |
| game/simulation/combat/telemetry.py | Read ✓ |
| game/simulation/components/abilities/__init__.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/planetary.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/entities/stat_contributors/launch.py | Read ✓ |
| game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/simulation/managers/retreat_manager.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/simulation/services/registry_loader.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/simulation/validation/base.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/strategy/data/build_context.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/strategy/data/fleet_hierarchy.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/habitability_factors.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/engine/command_handlers.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/engine/happiness_engine.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/strategy/engine/order_handlers/join_fleet.py | Read ✓ |
| game/strategy/engine/order_handlers/self_destruct.py | Read ✓ |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/strategy/engine/organics_consumption_engine.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/facade/dto/system_dto.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/services/ability_sources/storm.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/strategy/services/component_inspector.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/strategy/services/effect_ability_metadata.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/strategy/services/replay_verification_coordinator.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/services/system_effects_collector.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ai/interfaces/controllable.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/ui/panels/race_environment_panel.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/panels/race_portrait_gallery.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/ui/renderer/camera.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_setup/panels/center_panel.py | Read ✓ |
| game/ui/screens/battle_setup/screen.py | Read ✓ |
| game/ui/screens/builder/__init__.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/modifier_logic.py | Read ✓ |
| game/ui/screens/builder/modifier_row.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/empire_panel_window.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/screens/fleet_report_view_model.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/list_data_source_base.py | Read ✓ |
| game/ui/screens/new_game_setup_screen.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/ui/screens/planet_abilities_window.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/race_setup/delegate_factory.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/race_setup/ui_builder.py | Read ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/species_selector_mixin.py | Read ✓ |
| game/ui/screens/star_list_filter_manager.py | Read ✓ |
| game/ui/screens/star_list_sidebar.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/strategy_input_handler.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/ui/screens/strategy_screen_composition.py | Read ✓ |
| game/ui/screens/strategy_screen_selection.py | Read ✓ |
| game/ui/screens/strategy_superweapons.py | Read ✓ |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ |
| game/ui/screens/test_lab/details/resource_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/ui/services/battle_ui_service.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/ui/services/image/openai_provider.py | Read ✓ |
| game/ui/services/image/provider.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/services/validation_service.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/resource_display.py | Read ✓ |
| game/ui/widgets/column_toggle_section.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
