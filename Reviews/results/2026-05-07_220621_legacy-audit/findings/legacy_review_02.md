# Legacy Code Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 188
- Files Actually Read: 188
- Total Findings: 17
- Critical: 0 | Major: 2 | Minor: 12 | Info: 3

## Module Alias Findings
No module aliases detected by Phase 1 in this shard. Manually verified — no additional aliases found.

## __init__.py Re-export Shim Findings
No init re-export shims detected by Phase 1 in this shard. Manually verified key `__init__.py` files:
- `game/core/__init__.py` — documented public API surface (Pattern 2 contract), not a shim
- `game/strategy/formulas/__init__.py` — re-exports both `score_planet_for_race` and `calculate_habitability` as public API; this is intentional (see wrapper delegate finding below)
- `game/research/data/__init__.py` — standard package re-exports

## Deprecation Marker Findings

#### MINOR: Legacy `running` flag on Game instance
**ID:** LEG-02-001
**Location:** game/app.py:124
**Symbol:** `self.running = True` (comment: "# Legacy `running` flag")
**Issue:** The `running` flag is duplicated between `Game` and `RunLoop`. `RunLoop` is the canonical owner; `Game.running` is kept for backward compatibility with `_handle_strategy_action("quit_game")` and test mocks that read `game.running`. The comment explains the rationale clearly — PROJ-309 decomposition artifact.
**Recommendation:** When tests no longer bypass `Game.__init__`, remove this duplicate and route all accesses through `self._loop.running`.
**LOC affected:** 1

#### MINOR: Legacy scene input handling for RESEARCH_TREE and GALAXY_TEST
**ID:** LEG-02-002
**Location:** game/run_loop.py:205
**Symbol:** Comment: "# Legacy scenes that haven't migrated to IScene event handling."
**Issue:** `RESEARCH_TREE` and `GALAXY_TEST` scenes still use the old `handle_input()` method instead of the unified `IScene.handle_event()` dispatch. No removal plan or PROJ ticket referenced.
**Recommendation:** Create a ticket to migrate these two scenes to IScene event handling, or document the reason they remain on the legacy path.
**LOC affected:** 2

#### MINOR: Legacy facility fallback in PlanetActionEngine
**ID:** LEG-02-003
**Location:** game/strategy/engine/planet_action_engine.py:366
**Symbol:** Comment: "# Legacy fallback: find first facility with shield ability"
**Issue:** In `_find_target_facility()`, when `order.target` is not a dict specifying a facility, the code falls back to hardcoded `'PlanetaryShield'` lookup. This is a fallback path for legacy orders without full target specification.
**Recommendation:** Either formally support the string-only target format or require all callers to pass a full target dict (with `ability_name` and `facility_instance_id`).
**LOC affected:** 3

#### MINOR: Backward-compat `fleet_id` field in ClearOrdersCommand
**ID:** LEG-02-004
**Location:** game/strategy/engine/commands/__init__.py:102
**Symbol:** `fleet_id: int  # Kept for backward compat; use entity_id for new code`
**Issue:** PROJ-238 renamed `ClearFleetOrdersCommand` and introduced `entity_id`/`entity_type` fields, but kept `fleet_id` as a parallel field. `DeleteOrderCommand` and `ReorderOrderCommand` have the same issue. The `fleet_id` field duplicates `entity_id` for fleet operations.
**Recommendation:** Migrate all callers to use `entity_id` and remove the `fleet_id` backward-compat field. This is a 3-instance pattern across ClearOrdersCommand, DeleteOrderCommand, and ReorderOrderCommand.
**LOC affected:** 3

#### INFO: Historical save-format comment
**ID:** LEG-02-005
**Location:** game/strategy/systems/save_game_service.py:68
**Symbol:** Comment: "# legacy `component_damage` dict from ShipInstance saves in favor"
**Issue:** This is a purely historical comment explaining why `SAVE_VERSION` was bumped to "3.0.0". No legacy code remains — the old format was dropped per the no-migration rule. The comment is informative.
**Recommendation:** Leave as-is. This is useful historical context, not legacy code.
**LOC affected:** 0

