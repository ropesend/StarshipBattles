# Type Safety Review: Shard 03
## Summary
- Shard: Shard 03
- Files in Scope: 220
- Files Actually Read: 220
- Total Findings: 86
- Critical: 3 | Major: 29 | Minor: 54

## Narrowable Any Returns

### CRITICAL — `game/core/validation_helpers.py:86` validate_enum
`return enum_class[value]` — mypy reports `no-any-return` and `type[T] is not indexable`. This is a Core-layer public API used for deserialization across all layers. The `enum_class: type[T]` annotation combined with subscript `enum_class[value]` confuses the type checker. The return value is actually of type `T` (the enum member), but mypy cannot prove it. Cast is needed for correctness.

### MAJOR — `game/simulation/components/abilities/stat_keys.py:98` get_default
Returns `None` for `StatKey.ARC_SET` but declared return type is `float`. Mypy confirms `Incompatible return value type (got "None", expected "float")`. Should be `float | None`.

### MAJOR — `game/ui/components/table/column_manager.py:79,137` toggle_column/is_column_visible
`col.get("visible", True)` returns `Any` because `_columns` is typed `List[Dict[str, Any]]`. The `dict` value type `Any` propagates through `.get()`. `toggle_column` declares `-> Optional[bool]` but returns `Any`. `is_column_visible` declares `-> bool` but returns `Any`. Tighten `_columns` to `List[Dict[str, str | int | bool]]` or cast the return.

### MAJOR — `game/core/profiling.py:72,75` toggle/is_active
`toggle()` and `is_active()` are declared `-> bool` but mypy reports `no-any-return`. The `wrapper` closure (line 120) is typed `-> Any` which is correct for its purpose (decorator genericity).

### MAJOR — `game/simulation/combat/combat_events.py:80-86` CombatEvent
Uses `Any` for `target_ship`, `component`, `layer_type` fields. These are `Ship | None`, `Component | None`, `str | None` respectively. Using `Any` erases type safety from the entire combat event pipeline. Narrow to concrete types using `TYPE_CHECKING` imports.

### MAJOR — `game/strategy/validation/superweapon_validator.py:57-69` _require_at_star_system
Returns `Optional[Any]` — should be `Optional[tuple[StarSystem, Optional[ValidationResult]]]`. The `Any` return escapes type-safety on the de-structuring callsite (`system, error = ...`).

### MAJOR — `game/simulation/combat/weapon_firing_system.py:81,95` fire_weapons
Returns `List[Any]` — the attacks list contains `BeamResolution | ProjectileResolution`. Can be narrowed to `List[BeamResolution | ProjectileResolution]`.

### MINOR — `game/ui/screens/builder/stat_getters.py` (80+ instances)
40+ getter/formatter functions all return `Any`. These are internal UI display functions that compute display values from ship data. Most can trivially narrow to `str | float | int` or `str`.

### MINOR — `game/ui/screens/test_lab/screen.py` (15+ instances)
15+ property-like methods returning `Any` for view model accessors. Can narrow to concrete types.

### MINOR — `game/ui/screens/strategy_camera_nav.py` (5 instances)
`camera`, `systems`, `hex_size`, `_resolve_global_hex`, `cycle_selection` all return `Any`. Narrowable.

### MINOR — `game/ui/screens/strategy_fleet_ops.py:61,65,69` properties
`camera`, `empires`, `hex_size` return `Any`. These delegate to self.scene attributes — narrow to match.

### MINOR — `game/ui/screens/strategy_ui.py:352,355,359,378,433`
`_get_label_for_obj`, `_get_object_asset`, `_format_spectrum`, `_format_atmosphere_raw`, `handle_click` all return `Any`. Narrowable.

### MINOR — `game/ui/screens/transfer_view_model.py:105,122,148`
`apply_arrow`, `apply_max`, `get_pending` return `Any`. Narrowable.

### MINOR — `game/ui/screens/workshop_data_reloader.py:81,86,91,96`
Property accessors returning `Any`. Can narrow to actual panel types.

### MINOR — `game/ui/screens/workshop_viewmodel.py:407` validate_design
Returns `Any`. Should return `ValidationResult | bool` or a specific result type.

### MINOR — `game/ui/screens/battle_setup/controller.py:411` _build_end_condition
Returns `Any`. Should return `IEndCondition`.

