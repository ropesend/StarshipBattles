# Error Handling Review: Shard 03

## Summary
- Shard: Shard 03
- Files in Scope: 225
- Files Actually Read: 225
- Total Findings: 15
- Critical: 0 | Major: 7 | Minor: 8

## Scope Validation
The deterministic scanner found 128 broad_except sites with valid `# Intentional broad catch:` comments — all properly commented. This report focuses on issues the scanner cannot detect: generic exceptions where domain-specific ones exist, lost exception chaining, missing error codes, inconsistent log levels, and silent swallows.

---

## MAJOR Findings

### MAJOR-001: `raise TypeError` instead of domain exception — `replay_serialization.py:115`
**File:** `game/simulation/replay/replay_serialization.py`
**Line:** 115
**Issue:** `boundary_to_dict()` raises generic `TypeError` for unknown BoundaryRegion subtypes. Per `docs/05_ERROR_HANDLING.md`, serialization errors at a persistence boundary should use `PersistenceException`.
```python
raise TypeError(
    f"boundary_to_dict: unknown BoundaryRegion subtype {type(boundary).__name__}"
)
```
**Recommendation:** Raise `PersistenceException(corrupt_data)` to match the module's `from_dict` parity.

### MAJOR-002: `raise ValueError` instead of `PersistenceException` — `replay_serialization.py:139`
**File:** `game/simulation/replay/replay_serialization.py`
**Line:** 139
**Issue:** `boundary_from_dict()` raises generic `ValueError` for unknown boundary types in loaded data. This is a persistence corruption mode and should raise `PersistenceException(CORRUPT_DATA)` per `from_dict` conventions.
```python
raise ValueError(f"boundary_from_dict: unknown type {kind!r}")
```
**Recommendation:** Replace with `raise PersistenceException(..., code=ErrorCode.CORRUPT_DATA.value, ...)`.

### MAJOR-003: Missing `code=` on `ValidationException` — `happiness_engine.py:96`
**File:** `game/strategy/engine/happiness_engine.py`
**Line:** 96
**Issue:** `_validate_tick_inputs()` raises `ValidationException` without a `code=` parameter, unlike every other engine's `_validate_tick_inputs()` in this shard (cf. `quality_engine.py:36`, `consumable_management_engine.py:75`, `resupply_engine.py:81`, `planet_action_engine.py:72`, `battle_setup.py:107`).
```python
raise ValidationException(
    f"Empire {empire.id}: colony list contains None entry",
    context={"empire_id": empire.id},
)
```
vs the correct pattern (e.g. `quality_engine.py:36`):
```python
raise ValidationException(
    f"Empire {empire.id}: colony list contains None entry",
    context={"empire_id": empire.id}
)
```
**Recommendation:** Add `code=ErrorCode.INVALID_STATE.value` or equivalent.

### MAJOR-004: `raise ValueError` in `planetary_facility.py:149` — generic instead of domain exception
**File:** `game/strategy/data/planetary_facility.py`
**Line:** 149
**Issue:** `_validate_resource_id()` raises generic `ValueError` for unknown resource IDs. This is a validation boundary and should raise `ValidationException` or `ResourceException`.
```python
raise ValueError(f"Unknown resource_id: {resource_id!r}")
```
**Recommendation:** Replace with `ValidationException(..., code=ErrorCode.RESOURCE_NOT_FOUND.value, ...)`.

### MAJOR-005: `raise ValueError` in `ship_stats_cache.py:41` — generic instead of domain exception
**File:** `game/strategy/data/ship_stats_cache.py`
**Line:** 41
**Issue:** `ShipStatsCache.calculate()` raises generic `ValueError` when registries are `None`. This is a missing-dependency condition and should use `ValidationException(MISSING_DEPENDENCY)`.
```python
raise ValueError(
    "ShipInstance requires registries for stats calculation. ..."
)
```
**Recommendation:** Replace with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`.

### MAJOR-006: `raise ValueError` in `fleet_capability_calculator.py:70,138` — generic instead of domain exception
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Lines:** 70, 138
**Issue:** Two methods (`ship_has_spaceyard` and `_get_registry`) raise generic `ValueError` when no component registry is available. This is a missing-dependency error — `ValidationException(MISSING_DEPENDENCY)` is the correct class.
```python
# Line 70
raise ValueError(
    "FleetCapabilityCalculator.ship_has_spaceyard requires a component registry..."
)
# Line 138
raise ValueError(
    "FleetCapabilityCalculator requires a component registry..."
)
```
**Recommendation:** Replace both with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`.

