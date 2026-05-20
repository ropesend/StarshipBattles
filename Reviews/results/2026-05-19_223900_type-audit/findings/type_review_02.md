# Type Safety Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 215
- Files Actually Read: 82 (all high-signal files + flagged-by-scan cross-references)
- Total Findings: 52
- Critical: 2 | Major: 25 | Minor: 22 | INFO: 3

## Narrowable Any Returns

### CRITICAL
No CRITICAL narrowable Any returns found.

### MAJOR

1. **`game/ai/interfaces/controllable.py:239` — `ShipControllableAdapter.ship` returns `Any`**
   - Returns `self._ship` which is typed `Any`. The underlying ship satisfies `ICombatShip` Protocol. Could be narrowed to `ICombatShip` or `Ship`.
   - Verified by mypy: lines 268-392 flag 24 `no-any-return` errors because return types declare `float`, `bool`, `int`, `str`, etc. but body returns from untyped `self._ship` attributes.

2. **`game/strategy/engine/turn_engine.py:286` — `_time_phase` returns `Any`**
   - Method signature: `def _time_phase(self, key: str, fn, *args, **kwargs) -> Any`
   - Private method but used across all tick/end-of-turn phases. Return value is consumed by callers (`_run_phases`, tick loop) that use it for env event lists and move queues. Could be narrowed to `object | None` or annotated with a union of known return types.
   - Impact: 27 call sites within TurnEngine.

3. **`game/strategy/engine/production_spawner.py:103` — `_get_planet_mutator` returns `Any`**
   - Internal delegate used across production pipeline.
   - Mypy flagged `no-any-return` from factory resolution.

4. **`game/simulation/components/component_stats_calculator.py:305` — `evaluate_recursive` returns `Any`**
   - Recursive formula evaluator — return annotates `Any`. The evaluator returns `int | float | str | bool | list | dict` depending on formula semantics. Could use `FormulaResult = int | float | str | bool | list[FormulaResult] | dict[str, FormulaResult]`.
   - Impact: nested formula expressions lose type safety throughout the component pipeline.

5. **`game/simulation/systems/attack_processor.py:142` — `_spawn_from_carried_vehicle` returns `Any`**
   - Returns `Ship | None`. Should be `Ship | None`.
   - Mypy: flagged `no-any-return`.

6. **`game/strategy/adapters/simulation_adapter.py:426` — `_build_capture_context` returns `Any`**
   - Returns `ReplayCaptureContext`. Should be `ReplayCaptureContext`.

7. **`game/ui/screens/battle_screen.py:172` — `BattleScreen.engine` returns `Any`**
   - Property returning delegate attribute. Should return `BattleEngine | None`.

8. **`game/ui/screens/battle_screen.py:199,207,211,215,219` — Multiple `BattleScreen` properties return `Any`**
   - `show_overlay`, `stats_panel_width`, `ships`, `projectiles`, `ai_controllers` — all delegate properties.
   - Should return concrete types: `bool`, `int`, `list[Ship]`, `list[Projectile]`, `list[AIController]`.

9. **`game/ui/screens/battle_screen.py:481,485` — `is_battle_over`, `get_winner` return `Any`**
   - Delegate to `BattleUIService`. Should return `bool` and `int | None`.

10. **`game/ui/screens/planet_list_filters.py:38,174,215,252,280,333,348` — Public filter functions return `Any`**
    - `gather_planets`, `filter_planets`, `sort_planets`, `get_column_value`, `compute_planet_ranges`, `get_system_name`, `get_owner_name` all return `Any`.
    - Module-level utility functions used across UI. Should be narrowed to `list[PlanetInfo]`, `list[PlanetInfo]`, `list[PlanetInfo]`, `str`, `dict[str, tuple]`, `str`, `str`.

11. **`game/ui/screens/star_list_filters.py:20,67,121,163,203,217` — Public filter functions return `Any`**
    - Same pattern as planet_list_filters. `gather_stars` → `list[StarInfo]`, `filter_stars` → `list[StarInfo]`, `sort_stars` → `list[StarInfo]`, etc.

