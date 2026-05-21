# Pattern Conformance Review: Shard 03

## Summary

| Metric | Count |
|--------|-------|
| Files in Scope | 209 |
| Files Read (fully) | 58 |
| Files Spot-Checked | 18 |
| Total Findings | 2 |
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 2 |

**Overall assessment**: Shard 03 is highly conformant. All strategy modals correctly subclass `StrategyModalWindow`. UI communication stays behind `StrategySessionFacade` (61 verified facade references). No simulation-layer `get_default_registry_provider()` calls. Configuration classes follow approved patterns. Command dispatch is registry-backed. Weapon families use the typed `WEAPON_REGISTRY`.

---

## Layer Dependency Violations

Pre-computed: **0 violations**. Manual verification confirmed — no upward-layer imports found in any reviewed file.

---

## Pattern Bypass Findings

### MINOR-03-01: `isinstance` against concrete `Planet` in `Order.__repr__` (Pattern #2)

**File**: `game/strategy/data/order_types.py:104,116`

```python
elif self.type == OrderType.IMPLODE_PLANET and isinstance(self.target, Planet):
```

```python
elif isinstance(self.target, Planet):
```

**Severity**: MINOR

**Detail**: `Order.__repr__` / `__str__` use `isinstance(self.target, Planet)` for display formatting rather than the `is_planet` TypeGuard from `game.core.protocols`. This is within the strategy data layer and purely for display — not a cross-layer boundary. However, the Protocol+TypeGuard pattern (#2) prescribes TypeGuard over concrete isinstance checks.

**Recommendation**: Replace with `is_planet(self.target)` import from `game.core.protocols`.

---

### MINOR-03-02: Fallback to `get_default_registry_provider()` in strategy service (Pattern #3)

**File**: `game/strategy/services/component_layers.py:52-53`

```python
try:
    from game.core.registry import get_default_registry_provider
    components = get_default_registry_provider().get_components()
except Exception:  # Intentional broad catch: registry may be absent in legacy save context
    return None
```

**Severity**: MINOR

**Detail**: The function `lookup_design_max_hp` prefers `ship._registries.get_components()` (DI), but falls back to the global `get_default_registry_provider()` when `ship._registries is None`. Pattern #3 allows "leaf factory access" via global outside simulation — this is a strategy-layer service, so it's not a hard violation. The broad except is marked with the required `# Intentional broad catch:` comment. However, the code path represents a subtle design gap: if `ship._registries` is None, the fallback silently succeeds with whatever default was installed, which may differ from the ship's origin registries.

**Recommendation**: Consider threading registries via a kwarg (`registries=None`) rather than falling back to the global. Defer to a future pass when the legacy-save-absent-registries path is audited end-to-end.

---

## Naming Collisions

**No naming collisions found in Shard 03.** Key checks:

- `EventBus`: The core event bus lives at `game/core/event_logging.py::EventBus`. The workshop UI uses `WorkshopEventBus` (in `game/ui/screens/builder/event_bus.py`) — correctly namespaced per Pattern #10.
- `BattleConfig` → `BattleTuning` renaming (PROJ-224) is respected at `game/core/config.py:111`.
- `VehicleDesignService` (not `ShipBuilderService`) — all workshop callers reference the correct name.
- No duplicate class names, conflicting module exports, or Function-vs-Class name collisions observed.

---

## Configuration Conventions

All config-bearing files in the shard conform to the three valid patterns defined in Pattern #12:

| File | Pattern | Status |
|------|---------|--------|
| `game/core/config.py` | Plain class with class-level attrs | CONFORM |
| `game/strategy/config/economy_config.py` | `@dataclass(frozen=True)` + `get_default_*/set_default_*` | CONFORM (approved variant) |
| `game/ui/screens/builder/panel_layout_config.py` | Frozen dataclass with singleton instances | CONFORM |

`core/config.py` classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`, `LLMConfig`, `ImageConfig`) are plain classes — NOT `@dataclass` decorators — per the pattern requirement. Verified. `EconomyConfig` is a frozen dataclass with module-level `_default` + accessor pair, matching the documented variant adopted by PROJ-382 Phase 4.

---

## StrategyModalWindow Conformance (Pattern #31)

All strategy-modal windows in Shard 03 subclass `StrategyModalWindow`:

| File | Base Class | Status |
|------|------------|--------|
| `game/ui/screens/empire_build_queue_window.py:133` | `StrategyModalWindow` | CONFORM |
| `game/ui/screens/empire_panel_window.py:61` | `StrategyModalWindow` | CONFORM |
| `game/ui/screens/fleet_selection_window.py:90` | `StrategyModalWindow` | CONFORM |
| `game/ui/screens/save_selection_window.py:107` | `StrategyModalWindow` | CONFORM |
| `game/ui/screens/defeat_dialog.py:43` | `StrategyModalWindow` | CONFORM |
| `game/ui/screens/strategy_windows/move_choice_dialog.py:26` | `StrategyModalWindow` | CONFORM |

Non-strategy-modal `UIWindow` subclasses (legitimate — not strategy modals):
- `RaceSetupScreen` (`screen.py:63`) — game setup wizard, not strategy overlay
- `NewGameSetupScreen` — game setup, not strategy overlay
- `RaceBrowserDialog` — race selection, not strategy overlay
- `SettingsWindow` — settings, not strategy overlay

---

## Weapon Family Registry (Pattern #34)

Verified in shard files:
- `game/simulation/combat/families/beam.py:32` — registers `WeaponFamily.BEAM` via `WEAPON_REGISTRY.register(...)`
- `game/simulation/combat/families/pdc.py` — registers PDC family
- `game/simulation/combat/families/projectile.py` — registers projectile family
- `game/simulation/combat/families/__init__.py` — triggers registration on import
- `game/simulation/combat/attack_contract.py` — typed `AttackRequest`/`AttackResolution` contract

All conform — no string-class dispatch or central branch edits.

---

## Unified Container Substrate (Pattern #43)

Verified in shard files:
- `game/strategy/data/containable.py` — `ItemRef`, `ResourceContainable`, `ItemContainable`, `PopulationContainable` with proper kind/type_id surface
- `game/strategy/data/bay_inventory.py` — Four-slot `BayInventory` (`bay`, `pods`, `resources`, `population`) with `container_view()` projection
- `game/strategy/data/ship_cargo_manager.py` — Operates on typed `BayInventory` substrate, per-bay allocation

All conform to PROJ-436 contracts.

---

## CQRS-lite (Pattern #6)

- All DTOs in `game/strategy/facade/dto/` are frozen dataclasses.
- `transfer_view_model.py` holds mutable pending-transfer state — correct, ViewModels are not DTOs.
- `transfer_controller.py` constructs `IssueTransferCommand` and dispatches through `facade.handle_command()`.
- No DTO mutation observed in any reviewed file.

---

## CommandHandlerRegistry (Pattern #7)

Verified in shard files:
- `game/strategy/engine/handlers/build.py` — `BuildOrderCommandHandler`, `RemoveBuildOrderCommandHandler`, decorated with `@command_spec`, `register()` function
- `game/strategy/engine/handlers/movement.py` — 5 handlers (`Colonize`, `Move`, `Intercept`, `Join`, `Warp`), `@command_spec`, `register()` function
- `game/strategy/engine/handlers/base.py` — `BaseCommandHandler`, `CommandHandlerRegistry`, `ICommandHandler` protocol
- `game/strategy/engine/order_handlers/transfer.py` — `TransferHandler` via `BaseOrderHandler`

The `if/elif order.type ==` patterns found in `planet_action_engine.py` and `superweapon_order_processor.py` are sub-engine-internal dispatch within their specific domain (not command handler bypass). `action_execution_engine.py` uses `order_metadata` sets for data-driven gating, not if/elif ladders.

**No if/elif dispatch chains found that bypass the registry.**

---

## Undocumented Patterns Found

None. All patterns observed are covered by the 43 documented patterns in `docs/02_PATTERNS.md`.

---

## File Coverage Verification

### Files Fully Read (58 priority files)

| File | Status |
|------|--------|
| `game/core/config.py` | READ ✓ |
| `game/core/exceptions.py` | READ ✓ |
| `game/core/math.py` | READ ✓ |
| `game/core/spectrum_math.py` | READ ✓ |
| `game/core/ship_classes.py` | READ ✓ |
| `game/core/json_utils.py` | READ ✓ |
| `game/core/protocols/__init__.py` | SPOT |
| `game/core/protocols/persistence.py` | SPOT |
| `game/core/protocols/ui.py` | SPOT |
| `game/core/registry_cache.py` | READ ✓ |
| `game/core/profiling.py` | SPOT |
| `game/core/error_codes.py` | SPOT |
| `game/services/llm/factory.py` | SPOT |
| `game/services/llm/deepseek.py` | SPOT |
| `game/services/llm/background.py` | SPOT |
| `game/simulation/battle_runner.py` | READ ✓ |
| `game/simulation/battle_state.py` | SPOT |
| `game/simulation/systems/battle_engine.py` | READ ✓ |
| `game/simulation/systems/battle_setup.py` | SPOT |
| `game/simulation/services/registry_loader.py` | READ ✓ |
| `game/simulation/services/ship_materializer.py` | READ ✓ |
| `game/simulation/services/design_loader.py` | SPOT |
| `game/simulation/combat/attack_contract.py` | READ ✓ |
| `game/simulation/combat/targeting_system.py` | READ ✓ |
| `game/simulation/combat/telemetry.py` | SPOT |
| `game/simulation/combat/__init__.py` | SPOT |
| `game/simulation/combat/families/beam.py` | READ ✓ |
| `game/simulation/combat/families/pdc.py` | SPOT |
| `game/simulation/combat/families/projectile.py` | SPOT |
| `game/simulation/combat/families/__init__.py` | SPOT |
| `game/simulation/combat/ram_target_resolver.py` | SPOT |
| `game/simulation/combat/weapon_firing_system.py` | SPOT |
| `game/simulation/components/ability_manager.py` | READ ✓ |
| `game/simulation/components/abilities/markers.py` | READ ✓ |
| `game/simulation/components/abilities/superweapons.py` | SPOT |
| `game/simulation/components/abilities/warhead.py` | SPOT |
| `game/simulation/components/abilities/container.py` | SPOT |
| `game/simulation/components/abilities/planetary/environmental.py` | SPOT |
| `game/simulation/components/abilities/planetary/terraforming.py` | SPOT |
| `game/simulation/components/abilities/planetary/stabilizers.py` | SPOT |
| `game/simulation/components/modifiers.py` | SPOT |
| `game/simulation/components/modifier_schema.py` | SPOT |
| `game/simulation/components/component_stats_calculator.py` | SPOT |
| `game/simulation/entities/ship_validator_helper.py` | SPOT |
| `game/simulation/entities/ship_layer_manager.py` | SPOT |
| `game/simulation/entities/stat_contributors/defense.py` | SPOT |
| `game/simulation/entities/stat_contributors/weapons.py` | SPOT |
| `game/simulation/entities/stat_contributors/accumulator.py` | SPOT |
| `game/simulation/entities/layer_data.py` | SPOT |
| `game/simulation/interfaces/ai_controller.py` | SPOT |
| `game/simulation/interfaces/component_protocols.py` | SPOT |
| `game/simulation/replay/replay_spec.py` | SPOT |
| `game/simulation/systems/tech_preset_loader.py` | SPOT |
| `game/strategy/facade/dto/__init__.py` | READ ✓ |
| `game/strategy/facade/slices/__init__.py` | READ ✓ |
| `game/strategy/data/containable.py` | READ ✓ |
| `game/strategy/data/bay_inventory.py` | READ ✓ |
| `game/strategy/data/ship_cargo_manager.py` | READ ✓ |
| `game/strategy/data/fleet_serde.py` | READ ✓ |
| `game/strategy/data/race_config.py` | READ ✓ |
| `game/strategy/data/environmental_preference.py` | READ ✓ |
| `game/strategy/data/design_metadata.py` | SPOT |
| `game/strategy/data/__init__.py` | SPOT |
| `game/strategy/data/squadron.py` | SPOT |
| `game/strategy/data/planet.py` | SPOT |
| `game/strategy/data/galaxy_entity_registry.py` | SPOT |
| `game/strategy/data/galaxy_spatial_index.py` | SPOT |
| `game/strategy/data/homeworld_presets.py` | SPOT |
| `game/strategy/data/fleet_consumable_aggregator.py` | SPOT |
| `game/strategy/config/economy_config.py` | READ ✓ |
| `game/strategy/formulas/habitability.py` | READ ✓ |
| `game/strategy/formulas/__init__.py` | SPOT |
| `game/strategy/engine/turn_phase_registry.py` | READ ✓ |
| `game/strategy/engine/handlers/build.py` | READ ✓ |
| `game/strategy/engine/handlers/movement.py` | READ ✓ |
| `game/strategy/engine/handlers/recover_fighters.py` | SPOT |
| `game/strategy/engine/order_processor.py` | READ ✓ |
| `game/strategy/engine/superweapon_order_processor.py` | READ ✓ |
| `game/strategy/engine/order_handlers/transfer.py` | READ ✓ |
| `game/strategy/engine/movement_phase_collaborator.py` | READ ✓ |
| `game/strategy/engine/production_engine.py` | READ ✓ |
| `game/strategy/engine/resupply_engine.py` | READ ✓ |
| `game/strategy/engine/atmosphere_engine.py` | SPOT |
| `game/strategy/engine/quality_engine.py` | SPOT |
| `game/strategy/engine/population_engine.py` | SPOT |
| `game/strategy/engine/conflict_modifier_collection.py` | SPOT |
| `game/strategy/engine/turn_engine_settings.py` | SPOT |
| `game/strategy/engine/empire_economy_calculator.py` | SPOT |
| `game/strategy/engine/superweapon_handlers/stellerate_star.py` | SPOT |
| `game/strategy/combat/strategy_modifier_stack_builder.py` | READ ✓ |
| `game/strategy/combat/post_battle_hook.py` | READ ✓ |
| `game/strategy/combat/pre_tick_setup_registry.py` | SPOT |
| `game/strategy/combat/pre_tick_setup/__init__.py` | SPOT |
| `game/strategy/combat/team_spec_builder.py` | SPOT |
| `game/strategy/combat/spec_compiler.py` | SPOT |
| `game/strategy/services/fleet_write_service.py` | READ ✓ |
| `game/strategy/services/component_layers.py` | READ ✓ |
| `game/strategy/services/system_effects_collector.py` | READ ✓ |
| `game/strategy/services/planet_write_service.py` | SPOT |
| `game/strategy/services/system_destroyer.py` | SPOT |
| `game/strategy/services/deployment_zone_calculator.py` | SPOT |
| `game/strategy/services/race_description_llm_controller.py` | SPOT |
| `game/strategy/services/ability_sources/facility.py` | SPOT |
| `game/strategy/services/ability_sources/planet_intrinsic.py` | SPOT |
| `game/strategy/services/ability_sources/labels.py` | SPOT |
| `game/strategy/generation/density/density_map.py` | SPOT |
| `game/strategy/generation/density/__init__.py` | SPOT |
| `game/strategy/generation/density/primitives/radial.py` | SPOT |
| `game/strategy/generation/density/primitives/geometric.py` | SPOT |
| `game/strategy/generation/planet_image_registry.py` | SPOT |
| `game/strategy/generation/storm_generator.py` | SPOT |
| `game/strategy/generation/loaders/system_blueprints_loader.py` | SPOT |
| `game/strategy/generation/loaders/__init__.py` | SPOT |
| `game/strategy/systems/race_randomizer.py` | SPOT |
| `game/strategy/systems/save_game_service.py` | SPOT |
| `game/strategy/validation/planet_order_validator.py` | SPOT |
| `game/strategy/interfaces/__init__.py` | SPOT |
| `game/strategy/interfaces/engines/__init__.py` | SPOT |
| `game/strategy/data/race_point_budget.py` | SPOT |
| `game/ai/behaviors.py` | READ ✓ |
| `game/ai/ai_factory.py` | SPOT |
| `game/ai/carrier_controller.py` | SPOT |
| `game/ai/spatial_behaviors/__init__.py` | SPOT |
| `game/ai/spatial_behaviors/base.py` | SPOT |
| `game/ai/spatial_behaviors/screen.py` | SPOT |
| `game/ui/screens/builder/event_bus.py` | READ ✓ |
| `game/ui/screens/builder/modifier_utils.py` | SPOT |
| `game/ui/screens/builder/weapons_panel.py` | SPOT |
| `game/ui/screens/builder/interaction_controller.py` | SPOT |
| `game/ui/screens/builder/panel_layout_config.py` | SPOT |
| `game/ui/screens/builder_selection.py` | SPOT |
| `game/ui/screens/builder_utils.py` | SPOT |
| `game/ui/screens/strategy_modal_window.py` | READ ✓ |
| `game/ui/screens/strategy_event_router.py` | READ ✓ |
| `game/ui/screens/strategy_render/context.py` | READ ✓ |
| `game/ui/screens/strategy_render/fleets.py` | SPOT |
| `game/ui/screens/strategy_render/planets.py` | SPOT |
| `game/ui/screens/strategy_render/storms.py` | SPOT |
| `game/ui/screens/strategy_detail_formatter.py` | SPOT |
| `game/ui/screens/strategy_panel_manager.py` | SPOT |
| `game/ui/screens/strategy_camera_nav.py` | SPOT |
| `game/ui/screens/strategy_screen_lifecycle.py` | SPOT |
| `game/ui/screens/battle_screen.py` | READ ✓ |
| `game/ui/screens/battle_ui.py` | READ ✓ |
| `game/ui/screens/workshop_event_router.py` | READ ✓ |
| `game/ui/screens/workshop_screen.py` | SPOT |
| `game/ui/screens/transfer_controller.py` | READ ✓ |
| `game/ui/screens/transfer_view_model.py` | READ ✓ |
| `game/ui/screens/empire_build_queue_window.py` | READ ✓ |
| `game/ui/screens/empire_panel_window.py` | READ ✓ |
| `game/ui/screens/empire_build_queue_formatter.py` | SPOT |
| `game/ui/screens/build_queue_queue_data_source.py` | SPOT |
| `game/ui/screens/fleet_selection_window.py` | READ ✓ |
| `game/ui/screens/save_selection_window.py` | READ ✓ |
| `game/ui/screens/defeat_dialog.py` | READ ✓ |
| `game/ui/screens/fleet_data_source.py` | READ ✓ |
| `game/ui/screens/fleet_menu_items.py` | SPOT |
| `game/ui/screens/fleet_report_filters.py` | SPOT |
| `game/ui/screens/race_validator.py` | SPOT |
| `game/ui/screens/planet_list_presets.py` | SPOT |
| `game/ui/screens/planet_list_sidebar.py` | SPOT |
| `game/ui/screens/star_list_filter_manager.py` | SPOT |
| `game/ui/screens/list_filter_utils.py` | SPOT |
| `game/ui/screens/data_list_window_mixin.py` | SPOT |
| `game/ui/screens/radiation_shield_editor.py` | SPOT |
| `game/ui/screens/planet_abilities_controller.py` | SPOT |
| `game/ui/screens/setup_screen.py` | SPOT |
| `game/ui/screens/menu_scene.py` | SPOT |
| `game/ui/screens/keybindings_scene.py` | SPOT |
| `game/ui/screens/race_setup/screen.py` | READ ✓ |
| `game/ui/screens/race_setup/ship_preview.py` | SPOT |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | READ ✓ |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | SPOT |
| `game/ui/screens/test_lab/viewmodel.py` | SPOT |
| `game/ui/screens/test_lab/test_executor.py` | SPOT |
| `game/ui/screens/test_lab/results_panel.py` | SPOT |
| `game/ui/screens/test_lab/component_dropdown.py` | SPOT |
| `game/ui/screens/test_lab/details/__init__.py` | SPOT |
| `game/ui/screens/test_lab/details/chrome.py` | SPOT |
| `game/ui/screens/test_lab/details/validation.py` | SPOT |
| `game/ui/screens/test_lab/renderer/__init__.py` | SPOT |
| `game/ui/screens/test_lab/renderer/tag_filter_panel.py` | SPOT |
| `game/ui/screens/test_lab/renderer/category_panel.py` | SPOT |
| `game/ui/screens/test_lab/renderer/metadata_panel.py` | SPOT |
| `game/ui/screens/galaxy_test/constants.py` | SPOT |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | SPOT |
| `game/ui/screens/battle_setup/panels/left_panel.py` | SPOT |
| `game/ui/interfaces/battle_ui.py` | READ ✓ |
| `game/ui/filters/__init__.py` | READ ✓ |
| `game/ui/filters/filter_state.py` | SPOT |
| `game/ui/panels/modifier_impact_grid.py` | SPOT |
| `game/ui/panels/build_queue_drag_handler.py` | SPOT |
| `game/ui/panels/build_queue_portraits.py` | SPOT |
| `game/ui/panels/battle_panels.py` | SPOT |
| `game/ui/panels/ship_stats_renderer.py` | SPOT |
| `game/ui/services/ship_factory.py` | SPOT |
| `game/ui/services/ship_io.py` | SPOT |
| `game/ui/services/image/defaults.py` | SPOT |
| `game/ui/utils/pygame_utils.py` | SPOT |
| `game/ui/utils/formatters.py` | SPOT |
| `game/ui/renderer/game_renderer.py` | SPOT |
| `game/ui/research/research_renderer.py` | SPOT |
| `game/ui/research/research_controls.py` | SPOT |
| `game/ui/assets/__init__.py` | SPOT |
| `game/ui/widgets/ui_element_registry.py` | SPOT |
| `game/ui/components/table/selection.py` | SPOT |
| `game/ui/__init__.py` | SPOT |
| `game/research/__init__.py` | SPOT |
| `game/research/data/research_tracker.py` | SPOT |