### MAJOR-007: `raise RuntimeError` in `battle_runner.py:294,314` — generic instead of domain exception
**File:** `game/simulation/battle_runner.py`
**Lines:** 294, 314
**Issue:** Both `start_engine_from_spec()` and `run_battle()` raise generic `RuntimeError` when neither `ship_builder` nor `registry_provider` is supplied. This is a configuration/invocation error and Per `docs/05_ERROR_HANDLING.md`, simulation-code should use domain exceptions.
```python
raise RuntimeError(
    "BattleController.start_from_spec requires either an explicit "
    "`ship_builder` callable or a `registry_provider`..."
)
```
**Recommendation:** Replace with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`. This is a hard pre-condition violation, not an unexpected runtime state.

---

## MINOR Findings

### MINOR-001: Silently swallowed `KeyError` in `battle_outcome_from_dict` — `replay_serialization.py:558-561`
**File:** `game/simulation/replay/replay_serialization.py`
**Lines:** 555-561
**Issue:** `battle_outcome_from_dict()` and `battle_spec_from_dict()` catch `KeyError` when looking up `TelemetryLevel[telemetry_name]` and fall back to using the raw string as an opaque value. This silently accepts unknown telemetry level names without any log message.
```python
try:
    telemetry_level: Any = TelemetryLevel[telemetry_name]
except KeyError:
    telemetry_level = telemetry_name  # opaque fallback
```
**Recommendation:** Log a warning when the telemetry level name is unrecognized, or raise `PersistenceException(CORRUPT_DATA)` for strict validation.

### MINOR-002: Inconsistent `logger.error` + silent return — `asset_manager.py:59-60`
**File:** `game/assets/asset_manager.py`
**Lines:** 58-60
**Issue:** `load_manifest()` logs at `error` level when the manifest file is not found, but returns silently without raising. The method has no return value and callers cannot distinguish "loaded successfully" from "file missing." If the manifest is truly optional, `logger.warning` is more appropriate. If it's critical, it should raise.
```python
if not os.path.exists(self.manifest_path):
    logger.error(f"Asset Manifest not found: {self.manifest_path}")
    return
```
**Recommendation:** Either downgrade to `logger.warning` (if optional) or raise `MissingResourceException` (if critical).

### MINOR-003: `fleet_write_service.py` uses bare `NotImplementedError` — `fleet_write_service.py:57,65`
**File:** `game/strategy/services/fleet_write_service.py`
**Lines:** 57, 65
**Issue:** `set_location()` and `set_path()` raise bare `NotImplementedError` when no `navigation_service` is configured. This is a configuration error, not an abstract method stub. Per the error handling guidelines, it should use a domain exception.
```python
raise NotImplementedError(
    "FleetWriteService requires FleetNavigationService for ..."
)
```
**Recommendation:** Replace with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)` or `StateException(NOT_INITIALIZED)`.

### MINOR-004: `asset_manager.py:153` catch tuple should include `OSError` — matches `load_planet_image` pattern
**File:** `game/assets/asset_manager.py`
**Line:** 153
**Issue:** `load_star_image()` catches `(FileNotFoundError, pygame.error, ValueError, OSError)` but `load_planet_image()` at line 319 catches only `(FileNotFoundError, pygame.error, ValueError)`. The comment at line 154 references parity with `load_planet_image` but the catch tuples diverge. `OSError` was added to the star path in PROJ-381 Phase 2 (ERR-02-001) to avoid swallowing `MemoryError`/`KeyboardInterrupt`, but the planet path was not updated to match.
```python
# load_star_image line 153 — includes OSError
except (FileNotFoundError, pygame.error, ValueError, OSError) as e:
    ...
# load_planet_image line 319 — does NOT include OSError
except (FileNotFoundError, pygame.error, ValueError) as e:
    ...
```
The comment at line 154 says the star catch was narrowed to match `load_planet_image`, but the planet path is actually NOT narrowed — it's missing `OSError`. If the intent is parity, `load_planet_image` should also include `OSError`. If the intent is the star path should match the planet path, `OSError` should be removed from `load_star_image`.

**Recommendation:** Add `OSError` to `load_planet_image`'s catch tuple for consistency with the documented ERR-02-001 fix.