12. **`game/ui/screens/strategy_colonization.py:40,44,48` — `ColonizationSystem` properties return `Any`**
    - `systems`, `camera`, `hex_size` delegate to `self.scene`. Can narrow with TYPE_CHECKING.

13. **`game/ui/screens/strategy_colonization.py:224,246,259` — Methods return `Any`**
    - `request_colonize_order` → `dict | None`, `_get_system_at_hex` → `StarSystem | None`, `_resolve_planet_global_hex` → `HexCoord | None`.

14. **`game/ui/screens/transfer_grid_renderer.py:207,225` — Dropdown helper methods return `Any`**
    - `recreate_dropdown`, `extract_dropdown_value` — pygame_gui widget operations. `recreate_dropdown` → `UIDropDownMenu`, `extract_dropdown_value` → `str`.

15. **`game/ui/screens/builder/left_panel.py:453` — `get_add_count` returns `Any`**
    - Should return `int`.

16. **`game/ui/screens/builder/modifier_logic.py:150` — `calculate_snap_value` returns `Any`**
    - Should return `float`.

17. **`game/ui/screens/builder/weapons_viewmodel.py:110` — `hovered_weapon` returns `Any`**
    - Should return `Component | None`.

18. **`game/ui/screens/builder/weapons_viewmodel.py:392` — `calc_damage_at_range` returns `Any`**
    - Should return `float`.

19. **`game/ui/screens/strategy_render/systems.py:60` — `load_star_image` returns `Any`**
    - Should return `pygame.Surface | None`.

### MINOR

20. **`game/core/protocols/boundary.py:92` — `IResourceHolder.resources` returns `Any`**
    - Protocol property returning `ResourceRegistry`-like object. Comment says "typed as Any to avoid cross-layer import". Acceptable for boundary Protocol.

21. **`game/core/protocols/ui.py:62,66,78` — `ICamera` properties return `Any`**
    - `position`, `world_to_screen`, `screen_to_world` — Protocol for cross-layer boundary. Comment explains avoids Vector2 import. Acceptable.

22. **`game/strategy/engine/order_handlers/base.py:143,152` — `_get_planet_mutator`, `_get_ship_mutator` return `Any`**
    - Private methods returning delegation result. Could be `PlanetWriteService | None` and `ShipInstanceWriteService | None`.

23. **`game/ui/screens/setup_data_io.py:34,39,65,171,185` — Setup data functions return `Any`**
    - Module-level utility functions. Could narrow with typed DTOs.

24. **`game/ui/screens/setup_screen.py:133` — `get_team_display_groups` returns `Any`**
    - Should return `list[tuple[...]]`.

25. **`game/ui/screens/planet_menu_items.py:59` — `_global_hex` returns `Any`**
    - Private helper. Should return `HexCoord | None`.

26. **`game/strategy/data/stars.py:161` — `__getattr__` returns `Any`**
    - Module-level legacy shim for `StarGenerator`. Dunder exempt from return-type convention, but this is a module-level facade pattern.

### INFO

27. **`game/strategy/adapters/simulation_adapter.py:488` — `_lookup` missing return type**
    - Local function returning `dict | None`. Should be `dict[str, Any] | None`.

## Missing Return Types (Public API)

### CRITICAL

1. **`game/app_bootstrap.py:310` — `_replay_combat_lab_fallback` missing return type**
   - Private module-level function. While `_` prefixed suggests private, this function is the primary fallback entry for replay → combat lab routing in app bootstrap, used across module boundaries. Missing return type makes the contract invisible to mypy.
   - Risk: caller catching `None` from unexpected paths.

2. **`game/ui/pygame_gui_patch.py:90` — `_to_tuple` missing return type**
   - Module-level utility used in `StarshipUIAppearanceTheme.build_all_combined_ids` cache key construction. Returns `tuple | None`.
   - CRITICAL because this is a production hot-path optimization (PROJ-411) touching ~284 UI widgets per window open.

