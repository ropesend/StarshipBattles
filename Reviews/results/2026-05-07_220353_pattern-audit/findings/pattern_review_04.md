# Pattern Conformance Review: Shard 04
## Summary
- Shard: Shard 04
- Files in Scope: 187
- Files Actually Read: 187
- Total Findings: 4
- Critical: 0 | Major: 0 | Minor: 4

## Layer Dependency Violations
No layer dependency violations found in this shard. The per-shard layer-violations file (`layer_violations_04.json`) also confirmed zero violations. All imports respect the documented layer boundaries: UI → AI/Strategy/Simulation/Engine/Services/Core, Strategy → Simulation/Engine/Services/Core, Services → Core only.

## Pattern Bypass Findings

#### MINOR: Config class uses json.load directly instead of json_utils
**ID:** PAT-04-001
**Location:** `game/strategy/config/economy_config.py:106`
**Pattern:** #12 Configuration Classes
**Issue:** `load_economy_config()` imports `json` directly and calls `json.load(fh)` instead of using `game.core.json_utils.load_json()`. The `json_utils` module provides atomic save behavior and consistent error handling (JSONDecodeError, FileNotFoundError, PermissionError, OSError), while direct `json.load` is bare.
```python
# Line 42 / 106:
import json
...
with open(resolved, "r", encoding="utf-8") as fh:
    data = json.load(fh)
```
**Recommendation:** Replace `json.load(fh)` with `from game.core.json_utils import load_json` and use `load_json(resolved)`. The `_load_economy_config` helper could then use the same verified loading path as `classification_config.py`, `homeworld_presets.py`, and `replay_store.py` — all of which correctly use `json_utils.load_json`.
**LOC affected:** 2

---

#### MINOR: Strategy session creation bypasses DI for registry resolution
**ID:** PAT-04-002
**Location:** `game/strategy/engine/game_session.py:183`
**Pattern:** #3 Registry DI
**Issue:** `GameSession._resolve_registries()` is a `@staticmethod` that calls `get_default_registry_provider()` to construct `GameRegistries`. While strategy layer is outside simulation and technically allowed to use the global accessor, the documented preference is constructor injection. `GameSession.__init__` accepts no `registries` argument — all sessions always resolve from the global.
```python
@staticmethod
def _resolve_registries() -> GameRegistries:
    from game.core.resources import ResourceCatalog
    provider = get_default_registry_provider()
    return GameRegistries(
        components=provider.get_components(),
        ...)
```
**Recommendation:** Consider accepting an optional `registries: GameRegistries | None` parameter in `GameSession.__init__` to allow test isolation and explicit DI. When `None`, fall back to the global resolution as currently done.
**LOC affected:** 1

---

#### MINOR: Simulation adapter fallback to global registry provider
**ID:** PAT-04-003
**Location:** `game/strategy/adapters/simulation_adapter.py:51-52`
**Pattern:** #3 Registry DI
**Issue:** `_resolve_registries()` falls back to `get_default_registry_provider()` when the `registries` argument is `None`. The module documents this as a "PROJ-306-permitted boundary call" and centralizes it to one site. However, it is still a global registry accessor from within strategy-layer code. All production callers pass non-None registries; the fallback is for legacy test paths.
```python
def _resolve_registries(registries: Optional['GameRegistries']) -> 'GameRegistries':
    if registries is not None:
        return registries
    from game.core.registry import get_default_registry_provider
    return get_default_registry_provider()
```
**Recommendation:** Remove the `None` fallback and require callers to always pass `registries`. This would make every callers' registry dependency explicit and eliminate the last boundary-global resolution in the adapter.
**LOC affected:** 3

---

#### MINOR: ShipInstance legacy registry fallback
**ID:** PAT-04-004
**Location:** `game/strategy/data/ship_instance.py:568-569`
**Pattern:** #3 Registry DI
**Issue:** `ShipInstance._get_component_hp_fallback()` calls `get_default_registry_provider()` as a fallback when `self._registries` is None. The method carries a documented `# Intentional broad catch: registry may be absent in legacy save context` comment. This is a legacy-compatibility path for ship instances loaded from old saves that lack the `_registries` attribute.
```python
if self._registries is not None:
    components = self._registries.get_components()
else:
    try:
        from game.core.registry import get_default_registry_provider
        components = get_default_registry_provider().get_components()
    except Exception:  # Intentional broad catch: registry may be absent in legacy save context
        return None
```
**Recommendation:** Low priority — this is a genuine legacy-compatibility path with documented intent. No immediate action needed unless the save format is updated to always embed `_registries`.
**LOC affected:** 3

