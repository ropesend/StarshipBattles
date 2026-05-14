# Legacy Code Review: Shard 04

## Summary
- Shard: Shard 04
- Files in Scope: 185
- Files Actually Read: 185
- Total Findings: 5
- Critical: 0 | Major: 1 | Minor: 4 | Info: 0

---

## CRITICAL

None.

---

## MAJOR

### MAJ-001: `game/strategy/data/pathfinding.py` — Shim file with 14 deferred migration callers

- **File:** `game/strategy/data/pathfinding.py:1-102`
- **Category:** wrapper delegates / shim file
- **Description:** The module docstring explicitly states it contains "Pathfinding free-function shims" — each public function is a 1-line forwarder to `GalaxyPathfindingService` or `InterceptCalculator`. The shims remain as a back-compat surface for "~14 production caller sites that still import them directly." PROJ-372 Phase 5 closed without the caller-site migration sweep; the follow-up is tracked as **PROJ-376**.
- **Evidence:** Module docstring lines 1-18; functions `strip_start_hex`, `find_path_deep_space`, `find_hybrid_path`, `get_system_at_hex`, `_pathfinder_for`, `_intercept_for`.
- **Impact:** Every new pathfinding feature must be tested through both the service API and the shim interface. The `_intercept_for(galaxy)` shim constructs a fresh `InterceptCalculator` per call rather than using `galaxy._intercept`, which is explicitly called out as "intentional — ... would defeat the test-patch transparency the shims provide." This design tradeoff leaks implementation concerns upward.
- **Recommendation:** Execute the PROJ-376 migration sweep to point ~14 callers at `GalaxyPathfindingService` / `InterceptCalculator` directly, then delete the shim module.

---

## MINOR

### MIN-001: `game/app.py:124` — Legacy `running` flag

- **File:** `game/app.py:124-127`
- **Category:** deprecation marker (Phase 1)
- **Description:** `self.running = True` attribute on `Game` is marked `# Legacy` in source. RunLoop owns the canonical flag; the attribute is kept on `Game` for backward compatibility with `_handle_strategy_action("quit_game")` and tests that construct `Game` via `__new__` bypass.
- **Impact:** Minor confusion about which flag is authoritative (`Game.running` vs `RunLoop.running`). The `run()` method bridges them explicitly. Tests that bypass `__init__` via `Game.__new__` rely on this attribute.
- **Recommendation:** Document the full removal plan (part of PROJ-309 decomposition). Once all test bypasses are migrated, delete the attribute.

### MIN-002: `game/ui/screens/race_setup_screen.py` — Legacy import shim

- **File:** `game/ui/screens/race_setup_screen.py` (31 lines)
- **Category:** shim file
- **Description:** After PROJ-309 sub-phase 3.1 decomposed the original 1598-LOC `race_setup_screen.py` into the `race_setup/` package, this module preserves legacy import paths. Re-exports `RaceSetupScreen` (canonical home: `race_setup.screen`), `RaceBrowserDialog` (canonical: `race_browser_dialog`), and `RaceRandomizer` (canonical: `strategy.systems.race_randomizer`).
- **Callers:** `game/app.py` imports `RaceSetupScreen` from here; tests patch `RaceRandomizer` on this module path.
- **Recommendation:** Migrate callers to canonical paths per the module's own docstring guidance (lines 1-26), then delete.

### MIN-003: `game/ui/screens/test_lab/test_run_details.py` — Re-export shim

- **File:** `game/ui/screens/test_lab/test_run_details.py` (12 lines)
- **Category:** shim file
- **Description:** Thin re-export of `TestRunDetailsPanel` from `details/` subpackage. Kept for 2 call sites (`panel_manager.py`, `results_panel.py`) that use the historical import path. Documented as a "Re-export shim."
- **Recommendation:** Migrate the 2 caller imports to `game.ui.screens.test_lab.details`, then delete.

### MIN-004: Phase 1 wrapper-delegate false positives (confirmed NOT legacy)