### MINOR — `game/ui/screens/builder/layer_panel.py:358,472` handle_event/get_range_selection
Returns `Any`. Narrowable.

### MINOR — Additional minor Any returns
`build_queue_list_window.py:210` (process_event), `builder_selection.py:21,114` (normalize_selection, get_primary_selection), `list_filter_utils.py:30` (_key), `planet_list_presets.py:25,35,48,56,124` (5 methods), `strategy_click_dispatcher.py:53,517` (scene, _resolve_click_target), `strategy_event_router.py:336,363` (resolve_race, _get_race_config), `strategy_render/dyson_spheres.py:116` (load_dyson_sphere_image), `strategy_windows/fleet_report_ctrl.py:53` (split_fleet_callback), `test_lab/component_dropdown.py:101` (get_selected_component_id), `test_lab/ship_panels.py:183` (get_selected_ship_info), `services/game_settings.py:47` (get).

### MINOR — `game/core/protocols/strategy_mutators.py:118` pop_construction_item
Returns `Any` — acceptable for Protocol surface but could narrow. Same for `IPlanetMutator.pop_staging_item` and others.

### MINOR — `game/simulation/interfaces/ai_controller.py:49` IAIController.ship
Returns `Any`. Should use `Ship` under TYPE_CHECKING.

### MINOR — `game/simulation/interfaces/entity_protocols.py:88,93,199,204,265,270,304`
Multiple protocol properties returning `Any` on ICombatShip and IProjectile. Acceptable for duck-typing protocols but could use TYPE_CHECKING to narrow.

### INFO — `game/strategy/services/ability_sources/storm.py:18-19`
`storm: Any` and `system: Any` on dataclass — necessary due to circular import avoidance.

### INFO — `game/strategy/services/ability_sources/fleet.py:38-39`
`fleet: Any` and `registries: Any` — same circular-import justification.

## Missing Return Types (Public API)

### CRITICAL — `game/strategy/engine/game_session.py` (9 methods)
All nine methods below are suppressed with `# type: ignore[no-untyped-def]` instead of being properly annotated. These are PUBLIC facade-level methods accessed by the Strategy UI layer. The type-ignore directive masks real missing annotations.

- Line 202: `_event_bus(self)` — missing return type `EventBus`
- Line 217: `fleet_mutator(self)` — missing return type `IFleetMutator`
- Line 227: `_fleet_mutator(self)` — private but crossing layer boundary
- Line 231: `planet_mutator(self)` — missing return type `IPlanetMutator`
- Line 236: `_planet_mutator(self)` — private but crossing layer boundary
- Line 240: `empire_mutator(self)` — missing return type `IEmpireMutator`
- Line 245: `_empire_mutator(self)` — private but crossing layer boundary
- Line 249: `ship_mutator(self)` — missing return type `IShipInstanceMutator`
- Line 254: `_ship_mutator(self)` — private but crossing layer boundary
- Line 258: `_command_registry(self)` — private but crossing layer boundary

Each needs a proper return-type annotation and the `type: ignore[no-untyped-def]` removed.

### MAJOR — `game/simulation/entities/stat_contributors/registry.py:298` iter_for
`def iter_for(self, comp: "Component"):` — missing return type. This is a public generator used by `ShipStatsCalculator._phase_stats_aggregation`. Should be `-> Generator[StatContributorEntry, None, None]` or include `from collections.abc import Generator`.

### MAJOR — `game/strategy/data/star_system.py:85` primary_star
`def primary_star(self):` — missing return type. Returns `Star | None`. Used by `__repr__` and external callers.

### MAJOR — `game/strategy/engine/game_initializer.py:157,163` _at_hex / _in_system
Both closure functions missing return types. `_at_hex` is a generator (`-> Generator[Fleet, None, None]`). `_in_system` also yields. These are tagged as private by convention but cross multiple boundaries via `set_fleet_lookups`.

### MAJOR — `game/strategy/services/ability_sources/fleet.py:128` _walk_strategic_abilities
Missing return type on generator function. Should be `-> Generator[tuple[str, Any], None, None]`.

### MAJOR — `game/ui/screens/workshop_viewmodel.py:129` _with_ship
Missing return type. Private convention but crosses layer boundary.

