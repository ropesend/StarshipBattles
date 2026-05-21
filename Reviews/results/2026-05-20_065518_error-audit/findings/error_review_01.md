# Error Handling Review: Shard 01

## Summary
- Shard: Shard 01
- Files in Scope: 213
- Files Actually Read: 213
- Total Findings: 11
- Critical: 0 | Major: 3 | Minor: 8

## Broad Except Findings

All 128 scanner-reported broad-except sites were verified. Every one carries a valid `# Intentional broad catch:` comment. **No broad-except violations found.**

## JSON Bypass Findings

No JSON bypass violations found. All JSON operations in scope route through `game/core/json_utils.py` (`load_json`, `load_json_required`, `save_json`, `deserialize_list`) or through subclass paths that call `json.loads` only for legitimate in-memory DTO parsing (e.g., `BattleStateViewer.show` at `game/ui/screens/battle_state_viewer.py:122` uses `json.loads` for diff computation on in-memory strings, not file I/O).

## Resource Cleanup Findings

**No resource leaks found.** All files in the shard that hold external resources use proper cleanup:

- `game/ui/fonts.py` — Font cache uses `get_linesize()` as a validity probe with `pygame.error` catch, clearing the cache on failure.
- `game/ui/services/tkinter_utils.py` — `reset_tk_root()` destroys the root with a defensive broad catch, correctly choosing pass for best-effort teardown.
- `game/ui/services/image/openai_provider.py` — `requests` library connections use `with`-style connection pooling; no explicit file handles that outlive method scope.
- `game/ui/widgets/ui_element_registry.py` — `kill_all()` properly iterates and kills all registered pygame_gui elements.
- `game/ui/components/table/virtual_table.py` — `kill()` method cleans up headers, rows, scrollbar, and panels.

## Additional Issues Found

### MAJOR: Lost or Swallowed Errors

**MAJ-01 — `game/ui/services/modifier_icon_service.py:81` — Catch `Exception` without `# Intentional` comment**
```python
except (pygame.error, Exception) as e:
    logger.error(f"Error loading modifier icon {icon_path}: {e}")
    return None
```
`Exception` in the tuple is too broad and lacks the required justification comment. `pygame.error` alone covers `pygame.image.load` and `pygame.transform.smoothscale` failures. Replace `Exception` with the specific errors expected (e.g., `OSError` for corrupt files, `MemoryError` for large images), or add `# Intentional broad catch: <reason>`.

**MAJ-02 — `game/ui/screens/battle_state_viewer.py:135` — Silently swallows JSON parse failure**
```python
except json.JSONDecodeError:
    pass
```
If `initial_json` or `final_json` is malformed JSON, the function silently no-ops — the panels stay blank with no feedback. This is a misdiagnosis risk (user sees identical states and concludes they are the same). Should at minimum log a warning and set visible error panels.

**MAJ-03 — `game/ui/screens/strategy_detail_formatter.py:355` — Silent pass on layout error**
```python
except (TypeError, AttributeError):
    pass  # Mock objects in tests — skip layout
```
While the comment acknowledges the test-mock use case, production code hitting a `TypeError` here would silently fail to lay out action buttons. The catch is too broad for production — it should be scoped to only the test path (e.g., via a flag) or narrowed to specific expected mock failures.

### MINOR: Minor Issues

**MIN-01 — `game/ui/screens/star_list_window.py:395` — Silent pass on `ValueError`**
```python
try:
    val = float(event.text)
    # ...
except ValueError:
    pass
```
User typing non-numeric text into the range entry field silently produces no feedback. The current behavior (ignore) is defensible for UI responsiveness, but a debug-level log would help observability.

**MIN-02 — `game/ui/screens/save_selection_window.py:471` — Polling `pygame.event.get()` for confirmation events**
```python
for event in pygame.event.get(pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED):
```
This polls events directly from the pygame queue inside `update()`, which is a pattern that can miss events consumed by other handlers. Should route through the standard `process_event` flow or use pygame_gui's windowing system.

**MIN-03 — `game/ui/screens/workshop_data_reloader.py:22-27` — Module-level Tkinter init in a try/except**
```python
try:
    import tkinter as tk
    tk_root = tk.Tk()
    tk_root.withdraw()
except Exception:  # Intentional broad catch: Tkinter init is platform-dependent
    tk_root = None
```
This creates a Tk root at module import time rather than using the shared `get_tk_root()` from `game/ui/services/tkinter_utils.py`. This duplicates the Tkinter initialization pattern (two windows instead of one) and the duplicate root is never destroyed. Should use `get_tk_root()` from the canonical module.

