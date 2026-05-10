# Pattern Conformance Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 194
- Files Actually Read: 194
- Total Findings: 9
- Critical: 1 | Major: 3 | Minor: 5

## Layer Dependency Violations

**No per-shard layer violation file entries for Shard 02** — the pre-generated `layer_violations_02.json` has 0 entries.

After exhaustive file review, no unsuppressed layer dependency violations were found. All cross-layer imports observed in the shard are either:
- `TYPE_CHECKING` guarded (benign)
- Documented intentional bridges (e.g., `Ship.add_component()` importing `ModifierService`)
- UI → Strategy imports that conform to the Architecture table (UI may depend on all layers)

## Pattern Bypass Findings

#### CRITICAL: Registry DI Bypass — GameSession calls `get_default_registry_provider()` (Pattern #3)
**ID:** PAT-02-001
**Location:** `game/strategy/engine/game_session.py:60,183`
**Pattern:** #3 (Registry DI)
**Issue:** `GameSession._resolve_registries()` (line 176-190) calls `get_default_registry_provider()` at line 183 to resolve `GameRegistries`. Per Pattern #3, "Simulation code must not call `get_default_registry_provider()`" — and per `docs/01_ARCHITECTURE.md`, "Prefer constructor injection. Module-level defaults are for composition roots, decorators, convenience functions, and established leaf code." GameSession is a strategy-layer class (not a composition root) and should receive registries via constructor injection or through its TurnEngineConfig. The import at line 60 (`from game.core.registry import GameRegistries, get_default_registry_provider`) also brings in the global accessor.

The same method is called from `__init__` (line 89) and `from_dict()` (line ~480) — both pathways go through the same global resolution.

**Recommendation:** Accept `GameRegistries` as a constructor parameter or inject it through `GameConfig` / `TurnEngineConfig`. The composition root (`game/app_bootstrap.py`) should resolve registries and pass them down.
**LOC affected:** ~25

#### MAJOR: Strategy Modal Window Bypass — DesignSelectorWindow uses UIWindow (Pattern #31)
**ID:** PAT-02-002
**Location:** `game/ui/screens/design_selector_window.py:45`
**Pattern:** #31 (Strategy Modal Window Base Class)
**Issue:** `DesignSelectorWindow` extends `UIWindow` directly instead of subclassing `StrategyModalWindow`. All other strategy-screen modal windows in this shard (`OrdersWindow`, `FleetReportWindow`, `EventLogWindow`, `SystemSelectionWindow`, `EmpireBuildQueueWindow`) correctly use `StrategyModalWindow` which provides automatic modal registration/unregistration. `DesignSelectorWindow` does not register with `StrategyWindowManager`, so it cannot participate in modal-detection for click-blocking (`StrategyEventRouter.has_modal_open()`).

**Recommendation:** Change to `class DesignSelectorWindow(StrategyModalWindow):` and pass `window_manager` keyword. If it genuinely doesn't need modal behavior (used in non-strategy contexts), document this as an intentional exclusion.
**LOC affected:** ~30

