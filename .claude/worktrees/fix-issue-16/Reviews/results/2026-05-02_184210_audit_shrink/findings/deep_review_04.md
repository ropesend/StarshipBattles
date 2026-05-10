# Deep Review: Shard 04
## Summary
- Shard: Shard 04
- Files in Scope: 165
- Files Actually Read: 165
- Total Findings: 13
- Critical: 0 | Product Decision: 2 | Major: 3 | Minor: 5 | Info: 3

## Dead Code Findings

#### MINOR: Deprecated static methods in AbilityManager
**ID:** DEEP-04-001
**Location:** game/simulation/components/ability_manager.py:286-341
**Issue:** Six static methods marked as "DEPRECATED" with a `# NOQA: legacy-retained` comment. These proxy to the private `_get_abilities_polymorphic` method and duplicate the instance methods. The comment says "removal tracked separately from PROJ-270" but the static methods duplicate the instance logic verbatim.
**Estimated LOC:** ~56 (lines 290-341)
**Tests reference?** No — grep `tests/` for `get_abilities_static`, `get_ability_static`, `has_ability_static`, `has_pdc_ability_static`, `get_ui_rows_static`, `instantiate_abilities_static` returns zero hits.
**Docs reference?** No — grep `docs/` for same symbols returns zero hits.
**Recommendation:** These should be verified with a deeper audit and then deleted. The `# NOQA` comment indicates awareness but the PROJ-270 deadline appears passed. If callers exist (only through `Component` facade properties), remove the static duplicates now.