### MINOR-005: Generic `Exception` subclass with no error code — `roles.py:64`
**File:** `game/core/roles.py`
**Line:** 64
**Issue:** `RoleRegistryReadOnlyError` inherits from `Exception` directly rather than from `GameException`. Per `docs/05_ERROR_HANDLING.md`, all custom exceptions should inherit from `GameException` to participate in the common `code`/`context` contract.
```python
class RoleRegistryReadOnlyError(Exception):
```
**Recommendation:** Inherit from `GameException` or a narrower subclass like `StateException`.

### MINOR-006: `except (ValueError, KeyError)` swallows design validation failures silently — `construction_queue.py:160`
**File:** `game/strategy/engine/handlers/construction_queue.py`
**Line:** 160
**Issue:** `_check_design_valid()` catches `(ValueError, KeyError)` and returns `True` (allows the design). A corrupt design entry that raises during validation is silently treated as valid. A logger.warning would help surface the swallowed error.
```python
except (ValueError, KeyError):
    return True  # Can't validate, allow by default
```
**Recommendation:** Add `logger.warning(...)` inside the catch block.

### MINOR-007: `except (ValueError, KeyError)` swallows cost calculation failure silently — `construction_queue.py:186`
**File:** `game/strategy/engine/handlers/construction_queue.py`
**Line:** 186
**Issue:** `_load_design_cost()` catches `(ValueError, KeyError)` and returns `{}`. While a `logger.warning` is present, the design that triggered a cost-calculation error goes into the queue with `total_cost={}` — effectively zero-cost. This is arguably correct (the design has no cost data) but deserves a comment documenting the intent.
```python
except (ValueError, KeyError) as e:
    logger.warning(f"Failed to calculate design cost for {design_id}: {e}")
    return {}
```
**Recommendation:** Add a brief comment documenting that zero-cost is intentional for un-costable designs.

### MINOR-008: `except AttributeError` suppresses structural errors silently — `satellite_controller.py:70-75,79-83,86-90,107-109`
**File:** `game/ai/satellite_controller.py`
**Lines:** 70-75, 79-83, 86-90, 107-109
**Issue:** Multiple broad `except AttributeError` blocks in `SatelliteAIController.update()` and `_find_nearest_enemy()` suppress missing-attribute errors without logging. While the intent (defensive against stub/test adapters) is valid per the comment at line 73, the doc comment "the absence of acceleration on those stubs is what we want anyway" only covers the first two blocks. The `get_position` exception at line 108 returns `None` silently with no log — that could mask a real bug in production.
```python
try:
    my_pos = self.ship.get_position()
except AttributeError:
    return None
```
**Recommendation:** Add `logger.debug(...)` to each `except AttributeError` block that doesn't already have a rationale comment.

---

## Resource Cleanup Findings

No resource-leak issues found in this shard. All file handles are properly closed:
- `BattleLogger` has proper `__exit__`, `__del__`, and try/finally in `start_session()`.
- `json_utils.save_json` uses atomic `write-to-tmp-then-replace`.
- All `Intentional broad catch` sites around external resource operations (replay capture, minefield resolution, reboard) have proper `logger.exception()` fallback.

---

## File Coverage Verification

