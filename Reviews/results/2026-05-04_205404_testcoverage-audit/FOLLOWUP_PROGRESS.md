# Coverage Follow-up Progress

Source audit: `Reviews/results/2026-05-04_205404_testcoverage-audit/SUMMARY.md` and `SUMMARY.json`.

## Coordination

Five Codex worker agents were started with disjoint ownership:

| Worker | Slice | Primary test paths |
|---|---|---|
| A | Core/simulation protocols and replay DTOs | `tests/unit/core/test_protocols_boundary.py`, `tests/unit/simulation/interfaces/test_ability_protocols.py`, `tests/unit/simulation/replay/` |
| B | Strategy facade slices and DTOs | `tests/unit/strategy/facade/slices/`, `tests/unit/strategy/facade/dto/test_build_queue_dto.py` |
| C | Strategy services/data helpers | `tests/unit/strategy/services/`, `tests/unit/strategy/validation/`, `tests/unit/strategy/data/` |
| D | Simulation components/resources helpers | `tests/unit/simulation/` component, ability, resource-manager tests |
| E | UI pure-Python helpers and one AI helper | `tests/unit/ui/`, `tests/unit/ai/` |

## Completed Locally

| Claim | Result | Notes |
|---|---|---|
| `game/context.py` LLM/Image provider fallback paths lack targeted tests | Covered | Added `ApplicationContext.create_production()` tests for `LLMConfigError` -> `None`, `ImageConfigError` -> `NullImageProvider`, and `create_test()` image fallback. |
| `game/app.py` `_request_shutdown`, `_return_to`, `start_replay` lack unit tests | Covered | Added bootstrap-free `Game.__new__` tests for shutdown, return destinations, and replay config construction. |
| `game/run_loop.py` lacks automated coverage | Partially covered | Added event-routing tests for shutdown, exit dialog Esc/yes/cancel, global exit/profiler hotkeys, menu overlay forwarding, resize plumbing, strategy update/draw, and battle headless draw skip. Full `run()` loop startup/shutdown remains a follow-up. |
| `game/core/roles.py` `_fire_invalidation_callbacks` re-entrance guard untested | Disputed | Existing `tests/unit/core/test_role_registry.py::TestRoleRegistryInvalidation::test_reentrant_add_user_role_in_callback_does_not_recurse` directly covers the guard and nested mutation behavior. |

## Worker Results

| Worker | Result | Notes |
|---|---|---|
| A | Completed | `ability_protocols.py` gap confirmed and covered. `boundary.py` was partial; added missing `IResourceHolder` and `get_resource_names()` coverage. `replay_record.py` and `replay_outcome.py` claims disputed because `tests/unit/simulation/replay/test_serialization.py` already covers round trips. |
| B | Completed | Facade slice/DTO direct coverage gaps confirmed. Added focused tests for `FacadeSessionState`, `PlanetSlice`, `EmpireSlice`, `SystemSlice`, and `BuildQueueSourceDTO`. New DTO test exposed a real nested-shallow-copy bug and fixed it with `deepcopy()`. |
| C | Completed | Added strategy-helper coverage for `StarAbilitySource`, `_facility_has_ability`, `race_resolver.py`, `planet_physics.py`, and `FleetCapabilityCalculator.list_abilities()`. No production changes needed. |
| D | Completed | Added simulation-helper coverage for `BattleConfig`, `get_ability_default_scope`, weapon helper fallbacks, resource ability edges, resource manager edge helpers, and component health facade paths. No production changes needed. |
| E | Completed | Added pure helper coverage for `ListDataSource`, `GameSettings`, builder grouping strategies, stat definitions, and `get_capability_cache_key`. No production changes needed. |

## Test Receipts

