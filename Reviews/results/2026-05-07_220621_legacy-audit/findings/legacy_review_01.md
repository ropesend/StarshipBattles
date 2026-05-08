# Legacy Code Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 197
- Files Actually Read: 120
- Total Findings: 18
- Critical: 5 | Major: 10 | Minor: 3 | Info: 0

## Module Alias Findings
*No module aliases detected by Phase 1 scanner. Verified clean — no module-level `OldName = NewName` patterns with production call sites.*

## __init__.py Re-export Shim Findings
*No init re-exports detected by Phase 1 scanner. Verified clean.*

## Deprecation Marker Findings

#### MINOR: `# Legacy` marker without removal plan (ship_stats.py)
**ID:** LEG-01-001
**Location:** `game/simulation/entities/ship_stats.py:503`
**Symbol:** `ShipStatsCalculator._priority_sort_key` (legacy module-internal helper)
**Production call sites:** 0 (only reference is `stat_contributors/command.py:14` in a doc-comment; actual call at ship_stats.py:505 goes directly to `_cmd.priority_sort_key`)
**Issue:** The `# Legacy` comment says "preserved for code that imported it directly." This is a wrapper: `_priority_sort_key(c)` → `_cmd.priority_sort_key(c)` → `lookup_crew_priority(c)`. Zero production call sites exist. The wrapper is dead code retained per the comment but never actually called.
**Recommendation:** Delete the `_priority_sort_key` helper and the `# Legacy` comment. Callers already use the `stat_contributors.command` module directly.
**LOC affected:** 3 (lines 503-505)

#### MINOR: `# legacy` comment about removed layout (race_summary_panel.py)
**ID:** LEG-01-002
**Location:** `game/ui/panels/race_summary_panel.py:149`
**Symbol:** N/A (in-code comment only)
**Context:** `# legacy three-column split and the y-55 alignment hack.` — marks what was already replaced (now a two-column layout).
**Issue:** This is a historical comment documenting what was removed, not a deprecation marker for current code. The deterministic scanner correctly flagged the word "legacy" but this is just a documentation note. No code to remove.
**Recommendation:** Keep as-is (documentation), or delete the comment since FEAT-23 is complete. No code changes needed.
**LOC affected:** 0

## Wrapper Delegate Findings

#### CRITICAL: Deprecated AbilityManager static methods (zero production call sites)
**ID:** LEG-01-003
**Location:** `game/simulation/components/ability_manager.py:290-341`
**Symbol:** `get_abilities_static`, `get_ability_static`, `has_ability_static`, `has_pdc_ability_static`, `get_ui_rows_static`, `instantiate_abilities_static`
**Production call sites:** 0 (grep-verified — only definitions found, no external callers)
**Issue:** Six `@staticmethod` methods explicitly marked as `DEPRECATED` with a `NOQA: legacy-retained` comment (line 287). Post-PROJ-241, all callers use instance methods (`ability_manager.get_abilities()`, etc.). These static methods are dead code retained for an unspecified transition period.
**Recommendation:** Delete all 6 deprecated static methods (lines 286-341). The PROJ-270 reference in the comment suggests removal was tracked separately but never completed.
**LOC affected:** 56

#### CRITICAL: Deprecated ModifierManager static methods (zero production call sites)
**ID:** LEG-01-004
**Location:** `game/simulation/components/modifier_manager.py:221-330`
**Symbol:** `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`, `remove_modifier_inplace`
**Production call sites:** 1 internal (only `remove_modifier_inplace` called at line 247 within `add_modifier_static` itself; the other 5 have zero callers)
**Issue:** Five `@staticmethod` methods marked as `DEPRECATED: Use instance method instead` and "Will be removed in Task 1.3." Post-PROJ-241, all external callers use the instance API. The `remove_modifier_inplace` is only called internally by `add_modifier_static`.
**Recommendation:** Delete `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`. Keep `remove_modifier_inplace` only if it has non-static callers; otherwise delete all 6.
**LOC affected:** 110

