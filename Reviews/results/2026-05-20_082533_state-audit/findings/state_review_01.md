# State Management Review: Shard 01

## Summary
- Shard: Shard 01
- Files in Scope: 156
- Files Actually Read: 156
- Total Findings: 5
- Critical: 1 | Major: 1 | Minor: 3

## Singleton Findings

#### CRITICAL: Module-level mutable rect state in exit_dialog.py
**ID:** ST-01-001
**Location:** `game/exit_dialog.py:11-12`
**Description:** Two module-level globals `_exit_yes_rect` and `_exit_no_rect` are initialized to `None` and reassigned every frame by `draw_exit_dialog()`. These are not protected by any lock or lifecycle management. The `handle_exit_dialog_click()` and `handle_exit_dialog_cancel()` functions read these module-level variables, creating implicit coupling through global mutable state. The `global` keyword at line 24 confirms these are write-through globals.
**Recommendation:** Encapsulate the exit dialog in a class. The `draw_exit_dialog` function should return the rects, or the dialog should be a class with instance-level `yes_rect` / `no_rect` attributes.

#### MAJOR: Global counter for fleet IDs in battle_setup_state.py
**ID:** ST-01-002
**Location:** `game/ui/screens/battle_setup_state.py:24`
**Description:** Module-level `_next_fleet_id = 1000` is a mutable global integer counter incremented by `_generate_fleet_id()` (line 30: `_next_fleet_id += 1`) via the `global` keyword at line 29. This counter is a persistent side-channel that grows across the entire process lifetime, and is not validated or bounded. Multiple `BattleSetupState` instances share the same counter, creating test-isolation risk.
**Recommendation:** Make `_next_fleet_id` an instance attribute on `BattleSetupState` and pass the counter context into `BattleSetupSide.create_fleet()`.

## Module Mutable Collection Findings