| Command | Result |
|---|---|
| `pytest tests/unit/core/test_application_context.py -q` | Passed: 21 tests |
| `pytest tests/unit/test_app_delegators.py -q` | Passed: 6 tests |
| `pytest tests/unit/test_run_loop.py -q` | Passed: 10 tests |
| Worker A targeted protocol/replay suite | Passed: 61 tests |
| Worker B targeted facade slice suite | Passed: 22 tests; broader facade suite passed: 268 tests |
| Worker C targeted strategy-helper suite | Passed: 48 tests |
| Worker D targeted simulation-helper suite | Passed: 257 tests |
| Worker E targeted UI/AI helper suite | Passed: 58 tests |
| Combined targeted suite across all touched files | Passed: 707 tests |

Combined command:

```powershell
pytest tests/unit/core/test_application_context.py tests/unit/core/test_protocols_boundary.py tests/unit/simulation/test_battle_config.py tests/unit/simulation/interfaces/test_ability_protocols.py tests/unit/simulation/components/abilities/test_ability_registry.py tests/unit/simulation/components/abilities/test_resource_consumption.py tests/unit/simulation/components/abilities/test_weapons_isolation.py tests/unit/simulation/components/test_component_health_manager.py tests/unit/simulation/systems/test_resource_manager_edge_cases.py tests/unit/strategy/facade tests/unit/strategy/services/ability_sources/test_star.py tests/unit/strategy/validation/test_planet_order_validator.py tests/unit/strategy/services/test_race_resolver.py tests/unit/strategy/data/test_planet_physics.py tests/unit/strategy/data/test_fleet_capability_calculator.py tests/unit/test_app_delegators.py tests/unit/test_run_loop.py tests/unit/ui/screens/test_list_data_source_base.py tests/unit/ui/services/test_game_settings.py tests/unit/ui/screens/builder/test_grouping_strategies.py tests/unit/ui/screens/builder/test_stat_definitions.py tests/unit/ai/test_combat_utils.py -q -n 0
```

## Production Fixes

| File | Fix |
|---|---|
| `game/strategy/facade/dto/build_queue_dto.py` | `BuildQueueSourceDTO.from_domain()` now deep-copies queue item dictionaries so nested data cannot be mutated through the UI DTO. |

## Pass 2 Results

Second pass started 2026-05-05 with five more worker slices plus two local low-overlap gaps.

| Slice | Result | Notes |
|---|---|---|
| Local | Completed | Added full `RunLoop.run()` one-frame smoke coverage and `normalize_angle()` edge-case coverage. |
| F / command handlers | Completed | Added movement and order-queue handler tests. Found and fixed a `MoveCommandHandler` no-op defect: moving to the current hex now returns success without queueing a `MOVE` order. |
| G / simulation entity helpers | Completed | Added direct coverage for `ShipValidatorHelper`, `ShipResourceManager`, ship stats routing, ship construction branches, and serialization warnings. Found and fixed `_verify_stats` skipping expected zero values. |
| H / app router/dialog | Completed | Added `ScreenRouter` and `exit_dialog` tests for scene callbacks, transitions, dialog rects/clicks/cancel behavior, and load/setup flags. No production changes needed. |
| I / UI builder helpers | Completed | Added `stat_rows_dynamic`, `components`, `stat_getters`, and `workshop_viewmodel_layer_ops` coverage. Found and fixed `ResourceGeneration` tooltip handling, generic ability fallback, resource getter guards, missing-data guards, and a planetary engineering row break bug. |
| J / strategy engine/services | Completed | Added tests for `planet_energy_engine`, `water_engine`, `turn_state_snapshot`, `ability_iterator`, `system_effects_collector`, and `spec_compiler` branches. No production changes needed. |

Pass 2 combined targeted command:

```powershell
pytest tests/unit/core/test_math_vector2.py tests/unit/test_run_loop.py tests/unit/test_screen_router.py tests/unit/test_exit_dialog.py tests/unit/strategy/engine/handlers/test_movement_handlers.py tests/unit/strategy/engine/handlers/test_order_queue_handlers.py tests/unit/simulation/entities/test_ship.py tests/unit/simulation/entities/test_ship_resource_manager.py tests/unit/simulation/entities/test_ship_serialization.py tests/unit/simulation/entities/test_ship_shield_bonus_add.py tests/unit/simulation/entities/test_ship_stats.py tests/unit/simulation/entities/test_ship_validator_helper.py tests/unit/ui/screens/builder/test_stat_rows_dynamic.py tests/unit/ui/screens/builder/test_components.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py tests/unit/strategy/engine/test_planet_energy_engine.py tests/unit/strategy/engine/test_water_engine.py tests/unit/strategy/turn_engine/test_turn_state_snapshot.py tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py tests/unit/strategy/combat/test_spec_compiler.py -q -n 0
```

Pass 2 result: `295 passed`.

## Pass 2 Production Fixes

| File | Fix |
|---|---|
| `game/strategy/engine/handlers/movement.py` | `MoveCommandHandler` now treats current-hex moves as a true no-op instead of queueing a redundant `MOVE` order. |
| `game/simulation/entities/ship_serialization.py` | Expected stat verification now checks present zero-valued expected stats instead of skipping all falsey expected values. |
| `game/ui/screens/builder/components.py` | Component tooltips now recognize `ResourceGeneration` and list generic abilities through `has_ability()` instead of only raw instance keys. |
| `game/ui/screens/builder/stat_getters.py` | Resource getter helpers now tolerate missing `resources`, missing `get_resource_stat`, and non-numeric stat values. |
| `game/ui/screens/builder/stat_rows_dynamic.py` | Dynamic rows now tolerate missing resource/layer APIs and no longer stops planetary engineering row discovery after the first component without a matching ability. |

## Pass 3 Results

Third pass started 2026-05-05 with five subagents plus one local P2/minor slice.

| Slice | Result | Notes |
|---|---|---|
| Local P2/minor | Completed | Added edge coverage for combat protocol TypeGuards rejecting incomplete objects, `FleetAuraManager` unknown-team default bonuses, `ReplayStore._evict_excess()` OSError continuation, and `StormGenerator` placement helpers. `ProjectileManager._apply_hit()` source-weapon/static-damage paths and incident radiation empty/zero-distance branches were disputed because existing tests already cover them. |
| A / remaining UI criticals | Completed | Added focused tests for `OrdersRegistrar`, `TransferGridRenderer`, and Test Lab `MetadataPanel` button hover/baseline branches. No production changes needed. |
| B / Test Lab UI events/cards | Completed | Added `TestRunCard` click/hover/header tests and `TestLabInputHandler` event routing, dialog gating, panel dispatch, and scroll/mouse tests. No production changes needed. |
| C / battle setup, event log, save selection, species selector | Completed | Added controller, replay/failure, save file-operation, and species selector branch coverage. Found and fixed a `BattleSetupController.remove_ship()` defect where removed ships remained assigned to task-force/squadron hierarchy nodes. |
| D / race setup, empire windows, strategy registrars | Completed | Added race setup panel/controller tests, strategy registrar lifecycle tests, and `EmpirePanelWindow` tab/empty-data branch tests. No production changes needed. |
| E / simulation and strategy majors | Completed | Added telemetry guard/modifier trace tests, `_derive_end_reason` disambiguation coverage, planetary strategic ability tests, galaxy warp generator helper tests, and socio re-roll/cancel tests. No production changes needed. |

Pass 3 targeted worker receipts:

| Slice | Command Result |
|---|---|
| Local initial no-test probes | `pytest ... -k unknown_team_returns_zero_bonuses...` -> `32 deselected`; `pytest tests/unit/strategy/services -k evict_excess_continues_after_unlink_oserror -q -n 0` -> `564 deselected`; `pytest tests/unit/core/test_protocols.py -k combat_protocol_typeguards_reject_incomplete_objects -q -n 0` -> `41 deselected` |
| Local targeted suite | `pytest tests/unit/core/test_protocols.py tests/unit/simulation/combat/test_fleet_aura_extended.py tests/unit/strategy/generation/test_storm_generator.py tests/unit/strategy/services/test_replay_store_eviction.py -q -n 0` -> `79 passed` |
| Worker A targeted suite | `13 passed` |
| Worker B targeted suite | `32 passed`; broader Test Lab slice `55 passed` |
| Worker C targeted suite | `131 passed` |
| Worker D targeted suite | `71 passed` |
| Worker E targeted suite | `89 passed` |
| Combined Pass 3 targeted suite | `415 passed` |
| `git diff --check` | Passed |

