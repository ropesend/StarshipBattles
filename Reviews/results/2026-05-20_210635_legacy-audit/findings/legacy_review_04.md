# Legacy Code Review: Shard 04
## Summary
- Shard: Shard 04
- Files in Scope: 214
- Files Actually Read: 214
- Total Findings: 6
- Critical: 0 | Major: 1 | Minor: 5 | Info: 0

## Module Alias Findings

**None.** The deterministic scan found zero module aliases in this shard. Independently verified as correct — no `import X as OldName` patterns that create legacy import paths were found.

## __init__.py Re-export Shim Findings

### MINOR — `game/ui/services/image/__init__.py:37` — Unused `_null_provider` side-effect import

**Finding:** The line `from game.ui.services.image import null_provider as _null_provider  # noqa: F401` imports the `null_provider` module as `_null_provider` for side effects (the module's import triggers `register_provider("null", NullImageProvider)`). However, `NullImageProvider` is already explicitly registered on line 42 via `register_image_provider("null", NullImageProvider)`. The `_null_provider` alias is never referenced — the `# noqa: F401` confirms intentional suppression of the unused-import linting. The side-effect import is redundant; the null provider is already registered by the explicit `register_image_provider` call. **Remove the unused import at line 37.**

## Deprecation Marker Findings

### MAJOR — `game/strategy/data/planetary_facility.py:196` — Deprecated fuel wrappers without removal plan

**Finding:** Four methods are marked `# Deprecated fuel-specific wrappers (F-A-012)`:
- `get_fuel_storage()` (line 209)
- `get_max_fuel_storage()` (line 213)
- `add_fuel()` (line 217)
- `withdraw_fuel()` (line 221)

These methods remain in **active production use** via `game/strategy/engine/resupply_engine.py:135,208,293` (`add_fuel`, `get_fuel_storage`, `withdraw_fuel`). They are also covered by 56 test call sites across `tests/unit/strategy/data/test_facility_resource_tracking.py` and other test files.

**Severity rationale:** The deprecation marker references ticket F-A-012 but provides no linked PROJ project, dated TODO, or removal timeline. The code is actively used in production — this is a "deprecated but can't be removed" state. The `# Deprecated` comment is misleading to contributors; the code should either (a) be replaced by the generic `*_consumable` API in the sole production caller and tests migrated, or (b) have the deprecation marker removed.

### MINOR — `game/strategy/combat/post_battle_hook_builder.py:67` — "# legacy" comment

**Finding:** Comment `# legacy direct-construction tests` describes a fallback path in `build()` that only fires when `owner_to_team_id` is `None` (tests that pre-date the canonical mapping kwarg). The fallback path is harmless and production callers always pass the mapping via the assembler. The "# legacy" label is accurate documentation, not a bug. No action needed.

### MINOR — `game/ui/screens/test_lab/dialogs.py:256` — "# Old" comment

**Finding:** Line 256's `# Old value (strikethrough)` comment is an inline UI rendering annotation describing the visual style of a stale value in a comparison display. Not a legacy code indicator — just a UI layout comment. No action needed.

## Wrapper Delegate Findings

### MINOR — `game/simulation/systems/battle_engine.py:687` — `_collect_new_attacks` pass-through

**Finding:** The method `BattleEngine._collect_new_attacks` (line 687) is a one-line pass-through to `_attacks.collect_new_attacks(self, alive_ships)`. It has one production caller in `tick_phase.py:149` (`AttackProcessingPhase.execute()` calls `engine._collect_new_attacks(engine._alive_ships_cache)`). The wrapper preserves the BattleEngine's method surface for the tick phase system; this is a legitimate architectural delegation (PROJ-382 Phase 5 extraction to stay under 500 LOC). Not dead code.

## Name-Pair Drift Findings

**None.** Deterministic scan found zero name-pair drift entries. Independent review confirmed — no semantic pairs with one member using a legacy name.

## Save Migration Code Findings

**None.** Deterministic scan found zero save migration patterns. All serialization in this shard uses the canonical `to_dict`/`from_dict`/`to_json`/`from_json` patterns consistent with the current save format.

## Superseded Pattern Usage Findings

**None.** Pattern 30 (Registrar Close-Callback) is superseded by Pattern 31 (Strategy Modal Window Base Class), but the scan found zero uses of Pattern 30's close-callback mechanism in this shard. All modal registration in files like `game/ui/screens/strategy_windows/` and `game/ui/screens/strategy_modal_window.py` uses Pattern 31.

**Note:** `bypass_init` is used extensively across 46 locations in these files (e.g., `new_game_setup_screen.py:186`, `race_setup/screen.py:149`, `strategy_modal_window.py:118`). This is Pattern 33 (UI Widget Test Factory) — a **current** documented pattern, not superseded. No finding.

## TYPE_CHECKING Re-export Findings

**None.** Deterministic scan found zero TYPE_CHECKING-only re-exports. Verified — all `TYPE_CHECKING` imports in the shard serve circular-dependency resolution purposes and are not preserving legacy import paths.

## Partial Protocol Implementer Findings

**None.** Deterministic scan found zero partial Protocol implementers. Verified — the Protocol implementations in this shard (e.g., `IAIControllerFactory`, `ICombatShip`, `IComponent`, `IReplayCaptureSink`, etc.) are fully wired in production.

## Additional Legacy Indicators (Phase 1 did not catch)

### MINOR — `game/ai/policy_manager.py:22-37` — Module-level default without public setter

**Finding:** `PolicyManager` has a `get_default_policy_manager()` function that auto-creates on first access, but no corresponding `set_default_policy_manager()` function. The module-level `_default_policy_manager` variable is set only by `ApplicationContext.create_production()` at `game/context.py:190` via direct module attribute access: `_pm_module._default_policy_manager = policy_manager`. This is the "unused set_default_* shim" anti-pattern in reverse — the module has a getter but the setter is an undocumented direct assignment from the DI container. Compare with other services (`AssetManager`, `Profiler`, `SpriteManager`) which all have explicit `set_default_xxx()` functions. **Add `set_default_policy_manager()` for parity, with the same docstring pattern as `set_default_asset_manager`.**

### MINOR — `game/simulation/components/component.py:391-405` — Re-exports from extacted module

**Finding:** The `Component` module re-exports 8 symbols from `component_loader.py` (`ComponentCacheManager`, `get_default_cache_manager`, `reset_component_caches`, `load_components_data`, `load_components`, `load_modifiers_data`, `load_modifiers`, `create_component`, `get_all_components`). These are deliberate re-exports per Pattern 36 (Re-Export Shim) — the decomposition moved loader logic out but preserved the import path for existing callers. The old `from game.simulation.components.component import ComponentCacheManager` import path still works. These re-exports are **documented and tied to a tracked migration project** (the module docstring line 387 explains the purpose). No finding — this is Pattern 36 compliance.

## Verification Coverage
- Critical findings verified: 0/0 (N/A — no critical findings)
- Major findings sampled: 1/1 (100%)
  - `planetary_facility.py` deprecated fuel wrappers: Verified via grep for production callers (`resupply_engine.py`) and test callers (`tests/unit/strategy/data/test_facility_resource_tracking.py`). Confirmed F-A-012 ticket has no linked PROJ project or removal timeline.
- Minor findings sampled: 2/5 (40%) — sampled the `_null_provider` and `_default_policy_manager` findings

## File Coverage Verification
| File | Status |
|------|--------|
| 1. game/ai/__init__.py | Read ✓ |
| 2. game/ai/policy_manager.py | Read ✓ |
| 3. game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| 4. game/assets/asset_manager.py | Read ✓ |
| 5. game/context.py | Read ✓ |
| 6. game/core/__init__.py | Read ✓ |
| 7. game/core/config.py | Read ✓ |
| 8. game/core/constants.py | Read ✓ |
| 9. game/core/math.py | Read ✓ |
| 10. game/core/profiling.py | Read ✓ |
| 11. game/core/protocols/common.py | Read ✓ |
| 12. game/core/protocols/ui.py | Read ✓ |
| 13. game/core/ship_classes.py | Read ✓ |
| 14. game/core/string_utils.py | Read ✓ |
| 15. game/engine/physics.py | Read ✓ |
| 16. game/research/data/tech_tree.py | Read ✓ |
| 17. game/research/systems/__init__.py | Read ✓ |
| 18. game/services/llm/background.py | Read ✓ |
| 19. game/services/llm/deepseek.py | Read ✓ |
| 20. game/services/llm/factory.py | Read ✓ |
| 21. game/services/llm/types.py | Read ✓ |
| 22. game/simulation/battle_outcome.py | Read ✓ |
| 23. game/simulation/battle_runner.py | Read ✓ |
| 24. game/simulation/battle_state.py | Read ✓ |
| 25. game/simulation/combat/__init__.py | Read ✓ |
| 26. game/simulation/combat/attack_contract.py | Read ✓ |
| 27. game/simulation/combat/families/__init__.py | Read ✓ |
| 28. game/simulation/combat/families/projectile.py | Read ✓ |
| 29. game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| 30. game/simulation/combat/targeting_system.py | Read ✓ |
| 31. game/simulation/components/abilities/base.py | Read ✓ |
| 32. game/simulation/components/abilities/markers.py | Read ✓ |
| 33. game/simulation/components/abilities/weapons.py | Read ✓ |
| 34. game/simulation/components/component.py | Read ✓ |
| 35. game/simulation/components/modifier_schema.py | Read ✓ |
| 36. game/simulation/entities/ship_design_stats.py | Read ✓ |
| 37. game/simulation/entities/stat_contributors/__init__.py | Read ✓ |
| 38. game/simulation/entities/stat_contributors/command.py | Read ✓ |
| 39. game/simulation/entities/stat_contributors/defense.py | Read ✓ |
| 40. game/simulation/entities/stat_contributors/launch.py | Read ✓ |
| 41. game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| 42. game/simulation/interfaces/component_protocols.py | Read ✓ |
| 43. game/simulation/managers/__init__.py | Read ✓ |
| 44. game/simulation/replay/__init__.py | Read ✓ |
| 45. game/simulation/replay/replay_capture.py | Read ✓ |
| 46. game/simulation/services/battle_service.py | Read ✓ |
| 47. game/simulation/systems/attack_processor.py | Read ✓ |
| 48. game/simulation/systems/battle_engine.py | Read ✓ |
| 49. game/simulation/systems/battle_logger.py | Read ✓ |
| 50. game/simulation/systems/battle_setup.py | Read ✓ |
| 51. game/simulation/systems/tactical_mine_resolver.py | Read ✓ |
| 52. game/simulation/systems/tech_preset_loader.py | Read ✓ |
| 53. game/simulation/systems/tick_phase.py | Read ✓ |
| 54. game/strategy/adapters/simulation_adapter.py | Read ✓ |
| 55. game/strategy/combat/post_battle_hook_builder.py | Read ✓ |
| 56. game/strategy/data/classification_config.py | Read ✓ |
| 57. game/strategy/data/design_role.py | Read ✓ |
| 58. game/strategy/data/environmental_preference.py | Read ✓ |
| 59. game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| 60. game/strategy/data/fleet_hierarchy.py | Read ✓ |
| 61. game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| 62. game/strategy/data/galaxy_state.py | Read ✓ |
| 63. game/strategy/data/homeworld_presets.py | Read ✓ |
| 64. game/strategy/data/orbital_generation_config.py | Read ✓ |
| 65. game/strategy/data/physics.py | Read ✓ |
| 66. game/strategy/data/planet.py | Read ✓ |
| 67. game/strategy/data/planet_atmosphere.py | Read ✓ |
| 68. game/strategy/data/planet_gen.py | Read ✓ |
| 69. game/strategy/data/planet_gen_surface.py | Read ✓ |
| 70. game/strategy/data/planetary_facility.py | Read ✓ |
| 71. game/strategy/data/resource_generation_config.py | Read ✓ |
| 72. game/strategy/data/spectrum.py | Read ✓ |
| 73. game/strategy/data/task_force.py | Read ✓ |
| 74. game/strategy/engine/commands/order_metadata_view.py | Read ✓ |
| 75. game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| 76. game/strategy/engine/game_initializer.py | Read ✓ |
| 77. game/strategy/engine/game_session.py | Read ✓ |
| 78. game/strategy/engine/handlers/launch_fighters.py | Read ✓ |
| 79. game/strategy/engine/handlers/recover_fighters.py | Read ✓ |
| 80. game/strategy/engine/handlers/transfer.py | Read ✓ |
| 81. game/strategy/engine/happiness_engine.py | Read ✓ |
| 82. game/strategy/engine/movement_phase_collaborator.py | Read ✓ |
| 83. game/strategy/engine/order_handlers/join_fleet.py | Read ✓ |
| 84. game/strategy/engine/order_handlers/launch_satellites.py | Read ✓ |
| 85. game/strategy/engine/order_handlers/recover_fighters.py | Read ✓ |
| 86. game/strategy/engine/order_handlers/registry_factory.py | Read ✓ |
| 87. game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| 88. game/strategy/engine/production_engine.py | Read ✓ |
| 89. game/strategy/engine/production_math.py | Read ✓ |
| 90. game/strategy/engine/resupply_engine.py | Read ✓ |
| 91. game/strategy/engine/session/__init__.py | Read ✓ |
| 92. game/strategy/engine/superweapon_handlers/create_dyson_sphere.py | Read ✓ |
| 93. game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| 94. game/strategy/engine/turn_engine.py | Read ✓ |
| 95. game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| 96. game/strategy/events/__init__.py | Read ✓ |
| 97. game/strategy/events/event_log.py | Read ✓ |
| 98. game/strategy/facade/dto/__init__.py | Read ✓ |
| 99. game/strategy/facade/dto/fleet_dto.py | Read ✓ |
| 100. game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| 101. game/strategy/facade/dto/system_dto.py | Read ✓ |
| 102. game/strategy/facade/grouped_namespaces.py | Read ✓ |
| 103. game/strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| 104. game/strategy/facade/slices/planet_slice.py | Read ✓ |
| 105. game/strategy/facade/slices/system_slice.py | Read ✓ |
| 106. game/strategy/formulas/__init__.py | Read ✓ |
| 107. game/strategy/formulas/colony_output.py | Read ✓ |
| 108. game/strategy/generation/density/primitives/__init__.py | Read ✓ |
| 109. game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| 110. game/strategy/generation/density/primitives/noise.py | Read ✓ |
| 111. game/strategy/generation/density/primitives/ring.py | Read ✓ |
| 112. game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| 113. game/strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| 114. game/strategy/generation/storm_generator.py | Read ✓ |
| 115. game/strategy/interfaces/battle_resolver.py | Read ✓ |
| 116. game/strategy/interfaces/engines/planet_ops.py | Read ✓ |
| 117. game/strategy/interfaces/engines/terraforming.py | Read ✓ |
| 118. game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| 119. game/strategy/services/action_time_resolver.py | Read ✓ |
| 120. game/strategy/services/design_cost_calculator.py | Read ✓ |
| 121. game/strategy/services/design_validator.py | Read ✓ |
| 122. game/strategy/services/empire_write_service.py | Read ✓ |
| 123. game/strategy/services/fleet_path_projection.py | Read ✓ |
| 124. game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| 125. game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| 126. game/strategy/services/race_resolver.py | Read ✓ |
| 127. game/strategy/services/replay_store.py | Read ✓ |
| 128. game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| 129. game/strategy/services/ship_instance_factory.py | Read ✓ |
| 130. game/strategy/services/ship_instance_write_service.py | Read ✓ |
| 131. game/strategy/services/system_destroyer.py | Read ✓ |
| 132. game/strategy/systems/design_catalog.py | Read ✓ |
| 133. game/strategy/systems/design_repository.py | Read ✓ |
| 134. game/strategy/validation/__init__.py | Read ✓ |
| 135. game/strategy/validation/planet_order_validator.py | Read ✓ |
| 136. game/ui/assets/ship_theme_manager.py | Read ✓ |
| 137. game/ui/components/__init__.py | Read ✓ |
| 138. game/ui/components/table/column_manager.py | Read ✓ |
| 139. game/ui/filters/filter_state_manager.py | Read ✓ |
| 140. game/ui/orchestration/__init__.py | Read ✓ |
| 141. game/ui/panels/build_queue_portraits.py | Read ✓ |
| 142. game/ui/panels/builder_widgets.py | Read ✓ |
| 143. game/ui/panels/design_report_panel.py | Read ✓ |
| 144. game/ui/panels/planet_report_panel.py | Read ✓ |
| 145. game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| 146. game/ui/panels/race_portrait_gallery.py | Read ✓ |
| 147. game/ui/panels/ship_stats_renderer.py | Read ✓ |
| 148. game/ui/panels/strategy_widgets.py | Read ✓ |
| 149. game/ui/renderer/camera.py | Read ✓ |
| 150. game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ |
| 151. game/ui/screens/battle_setup/panels/left_panel.py | Read ✓ |
| 152. game/ui/screens/battle_setup_state.py | Read ✓ |
| 153. game/ui/screens/build_queue_helpers.py | Read ✓ |
| 154. game/ui/screens/build_queue_screen.py | Read ✓ |
| 155. game/ui/screens/builder/__init__.py | Read ✓ |
| 156. game/ui/screens/builder/components.py | Read ✓ |
| 157. game/ui/screens/builder/modifier_logic.py | Read ✓ |
| 158. game/ui/screens/builder/modifier_utils.py | Read ✓ |
| 159. game/ui/screens/builder/schematic_view.py | Read ✓ |
| 160. game/ui/screens/builder/stats_config.py | Read ✓ |
| 161. game/ui/screens/builder_selection.py | Read ✓ |
| 162. game/ui/screens/builder_utils.py | Read ✓ |
| 163. game/ui/screens/cargo_quick_dialog.py | Read ✓ |
| 164. game/ui/screens/data_list_window_mixin.py | Read ✓ |
| 165. game/ui/screens/empire_panel_window.py | Read ✓ |
| 166. game/ui/screens/fleet_report_window.py | Read ✓ |
| 167. game/ui/screens/fleet_selection_window.py | Read ✓ |
| 168. game/ui/screens/fms_menu_callbacks.py | Read ✓ |
| 169. game/ui/screens/galaxy_test/constants.py | Read ✓ |
| 170. game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ |
| 171. game/ui/screens/list_filter_utils.py | Read ✓ |
| 172. game/ui/screens/new_game_setup_screen.py | Read ✓ |
| 173. game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| 174. game/ui/screens/per_player_ui_state.py | Read ✓ |
| 175. game/ui/screens/planet_abilities_controller.py | Read ✓ |
| 176. game/ui/screens/planet_list_helpers.py | Read ✓ |
| 177. game/ui/screens/planet_selection_window.py | Read ✓ |
| 178. game/ui/screens/race_browser_dialog.py | Read ✓ |
| 179. game/ui/screens/race_setup/panel_factory.py | Read ✓ |
| 180. game/ui/screens/race_setup/screen.py | Read ✓ |
| 181. game/ui/screens/species_selector_mixin.py | Read ✓ |
| 182. game/ui/screens/star_data_source.py | Read ✓ |
| 183. game/ui/screens/strategy_fleet_context_menu.py | Read ✓ |
| 184. game/ui/screens/strategy_menu_panel.py | Read ✓ |
| 185. game/ui/screens/strategy_panel_manager.py | Read ✓ |
| 186. game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| 187. game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| 188. game/ui/screens/strategy_renderer.py | Read ✓ |
| 189. game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| 190. game/ui/screens/strategy_screen_order_editing.py | Read ✓ |
| 191. game/ui/screens/strategy_ui.py | Read ✓ |
| 192. game/ui/screens/strategy_windows/__init__.py | Read ✓ |
| 193. game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| 194. game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| 195. game/ui/screens/test_lab/details/resource_outcomes.py | Read ✓ |
| 196. game/ui/screens/test_lab/details/validation.py | Read ✓ |
| 197. game/ui/screens/test_lab/dialogs.py | Read ✓ |
| 198. game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| 199. game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| 200. game/ui/screens/test_lab/results_panel.py | Read ✓ |
| 201. game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| 202. game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| 203. game/ui/screens/workshop_context.py | Read ✓ |
| 204. game/ui/screens/workshop_ship_io.py | Read ✓ |
| 205. game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| 206. game/ui/services/image/__init__.py | Read ✓ |
| 207. game/ui/services/image/defaults.py | Read ✓ |
| 208. game/ui/services/image/factory.py | Read ✓ |
| 209. game/ui/services/image/provider.py | Read ✓ |
| 210. game/ui/services/vehicle_class_service.py | Read ✓ |
| 211. game/ui/utils/json_diff.py | Read ✓ |
| 212. game/ui/utils/portraits.py | Read ✓ |
| 213. game/ui/utils/pygame_utils.py | Read ✓ |
| 214. game/ui/widgets/column_toggle_section.py | Read ✓ |