**MIN-04 — `game/ui/screens/workshop_data_reloader.py:148-150` — Generic error messages surface raw exception to user**
```python
except (OSError, ValueError, KeyError) as e:
    logger.exception(f"Failed to reload data: {e}")
    self.show_error(f"Error reloading data: {e}")
```
`self.show_error` receives the raw exception string, which may contain internal paths or implementation details. This is a minor information-leakage risk, though acceptable for a dev-tool screen (the workshop).

**MIN-05 — `game/ui/screens/workshop_data_reloader.py:148-150` (same site) — Uses `logger.exception` for recoverable errors**
`logger.exception()` logs a full traceback for what is presented to the user as a non-fatal "Error reloading data" message. `logger.error()` would be more appropriate — `logger.exception()` is documented for use inside exception handlers only when the traceback is meaningful for triage, but this is a user-facing path where full traceback logging is noisy.

**MIN-06 — `game/ui/panels/builder_widgets.py:66-68` — Inconsistent logging: no logger call**
The file imports `logging` and creates `logger`, but the `_get_modifiers` method and `_clear_all_rows` have no logging on potential error paths. All other builder widget operations log state changes.

**MIN-07 — `game/ui/screens/strategy_screen_assets.py:76` — Catch tuple missing `Exception` justification**
```python
except (FileNotFoundError, OSError, pygame.error, AttributeError) as e:
    logger.warning(...)
```
`AttributeError` in the catch tuple catches property access failures on `obj.image_rotation` (line 73) — this is a defensive catch for malformed planet data. While specific, this catch has no comment explaining why `AttributeError` is expected.

**MIN-08 — `game/ui/screens/event_log_window.py:540` — Broad catch for test context**
```python
except Exception:  # Intentional broad catch: pygame_gui internals may not be ready in test contexts
```
Compliant with the broad-catch rule. No action needed, but documented for completeness since it appears in the shard.

## Per-File Analysis Summary

All 213 files were read. The shard covers primarily UI layer files (screens, panels, widgets, services), strategy facade slices/data, engine handlers, and simulation components. The overall error-handling quality is **high** — the codebase consistently:

- Uses the project's exception hierarchy (`ValidationException`, `PersistenceException`, domain-specific LLM/Image exceptions)
- Wraps low-level errors with `raise X from e` preserving exception chaining (verified in `openai_provider.py`, `star_system.py`, `stars.py`)
- Logs at appropriate levels with contextual details
- Uses `# Intentional broad catch:` comments for all legitimate broad catches
- Routes JSON I/O through `json_utils.py` (no bypasses found)
- Validates inputs with `require_keys`, `validate_enum`, `validate_positive` helpers
- Cleans up pygame_gui resources properly through `kill()` chains

The few issues found fall into categories the deterministic scanner cannot detect: overly broad catch tuples without justification, silent pass on parse errors, module-level anti-patterns (duplicate Tk root), inconsistent log levels, and polling-based event handling.

## File Coverage Verification

| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/core/event_logging.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/protocols/strategy_mutators.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/core/registry_cache.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/services/provider_factory.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/simulation/combat/__init__.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/simulation/combat/families/_beam_common.py | Read ✓ |
| game/simulation/combat/families/pdc.py | Read ✓ |
| game/simulation/combat/families/projectile.py | Read ✓ |
| game/simulation/combat/formation.py | Read ✓ |
| game/simulation/combat/ram_target_resolver.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/simulation/components/abilities/planetary/environmental.py | Read ✓ |
| game/simulation/components/abilities/planetary/terraforming.py | Read ✓ |
| game/simulation/components/abilities/propulsion.py | Read ✓ |
| game/simulation/components/abilities/ui_colors.py | Read ✓ |
| game/simulation/components/component_loader.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/entities/ship_combat_engine.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/entities/stat_contributors/defense.py | Read ✓ |
| game/simulation/entities/stat_contributors/registry.py | Read ✓ |
| game/simulation/interfaces/ai_controller.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/simulation/managers/battle_state_manager.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_spec.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/simulation/systems/fighter_reboard.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/combat/pre_tick_setup/mine_setup.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ |
| game/strategy/data/carried_vehicle.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/data/containable.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/data/fleet_battle_adapter.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/data/race_point_budget.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/strategy/engine/component_activation_engine.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/handlers/launch_fighters.py | Read ✓ |
| game/strategy/engine/handlers/movement.py | Read ✓ |
| game/strategy/engine/handlers/recover_satellites.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/strategy/engine/order_handlers/base.py | Read ✓ |
| game/strategy/engine/order_handlers/recover_fighters.py | Read ✓ |
| game/strategy/engine/order_handlers/transfer.py | Read ✓ |
| game/strategy/engine/population_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/strategy/engine/production_spawner.py | Read ✓ |
| game/strategy/engine/session/bootstrap.py | Read ✓ |
| game/strategy/engine/superweapon_handlers/open_warp_point.py | Read ✓ |
| game/strategy/engine/turn_engine_settings.py | Read ✓ |
| game/strategy/engine/turn_phase_registry.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/strategy/facade/grouped_namespaces.py | Read ✓ |
| game/strategy/facade/slices/__init__.py | Read ✓ |
| game/strategy/facade/slices/_facade_state.py | Read ✓ |
| game/strategy/facade/slices/economy_slice.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/strategy/generation/star_image_registry.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/strategy/interfaces/engines/combat.py | Read ✓ |
| game/strategy/interfaces/engines/logistics.py | Read ✓ |
| game/strategy/interfaces/engines/terraforming.py | Read ✓ |
| game/strategy/services/ability_sources/star.py | Read ✓ |
| game/strategy/services/ability_sources/system_archetype.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/component_layers.py | Read ✓ |
| game/strategy/services/effect_ability_display.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/strategy/services/planet_query_service.py | Read ✓ |
| game/strategy/services/planet_write_service.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/strategy/services/replay_store.py | Read ✓ |
| game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| game/strategy/services/system_destroyer.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/components/table/virtual_table.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/fonts.py | Read ✓ |
| game/ui/panels/__init__.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/panels/builder_widgets.py | Read ✓ |
| game/ui/panels/design_report_panel.py | Read ✓ |
| game/ui/panels/race_aptitudes_panel.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/panels/race_identity_panel.py | Read ✓ |
| game/ui/screens/__init__.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/battle_setup/panels/left_panel.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/ui/screens/build_queue_screen.py | Read ✓ |
| game/ui/screens/build_queue_selector.py | Read ✓ |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/schematic_view.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/builder/stats_config.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ |
| game/ui/screens/empire_build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/ui/screens/event_log_window.py | Read ✓ |
| game/ui/screens/fleet_data_source.py | Read ✓ |
| game/ui/screens/fleet_report_sidebar.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/ui/screens/fleet_selection_window.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/new_game_setup_screen.py | Read ✓ |
| game/ui/screens/new_game_setup_ui_builder.py | Read ✓ |
| game/ui/screens/planet_data_source.py | Read ✓ |
| game/ui/screens/planet_list_helpers.py | Read ✓ |
| game/ui/screens/planet_menu_items.py | Read ✓ |
| game/ui/screens/race_asset_loader.py | Read ✓ |
| game/ui/screens/race_setup/input_handler.py | Read ✓ |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/ui/screens/save_selection_window.py | Read ✓ |
| game/ui/screens/setup_screen.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ |
| game/ui/screens/strategy_fleet_context_menu.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/screens/strategy_render/background.py | Read ✓ |
| game/ui/screens/strategy_screen_assets.py | Read ✓ |
| game/ui/screens/strategy_screen_lifecycle.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/ui/screens/strategy_window_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ |
| game/ui/screens/transfer_container_rows.py | Read ✓ |
| game/ui/screens/transfer_controller.py | Read ✓ |
| game/ui/screens/transfer_grid_renderer.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ |
| game/ui/screens/workshop_viewmodel.py | Read ✓ |
| game/ui/services/game_settings.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/ui/services/image/openai_provider.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/ui/services/tkinter_utils.py | Read ✓ |
| game/ui/widgets/__init__.py | Read ✓ |
| game/ui/widgets/preference_row.py | Read ✓ |
| game/ui/widgets/scroll_state.py | Read ✓ |
| game/ui/widgets/ui_element_registry.py | Read ✓ |