Combined Pass 3 command:

```powershell
pytest tests/unit/core/test_protocols.py tests/unit/simulation/combat/test_fleet_aura_extended.py tests/unit/strategy/generation/test_storm_generator.py tests/unit/strategy/services/test_replay_store_eviction.py tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py tests/unit/ui/screens/test_transfer_grid_renderer.py tests/unit/ui/screens/test_lab/renderer/test_metadata_panel.py tests/unit/ui/screens/test_lab/test_test_run_card.py tests/unit/ui/screens/test_lab/test_screen_input_handler.py tests/unit/ui/screens/battle_setup/test_controller.py tests/unit/ui/screens/test_event_log_window.py tests/unit/ui/screens/test_event_log_replay_button.py tests/unit/ui/screens/test_save_selection_window.py tests/unit/ui/screens/test_species_selector_mixin.py tests/unit/ui/screens/race_setup/test_panel_factory.py tests/unit/ui/screens/race_setup/test_controller.py tests/unit/ui/screens/strategy_windows/test_build_queue_windows.py tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py tests/unit/ui/screens/strategy_windows/test_list_windows.py tests/unit/ui/screens/test_empire_panel_window.py tests/unit/simulation/combat/test_ship_stats_aggregator.py tests/unit/simulation/combat/test_hit_log_recorder.py tests/unit/simulation/combat/test_hit_log_modifier_trace.py tests/unit/simulation/test_battle_runner.py tests/unit/simulation/components/abilities/test_strategic_abilities.py tests/unit/strategy/data/test_galaxy_warp_generator.py tests/unit/strategy/services/test_race_description_llm_controller.py -q -n 0
```

## Pass 3 Production Fixes

| File | Fix |
|---|---|
| `game/ui/screens/battle_setup/controller.py` | `BattleSetupController.remove_ship()` now also removes the removed ship from task-force lone-ship assignments and squadron membership so battle setup hierarchy state cannot retain deleted ships. |

## Pass 4 Results

Fourth pass started 2026-05-05 with five more worker slices.

| Slice | Result | Notes |
|---|---|---|
| F / builder widgets | Completed | Added focused tests for `WeaponsReportPanel` event/scroll/viewport behavior, `ModifierControlRow` build/update/event/kill branches for supported control types, and `copy_modifiers()` replacement/clone/recalc semantics. No production changes needed. |
| G / strategy UI helpers | Completed | Added focused tests for `StrategyFleetOps`, camera navigation, panel manager resize/tooltips, click dispatcher hit/picking paths, and strategy detail ability-status branches. No production changes needed. |
| H / UI services | Completed | Added OpenAI image-provider edit/error/read-size coverage, NullImageProvider string coverage, and ModifierIconService cache/fallback/missing/load-error/scale coverage. Found and fixed SSL-specific exception handling and invalid-base64 response parsing in `OpenAIImageProvider`. |
| I / view-model and filter helpers | Completed | Added direct branch coverage for transfer view-model sentinel/max/species-row behavior, planet list dot-walk/empty ranges, builder detail-panel selection dispatch, and fleet-report predicates. No production changes needed. |
| J / non-UI edge cases | Completed | Added projectile guidance math, race randomizer helper, resupply fuel-distribution, and fleet order-removal coverage. Found and fixed `Fleet.remove_orders_by_type_and_target()` tracker/path behavior. |

Pass 4 targeted receipts:

| Slice | Command Result |
|---|---|
| Worker F targeted suite | `30 passed`; broader builder slice `103 passed` |
| Worker G targeted suite | `140 passed` |
| Worker H targeted suite | Initial new tests exposed 2 failures; final targeted suite `24 passed`; broader image/service slice `38 passed` |
| Worker I targeted suite | `94 passed` |
| Worker J targeted suite | Initial new tests exposed 2 failures; final targeted suite `78 passed`; related fleet regression suite `64 passed` |
| Combined Pass 4 targeted suite | `426 passed` |
| Combined Pass 3+4 targeted suite | `841 passed` |
| `git diff --check` | Passed |

Combined Pass 4 command:

```powershell
pytest tests/unit/ui/screens/builder/test_weapons_panel.py tests/unit/ui/screens/builder/test_modifier_row.py tests/unit/ui/screens/builder/test_modifier_utils.py tests/unit/ui/screens/test_strategy_fleet_ops.py tests/unit/ui/screens/test_camera_navigator.py tests/unit/ui/screens/test_strategy_panel_manager.py tests/unit/ui/screens/test_strategy_click_dispatcher.py tests/unit/ui/screens/test_strategy_detail_fmt.py tests/unit/ui/services/image/test_openai_provider.py tests/unit/ui/services/image/test_null_provider.py tests/unit/ui/services/test_modifier_icon_service.py tests/unit/ui/screens/test_transfer_view_model.py tests/unit/ui/screens/test_planet_list_filters.py tests/unit/ui/screens/builder/test_detail_panel.py tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/simulation/entities/test_projectile.py tests/unit/strategy/systems/test_race_randomizer_helpers.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/data/test_fleet_order_removal.py tests/unit/strategy/fleet/test_basics.py tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py -q -n 0
```

Combined Pass 3+4 command:

```powershell
pytest tests/unit/core/test_protocols.py tests/unit/simulation/combat/test_fleet_aura_extended.py tests/unit/strategy/generation/test_storm_generator.py tests/unit/strategy/services/test_replay_store_eviction.py tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py tests/unit/ui/screens/test_transfer_grid_renderer.py tests/unit/ui/screens/test_lab/renderer/test_metadata_panel.py tests/unit/ui/screens/test_lab/test_test_run_card.py tests/unit/ui/screens/test_lab/test_screen_input_handler.py tests/unit/ui/screens/battle_setup/test_controller.py tests/unit/ui/screens/test_event_log_window.py tests/unit/ui/screens/test_event_log_replay_button.py tests/unit/ui/screens/test_save_selection_window.py tests/unit/ui/screens/test_species_selector_mixin.py tests/unit/ui/screens/race_setup/test_panel_factory.py tests/unit/ui/screens/race_setup/test_controller.py tests/unit/ui/screens/strategy_windows/test_build_queue_windows.py tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py tests/unit/ui/screens/strategy_windows/test_list_windows.py tests/unit/ui/screens/test_empire_panel_window.py tests/unit/simulation/combat/test_ship_stats_aggregator.py tests/unit/simulation/combat/test_hit_log_recorder.py tests/unit/simulation/combat/test_hit_log_modifier_trace.py tests/unit/simulation/test_battle_runner.py tests/unit/simulation/components/abilities/test_strategic_abilities.py tests/unit/strategy/data/test_galaxy_warp_generator.py tests/unit/strategy/services/test_race_description_llm_controller.py tests/unit/ui/screens/builder/test_weapons_panel.py tests/unit/ui/screens/builder/test_modifier_row.py tests/unit/ui/screens/builder/test_modifier_utils.py tests/unit/ui/screens/test_strategy_fleet_ops.py tests/unit/ui/screens/test_camera_navigator.py tests/unit/ui/screens/test_strategy_panel_manager.py tests/unit/ui/screens/test_strategy_click_dispatcher.py tests/unit/ui/screens/test_strategy_detail_fmt.py tests/unit/ui/services/image/test_openai_provider.py tests/unit/ui/services/image/test_null_provider.py tests/unit/ui/services/test_modifier_icon_service.py tests/unit/ui/screens/test_transfer_view_model.py tests/unit/ui/screens/test_planet_list_filters.py tests/unit/ui/screens/builder/test_detail_panel.py tests/unit/ui/screens/test_fleet_report_filters.py tests/unit/simulation/entities/test_projectile.py tests/unit/strategy/systems/test_race_randomizer_helpers.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/strategy/data/test_fleet_order_removal.py tests/unit/strategy/fleet/test_basics.py tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py -q -n 0
```