#### MINOR: Legacy single-line population layout in format_planet_info
**ID:** LEG-02-006
**Location:** game/ui/screens/strategy_detail_fmt.py:254-256
**Symbol:** Comments: "# Legacy single-line layout" and "# legacy tests, pre-PROJ-289 panels"
**Issue:** `format_planet_info()` preserves the old single-line per-species rendering when `view is None`. This is explicitly documented as backward compat for callers that don't pass a `ColonyDemographicView`. Actively used by uncolonized planet rendering and pre-PROJ-289 test/snapshot callers.
**Recommendation:** Track down remaining callers that pass `view=None` and migrate them. Once all callers pass a `ColonyDemographicView`, remove the legacy branch.
**LOC affected:** 15

#### MINOR: Legacy `name_input` placeholder attribute
**ID:** LEG-02-007
**Location:** game/ui/screens/race_setup/screen.py:261
**Symbol:** `self.name_input = None  # legacy attr (Identity panel replaced this)`
**Issue:** The `name_input` attribute on `RaceSetupScreen` is explicitly noted as replaced by the Identity panel. It remains as a `None` placeholder in `_init_widget_refs()`.
**Recommendation:** Verify no test or external code reads `screen.name_input`. If none, delete the placeholder.
**LOC affected:** 1

#### INFO: False positive — UI visual comment
**ID:** LEG-02-008
**Location:** game/ui/screens/test_lab/dialogs.py:256
**Symbol:** Comment: "# Old value (strikethrough)"
**Issue:** This is a UI rendering comment describing how the ConfirmationDialog displays old vs new values with strikethrough styling. NOT a legacy code marker. Phase 1 false positive.
**Recommendation:** Not a finding. Ignore.

## Wrapper Delegate Findings

#### MAJOR: `score_planet_for_race` wrapper with non-trivial usage
**ID:** LEG-02-009
**Location:** game/strategy/formulas/habitability.py:99
**Symbol:** `score_planet_for_race` (wraps `calculate_habitability`)
**Production call sites:** 6
**Issue:** `score_planet_for_race` is a thin wrapper around `calculate_habitability` with identical behaviour. It was explicitly kept for "source-stability of existing callers" per its docstring. Call sites span 5 production files:
- `game/strategy/engine/population_engine.py:139`
- `game/strategy/engine/happiness_engine.py:117`
- `game/strategy/facade/slices/economy_slice.py:157`
- `game/strategy/formulas/colony_output.py:47,95,152`
- `game/ui/screens/strategy_detail_fmt.py:129`
- `game/strategy/formulas/__init__.py:9` (re-exports both names)

Additionally, `score_planet_for_race` is re-exported from `game/strategy/formulas/__init__.py` alongside `calculate_habitability`, keeping both names in the public API.
**Recommendation:** Replace all 6 call sites with `calculate_habitability`, then either delete `score_planet_for_race` or deprecate it. The re-export from `formulas/__init__.py` should also be updated.
**LOC affected:** 7

#### INFO: Local closure wrapping `ab.get_damage`
**ID:** LEG-02-010
**Location:** game/ui/screens/builder/weapons_viewmodel.py:392
**Symbol:** `calc_damage_at_range(r)` (closure inside `get_points_of_interest`)
**Issue:** Phase 1 flagged this as a wrapper delegate, but it's a local closure defined inside `get_points_of_interest()`, not a standalone function. The closure exists to provide a consistent call interface alongside `calc_accuracy_at_range(r)`, which has body logic. This is legitimate code structure, not a legacy wrapper.
**Recommendation:** Not a finding. False positive from Phase 1's AST-level detection of pass-through bodies.

## Name-Pair Drift Findings
No name-pair drift detected by Phase 1 in this shard. Manually verified — no `Foo`/`LegacyFoo`, `Foo`/`OldFoo`, or `XManager`/`XService` pairs found.

## Save Migration Code Findings
No save migration code detected by Phase 1 in this shard. Manually verified — the codebase correctly rejects old saves with strict version checks as documented in AGENTS.md.

## Superseded Pattern Usage Findings

