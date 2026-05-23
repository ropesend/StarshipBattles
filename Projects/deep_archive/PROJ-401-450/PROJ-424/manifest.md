# PROJ-424 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/commands/order_metadata_view.py` | Production (new) | Phase 2: new `OrderMetadataView` class + `order_metadata` singleton. Lazy registry import inside `_registry()`. |
| `game/strategy/engine/commands/registry.py` | Production | Phase 1: add `CommandRegistry.planet_fms_action_order_types()` deriving from `CommandSpec.subcategories`. |
| `game/strategy/engine/handlers/lay_mines.py` | Production | Phase 1: add `subcategories=frozenset({"planet_fms"})` to `@command_spec(...)`. |
| `game/strategy/engine/handlers/launch_fighters.py` | Production | Phase 1: add `subcategories=frozenset({"planet_fms"})` to `@command_spec(...)`. |
| `game/strategy/engine/handlers/launch_satellites.py` | Production | Phase 1: add `subcategories=frozenset({"planet_fms"})` to `@command_spec(...)`. |
| `game/strategy/engine/handlers/recover_fighters.py` | Production | Phase 1: add `subcategories=frozenset({"planet_fms"})` to `@command_spec(...)`. |
| `game/strategy/engine/handlers/recover_satellites.py` | Production | Phase 1: add `subcategories=frozenset({"planet_fms"})` to `@command_spec(...)`. |
| `game/strategy/services/action_time_resolver.py` | Production | Phase 3: delete `_build_order_to_ability_map` + `ORDER_TO_ABILITY_MAP` import-time snapshot. Replace with call-time `order_metadata.order_to_ability_map` read. Migrate `MOVEMENT_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` imports to `order_metadata`. |
| `game/strategy/engine/action_execution_engine.py` | Production | Phase 4: replace `MOVEMENT_ORDER_TYPES` / `ACTION_ORDER_TYPES` / `PLANET_FMS_ACTION_ORDER_TYPES` imports with `order_metadata`. |
| `game/strategy/engine/fleet_movement_engine.py` | Production | Phase 4: replace `MOVEMENT_ORDER_TYPES` / `ACTION_ORDER_TYPES` imports with `order_metadata`. |
| `game/strategy/engine/planet_action_engine.py` | Production | Phase 4: replace `PLANET_ACTION_ORDER_TYPES` import with `order_metadata`. |
| `game/strategy/services/fleet_navigation_service.py` | Production | Phase 4: replace `MOVEMENT_ORDER_TYPES` / `ACTION_ORDER_TYPES` imports with `order_metadata`. |
| `game/strategy/services/fleet_path_projection.py` | Production | Phase 4: replace `MOVEMENT_ORDER_TYPES` import with `order_metadata`. |
| `game/strategy/services/cargo_transfer_service.py` | Production | Phase 4: replace `MOVEMENT_ORDER_TYPES` import with `order_metadata`. |
| `game/strategy/data/order_types.py` | Production | Phase 5: delete `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, `PLANET_FMS_ACTION_ORDER_TYPES`. No compatibility aliases. |
| `game/strategy/data/fleet.py` | Production | Phase 5: delete re-exports of the deleted frozensets. |
| `tests/unit/strategy/engine/commands/test_order_metadata_view.py` | Test (new) | Phase 2: new module. Tests `test_view_movement_matches_registry`, `test_view_action_matches_registry`, `test_view_planet_action_matches_registry`, `test_view_planet_fms_matches_registry`, `test_view_order_to_ability_matches_registry`, `test_view_is_lazy_at_import_time`, `test_view_reflects_replace_overlay`. |
| `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py` | Test (new) | Phase 5: final guard. `test_order_types_module_no_longer_exports_metadata_constants` + `test_fleet_module_no_longer_re_exports_metadata_constants`. |
| `tests/unit/strategy/engine/test_command_specs_contract.py` | Test | Phase 1 + Phase 3: add `planet_fms` derivation assertions; switch order-to-ability contract to `order_metadata.order_to_ability_map`. |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | Test | Phase 1: add `planet_fms_action_order_types()` derivation contract. |
| `tests/unit/strategy/engine/test_command_registry_thirdparty.py` | Test | Phase 4: update if it imports duplicated constants directly. |
| `tests/unit/strategy/data/test_order_types_characterization.py` | Test | Phase 5: drop characterization assertions on the deleted constants. |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Test | Phase 3: add `test_resolve_action_time_reflects_registry_replace`; remove `ORDER_TO_ABILITY_MAP` import-time assertions. |
| `tests/unit/strategy/fleet_movement_engine/test_characterization.py` | Test | Phase 4: update imports to `order_metadata`. |
| `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py` | Test | Phase 4: update imports to `order_metadata`. |
| `tests/unit/strategy/test_fleet_order_processor.py` | Test | Phase 4: update imports to `order_metadata`. |
| `docs/systems/orders_system.md` | Docs | Phase 6: describe `order_metadata` as the single read path; document `planet_fms` subcategory + lazy-view cycle break; remove "edit `ORDER_TO_ABILITY_MAP` / frozensets manually" guidance. |
| `docs/04_SERVICES.md` | Docs | Phase 6: update strategy-services description to reference `order_metadata`. |
| `docs/systems/satellites.md` | Docs | Phase 6: refresh any reference to `PLANET_FMS_ACTION_ORDER_TYPES` / FMS metadata derivation. |
