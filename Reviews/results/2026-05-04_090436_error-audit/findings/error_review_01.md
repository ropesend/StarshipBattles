# Error Handling Review: Shard 01

## Summary
- Files in Scope: 143
- Files Actually Read: 143
- Total Findings: 13
- Critical: 0 | Major: 0 | Minor: 13

## Broad Except Findings

#### MINOR: Missing justification comment on broad except in _time_phase
**ID:** ERR-01-001
**Location:** game/strategy/engine/turn_engine.py:266
**Code:** `except Exception as e:`
**Issue:** The `_time_phase` method catches broad `Exception` (docs-approved PROJ-251 pattern -- wraps in `EnginePhaseError`) but lacks the required `# Intentional broad catch: <reason>` justification comment on the same line.
**Suggestion:** Add: `except Exception as e:  # Intentional broad catch: sub-engines may raise anything; wrapped in EnginePhaseError for snapshot rollback (PROJ-251)`
**LOC affected:** 1

#### MINOR: Missing justification comment on broad except in snapshot capture
**ID:** ERR-01-002
**Location:** game/strategy/engine/turn_engine.py:522
**Code:** `except Exception as e:`
**Issue:** `TurnStateSnapshot.capture()` failure is caught broadly but logged. Missing `# Intentional broad catch:` comment. The code continues processing the turn without a snapshot -- defensible but undocumented.
**Suggestion:** Add: `except Exception as e:  # Intentional broad catch: snapshot capture can fail on deep serialization of complex objects; turn proceeds without rollback capability`
**LOC affected:** 1

#### MINOR: Missing justification comment on broad except in race_registry lookup
**ID:** ERR-01-003
**Location:** game/strategy/formulas/colony_output.py:85
**Code:** `except Exception as e:`
**Issue:** `race_registry.get_race(race_id)` failure is caught broadly and continues the loop. Missing `# Intentional broad catch:` comment. The error data is logged as debug (not warning/error), which is inconsistent with other registry-lookup error handling.
**Suggestion:** Add comment + consider logging at warning level: `except Exception as e:  # Intentional broad catch: race_registry lookup may fail on save-drift or missing config data; skips species for multiplier` and change `logger.debug` to `logger.warning`.
**LOC affected:** 3

#### MINOR: Missing justification comment on broad except in Ship instantiation
**ID:** ERR-01-004
**Location:** game/strategy/services/design_validator.py:76
**Code:** `except Exception as e:`
**Issue:** Ship.from_dict() can raise a range of exceptions (ValidationException, ComponentException, PersistenceException, KeyError, etc.). Missing `# Intentional broad catch:` comment. Behavior (logging + returning result with error) is correct but needs documentation.
**Suggestion:** Add: `except Exception as e:  # Intentional broad catch: Ship.from_dict can raise ValidationException, ComponentException, PersistenceException, KeyError; any failure means design is invalid`
**LOC affected:** 1

#### MINOR: Missing justification comment on broad except in simulation validator
**ID:** ERR-01-005
**Location:** game/strategy/services/design_validator.py:92
**Code:** `except Exception as e:`
**Issue:** The simulation-layer validator failure is caught broadly and logged as warning. Missing `# Intentional broad catch:` comment.
**Suggestion:** Add: `except Exception as e:  # Intentional broad catch: simulation validator may raise any exception on malformed ship data; logged and skipped`
**LOC affected:** 1

#### MINOR: Missing justification comment on broad except in design scan
**ID:** ERR-01-006
**Location:** game/ui/screens/battle_setup/controller.py:123
**Code:** `except Exception as e:`
**Issue:** `scan_designs()` catches broad `Exception` while loading design files. `load_json` already handles FileNotFoundError, JSONDecodeError, etc. internally and returns the default. The broad catch here indicates a code-path concern where non-JSON loading failures could occur. Missing `# Intentional broad catch:` comment.
**Suggestion:** Add: `except Exception as e:  # Intentional broad catch: design file may have structural issues beyond JSON parse errors; skip and continue scanning`
**LOC affected:** 1

## JSON Bypass Findings

#### MINOR: Direct json.load bypasses json_utils for file I/O
**ID:** ERR-01-007
**Location:** game/strategy/data/galaxy_warp_generator.py:391
**Code:** `data = json.load(f)`
**Issue:** Uses `json.load` directly on a file handle instead of the project-standard `game.core.json_utils.load_json()`. This bypasses the centralized error handling (FileNotFoundError, JSONDecodeError, PermissionError, OSError are all handled by `load_json` with a safe default fallback).
**Suggestion:** Replace with:
```python
from game.core.json_utils import load_json
data = load_json(str(path), default={})
_WARP_POINT_TYPES_CACHE = data.get('warp_point_types', {})
```
**LOC affected:** 3

## Resource Cleanup Findings

None found. All files in this shard use `with` for file handles, proper pygame resource lifecycle management, and no subprocess usage.

## Additional Issues Found