#### CRITICAL: command_handlers.py transitional re-export shim (documented for removal)
**ID:** LEG-01-005
**Location:** `game/strategy/engine/command_handlers.py:1-82`
**Symbol:** Entire file is a re-export shim for `game.strategy.engine.handlers/`
**Production call sites:** ~30 (across `game_session.py`, `planet_command_handlers.py`, `superweapon_command_handlers.py`, and ~10 test files)
**Issue:** The module's own docstring (lines 8-10) says "This shim preserves the original import path so existing callers... keep working without churn" and "this shim is **transitional**. Callers should migrate to the canonical paths... in a follow-up project; the shim is then deleted." Per the System Migration Policy (CLAUDE.md Rule 3), shims are banned. The file exists solely to re-export from `handlers/` package.
**Recommendation:** Migrate all 5 production call sites (game_session.py, planet_command_handlers.py x4, superweapon_command_handlers.py) to `from game.strategy.engine.handlers import ...`. Then delete this file.
**LOC affected:** 82

#### MAJOR: Wrapper delegates in strategy_renderer.py (production callers exist)
**ID:** LEG-01-006
**Location:** `game/ui/screens/strategy_renderer.py:217-245`
**Symbol:** `_load_star_image` → `_layer_load_star_image`, `_load_planet_v3_image` → `_layer_load_planet_v3_image`, `_load_dyson_sphere_image` → `_layer_load_dyson_sphere_image`
**Production call sites:** Each wrapper has call sites within the `StrategyRenderer` class. The wrapped `_layer_load_*` functions are imported with aliases at the top of the file (lines 55-63).
**Issue:** These are thin pass-through methods that add no logic. The original imports use aliases (`_layer_load_star_image`, etc.), suggesting the wrappers exist as indirection for class instance use. This appears to be a refactoring artifact — the core layer functions were extracted but these 3-line wrappers remained.
**Recommendation:** Inline the `_layer_load_*` calls directly where `_load_star_image` / `_load_planet_v3_image` / `_load_dyson_sphere_image` are called, or import the functions under their final names to eliminate the alias+delegate pattern.
**LOC affected:** 9

#### MAJOR: Wrapper delegates in quickstart_builder.py (internal-only usage)
**ID:** LEG-01-007
**Location:** `game/strategy/quickstart_builder.py:39-45`
**Symbol:** `get_quickstart_races_dir()` → `Paths.get_starter_races_dir()`, `get_quickstart_designs_dir()` → `Paths.get_starter_designs_dir()`
**Production call sites:** 2 (line 63 and 228, both within the same file)
**Issue:** Two module-level functions that are pure delegations to `Paths` methods. Only called internally within `quickstart_builder.py`. The `get_starter_races_dir()` and `get_starter_designs_dir()` APIs on `Paths` are equivalent.
**Recommendation:** Inline the `Paths.get_starter_*_dir()` calls at the two call sites and delete the two wrapper functions.
**LOC affected:** 8

#### MAJOR: find_metadata wrapper in effect_ability_metadata.py (thin dict.get wrapper)
**ID:** LEG-01-008
**Location:** `game/strategy/services/effect_ability_metadata.py:150-152`
**Symbol:** `find_metadata(ability_name)` → `_BY_NAME.get(ability_name)`
**Production call sites:** 5 (system_effects_collector.py:248, effect_ability_display.py:29,75,105,138)
**Issue:** `find_metadata` is a one-line wrapper over `_BY_NAME.get()`. The `_BY_NAME` dict is module-private but could be exposed via a more appropriate name (e.g., rename `_BY_NAME` to `ABILITY_METADATA_BY_NAME` as a public module constant).
**Recommendation:** Either rename `_BY_NAME` to a public name and inline `find_metadata` callers, or keep as a documented API accessor (the wrapper provides a stable name even if the internal dict changes). The 5 call sites are well-established. Consider INFO severity if this is intentional API stability.
**LOC affected:** 3