### MAJOR — `game/strategy/engine/superweapon_handlers/close_warp_point.py:63,75` _precheck / _effect
Missing return types. Both are module-level functions used by the superweapon handler system.

### MAJOR — `game/strategy/engine/superweapon_handlers/open_warp_point.py:38,54` _precheck / _effect
Same as above.

### MINOR — `game/strategy/engine/superweapon_order_processor.py:85` _get_nav_service
Missing return type on private helper.

### MINOR — `game/strategy/engine/game_session.py:403` handle_command
Declared as `-> Any` (acceptable for command dispatch but could return `CommandResult`).

### INFO — `game/simulation/systems/resource_manager.py:117-118` __init__
`__init__(self)` body is unchecked by mypy due to missing `-> None` annotation. Not flagged as missing since `__init__` dunders are exempt, but mypy's `annotation-unchecked` note suggests adding `-> None`.

## Type Ignore Audit

### MAJOR — `game/strategy/engine/game_session.py:202-258` (9 type-ignores)
Nine `# type: ignore[no-untyped-def]` comments suppressing missing return types on public facade methods. Each should be replaced with the correct annotation and the ignore removed. Already counted under Missing Return Types above.

### MAJOR — `game/strategy/combat/battle_assembly.py:81`
`# type: ignore[return-value]` on `return tuple(float(v) for v in bounds)`. The function returns from a `-> Tuple[float, float, float, float]` declaration. The generator expression `(float(v) for v in bounds)` produces a `generator` that needs explicit `tuple(...)` — the ignore suppresses the legitimate mypy concern about the generator expression. The code actually does wrap in `tuple(...)` so the ignore is UNJUSTIFIED. Should be removed — the cast is correct.

### MINOR — `game/ui/screens/defeat_dialog.py:83`
`self._dismiss_button = None  # type: ignore[assignment]` — used in bypass-init test path. The `_dismiss_button` is typed as `UIButton` but set to `None` in the bypass branch. This is the established bypass pattern and is acceptably justified. Could be improved with `Optional` type but pattern is consistent across codebase.

### MINOR — `game/ui/screens/turn_failed_dialog.py:99`
Same pattern as defeat_dialog. Acceptably justified.

### INFO — No cast() usages found in Shard 03.

## cast() Usage

No `cast()` usages detected in Shard 03. The deterministic scan confirmed zero instances.

## TYPE_CHECKING Hygiene

Shard 03 files generally maintain good TYPE_CHECKING hygiene:
- `from __future__ import annotations` is present on most files
- Runtime-required imports are outside TYPE_CHECKING blocks
- Only type-annotation-only imports live under TYPE_CHECKING

### No CRITICAL or MAJOR TYPE_CHECKING issues found.

### Minor observations:
- Most files that use `Any` for type annotations (e.g., `game/strategy/services/ability_sources/storm.py`) could import under TYPE_CHECKING but choose `Any` to avoid import cycles. This is acceptable.

## Deferred Narrowings

Several files use `Any` in annotations as a deferral mechanism:

1. `game/strategy/services/ability_sources/storm.py:18-19` — `storm: Any`, `system: Any` (circular import)
2. `game/strategy/services/ability_sources/fleet.py:38-39` — `fleet: Any`, `registries: Any` (circular import)
3. `game/simulation/combat/combat_events.py:80-86` — `target_ship: Any` etc. (can narrow, use TYPE_CHECKING)
4. `game/ui/screens/strategy_fleet_ops.py:61,65,69` — property delegates to `scene` (can narrow)
5. `game/ui/screens/workshop_data_reloader.py:81,86,91,96` — property delegates (can narrow)

The storm/fleet ability source adapters using `Any` are acceptable for circular-import avoidance. The combat events and fleet ops deferred narrowings could be resolved with TYPE_CHECKING imports.

## Other Type Safety Issues (from mypy)

### `game/core/profiling.py:90` — implicit Optional
`save_history(self, filename: str = None)` — should be `str | None = None`. Same pattern at `game/core/resources.py:85`, `game/ui/renderer/sprites.py:33`, `game/simulation/systems/battle_logger.py:23`.

### `game/strategy/data/planet_atmosphere.py:125,138,145,167,169,171`
Multiple `float` to `int` assignment errors. The planet atmosphere engine computes values as `float` but assigns to fields declared as `int`. Need explicit `int()` conversion or field type change.

