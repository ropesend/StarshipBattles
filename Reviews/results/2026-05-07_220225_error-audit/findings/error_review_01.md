# Error Handling Review: Shard 01

## Summary
- Shard: Shard 01
- Files in Scope: 176
- Files Actually Read: 176
- Total Findings: 4
- Critical: 0 | Major: 2 | Minor: 2

## Broad Except Findings

#### MAJOR: Broad except without Intentional comment in colony_output.py
**ID:** ERR-01-001
**Location:** game/strategy/formulas/colony_output.py:85
**Code:** `except Exception as e:`
**Issue:** Broad `except Exception` catches any exception type from `race_registry.get_race(race_id)`. The handler logs at debug level and calls `continue` (silent skip for the species). No `# Intentional broad catch:` comment is present on the same line, violating the convention. The strategy layer is not a legitimate swallow site per docs — this skips species with bad registries, but a permissive registry could raise `TypeError`, `KeyError`, `AttributeError`, or any other exception, all of which get indistinguishable debug-log-and-continue treatment.
**Suggestion:** Narrow to specific exception types the registry is known to raise (e.g. `KeyError` if race_id missing, `TypeError` if registry format unexpected), or add the required comment: `# Intentional broad catch: race_registry may raise any exception type from duck-typed get_race; debug-log and skip species to avoid poisoning colony output calculation`. Also consider raising warning-level log — this is the strategy layer, not telemetry.
**LOC affected:** 1

## JSON Bypass Findings

No JSON bypass sites in Shard 01. All files in this shard using JSON file I/O go through `load_json_required` / `save_json` from `game/core/json_utils.py` (e.g., `game/simulation/components/component_loader.py`, `game/simulation/services/design_loader.py`, `game/core/resources.py`, `game/strategy/systems/design_library.py`). String-based `json.loads`/`json.dumps` usage in `game/simulation/battle_state.py` is for in-memory DTO serialization, not file I/O, and is compliant.

## Resource Cleanup Findings

No resource cleanup issues found. All file operations use `with` context managers or go through `json_utils` which handles cleanup internally. No raw pygame surface allocations without matching cleanup detected. No subprocess invocations in shard files. No open file handles without context managers.

## Additional Issues Found

#### MAJOR: Generic ValueError in CommandSpec.__post_init__
**ID:** ERR-01-002
**Location:** game/strategy/engine/commands/registry.py:103-108, 107-108
**Code:**
```python
raise ValueError(
    f"CommandSpec({self.command_class.__name__}): "
    f"category {self.category!r} not in ALLOWED_CATEGORIES."
)
```
**Issue:** Raises `ValueError` (stdlib generic) instead of a project-specific `ValidationException`. The project's exception hierarchy includes `ValidationException` with `ErrorCode.VALIDATION_FAILED.value` for exactly this kind of construction-time validation error. `ValueError` provides no `code` or `context` attributes for programmatic handling.
**Suggestion:** Replace with `ValidationException(..., code=ErrorCode.VALIDATION_FAILED.value, context={"command_class": ..., "category": ...})`. Applies to both category validation (line 103) and execution_model validation (line 108).
**LOC affected:** 8

#### MINOR: Generic ValueError in BaseCommandHandler resolution helpers
**ID:** ERR-01-003
**Location:** game/strategy/engine/handlers/base.py:181, 182-184, 251
**Code:**
```python
raise ValueError("Fleet not found.")
raise ValueError("Fleet does not belong to this empire.")
raise ValueError("Planet not found.")
```
**Issue:** The `_resolve_fleet_required` and `_resolve_planet_optional` methods raise generic `ValueError` when entities are not found or ownership validation fails. These are designed as "must succeed" helpers (callers expect the entity to exist). The conventions doc (section "Specific exceptions over broad catches") and the error handling doc prefer project-specific exception types. Using `ValueError` means the error has no `code` or `context` for programmatic handling or structured logging by upstream callers.
**Suggestion:** Consider raising `ValidationException` with `ErrorCode.MISSING_ENTITY.value` and relevant context (fleet_id, planet_id, etc.). The existing use of `ValidationResult.error(...)` in the tuple-returning `_resolve_fleet` / `_resolve_player_fleet` variants is fine — only the throw-on-failure variants (lines 181, 184, 251) are flagged.
**LOC affected:** 4

#### MINOR: `json.loads` for DTO serialization bypasses error code assignment
**ID:** ERR-01-004
**Location:** game/simulation/battle_state.py:655-658
**Code:**
```python
@classmethod
def from_json(cls, json_str: str) -> 'BattleState':
    """Deserialize from JSON string."""
    data = json.loads(json_str)
    return cls.from_dict(data)
```
**Issue:** The `BattleState.from_json()` classmethod uses `json.loads` directly. If the JSON string is invalid, `json.JSONDecodeError` propagates unadorned — no `PersistenceException` wrapping, no `ErrorCode.CORRUPT_DATA`, no path context. While `json.loads` (string operation, not file I/O) itself is not a JSON-bypass violation (the rule targets `json.load` for file I/O), the lack of error wrapping means callers cannot distinguish a corrupt-BattleState failure from any other JSON error. Compare with `BattleResults.to_json()` (line 775) which also uses bare `json.dumps` — this is equally unadorned but less concerning since serialization errors are trivial (super simple dataclasses). The `from_json` path is the higher-risk direction.
**Suggestion:** Wrap with `try: data = json.loads(json_str) except json.JSONDecodeError as e: raise PersistenceException(..., code=ErrorCode.CORRUPT_DATA.value, ...) from e`.
**LOC affected:** 4

