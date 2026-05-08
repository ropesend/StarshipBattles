# Deep Review: Shard 02
## Summary
- Shard: Shard 02
- Files in Scope: 188
- Files Actually Read: 188
- Total Findings: 24
- Critical: 0 | Product Decision: 3 | Major: 5 | Minor: 5 | Info: 11

## Dead Code Findings

#### PRODUCT_DECISION: Legacy test ship constructors in designs.py
**ID:** DEEP-02-001
**Location:** game/simulation/designs.py:11-68
**Issue:** `create_brick` and `create_interceptor` are hardcoded test-ship factory functions that use specific component IDs (`"railgun"`, `"standard_engine"`, `"thruster"`, `"fuel_tank"`, `"ordnance_tank"`, `"generator"`, `"armor_plate"`). These are wireframe helpers from early development.
**Estimated LOC:** 68
**Tests reference?** Yes — `tests/` imports designs.py for Combat Lab fixture setup
**Docs reference?** No
**Recommendation:** Either promote to test fixtures (move to tests/fixtures/) or update to use quickstart design data files (data/designs/qs_*.json). Do not delete without ensuring no test references remain.

#### PRODUCT_DECISION: `ShipPickerStub` placeholder class
**ID:** DEEP-02-002
**Location:** game/ui/screens/strategy_windows/ship_picker.py:16-43
**Issue:** `ShipPickerStub` is explicitly marked as a **stub** that auto-selects all ships. The docstring states "a real ship-picker dialog with individual selection is a future enhancement". It is wired in `strategy_window_manager.py` as `self._ship_picker = ShipPickerStub()`, so production code does reach it, but it provides no choice UI.
**Estimated LOC:** 43
**Tests reference?** Yes — tests for superweapon logic exercise the stub path
**Docs reference?** No
**Recommendation:** PROJ-198 placeholder. Implement the real ship-picker dialog or accept the stub as the permanent behavior (auto-select all). If accepting, remove the stub wrapper and inline the auto-select logic.

#### PRODUCT_DECISION: `allocate_crew_and_life_support` in command.py
**ID:** DEEP-02-003
**Location:** game/simulation/entities/stat_contributors/command.py:56-100
**Issue:** `allocate_crew_and_life_support` is defined in the command stat contributor but is called from `ShipStatsCalculator` methods, not from the registered contributor pipeline. It is used as a shared helper, not dead code, but sits in the stat contributor module rather than the calculator where it's called.
**Estimated LOC:** 44
**Tests reference?** Yes — tested via ShipStatsCalculator integration tests
**Docs reference?** No
**Recommendation:** This is correctly placed — the command module owns command/crew logic. The `contribute_multiplex_tracking` registered contributor co-locates the multiplex concern. Clarify via docstring that `allocate_crew_and_life_support` is a Phase-2 helper consumed by `ShipStatsCalculator`, not a Phase-3 registered contributor.

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:
| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| DEEP-02-001 | `create_brick` / `create_interceptor` in simulation/designs.py | 68 | Combat Lab fixtures | None | None | Move to test fixtures or retire |
| DEEP-02-002 | `ShipPickerStub` in strategy_windows/ship_picker.py | 43 | Superweapon tests | None | None | Implement PROJ-198 or inline auto-select |
| DEEP-02-003 | `allocate_crew_and_life_support` placement | 44 | ShipStatsCalculator tests | None | None | Clarify via docstring; correctly placed now |

## Internal Duplication Findings

#### MAJOR: Inline 5-element stat repetition in classification_config.py
**ID:** DEEP-02-004
**Location:** game/strategy/data/classification_config.py:128-154
**Issue:** `_use_defaults()` method has 26 self-assignment lines that are exact copies of `_load_from_json()` fallback values. The two methods differ only in whether they read `classification.get(...)` or `self.DEFAULT_*[...]`. A single parametrized initializer could collapse ~100 lines of duplicated assignments.
**Estimated LOC:** ~50 (after consolidation)
**Recommendation:** Replace `_use_defaults()` with a call to `_init_from_dict({})` and handle missing defaults in the loader. Reduces classification_config.py from 173 LOC to ~120 LOC.

#### MAJOR: BattleSetupController TF/SQ ship-cloning loops  
**ID:** DEEP-02-005
**Location:** game/ui/screens/battle_setup/controller.py:579 LOC
**Issue:** The `BattleSetupController` (579 LOC, over ceiling) has duplicated ship-cloning loops for TaskForce and Squadron manipulation. The file's own docstring acknowledges this: "Phase 7 will extract the duplicated TF/SQ ship-cloning loops into a `FleetHierarchyEditor`". ~120 LOC of near-identical iteration patterns.
**Estimated LOC:** ~120 (reduction via extraction)
**Recommendation:** Implement the planned `FleetHierarchyEditor` extraction to reduce controller LOC below 500.