#### MINOR: Redundant exception type in image loading
**ID:** ERR-01-008
**Location:** game/ui/services/modifier_icon_service.py:81
**Code:** `except (pygame.error, Exception) as e:`
**Issue:** `pygame.error` is a subclass of `Exception`, so catching both is redundant. The `Exception` catch is broad without a comment. The image-loading operation could be narrowed to `(pygame.error, FileNotFoundError, OSError)`.
**Suggestion:** Replace with `except (pygame.error, OSError) as e:` since these are the expected failure modes for `pygame.image.load()`.
**LOC affected:** 1

#### MINOR: Broad except without comment in colony_output registry lookup
**ID:** ERR-01-009
**Location:** game/strategy/formulas/colony_output.py:85-89
**Code:** `except Exception as e:` followed by `logger.debug(...)`
**Issue:** The log level `debug` is inconsistent with other registry-lookup failure logging (typically `warning`). A failed species lookup during harvest multiplier calculation is a recoverable but noteworthy event.
**Suggestion:** Change `logger.debug` to `logger.warning` to align with convention.
**LOC affected:** 1

#### MINOR: Modified `load_json` result checked as falsy-truthy does not call `load_json`
**ID:** ERR-01-010
**Location:** game/ui/screens/battle_setup/controller.py:118-123
**Code:** `data = load_json(filepath, default=None)` then `if data and ...`
**Issue:** `load_json` is used (correct) but the subsequent `except Exception` catch is unnecessary if `load_json` is functioning correctly (it handles all file/JSON errors internally and returns the default). The broad except suggests awareness that `load_json` might fail in unexpected ways, but the correct fix is removing the try/except around the data inspection code.
**Suggestion:** The `try/except Exception` block should wrap only the `load_json` call for clarity, or be removed as `load_json` handles errors internally.
**LOC affected:** 5

#### MINOR: Inconsistent error handling severity in setup_data_io
**ID:** ERR-01-011
**Location:** game/ui/screens/setup_data_io.py:73 vs 228
**Issue:** In `scan_ship_designs()` (line 73), `load_json` errors are caught with specific exception types `(FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError)` and logged as `warning`. In `load_battle_setup()` (line 228), the same exception tuple is caught but logged as `error`. These are similar operations (loading ship design files) but have different severity -- should be consistent.
**Suggestion:** Standardize on `warning` for both (non-critical design scanning).
**LOC affected:** 1

#### MINOR: Direct open() in naming.py not using json_utils (YAML - not actionable)
**ID:** ERR-01-012
**Location:** game/strategy/data/naming.py:36
**Code:** `with open(file_path, "r", encoding="utf-8") as f:` + `yaml.safe_load(f)`
**Issue:** This is YAML loading, not JSON, so `json_utils` does not apply. No finding -- documented for completeness only. The specific exception catch on line 46 is properly narrowed to `(FileNotFoundError, OSError, yaml.YAMLError, KeyError, TypeError, UnicodeDecodeError)`.
**LOC affected:** 0 (documentation only)

#### MINOR: planet_modifier_effect_engine has no _validate_tick_inputs
**ID:** ERR-01-013
**Location:** game/strategy/engine/planet_modifier_effect_engine.py:33
**Issue:** Unlike other strategy sub-engines (harvesting, quality, environmental_hazard) which implement `_validate_tick_inputs()` per PROJ-251, `PlanetModifierEffectEngine.process_modifier_effects_tick()` does not validate its inputs before mutating planet state. Empires could have None colonies or malformed facility data.
**Suggestion:** Add a `_validate_tick_inputs()` method that checks colonies and facility existence before mutation, following the same pattern as `HarvestingEngine._validate_tick_inputs()`.
**LOC affected:** 0 (suggested addition)

## File Coverage Verification

