# Deep Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 172
- Files Actually Read: 172
- Total Findings: 13
- Critical: 1 | Product Decision: 3 | Major: 0 | Minor: 3 | Info: 6

## Dead Code Findings
#### CRITICAL: Dead function `_extract_weapon_summaries` in battle_runner.py
**ID:** DEEP-02-001
**Location:** game/simulation/battle_runner.py:647-671
**Issue:** `_extract_weapon_summaries()` is defined with full logic (iterating ship layers, collecting WeaponSummary), but is never called from any production code. The `WeaponSummaryAggregator` in telemetry.py handles this same concern. The function was likely written during PROJ-269 Phase 2 weapon-stats extraction but was superseded by the telemetry aggregator path.
**Estimated LOC:** 25
**Tests reference?** No
**Docs reference?** No
**Recommendation:** Delete the function. The telemetry aggregator in `_attach_telemetry` / `extract_outcome` already handles weapon-summary collection.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:

| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-02-002 | `create_brick()` in game/simulation/designs.py:11-36 | 26 | tests/unit/builder/test_designs.py:7,13-42,77 | None | None | Wire into a quickstart/battle-setup scenario or delete tests + function |
| DEEP-02-003 | `create_interceptor()` in game/simulation/designs.py:39-68 | 29 | tests/unit/builder/test_designs.py:7,47-78 | None | None | Wire into a quickstart/battle-setup scenario or delete tests + function |
| DEEP-02-004 | `BattleController.load_state()` in game/simulation/battle_controller.py:613-695 | 82 | tests/backfill — has zero production callers (grep-verified, per own docstring comment at line 614) | None | None | The docstring itself confirms zero production callers. Wire it or delete it. Saves are disposable per CLAUDE.md |

## Internal Duplication Findings
(No significant internal duplication >30 lines found in this shard.)

## Fragmentation Findings
(No significant fragmentation issues found. Files are well-organized with clear single responsibilities.)

## Quality / LOC Reduction Findings
#### MINOR: `game/strategy/config/__init__.py` and `game/strategy/data/__init__.py` are empty
**ID:** DEEP-02-005
**Location:** game/strategy/config/__init__.py:0, game/strategy/data/__init__.py:0
**Issue:** Empty `__init__.py` files serve as namespace markers (Python 3.3+) but can be deleted since implicit namespace packages are supported.
**Estimated LOC:** 0 (both empty)
**Recommendation:** Delete both empty `__init__.py` files.

#### MINOR: `game/ui/renderer/__init__.py` is empty
**ID:** DEEP-02-006
**Location:** game/ui/renderer/__init__.py:0
**Issue:** Empty file with no content.
**Estimated LOC:** 0
**Recommendation:** Delete the empty `__init__.py`.

#### MINOR: `game/ui/orchestration/__init__.py` contains only a docstring
**ID:** DEEP-02-007
**Location:** game/ui/orchestration/__init__.py:1
**Issue:** The file contains only a module-level docstring with no imports or exports. No other files in the shard reference this module.
**Estimated LOC:** 1
**Recommendation:** Verify the `orchestration` subpackage is still needed; if no other shard uses it, consider deletion.

#### INFO: `Component.__init__` unused `os` import in `game/ui/screens/builder/detail_panel.py`
**ID:** DEEP-02-008
**Location:** game/ui/screens/builder/detail_panel.py:15
**Issue:** `import os` is already imported at line 15 but `os` is used via `os.path.join` and `os.path.exists`. The import is used — no issue. (Self-corrected during review.)

#### INFO: `LayerType` not imported from core.constants in detail_panel.py but used in signature name only
**ID:** DEEP-02-009
**Location:** game/ui/screens/builder/detail_panel.py
**Issue:** LayerType is imported at line 17 but used only in the module-level docstring comment at line 11. The import is unused at runtime.
**Estimated LOC:** 1
**Recommendation:** Remove the unused `LayerType` import.

#### INFO: Verbose logging in battle_panels.py ship detail draw methods calls `UIConfig` many times
**ID:** DEEP-02-010
**Location:** game/ui/panels/battle_panels.py:197-225
**Issue:** `draw_ship_details` delegates to individual `draw_ship_*` functions but has comments describing the delegation pattern — this is fine architecture, no LOC to reduce.