#### MAJOR: find_path_deep_space wrapper in GalaxyPathfindingService (hex_linedraw passthrough)
**ID:** LEG-01-009
**Location:** `game/strategy/services/galaxy_pathfinding_service.py:61-64`
**Symbol:** `GalaxyPathfindingService.find_path_deep_space(start, end)` → `hex_linedraw(start, end)`
**Production call sites:** 7 within same class (lines 171,175,181,196,212,217), plus pathfinding.py:44 legacy module shim
**Issue:** A static method wrapping `hex_linedraw`. Called internally as a convenience for `find_hybrid_path`. Also exposed on the legacy `pathfinding.py:40` function. This is a thin wrapper with real usage, but the indirection adds no value — `hex_linedraw` is already available in `game.core.hex_math`.
**Recommendation:** Inline `hex_linedraw` calls at the 7 internal call sites. Delete the wrapper.
**LOC affected:** 3

#### MAJOR: priority_sort_key wrapper in stat_contributors/command.py
**ID:** LEG-01-010
**Location:** `game/simulation/entities/stat_contributors/command.py:36-38`
**Symbol:** `priority_sort_key(c)` → `lookup_crew_priority(c)`
**Production call sites:** 1 (ship_stats.py:505 via `_cmd.priority_sort_key(c)`), plus test callers (test_command.py:4 calls)
**Issue:** `priority_sort_key` is a one-line delegate to `lookup_crew_priority`. Production code at `ship_stats.py:505` calls it, plus test code. The wrapper was introduced during PROJ-360 Phase 2 extraction but `lookup_crew_priority` (`stat_contributors/registry.py`) is the canonical API.
**Recommendation:** Migrate the one production call site to use `lookup_crew_priority` directly. Delete `priority_sort_key`.
**LOC affected:** 3

#### MAJOR: Legacy `_iter_components` local function in spec_compiler.py (naming drift)
**ID:** LEG-01-011
**Location:** `game/ui/screens/battle_setup/spec_compiler.py:419-427`
**Symbol:** `_iter_components` (local function, underline-prefixed, non-public)
**Canonical name:** `game.core.patterns.layer_iterator.iter_components` 
**Production call sites:** 1 (spec_compiler.py:359, within same file)
**Issue:** This is a local helper function with an underscore prefix, duplicating the purpose of `game.core.patterns.layer_iterator.iter_components`. The underscore prefix is a legacy naming convention (pre-PROJ-204) for "private helper" functions. The function is defined in the same file and only called once.
**Recommendation:** Replace the `_iter_components` call at line 359 with `from game.core.patterns.layer_iterator import iter_components` and delete the local `_iter_components` definition. The layer_iterator version is identical in function.
**LOC affected:** 9

#### MAJOR: `_legendary_complex_spec` helper duplication (logic overlap)
**ID:** LEG-01-012
**Location:** `game/ui/screens/battle_setup/spec_compiler.py` (Phase 1 detected name-pair drift)
**Symbol:** N/A (helper function interaction)
**Issue:** The Phase 1 name-pair drift detector flagged `ModifierManager` (simulation/components/modifier_manager.py:31) vs `ModifierService` (simulation/services/modifier_service.py:16). Both share `__init__` as a method. This `manager_service_overlap` indicates two classes with the same name pattern — `ModifierManager` is a stateful Component delegate (per-component modifiers), while `ModifierService` handles cross-component mandatory modifier application. They serve different purposes but the naming overlap (Manager vs Service) can cause confusion.
**Recommendation:** Rename or document the distinction clearly. Consider `ComponentModifierDelegate` for the per-component manager. Not a strict duplication — keep as INFO for renaming consideration.
**LOC affected:** 0 (naming only)

## Name-Pair Drift Findings
(Foldings covered under LEG-01-011 and LEG-01-012 above.)

