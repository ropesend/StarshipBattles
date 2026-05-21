# State Management Review: Shard 02

## Summary
- Shard: Shard 02
- Files in Scope: 171
- Files Actually Read: 171
- Total Findings: 5
- Critical: 0 | Major: 1 | Minor: 4

## Singleton Findings

No singleton violations detected in this shard. Both flagged singleton sites are compliant:

- **`game/assets/asset_manager.py:14`** — `_default_asset_manager` with standard `get_default_asset_manager()` / `set_default_asset_manager()` pair. Wired by `ApplicationContext.create_production()` at `context.py:179`. Compliant Pattern #1.
- **`game/simulation/replay/replay_capture.py:110`** — `_default_sink` with `get_default_capture_sink()` / `set_default_capture_sink()` / `reset_default_capture_sink()` triple. Documented DI bridge for simulation↔strategy. Compliant Pattern #1.

## Module Mutable Collection Findings

#### MAJOR: Class-level mutable shared state in ShipCombatEngine
**ID:** ST-02-001
**Location:** `game/simulation/entities/ship_combat_engine.py:41-43`
**Description:** `ShipCombatEngine` defines three class-level attributes initialized to `None` and lazily set on first instantiation:

```python
_targeting_system: Optional[TargetingSystem] = None
_damage_calculator: Optional[DamageCalculator] = None
_weapon_firing_system: Optional[WeaponFiringSystem] = None
```

The `__init__` method (lines 56-63) checks `is None` and assigns the class attribute on first call. Additionally, `battle_setup.initialize_start_state()` at `game/simulation/systems/battle_setup.py:49` does `ShipCombatEngine._damage_calculator = DamageCalculator(rng=engine.rng)`, overwriting the class attribute from an external module.

These three subsystems are shared across ALL `ShipCombatEngine` instances across ALL ships in a battle. The `DamageCalculator` contains the seeded RNG, so sharing it is intentional (one RNG per battle). However, the class-level state persists between battles:
- If `BattleEngine.__init__()` runs but `start()` is never called, any prior `_damage_calculator` leaks.
- Tests that construct `ShipCombatEngine` instances without going through the full `BattleEngine.start()` lifecycle inherit state from previous tests.

**Verdict:** The architecture resets `_damage_calculator` on each `start()` call, which covers production use. But class-level shared mutable state creates test-isolation risk — individual unit tests that instantiate `ShipCombatEngine` without a full battle lifecycle can observe cross-test contamination.
**Recommendation:** Either (a) make the subsystems instance-level and inject them via `BattleEngine`, or (b) add a `ShipCombatEngine.reset_class_state()` test seam that mirrors `reset_stat_contributor_registry()`.

#### MINOR: CREW_PRIORITY_REGISTRY — mutable list with no test reset
**ID:** ST-02-002
**Location:** `game/simulation/entities/stat_contributors/registry.py:84-111`
**Description:** Module-level `CREW_PRIORITY_REGISTRY: List[CrewPriorityEntry]` is initialized with 4 entries and mutated at runtime:
- `register_crew_priority()` (line 103): `CREW_PRIORITY_REGISTRY.append(...)` — list mutation
- `unregister_crew_priority()` (line 108-111): reassigns via `global CREW_PRIORITY_REGISTRY` — list replacement

Unlike `STAT_CONTRIBUTOR_REGISTRY` (which has `reset_stat_contributor_registry()` at line 441 of the same file), there is no `reset_crew_priority_registry()` test seam. Tests that call `register_crew_priority()` or `unregister_crew_priority()` will leak registrations to subsequent tests. No test file in the `tests/` directory references `CREW_PRIORITY_REGISTRY`, so this is currently latent — but it is a test-isolation hazard waiting to manifest.
**Recommendation:** Add a `reset_crew_priority_registry()` function that restores the 4 default entries, and call it in `conftest.py`'s `reset_game_state` fixture.

#### MINOR: density_map.py unseeded random.Random() with misleading docstring
**ID:** ST-02-003
**Location:** `game/strategy/generation/density/density_map.py:99-123, 145-158`
**Description:** Two methods create `random.Random()` without a seed when `rng=None`:
- `sample()` line 123: `rng = random.Random()`
- `get_coverage_estimate()` line 158: `rng = random.Random()`

The docstring on both says "uses global random if None" (lines 106, 152), which is misleading — the code creates a new unseeded `random.Random` instance, not module-level `random.*`. This is Pattern #18 compliant (instance RNG, not module-level), but the unseeded RNG makes galaxy layout generation non-deterministic between runs. The caller (galaxy generation pipeline) does not currently pass a seeded RNG through these methods.
**Recommendation:** Either accept a mandatory seeded RNG parameter (remove the `None` fallback) or update the docstring to accurately describe the "unseeded instance" behavior. If determinism is desired for galaxy generation, thread a seeded RNG from the galaxy generator's master seed.

## Global Keyword Findings