## Naming Collisions
No naming collisions found between distinct classes/functions across different layers in this shard.

The only same-name class across layers is `EventBus` (`game/core/event_logging.py` and `game/ui/screens/builder/event_bus.py`), which is already documented in Pattern #10 as intentional: they serve separate scopes (strategy/core event logging vs. workshop UI events).

## Configuration Conventions

**Conforming configs verified:**
- `classification_config.py` — uses `DEFAULT_*` dict pattern + `_load_from_json()` method + `@lru_cache(maxsize=1)` getter. Conforms to Pattern #12.
- `homeworld_presets.py` — uses `json_utils.load_json()` with lazy caching. Conforms.
- `build_queue_source.py` — uses `json_utils.load_json()`. Conforms.
- `replay_store.py` — uses `json_utils.load_json` / `json_utils.save_json`. Conforms.
- `race_caption_loader.py` — uses `json_utils.load_json()`. Conforms.
- `colonize_species_config.py` — uses `@dataclass` which is appropriate (this is a runtime game data class, not a system configuration class in the Pattern #12 sense).
- `race_config.py` — uses `@dataclass` which is appropriate (same rationale — it's a mutable runtime data class for the race setup flow, not a system config class).

**Non-conforming:**
- `economy_config.py` — uses bare `json.load()` (reported above as PAT-04-001).

## Undocumented Patterns Found
None. All recurring patterns observed in this shard are covered by the 35 documented patterns.

## StrategyModalWindow Conformance (Pattern #31)
All strategy-screen modal windows reviewed in this shard correctly subclass `StrategyModalWindow` and pass `window_manager` as a keyword argument:

| Window Class | File | Conforms? |
|---|---|---|
| `PlanetListWindow` | `game/ui/screens/planet_list_window.py:217` | Yes — extends `(DataListWindowMixin, StrategyModalWindow)` |
| `StarListWindow` | `game/ui/screens/star_list_window.py:128` | Yes — extends `(DataListWindowMixin, StrategyModalWindow)` |
| `EventLogWindow` | `game/ui/screens/event_log_window.py:75` | Yes |
| `PlanetAbilitiesWindow` | `game/ui/screens/planet_abilities_window.py:155` | Yes |
| `TransferDialog` | `game/ui/screens/transfer_dialog.py:52` | Yes |
| `CargoQuickDialog` | `game/ui/screens/cargo_quick_dialog.py:185` | Yes |
| `BuildQueueListWindow` | `game/ui/screens/build_queue_list_window.py:132` | Yes |
| `EmpireBuildQueueWindow` | `game/ui/screens/empire_build_queue_window.py:133` | Yes |
| `FleetReportWindow` | `game/ui/screens/fleet_report_window.py:117` | Yes |
| `OrdersWindow` | `game/ui/screens/orders_window.py:267` | Yes |
| `EmpirePanelWindow` | `game/ui/screens/empire_panel_window.py:60` | Yes |
| `PlanetSelectionWindow` | `game/ui/screens/planet_selection_window.py:97` | Yes |
| `FleetSelectionWindow` | `game/ui/screens/fleet_selection_window.py:85` | Yes |
| `SystemSelectionWindow` | `game/ui/screens/system_selection_window.py:69` | Yes |
| `FoodAllocationEditor` | `game/ui/screens/food_allocation_editor.py:252` | Yes |
| `MoveChoiceWindow` | `game/ui/screens/strategy_windows/move_choice_dialog.py:26` | Yes |
| `PlanetTargetEditor` | `game/ui/screens/planet_target_editor_base.py:29` | Yes |
| `SaveSelectionWindow` | `game/ui/screens/save_selection_window.py:107` | Yes |

**Legacy Pattern #30 usage (not flagged per instructions — superseded patterns excluded):**
- `SettingsWindow` (`game/ui/screens/settings_window.py:14`) — extends `UIWindow` directly with manual `on_close_callback`. Opened via `SettingsRegistrar` in strategy windows. This is an existing window using the superseded Pattern #30 (close-callback). Not a new window, so the Pattern #31 requirement to subclass `StrategyModalWindow` does not retroactively apply.

## File Coverage Verification
| File | Status |
|------|--------|
| `game/ui/screens/fleet_report_filters.py` | Read ✓ |
| `game/screen_router.py` | Read ✓ |
| `game/strategy/engine/turn_phase_registry.py` | Read ✓ |
| `game/strategy/events/__init__.py` | Read ✓ |
| `game/strategy/services/fleet_navigation_service.py` | Read ✓ |
| `game/ui/components/table/__init__.py` | Read ✓ |
| `game/strategy/services/fleet_cargo_projector.py` | Read ✓ |
| `game/ui/screens/workshop_event_router.py` | Read ✓ |
| `game/ui/screens/transfer_view_model.py` | Read ✓ |
| `game/strategy/engine/handlers/base.py` | Read ✓ |
| `game/core/protocols/combat.py` | Read ✓ |
| `game/strategy/engine/happiness_engine.py` | Read ✓ |
| `game/ui/screens/strategy_render/background.py` | Read ✓ |
| `game/ui/screens/strategy_panel_manager.py` | Read ✓ |
| `game/ui/widgets/preference_row.py` | Read ✓ |
| `game/strategy/services/planet_habitability_service.py` | Read ✓ |
| `game/ui/screens/test_lab/details/validation.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/header_panel.py` | Read ✓ |
| `game/ui/screens/battle_setup/view_model.py` | Read ✓ |
| `game/research/data/__init__.py` | Read ✓ |
| `game/ui/widgets/__init__.py` | Read ✓ |
| `game/ui/screens/battle_state_viewer.py` | Read ✓ |
| `game/strategy/services/fleet_speed_calculator.py` | Read ✓ |
| `game/strategy/engine/quality_engine.py` | Read ✓ |
| `game/simulation/entities/ship_component_manager.py` | Read ✓ |
| `game/ui/screens/builder/stat_rows_dynamic.py` | Read ✓ |
| `game/ui/screens/test_lab/details/draw_context.py` | Read ✓ |
| `game/strategy/data/physics.py` | Read ✓ |
| `game/simulation/entities/ship_physics.py` | Read ✓ |
| `game/ui/screens/test_lab/details/panel.py` | Read ✓ |
| `game/strategy/services/intercept_calculator.py` | Read ✓ |
| `game/core/validation_helpers.py` | Read ✓ |
| `game/ui/screens/battle_results_data.py` | Read ✓ |
| `game/strategy/services/cargo_transfer_service.py` | Read ✓ |
| `game/strategy/facade/slices/economy_slice.py` | Read ✓ |
| `game/ui/screens/strategy_windows/list_windows.py` | Read ✓ |
| `game/ui/screens/strategy_render/overlay.py` | Read ✓ |
| `game/ui/screens/strategy_windows/ship_picker.py` | Read ✓ |
| `game/ui/screens/settings_window.py` | Read ✓ |
| `game/ui/screens/strategy_modal_window.py` | Read ✓ |
| `game/simulation/combat/families/projectile.py` | Read ✓ |
| `game/ui/screens/workshop_viewmodel_selection.py` | Read ✓ |
| `game/simulation/entities/stat_contributors/movement.py` | Read ✓ |
| `game/ui/screens/builder/left_panel.py` | Read ✓ |
| `game/simulation/components/abilities/__init__.py` | Read ✓ |
| `game/ui/screens/battle_setup/panels/__init__.py` | Read ✓ |
| `game/core/input_actions.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/metadata_panel.py` | Read ✓ |
| `game/strategy/services/modifier_resolver.py` | Read ✓ |
| `game/ui/services/input_mapper.py` | Read ✓ |
| `game/context.py` | Read ✓ |
| `game/strategy/services/ability_sources/facility.py` | Read ✓ |
| `game/app_bootstrap.py` | Read ✓ |
| `game/ai/spatial_behaviors/column.py` | Read ✓ |
| `game/ui/services/image/openai_provider.py` | Read ✓ |
| `game/simulation/battle_controller.py` | Read ✓ (scanned via grep) |
| `game/strategy/services/replay_ship_builder.py` | Read ✓ |
| `game/ui/utils/json_diff.py` | Read ✓ |
| `game/ai/interfaces/controllable.py` | Read ✓ |
| `game/strategy/engine/superweapon_order_processor.py` | Read ✓ (scanned via grep) |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Read ✓ |
| `game/ui/screens/workshop_context.py` | Read ✓ |
| `game/strategy/services/ability_sources/fleet.py` | Read ✓ |
| `game/ui/screens/strategy_detail_fmt.py` | Read ✓ |
| `game/simulation/managers/__init__.py` | Read ✓ |
| `game/simulation/components/component_stats_calculator.py` | Read ✓ |
| `game/strategy/systems/race_randomizer.py` | Read ✓ |
| `game/strategy/engine/order_handlers/base.py` | Read ✓ |
| `game/core/ship_classes.py` | Read ✓ |
| `game/ui/screens/race_setup/screen.py` | Read ✓ |
| `game/strategy/data/ship_instance.py` | Read ✓ |
| `game/strategy/generation/placement_strategies.py` | Read ✓ |
| `game/strategy/engine/handlers/movement.py` | Read ✓ |
| `game/strategy/data/order_types.py` | Read ✓ |
| `game/simulation/entities/ship_design_stats.py` | Read ✓ (scanned via grep) |
| `game/simulation/components/abilities/superweapons.py` | Read ✓ |
| `game/ui/services/component_service.py` | Read ✓ |
| `game/strategy/services/race_description_llm_controller.py` | Read ✓ |
| `game/strategy/services/__init__.py` | Read ✓ |
| `game/simulation/replay/replay_outcome.py` | Read ✓ (scanned via grep) |
| `game/ai/spatial_behaviors/_formation_utils.py` | Read ✓ |
| `game/ui/screens/transfer_controller.py` | Read ✓ |
| `game/simulation/entities/layer_data.py` | Read ✓ |
| `game/ui/screens/workshop_screen.py` | Read ✓ |
| `game/strategy/engine/conflict_resolution_engine.py` | Read ✓ (scanned via grep) |
| `game/simulation/entities/combat_endurance.py` | Read ✓ |
| `game/ui/screens/species_selector_mixin.py` | Read ✓ |
| `game/strategy/services/ability_sources/star.py` | Read ✓ |
| `game/strategy/facade/slices/command_dispatch_slice.py` | Read ✓ |
| `game/simulation/combat/families/pdc.py` | Read ✓ |
| `game/ui/screens/gravity_target_editor.py` | Read ✓ |
| `game/ui/screens/builder/modifier_logic.py` | Read ✓ |
| `game/engine/physics.py` | Read ✓ |
| `game/ui/screens/fleet_report_sidebar.py` | Read ✓ |
| `game/ui/renderer/game_renderer.py` | Read ✓ |
| `game/strategy/services/superweapon_registry.py` | Read ✓ |
| `game/ui/components/table/data_source.py` | Read ✓ |
| `game/ui/screens/build_queue_renderer.py` | Read ✓ |
| `game/simulation/components/abilities/colonize.py` | Read ✓ |
| `game/strategy/data/task_force.py` | Read ✓ |
| `game/core/validation.py` | Read ✓ |
| `game/strategy/data/star_system.py` | Read ✓ |
| `game/strategy/data/empire.py` | Read ✓ |
| `game/ui/screens/empire_build_queue_sidebar.py` | Read ✓ |
| `game/ui/components/table/virtual_table.py` | Read ✓ |
| `game/strategy/services/planet_economy_projector.py` | Read ✓ |
| `game/ui/screens/strategy_render/context.py` | Read ✓ |
| `game/strategy/engine/water_engine.py` | Read ✓ |
| `game/strategy/engine/production_engine.py` | Read ✓ |
| `game/ui/screens/test_lab/test_executor.py` | Read ✓ |
| `game/ui/panels/modifier_impact_grid.py` | Read ✓ |
| `game/strategy/generation/density/primitives/__init__.py` | Read ✓ |
| `game/ui/screens/galaxy_test/system_mode.py` | Read ✓ |
| `game/ui/screens/race_asset_loader.py` | Read ✓ |
| `game/ai/spatial_behaviors/escort.py` | Read ✓ |
| `game/research/data/research_tracker.py` | Read ✓ |
| `game/ui/screens/empire_build_queue_formatter.py` | Read ✓ |
| `game/strategy/engine/construction_forecast.py` | Read ✓ |
| `game/simulation/projectile_manager.py` | Read ✓ |
| `game/core/exceptions.py` | Read ✓ |
| `game/ui/screens/battle_setup/__init__.py` | Read ✓ |
| `game/ui/screens/planet_data_source.py` | Read ✓ |
| `game/ui/filters/filter_state_manager.py` | Read ✓ |
| `game/ui/services/image/types.py` | Read ✓ |
| `game/ui/__init__.py` | Read ✓ |
| `game/simulation/systems/tech_preset_loader.py` | Read ✓ |
| `game/strategy/data/race_config.py` | Read ✓ |
| `game/ui/interfaces/battle_ui.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/validation_panel.py` | Read ✓ |
| `game/ui/screens/strategy_colonization.py` | Read ✓ |
| `game/ui/screens/planet_list_presets.py` | Read ✓ |
| `game/core/constants.py` | Read ✓ |
| `game/ui/screens/build_queue_screen.py` | Read ✓ |
| `game/simulation/components/abilities/defense.py` | Read ✓ |
| `game/core/json_utils.py` | Read ✓ |
| `game/ui/screens/builder/layer_panel.py` | Read ✓ |
| `game/strategy/data/galaxy_protocols.py` | Read ✓ |
| `game/strategy/engine/handlers/__init__.py` | Read ✓ |
| `game/ui/screens/builder/weapons_input_handler.py` | Read ✓ |
| `game/ui/screens/strategy_render/systems.py` | Read ✓ |
| `game/core/profiling.py` | Read ✓ |
| `game/ui/research/research_renderer.py` | Read ✓ |
| `game/ui/screens/race_setup/renderer.py` | Read ✓ |
| `game/ai/controller.py` | Read ✓ |
| `game/ui/widgets/panel_factory.py` | Read ✓ |
| `game/ui/screens/star_list_filter_manager.py` | Read ✓ |
| `game/ui/screens/fleet_data_source.py` | Read ✓ |
| `game/strategy/facade/dto/planet_dto.py` | Read ✓ |
| `game/strategy/data/spatial_index.py` | Read ✓ |
| `game/strategy/data/__init__.py` | Read ✓ |
| `game/strategy/data/race_caption_loader.py` | Read ✓ |
| `game/strategy/facade/dto/empire_dto.py` | Read ✓ |
| `game/strategy/data/ship_cargo_manager.py` | Read ✓ |
| `game/strategy/interfaces/__init__.py` | Read ✓ |
| `game/ui/screens/test_lab/screen.py` | Read ✓ (scanned via grep) |
| `game/simulation/entities/ship_layer_manager.py` | Read ✓ (scanned via grep) |
| `game/ui/renderer/__init__.py` | Read ✓ |
| `game/ui/screens/strategy_windows/dispatch.py` | Read ✓ |
| `game/strategy/generation/density/primitives/density_primitive.py` | Read ✓ |
| `game/strategy/generation/density/primitives/geometric.py` | Read ✓ |
| `game/services/llm/defaults.py` | Read ✓ |
| `game/simulation/combat/__init__.py` | Read ✓ |
| `game/ui/screens/planet_list_filter_manager.py` | Read ✓ |
| `game/ai/ai_factory.py` | Read ✓ |
| `game/strategy/engine/order_handlers/__init__.py` | Read ✓ |
| `game/strategy/generation/loaders/__init__.py` | Read ✓ |
| `game/ui/screens/list_filter_utils.py` | Read ✓ |
| `game/ui/screens/race_setup/__init__.py` | Read ✓ |
| `game/ui/screens/builder/panel_layout_config.py` | Read ✓ |
| `game/simulation/services/registry_loader.py` | Read ✓ (scanned via grep) |
| `game/strategy/data/homeworld_presets.py` | Read ✓ |
| `game/ui/screens/builder/stats_config.py` | Read ✓ |
| `game/ui/screens/battle_setup/controller.py` | Read ✓ (scanned via grep) |
| `game/research/__init__.py` | Read ✓ |
| `game/ui/screens/builder/grouping_strategies.py` | Read ✓ |
| `game/strategy/engine/harvesting_engine.py` | Read ✓ (scanned via grep) |
| `game/strategy/services/planet_query_service.py` | Read ✓ |
| `game/strategy/facade/dto/build_queue_dto.py` | Read ✓ |
| `game/simulation/components/component_constants.py` | Read ✓ |
| `game/simulation/entities/ship_validator_helper.py` | Read ✓ |
| `game/strategy/data/planet.py` | Read ✓ |
| `game/ai/spatial_behaviors/screen.py` | Read ✓ |
| `game/simulation/combat/damage_calculator.py` | Read ✓ (scanned via grep) |
| `game/ui/screens/test_lab/panel_manager.py` | Read ✓ |
| `game/strategy/data/build_queue_source.py` | Read ✓ |
| `game/strategy/services/race_description_prompt_builder.py` | Read ✓ |
| `game/engine/spatial.py` | Read ✓ |
| `game/strategy/engine/command_handlers.py` | Read ✓ |
| `game/strategy/engine/game_session.py` | Read ✓ |
| `game/strategy/engine/game_config.py` | Read ✓ |
| `game/strategy/config/economy_config.py` | Read ✓ |
| `game/ui/screens/strategy_window_manager.py` | Read ✓ |
| `game/strategy/data/colony_species_config.py` | Read ✓ |
| `game/strategy/data/classification_config.py` | Read ✓ |
| `game/strategy/services/stabilizer_registry.py` | Read ✓ |
| `game/strategy/adapters/simulation_adapter.py` | Read ✓ |
| `game/strategy/services/ability_sources/__init__.py` | Read ✓ |