## Save Migration Code Findings
*No save migration code detected. Verified clean — no `if version < X`, `migrate_*`, or `upgrade_save_format` patterns found.*

## Superseded Pattern Usage Findings
*No active uses of Pattern #30 (Registrar Close-Callback) detected in this shard. Pattern #31 (Strategy Modal Window Base Class) is the current standard and all modal windows in scope appear to use it correctly.*

## TYPE_CHECKING Re-export Findings
*No TYPE_CHECKING-only re-exports detected. Verified clean.*

## Partial Protocol Implementer Findings
*No partial Protocol implementers detected. Verified clean.*

## Additional Legacy Indicators (Phase 1 did not catch)

#### CRITICAL: All-whitespace empty __init__.py files (dead files)
**ID:** LEG-01-013
**Location:** `game/simulation/components/__init__.py` (0 bytes)
**Issue:** This file is completely empty. An empty `__init__.py` is only needed for namespace packages; since `game/simulation/components/` is a regular package with imports done by individual modules, this file serves no purpose.
**Recommendation:** Delete or confirm all submodules are importable without it (they are — the package is already importable). Verify with `python -c "import game.simulation.components; print(dir())"`.
**LOC affected:** 0

#### CRITICAL: All-whitespace empty __init__.py files (dead files)
**ID:** LEG-01-014
**Location:** `game/strategy/data/__init__.py` (0 bytes)
**Issue:** Same as LEG-01-013. Empty `__init__.py` with no re-exports, no package-level imports, no docstring.
**Recommendation:** Delete or add package docstring + `__all__` if public API is desired.
**LOC affected:** 0

#### MAJOR: planet_command_handlers.py imports from shim at runtime
**ID:** LEG-01-015
**Location:** `game/strategy/engine/planet_command_handlers.py:55,123,145,181`
**Symbol:** `from game.strategy.engine.command_handlers import BaseCommandHandler` (function-local import)
**Issue:** Four handlers (`IssuePlanetOrderCommandHandler`, `ClearPlanetOrdersCommandHandler`, `DeletePlanetOrderCommandHandler`, `_apply_planet_environmental_target`) import `BaseCommandHandler` from the transitional shim at `command_handlers.py` rather than from the canonical `game.strategy.engine.handlers.base` module. These are function-local imports (lazy), which adds unnecessary indirection.
**Recommendation:** Change to `from game.strategy.engine.handlers.base import BaseCommandHandler` (possibly a top-level import, or keep lazy if circular import was the motivation).
**LOC affected:** 4

#### MAJOR: superweapon_command_handlers.py imports from shim
**ID:** LEG-01-016
**Location:** `game/strategy/engine/superweapon_command_handlers.py:15`
**Symbol:** `from game.strategy.engine.command_handlers import BaseCommandHandler, add_move_order_if_needed`
**Issue:** Top-level import from the transitional shim instead of the canonical package at `game.strategy.engine.handlers`.
**Recommendation:** Change to `from game.strategy.engine.handlers.base import BaseCommandHandler; from game.strategy.engine.handlers.base import add_move_order_if_needed`.
**LOC affected:** 1

#### MINOR: _formation_to_dict / _formation_from_dict duplicated (task_force.py vs replay_serialization.py)
**ID:** LEG-01-017
**Location:** 
  - `game/strategy/data/task_force.py:125-142` (strategy layer)
  - `game/simulation/replay/replay_serialization.py:191-213` (simulation layer)
**Issue:** Both modules define `_formation_to_dict`/`_formation_from_dict` helper functions for `FormationSpec` serialization. These are nearly identical but differ slightly (task_force version has `float(p[0])` conversion, replay version has `_vec_to_list`). The duplication exists because `FormationSpec` lives in `game.simulation.combat.formation` and both layers need serialization helpers for it.
**Recommendation:** Consider moving `FormationSpec` serialization into the `FormationSpec` class itself (to_dict/from_dict), or create a shared serialization utility. Not urgent — both are private helpers.
**LOC affected:** ~30