## Pass 4 Production Fixes

| File | Fix |
|---|---|
| `game/ui/services/image/openai_provider.py` | `OpenAIImageProvider` now catches `requests.exceptions.SSLError` before broader connection errors, preserving the SSL-specific `ImageNetworkError`; response parsing now uses validated base64 decoding so invalid payloads raise `ImageResponseError` instead of silently decoding empty bytes. |
| `game/strategy/data/fleet.py` | `Fleet.remove_orders_by_type_and_target()` now removes matching orders before unregistering pursuers, so the target tracker observes the true remaining queue; it also clears `fleet.path` when the active order is removed. |

## Pass 5 Results

Fifth pass continued 2026-05-05 with five worker slices plus one local advisory slice.

| Slice | Result | Notes |
|---|---|---|
| Local / Test Lab dialog advisory | Completed | Added focused state-transition tests for `JSONPopup.close()` and `ConfirmationDialog` confirm/cancel/Escape paths. No production changes needed. |
| A / battle setup compiler + schematic | Completed | Added branch coverage for `_load_complex_design()` OSError handling, `_iter_components()` malformed layer entries, `_ship_spec_from_instance(..., pose=None)`, and schematic cube-root radius scaling. Found and fixed schematic radius truncation. |
| B / builder/rendering helper gaps | Completed | Added focused tests for weapons panel no-weapons/target-info/tooltip dispatch, weapons renderer no-weapons/target-info/verbose-tooltip text generation, and battle state viewer event/draw dispatch. No production changes needed. |
| C / UI services leftovers | Completed | Added OpenAI edit-image/mask file-read failure tests and `ModifierIconService.clear_cache()` coverage. Found and fixed raw `FileNotFoundError` leakage from OpenAI edit file reads. |
| D / app/UI screen edge cases | Completed | Added `StrategyScreen.current_empire` empty-human-ID coverage, workshop data-loader policy/layer path coverage, and direct `UIActionRouter` mapping tests. Found and fixed `current_empire` empty-list indexing. |
| E / non-UI minor/advisory | Completed | Added battle-line wedge/echelon geometry tests, direct habitability sigma-guard coverage, and atmosphere malformed-data/list-form edge coverage. `_flee_direction` zero-length vector was disputed because an existing direct test already covers it. |

Pass 5 targeted receipts:

| Slice | Command Result |
|---|---|
| Local probe | `pytest tests/unit/ui/screens/test_lab -k confirmation_dialog_state_transitions -q -n 0` -> `55 deselected` |
| Local targeted suite | `pytest tests/unit/ui/screens/test_lab/test_dialogs.py -q -n 0` -> `5 passed` |
| Worker A targeted suite | `46 passed`; `git diff --check` passed |
| Worker B targeted suite | `19 passed`; scoped diff check passed |
| Worker C targeted suite | Initial new tests exposed 2 failures; final targeted suite `23 passed`; `git diff --check` passed |
| Worker D targeted suite | Initial new `current_empire` test failed with `IndexError`; final targeted suite `80 passed`; `git diff --check` passed |
| Worker E targeted suite | `102 passed`; `git diff --check` passed |
| Combined Pass 5 targeted suite | `275 passed` |
| `git diff --check` | Passed |

Combined Pass 5 command:

```powershell
pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py tests/unit/ui/screens/builder/test_schematic_view.py tests/unit/builder/test_schematic_cache_key.py tests/unit/ui/screens/builder/test_weapons_panel.py tests/unit/ui/screens/builder/test_weapons_renderer.py tests/unit/ui/screens/test_battle_state_viewer.py tests/unit/ui/services/image/test_openai_provider.py tests/unit/ui/services/test_modifier_icon_service.py tests/unit/ui/screens/test_strategy_screen.py tests/unit/ui/screens/test_workshop_data_loader.py tests/unit/ui/screens/test_strategy_ui_action_router.py tests/unit/ai/test_behavior_units.py tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py tests/unit/strategy/formulas/test_habitability.py tests/unit/strategy/engine/test_atmosphere_engine.py tests/unit/ui/screens/test_lab/test_dialogs.py -q -n 0
```

## Pass 5 Production Fixes

| File | Fix |
|---|---|
| `game/ui/screens/builder/schematic_view.py` | `_calculate_max_r()` now rounds the cube-root mass radius calculation instead of truncating it, matching the documented Escort/Dreadnought scaling. |
| `game/ui/services/image/openai_provider.py` | OpenAI edit image/mask file-read failures now raise `ImageConfigError` with field/path/error context before any network call. |
| `game/ui/screens/strategy_screen.py` | `current_empire` now handles empty `human_player_ids` by returning `active_empire` or the first available empire instead of indexing an empty list. |

## Pass 5 Disputed / Already Covered

| Claim | Result | Notes |
|---|---|---|
| `game/ai/behaviors.py` `_flee_direction` zero-length vector | Disputed | Existing `TestFleeBehavior::test_flee_zero_distance_uses_default_vector` directly covers the branch. |
| Broad `WeaponsReportPanel` event/scroll/viewport gaps | Disputed/partial | Pass 4 already covered event, scrollbar, and viewport clipping behavior; Pass 5 added only the remaining no-weapons, target-info, and tooltip dispatch branches. |
| OpenAI parse/SSL/PIL and ModifierIconService cache/missing/load-error paths | Disputed/partial | Pass 4 already covered these; Pass 5 added edit file-read failure and clear-cache coverage only. |
| Builder helper leftovers (`modifier_utils`, grouping, stat definitions/getters) | Disputed | Passes 1, 2, and 4 already added direct tests for these suggested local candidates, so Pass 5 did not duplicate them. |

## Deferred High-Risk/High-Effort Claims

These remain good follow-up candidates after Pass 5:

- Remaining UI opportunities are now mostly deeper rendering/integration branches: full `StrategyScreen` construction paths, real `pygame_gui` layout integration for windows/widgets, and broad pixel/rendering paths where mocks are not representative.
- Remaining Test Lab/UI advisory gaps include deeper dialog drawing, tag filter rendering, virtual table/slider widget construction, and other low-risk visual-only helpers.
- Remaining non-UI opportunities are lower priority after Pass 5; another pass may still be worthwhile only if it targets a small curated set of verified leftover P2/advisory items rather than re-scanning broad audit claims.

## Pass 6 Results

Sixth pass continued 2026-05-05 with four small worker slices plus one local render-dispatch slice. The pass intentionally stayed in low-risk UI advisory/P2 territory and did not re-scan broad audit claims.

| Slice | Result | Notes |
|---|---|---|
| Local / strategy render hex outlines | Completed | Added direct non-pixel tests for `HexOutlineLayer` occupancy aggregation, turn-keyed cache invalidation, draw dispatch by ownership state, and offscreen culling. No production changes needed. |
| A / Test Lab visual helpers | Completed | Added direct `TagFilterPanel.draw()` tests for priority tag ordering, 8-tag display cap, viewmodel rect writes, active/excluded/normal hover branches, and clear-button count/hover branches. Pass 5 dialog state-transition tests were treated as already covered. |
| B / UI widget construction helpers | Completed | Added mocked construction coverage for `build_range_slider_row()` and replay-action branch coverage for `VirtualTable` row-pool construction, enabled/disabled tooltip updates, action lookup, and cleanup. Existing generic `VirtualTable` construction/action/scroll tests were treated as already covered. |
| C / StrategyScreen cheap construction | Completed | Added a real `StrategyScreen.__init__` test with heavy upstream pieces patched out, verifying injected composition wires all 8 collaborator slots and bypasses the default composition factory. Broad real `pygame_gui` construction remains deferred. |
| D / strategy render dispatch | Completed | Added direct tests for `draw_grid()` large-viewport culling and visible snake-line dispatch plus `draw_storms()` low-zoom dispatch and low-detail offscreen culling. `TriStateFilterWidget` was disputed because existing tests already cover state/visual updates. |

