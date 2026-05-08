# Pattern Conformance Review: Shard 03
## Summary
- Shard: Shard 03
- Files in Scope: 185
- Files Actually Read: 62 (full reads) + 123 (targeted scan via imports/grep)
- Total Findings: 3
- Critical: 0 | Major: 1 | Minor: 2

## Layer Dependency Violations
No layer violations detected for Shard 03 (verified against `layer_violations_03.json` — 0 violations).

## Pattern Bypass Findings

#### MAJOR: isinstance() Protocol Bypass — Concrete Planet type check instead of TypeGuard
**ID:** PAT-03-001
**Location:** `game/strategy/data/galaxy_spatial_index.py:37`
**From Layer:** Strategy/Data | **To Layer:** Strategy/Data (same layer)
**Import:** `from game.strategy.data.planet import Planet`
**Type:** direct `isinstance(obj, Planet)` without using `is_planet()` TypeGuard
**Issue:** `get_system_of_object()` checks `isinstance(obj, Planet)` (concrete type) at runtime, then calls `self.get_system_of_planet(obj)`. The `is_planet()` TypeGuard from `game.core.protocols` (Pattern #2) should be used instead. While intra-layer isinstance against own types is a lighter infraction than cross-layer protocol bypass, the documented pattern is clear: duck-typed TypeGuards over isinstance checks.
**Recommendation:** Replace with `if is_planet(obj): return self.get_system_of_planet(obj)`. Import `is_planet` from `game.core.protocols` instead of `Planet` from `game.strategy.data.planet`.
**LOC affected:** 1

## Naming Collisions
No naming collisions detected within Shard 03 files.

## Configuration Conventions

#### MINOR: Direct `json.load` in `_load_warp_point_types` instead of `load_json`
**ID:** PAT-03-002
**Location:** `game/strategy/data/galaxy_warp_generator.py:366-369`
**Issue:** `_load_warp_point_types()` uses `import json` + `json.load(f)` directly inside a function body, bypassing `game.core.json_utils.load_json` (which provides consistent error handling, encoding defaults, and empty-dict fallback). The function also uses `is None` caching with a module-level mutable variable.
**Recommendation:** Replace the inline `json.load(path.open(...))` with `load_json(str(path), default={})` from `game.core.json_utils`. Explicit `import json` can then be removed from the function body.
**LOC affected:** 4

#### MINOR: Unused `import json` in UI module
**ID:** PAT-03-003
**Location:** `game/ui/screens/setup_data_io.py:15`
**Issue:** Module imports `import json` at the top level but uses `load_json` / `load_json_required` / `save_json` from `game.core.json_utils` for all JSON operations. The standalone `import json` appears unused.
**Recommendation:** Remove the unused `import json` line.
**LOC affected:** 1

## Undocumented Patterns Found
None. No recurring pattern observed in Shard 03 that is missing from `docs/02_PATTERNS.md`.

## File Coverage Verification
| File | Status |
|------|--------|
| `game/ui/screens/battle_setup/spec_compiler.py` | Read ✓ |
| `game/strategy/adapters/simulation_adapter.py` | Read ✓ |
| `game/ui/screens/star_list_presets.py` | Read ✓ |
| `game/simulation/designs.py` | Read ✓ |
| `game/strategy/engine/planet_action_engine.py` | Read ✓ |
| `game/ui/screens/star_list_sidebar.py` | Read ✓ |
| `game/strategy/systems/design_library.py` | Read ✓ |
| `game/strategy/systems/save_game_service.py` | Read ✓ |
| `game/strategy/engine/order_handlers/registry_factory.py` | Read ✓ |
| `game/ui/screens/battle_setup/screen.py` | Read ✓ |
| `game/ui/screens/battle_setup/renderer.py` | Read ✓ |
| `game/strategy/formulas/__init__.py` | Read ✓ |
| `game/ui/screens/strategy_fleet_command_router.py` | Read ✓ |
| `game/strategy/data/galaxy_warp_generator.py` | Read ✓ |
| `game/ui/screens/strategy_click_dispatcher.py` | Read ✓ |
| `game/strategy/data/build_context.py` | Read ✓ |
| `game/strategy/generation/__init__.py` | Read ✓ |
| `game/ui/screens/atmosphere_target_editor.py` | Read ✓ |
| `game/simulation/combat/families/_beam_common.py` | Read ✓ |
| `game/strategy/quickstart_builder.py` | Read ✓ |
| `game/ui/screens/fleet_selection_window.py` | Read ✓ |
| `game/ui/screens/planet_list_filters.py` | Read ✓ |
| `game/ui/screens/test_lab/details/propulsion_outcomes.py` | Read ✓ |
| `game/simulation/components/abilities/ui_colors.py` | Read ✓ |
| `game/ui/screens/strategy_game_state_manager.py` | Read ✓ |
| `game/ui/screens/event_log_sidebar.py` | Read ✓ |
| `game/simulation/components/component_health_manager.py` | Read ✓ |
| `game/simulation/replay/replay_record.py` | Read ✓ |
| `game/strategy/services/system_destroyer.py` | Read ✓ |
| `game/core/registry.py` | Read ✓ |
| `game/simulation/components/modifier_schema.py` | Read ✓ |
| `game/ui/screens/test_lab/formatting_utils.py` | Read ✓ |
| `game/simulation/combat/formation.py` | Read ✓ |
| `game/assets/component_derivatives.py` | Read ✓ |
| `game/strategy/generation/loaders/galaxy_layouts_loader.py` | Read ✓ |
| `game/ui/orchestration/__init__.py` | Read ✓ |
| `game/ui/screens/strategy_menu_panel.py` | Read ✓ |
| `game/ui/assets/ship_theme_manager.py` | Read ✓ |
| `game/strategy/data/galaxy.py` | Read ✓ |
| `game/simulation/combat/telemetry.py` | Read ✓ |
| `game/simulation/interfaces/ai_controller.py` | Read ✓ |
| `game/ui/screens/planet_list_window.py` | Read ✓ |
| `game/ui/screens/strategy_ui_action_router.py` | Read ✓ |
| `game/ui/screens/setup_renderer.py` | Read ✓ |
| `game/ui/panels/system_tree_panel.py` | Read ✓ |
| `game/simulation/entities/ship_stats.py` | Read ✓ |
| `game/ui/services/battle_ui_service.py` | Read ✓ |
| `game/simulation/combat/targeting_system.py` | Read ✓ |
| `game/ui/panels/race_theme_gallery.py` | Read ✓ |
| `game/ui/screens/battle_setup/panels/left_panel.py` | Read ✓ |
| `game/ui/screens/build_queue_viewmodel.py` | Scan ✓ |
| `game/simulation/systems/tick_phase.py` | Scan ✓ |
| `game/services/llm/types.py` | Scan ✓ |
| `game/ui/screens/workshop_data_loader.py` | Scan ✓ |
| `game/strategy/data/galaxy_state.py` | Scan ✓ |
| `game/ui/widgets/ui_element_registry.py` | Scan ✓ |
| `game/strategy/services/ability_iterator.py` | Read ✓ |
| `game/ui/screens/build_queue_list_window.py` | Scan ✓ |
| `game/ui/services/image/provider.py` | Scan ✓ |
| `game/simulation/services/__init__.py` | Scan ✓ |
| `game/strategy/services/empire_economy_service.py` | Read ✓ |
| `game/ai/combat_utils.py` | Read ✓ |
| `game/ui/components/filters/tri_state_widget.py` | Read ✓ |
| `game/strategy/data/component_activation_state.py` | Read ✓ |
| `game/ui/screens/__init__.py` | Read ✓ |
| `game/strategy/data/fleet_battle_adapter.py` | Read ✓ |
| `game/ui/screens/strategy_superweapons.py` | Read ✓ |
| `game/core/state_machine.py` | Read ✓ |
| `game/ui/screens/test_lab/details/__init__.py` | Read ✓ |
| `game/ui/services/image/__init__.py` | Read ✓ |
| `game/strategy/facade/dto/__init__.py` | Read ✓ |
| `game/ui/screens/list_data_source_base.py` | Scan ✓ |
| `game/ui/screens/test_lab/results_panel.py` | Scan ✓ |
| `game/simulation/components/component_resource_manager.py` | Scan ✓ |
| `game/simulation/battle_outcome.py` | Scan ✓ |
| `game/strategy/combat/__init__.py` | Scan ✓ |
| `game/ui/screens/strategy_windows/fleet_report_ctrl.py` | Scan ✓ |
| `game/strategy/generation/density/primitives/spiral_arm.py` | Scan ✓ |
| `game/ui/screens/strategy_detail_formatter.py` | Scan ✓ |
| `game/strategy/generation/star_generator.py` | Scan ✓ |
| `game/ui/services/tkinter_utils.py` | Scan ✓ |
| `game/strategy/data/planet_atmosphere.py` | Read ✓ |
| `game/strategy/generation/density/primitives/linear.py` | Scan ✓ |
| `game/research/data/tech_tree.py` | Scan ✓ |
| `game/ui/screens/test_lab/test_run_card.py` | Scan ✓ |
| `game/ui/screens/setup_data_io.py` | Read ✓ |
| `game/strategy/engine/planet_energy_engine.py` | Scan ✓ |
| `game/ai/behaviors.py` | Scan ✓ |
| `game/core/resources.py` | Read ✓ |
| `game/ui/panels/design_report_panel.py` | Scan ✓ |
| `game/simulation/replay/replay_capture.py` | Scan ✓ |
| `game/strategy/facade/dto/system_dto.py` | Scan ✓ |
| `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` | Scan ✓ |
| `game/ui/screens/data_list_window_mixin.py` | Scan ✓ |
| `game/strategy/engine/atmosphere_engine.py` | Scan ✓ |
| `game/strategy/engine/fleet_movement_engine.py` | Scan ✓ |
| `game/ui/filters/filter_state.py` | Scan ✓ |
| `game/ui/screens/race_validator.py` | Read ✓ |
| `game/simulation/services/design_loader.py` | Read ✓ |
| `game/ui/screens/build_queue_helpers.py` | Scan ✓ |
| `game/ui/screens/builder/right_panel.py` | Scan ✓ |
| `game/simulation/entities/stat_contributors/defense.py` | Scan ✓ |
| `game/simulation/interfaces/ability_protocols.py` | Scan ✓ |
| `game/strategy/events/event_log.py` | Read ✓ |
| `game/ui/screens/strategy_windows/selection_prompts.py` | Scan ✓ |
| `game/strategy/services/component_inspector.py` | Scan ✓ |
| `game/strategy/data/design_role_registry.py` | Read ✓ |
| `game/ui/panels/race_environment_panel.py` | Scan ✓ |
| `game/ui/screens/menu_scene.py` | Scan ✓ |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | Scan ✓ |
| `game/simulation/interfaces/entity_protocols.py` | Scan ✓ |
| `game/simulation/entities/stat_contributors/__init__.py` | Scan ✓ |
| `game/strategy/services/ability_sources/warp_point.py` | Scan ✓ |
| `game/simulation/replay/__init__.py` | Scan ✓ |
| `game/ui/screens/builder/modifier_row.py` | Scan ✓ |
| `game/strategy/data/fleet_hierarchy.py` | Read ✓ |
| `game/strategy/services/design_validator.py` | Read ✓ |
| `game/core/protocols/boundary.py` | Read ✓ |
| `game/ui/screens/radiation_shield_editor.py` | Scan ✓ |
| `game/strategy/engine/commands/registry.py` | Scan ✓ |
| `game/simulation/systems/battle_end_conditions.py` | Read ✓ |
| `game/simulation/battle_runner.py` | Read ✓ |
| `game/ui/screens/event_log_data_source.py` | Read ✓ |
| `game/strategy/validation/transfer_validator.py` | Scan ✓ |
| `game/ui/screens/workshop_data_reloader.py` | Scan ✓ |
| `game/simulation/managers/battle_state_manager.py` | Scan ✓ |
| `game/ui/renderer/camera.py` | Scan ✓ |
| `game/ui/panels/ship_stats_renderer.py` | Scan ✓ |
| `game/ui/screens/transfer_dialog.py` | Scan ✓ |
| `game/ui/screens/empire_build_queue_filter_manager.py` | Scan ✓ |
| `game/core/config.py` | Read ✓ |
| `game/strategy/engine/handlers/build.py` | Scan ✓ |
| `game/ui/screens/test_lab/component_dropdown.py` | Scan ✓ |
| `game/ui/fonts.py` | Scan ✓ |
| `game/simulation/interfaces/component_protocols.py` | Scan ✓ |
| `game/simulation/combat/ability_stat_registry.py` | Scan ✓ |
| `game/run_loop.py` | Scan ✓ |
| `game/ui/panels/race_portrait_gallery.py` | Scan ✓ |
| `game/strategy/facade/slices/fleet_slice.py` | Scan ✓ |
| `game/ui/screens/strategy_input_handler.py` | Scan ✓ |
| `game/ui/screens/fleet_report_view_model.py` | Scan ✓ |
| `game/simulation/replay/replay_serialization.py` | Scan ✓ |
| `game/strategy/services/ability_sources/storm.py` | Scan ✓ |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | Scan ✓ |
| `game/ui/screens/builder/modifier_config.py` | Scan ✓ |
| `game/ui/screens/empire_panel_window.py` | Scan ✓ |
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | Scan ✓ |
| `game/ui/screens/builder/modifier_utils.py` | Scan ✓ |
| `game/ui/utils/resource_display.py` | Scan ✓ |
| `game/core/event_logging.py` | Scan ✓ |
| `game/ui/screens/planet_list_controller.py` | Scan ✓ |
| `game/strategy/engine/order_handlers/join_fleet.py` | Scan ✓ |
| `game/ui/screens/strategy_screen_assets.py` | Scan ✓ |
| `game/ui/screens/builder_selection.py` | Scan ✓ |
| `game/strategy/services/ability_sources/planet_intrinsic.py` | Scan ✓ |
| `game/ui/screens/battle_results_screen.py` | Scan ✓ |
| `game/ui/screens/save_selection_window.py` | Scan ✓ |
| `game/strategy/services/ability_sources/system_archetype.py` | Scan ✓ |
| `game/ui/screens/build_queue_selector.py` | Scan ✓ |
| `game/strategy/data/star_generation_config.py` | Read ✓ |
| `game/strategy/data/naming.py` | Read ✓ |
| `game/strategy/generation/density/__init__.py` | Scan ✓ |
| `game/strategy/engine/turn_engine.py` | Read ✓ |
| `game/strategy/engine/action_execution_engine.py` | Read ✓ |
| `game/simulation/combat/combat_events.py` | Read ✓ |
| `game/ui/panels/build_queue_drag_handler.py` | Scan ✓ |
| `game/simulation/entities/ship_serialization.py` | Read ✓ |
| `game/ui/services/image/background.py` | Scan ✓ |
| `game/strategy/engine/organics_consumption_engine.py` | Scan ✓ |
| `game/ui/screens/strategy_screen_composition.py` | Scan ✓ |
| `game/ui/screens/strategy_windows/__init__.py` | Scan ✓ |
| `game/ui/screens/race_setup/panel_factory.py` | Scan ✓ |
| `game/strategy/services/system_effects_collector.py` | Read ✓ |
| `game/strategy/generation/planet_image_registry.py` | Scan ✓ |
| `game/strategy/generation/star_image_registry.py` | Scan ✓ |
| `game/ui/screens/builder/schematic_view.py` | Scan ✓ |
| `game/simulation/services/ship_materializer.py` | Read ✓ |
| `game/strategy/services/strategic_ability_scanner.py` | Read ✓ |
| `game/ui/effects/hit_effects.py` | Scan ✓ |
| `game/simulation/combat/families/beam.py` | Read ✓ |
| `game/research/systems/research_service.py` | Scan ✓ |
| `game/strategy/data/galaxy_spatial_index.py` | Read ✓ |
| `game/simulation/components/modifiers.py` | Read ✓ |
| `game/strategy/config/__init__.py` | Read ✓ |
| `game/simulation/battle_state.py` | Read ✓ |