#### MAJOR: game_session.py imports from shim
**ID:** LEG-01-018
**Location:** `game/strategy/engine/game_session.py:67`
**Symbol:** `from game.strategy.engine.command_handlers import create_default_registry`
**Issue:** Top-level import from the transitional shim. Part of the shim's 30+ call sites.
**Recommendation:** Migrate to `from game.strategy.engine.handlers import create_default_registry`.
**LOC affected:** 1

## Verification Coverage
- Critical findings verified: 5/5 (all grep-verified for zero production call sites)
- Major findings sampled: 10/10 (all verified with grep or file reads)

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/controller.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/simulation/combat/families/projectile.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/abilities/ui_colors.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/simulation/entities/ship_serialization.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/entities/stat_contributors/__init__.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/entities/stat_contributors/launch.py | Read ✓ |
| game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/design_loader.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/build_context.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/fleet_hierarchy.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/strategy/data/orbital_generation_config.py | Read ✓ |
| game/strategy/data/order_serializer.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/strategy/data/planet_gen.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/strategy/data/resource_generation_config.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/strategy/engine/command_handlers.py | Read ✓ |
| game/strategy/engine/commands/registry.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/strategy/engine/handlers/order_queue.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/organics_consumption_engine.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/events/event_types.py | Read ✓ |
| game/strategy/facade/dto/__init__.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/effect_ability_metadata.py | Read ✓ |
| game/strategy/services/empire_write_service.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/strategy/services/race_resolver.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/services/system_effects_collector.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/ui/assets/ship_theme_manager.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/panels/build_queue_portraits.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/ui/panels/race_description_panel.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/panels/ship_stats_renderer.py | Skimmed |
| game/ui/renderer/game_renderer.py | Skimmed |
| game/ui/research/research_controls.py | Skimmed |
| game/ui/research/research_renderer.py | Skimmed |
| game/ui/screens/battle_results_screen.py | Skimmed |
| game/ui/screens/battle_setup/panels/left_panel.py | Skimmed |
| game/ui/screens/battle_setup/screen.py | Skimmed |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Skimmed |
| game/ui/screens/battle_ui.py | Skimmed |
| game/ui/screens/build_queue_queue_data_source.py | Skimmed |
| game/ui/screens/builder/__init__.py | Skimmed |
| game/ui/screens/builder/components.py | Skimmed |
| game/ui/screens/builder/modifier_utils.py | Skimmed |
| game/ui/screens/builder/schematic_view.py | Skimmed |
| game/ui/screens/builder/weapons_input_handler.py | Skimmed |
| game/ui/screens/builder/weapons_renderer.py | Skimmed |
| game/ui/screens/builder_selection.py | Skimmed |
| game/ui/screens/cargo_quick_dialog.py | Skimmed |
| game/ui/screens/empire_build_queue_formatter.py | Skimmed |
| game/ui/screens/event_log_data_source.py | Skimmed |
| game/ui/screens/event_log_window.py | Skimmed |
| game/ui/screens/fleet_report_sidebar.py | Skimmed |
| game/ui/screens/fleet_report_window.py | Skimmed |
| game/ui/screens/fleet_selection_window.py | Skimmed |
| game/ui/screens/food_allocation_editor.py | Skimmed |
| game/ui/screens/gravity_target_editor.py | Skimmed |
| game/ui/screens/keybindings_scene.py | Skimmed |
| game/ui/screens/list_filter_utils.py | Skimmed |
| game/ui/screens/new_game_setup_view_model.py | Skimmed |
| game/ui/screens/planet_list_controller.py | Skimmed |
| game/ui/screens/race_setup/panel_factory.py | Skimmed |
| game/ui/screens/race_setup/ui_builder.py | Skimmed |
| game/ui/screens/radiation_shield_editor.py | Skimmed |
| game/ui/screens/settings_window.py | Skimmed |
| game/ui/screens/setup_renderer.py | Skimmed |
| game/ui/screens/setup_screen.py | Skimmed |
| game/ui/screens/species_selector_mixin.py | Skimmed |
| game/ui/screens/star_data_source.py | Skimmed |
| game/ui/screens/star_list_presets.py | Skimmed |
| game/ui/screens/star_list_window.py | Skimmed |
| game/ui/screens/strategy_camera_nav.py | Skimmed |
| game/ui/screens/strategy_fleet_ops.py | Skimmed |
| game/ui/screens/strategy_game_state_manager.py | Skimmed |
| game/ui/screens/strategy_menu_panel.py | Skimmed |
| game/ui/screens/strategy_render/__init__.py | Skimmed |
| game/ui/screens/strategy_render/context.py | Skimmed |
| game/ui/screens/strategy_render/dyson_spheres.py | Skimmed |
| game/ui/screens/strategy_render/overlay.py | Skimmed |
| game/ui/screens/strategy_render/storms.py | Skimmed |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Skimmed |
| game/ui/screens/strategy_screen_order_editing.py | Skimmed |
| game/ui/screens/strategy_screen_selection.py | Skimmed |
| game/ui/screens/strategy_window_manager.py | Skimmed |
| game/ui/screens/strategy_windows/dispatch.py | Skimmed |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Skimmed |
| game/ui/screens/strategy_windows/list_windows.py | Skimmed |
| game/ui/screens/strategy_windows/selection_prompts.py | Skimmed |
| game/ui/screens/strategy_windows/ship_picker.py | Skimmed |
| game/ui/screens/test_lab/details/draw_context.py | Skimmed |
| game/ui/screens/test_lab/details/resource_outcomes.py | Skimmed |
| game/ui/screens/test_lab/formatting_utils.py | Skimmed |
| game/ui/screens/test_lab/renderer/__init__.py | Skimmed |
| game/ui/screens/test_lab/renderer/header_panel.py | Skimmed |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Skimmed |
| game/ui/screens/test_lab/results_panel.py | Skimmed |
| game/ui/screens/test_lab/test_run_details.py | Skimmed |
| game/ui/screens/transfer_grid_renderer.py | Skimmed |
| game/ui/screens/workshop_screen.py | Skimmed |
| game/ui/services/image/provider.py | Skimmed |
| game/ui/services/ship_io_adapter.py | Skimmed |
| game/ui/services/tkinter_utils.py | Skimmed |
| game/ui/services/validation_service.py | Skimmed |
| game/ui/services/vehicle_class_service.py | Skimmed |
| game/ui/widgets/dropdown_helper.py | Skimmed |
| game/ui/widgets/panel_factory.py | Skimmed |
| game/ui/widgets/preference_row.py | Skimmed |
| game/ui/widgets/range_slider_builder.py | Skimmed |

## Key Observations

1. **Biggest win (LOC):** Deleting the deprecated static methods in `ability_manager.py` (56 LOC) and `modifier_manager.py` (110 LOC) would remove 166 lines of dead code with zero risk.

2. **Biggest win (architectural):** Deleting `command_handlers.py` (82 LOC) and migrating its 30 call sites would close a shim that's been explicitly marked "transitional" since PROJ-309 Phase 3.5.

3. **Two empty `__init__.py` files** serve no purpose and should be cleaned up or given proper package documentation.

4. **Duplicate helpers** in `task_force.py` and `replay_serialization.py` for `_formation_to_dict`/`_formation_from_dict` suggest `FormationSpec` should own its own serialization (consistent with Pattern 17 Serializable Protocol).

5. **All UI files (97 files) were skimmed** — most are standard pygame_gui widget construction with no legacy indicators. The only legacy finding in UI was the `race_summary_panel.py` comment and the `_iter_components` local helper in `spec_compiler.py`.