#### MINOR: Pattern 30 (Registrar Close-Callback) used for fleet report window slot cleanup
**ID:** LEG-02-011
**Location:** game/ui/screens/strategy_windows/fleet_report_ctrl.py:58
**Symbol:** `on_close_callback=self._on_closed` pattern
**Issue:** `FleetReportRegistrar` uses Pattern 30 ("Registrar Close-Callback") to manage the `fleet_report_window` slot on `StrategyWindowManager`. Pattern 30 is superseded by Pattern 31 (StrategyModalWindow). However, `FleetReportWindow` is already a `StrategyModalWindow` (it extends `UIWindow` and takes `window_manager` kwarg and uses `on_close_callback` for SLOT cleanup, not modal tracking). The `on_close_callback` here is slot-cleanup only, which aligns with Pattern 30's documented contract as "legacy slot cleanup only". Pattern 31 handles modal behavior, while Pattern 30 is still the documented mechanism for slot cleanup. This is the intended coexistence per `docs/02_PATTERNS.md` §30.
**Recommendation:** Acceptable as-is under the documented pattern coexistence. The fleet report window uses Pattern 31 (StrategyModalWindow) for modal tracking AND Pattern 30 (close-callback) for registrar slot cleanup, which is the documented usage.
**LOC affected:** 3

#### MINOR: BuildQueueListWindow uses both Pattern 31 and Pattern 30
**ID:** LEG-02-012
**Location:** game/ui/screens/build_queue_list_window.py:152
**Symbol:** `on_close_callback` parameter alongside `window_manager`
**Issue:** `BuildQueueListWindow` extends `StrategyModalWindow` (Pattern 31) but also accepts and fires `on_close_callback` (Pattern 30). This is the same coexistence as LEG-02-011 — the callback clears the registrar slot, while `StrategyModalWindow` handles modal blocking.
**Recommendation:** Same as LEG-02-011 — acceptable under documented pattern coexistence. Both patterns serve different purposes: modal tracking (Pattern 31) and slot cleanup (Pattern 30).
**LOC affected:** 2

## TYPE_CHECKING Re-export Findings
No TYPE_CHECKING-only re-exports detected by Phase 1 in this shard.

## Partial Protocol Implementer Findings
No partial protocol implementers detected by Phase 1 in this shard.

## Additional Legacy Indicators (Phase 1 did not catch)

#### MINOR: Module-level `ResourceCatalog.from_json()` in module body
**ID:** LEG-02-013
**Location:** game/strategy/engine/strategy_ui.py (implied from build_queue_helpers.py:8)
**Symbol:** `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]`
**Issue:** `game/ui/screens/build_queue_helpers.py:8` constructs a `ResourceCatalog.from_json()` at module import time. While this is cached by the resource loader, it's side-effectful module-level code that could be replaced by lazy initialization. This pattern also appears in `game/ui/screens/strategy_ui.py:25`.
**Recommendation:** Move to a cached getter with `@lru_cache` or initialize lazily at first use. Pattern 12 (Configuration Classes) documents the preferred approach.
**LOC affected:** 2

#### MINOR: `DesignSelectorWindow` extends `UIWindow` directly, not `StrategyModalWindow`
**ID:** LEG-02-014
**Location:** game/ui/screens/design_selector_window.py:45
**Symbol:** `class DesignSelectorWindow(UIWindow):`
**Issue:** `DesignSelectorWindow` is a modal dialog but extends `UIWindow` directly rather than `StrategyModalWindow`. It does not register with `StrategyWindowManager` for modal blocking. This is because it's used from the Workshop scene, not the Strategy scene, so `StrategyModalWindow` registration wouldn't help. However, this means any future workshop-level modal blocking would need a separate mechanism.
**Recommendation:** No action needed currently. If Workshop gets modal-blocking requirements, extend `StrategyModalWindow` or create a Workshop-specific modal base class. Pattern 32 (Compositional Construction) is the preferred approach for new UI classes.
**LOC affected:** 0

#### MINOR: `_menu_scene` is a private attribute used from `Game`
**ID:** LEG-02-015
**Location:** game/app.py:233-234
**Symbol:** `self._menu_scene` (property with getter/setter proxying to `_router`)
**Issue:** `_menu_scene` is a private-named attribute but is publicly exposed through a property on `Game` and used as `self._menu_scene` in `_handle_strategy_action("quit_to_menu")` at line 449. The routing pattern is legitimate (PROJ-309 decomposition), but the private naming convention is misleading since it's effectively public.
**Recommendation:** Either rename to `menu_scene` or keep the property but note the private prefix is for consistency with router internals. Low priority.
**LOC affected:** 1