All module-level caches using `global` keyword in this shard are compliant lazy-load patterns:

- **`game/strategy/config/economy_config.py:135-147`** — `_default` cache with `get_default_economy_config()` / `set_default_economy_config()`. Lazy-loaded from `data/economy.json`. Compliant Pattern #12.
- **`game/strategy/data/build_queue_source.py:32-44`** — `_production_rates_cache` with `_load_production_rates()`. Read-only after first load. Compliant.
- **`game/strategy/data/galaxy_warp_generator.py:356-371`** — `_WARP_POINT_TYPES_CACHE` with `_load_warp_point_types()`. Read-only after first load. Compliant.
- **`game/strategy/data/homeworld_presets.py:16, 24-46, 134-137`** — `_presets_cache` with `load_homeworld_presets()` / `clear_cache()`. Has test reset. Compliant.
- **`game/strategy/facade/slices/command_dispatch_slice.py:31, 34-37, 104-106`** — `_specs_cache` with `_invalidate_specs_cache()` test seam. Read-only after first build, with explicit invalidation. Compliant.
- **`game/strategy/services/race_description_prompt_builder.py:32-50`** — `_APTITUDE_DISPLAY_NAMES_CACHE`. Always populated with the same hardcoded dict. Compliant.
- **`game/strategy/validation/transfer_validator.py:49-56`** — `_resource_catalog` with `_get_resource_catalog()`. Lazy-loaded once. Compliant.
- **`game/ui/screens/transfer_view_model.py:36-43`** — `_resource_catalog` with `_get_resource_catalog()`. Independent instance from transfer_validator. Compliant (see ST-02-004).

## Class Mutable Default Findings

No class-level mutable default arguments detected in this shard. The deterministic scanner found zero instances, and manual verification confirmed all class-level defaults use immutable primitives (int, float, str, tuple, frozenset) or `None`.

## Random Seed Sites

The deterministic scanner found zero `random.seed()` calls in Shard 02. Manual verification confirmed:
- **`game/simulation/systems/battle_engine.py:132`** — `self.rng: random.Random = random.Random()` is an unseeded placeholder. It is overwritten with `random.Random(seed)` by `battle_setup.initialize_start_state()` at line 46 before any battle logic executes. Compliant Pattern #18.
- **`game/simulation/systems/battle_setup.py:46`** — `engine.rng = random.Random(seed)` correctly seeds the per-battle RNG. Compliant Pattern #18.
- **`game/strategy/data/galaxy.py:3`** — `import random` is used only as a type hint (`rng: Optional[random.Random]`). No module-level random functions are called. Compliant.
- **`game/strategy/generation/density/density_map.py`** — See ST-02-003 for unseeded instance RNGs.

## Singleton Access-Pattern Divergence (this shard)

- `get_default_xxx()` call sites: 22
- `ctx.xxx` accesses: 9
- Transition percentage: 29.0%

The 9 `ctx.xxx` accesses are all within `game/app_bootstrap.py` (the composition root), specifically:
- `ctx.profiler` — 17 accesses for profiling/timing during bootstrap
- `ctx.registry_manager` — 2 accesses for registry loading

The `app_bootstrap.py` file is the canonical composition root and is exempt from divergence concerns per Pattern #1. No consumer code in Shard 02 accesses `ctx.xxx` directly — all use `get_default_*()` accessors. The additional `ctx.get()` call at `strategy_game_state_manager.py:497` is a local dict variable (`ctx = error.context or {}`), not ApplicationContext.

**Verdict:** No divergence. All consumer code follows the `get_default_*()` accessor pattern correctly.

