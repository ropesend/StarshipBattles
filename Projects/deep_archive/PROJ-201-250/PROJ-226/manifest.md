# PROJ-226: Strategy Layer Consolidation — File Manifest

## Production Files

### Strategy Engine
- `game/strategy/engine/superweapon_command_handlers.py` — DUP-SE-001 (mission move bug), DUP-SE-008 (11 private `_registries` accesses), DUP-SS-02 (validation dedup)
- `game/strategy/engine/command_handlers.py` — DUP-SE-008 (1 private `_registries` access), DUP-SE-006 (JOIN_FLEET handling)
- `game/strategy/engine/conflict_resolution_engine.py` — DUP-SE-003/004 (spawn logic)
- `game/strategy/engine/fleet_order_processor.py` — DUP-SE-006 (JOIN_FLEET), DUP-SE-009 (`process_end_turn_orders` alias)
- `game/strategy/engine/game_session.py` — DUP-SE-006 (JOIN_FLEET), DUP-SE-007 (registries init)
- `game/strategy/engine/production_engine.py` — DUP-SE-003/004 (spawn logic), DUP-SD-10 (`_facility_is_shipyard`), DUP-SE-007 (registries init)
- `game/strategy/engine/turn_engine.py` — DUP-SE-006 (JOIN_FLEET), DUP-SE-008 (public API for registries)
- `game/strategy/engine/empire_economy_calculator.py` — DUP-SD-10 (`_facility_is_shipyard`), DUP-SE-007 (registries init)
- `game/strategy/engine/resupply_engine.py` — DUP-SE-007 (registries init)
- `game/strategy/engine/resource_management_engine.py` — DUP-SE-007 (registries init)
- `game/strategy/engine/maintenance_engine.py` — DUP-SE-007 (registries init)
- `game/strategy/engine/harvesting_engine.py` — DUP-SE-007 (registries init)

### Strategy Data
- `game/strategy/data/stars.py` — DUP-SD-06 (dead `_generate_mass`)
- `game/strategy/data/galaxy_entity_registry.py` — DUP-SD-02 (planet registration), DUP-SD-09 (occupied_hexes)
- `game/strategy/data/galaxy_spatial_index.py` — DUP-SD-02 (planet registration), DUP-SD-09 (occupied_hexes)
- `game/strategy/data/galaxy_system_generator.py` — DUP-SD-02 (planet registration)
- `game/strategy/data/galaxy.py` — DUP-SD-02 (planet registration), DUP-SD-09 (occupied_hexes)
- `game/strategy/data/build_queue_source.py` — DUP-SD-10 (`_facility_is_shipyard`)
- `game/strategy/data/planet.py` — DUP-SD-09 (occupied_hexes)
- `game/strategy/data/storm.py` — DUP-SD-09 (occupied_hexes)
- `game/strategy/generation/planet_gen.py` — DUP-SD-01 (companion star gen), DUP-SD-06 (dead `_generate_mass`)
- `game/strategy/generation/storm_generator.py` — DUP-SD-09 (occupied_hexes)

### Strategy Services & Validation
- `game/strategy/services/cargo_transfer_service.py` — DUP-SS-01 (population extraction)
- `game/strategy/validation/superweapon_validator.py` — DUP-SS-02 (superweapon validation dedup)

### Strategy Interfaces
- `game/strategy/interfaces/engines.py` — DUP-SE-006 (JOIN_FLEET), DUP-SE-009 (`process_end_turn_orders`)

## Test Files

### Unit Tests — Strategy Engine
- `tests/unit/strategy/engine/test_superweapon_handler_validation.py`
- `tests/unit/strategy/engine/test_superweapon_edge_cases.py`
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
- `tests/unit/strategy/engine/test_superweapon_order_processor.py`
- `tests/unit/strategy/engine/test_colonize_mission_handler.py`
- `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- `tests/unit/strategy/engine/test_build_order_processor.py`
- `tests/unit/strategy/engine/test_production_refactor.py`
- `tests/unit/strategy/engine/test_production_repro.py`

### Unit Tests — Strategy Data
- `tests/unit/strategy/data/test_stars.py`
- `tests/unit/strategy/data/test_planet_gen.py`
- `tests/unit/strategy/data/test_build_queue_source.py`
- `tests/unit/strategy/data/test_superweapon_orders.py`
- `tests/unit/strategy/data/test_fleet_order_resolution.py`

### Unit Tests — Strategy Services & Other
- `tests/unit/strategy/services/test_cargo_transfer_service.py`
- `tests/unit/strategy/validation/test_superweapon_validator.py`
- `tests/unit/strategy/test_fleet_order_processor.py`
- `tests/unit/strategy/test_game_session.py`
- `tests/unit/strategy/test_game_session_events.py`
- `tests/unit/strategy/test_game_session_save_load_registries.py`
- `tests/unit/strategy/mocks/mock_engines.py`
- `tests/unit/strategy/turn_engine/test_dependency_injection.py`
- `tests/unit/test_advanced_fleet_orders.py`
- `tests/unit/test_fleet_orders_logic.py`

### Integration Tests
- `tests/integration/strategy/test_star_generation.py`
- `tests/integration/strategy/test_planet_gen.py`
- `tests/integration/strategy/test_planet_physics.py`
- `tests/integration/strategy/test_colonize_logic.py`
- `tests/integration/strategy/test_superweapon_integration.py`
- `tests/integration/strategy/test_game_session_strategy.py`
- `tests/integration/strategy/test_production_rates.py`
- `tests/integration/strategy/production/test_fleet_production_e2e.py`