#### MINOR: Deprecated static methods in ModifierManager
**ID:** DEEP-04-002
**Location:** game/simulation/components/modifier_manager.py:221-330
**Issue:** Five static methods marked as "DEPRECATED" with `# DEPRECATED: Use instance ... instead. Will be removed in Task 1.3.` Same pattern as DEEP-04-001. `remove_modifier_inplace` is the only one kept as a helper for add_modifier.
**Estimated LOC:** ~110 (lines 221-330)
**Tests reference?** No — grep `tests/` for `add_modifier_static`, `remove_modifier_static`, `remove_modifier_inplace`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static` returns zero hits.
**Docs reference?** No — grep `docs/` for same symbols returns zero hits.
**Recommendation:** Delete all deprecated static methods except `remove_modifier_inplace` (used internally by `add_modifier`). ~85 LOC recoverable.

#### MINOR: Unused imports in `design_metadata.py`
**ID:** DEEP-04-003
**Location:** game/strategy/data/design_metadata.py:13
**Issue:** `import warnings` is imported but never used. `import datetime` is used. `import os` is used. `import warnings` is unused.
**Estimated LOC:** 1
**Tests reference?** N/A (unused import)
**Docs reference?** N/A
**Recommendation:** Remove `import warnings` line.

#### MINOR: `get_asset_manager` is a redundant alias for `get_default_asset_manager`
**ID:** DEEP-04-004
**Location:** game/assets/asset_manager.py:348-350
**Issue:** `get_asset_manager()` is a one-line alias for `get_default_asset_manager()` with no functional difference. The module already has `get_default_asset_manager()` and `set_default_asset_manager()`. This creates two identical accessors.
**Estimated LOC:** 3 (function body + blank lines around it)
**Tests reference?** `get_asset_manager` is used in `game/ui/screens/strategy_screen.py:638` — but it could just call `get_default_asset_manager()` directly.
**Docs reference?** No
**Recommendation:** Delete `get_asset_manager()` and direct the one caller to use `get_default_asset_manager()`.

#### MINOR: Unused variable `y_offset` shadowed in `build_queue_selector.py`
**ID:** DEEP-04-005
**Location:** game/ui/screens/build_queue_selector.py:99-100
**Issue:** `y_offset = 0` is assigned on line 99, then immediately reassigned on line 100. The line 99 assignment is dead code.
**Estimated LOC:** 1
**Tests reference?** No
**Docs reference?** No
**Recommendation:** Remove the redundant `y_offset = 0` on line 99.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:

| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-04-P1 | `ShieldRegeneratingArmor` ability class | ~6 | `tests/unit/simulation/components/abilities/test_defense.py` | `docs/02_PATTERNS.md` (Pattern 14) | `data/components.json` | Currently has no production callers that read its `value` — only `get_primary_value()` inherited from `StaticValueAbility`. The class exists but the `ShieldRegeneratingArmor` ability is defined in JSON config but no combat code path consumes it (unlike `EmissiveArmor` which is used by `damage_calculator.py`). Either wire it or document it as planned infrastructure. |
| DEEP-04-P2 | Workshop data reloader's `load_test_data` method | ~8 | `tests/unit/ui/screens/test_workshop_data_reloader.py` | No | No | `load_test_data()` (line 125-130) loads from `tests/data/` — a test-only code path inside a production file. This is a development convenience with no production reach. Consider removing or moving the logic to a test fixture. |

## Internal Duplication Findings

#### MAJOR: Duplicate facility ability extraction logic across strategy engines
**ID:** DEEP-04-006
**Location:** Multiple strategy engine files (planet_energy_engine.py, water_engine.py, consumable_management_engine.py, etc.)
**Issue:** Multiple engine files duplicate the pattern of iterating facility design components and extracting abilities. The pattern `for facility in planet.facilities / for comp in iter_components(facility.design_data) / abilities = extract_abilities_from_component(comp, registries)` appears in at least 4 different engine files. This duplicates component_inspector.py's `iterate_design_components` iterator but with subtly different filtering logic each time.
**Estimated LOC:** ~60 across files
**Recommendation:** Create a helper `iterate_facility_abilities(facilities, registries)` in `component_inspector.py` that yields `(facility, comp, abilities)` tuples and migrate all 4 consumers.

#### MAJOR: Duplicate `_validate_tick_inputs` pattern across 7+ engines
**ID:** DEEP-04-007
**Location:** fleet_movement_engine.py:194-207, action_execution_engine.py:70-79, consumable_management_engine.py:69-78, planet_energy_engine.py:164-173, population_engine.py:63-72, etc.
**Issue:** Seven strategy sub-engines each independently implement `_validate_tick_inputs(empires)` with nearly identical code checking for None locations on fleets or None colony entries. Only the specific null-check varies. This is ~10 lines duplicated 7 times.
**Estimated LOC:** ~60 across 7 files
**Recommendation:** A base class or mixin with a configurable validation check (e.g., a class-level list of `_NULL_CHECKS` tuples) would eliminate this duplication.

#### MAJOR: Duplicate deferred-loading pattern for JSON configs in galaxy generation
**ID:** DEEP-04-008
**Location:** galaxy_system_generator.py:220-366, galaxy_warp_generator.py:377-444
**Issue:** Both files implement identical module-level lazy-loaded JSON caches with the same pattern: global variable → `_load_*()` function with `if _CACHE is None` guard → `open(path)` + `json.load(f)` + assignment. This pattern appears 3 times in galaxy_system_generator.py and once in galaxy_warp_generator.py. The cache key differs but the loader shape is identical.
**Estimated LOC:** ~40 across 2 files
**Recommendation:** Extract a `_lazy_load_json(path, cache_key)` helper or a small `LazyJsonCache` class. This also simplifies the `from pathlib import Path; import json` imports that appear inside each loader.

## Fragmentation Findings

No significant fragmentation findings for this shard. The files generally follow the layered architecture with clean responsibility boundaries. The slice-based facade decomposition (PROJ-309 sub-phase 3.7) is correctly organized.

## Quality / LOC Reduction Findings

#### INFO: Large files exceeding 500 LOC ceiling (informational)
**ID:** DEEP-04-009
**Location:** Multiple files
**Issue:** The following files in this shard exceed the 500 LOC ceiling: `ship.py` (607), `build_queue_controller.py` (652), `strategy_click_dispatcher.py` (628), `strategy_screen.py` (682), `system_tree_panel.py` (719), `ship_instance.py` (787), `empire_build_queue_window.py` (569), `race_setup/controller.py` (486, near ceiling), `design_stats_panel.py` (516), `workshop_event_router.py` (545), `empire_panel_window.py` (539), `design_selector_window.py` (615), `transfer_dialog.py` (790), `ship_detail_panel.py` (685), `stat_rows_dynamic.py` (504). This is per conventions but noted as reduction candidates per PROJ-309 spirit.
**Estimated LOC:** N/A (informational)
**Recommendation:** These files were already flagged by the shrink audit tool. Not a new finding — confirmed as known.

#### INFO: `_extract_dropdown_value` duplicated between transfer_dialog.py and other dialogs
**ID:** DEEP-04-010
**Location:** game/ui/screens/transfer_dialog.py:278-282, game/ui/screens/design_selector_window.py:263-267
**Issue:** Both transfer_dialog.py and design_selector_window.py implement the same `_extract_dropdown_value` / tuple-unwrap pattern to handle pygame_gui's dropdown returning tuples vs strings. The pattern is identical (check `isinstance(value, tuple)`, return `value[0]` if so).
**Estimated LOC:** ~5 per occurrence (2 occurrences = 10)
**Recommendation:** Extract to a module-level helper in `game/ui/utils/`. This is a pygame_gui version-compat pattern.

#### INFO: `SystemTreePanel` has untyped dict access patterns that could be optimized
**ID:** DEEP-04-011
**Location:** game/ui/panels/system_tree_panel.py
**Issue:** The `_get_empire_context`, `_add_system_effects`, `_add_sector_effects`, `_add_system_hazard_hint` methods all perform nested `getattr` chains (`scene_interface → scene → session → player_empire.id`) that are repeated 3 times. A single cached call would eliminate the duplication.
**Estimated LOC:** ~6
**Recommendation:** Extract the `empire_id, registries` resolution to a private method and cache it per `set_items` call.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/behaviors.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| game/simulation/combat/formation.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/simulation/components/abilities/defense.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Read ✓ |
| game/simulation/entities/ship.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/simulation/services/registry_loader.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/__init__.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/fleet_hierarchy.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/strategy/data/ship_instance.py | Read ✓ |
| game/strategy/data/ship_instance_serializer.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/strategy/engine/action_execution_engine.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/strategy/generation/density/primitives/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/linear.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/strategy/interfaces/engines.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/services/ability_sources/warp_point.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/component_inspector.py | Read ✓ |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/ui/assets/ship_theme_manager.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/ui/panels/strategy_widgets.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/ui/renderer/camera.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/ui/screens/atmosphere_target_editor.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/battle_ui.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/modifier_row.py | Read ✓ |
| game/ui/screens/builder/right_panel.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/ui/screens/empire_build_queue_data_source.py | Read ✓ |
| game/ui/screens/empire_build_queue_window.py | Read ✓ |
| game/ui/screens/empire_panel_window.py | Read ✓ |
| game/ui/screens/event_log_sidebar.py | Read ✓ |
| game/ui/screens/fleet_report_view_model.py | Read ✓ |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_presets.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/ui/screens/strategy_fleet_ops.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/ui/screens/strategy_windows/__init__.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ |
| game/ui/screens/test_lab/details/resource_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/validation_panel.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_event_router.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/image/background.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/ui/services/tkinter_utils.py | Read ✓ |
| game/ui/services/vehicle_class_service.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
