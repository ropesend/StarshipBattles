# PROJ-226: Strategy Layer Consolidation — Design Notes

## Approach

### DUP-SE-008: Private API Access
The 12 instances of `session.turn_engine._registries` in `superweapon_command_handlers.py` and `command_handlers.py` must be replaced with a public accessor. The `turn_engine` should expose a public `registries` property or `get_registries()` method if one does not already exist.

### DUP-SE-009: Backward Compat Alias
`process_end_turn_orders` is a backward compatibility alias in `fleet_order_processor.py` and referenced in `interfaces/engines.py`. Per project policy (CLAUDE.md: System Migration Policy), backward compatibility layers must be eradicated. Remove the alias and update all call sites.

### DUP-SD-10: Facility Shipyard Check
`_facility_is_shipyard` is duplicated across `build_queue_source.py`, `production_engine.py`, and `empire_economy_calculator.py`. Extract to a shared utility or method on the facility/planet class.

### DUP-SD-09: Occupied Hexes
`occupied_hexes` logic appears in 7 files. Centralize into `galaxy_spatial_index.py` as the single authority for spatial queries.

### DUP-SE-003/004: Spawn Logic
Fleet/ship spawning is duplicated between `production_engine.py` and `conflict_resolution_engine.py`. Extract a shared `fleet_spawner` utility.

### DUP-SE-007: Registries Init
Seven engine files each initialize registries independently. Consolidate into a base class or shared initialization helper.

## Constraints

- All changes must pass the existing 7353+ test baseline
- No backward compatibility layers — old patterns are removed completely
- Follow facade/delegate pattern for any new abstractions