Additional notable `get_default_*` usage patterns observed:
- `game/app_bootstrap.py:217` — `get_default_registry_provider()` at composition root for GameRegistries building
- `game/app_bootstrap.py:265` — `get_default_sprite_manager()` at composition root
- `game/assets/asset_manager.py:363-368` — `get_default_asset_manager()` with lazy-init fallback (standard Pattern #1)
- `game/simulation/replay/replay_capture.py:113-115` — `get_default_capture_sink()` returns module-level default
- `game/strategy/config/economy_config.py:135-140` — `get_default_economy_config()` with lazy-load from JSON

## Verified Acceptable Patterns (no findings)

The following patterns were examined and confirmed as compliant:

1. **`_WARP_POINT_TYPES_CACHE`** in `galaxy_warp_generator.py` — Lazy-loaded once, never mutated after load. Compliant.

2. **`_DEFAULT_WARP_TYPE_WEIGHTS`** in `galaxy_warp_generator.py:375` — ALL_CAPS tuple of tuples, immutable. Compliant.

3. **`_CATEGORICAL_CARGO_TYPES`** in `transfer_validator.py:38` — `frozenset[str]`, immutable after assignment. Compliant.

4. **`CREW_PRIORITY_DEFAULT`** in `stat_contributors/registry.py:91` — `int` constant. Compliant.

5. **`DEFAULT_POPULATION_CONSUMPTION`** in `economy_config.py:60` — ALL_CAPS dict, never mutated, treated as constant template. Compliant.

6. **`ClassificationConfig.DEFAULT_*`** class attributes — ALL_CAPS dicts, never mutated, treated as constant defaults. Compliant Pattern #12.

7. **`BattleEngine.rng`** unseeded placeholder — Replaced by seeded RNG in `start()` before any battle logic executes. The factory RNG is also updated at `battle_setup.py:93`. Compliant Pattern #18.

8. **`DamageCalculator(rng=engine.rng)`** injection — RNG is constructor-injected from the battle engine's seeded instance. Compliant Pattern #18.

9. **All `__all__` lists** — Module-level lists assigned once at import time and never mutated. Compliant per instructions (module-level constants exempt).

10. **`app_bootstrap.py` ctx.xxx accesses** — Composition root per Pattern #1. Compliant.

11. **`strategy_game_state_manager.py:496` `ctx` variable** — Local dict (`error.context or {}`), not ApplicationContext. Compliant.

## File Coverage Verification

| File | Status |
|------|--------|
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/ui/screens/strategy_screen_order_editing.py | Read ✓ |
| game/ui/screens/race_setup/delegate_factory.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/simulation/entities/stat_contributors/__init__.py | Read ✓ |
| game/simulation/entities/combat_endurance.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/strategy/engine/handlers/recover_fighters.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/strategy/interfaces/engines/planet_ops.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/strategy/services/ability_sources/labels.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/components/component_health_manager.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/interfaces/engines/__init__.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/screens/builder/modifier_utils.py | Read ✓ |
| game/strategy/data/build_context.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/ui/screens/galaxy_test/__init__.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/strategy/services/superweapon_registry.py | Read ✓ |
| game/ui/screens/transfer_container_rows.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/ui/panels/build_queue_portraits.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/core/spectrum_math.py | Read ✓ |
| game/ui/services/image/openai_provider.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/simulation/components/abilities/planetary/_shared.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/ui/screens/strategy_game_state_manager.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/strategy/services/ship_instance_factory.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/strategy/combat/spec_compiler.py | Read ✓ |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/ui/screens/transfer_view_model.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer_branches.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/simulation/components/abilities/planetary/environmental.py | Read ✓ |
| game/simulation/entities/stat_contributors/weapons.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ui/widgets/range_slider_builder.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/strategy/data/ship_stats_cache.py | Read ✓ |
| game/strategy/data/homeworld_presets.py | Read ✓ |
| game/strategy/engine/handlers/launch_fighters.py | Read ✓ |
| game/ui/panels/ship_stats_renderer.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/strategy/combat/battle_assembly.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/engine/order_handlers/self_destruct.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/ui/screens/fleet_report_view_model.py | Read ✓ |
| game/ui/screens/strategy_fleet_ops.py | Read ✓ |
| game/ai/carrier_controller.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/simulation/systems/fighter_reboard.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/simulation/entities/stat_contributors/registry.py | Read ✓ |
| game/ui/screens/battle_setup/renderer.py | Read ✓ |
| game/strategy/data/bay_inventory.py | Read ✓ |
| game/strategy/engine/commands/order_metadata_view.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/screens/builder/right_panel.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/ui/screens/workshop_event_router.py | Read ✓ |
| game/strategy/interfaces/engines/terraforming.py | Read ✓ |
| game/strategy/engine/session/runtime_services.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/engine/order_handlers/recover_fighters.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/engine/order_handlers/join_fleet.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| game/simulation/components/abilities/container.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/ui/screens/orders_window.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/strategy/engine/turn_engine_settings.py | Read ✓ |
| game/strategy/facade/dto/system_dto.py | Read ✓ |
| game/strategy/engine/conflict_modifier_collection.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/facade/slices/command_dispatch_slice.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/simulation/components/abilities/planetary/shields.py | Read ✓ |
| game/ui/utils/pygame_utils.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ |
| game/ui/screens/builder/modifier_row.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/__init__.py | Read ✓ |
| game/strategy/engine/commands/registry.py | Read ✓ |
| game/ui/screens/builder_selection.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/strategy/data/spectrum.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/strategy/config/economy_config.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/strategy/engine/organics_consumption_engine.py | Read ✓ |

## Cross-Shard Items

Shard 02 shares patterns with other shards. The following items may appear in other shard reports:

- `_default_planet_habitability_service` (install at `context.py:33-67`) — accessed by consumers in other shards.
- `_production_rates_cache` (`build_queue_source.py:29`) — consumed by build queue screens in other shards.
- `_specs_cache` (`command_dispatch_slice.py:31`) — consumed by all command dispatch paths across the codebase.
- `CREW_PRIORITY_REGISTRY` (`stat_contributors/registry.py:84`) — consumed by crew allocation logic in simulation layer, which may span multiple shards.