Pass 6 targeted receipts:

| Slice | Command Result |
|---|---|
| Local no-test probe | `pytest tests/unit/ui/screens/strategy_render/test_hex_outlines.py -q -n 0` -> file not found / no tests |
| Local targeted suite | `pytest tests/unit/ui/screens/strategy_render/test_hex_outlines.py -q -n 0` -> `4 passed` |
| Worker A targeted suite | `pytest tests/unit/ui/screens/test_lab/renderer tests/unit/ui/screens/test_lab/test_dialogs.py -q -n 0` -> `13 passed`; `git diff --check` passed |
| Worker B targeted suite | `pytest tests/unit/ui/widgets/test_range_slider_builder.py tests/unit/ui/components/table/test_virtual_table.py -q -n 0` -> `30 passed`; `git diff --check` passed |
| Worker C targeted suite | `pytest tests/unit/ui/screens/test_strategy_screen_composition.py tests/unit/ui/screens/test_strategy_screen.py -q -n 0` -> `83 passed`; `git diff --check` passed |
| Worker D targeted suite | `pytest tests/unit/ui/screens/strategy_render -q -n 0` -> `8 passed`; `git diff --check` passed |
| Combined Pass 6 targeted suite | `130 passed` |
| `git diff --check` | Passed |

Combined Pass 6 command:

```powershell
pytest tests/unit/ui/screens/test_lab/test_dialogs.py tests/unit/ui/screens/test_lab/renderer/test_tag_filter_panel.py tests/unit/ui/widgets/test_range_slider_builder.py tests/unit/ui/components/table/test_virtual_table.py tests/unit/ui/screens/test_strategy_screen.py tests/unit/ui/screens/test_strategy_screen_composition.py tests/unit/ui/screens/strategy_render/test_hex_outlines.py tests/unit/ui/screens/strategy_render/test_grid_and_storms.py -q -n 0
```

## Pass 6 Production Fixes

None. Pass 6 added targeted test coverage only.

## Pass 6 Disputed / Already Covered

| Claim | Result | Notes |
|---|---|---|
| Test Lab dialog close/confirm/cancel/Escape branches | Already covered | Pass 5 added direct `JSONPopup.close()` and `ConfirmationDialog` state-transition coverage, so Pass 6 did not duplicate it. |
| Generic `VirtualTable` construction/action/scroll/selection/cleanup branches | Already covered | Existing `tests/unit/ui/components/table/test_virtual_table.py` covered the generic paths; Pass 6 only added replay-action-specific branch coverage. |
| `StrategyScreen.current_empire` empty-human-ID branch | Already covered | Pass 5 added the targeted regression and production fix. |
| `TriStateFilterWidget` visual state branch | Disputed | Existing `tests/unit/ui/components/filters/test_tri_state_widget.py` covers state changes and visual select/unselect behavior. |

## Remaining Recommendation After Pass 6

Another pass is still possible, but the marginal value is now low unless it is scoped to one or two verified UI integration seams. The remaining useful work is mostly broad real-widget construction or rendering/pixel behavior where mock-only tests are less representative. A broad Pass 7 is not recommended; a worthwhile Pass 7 would target a specific existing fixture-supported real `pygame_gui` window/widget integration path or stop here and let future feature work add coverage near touched UI code.