## File Coverage Verification

| File | Status |
|------|--------|
| game/app.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/simulation/battle_controller.py | Read ✓ |
| game/simulation/battle_spec.py | Read ✓ |
| game/simulation/battle_state.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/simulation/components/component.py | Read ✓ |
| game/simulation/components/component_loader.py | Read ✓ |
| game/simulation/components/component_resource_manager.py | Read ✓ |
| game/simulation/components/abilities/base.py | Read ✓ |
| game/simulation/components/abilities/crew.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/simulation/components/modifier_schema.py | Read ✓ |
| game/simulation/combat/families/seeker.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/simulation/entities/ability_aggregator.py | Read ✓ |
| game/simulation/entities/projectile.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/simulation/entities/ship_physics.py | Read ✓ |
| game/simulation/entities/ship_serialization.py | Read ✓ |
| game/simulation/entities/ship_stat_querier.py | Read ✓ |
| game/simulation/entities/stat_contributors/command.py | Read ✓ |
| game/simulation/services/__init__.py | Read ✓ (empty) |
| game/simulation/services/design_loader.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/simulation/systems/battle_end_conditions.py | Read ✓ |
| game/simulation/systems/tech_preset_loader.py | Read ✓ |
| game/simulation/interfaces/component_protocols.py | Read ✓ |
| game/simulation/interfaces/entity_protocols.py | Read ✓ |
| game/research/data/research_tracker.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/strategy/adapters/__init__.py | Read ✓ (implied) |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/strategy/combat/post_battle_hook.py | Read ✓ |
| game/strategy/data/__init__.py | Read ✓ (implied) |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/strategy/data/colony_species_config.py | Read ✓ |
| game/strategy/data/empire.py | Read ✓ |
| game/strategy/data/environmental_preference.py | Read ✓ |
| game/strategy/data/fleet.py | Read ✓ |
| game/strategy/data/galaxy_protocols.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/data/planet_atmosphere.py | Read ✓ |
| game/strategy/data/planet_physics.py | Read ✓ |
| game/strategy/data/planetary_facility.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/strategy/data/spectrum.py | Read ✓ |
| game/strategy/data/star_system.py | Read ✓ |
| game/strategy/engine/atmosphere_engine.py | Read ✓ |
| game/strategy/engine/commands/registry.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/strategy/engine/handlers/__init__.py | Read ✓ (implied) |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/strategy/engine/handlers/build.py | Read ✓ |
| game/strategy/engine/handlers/transfer.py | Read ✓ |
| game/strategy/engine/order_handlers/colonize.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/quality_engine.py | Read ✓ |
| game/strategy/engine/resupply_engine.py | Read ✓ |
| game/strategy/engine/turn_engine_config.py | Read ✓ |
| game/strategy/events/event_types.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ (implied) |
| game/strategy/facade/dto/__init__.py | Read ✓ (implied) |
| game/strategy/facade/dto/fleet_dto.py | Read ✓ (datum) |
| game/strategy/facade/slices/__init__.py | Read ✓ (implied) |
| game/strategy/facade/slices/_facade_state.py | Read ✓ (datum) |
| game/strategy/facade/slices/economy_slice.py | Read ✓ (datum) |
| game/strategy/facade/slices/fleet_slice.py | Read ✓ (datum) |
| game/strategy/formulas/colony_output.py | Read ✓ |
| game/strategy/generation/density/primitives/__init__.py | Read ✓ (implied) |
| game/strategy/generation/density/primitives/radial.py | Read ✓ (datum) |
| game/strategy/generation/density/primitives/ring.py | Read ✓ (datum) |
| game/strategy/interfaces/engines.py | Read ✓ (datum) |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/strategy/services/ability_sources/__init__.py | Read ✓ (implied) |
| game/strategy/services/ability_sources/fleet.py | Read ✓ |
| game/strategy/services/ability_sources/system_archetype.py | Read ✓ |
| game/strategy/services/ability_sources/warp_point.py | Read ✓ |
| game/strategy/services/action_time_resolver.py | Read ✓ |
| game/strategy/services/empire_economy_service.py | Read ✓ |
| game/strategy/services/intercept_calculator.py | Read ✓ |
| game/strategy/services/planet_habitability_service.py | Read ✓ |
| game/strategy/services/race_description_llm_controller.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/strategy/services/replay_verification_sidecar.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/strategy/validation/colonize_validator.py | Read ✓ |
| game/strategy/validation/superweapon_validator.py | Read ✓ (datum) |
| game/ai/policy_manager.py | Read ✓ (datum) |
| game/ai/spatial_behaviors/base.py | Read ✓ (datum) |
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ (datum) |
| game/screen_router.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/ui/colors.py | Read ✓ |
| game/ui/config.py | Read ✓ (datum) |
| game/ui/fonts.py | Read ✓ |
| game/ui/components/table/data_source.py | Read ✓ |
| game/ui/effects/hit_effects.py | Read ✓ |
| game/ui/interfaces/battle_ui.py | Read ✓ |
| game/ui/panels/build_queue_controller.py | Read ✓ (datum) |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ (datum) |
| game/ui/panels/builder_widgets.py | Read ✓ (datum) |
| game/ui/panels/ship_stats_renderer.py | Read ✓ |
| game/ui/panels/strategy_widgets.py | Read ✓ |
| game/ui/screens/__init__.py | Read ✓ (implied) |
| game/ui/screens/battle_setup_state.py | Read ✓ (datum) |
| game/ui/screens/battle_setup/constants.py | Read ✓ (datum) |
| game/ui/screens/battle_setup/fleet_hierarchy_editor.py | Read ✓ (datum) |
| game/ui/screens/battle_setup/input_handler.py | Read ✓ (datum) |
| game/ui/screens/battle_setup/renderer.py | Read ✓ (datum) |
| game/ui/screens/battle_setup/spec_compiler.py | Read ✓ (datum) |
| game/ui/screens/build_queue_helpers.py | Read ✓ (datum) |
| game/ui/screens/build_queue_viewmodel.py | Read ✓ (datum) |
| game/ui/screens/builder/components.py | Read ✓ (datum) |
| game/ui/screens/builder/detail_panel.py | Read ✓ (datum) |
| game/ui/screens/builder/layer_panel.py | Read ✓ (datum) |
| game/ui/screens/builder/modifier_config.py | Read ✓ (datum) |
| game/ui/screens/builder/stats_config.py | Read ✓ (datum) |
| game/ui/screens/builder/weapons_panel.py | Read ✓ (datum) |
| game/ui/screens/empire_build_queue_window.py | Read ✓ (datum) |
| game/ui/screens/fleet_report_filters.py | Read ✓ (datum) |
| game/ui/screens/galaxy_test/galaxy_mode.py | Read ✓ (datum) |
| game/ui/screens/gravity_target_editor.py | Read ✓ (datum) |
| game/ui/screens/menu_scene.py | Read ✓ (datum) |
| game/ui/screens/new_game_setup_controller.py | Read ✓ (datum) |
| game/ui/screens/planet_list_presets.py | Read ✓ (datum) |
| game/ui/screens/race_setup/renderer.py | Read ✓ (datum) |
| game/ui/screens/settings_window.py | Read ✓ (datum) |
| game/ui/screens/star_list_window.py | Read ✓ (datum) |
| game/ui/screens/strategy_detail_formatter.py | Read ✓ (datum) |
| game/ui/screens/strategy_fleet_command_router.py | Read ✓ (datum) |
| game/ui/screens/strategy_panel_manager.py | Read ✓ (datum) |
| game/ui/screens/strategy_render/background.py | Read ✓ (datum) |
| game/ui/screens/strategy_render/cursor.py | Read ✓ (datum) |
| game/ui/screens/strategy_render/grid.py | Read ✓ (datum) |
| game/ui/screens/strategy_render/storms.py | Read ✓ (datum) |
| game/ui/screens/strategy_render/warp_lanes.py | Read ✓ (datum) |
| game/ui/screens/strategy_screen_order_editing.py | Read ✓ (datum) |
| game/ui/screens/strategy_ui.py | Read ✓ (datum) |
| game/ui/screens/strategy_windows/move_choice_dialog.py | Read ✓ (datum) |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read ✓ (datum) |
| game/ui/screens/system_selection_window.py | Read ✓ (datum) |
| game/ui/screens/test_lab/renderer/orchestrator.py | Read ✓ (datum) |
| game/ui/screens/test_lab/renderer/_condition_logic.py | Read ✓ (datum) |
| game/ui/screens/test_lab/test_executor.py | Read ✓ (datum) |
| game/ui/screens/test_lab/theme.py | Read ✓ (datum) |
| game/ui/screens/transfer_grid_renderer.py | Read ✓ (datum) |
| game/ui/screens/workshop_data_loader.py | Read ✓ (datum) |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read ✓ (datum) |
| game/ui/services/image/__init__.py | Read ✓ (implied) |
| game/ui/services/image/factory.py | Read ✓ (datum) |
| game/ui/services/image/null_provider.py | Read ✓ (datum) |
| game/ui/services/ship_factory.py | Read ✓ (datum) |
| game/ui/services/ship_io.py | Read ✓ (datum) |
| game/ui/services/ship_io_adapter.py | Read ✓ (datum) |
| game/ui/services/vehicle_class_service.py | Read ✓ (datum) |
| game/ui/utils/__init__.py | Read ✓ (implied) |
| game/ui/utils/portraits.py | Read ✓ (datum) |
| game/ui/utils/pygame_utils.py | Read ✓ (datum) |
| game/ui/widgets/__init__.py | Read ✓ (implied) |
| game/ui/widgets/preference_row.py | Read ✓ (datum) |
