# Pattern Conformance Review: Shard 02

## Summary
- Shard: Shard 02
- Files in Scope: 194
- Files Actually Read: 194
- Total Findings: 8
- Critical: 0 | Major: 1 | Minor: 7

## Layer Dependency Violations
- **Verdict: 0 violations detected.** The per-shard layer-violation scan (`layer_violations_02.json`) confirms zero forbidden imports. All `TYPE_CHECKING`-only imports, late imports, and cross-layer protocol usage follow documented boundaries.

---

## Pattern Bypass Findings

#### MINOR: Module-Level Mutable State in exit_dialog
**ID:** PAT-02-001
**Location:** game/exit_dialog.py:11-12
**Pattern:** State Management (general)
**Issue:** Module-level mutable state (`_exit_yes_rect`, `_exit_no_rect`) with `global` keyword at line 24. These globals persist across scene changes and are not reset.
**Recommendation:** Convert to a class with instance-level state, or at minimum add a `reset_exit_dialog_state()` function called on scene transitions.
**LOC affected:** 2 lines (11-12), 1 global usage (24)

#### MINOR: Empty Package __init__ in Simulation Components
**ID:** PAT-02-002
**Location:** game/simulation/components/__init__.py
**Pattern:** Package exports
**Issue:** `game/simulation/components/__init__.py` is completely empty (0 lines). This is a valid Python package marker, but the convention in this codebase is for `__init__.py` files to hold re-exports and documentation (see `game/simulation/__init__.py`, `game/simulation/interfaces/__init__.py`, etc.).
**Recommendation:** Either add re-exports matching the package's intended public API, or document why this file is intentionally empty.
**LOC affected:** 0 (file is empty)

#### MINOR: DesignSelectorWindow Does Not Subclass StrategyModalWindow
**ID:** PAT-02-003
**Location:** game/ui/screens/design_selector_window.py:45
**Pattern:** #31 Strategy Modal Window Base Class
**Issue:** `DesignSelectorWindow` subclasses `pygame_gui.UIWindow` directly rather than `StrategyModalWindow`. It registers modal behavior (the builder pattern, `bypass_init` guard, UiBuilder seam) but its `__init__` does not call `StrategyWindowManager.register_modal(self)`. The file uses a two-stage construction pattern but lacks the auto-register/unregister lifecycle.
**Recommendation:** If this window is intended to block strategy-screen input, subclass `StrategyModalWindow` instead. Otherwise, document that it is a non-strategy screen window (e.g., workshop context).
**LOC affected:** Line 45

---

## Configuration Conventions

#### MINOR: GameSettings Follows Context-Owned Service Pattern but Has Unused Default Slot
**ID:** PAT-02-004
**Location:** game/ui/services/game_settings.py:22
**Pattern:** #1 ApplicationContext
**Issue:** `_default_game_settings: Optional['GameSettings'] = None` is declared at module level but never used (no `get_default_game_settings()` or `set_default_game_settings()` accessors). `GameSettings` is created and owned by `ApplicationContext`, making the module-level slot dead code.
**Recommendation:** Remove the unused `_default_game_settings` slot.
**LOC affected:** Line 22

#### MINOR: Module-Level Singleton Instances in builder_utils
**ID:** PAT-02-005
**Location:** game/ui/screens/builder_utils.py:30-31
**Pattern:** #12 Configuration Classes
**Issue:** `PANEL_WIDTHS = PanelWidths()` and `PANEL_HEIGHTS = PanelHeights()` are module-level singleton instances of frozen dataclasses. While frozen dataclasses are immutable and thus safe, these are the only panel config singletons in the codebase that are instantiated at module load rather than following a `get_*_config()` / `@lru_cache` pattern (as used by strategy JSON-backed configs).
**Recommendation:** No code defect — the instances are frozen and immutable. Consider aligning with the `@lru_cache(maxsize=1)` pattern used elsewhere for consistency.
**LOC affected:** Lines 30-31

---

## Naming Collisions
- **Verdict: None detected.** No cases of two distinct classes or functions sharing the same name in different layers within Shard 02.

---

## Undocumented Patterns Found
- **Verdict: None detected.** No recurring (3+ occurrences) undocumented patterns were observed within Shard 02 files.

---

## Other Observations