#### MAJOR: stat_rows_dynamic.py has duplicated resource-iteration patterns
**ID:** DEEP-02-006
**Location:** game/ui/screens/builder/stat_rows_dynamic.py:515 LOC
**Issue:** Functions `_build_resource_rows()`, `_build_construction_rows()`, and `_build_strategic_rows()` all follow identical pattern: iterate `_discover_resources(ship)`, construct `StatDefinition` objects, and append. Each section differs only in which getters/formatters it wires. At 515 LOC this file exceeds the ceiling.
**Estimated LOC:** ~80 (reduction via shared row-builder abstraction)
**Recommendation:** Extract a shared `_build_resource_stat_rows(ship, row_specs)` function that takes a list of `(label, getter, formatter, validator)` tuples. Reduces ~80 lines of duplicated loop boilerplate.

#### MAJOR: stat_getters.py has repetitive resource getter pattern
**ID:** DEEP-02-007
**Location:** game/ui/screens/builder/stat_getters.py:111-184
**Issue:** `get_resource_storage`, `get_resource_current`, `get_resource_generation`, `get_resource_consumption`, `get_resource_endurance`, `get_resource_replenish`, `get_resource_max_usage` are 7 functions that follow nearly identical patterns (get resource registry, extract attribute, compute). Each is 2-30 LOC with the same fallback branches. Could be collapsed into a `_make_resource_getter(attr, compute_fn)` factory.
**Estimated LOC:** ~40 (reduction)
**Recommendation:** Extract a factory function that generates resource getters by attribute name and optional compute closure.

## Fragmentation Findings

#### MAJOR: session-state scattered across _cached_registries module-level globals
**ID:** DEEP-02-008
**Location:** game/ui/screens/strategy_build_queue_manager.py:40-44
**Issue:** `_cached_registries` module-level global is set on first access and never cleared. The same pattern appears in `setup_screen.py:48` (`_ship_factory`). Both are legacy lazy-DI patterns (pre-PROJ-211) now marked with "PROJ-211: Lazy registries initialization". These globals are held at module level and never invalidated across game sessions.
**Estimated LOC:** Minimal code change, but a state-mutation concern.
**Recommendation:** Replace module-level `_cached_registries` / `_ship_factory` globals with constructor-injected dependencies from the composition root. Already documented as "PROJ-211: Lazy registries initialization" — execute the planned cleanup.

## Quality / LOC Reduction Findings

#### INFO: ClassificationConfig in classification_config.py — verbose attribute assignments
**ID:** DEEP-02-009
**Location:** game/strategy/data/classification_config.py:76-154
**Issue:** Both `_load_from_json()` and `_use_defaults()` contain 26 lines each of explicit `self.field = value` assignments. These could be driven by a static `_FIELD_NAMES` list with dynamic `setattr`.
**Estimated LOC:** ~40 (reduction)
**Recommendation:** Define `_CLASSIFICATION_FIELDS: list[str]` covering all 26 config attributes and use `setattr(self, name, lookup_fn(name))` to eliminate both method bodies. From 173 LOC → ~130 LOC.

#### INFO: VirtualTable exceeds 500 LOC ceiling
**ID:** DEEP-02-010
**Location:** game/ui/components/table/virtual_table.py (607 LOC)
**Issue:** 607 LOC, 107 over ceiling. Contains event handling (~150 LOC), rendering (~200 LOC), tooltip helpers, and row management. The replay-tooltip helper (`_disabled_replay_tooltip`) could be extracted to its own module.
**Estimated LOC:** ~100 (extraction candidates: replay tooltip logic, scrollbar sync logic)
**Recommendation:** Extract replay-tooltip logic to `game/ui/screens/event_log_tooltip.py`. Extract scrollbar event handling to a `_scrollbar_handler.py` sub-module.

#### INFO: BuildQueueController exceeds 500 LOC ceiling
**ID:** DEEP-02-011
**Location:** game/ui/panels/build_queue_controller.py (707 LOC)
**Issue:** At 707 LOC, well over the ceiling. Contains category-filtering logic (~120 LOC), queue-add operations (~200 LOC), design-report refresh (~100 LOC), and multi-queue mode handling (~150 LOC).
**Estimated LOC:** Not directly reducible without sub-module split
**Recommendation:** Split into `build_queue_category_manager.py` (filtering + categories), `build_queue_add_controller.py` (add-to-queue operations), and `build_queue_report_controller.py` (design report updates).