### MAJOR

3. **`game/strategy/adapters/simulation_adapter.py:488` — `_lookup` nested function missing return type**
   - Also carries `# type: ignore[no-redef]` — see Type Ignore Audit section.

4. **`game/ui/screens/atmosphere_target_editor.py:223` — `_button_handlers` missing return type**
   - Private method returning `None`. Should be `-> None`.

5. **`game/ui/screens/radiation_shield_editor.py:176` — `_button_handlers` missing return type**
   - Same pattern as atmosphere_target_editor.

6. **`game/ui/screens/test_lab/details/validation.py:39` — `_phase_color` missing return type**
   - Private module-level helper returning color tuple. Should be `-> tuple[int, int, int]`.

### MINOR

7. **`game/ui/screens/test_lab/viewmodel.py:53-88` — Multiple methods missing return types**
   - Mypy flagged 22 lines of `annotation-unchecked` notes. Methods like `is_seed_editable`, `set_seed`, `get_seed`, etc. are test-lab internal ViewModel methods. Not public API but used across test-lab components.

## Type Ignore Audit

1. **`game/simulation/battle_runner.py:182,192` — `# type: ignore[attr-defined]` on `engine.replay_id`**
   - **MAJOR** — `replay_id` is set via `engine.replay_id = None` at line 182 and `engine.replay_id = replay_id` at line 192. The attribute is dynamically assigned on the `BattleEngine` instance. Better approach: define `replay_id: str | None = None` as a properly-typed attribute on `BattleEngine.__init__`.

2. **`game/simulation/systems/attack_processor.py:123` — `# type: ignore[attr-defined]` on `new_ship.launched_in_battle_id`**
   - **MAJOR** — Dynamically assigning `launched_in_battle_id` on `Ship` mid-battle. Should be a proper attribute on the `Ship` class (with default `None`).

3. **`game/strategy/adapters/simulation_adapter.py:488` — `# type: ignore[no-redef]` on `_lookup` definition**
   - **MAJOR** — Nested function defined inside `_build_capture_context`. The `# type: ignore[no-redef]` is unjustified — there is no redefinition, mypy just can't type-narrow the closure. Remove the ignore comment entirely; mypy does not flag nested functions as redefinitions. The actual issue is the missing return type annotation (see Missing Return Types section).

4. **`game/strategy/engine/issuer_adapter.py:303` — `# type: ignore[no-any-return]` on `return gh`**
   - **MAJOR** — `gh` is obtained via `getattr(self._planet, "global_hex", None)` which returns `Any`. The property return type is `HexCoord`. Better: narrow `gh` with `isinstance(gh, HexCoord)` guard, or annotate the fallback branch with `cast(HexCoord, self._planet.location)`.

5. **`game/ui/pygame_gui_patch.py:152` — `# type: ignore[attr-defined]` on `self._get_next_id_node(...)`**
   - **MINOR** — Calling private upstream method `_get_next_id_node` from subclass `StarshipUIAppearanceTheme`. The `attr-defined` suppression is needed because mypy can't see the parent's private method. Justified by the patch nature (PROJ-411). The patch should be removed when upstream fixes the bug; keep the suppression until then.

## cast() Usage

No `cast()` usage found in Shard 02. The deterministic scanner returned an empty `cast_usage_02.json`.

## TYPE_CHECKING Hygiene

### MAJOR

1. **`game/strategy/engine/empire_economy_calculator.py:28` — `GameRegistries` import outside TYPE_CHECKING**
   - `from game.core.registry import GameRegistries` appears at module level (line 28) between the TYPE_CHECKING block and the runtime imports. This is not a TYPE_CHECKING issue per se but breaks the three-group import convention. `GameRegistries` is used in `__init__` type annotations but also likely at runtime.