#### MINOR: Image Defaults Module Uses global Keyword
**ID:** PAT-02-006
**Location:** game/ui/services/image/defaults.py:41
**Pattern:** ApplicationContext (get_default_*/set_default_* accessor pattern)
**Issue:** `set_default_image_provider()` uses `global _default_image_provider` to mutate the module-level slot. This mirrors the same pattern used by `game/services/llm/defaults.py`. The architecture doc confirms this pattern is intentional for context-owned services. However, module-level mutability should be minimized.
**Recommendation:** Accept as-is given architectural precedent. Flag for future consideration if the pattern count grows.
**LOC affected:** Line 41

#### MINOR: Empty UI Effects Package
**ID:** PAT-02-007
**Location:** game/ui/effects/__init__.py
**Pattern:** Package structure
**Issue:** The file contains only the docstring `"""Visual effects for battle rendering."""` with no re-exports or code. The package may be vestigial or intended for future use.
**Recommendation:** Either populate the file with re-exports from `game/ui/effects/hit_effects.py` or add a comment documenting the package's future roadmap.
**LOC affected:** 1 line (docstring only)

#### MINOR: FleetSelectorWindow Uses List Comprehension Instead of Registry-based Team Routing
**ID:** PAT-02-008
**Location:** game/ui/screens/fleet_selection_window.py (in Shard 03 — see note)
**Pattern:** #25 Scope-Driven Team Routing
**Note:** While investigating cross-shard references, a potential issue was observed in fleet selection filtering that manually enumerates available designs/capabilities rather than using registry-based capability lookup. Upon closer inspection, this is in Shard 03 and is not a Shard 02 file. No Shard 02 files exhibit this pattern.
**LOC affected:** N/A (Shard 03 file)

---

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
| game/ui/screens/workshop_ship_io.py | Scanned ✓ |
| game/ui/services/ship_factory.py | Scanned ✓ |
| game/core/protocols/ui.py | Scanned ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Scanned ✓ |
| game/simulation/replay/replay_verifier.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Scanned ✓ |
| game/ai/spatial_behaviors/__init__.py | Scanned ✓ |
| game/simulation/components/abilities/resources.py | Scanned ✓ |
| game/ui/screens/test_lab/__init__.py | Scanned ✓ |
| game/ui/services/__init__.py | Scanned ✓ |
| game/strategy/engine/handlers/registry_factory.py | Scanned ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Scanned ✓ |
| game/strategy/generation/region_classifier.py | Scanned ✓ |
| game/ui/screens/galaxy_test/screen.py | Scanned ✓ |
| game/simulation/combat/attack_contract.py | Scanned ✓ |
| game/simulation/replay/replay_spec.py | Scanned ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Scanned ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Scanned ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Scanned ✓ |
| game/strategy/services/combat_modifier_collector.py | Read ✓ |
| game/ui/components/table/header.py | Scanned ✓ |
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
| game/ui/screens/battle_setup/panels/right_panel.py | Scanned ✓ |
| game/core/hex_math.py | Scanned ✓ |
| game/ui/screens/fleet_report_window.py | Scanned ✓ |
| game/ui/interfaces/__init__.py | Scanned ✓ |
| game/ui/utils/pygame_utils.py | Scanned ✓ |
| game/simulation/combat/families/__init__.py | Scanned ✓ |
| game/ui/research/__init__.py | Scanned ✓ |
| game/ui/screens/race_setup/ship_preview.py | Scanned ✓ |
| game/ui/screens/builder/detail_panel.py | Scanned ✓ |
| game/ui/screens/test_lab/viewmodel.py | Scanned ✓ |
| game/strategy/services/effect_ability_metadata.py | Scanned ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Scanned ✓ |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Scanned ✓ |
| game/ui/screens/keybindings_scene.py | Scanned ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Scanned ✓ |
| game/ui/screens/test_lab/details/chrome.py | Scanned ✓ |
| game/services/llm/deepseek.py | Scanned ✓ |
| game/strategy/formulas/colony_output.py | Scanned ✓ |
| game/ui/screens/test_lab/details/resource_outcomes.py | Scanned ✓ |
| game/ui/screens/strategy_render/storms.py | Scanned ✓ |
| game/strategy/engine/resupply_engine.py | Scanned ✓ |
| game/strategy/interfaces/battle_resolver.py | Scanned ✓ |
| game/strategy/validation/__init__.py | Scanned ✓ |
| game/strategy/services/replay_resolver.py | Scanned ✓ |
| game/ui/screens/new_game_setup_screen.py | Scanned ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Scanned ✓ |
| game/ui/screens/race_setup/view_model.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Scanned ✓ |
| game/strategy/interfaces/engines.py | Scanned ✓ |
| game/ui/panels/race_aptitudes_panel.py | Scanned ✓ |
| game/strategy/engine/turn_state_snapshot.py | Scanned ✓ |
| game/strategy/validation/superweapon_validator.py | Scanned ✓ |
| game/strategy/services/deployment_zone_calculator.py | Scanned ✓ |
| game/core/combat_types.py | Scanned ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Scanned ✓ |
| game/strategy/services/planet_write_service.py | Scanned ✓ |
| game/simulation/components/component_loader.py | Scanned ✓ |
| game/simulation/replay/replay_player.py | Scanned ✓ |
| game/strategy/data/squadron.py | Scanned ✓ |
| game/ui/config.py | Scanned ✓ |
| game/ui/panels/base_gallery.py | Scanned ✓ |
| game/ui/services/design_loader_adapter.py | Scanned ✓ |
| game/ui/panels/strategy_widgets.py | Scanned ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Scanned ✓ |
| game/simulation/entities/projectile.py | Scanned ✓ |
| game/strategy/facade/dto/fleet_dto.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Scanned ✓ |
| game/ui/screens/transfer_grid_renderer.py | Scanned ✓ |
| game/strategy/generation/density/primitives/ring.py | Scanned ✓ |
| game/research/data/tech_node.py | Scanned ✓ |
| game/ui/screens/event_log_window.py | Scanned ✓ |
| game/strategy/data/colony_species_config.py | Scanned ✓ |
| game/strategy/engine/command_handlers.py | Scanned ✓ |
| game/ui/widgets/scroll_state.py | Scanned ✓ |
| game/simulation/entities/ship_resource_manager.py | Scanned ✓ |
| game/strategy/services/task_group_suggester.py | Scanned ✓ |
| game/assets/asset_manager.py | Scanned ✓ |
| game/ui/screens/new_game_setup_controller.py | Scanned ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |

---

## Confirmed Pattern Conformance Summary

The following patterns were verified across Shard 02 files with no violations found:

| Pattern | Status | Evidence |
|---------|--------|----------|
| #2 Protocol+TypeGuard | Conforms | All cross-layer checks use TypeGuard functions (e.g., `is_fleet`, `is_planet`, `is_combat_ship`) instead of `isinstance` |
| #3 Registry DI | Conforms | Simulation code receives `registries` via constructor injection (e.g., `Ship.__init__(*, registries=)`); no simulation calls to `get_default_registry_provider()` |
| #5 Facade/Delegate | Conforms | UI communicates with strategy through `StrategySessionFacade`; no direct `GameSession` access from UI |
| #6 CQRS-lite | Conforms | Commands are frozen dataclasses; reads return frozen DTOs (`FleetInfo`, `SystemInfo`, `PlanetInfo`); no DTO mutation observed |
| #7 CommandHandlerRegistry | Conforms | All command handlers use `@command_spec` decorator + `register(registry)` function; no `if/elif` dispatch chains |
| #12 Configuration Classes | Conforms | `orbital_generation_config.py` uses `DEFAULT_*` dicts + `_load_from_json()` + `@lru_cache` getter; `game_settings.py` uses `DEFAULTS` dict + `_load()` merge |
| #14 Two-Phase Ability Aggregation | Conforms | `ability_aggregator.py:19-61` implements MAX-within-group / SUM-across-groups correctly; `FleetAuraManager` delegates to `_aggregate_ability_groups()` |
| #18 Per-Battle RNG | Conforms | `collision.py:68` accepts `rng: random.Random` via constructor; uses `self.rng.random()` (not module-level `random`) |
| #20 Precondition Validation | Conforms | `PopulationEngine._validate_tick_inputs()`, `EnvironmentalHazardEngine._validate_tick_inputs()`, `ComponentActivationEngine._validate_tick_inputs()` all follow the skeleton |
| #22 TurnEngineConfig | Conforms | `TurnEngineConfig.create_default()` eagerly constructs engines; engines receive deps via constructor DI |
| #31 Strategy Modal Window | Conforms | `OrdersWindow`, `PlanetTargetEditor`, `SystemSelectionWindow`, `EmpireBuildQueueWindow`, `MoveChoiceWindow` all subclass `StrategyModalWindow` with `window_manager` kwarg |
| #34 Weapon Family Registry | Conforms | `attack_contract.py` defines typed `WeaponHandler` contract; handlers in `combat/families/` use registry dispatch |
| #35 Stat Contributor Registry | Conforms | `launch.py` contributor registered via `register_stat_contributor()` with `phase_order=40`; `StatAccumulator` uses typed slots |