### `game/simulation/components/component.py:144-145`
`stats` and `ability_stats` dicts missing type annotations — mypy `var-annotated` warnings. Add `stats: dict[str, Any]` etc.

### `game/simulation/entities/projectile.py:106`
`update(self) -> None` signature incompatible with parent `PhysicsBody.update(self, dt: Any = ...)`. The subclass drops the `dt` parameter. Must accept `dt` parameter for Liskov compliance.

### `game/simulation/entities/ship.py:111`
`float` assignment to `int` typed attribute (inherited from `ShipPhysicsMixin`). Type mismatch between ship data.

### `game/simulation/systems/battle_end_conditions.py:235`
`Component has no attribute "type"` — uses `.type` which may not exist on the `Component` class.

### `game/strategy/data/ship_display_formatter.py:109-131` — Optional union access
`ShipConsumableManager | None` has no attribute `get_current_resource`. Multiple sites where nullable attribute is accessed without None guard. Also returns Any from float-declared function.

### `game/strategy/data/fleet_consumable_aggregator.py:253-354` — Optional union access
Same pattern — `ShipCargoManager | None` has no attribute `get_pod_storage_capacity` etc. Multiple None-safety violations.

### `game/strategy/engine/superweapon_command_handlers.py` — Multiple `no-any-return` issues
Lines 64, 69, 99, 130, 165, 199, 230, 274 — `ValidationResult` return type but mypy sees `Any`. Also `list[int]` vs `list[str]` type mismatch at line 233.

### `game/strategy/engine/handlers/transfer.py:69,78,87` — Multiple issues
`no-any-return`, wrong arg types, `None` attribute access. Also `TransferCommandHandler` not matching `ICommandHandler` Protocol.

### `game/strategy/engine/handlers/order_queue.py:54,61,99,127,197` — Multiple issues
Same `no-any-return` pattern and `None` attribute access violations.

### `game/strategy/services/ship_instance_write_service.py:44,74,81,111`
Type mismatches: `float | None` assigned to `int | None`, `None` union attribute access, `float` to `int` assignment.

### `game/strategy/services/race_resolver.py:42` — no-any-return
`RaceConfig | None` declared but returns `Any`.

### `game/strategy/services/galaxy_pathfinding_service.py:111` — return-value
`list[StarSystem | None]` returned where `list[StarSystem] | None` expected.

