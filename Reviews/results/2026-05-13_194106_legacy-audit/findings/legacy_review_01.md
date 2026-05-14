# Legacy Code Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 165
- Files Actually Read: 165
- Total Findings: 6
- Critical: 0 | Major: 1 | Minor: 1 | Info: 4

## Module Alias Findings
*No module aliases detected by Phase 1 scan in this shard. Verified — no alias findings.*

## __init__.py Re-export Shim Findings
*No __init__.py re-exports identified as shims by Phase 1 scan in this shard. The re-exports in `game/simulation/replay/__init__.py`, `game/strategy/services/ability_sources/__init__.py`, and `game/strategy/generation/density/__init__.py` are documented public API surfaces, not legacy shims.*

## Deprecation Marker Findings
#### MINOR: Stale `# legacy` comment referencing completed migration
**ID:** LEG-01-001
**Location:** game/ui/panels/race_summary_panel.py:149
**Marker:** `# legacy three-column split and the y-55 alignment hack.`
**Issue:** Comment references the transition from a three-column to two-column layout with the "y-55 alignment hack" as if the migration is ongoing. The preceding line (147) marks the new two-column layout under FEAT-23 — the migration is already done. The stale comment misleads future readers into thinking the legacy code path still exists.
**Recommendation:** Remove the stale `# legacy` comment. The FEAT-23 marker on line 147 already documents the correct current state.
**LOC affected:** 1 (comment line)

#### INFO: Phase 1 false positive — UI rendering label, not deprecation
**ID:** LEG-01-002
**Location:** game/ui/screens/test_lab/dialogs.py:256
**Marker:** `# Old value (strikethrough)`
**Issue:** This is a rendering comment explaining how old values are displayed with strikethrough in the `ConfirmChangesDialog.draw()` method. It is NOT a deprecation marker. The Phase 1 detector matched the `# Old` substring but the full line reads `# Old value (strikethrough)` — a UI presentation label, not a code-deprecation indicator.
**Recommendation:** None — false positive.

## Wrapper Delegate Findings
#### MAJOR: `to_roman` wrapper with 1 internal call site
**ID:** LEG-01-003
**Location:** game/strategy/data/planet_naming.py:16
**Function:** `to_roman(n) -> str` delegates to `NameRegistry.to_roman(n)`
**Production call sites:** 1 (internal: planet_naming.py:64)
**Issue:** The module-level function `to_roman()` adds no logic beyond delegating to `NameRegistry.to_roman()`. It is called only once — from the same file on line 64 (`roman = to_roman(planet_idx)`). The single call site could be replaced by a direct call to `NameRegistry.to_roman(planet_idx)` and the wrapper deleted.
**Recommendation:** Replace the internal call on line 64 with `NameRegistry.to_roman(planet_idx)` and delete the `to_roman()` wrapper function (lines 16–28). Import `NameRegistry.to_roman` explicitly if callers need the name, though currently all external consumers use `NameRegistry.to_roman` directly (verified: no external call sites in `game/`).
**LOC affected:** 13 (lines 16–28)

#### INFO: Phase 1 false positive — `_get_system_at_hex` is documented test-patch surface
**ID:** LEG-01-004
**Location:** game/strategy/engine/superweapon_order_processor.py:343
**Function:** `_get_system_at_hex(galaxy, location)` delegates to `get_system_at_hex(galaxy, location)`
**Production call sites:** 11 (across 5 superweapon handler modules)
**Issue:** The docstring on lines 344–352 explicitly documents this as a shared patch surface for tests: "patches against `get_system_at_hex` affect this method's lookup, which is the only callsite handlers use." This is an intentional architectural choice, not legacy drift. The 11 call sites in superweapon handlers (`open_warp_point.py`, `close_warp_point.py`, `stellerate_star.py`, `create_dyson_sphere.py`, `implode_planet.py`) all route through this single indirection point.
**Recommendation:** Not legacy — false positive. The documentation is explicit and the patching seam prevents multiple handlers from independently resolving system lookups.

#### INFO: Phase 1 false positive — `find_metadata` is legitimate public API
**ID:** LEG-01-005
**Location:** game/strategy/services/effect_ability_metadata.py:150
**Function:** `find_metadata(ability_name) -> Optional[EffectAbilityMetadata]` delegates to `_BY_NAME.get(ability_name)`
**Production call sites:** 5 (in `system_effects_collector.py` and `effect_ability_display.py`)
**Issue:** This is a named public API function providing O(1) lookup into the registry of effect ability metadata. The `_BY_NAME` dict is a package-private module index, and `find_metadata()` is the public accessor. This is the standard registry pattern, not a legacy wrapper.
**Recommendation:** Not legacy — false positive. Keep as-is; this is a canonical public-accessor-over-private-index pattern.