- **Files reviewed:**
  - `game/simulation/entities/ship.py:568/581` — `to_dict` / `from_dict` delegate to `ShipSerializer`. Intentional Facade/Delegate pattern (Pattern #5), documented in class docstring.
  - `game/simulation/systems/battle_engine.py:449` — `_collect_new_attacks` delegates to `_attacks`. PROJ-382 Phase 5 extraction to meet 500 LOC ceiling. Documented as delegation.
  - `game/ui/screens/builder/weapons_viewmodel.py:392` — `calc_damage_at_range` lambda wraps `ab.get_damage`. Internal helper, not a public wrapper delegate.
- **Conclusion:** All 4 Phase 1 wrapper-delegate detections are confirmed false positives — they are documented, intentional delegation patterns, not legacy wrappers.

---

## Additional Legacy Indicators (Phase 1 did not catch)

1. **`game/strategy/data/pathfinding.py`** — Documented shim module (MAJ-001 above). Phase 1 `wrapper_delegates` detector did not flag these because the functions forward to different services rather than a single delegate, and use decorator-free plain-function signatures rather than a class method pattern the detector recognizes.

2. **`game/ui/screens/race_setup_screen.py`** — Legacy import shim (MIN-002 above). Phase 1 `init_reexports` detector scanned `__init__.py` files only, not `.py` modules acting as re-export shims.

3. **`game/ui/screens/test_lab/test_run_details.py`** — Re-export shim (MIN-003 above). Same root cause as above — the detector only scans `__init__.py` paths.

---

## Superseded Pattern #30 (Registrar Close-Callback)

- **Status:** No usages of Pattern #30 found in Shard 04.
- **Verification:** All modal windows in this shard (`FleetSelectionWindow`, `PlanetSelectionWindow`, `TransferDialog`, `TurnFailedDialog`, `PlanetAbilitiesWindow`, etc.) extend `StrategyModalWindow` (Pattern #31), which implements modal registration/unregistration. The legacy `Registrar Close-Callback` pattern (Pattern #30) has been fully migrated.

---

## Verification Coverage

- Critical findings verified: N/A (0 critical)
- Major findings sampled: 1/1 verified
  - MAJ-001 (`pathfinding.py`): Verified against source file. Docstring self-identifies as shims; functions are verified as 1-line forwarders. ~14 caller count from docstring.

---

## File Coverage Verification

| File | Status |
|------|--------|
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/app.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/core/ship_classes.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/research/data/research_tracker.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/simulation/battle_runner.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/simulation/combat/boundary.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/simulation/combat/families/_beam_common.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/simulation/combat/families/projectile.py | Read ✓ |
| game/simulation/combat/families/seeker.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/abilities/planetary/environmental.py | Read ✓ |
| game/simulation/components/abilities/planetary/shields.py | Read ✓ |
| game/simulation/components/abilities/planetary/stat_modifiers.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/simulation/components/modifiers.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/simulation/entities/ship.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/simulation/entities/ship_stats.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/simulation/validation/base.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/__init__.py | Read ✓ |
| game/strategy/data/build_context.py | Read ✓ |
| game/strategy/data/component_activation_state.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/strategy/data/galaxy_protocols.py | Read ✓ |
| game/strategy/data/habitability_factors.py | Read ✓ |
| game/strategy/data/naming.py | Read ✓ |
| game/strategy/data/orbital_generation_config.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/race_config.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/strategy/data/species_population.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/strategy/engine/action_execution_engine.py | Read ✓ |
| game/strategy/engine/conflict_modifier_collection.py | Read ✓ |
| game/strategy/engine/construction_forecast.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/engine/order_handlers/superweapons.py | Read ✓ |
| game/strategy/engine/order_processor.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/create_dyson_sphere.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/facade/dto/empire_dto.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/strategy/formulas/__init__.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/strategy/formulas/habitability.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/quickstart_builder.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/strategy/services/ship_instance_write_service.py | Read ✓ |
| game/strategy/services/system_destroyer.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/validation/colonize_validator.py | Read ✓ |
| game/ui/assets/ship_theme_manager.py | Read ✓ |
| game/ui/components/__init__.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/fonts.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/panels/battle_panels.py | Read ✓ |
| game/ui/panels/build_queue_portraits.py | Read ✓ |
| game/ui/panels/builder_widgets.py | Read ✓ |
| game/ui/panels/empire_treasury_panel.py | Read ✓ |
| game/ui/panels/modifier_impact_grid.py | Read ✓ |
| game/ui/panels/race_description_panel.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/screens/battle_screen.py | Read ✓ |
| game/ui/screens/battle_setup/constants.py | Read ✓ |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ |
| game/ui/screens/battle_setup/panels/left_panel.py | Read ✓ |
| game/ui/screens/battle_setup/renderer.py | Read ✓ |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ |
| game/ui/screens/battle_ui.py | Read ✓ |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ |
| game/ui/screens/builder/components.py | Read ✓ |
| game/ui/screens/builder/drop_target.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/layer_panel.py | Read ✓ |
| game/ui/screens/builder/modifier_logic.py | Read ✓ |
| game/ui/screens/builder/modifier_row.py | Read ✓ |
| game/ui/screens/builder/panel_layout_config.py | Read ✓ |
| game/ui/screens/builder/right_panel.py | Read ✓ |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/screens/builder/weapons_viewmodel.py | Read ✓ |
| game/ui/screens/empire_build_queue_formatter.py | Read ✓ |
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/ui/screens/fleet_report_view_model.py | Read ✓ |
| game/ui/screens/fleet_selection_window.py | Read ✓ |
| game/ui/screens/galaxy_test/screen.py | Read ✓ |
| game/ui/screens/list_data_source_base.py | Read ✓ |
| game/ui/screens/planet_abilities_window.py | Read ✓ |
| game/ui/screens/planet_list_presets.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/ui/screens/race_setup/delegate_factory.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/ui/screens/race_setup_screen.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/ui/screens/strategy_camera_nav.py | Read ✓ |
| game/ui/screens/strategy_fleet_context_menu.py | Read ✓ |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/ui/screens/strategy_screen_assets.py | Read ✓ |
| game/ui/screens/strategy_screen_order_editing.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/dispatch.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ |
| game/ui/screens/system_selection_window.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/details/resource_outcomes.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/panel_manager.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/validation_panel.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/ui/screens/test_lab/test_run_details.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/ui/screens/transfer_dialog.py | Read ✓ |
| game/ui/screens/turn_failed_dialog.py | Read ✓ |
| game/ui/screens/workshop_context.py | Read ✓ |
| game/ui/screens/workshop_viewmodel.py | Read ✓ |
| game/ui/services/__init__.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/services/image/background.py | Read ✓ |
| game/ui/services/ship_io_adapter.py | Read ✓ |
| game/ui/services/tkinter_utils.py | Read ✓ |
| game/ui/services/validation_service.py | Read ✓ |
| game/ui/services/vehicle_class_service.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
