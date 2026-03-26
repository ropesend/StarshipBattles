# PROJ-226 Phase 3: Engine & Service Consolidation

## DUP-SE-003/004: Spawn Logic Consolidation
- [x] Identify duplicated fleet/ship spawn logic in production_engine.py
- [x] Extract `_load_design`, `_create_and_place_facility`, `_load_and_create_ship` helpers
- [x] Refactor `_spawn_complex`, `_spawn_ship`, `_spawn_fleet_ship`, `_spawn_fleet_complex`
- [x] Verify production and conflict resolution tests pass

Note: conflict_resolution_engine.py had no spawn logic — duplication was entirely within production_engine.py between planet and fleet production paths.

## DUP-SE-006: JOIN_FLEET Handling Consolidation
- [x] Identify duplicated merge+log logic in fleet_order_processor.py
- [x] Extract `_execute_fleet_merge` helper
- [x] Updated `process_join_fleet` and `process_instant_orders` to use helper
- [x] Verify fleet order tests pass

## DUP-SE-007: Registries Initialization Consolidation
- [x] Identified duplicated GameRegistries construction in game_session.py (__init__ and from_dict)
- [x] Extracted `_resolve_registries()` static method
- [x] Both init paths now use the shared method
- [x] Verify DI and initialization tests pass

Note: The 7 engine files (resupply, resource, production, etc.) each receive registries via DI constructor injection — they don't duplicate the initialization. The duplication was only in GameSession's two construction paths.

## DUP-SS-01: Population Extraction
- [x] Identified duplicated population logic in cargo_transfer_service.py
- [x] Extracted `_extract_population_items()` module-level helper
- [x] Updated `get_load_items` and `get_inventory_items` to use helper
- [x] Verify cargo transfer tests pass

## DUP-SS-02: Superweapon Validation Consolidation
- [x] Identified duplicated ability-check and location-check patterns
- [x] Extracted `_require_ability()` and `_require_at_star_system()` helpers
- [x] Updated all 5 validation methods to use helpers
- [x] Verify superweapon tests pass

## Completion
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All Phase 3 items verified

Test count: 13433 passed, 2 skipped (same as Phase 2)