## Name-Pair Drift Findings
#### INFO: Phase 1 false positive — ModifierManager and ModifierService are unrelated
**ID:** LEG-01-006
**Location:** game/simulation/components/modifier_manager.py:30 (`ModifierManager`) / game/simulation/services/modifier_service.py:16 (`ModifierService`)
**Shared methods detected:** `__init__` only
**Issue:** `ModifierManager` is a stateful per-component delegate (owns `_modifiers` list, handles add/remove/query against a component's registries). `ModifierService` is a service that validates modifier operations against a registry. They share only the trivial `__init__` method name — zero behavioral overlap. They serve different layers (component delegate vs service) with different callers (`Component` vs `ShipComponentManager`). The Phase 1 detector flagged the "manager_service_overlap" heuristic but the two classes have entirely different APIs, purposes, and consumers.
**Recommendation:** Not legacy — false positive. The naming similarity is coincidental; no duplication or drift exists.

## Save Migration Code Findings
*No save migration code detected by Phase 1 scan in this shard. Verified — no findings.*

## Superseded Pattern Usage Findings
*Pattern 30 (Registrar Close-Callback) is superseded by Pattern 31 (Strategy Modal Window Base Class). Per `docs/02_PATTERNS.md` §30: "Use only when maintaining existing slot cleanup. New strategy modal windows use StrategyModalWindow." The `on_close_callback` usage across the codebase (fleet_report_window.py, event_log_window.py, planet_list_window.py, etc.) is documented valid maintenance of existing slots — not unauthorized new usage. No findings for this shard.*

## TYPE_CHECKING Re-export Findings
*No TYPE_CHECKING-only re-exports detected by Phase 1 scan in this shard. Verified — no findings.*

## Partial Protocol Implementer Findings
*No optional protocol methods with legacy implementations detected by Phase 1 scan in this shard. Verified — no findings.*

## Additional Legacy Indicators (Phase 1 did not catch)
No additional legacy indicators found through manual review. Specific checks performed:
- **Shim files:** No file in this shard exists solely to re-export from another file. All `__init__.py` files serve documented public API surfaces per `docs/02_PATTERNS.md`.
- **Stale PROJ comments:** Only the one identified above (LEG-01-001 in race_summary_panel.py:149). All other PROJ comments reference active or completed work with clear completion markers.
- **Test-only callers:** Not comprehensively instrumented (requires per-function call-site analysis beyond Phase 1 deterministic scan scope). No obvious suspect functions surfaced during full-file review.
- **Unused `set_default_*` shim functions:** Verified `set_default_planet_habitability_service` has 3 production references (context.py definition, planet_habitability_service.py usage, planet.py documentation) — actively wired via PROJ-372. Not unused.
- **Module-level mutable state:** `game/ui/screens/battle_setup_state.py:24` (`_next_fleet_id`) and `game/simulation/replay/__init__.py` (`get_default_capture_sink/set_default_capture_sink`) use module-level default accessor patterns, both follow documented conventions per Pattern #1 (ApplicationContext) and #28 (Background Service Call).

## Verification Coverage
- Critical findings verified: N/A (0 critical findings)
- Major findings sampled: 1/1 (LEG-01-003: re-read planet_naming.py, verified single internal call site at line 64; confirmed no external production callers via grep)

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/behaviors.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/ai/interfaces/controllable.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/context.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/core/event_logging.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/core/protocols/strategy_mutators.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| game/simulation/combat/formation.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Read ✓ |
| game/simulation/components/modifier_schema.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/simulation/entities/stat_contributors/__init__.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/entities/stat_contributors/weapons.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/simulation/systems/attack_processor.py | Read ✓ |
| game/simulation/systems/battle_end_conditions.py | Read ✓ |
| game/simulation/systems/battle_logger.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/strategy/config/__init__.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/strategy/data/fleet_hierarchy.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/data/ship_instance_serializer.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/strategy/engine/order_handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/self_destruct.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/strategy/engine/superweapon_command_handlers.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/__init__.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/implode_planet.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/strategy/engine/turn_engine_settings.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/strategy/facade/dto/__init__.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/facade/dto/system_dto.py | Read ✓ |
| game/strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/linear.py | Read ✓ |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/generation/star_generator.py | Read ✓ |
| game/strategy/interfaces/engines.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/strategy/services/ability_sources/warp_point.py | Read ✓ |
| game/strategy/services/component_inspector.py | Read ✓ |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/strategy/services/effect_ability_metadata.py | Read ✓ |
| game/strategy/services/empire_economy_service.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/services/fleet_path_projection.py | Read ✓ |
| game/strategy/services/fleet_warp_resolution.py | Read ✓ |
| game/strategy/services/modifier_resolver.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/services/system_effects_collector.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/ui/components/filters/__init__.py | Read ✓ |
| game/ui/components/table/column_manager.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ui/orchestration/__init__.py | Read ✓ |
| game/ui/panels/__init__.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/ui/panels/race_environment_panel.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/pygame_gui_patch.py | Read ✓ |
| game/ui/renderer/camera.py | Read ✓ |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ |
| game/ui/screens/battle_setup/panels/right_panel.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/ui/screens/battle_setup_state.py | Read ✓ |
| game/ui/screens/build_queue_panel_factory.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/schematic_view.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ |
| game/ui/screens/builder_selection.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog_controller.py | Read ✓ |
| game/ui/screens/defeat_dialog.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/ui/screens/fleet_menu_items.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/list_filter_utils.py | Read ✓ |
| game/ui/screens/new_game_setup_controller.py | Read ✓ |
| game/ui/screens/per_player_ui_state.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_filter_manager.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/ui/screens/race_setup/ui_builder.py | Read ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/species_selector_mixin.py | Read ✓ |
| game/ui/screens/strategy_fleet_ops.py | Read ✓ |
| game/ui/screens/strategy_input_handler.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/screens/strategy_render/background.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| game/ui/screens/strategy_superweapons.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/ui/screens/strategy_ui_action_router.py | Read ✓ |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/ui/screens/transfer_view_model.py | Read ✓ |
| game/ui/screens/workshop_ship_io.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/ui/services/image/openai_provider.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/ui/utils/portraits.py | Read ✓ |
| game/ui/utils/resource_display.py | Read ✓ |
| game/ui/widgets/column_toggle_section.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