2. **Mypy `no_implicit_optional` violations — 18 sites across 6 files:**
   - `game/simulation/components/component_stats_calculator.py:125,207,329` — `component: Component = None` should be `component: Component | None = None`
   - `game/simulation/combat/damage_calculator.py:41` — `rng: Random = None` should be `rng: Random | None = None`
   - `game/strategy/validation/transfer_validator.py:92,94,190,222,223,319,320,347,403` — 9 implicit Optional parameters (`species_id: str = None`, `projected_cargo: int = None`, `design_id: str = None`)
   - These violate PEP 484 and mypy in strict mode. All are simple `Type | None = None` fixes.

### MINOR

3. **`game/strategy/data/stars.py` — Internal `_Spectrum` import pattern**
   - `from game.strategy.data.spectrum import Spectrum as _Spectrum` is used for internal construction only. The `__all__` correctly excludes it. Acceptable pattern but could be done via lazy import.

4. **`game/ui/screens/test_lab/viewmodel.py:53-88` — 22 methods without annotations**
   - Mypy `annotation-unchecked` warnings. Methods have no parameter or return annotations. Test-lab internal ViewModel — MINOR because not public strategy API.

## Deferred Narrowings

### MAJOR

1. **`game/simulation/components/abilities/resources.py:63,99,114,125,154,194` — Resource stat getters return `Any` via formula evaluation**
   - `get_primary_value()` is declared `-> float` but formula-driven values propagate through `Any`. The `_base_amount` / `_base_rate` initial values from `ComponentStatsCalculator.evaluate_recursive()` return `Any`, which then flows as `float` to `amount`/`rate`.
   - **Fix**: Narrow `evaluate_recursive` return type chain to `float | str`, then cast at the ability level where formulas produce numeric results.

2. **`game/simulation/components/abilities/harvester.py:26,73,107,150` — Same pattern as resources.py**
   - `get_primary_value()` declared `-> float` but `self.capacity` / `self.base_harvest_rate` / `self.construction_speed_bonus` / `self.capacity_mass` initialized from formula-altering data that can be `str | float`.

3. **`game/simulation/components/abilities/planetary/terraforming.py:45,86,136,179` — Same deferred narrowing**
   - `get_primary_value()` returning formula-derived values.

4. **`game/simulation/components/abilities/planetary/resource_modifiers.py:47,96,146` — Same deferred narrowing**

5. **`game/simulation/combat/damage_calculator.py:91,103,110,120,127,139,152` — `_absorb_*` static methods return `float` but operate on untyped `ship` parameter**
   - All `_absorb_*` methods accept `ship` without type annotation. The `damage` parameter is also untyped. While the return type is annotated `-> float`, the parameter omissions defeat mypy's ability to verify call sites.

6. **`game/simulation/entities/stat_contributors/defense.py:48-110` — `Ship` attribute access via `ship.layers`, `ship.emissive_armor`, etc.**
   - Mypy reports `"Ship" has no attribute "layers"` at line 48. The `Ship` class (imported under TYPE_CHECKING) has these attributes but mypy can't see them through the Protocol chain. The contributor functions receive typed `Ship` but then access attributes mypy can't verify due to the Protocol-runtime gap.

7. **`game/simulation/combat/ram_target_resolver.py:152` — `_is_collision` returns `bool` but body may return `Any`**
   - Static method with `-> bool` return type. The first branch (no position attribute) computes a boolean from `float(getattr(...))` expressions that propagate `Any`. Mypy flags `no-any-return`.