#### INFO: PlanetListWindow exceeds 500 LOC ceiling
**ID:** DEEP-02-012
**Location:** game/ui/screens/planet_list_window.py (732 LOC)
**Issue:** At 732 LOC, 232 over ceiling. Despite sidebar extraction, the main window still carries heavy UI builder logic, event dispatch, report panel wiring, and preset management.
**Estimated LOC:** ~200 (candidates for extraction to dedicated modules)
**Recommendation:** Extract `PlanetListEventRouter` from the ~200 lines of event handling. Extract preset I/O callbacks to `planet_list_presets.py` (which already exists but only holds data, not the UI callback wiring).

#### INFO: TurnEngine exceeds 500 LOC ceiling
**ID:** DEEP-02-013
**Location:** game/strategy/engine/turn_engine.py (700 LOC)
**Issue:** At 700 LOC. The turn engine has been progressively decomposed (engines extracted, tick-phase registry added) but the orchestrator body remains large due to snapshot/rollback logic (~80 LOC), tick-loop driver (~200 LOC), and end-of-turn processing (~100 LOC).
**Estimated LOC:** ~150 (candidates for extraction)
**Recommendation:** Extract `_execute_tick_phases()` to a separate `turn_tick_runner.py` module. Extract snapshot/rollback logic to `turn_snapshot_handler.py` (already partially in `turn_state_snapshot.py`).

#### INFO: BattlePanel exceeds 500 LOC ceiling
**ID:** DEEP-02-014
**Location:** game/ui/panels/battle_panels.py (563 LOC)
**Issue:** At 563 LOC. Contains base `BattlePanel` class + `ShipDetailPanel` + `ShipListPanel`. The ship-list rendering logic (~200 LOC) dominates the file.
**Estimated LOC:** ~150 (by extracting ShipListPanel to its own module)
**Recommendation:** Extract `ShipListPanel` to `game/ui/panels/ship_list_panel.py` (already exist as separate class within this file).

#### INFO: KeybindingsScene exceeds 500 LOC ceiling
**ID:** DEEP-02-015
**Location:** game/ui/screens/keybindings_scene.py (582 LOC)
**Issue:** At 582 LOC. Contains sprite-based rendering (~150 LOC), event handling (~200 LOC), and rebinding state machine (~200 LOC).
**Estimated LOC:** ~100 (by extracting sprite generation to a renderer module)
**Recommendation:** Extract `KeybindingsRenderer` similar to the `strategy_render` subpackage pattern.

#### INFO: star_generator.py near 500 LOC ceiling
**ID:** DEEP-02-016
**Location:** game/strategy/generation/star_generator.py (471 LOC)
**Issue:** Near the ceiling at 471 LOC. Contains spectral math, generation logic, hex radius mapping, and image assignment.
**Estimated LOC:** Already extracted from stars.py (which was larger). Minor cleanups possible.
**Recommendation:** Monitor. The spectral helpers were already extracted to `game/core/spectrum_math.py`. If it grows, extract image assignment to a separate generator.

#### INFO: Storefront-specific LOAD_POPULATION/UNLOAD_POPULATION in transfer.py
**ID:** DEEP-02-017
**Location:** game/strategy/engine/order_handlers/transfer.py:241 LOC
**Issue:** The TransferHandler's `_dispatch_*` private methods decompose 5 implicit branches into 7 explicit ones. The decomposition is correct per the docstring, but the LOAD_POPULATION auto-resolve at fleet hex (BUG-70) and the fleet-to-fleet co-location skip (BUG-122) create subtle coupling between order generation and execution that could be centralized.
**Estimated LOC:** No savings — this is a quality observation
**Recommendation:** Consider adding a `TransferPreconditions` data class to hold the skip_location_check, auto_resolve, and cargo_type precomputed at order-creation time, removing the handler's need to detect these conditions.

#### INFO: Dyson sphere render has documented latent bug
**ID:** DEEP-02-018
**Location:** game/ui/screens/strategy_render/dyson_spheres.py:1-9
**Issue:** Module docstring documents a pre-existing latent bug: `screen_diameter` is undefined at line 90 and line 98, referenced only in the rare code path where a Dyson Sphere is owner-marked AND the empire has no `'colony'` asset. The bug is preserved from the original monolith and flagged for follow-up.
**Estimated LOC:** ~2 (bug fix)
**Recommendation:** File a ticket. Replace `screen_diameter` references with `2 * screen_radius` to resolve the NameError.

#### INFO: `has_superweapons` function potentially unused in production
**ID:** DEEP-02-019
**Location:** game/ui/screens/builder/stat_getters.py:315-321
**Issue:** `has_superweapons` is defined as a standalone function (not in the GETTERS registry) and takes a `ship` parameter. It may have been superseded by `get_superweapon_summary`. If no production code calls it directly, it can be inlined or removed.
**Estimated LOC:** 7
**Recommendation:** Grep for `has_superweapons` in `game/`; if only referenced in tests, inline into the test or mark as test-helper only.