#### INFO: `game/simulation/combat/__init__.py` docstring references deleted `BattleModeHandler`
**ID:** DEEP-02-011
**Location:** game/simulation/combat/__init__.py:8-10
**Issue:** The module docstring mentions that `BattleModeHandler` was deleted in PROJ-269 Phase 6. This is historical documentation, not dead code, but the docstring should note `WeaponFiringSystem` is still an active export.
**Estimated LOC:** 0
**Recommendation:** No action needed — docstring is accurate historical context.

#### INFO: `game/core/patterns/layer_iterator.py` duplication of layer format handling
**ID:** DEEP-02-012
**Location:** game/core/patterns/layer_iterator.py:42-93
**Issue:** `iter_components()`, `iter_layers_and_components()`, and `iter_keyed_components()` each contain their own layer-format dispatch logic (list vs dict format). The three iterators replicate the same `isinstance(layer_data, list)` / `isinstance(layer_data, dict)` branches.
**Estimated LOC:** Could save ~15 LOC by extracting a shared `_iter_component_entries()` helper.
**Recommendation:** Refactor into a shared private helper — low priority, ~15 LOC savings.

#### INFO: `game/strategy/engine/order_processor.py` long `execute_action_order` method
**ID:** DEEP-02-013
**Location:** game/strategy/engine/order_processor.py:655-732
**Issue:** `execute_action_order()` uses a dict-of-lambdas for superweapon dispatch (lines 706-725). While clean, the overall method is 78 lines with multiple `if` branches for COLONIZE, TRANSFER, and superweapon routing. A handler-registry pattern like the command handler system would be more consistent.
**Estimated LOC:** Method is 78 lines — approaching the 50-line soft target per conventions.
**Recommendation:** Consider extracting superweapon dispatch to a per-order-type registry. Low priority.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/__init__.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ai/interfaces/controllable.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/event_logging.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/research/data/research_tracker.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/simulation/battle_runner.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/ability_stat_registry.py | Read ✓ |
| game/simulation/combat/boundary.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/simulation/components/abilities/ui_colors.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/simulation/entities/ship_serialization.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/simulation/services/vehicle_design_service.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/config/__init__.py | Read ✓ |
| game/strategy/config/economy_config.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/data/fleet.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/strategy/data/habitability_factors.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/strategy/data/planet_atmosphere.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/strategy/data/squadron.py | Read ✓ |
| game/strategy/engine/construction_forecast.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/happiness_engine.py | Read ✓ |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/strategy/engine/organics_consumption_engine.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/strategy/engine/superweapon_command_handlers.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/strategy/facade/dto/empire_dto.py | Read ✓ |
| game/strategy/facade/dto/system_dto.py | Read ✓ |
| game/strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/formulas/__init__.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/strategy/generation/density/primitives/ring.py | Read ✓ |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read ✓ |
| game/strategy/services/ability_sources/storm.py | Read ✓ |
| game/strategy/services/ability_sources/system_archetype.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/strategy/services/empire_economy_service.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/strategy/services/modifier_resolver.py | Read ✓ |
| game/strategy/services/system_effects_collector.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/ui/fonts.py | Read ✓ |
| game/ui/orchestration/__init__.py | Read ✓ |
| game/ui/panels/battle_panels.py | Read ✓ |
| game/ui/panels/build_queue_portraits.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/panels/race_description_panel.py | Read ✓ |
| game/ui/panels/race_portrait_gallery.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/panels/center_panel.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/ui/screens/battle_setup_state.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/builder/panel_layout_config.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/ui/screens/builder/weapons_panel.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/ui/screens/empire_build_queue_formatter.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/screens/food_allocation_editor.py | Read ✓ |
| game/ui/screens/galaxy_test/screen.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/menu_scene.py | Read ✓ |
| game/ui/screens/orders_window.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/ui/screens/star_data_source.py | Read ✓ |
| game/ui/screens/star_list_filter_manager.py | Read ✓ |
| game/ui/screens/star_list_presets.py | Read ✓ |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ |
| game/ui/screens/strategy_menu_panel.py | Read ✓ |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| game/ui/screens/strategy_ui_action_router.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/ui/screens/workshop_context.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/ui/utils/resource_display.py | Read ✓ |
| game/ui/widgets/dropdown_helper.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