| File | Status |
|------|--------|
| game/core/protocols/combat.py | Read - OK |
| game/ui/panels/planet_report_panel.py | Read - OK |
| game/ui/screens/race_setup/delegate_factory.py | Read - OK |
| game/simulation/components/abilities/__init__.py | Read - OK |
| game/ui/screens/test_lab/component_dropdown.py | Read - OK |
| game/strategy/data/orbital_generation_config.py | Read - OK (tight catch tuple) |
| game/strategy/engine/order_handlers/registry_factory.py | Read - OK |
| game/ui/screens/strategy_modal_window.py | Read - OK |
| game/strategy/engine/superweapon_command_handlers.py | Read - OK |
| game/ui/widgets/dropdown_helper.py | Read - OK |
| game/ui/screens/battle_setup/controller.py | Read - OK |
| game/strategy/engine/consumable_management_engine.py | Read - OK |
| game/ui/screens/battle_setup/panels/__init__.py | Read - OK |
| game/ui/screens/test_lab/renderer/metadata_panel.py | Read - OK |
| game/ui/panels/race_portrait_gallery.py | Read - OK |
| game/simulation/components/abilities/crew.py | Read - OK |
| game/strategy/combat/pre_tick_setup_registry.py | Read - OK |
| game/strategy/data/fleet_capability_calculator.py | Read - MAJOR-006 |
| game/strategy/engine/commands/order_metadata_view.py | Read - OK |
| game/simulation/replay/replay_record.py | Read - OK |
| game/ai/__init__.py | Read - OK |
| game/core/protocols/persistence.py | Read - OK |
| game/ui/screens/setup_renderer.py | Read - OK |
| game/strategy/engine/resupply_engine.py | Read - OK |
| game/ui/screens/builder/panel_layout_config.py | Read - OK |
| game/core/protocols/strategy_domain.py | Read - OK |
| game/strategy/engine/planet_action_engine.py | Read - OK |
| game/strategy/generation/density/primitives/geometric.py | Read - OK |
| game/ui/screens/strategy_render/dyson_spheres.py | Read - OK |
| game/simulation/components/abilities/defense.py | Read - OK |
| game/ui/screens/setup_data_io.py | Read - OK |
| game/ui/screens/test_lab/details/resource_outcomes.py | Read - OK |
| game/strategy/data/spectrum.py | Read - OK |
| game/ai/fighter_controller.py | Read - OK |
| game/core/string_utils.py | Read - OK |
| game/strategy/generation/loaders/__init__.py | Read - OK |
| game/simulation/combat/damage_calculator.py | Read - OK |
| game/simulation/systems/attack_processor.py | Read - OK (all broad catches properly commented) |
| game/ui/components/table/header.py | Read - OK |
| game/ui/screens/strategy_screen_order_editing.py | Read - OK |
| game/strategy/adapters/__init__.py | Read - OK |
| game/simulation/entities/ship_resource_manager.py | Read - OK |
| game/strategy/facade/dto/fleet_dto.py | Read - OK |
| game/simulation/systems/tactical_mine_resolver.py | Read - OK (all broad catches properly commented) |
| game/strategy/engine/quality_engine.py | Read - OK |
| game/ui/widgets/panel_factory.py | Read - OK |
| game/ui/screens/test_lab/screen_input_handler.py | Read - OK |
| game/simulation/systems/battle_logger.py | Read - OK |
| game/services/llm/defaults.py | Read - OK |
| game/ui/screens/strategy_fleet_command_router.py | Read - OK |
| game/ui/screens/test_lab/details/validation.py | Read - OK |
| game/core/protocols/common.py | Read - OK |
| game/strategy/data/order_types.py | Read - OK |
| game/ui/services/__init__.py | Read - OK |
| game/strategy/generation/planet_image_registry.py | Read - OK |
| game/simulation/components/component.py | Read - OK |
| game/core/patterns/layer_iterator.py | Read - OK |
| game/ui/utils/__init__.py | Read - OK |
| game/core/component_state.py | Read - OK |
| game/services/__init__.py | Read - OK |
| game/simulation/entities/ship_stat_querier.py | Read - OK |
| game/ui/screens/keybindings_scene.py | Read - OK |
| game/ui/panels/build_queue_portraits.py | Read - OK |
| game/strategy/data/fleet_consumable_aggregator.py | Read - OK |
| game/strategy/combat/post_battle_hook_builder.py | Read - OK (all broad catches properly commented) |
| game/engine/physics.py | Read - OK |
| game/strategy/combat/team_spec_builder.py | Read - OK |
| game/ui/screens/test_lab/formatting_utils.py | Read - OK |
| game/simulation/components/component_constants.py | Read - OK |
| game/strategy/services/superweapon_registry.py | Read - OK |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | Read - OK |
| game/strategy/data/planetary_facility.py | Read - MAJOR-004 |
| game/ui/__init__.py | Read - OK |
| game/simulation/systems/battle_setup.py | Read - OK |
| game/strategy/data/carried_vehicle_deploy.py | Read - OK (properly commented broad catch) |
| game/strategy/services/race_description_llm_controller.py | Read - OK (properly commented broad catch) |
| game/strategy/services/fleet_write_service.py | Read - MINOR-003 |
| game/strategy/data/spatial_index.py | Read - OK |
| game/strategy/data/ship_stats_cache.py | Read - MAJOR-005 |
| game/core/protocols/__init__.py | Read - OK |
| game/strategy/services/empire_economy_service.py | Read - OK |
| game/ui/research/__init__.py | Read - OK |
| game/strategy/services/ability_sources/fleet.py | Read - OK |
| game/ui/panels/base_gallery.py | Read - OK |
| game/ui/screens/builder/stat_rows_dynamic.py | Read - OK |
| game/ui/panels/race_environment_panel.py | Read - OK |
| game/strategy/data/task_force.py | Read - OK |
| game/simulation/components/modifier_manager.py | Read - OK |
| game/simulation/combat/combat_events.py | Read - OK (properly commented broad catch) |
| game/ui/screens/race_setup/controller.py | Read - OK |
| game/ui/screens/per_player_ui_state.py | Read - OK |
| game/core/registry.py | Read - OK |
| game/strategy/data/fleet_serde.py | Read - OK |
| game/ui/screens/battle_setup/panels/center_panel.py | Read - OK |
| game/ui/screens/menu_scene.py | Read - OK |
| game/ui/screens/race_setup/ship_preview.py | Read - OK |
| game/strategy/data/star_generation_config.py | Read - OK (tight catch tuple, intentional drop of KeyError) |
| game/simulation/components/abilities/colonize.py | Read - OK |
| game/strategy/data/race_config.py | Read - OK |
| game/ui/screens/transfer_view_model.py | Read - OK |
| game/ui/screens/build_queue_input_router.py | Read - OK |
| game/ui/screens/battle_setup/__init__.py | Read - OK |
| game/strategy/engine/order_handlers/transfer_branches.py | Read - OK |
| game/simulation/components/modifiers.py | Read - OK |
| game/research/data/tech_tree.py | Read - OK |
| game/ui/screens/planet_list_presets.py | Read - OK |
| game/strategy/services/empire_write_service.py | Read - OK |
| game/simulation/entities/ability_aggregator.py | Read - OK |
| game/ui/screens/data_list_window_mixin.py | Read - OK |
| game/strategy/systems/race_randomizer.py | Read - OK |
| game/ui/screens/battle_setup/spec_compiler.py | Read - OK |
| game/simulation/combat/boundary.py | Read - OK |
| game/simulation/designs.py | Read - OK |
| game/ui/screens/star_list_filters.py | Read - OK |
| game/simulation/components/abilities/weapons.py | Read - OK |
| game/ui/screens/strategy_render/systems.py | Read - OK |
| game/simulation/interfaces/ability_protocols.py | Read - OK |
| game/ui/screens/builder/modifier_config.py | Read - OK |
| game/ui/services/vehicle_class_service.py | Read - OK |
| game/strategy/data/planet_gen.py | Read - OK |
| game/simulation/__init__.py | Read - OK |
| game/strategy/engine/commands/__init__.py | Read - OK |
| game/strategy/engine/game_config.py | Read - OK |
| game/ui/services/design_loader_adapter.py | Read - OK |
| game/ui/utils/portraits.py | Read - OK |
| game/screen_router.py | Read - OK |
| game/ui/screens/battle_screen.py | Read - OK |
| game/core/protocols/strategy_entities.py | Read - OK |
| game/simulation/combat/ability_stat_registry.py | Read - OK |
| game/simulation/entities/ship_validator_helper.py | Read - OK |
| game/strategy/services/ability_sources/planet_intrinsic.py | Read - OK |
| game/strategy/engine/movement_phase_collaborator.py | Read - OK (properly commented broad catch) |
| game/strategy/engine/superweapon_handlers/close_warp_point.py | Read - OK |
| game/ui/screens/race_setup/screen.py | Read - OK |
| game/strategy/engine/happiness_engine.py | Read - MAJOR-003 |
| game/ui/screens/event_log_sidebar.py | Read - OK |
| game/strategy/services/ability_sources/warp_point.py | Read - OK |
| game/ui/services/component_service.py | Read - OK |
| game/strategy/facade/dto/system_dto.py | Read - OK |
| game/ui/screens/test_lab/dialogs.py | Read - OK |
| game/strategy/services/race_resolver.py | Read - OK |
| game/strategy/formulas/habitability.py | Read - OK |
| game/simulation/services/registry_loader.py | Read - OK |
| game/strategy/generation/density/primitives/__init__.py | Read - OK |
| game/strategy/data/galaxy_protocols.py | Read - OK |
| game/ui/screens/strategy_screen_composition.py | Read - OK |
| game/strategy/facade/__init__.py | Read - OK |
| game/strategy/combat/spec_compiler.py | Read - OK |
| game/ui/services/image/__init__.py | Read - OK |
| game/assets/asset_manager.py | Read - MINOR-002, MINOR-004 |
| game/ui/screens/new_game_setup_controller.py | Read - OK |
| game/core/validation_helpers.py | Read - OK |
| game/ui/screens/strategy_menu_panel.py | Read - OK |
| game/ui/screens/planet_list_controller.py | Read - OK |
| game/ui/screens/builder/drop_target.py | Read - OK |
| game/ui/panels/empire_treasury_panel.py | Read - OK |
| game/simulation/replay/replay_serialization.py | Read - MAJOR-001, MAJOR-002, MINOR-001 |
| game/strategy/events/event_types.py | Read - OK |
| game/ui/screens/list_data_source_base.py | Read - OK |
| game/strategy/services/combat_modifier_collector.py | Read - OK |
| game/ui/screens/race_setup/__init__.py | Read - OK |
| game/strategy/services/__init__.py | Read - OK |
| game/ui/screens/fleet_menu_items.py | Read - OK |
| game/simulation/components/abilities/cargo.py | Read - OK |
| game/strategy/engine/order_handlers/launch_satellites.py | Read - OK (properly commented broad catch) |
| game/ui/screens/battle_setup/panels/right_panel.py | Read - OK |
| game/strategy/engine/handlers/base.py | Read - OK |
| game/ui/screens/fleet_report_view_model.py | Read - OK |
| game/core/spectrum_math.py | Read - OK |
| game/strategy/validation/colonize_validator.py | Read - OK |
| game/ui/screens/planet_list_sidebar.py | Read - OK |
| game/core/roles.py | Read - MINOR-005 |
| game/strategy/formulas/__init__.py | Read - OK |
| game/ui/panels/strategy_widgets.py | Read - OK |
| game/ui/screens/battle_results_data.py | Read - OK |
| game/strategy/engine/handlers/lay_mines.py | Read - OK |
| game/ui/screens/strategy_click_dispatcher.py | Read - OK |
| game/ui/screens/build_queue_list_window.py | Read - OK |
| game/strategy/engine/session/persistence_adapter.py | Read - OK |
| game/ui/screens/test_lab/renderer/header_panel.py | Read - OK |
| game/ui/interfaces/__init__.py | Read - OK |
| game/ui/screens/galaxy_test/constants.py | Read - OK |
| game/ui/widgets/scrollable_json_panel.py | Read - OK |
| game/ui/screens/test_lab/renderer/validation_panel.py | Read - OK |
| game/ui/screens/battle_setup/constants.py | Read - OK |
| game/ui/screens/strategy_render/hex_outlines.py | Read - OK |
| game/strategy/generation/density/primitives/linear.py | Read - OK |
| game/ui/screens/strategy_render/overlay.py | Read - OK |
| game/core/config.py | Read - OK |
| game/ui/screens/race_setup/renderer.py | Read - OK |
| game/strategy/data/planet_naming.py | Read - OK |
| game/core/return_destination.py | Read - OK |
| game/ui/effects/hit_effects.py | Read - OK |
| game/strategy/data/planet_serde.py | Read - OK |
| game/ui/screens/test_lab/details/chrome.py | Read - OK |
| game/ui/screens/test_lab/theme.py | Read - OK |
| game/ai/satellite_controller.py | Read - MINOR-008 |
| game/strategy/engine/session/graph_restoration.py | Read - OK |
| game/strategy/generation/placement_strategies.py | Read - OK |
| game/simulation/managers/__init__.py | Read - OK |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Read - OK |
| game/ui/screens/empire_build_queue_window.py | Read - OK |
| game/engine/__init__.py | Read - OK |
| game/ui/screens/strategy_input_handler.py | Read - OK |
| game/strategy/engine/handlers/construction_queue.py | Read - MINOR-006, MINOR-007 |
| game/simulation/battle_controller.py | Read - OK (all broad catches properly commented) |
| game/simulation/replay/replay_player.py | Read - OK |
| game/services/llm/factory.py | Read - OK |
| game/ui/screens/builder/modifier_utils.py | Read - OK |
| game/strategy/combat/__init__.py | Read - OK |
| game/ui/screens/race_validator.py | Read - OK |
| game/strategy/services/replay_resolver.py | Read - OK |
| game/ui/screens/build_queue_renderer.py | Read - OK |
| game/simulation/entities/projectile.py | Read - OK |
| game/strategy/services/deployment_zone_calculator.py | Read - OK |
| game/ai/interfaces/__init__.py | Read - OK |
| game/strategy/data/planet_atmosphere.py | Read - OK |
| game/simulation/battle_runner.py | Read - MAJOR-007 |
| game/ui/screens/builder/right_panel.py | Read - OK |
| game/strategy/engine/production_math.py | Read - OK |
| game/ui/screens/workshop_context.py | Read - OK |
| game/strategy/data/homeworld_presets.py | Read - OK |
| game/strategy/generation/density/primitives/radial.py | Read - OK |
| game/simulation/components/abilities/planetary/__init__.py | Read - OK |
| game/ai/controller.py | Read - OK |