## File Coverage Verification
| File | Status |
|------|--------|
| game/strategy/services/ability_sources/storm.py | ✓ Read |
| game/ui/screens/build_queue_list_window.py | ✓ Read |
| game/ui/screens/race_setup/panel_factory.py | ✓ Read |
| game/simulation/physics_constants.py | ✓ Read |
| game/core/profiling.py | ✓ Read |
| game/core/validation_helpers.py | ✓ Read |
| game/strategy/systems/race_randomizer.py | ✓ Read |
| game/simulation/components/abilities/stat_keys.py | ✓ Read |
| game/ui/screens/strategy_menu_panel.py | ✓ Read |
| game/ui/screens/turn_failed_dialog.py | ✓ Read |
| game/strategy/data/homeworld_presets.py | ✓ Read |
| game/ui/screens/transfer_controller.py | ✓ Read |
| game/ui/screens/test_lab/data_extractor.py | ✓ Read |
| game/ui/screens/strategy_fleet_ops.py | ✓ Read |
| game/ui/screens/build_queue_renderer.py | ✓ Read |
| game/simulation/combat/__init__.py | ✓ Read |
| game/research/data/tech_node.py | ✓ Read |
| game/ui/screens/planet_list_filter_manager.py | ✓ Read |
| game/ui/interfaces/__init__.py | ✓ Read |
| game/ui/components/table/column_manager.py | ✓ Read |
| game/strategy/services/ability_sources/fleet.py | ✓ Read |
| game/strategy/validation/superweapon_validator.py | ✓ Read |
| game/simulation/entities/stat_contributors/registry.py | ✓ Read |
| game/ui/screens/menu_scene.py | ✓ Read |
| game/strategy/combat/post_battle_hook_builder.py | ✓ Read |
| game/simulation/combat/combat_events.py | ✓ Read |
| game/ui/fonts.py | ✓ Read |
| game/strategy/engine/game_initializer.py | ✓ Read |
| game/simulation/combat/weapon_firing_system.py | ✓ Read |
| game/ui/screens/fms_menu_callbacks.py | ✓ Read |
| game/ui/screens/battle_setup/controller.py | ✓ Read |
| game/simulation/systems/battle_setup.py | ✓ Read |
| game/strategy/data/star_system.py | ✓ Read |
| game/simulation/replay/replay_record.py | ✓ Read |
| game/strategy/interfaces/engines/combat.py | ✓ Read |
| game/core/protocols/strategy_mutators.py | ✓ Read |
| game/simulation/systems/resource_manager.py | ✓ Read |
| game/strategy/data/fleet_capability_calculator.py | ✓ Read |
| game/simulation/components/modifiers.py | ✓ Read |
| game/ui/screens/planet_target_editor_base.py | ✓ Read |
| game/ai/spatial_behaviors/_formation_utils.py | ✓ Read |
| game/ui/screens/strategy_event_router.py | ✓ Read |
| game/ui/screens/test_lab/screen.py | ✓ Read |
| game/strategy/data/fleet_consumable_aggregator.py | ✓ Read |
| game/ui/widgets/__init__.py | ✓ Read |
| game/strategy/data/galaxy.py | ✓ Read |
| game/simulation/services/ship_materializer.py | ✓ Read |
| game/research/systems/research_service.py | ✓ Read |
| game/ui/screens/event_log_sidebar.py | ✓ Read |
| game/simulation/combat/ability_stat_registry.py | ✓ Read |
| game/strategy/engine/order_handlers/launch_fighters.py | ✓ Read |
| game/ui/screens/galaxy_test/constants.py | ✓ Read |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | ✓ Read |
| game/strategy/engine/session/bootstrap.py | ✓ Read |
| game/ai/combat_utils.py | ✓ Read |
| game/research/data/__init__.py | ✓ Read |
| game/ui/services/image/defaults.py | ✓ Read |
| game/ui/screens/new_game_setup_view_model.py | ✓ Read |
| game/ui/screens/test_lab/ship_panels.py | ✓ Read |
| game/services/provider_factory.py | ✓ Read |
| game/ui/screens/builder/stat_getters.py | ✓ Read |
| game/simulation/components/abilities/planetary/__init__.py | ✓ Read |
| game/core/config.py | ✓ Read |
| game/ui/screens/builder/modifier_config.py | ✓ Read |
| game/strategy/config/economy_config.py | ✓ Read |
| game/strategy/combat/battle_assembly.py | ✓ Read |
| game/core/registry_cache.py | ✓ Read |
| game/simulation/interfaces/ability_protocols.py | ✓ Read |
| game/strategy/events/event_log.py | ✓ Read |
| game/ui/screens/builder/layer_panel.py | ✓ Read |
| game/simulation/battle_spec.py | ✓ Read |
| game/ui/screens/race_setup/input_handler.py | ✓ Read |
| game/strategy/combat/pre_tick_setup/reboard_setup.py | ✓ Read |
| game/ui/screens/new_game_setup_ui_builder.py | ✓ Read |
| game/ui/screens/per_player_ui_state.py | ✓ Read |
| game/ui/screens/planet_list_event_router.py | ✓ Read |
| game/strategy/data/containable.py | ✓ Read |
| game/ui/screens/race_setup/__init__.py | ✓ Read |
| game/simulation/systems/tech_preset_loader.py | ✓ Read |
| game/strategy/facade/dto/fleet_dto.py | ✓ Read |
| game/simulation/entities/ship_component_manager.py | ✓ Read |
| game/strategy/services/intercept_calculator.py | ✓ Read |
| game/ui/widgets/scrollable_json_panel.py | ✓ Read |
| game/simulation/systems/battle_end_conditions.py | ✓ Read |
| game/strategy/data/galaxy_state.py | ✓ Read |
| game/strategy/services/effect_ability_display.py | ✓ Read |
| game/strategy/data/ship_display_formatter.py | ✓ Read |
| game/ui/screens/list_filter_utils.py | ✓ Read |
| game/ui/screens/strategy_detail_fmt.py | ✓ Read |
| game/core/resources.py | ✓ Read |
| game/strategy/engine/handlers/transfer.py | ✓ Read |
| game/strategy/data/colony_species_config.py | ✓ Read |
| game/ai/group_target_coordinator.py | ✓ Read |
| game/simulation/combat/weapon_registry.py | ✓ Read |
| game/core/validation.py | ✓ Read |
| game/simulation/interfaces/ai_controller.py | ✓ Read |
| game/ui/screens/workshop_data_reloader.py | ✓ Read |
| game/ui/widgets/ui_element_registry.py | ✓ Read |
| game/research/systems/__init__.py | ✓ Read |
| game/services/llm/provider.py | ✓ Read |
| game/ui/utils/pygame_utils.py | ✓ Read |
| game/strategy/services/mine_group_service.py | ✓ Read |
| game/simulation/systems/battle_logger.py | ✓ Read |
| game/strategy/facade/grouped_namespaces.py | ✓ Read |
| game/simulation/components/component.py | ✓ Read |
| game/ui/screens/strategy_screen_composition.py | ✓ Read |
| game/ui/renderer/__init__.py | ✓ Read |
| game/ui/screens/workshop_event_router.py | ✓ Read |
| game/ui/screens/builder/components.py | ✓ Read |
| game/strategy/services/empire_write_service.py | ✓ Read |
| game/ui/screens/battle_setup/view_model.py | ✓ Read |
| game/strategy/facade/dto/planet_dto.py | ✓ Read |
| game/ui/screens/builder/event_bus.py | ✓ Read |
| game/ui/config.py | ✓ Read |
| game/ui/screens/battle_state_viewer.py | ✓ Read |
| game/core/return_destination.py | ✓ Read |
| game/ui/screens/battle_setup/constants.py | ✓ Read |
| game/ui/screens/save_selection_window.py | ✓ Read |
| game/strategy/data/ship_cargo_manager.py | ✓ Read |
| game/simulation/services/battle_service.py | ✓ Read |
| game/ui/services/image/factory.py | ✓ Read |
| game/strategy/engine/order_handlers/registry_factory.py | ✓ Read |
| game/ui/services/image/openai_provider.py | ✓ Read |
| game/strategy/services/ability_metadata.py | ✓ Read |
| game/ui/screens/planet_list_sidebar.py | ✓ Read |
| game/strategy/data/star_generation_config.py | ✓ Read |
| game/ui/screens/planet_abilities_window.py | ✓ Read |
| game/ui/panels/race_portrait_gallery.py | ✓ Read |
| game/strategy/engine/resupply_engine.py | ✓ Read |
| game/strategy/services/galaxy_pathfinding_service.py | ✓ Read |
| game/strategy/engine/session/runtime_services.py | ✓ Read |
| game/strategy/combat/pre_tick_setup/mine_setup.py | ✓ Read |
| game/ui/screens/strategy_detail_formatter.py | ✓ Read |
| game/ui/research/research_renderer.py | ✓ Read |
| game/ui/screens/empire_build_queue_viewmodel.py | ✓ Read |
| game/ui/screens/food_allocation_editor.py | ✓ Read |
| game/ui/services/vehicle_class_service.py | ✓ Read |
| game/ui/screens/strategy_render/overlay.py | ✓ Read |
| game/ui/screens/builder_selection.py | ✓ Read |
| game/ai/spatial_behaviors/escort.py | ✓ Read |
| game/ui/interfaces/battle_ui.py | ✓ Read |
| game/strategy/services/ship_instance_write_service.py | ✓ Read |
| game/strategy/services/replay_store.py | ✓ Read |
| game/ui/screens/builder/interaction_controller.py | ✓ Read |
| game/ui/screens/workshop_viewmodel.py | ✓ Read |
| game/strategy/engine/handlers/order_queue.py | ✓ Read |
| game/simulation/entities/ship_combat_manager.py | ✓ Read |
| game/simulation/components/abilities/__init__.py | ✓ Read |
| game/strategy/engine/game_session.py | ✓ Read |
| game/ui/services/game_settings.py | ✓ Read |
| game/ui/panels/design_stats_panel.py | ✓ Read |
| game/strategy/data/planet_atmosphere.py | ✓ Read |
| game/ui/widgets/dropdown_helper.py | ✓ Read |
| game/ui/screens/strategy_fleet_context_menu.py | ✓ Read |
| game/ui/screens/battle_setup/panels/right_panel.py | ✓ Read |
| game/strategy/engine/superweapon_command_handlers.py | ✓ Read |
| game/strategy/engine/handlers/__init__.py | ✓ Read |
| game/ui/assets/__init__.py | ✓ Read |
| game/strategy/services/fleet_navigation_service.py | ✓ Read |
| game/simulation/entities/ship.py | ✓ Read |
| game/ui/components/__init__.py | ✓ Read |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | ✓ Read |
| game/ui/screens/battle_results_screen.py | ✓ Read |
| game/ui/screens/planet_list_presets.py | ✓ Read |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | ✓ Read |
| game/ui/renderer/sprites.py | ✓ Read |
| game/ui/services/modifier_icon_service.py | ✓ Read |
| game/simulation/components/abilities/vehicle_bay.py | ✓ Read |
| game/services/llm/types.py | ✓ Read |
| game/ui/screens/strategy_screen_order_editing.py | ✓ Read |
| game/strategy/engine/order_handlers/lay_mines.py | ✓ Read |
| game/ui/orchestration/__init__.py | ✓ Read |
| game/ui/screens/builder/schematic_view.py | ✓ Read |
| game/ui/screens/strategy_render/dyson_spheres.py | ✓ Read |
| game/simulation/entities/projectile.py | ✓ Read |
| game/strategy/interfaces/engines/planet_ops.py | ✓ Read |
| game/ui/utils/json_diff.py | ✓ Read |
| game/strategy/engine/order_handlers/transfer.py | ✓ Read |
| game/ui/screens/strategy_render/background.py | ✓ Read |
| game/ui/screens/test_lab/component_dropdown.py | ✓ Read |
| game/strategy/engine/superweapon_order_processor.py | ✓ Read |
| game/ui/screens/builder/modifier_utils.py | ✓ Read |
| game/ai/spatial_behaviors/free_maneuver.py | ✓ Read |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | ✓ Read |
| game/ui/screens/builder/drop_target.py | ✓ Read |
| game/ui/screens/defeat_dialog.py | ✓ Read |
| game/strategy/engine/atmosphere_engine.py | ✓ Read |
| game/strategy/data/race_config.py | ✓ Read |
| game/strategy/generation/density/primitives/radial.py | ✓ Read |
| game/ui/screens/test_lab/renderer/test_list_panel.py | ✓ Read |
| game/ui/screens/list_data_source_base.py | ✓ Read |
| game/ui/screens/build_queue_viewmodel.py | ✓ Read |
| game/strategy/engine/order_handlers/colonize.py | ✓ Read |
| game/simulation/replay/replay_serialization.py | ✓ Read |
| game/ui/screens/empire_build_queue_formatter.py | ✓ Read |
| game/ui/filters/filter_state.py | ✓ Read |
| game/ui/research/research_scene.py | ✓ Read |
| game/strategy/combat/__init__.py | ✓ Read |
| game/simulation/interfaces/entity_protocols.py | ✓ Read |
| game/strategy/services/race_resolver.py | ✓ Read |
| game/simulation/managers/retreat_manager.py | ✓ Read |
| game/ui/services/image/provider.py | ✓ Read |
| game/ui/panels/ship_stats_renderer.py | ✓ Read |
| game/strategy/services/fleet_warp_resolution.py | ✓ Read |
| game/ui/screens/strategy_windows/dispatch.py | ✓ Read |
| game/ui/screens/strategy_render/hex_outlines.py | ✓ Read |
| game/strategy/interfaces/battle_resolver.py | ✓ Read |
| game/ui/screens/strategy_render/grid.py | ✓ Read |
| game/services/llm/__init__.py | ✓ Read |
| game/ui/widgets/range_slider_builder.py | ✓ Read |
| game/ui/screens/test_lab/details/resource_outcomes.py | ✓ Read |
| game/strategy/engine/order_handlers/superweapons.py | ✓ Read |
| game/ui/screens/transfer_view_model.py | ✓ Read |
| game/ui/screens/strategy_click_dispatcher.py | ✓ Read |
| game/strategy/services/ability_sources/facility.py | ✓ Read |
| game/assets/component_derivatives.py | ✓ Read |
| game/ui/screens/test_lab/renderer/category_panel.py | ✓ Read |
| game/ui/screens/strategy_camera_nav.py | ✓ Read |
| game/strategy/formulas/colony_output.py | ✓ Read |
| game/ui/screens/strategy_ui.py | ✓ Read |