#### MINOR: Mutable provider lists in ability_iterator.py
**ID:** ST-01-003
**Location:** `game/strategy/services/ability_iterator.py:31-32`
**Description:** Module-level `_HEX_PROVIDERS: List[ProviderFn] = []` and `_SYSTEM_PROVIDERS: List[ProviderFn] = []` are populated at import time by built-in registrations (lines 326-339). The `register_source_provider_at_hex` / `register_source_provider_in_system` functions append to these lists, and `unregister_source_provider` removes from them. While production usage is strictly additive (modules register once at import), the `unregister_source_provider` test-isolation helper exists as a mutation surface.
**Verdict:** Acceptable — this is the Registry pattern (Pattern #4). The lists are seeded once and mutated only by other modules' import-time registrations. `unregister_source_provider` is a documented test-isolation seam. Flagged as MINOR because the mutation surface exists.

## Global Keyword Findings

#### MINOR: Fleet lookup callbacks in ability_iterator.py
**ID:** ST-01-004
**Location:** `game/strategy/services/ability_iterator.py:264-265, 276`
**Description:** Module-level `_FLEETS_AT_HEX_LOOKUP` and `_FLEETS_IN_SYSTEM_LOOKUP` (both `Optional[Any] = None`) are mutated by `set_fleet_lookups()` via `global` keyword. These act as singleton-accessor slots without the standard `get_default_*` / `set_default_*` pair pattern. The strategy session calls `set_fleet_lookups()` at startup to wire the fleet provider; if never called, the fleet ability source yields nothing.
**Verdict:** Acceptable for current design — these are injected once at session start and never change during a session. However, the lack of a `get_*` accessor and the use of raw `global` (vs. the `_default_*` / `get_default_*` / `set_default_*` pattern used elsewhere) is a minor style divergence.

#### MINOR: Lazy-init fallback in get_default_sprite_manager()
**ID:** ST-01-005
**Location:** `game/ui/renderer/sprites.py:116-119`
**Description:** `get_default_sprite_manager()` uses `global _default_sprite_manager` and has a self-init fallback that creates a new `SpriteManager()` if `None`. This is the legacy latch-init pattern that differs from `ApplicationContext.create_production()` wiring. If any code calls `get_default_sprite_manager()` before `ApplicationContext.create_production()` runs (e.g., during import resolution), it will get a different instance than `ctx.sprite_manager`, creating singleton divergence.
**Recommendation:** Replace the lazy-init fallback with a sentinel that raises a descriptive error, or ensure `set_default_sprite_manager()` is called before any `get_default_sprite_manager()` call.

## Class Mutable Default Findings

No class-level mutable default findings in this shard. All files that define class-level defaults use immutable primitives (int, float, str, tuple, frozenset) or `None`.

## Singleton Access-Pattern Divergence (this shard)
- `get_default_xxx()` call sites: 40
- `ctx.xxx` accesses: 1
- Transition percentage: 2.4%

The overwhelming majority of code in this shard uses `get_default_xxx()` accessors rather than direct `ctx.xxx` access. The single `ctx.xxx` access is within `game/context.py` itself (the `ApplicationContext` class definition at lines 104-108), which is the canonical composition root and is exempt from divergence concerns. All consumer code in this shard uses the module-level accessor pattern correctly.

Additional notable `get_default_*` usage patterns observed:
- `game/ui/screens/strategy_event_router.py:331` — `get_default_registry_provider()` for resource catalog (properly guarded with try/except)
- `game/ui/screens/strategy_windows/planet_abilities_ctrl.py:30-34` — `get_default_registry_provider()` for component registry lookups
- `game/ui/screens/strategy_build_queue_manager.py:41` — `get_cached_registries()` via shared `registry_cache` module (PROJ-420 consolidation)
- `game/ui/screens/strategy_renderer.py:88` — `get_default_asset_manager()` for asset loading
- `game/ui/screens/strategy_screen_assets.py:47,56` — `get_default_asset_manager()` for asset loading
- `game/core/registry_cache.py:59` — `get_default_registry_provider()` in the cached registries helper

## Verified Acceptable Patterns (no findings)

The following patterns were examined and confirmed as compliant:

1. **`game/services/llm/defaults.py`** — Standard `_default_llm_provider` with `get_default_llm_provider()` / `set_default_llm_provider()` pair. Wired by `ApplicationContext.create_production()` at line 183. Fully compliant with Pattern #1.

2. **`game/simulation/services/ship_materializer.py`** — Standard `_default_ship_materializer` with `get_default_ship_materializer()` / `set_default_ship_materializer()` pair. Lazy-initializes to `InstanceBackedMaterializer()`. Wired by `ApplicationContext`. Compliant.

3. **`game/core/registry_cache.py`** — `_cached_registries` with `get_cached_registries()` / `reset_cached_registries()` pair. Proper lifecycle: reset on manager swap, test isolation. Compliant with Pattern #4.

4. **`game/strategy/data/design_role_registry.py`** — `_default` with `get_default_design_role_registry()` / `set_default_design_role_registry()` / `reset_default_design_role_registry()` triple. Lazy-init from layered data files. Compliant.

5. **`game/services/llm/background.py:56-62`** — Module-level `_in_flight_calls: int = 0` and `_active_workers: Set[threading.Thread] = set()`. Properly guarded by `_in_flight_lock`. Uses `global` keyword but is justified: cross-thread concurrent call accounting requires module-level state. Compliant.

6. **`game/strategy/engine/order_handlers/lay_mines.py:91`** — Uses `random.Random(seed)` (per-instance RNG) rather than module-level `random.*`. Compliant with Pattern #18.

7. **`game/context.py:33-67`** — `_default_planet_habitability_service` with `get_default_planet_habitability_service()` / `set_default_planet_habitability_service()` pair. Auto-installed via `_install_default_habitability_service()` at import time. Wired through `ApplicationContext`. Compliant with Pattern #1.

8. **`game/ui/colors.py`** — All module-level values are ALL_CAPS immutable tuples of ints. No mutable collections. Compliant.

9. **`game/ui/screens/test_lab/theme.py`** — All module-level values are ALL_CAPS immutable tuples. No mutable collections. Compliant.

10. **`game/strategy/engine/conflict_resolution_engine.py`** — Owns `self._rng = random.Random()` (unseeded, separate from battle determinism). Documented in Pattern #18. Compliant.

## File Coverage Verification

| File | Status |
|------|--------|
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read ✓ |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ |
| game/strategy/engine/order_handlers/lay_mines.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Read ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/strategy/services/fleet_warp_resolution.py | Read ✓ |
| game/strategy/services/mine_group_service.py | Read ✓ |
| game/ui/screens/strategy_screen_assets.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/ui/screens/menu_scene.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/screens/battle_ui.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/ui/screens/build_queue_renderer.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/ui/screens/per_player_ui_state.py | Read ✓ |
| game/ui/screens/empire_panel_window.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/ui/screens/fleet_selection_window.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/strategy/data/planet_gen.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/screens/strategy_colonization.py | Read ✓ |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/ui/screens/list_filter_utils.py | Read ✓ |
| game/strategy/generation/loaders/galaxy_layouts_loader.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/facade/dto/planet_dto.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/ui/services/validation_service.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/simulation/combat/telemetry.py | Read ✓ |
| game/simulation/combat/damage_calculator.py | Read ✓ |
| game/simulation/entities/stat_contributors/movement.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
| game/ui/screens/cargo_quick_dialog.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/strategy/services/planet_economy_projector.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/strategy/engine/handlers/launch_satellites.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/ui/screens/strategy_screen_selection.py | Read ✓ |
| game/core/ship_classes.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/strategy/engine/handlers/lay_mines.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/simulation/combat/ram_target_resolver.py | Read ✓ |
| game/ui/screens/strategy_panel_manager.py | Read ✓ |
| game/strategy/services/component_layers.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/ui/screens/strategy_fleet_context_menu.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/engine/order_handlers/launch_fighters.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/simulation/systems/battle_end_conditions.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/strategy/data/naming.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/strategy/generation/star_generator.py | Read ✓ |
| game/ui/components/table/column_manager.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/panels/race_environment_panel.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ |
| game/strategy/events/event_log.py | Read ✓ |
| game/context.py | Read ✓ |
| game/strategy/data/squadron.py | Read ✓ |
| game/simulation/entities/stat_contributors/defense.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/strategy/combat/pre_tick_setup/__init__.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/ui/widgets/scroll_state.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/ui/screens/battle_setup_state.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/simulation/combat/boundary.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/ui/screens/strategy_input_handler.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/ui/research/research_controls.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/strategy/facade/dto/__init__.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/strategy/data/fleet_serde.py | Read ✓ |
| game/strategy/combat/strategy_modifier_stack_builder.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/services/ability_metadata.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/strategy/engine/handlers/order_queue.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/planet_menu_items.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/interfaces/engines/components.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/ui/screens/empire_build_queue_window.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/strategy/combat/__init__.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/strategy/combat/post_battle_hook_builder.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/ui/services/image/types.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
| game/ui/panels/battle_panels.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/app.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/core/registry_cache.py | Read ✓ |