| File | Status |
|------|--------|
| game/ui/screens/test_lab/details/chrome.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/ui/screens/setup_data_io.py | Read ✓ |
| game/strategy/engine/harvesting_engine.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/simulation/components/modifier_effects.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/ui/screens/builder_utils.py | Read ✓ |
| game/strategy/services/design_validator.py | Read ✓ |
| game/strategy/engine/water_engine.py | Read ✓ |
| game/simulation/entities/layer_data.py | Read ✓ |
| game/strategy/data/physics.py | Read ✓ |
| game/ui/screens/strategy_render/grid.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ |
| game/ui/services/modifier_icon_service.py | Read ✓ |
| game/strategy/engine/superweapon_order_processor.py | Read ✓ |
| game/ui/screens/battle_setup/renderer.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ |
| game/strategy/data/design_role_registry.py | Read ✓ |
| game/strategy/data/galaxy_entity_registry.py | Read ✓ |
| game/simulation/systems/battle_end_conditions.py | Read ✓ |
| game/simulation/components/abilities/planetary.py | Read ✓ |
| game/simulation/entities/ship_validator_helper.py | Read ✓ |
| game/strategy/generation/density/__init__.py | Read ✓ |
| game/simulation/components/abilities/harvester.py | Read ✓ |
| game/ui/__init__.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/strategy/services/strategic_ability_scanner.py | Read ✓ |
| game/ui/panels/race_summary_panel.py | Read ✓ |
| game/ui/filters/filter_state_manager.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/simulation/designs.py | Read ✓ |
| game/ui/screens/battle_ui.py | Read ✓ |
| game/ui/screens/test_lab/details/propulsion_outcomes.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/ui/panels/race_portrait_gallery.py | Read ✓ |
| game/strategy/engine/planet_modifier_effect_engine.py | Read ✓ |
| game/ui/screens/strategy_detail_fmt.py | Read ✓ |
| game/ui/screens/strategy_event_router.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/ui/services/image/null_provider.py | Read ✓ |
| game/ui/screens/race_validator.py | Read ✓ |
| game/strategy/facade/slices/empire_slice.py | Read ✓ |
| game/strategy/events/__init__.py | Read ✓ |
| game/ui/screens/star_list_window.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ |
| game/__init__.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ |
| game/ui/orchestration/__init__.py | Read ✓ |
| game/ui/screens/race_browser_dialog.py | Read ✓ |
| game/strategy/services/system_effects_collector.py | Read ✓ |
| game/ui/screens/strategy_render/planets.py | Read ✓ |
| game/ui/services/input_mapper.py | Read ✓ |
| game/strategy/data/naming.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ |
| game/simulation/components/abilities/stat_keys.py | Read ✓ |
| game/ui/screens/builder/weapons_renderer.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ |
| game/ui/screens/food_allocation_editor.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/projectile_manager.py | Read ✓ |
| game/strategy/facade/slices/event_slice.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/core/protocols/__init__.py | Read ✓ |
| game/strategy/systems/save_game_service.py | Read ✓ |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ |
| game/strategy/engine/command_handlers.py | Read ✓ |
| game/strategy/engine/handlers/registry_factory.py | Read ✓ |
| game/ui/screens/strategy_screen.py | Read ✓ |
| game/ui/screens/builder/weapons_panel.py | Read ✓ |
| game/strategy/data/fleet.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/ui/screens/build_queue_panel_factory.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/ui/panels/builder_widgets.py | Read ✓ |
| game/ui/screens/strategy_windows/ship_picker.py | Read ✓ |
| game/ui/screens/race_setup/renderer.py | Read ✓ |
| game/simulation/components/abilities/markers.py | Read ✓ |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | Read ✓ |
| game/strategy/data/pathfinding.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/simulation/components/abilities/defense.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/ui/screens/transfer_view_model.py | Read ✓ |
| game/ui/screens/strategy_windows/selection_prompts.py | Read ✓ |
| game/ui/services/battle_ui_service.py | Read ✓ |
| game/strategy/data/ship_instance_bridge.py | Read ✓ |
| game/ui/widgets/dropdown_helper.py | Read ✓ |
| game/ui/widgets/scrollable_json_panel.py | Read ✓ |
| game/context.py | Read ✓ |
| game/ui/screens/workshop_viewmodel.py | Read ✓ |
| game/strategy/data/galaxy_spatial_index.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/ui/screens/battle_results_screen.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/simulation/combat/weapon_firing_system.py | Read ✓ |
| game/ui/services/image/background.py | Read ✓ |
| game/strategy/engine/handlers/construction_queue.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/strategy/generation/density/primitives/geometric.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/strategy/data/classification_config.py | Read ✓ |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ |
| game/ui/screens/strategy_render/__init__.py | Read ✓ |
| game/ui/services/image/defaults.py | Read ✓ |
| game/strategy/engine/environmental_hazard_engine.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/simulation/systems/tick_phase.py | Read ✓ |
| game/ui/components/table/__init__.py | Read ✓ |
| game/strategy/data/design_metadata.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ |
| game/ui/screens/builder/modifier_logic.py | Read ✓ |
| game/ui/renderer/game_renderer.py | Read ✓ |
| game/ui/filters/filter_state.py | Read ✓ |
| game/ui/screens/test_lab/component_dropdown.py | Read ✓ |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| game/simulation/managers/__init__.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/strategy/facade/dto/build_queue_dto.py | Read ✓ |
| game/strategy/engine/planet_command_handlers.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/gravity_target_editor.py | Read ✓ |
| game/ui/screens/test_lab/renderer/_draw_helpers.py | Read ✓ |
| game/ui/panels/race_theme_gallery.py | Read ✓ |
| game/strategy/services/design_cost_calculator.py | Read ✓ |
| game/strategy/data/stars.py | Read ✓ |
| game/strategy/formulas/__init__.py | Read ✓ |
| game/ui/panels/race_flag_gallery.py | Read ✓ |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/strategy/interfaces/engines.py | Read ✓ |
| game/ui/screens/test_lab/theme.py | Read ✓ |
| game/ui/services/ship_io.py | Read ✓ |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ |
| game/ui/screens/strategy_screen_composition.py | Read ✓ |
| game/ui/screens/water_target_editor.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |

## Verification Coverage
- Critical findings: 0 (no criticals found in shard)
- Major findings: 0 (no majors found in shard)
- Minor findings: 13 total, 100% verified against actual source files
- Deterministic broad-except sites in shard: 18 total, all 18 verified
- Deterministic JSON bypass sites in shard: 3 total, all 3 verified (2 false positives)