#### MAJOR: Superweapon Hardcoded Type List (Convention Violation)
**ID:** PAT-02-003
**Location:** `game/ui/screens/builder/stat_getters.py:288-301`
**Pattern:** Convention — "No Hardcoded Type Lists"
**Issue:** `_SUPERWEAPON_ABILITIES` is a hardcoded list of 6 superweapon ability names (`DestroyPlanet`, `DestroyStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `SelfDestruct`). Per `docs/03_CONVENTIONS.md` §6.5: "Do not hardcode lists of ability names, component types, or class names to control behavior. Prefer generic data inspection, registry metadata, shared properties, or protocols." The superweapon registry at `game/strategy/services/superweapon_registry.py` already exists (`SUPERWEAPONS` tuple) and should be the single source of truth.

**Recommendation:** Replace `_SUPERWEAPON_ABILITIES` with iteration over `SUPERWEAPONS` from `game.strategy.services.superweapon_registry`. Similarly, `_SUPERWEAPON_LABELS` should use `SuperweaponSpec.display_name`.
**LOC affected:** ~15

#### MAJOR: Empty Package Init — `game/simulation/components/__init__.py` (Orphan Module)
**ID:** PAT-02-004
**Location:** `game/simulation/components/__init__.py`
**Pattern:** General architecture — empty `__init__.py` files that serve no purpose beyond Python package declaration should carry re-exports or be removed.
**Issue:** The file is 0 lines. Every other `__init__.py` in the simulation layer has meaningful exports. An empty init that's never imported as a package is dead weight. However, if this is a deliberate Python namespace package marker, the file is needed.
**Recommendation:** Either add canonical re-exports or document this as an intentional package marker.
**LOC affected:** 0

## Naming Collisions

#### MAJOR: `EventBus` Name Collision (Already Documented)
**ID:** PAT-02-005
**Locations:**
- `game/ui/screens/builder/event_bus.py:12` — `class EventBus`
- `game/core/event_logging.py:6` — `class EventBus`

**Issue:** Two distinct classes with the same name exist in different layers. Per Pattern #10, "Workshop `EventBus` lives at `game/ui/screens/builder/event_bus.py`; it is distinct from `game/core/event_logging.py::EventBus` used by simulation/strategy logging." This is **documented as intentional** and the two classes serve different purposes (UI builder pub-sub vs. structured event logging). The naming collision is acknowledged but justified by differing contracts.

**Status:** Documented intentional collision — no remediation needed.

## Configuration Conventions

#### MINOR: `race_library.py` uses `import json` instead of `json_utils`
**ID:** PAT-02-006
**Location:** `game/strategy/systems/race_library.py:14`
**Pattern:** #12 (Configuration Classes)
**Issue:** Uses standard `import json` with `json.dumps()` / `json.dump()` / `json.loads()` instead of the project's `game.core.json_utils` module which provides atomic save behavior and standardized error handling. Pattern #12 and `docs/01_ARCHITECTURE.md` document `json_utils.py` as: "JSON helpers, including atomic save behavior used by replay sidecars." Strategy data persistence should route through `json_utils` for consistency.

**Recommendation:** Replace `json.dump()`, `json.dumps()`, and `json.loads()` with `game.core.json_utils.save_json()` and `load_json()` equivalents.
**LOC affected:** ~10

#### MINOR: `detail_panel.py` uses bare `import json` in UI layer
**ID:** PAT-02-007
**Location:** `game/ui/screens/builder/detail_panel.py:11`
**Issue:** Uses standard `import json` with `json.dumps()` calls. UI layer is less constrained for JSON usage than strategy layer, but consistency with `json_utils` is still preferred.

**Recommendation:** Use `game.core.json_utils` for consistency with project conventions.
**LOC affected:** ~5

#### MINOR: Module-level mutable state via `global` keyword
**ID:** PAT-02-008
**Locations:**
- `game/exit_dialog.py:24` — `global _exit_yes_rect, _exit_no_rect`
- `game/ui/services/game_settings.py:85,93` — `global _default_game_settings`

**Issue:** Both files use the `global` keyword for module-level mutable state. Pattern #1 (ApplicationContext) states: "SingletonMeta, `game/core/singleton.py`, and `.instance()` service access are retired. Use context, constructor injection, or documented default accessors." The `exit_dialog.py` global rect state is particularly fragile (non-thread-safe, survives between dialog invocations). `game_settings.py` uses the documented `get_default_*` / `set_default_*` pattern which is the approved accessor convention (matching `LLMProvider`, `ImageProvider`, `AssetManager`).

**Recommendation:** `exit_dialog.py` should be converted to a class or at minimum clear globals on dialog close. `game_settings.py` is conformant with the `get_default_*` / `set_default_*` convention.
**LOC affected:** ~15

#### MINOR: Legacy Registry Fallback in ShipInstance
**ID:** PAT-02-009
**Location:** `game/strategy/data/ship_instance.py:567-569`
**Issue:** `ShipInstance._resolve_component_max_hp()` falls back to `get_default_registry_provider()` when `self._registries is None`. This is a documented legacy fallback with an `# Intentional broad catch` comment — a genuine safety net for legacy save contexts, not a systematic bypass. The primary path uses `self._registries` (DI).

**Recommendation:** Low priority. Remove when legacy save support is formally dropped.
**LOC affected:** ~4

## Undocumented Patterns Found

None observed in Shard 02. All recurring patterns in the reviewed files are covered by the 35 documented patterns in `docs/02_PATTERNS.md`.

## File Coverage Verification
| File | Status |
|------|--------|
| game/ui/utils/portraits.py | Read ✓ |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/builder/__init__.py | Read ✓ |
| game/ui/screens/strategy_render/planets.py | Read ✓ |
| game/ui/screens/builder/stat_getters.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/strategy/services/empire_write_service.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/ui/screens/strategy_screen_selection.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/strategy/engine/handlers/order_queue.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/simulation/entities/ship.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
| game/strategy/data/orbital_generation_config.py | Read ✓ |
| game/ui/screens/strategy_screen_order_editing.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/services/vehicle_class_service.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/ui/screens/builder/event_bus.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/strategy/data/planet_gen.py | Read ✓ |
| game/ui/screens/builder/drop_target.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/ui/screens/orders_window.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/ui/screens/builder/weapons_panel.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/ui/screens/empire_build_queue_window.py | Read ✓ |
| game/ui/widgets/range_slider_builder.py | Read ✓ |
| game/core/protocols/strategy_mutators.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/ui/screens/test_lab/ship_panels.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/ui/screens/race_setup/delegate_factory.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/screens/strategy_render/hex_outlines.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/simulation/entities/stat_contributors/launch.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/ui/screens/workshop_ship_io.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/ui/screens/galaxy_test/screen.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/simulation/combat/boundary.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/ui/screens/design_selector_window.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/ui/screens/system_selection_window.py | Read ✓ |
| game/strategy/events/event_types.py | Read ✓ |
| game/ui/screens/builder/components.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/strategy/services/replay_verification_coordinator.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/strategy/generation/density/density_map.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/strategy/engine/commands/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/superweapons.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/strategy/engine/order_handlers/self_destruct.py | Read ✓ |
| game/ui/widgets/dropdown_helper.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/ui/screens/battle_setup/panels/right_panel.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/utils/pygame_utils.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/screens/race_setup/ship_preview.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/strategy/services/effect_ability_metadata.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/ui/screens/test_lab/details/resource_outcomes.py | Read ✓ |
| game/ui/screens/strategy_render/storms.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/strategy/services/replay_resolver.py | Read ✓ |
| game/ui/screens/new_game_setup_screen.py | Read ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Read ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/strategy/interfaces/engines.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/simulation/components/component_loader.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/strategy/data/squadron.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/panels/strategy_widgets.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/strategy/facade/dto/fleet_dto.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/screens/transfer_grid_renderer.py | Read ✓ |
| game/strategy/generation/density/primitives/ring.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/engine/command_handlers.py | Read ✓ |
| game/ui/widgets/scroll_state.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/ui/screens/new_game_setup_controller.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