#### INFO: `validate_positive` potentially unused import in galaxy.py
**ID:** DEEP-02-020
**Location:** game/strategy/data/galaxy.py:6
**Issue:** `validate_positive` is imported from `game.core.validation_helpers` but may not be used in galaxy.py. The import of `require_keys` IS used.
**Estimated LOC:** 1 (trivial removal)
**Recommendation:** Verify with grep; remove if unused.

#### INFO: WorkshopScreen exceeds 500 LOC ceiling
**ID:** DEEP-02-021
**Location:** game/ui/screens/workshop_screen.py (648 LOC)
**Issue:** At 648 LOC. Despite MVVM decomposition into WorkshopViewModel, WorkshopEventRouter, WorkshopLayerOps, etc., the screen class remains heavy with builder panel construction (~200 LOC), layout calculation (~100 LOC), and lifecycle management (~150 LOC).
**Estimated LOC:** ~150 (candidates for extraction)
**Recommendation:** Extract `WorkshopLayoutBuilder` for panel construction + layout and `WorkshopLifecycleManager` for save/load/close flows.

#### INFO: EventLogWindow exceeds 500 LOC ceiling
**ID:** DEEP-02-022
**Location:** game/ui/screens/event_log_window.py (539 LOC)
**Issue:** At 539 LOC. Contains tab filter bar (~80 LOC), replay-button logic (~100 LOC), sidebar wiring (~80 LOC), and VirtualTable construction (~100 LOC).
**Estimated LOC:** ~100 (candidates for extraction)
**Recommendation:** Extract `ReplayButtonHandler` and `EventLogTabBar` to smaller helper modules.

#### INFO: LayerPanel exceeds 500 LOC ceiling
**ID:** DEEP-02-023
**Location:** game/ui/screens/builder/layer_panel.py (536 LOC)
**Issue:** At 536 LOC. Contains grouping strategy selection, component list rendering, drag-drop interaction, and action dispatching.
**Estimated LOC:** ~80 (extract grouping strategy selection to its own panel)
**Recommendation:** Extract `LayerGroupingControls` to own sub-module within `builder/`.

#### INFO: trivial __init__.py with bare docstring
**ID:** DEEP-02-024
**Location:** game/ui/components/__init__.py:1
**Issue:** File is a single docstring line `"""Reusable UI components."""` with no imports or `__all__`. While the table sub-package has proper re-exports, this parent `__init__.py` is effectively empty.
**Estimated LOC:** Trivial — not actionable
**Recommendation:** Either add future re-exports here or leave as-is (convention allows empty `__init__`).

## File Coverage Verification
| File | Status |
|------|--------|
| game/ai/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/app.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/simulation/combat/combat_events.py | Read ✓ |
| game/simulation/combat/families/beam.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/simulation/components/component_constants.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/simulation/entities/stat_contributors/__init__.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_record.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/design_loader.py | Read ✓ |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/strategy/data/fleet_capability_calculator.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/strategy/data/group_policy_registry.py | Read ✓ |
| game/strategy/data/habitability_factors.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/turn_engine.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/strategy/facade/dto/fleet_hierarchy_dto.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/generation/planet_image_registry.py | Read ✓ |
| game/strategy/generation/star_generator.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/services/ability_sources/facility.py | Read ✓ |
| game/strategy/services/ability_sources/intrinsic_roll.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/services/fleet_write_service.py | Read ✓ |
| game/strategy/services/galaxy_pathfinding_service.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/strategy/validation/transfer_validator.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/panels/battle_panels.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/design_stats_panel.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ |
| game/ui/screens/battle_results_data.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/screens/builder/drop_target.py | Read ✓ |
| game/ui/screens/builder/interaction_controller.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/stat_getters.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/design_image_helper.py | Read ✓ |
| game/ui/screens/event_log_sidebar.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/ui/screens/fleet_selection_window.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/keybindings_scene.py | Read ✓ |
| game/ui/screens/menu_scene.py | Read ✓ |
| game/ui/screens/new_game_setup_controller.py | Read ✓ |
| game/ui/screens/new_game_setup_view_model.py | Read ✓ |
| game/ui/screens/orders_window.py | Read ✓ |
| game/ui/screens/planet_abilities_controller.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_presets.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/ui/screens/planet_list_window.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/race_setup/controller.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/star_data_source.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/ui/screens/strategy_render/context.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/ui/screens/strategy_render/storms.py | Read ✓ |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ |
| game/ui/screens/strategy_windows/fleet_report_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/list_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/ui/services/battle_ui_service.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/design_loader_adapter.py | Read ✓ |
| game/ui/services/image/__init__.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/utils/formatters.py | Read ✓ |
| game/ui/utils/portraits.py | Read ✓ |
| game/ui/widgets/column_toggle_section.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/ui/widgets/range_slider_builder.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