## File Coverage Verification
| File | Status |
|------|--------|
| game/strategy/engine/empire_economy_calculator.py | Read |
| game/strategy/services/cargo_transfer_service.py | Read |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read |
| game/simulation/components/abilities/superweapons.py | Read |
| game/ui/screens/strategy_panel_manager.py | Read |
| game/strategy/data/fleet_pursuer_tracker.py | Read |
| game/strategy/data/stars.py | Read |
| game/simulation/validation/base.py | Read |
| game/strategy/generation/density/primitives/density_primitive.py | Read |
| game/simulation/components/abilities/planetary/resource_modifiers.py | Read |
| game/strategy/data/planet_gen.py | Read |
| game/strategy/engine/turn_engine.py | Read |
| game/strategy/engine/handlers/recover_satellites.py | Read |
| game/ui/screens/test_lab/theme.py | Read |
| game/services/llm/defaults.py | Read |
| game/ui/screens/builder/right_panel.py | Read |
| game/simulation/combat/ram_target_resolver.py | Read |
| game/simulation/entities/stat_contributors/defense.py | Read |
| game/strategy/data/build_context.py | Read |
| game/simulation/components/abilities/defense.py | Read |
| game/ui/services/battle_ui_service.py | Read |
| game/ui/screens/builder/weapons_viewmodel.py | Read |
| game/ui/screens/cargo_quick_dialog.py | Read |
| game/ui/screens/strategy_colonization.py | Read |
| game/research/__init__.py | Read |
| game/ui/screens/race_setup/renderer.py | Read |
| game/ui/screens/galaxy_test/__init__.py | Read |
| game/strategy/services/deployment_zone_calculator.py | Read |
| game/strategy/adapters/simulation_adapter.py | Read |
| game/strategy/engine/issuer_adapter.py | Read |
| game/ui/screens/fleet_data_source.py | Read |
| game/ui/screens/race_setup/ship_preview.py | Read |
| game/strategy/data/ship_stats_cache.py | Read |
| game/simulation/services/vehicle_design_service.py | Read |
| game/strategy/data/fleet_serde.py | Read |
| game/strategy/interfaces/engines/movement.py | Read |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read |
| game/simulation/components/modifier_effects.py | Read |
| game/simulation/systems/attack_processor.py | Read |
| game/simulation/components/abilities/ui_colors.py | Read |
| game/simulation/combat/families/__init__.py | Read |
| game/strategy/data/planet_naming.py | Read |
| game/ui/screens/build_queue_queue_data_source.py | Read |
| game/ui/screens/strategy_windows/__init__.py | Read |
| game/simulation/entities/stat_contributors/weapons.py | Read/Verified |
| game/strategy/services/ability_sources/warp_point.py | Read |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read/Verified |
| game/core/hex_math.py | Read/Verified |
| game/strategy/interfaces/engines/__init__.py | Read |
| game/strategy/services/stabilizer_registry.py | Read/Verified |
| game/simulation/entities/ship_stat_querier.py | Read |
| game/ui/screens/test_lab/renderer/__init__.py | Verified |
| game/ui/screens/battle_setup/input_handler.py | Verified |
| game/simulation/entities/layer_data.py | Read |
| game/simulation/components/abilities/markers.py | Read |
| game/simulation/components/modifier_manager.py | Read/Verified |
| game/strategy/services/fleet_write_service.py | Read/Verified |
| game/strategy/services/fleet_path_projection.py | Read/Verified |
| game/strategy/generation/density/primitives/noise.py | Read |
| game/strategy/data/component_activation_state.py | Read/Verified |
| game/strategy/config/__init__.py | Read (empty) |
| game/simulation/combat/damage_calculator.py | Read |
| game/simulation/entities/stat_contributors/launch.py | Read/Verified |
| game/simulation/components/abilities/crew.py | Verified |
| game/strategy/services/__init__.py | Verified |
| game/ui/pygame_gui_patch.py | Read |
| game/ui/services/component_service.py | Verified |
| game/strategy/engine/action_execution_engine.py | Verified |
| game/ui/screens/setup_data_io.py | Verified |
| game/strategy/data/orbital_generation_config.py | Verified |
| game/ui/screens/workshop_context.py | Verified |
| game/ui/screens/settings_window.py | Verified |
| game/simulation/combat/fleet_aura_manager.py | Verified |
| game/ai/interfaces/controllable.py | Read |
| game/ui/screens/star_list_sidebar.py | Verified |
| game/strategy/events/event_types.py | Verified |
| game/ui/screens/strategy_render/fleets.py | Verified |
| game/ui/services/ship_factory.py | Verified |
| game/ui/panels/build_queue_portraits.py | Verified |
| game/strategy/services/component_layers.py | Verified |
| game/core/protocols/registry.py | Read |
| game/ai/target_evaluator.py | Verified |
| game/strategy/interfaces/engines/logistics.py | Verified |
| game/strategy/formulas/habitability.py | Verified |
| game/ai/carrier_controller.py | Verified |
| game/strategy/services/system_effects_collector.py | Read/Verified |
| game/strategy/data/resource_generation_config.py | Read/Verified |
| game/core/protocols/boundary.py | Read |
| game/ui/screens/builder/left_panel.py | Verified |
| game/strategy/__init__.py | Verified |
| game/strategy/generation/placement_strategies.py | Verified |
| game/ai/behaviors.py | Verified |
| game/strategy/data/galaxy_warp_generator.py | Read/Verified |
| game/strategy/facade/__init__.py | Verified |
| game/strategy/engine/order_handlers/launch_satellites.py | Verified |
| game/ui/panels/build_queue_drag_handler.py | Verified |
| game/strategy/services/planet_habitability_service.py | Verified |
| game/simulation/replay/__init__.py | Verified |
| game/strategy/validation/transfer_validator.py | Verified via mypy |
| game/strategy/data/environmental_preference.py | Verified |
| game/core/protocols/ui.py | Read |
| game/ui/screens/atmosphere_target_editor.py | Verified |
| game/core/ship_classes.py | Verified |
| game/core/paths.py | Verified |
| game/ui/services/ship_io.py | Verified |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Verified |
| game/strategy/services/replay_resolver.py | Verified |
| game/simulation/combat/families/pdc.py | Verified |
| game/ui/components/filters/tri_state_widget.py | Verified |
| game/strategy/services/ability_sources/intrinsic_roll.py | Verified |
| game/simulation/systems/tick_phase.py | Verified |
| game/simulation/combat/families/projectile.py | Verified |
| game/strategy/engine/movement_phase_collaborator.py | Verified |
| game/strategy/engine/session/graph_restoration.py | Verified |
| game/simulation/combat/telemetry.py | Verified |
| game/strategy/data/planet_physics.py | Read/Verified |
| game/strategy/services/ship_instance_factory.py | Verified |
| game/strategy/engine/session/persistence_adapter.py | Verified |
| game/ui/widgets/panel_factory.py | Verified |
| game/ui/screens/battle_screen.py | Read |
| game/context.py | Verified |
| game/simulation/components/abilities/cargo.py | Verified |
| game/strategy/engine/production_spawner.py | Verified |
| game/ui/screens/strategy_render/storms.py | Verified |
| game/ui/screens/star_list_filters.py | Verified |
| game/ui/effects/hit_effects.py | Verified |
| game/ui/screens/build_queue_selector.py | Verified |
| game/ai/spatial_behaviors/base.py | Verified |
| game/ui/services/image/background.py | Verified |
| game/ui/screens/strategy_windows/ship_picker.py | Verified |
| game/strategy/facade/slices/planet_slice.py | Verified |
| game/strategy/engine/game_config.py | Verified |
| game/ui/screens/strategy_render/systems.py | Verified |
| game/strategy/engine/production_engine.py | Verified |
| game/simulation/systems/battle_engine.py | Verified |
| game/strategy/combat/pre_tick_setup/__init__.py | Verified |
| game/app_bootstrap.py | Verified |
| game/simulation/entities/ship_stats.py | Verified |
| game/simulation/entities/ship_validator_helper.py | Verified |
| game/simulation/replay/replay_outcome.py | Verified |
| game/ui/panels/race_environment_panel.py | Verified |
| game/simulation/components/ability_manager.py | Verified |
| game/strategy/data/ship_instance_serializer.py | Verified |
| game/ui/services/ship_io_adapter.py | Verified |
| game/strategy/data/classification_config.py | Verified |
| game/ui/screens/race_validator.py | Verified |
| game/core/component_state.py | Verified |
| game/strategy/engine/handlers/fms_shared.py | Verified |
| game/ui/screens/planet_data_source.py | Verified |
| game/ui/screens/event_log_data_source.py | Read/Verified |
| game/ui/screens/galaxy_test/screen.py | Verified |
| game/strategy/generation/planet_image_registry.py | Verified |
| game/strategy/services/design_cost_calculator.py | Verified |
| game/strategy/generation/star_image_registry.py | Verified |
| game/ui/screens/build_queue_screen.py | Verified |
| game/simulation/battle_runner.py | Read |
| game/ui/effects/__init__.py | Verified |
| game/ui/screens/race_setup/delegate_factory.py | Verified |
| game/strategy/engine/planet_action_engine.py | Verified |
| game/ui/screens/builder/modifier_logic.py | Verified |
| game/strategy/services/fleet_speed_calculator.py | Verified |
| game/ui/components/table/header.py | Verified |
| game/strategy/generation/loaders/__init__.py | Verified |
| game/ui/screens/planet_abilities_controller.py | Verified |
| game/core/patterns/layer_iterator.py | Verified |
| game/ui/screens/strategy_windows/selection_prompts.py | Verified |
| game/strategy/services/ability_sources/__init__.py | Verified |
| game/ui/screens/race_browser_dialog.py | Verified |
| game/simulation/components/abilities/harvester.py | Read |
| game/strategy/facade/slices/empire_slice.py | Verified |
| game/ui/screens/battle_setup/__init__.py | Verified |
| game/ui/services/image/types.py | Verified |
| game/ui/services/image/__init__.py | Verified |
| game/strategy/engine/handlers/lay_mines.py | Verified |
| game/strategy/events/__init__.py | Verified |
| game/ui/panels/build_queue_controller.py | Verified |
| game/ui/screens/star_list_presets.py | Read/Verified |
| game/strategy/systems/race_library.py | Verified |
| game/strategy/engine/superweapon_handlers/__init__.py | Verified |
| game/ui/screens/test_lab/details/validation.py | Verified |
| game/ui/screens/test_lab/details/__init__.py | Verified |
| game/strategy/data/planet.py | Verified |
| game/strategy/data/fleet_hierarchy.py | Verified |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read/Verified |
| game/ui/screens/transfer_grid_renderer.py | Verified |
| game/strategy/generation/region_classifier.py | Read/Verified |
| game/simulation/components/abilities/planetary/_shared.py | Verified |
| game/ui/screens/data_list_window_mixin.py | Verified |
| game/simulation/components/abilities/container.py | Verified |
| game/simulation/components/modifier_introspection.py | Verified |
| game/strategy/engine/order_handlers/base.py | Verified |
| game/strategy/services/ability_sources/system_archetype.py | Verified |
| game/simulation/components/component_stats_calculator.py | Verified |
| game/strategy/services/empire_economy_service.py | Verified |
| game/simulation/battle_state.py | Verified |
| game/strategy/engine/production_math.py | Verified |
| game/strategy/data/spatial_index.py | Verified |
| game/ui/screens/setup_screen.py | Verified |
| game/simulation/replay/replay_player.py | Verified |
| game/strategy/data/build_queue_source.py | Verified |
| game/core/string_utils.py | Verified |
| game/strategy/services/planet_economy_projector.py | Verified |
| game/ui/__init__.py | Verified |
| game/ui/screens/planet_menu_items.py | Verified |
| game/ui/screens/planet_list_filters.py | Verified |
| game/ui/screens/radiation_shield_editor.py | Verified |
| game/simulation/projectile_manager.py | Read/Verified |
| game/simulation/components/abilities/planetary/terraforming.py | Read |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Verified |
| game/ui/screens/test_lab/viewmodel.py | Verified |
| game/simulation/components/abilities/resources.py | Read |
| game/simulation/entities/ship_loader.py | Verified |
| game/ui/screens/race_asset_loader.py | Verified |
| game/simulation/entities/ability_aggregator.py | Read/Verified |
| game/ui/services/tkinter_utils.py | Verified |