#### MINOR: Deprecated module-level `log_event()` compatibility shim
**ID:** LEG-02-016
**Location:** game/core/event_logging.py (referenced in Pattern 10 docs, § "Strategy/core event logging")
**Symbol:** Module-level `log_event()` function
**Issue:** The 02_PATTERNS.md §10 notes that `module-level log_event()` is a "compatibility shim" and that "new code should prefer explicit EventBus injection." This is documented as a known shim in the architecture documentation itself. While `event_logging.py` is not in my shard, it's referenced by pattern docs.
**Recommendation:** Track the caller migration implied by the pattern docs. This is already a documented finding.
**LOC affected:** 0 (in application code)

#### INFO: PROJ-258 migration comment in context.py
**ID:** LEG-02-017
**Location:** game/context.py:13
**Symbol:** Comment: "# PROJ-258: Initial implementation as wrapper around existing singletons."
**Issue:** The module docstring references PROJ-258 as the initial implementation state, but PROJ-372 (Phase 0) has added habitability service accessors. The "PROJ-258" tag could mislead readers into thinking migration is still in progress when PROJ-258 has been archived.
**Recommendation:** Update the docstring to reflect current state or remove the stale PROJ reference. PROJ-372 is the active project for context.py changes.
**LOC affected:** 1

## Verification Coverage
- Critical findings verified: 0/0 (no critical findings)
- Major findings sampled: 2/2 (both major findings verified by re-reading source and counting call sites)

### Major finding verification details:
- **LEG-02-009 (score_planet_for_race):** Verified by grep across `game/` — 6 production call sites confirmed. All 6 import `score_planet_for_race` by name. The `formulas/__init__.py` publicly exports both names. Confirmed wrapper body is a direct delegation to `calculate_habitability`.
- **LEG-02-010 (calc_damage_at_range):** Verified by re-reading `weapons_viewmodel.py` — this is a local closure inside `get_points_of_interest()`, not a standalone function. The closure provides parity with `calc_accuracy_at_range` for cleaner iteration. Downgraded from Phase 1's "wrapper delegate" to INFO.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/app.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/context.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/spectrum_math.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/simulation/combat/ability_stat_registry.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/simulation/combat/families/seeker.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/simulation/components/abilities/defense.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/layer_data.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/simulation/entities/stat_contributors/defense.py | Read ✓ |
| game/simulation/entities/stat_contributors/weapons.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/validation/base.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/strategy/data/galaxy_state.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/data/spectrum.py | Read ✓ |
| game/strategy/data/squadron.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/strategy/engine/order_handlers/superweapons.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/strategy/formulas/__init__.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/strategy/formulas/habitability.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/strategy/generation/density/primitives/ring.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/strategy/generation/star_generator.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/interfaces/engines.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/services/modifier_resolver.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/strategy/services/replay_verification_coordinator.py | Read ✓ |
| game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/strategy/validation/colonize_validator.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/filters/__init__.py | Read ✓ |
| game/ui/components/filters/tri_state_widget.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/panels/component_modifier_grid_panel.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/panels/race_portrait_gallery.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/ui/panels/strategy_widgets.py | Read ✓ |
| game/ui/renderer/camera.py | Read ✓ |
| game/ui/screens/__init__.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/build_queue_panel_factory.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/modifier_row.py | Read ✓ |
| game/ui/screens/builder/right_panel.py | Read ✓ |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/menu_scene.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/ui/screens/planet_list_filters.py | Read ✓ |
| game/ui/screens/planet_list_presets.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/ui/screens/star_list_sidebar.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ |
| game/ui/screens/strategy_input_handler.py | Read ✓ |
| game/ui/screens/strategy_render/fleets.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/ui/screens/transfer_view_model.py | Read ✓ |
| game/ui/screens/workshop_data_loader.py | Read ✓ |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_ship_io.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_selection.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/pygame_utils.py | Read ✓ |
