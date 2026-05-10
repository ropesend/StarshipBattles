# PROJ-276 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | DELETE `component_damage` field (L113); 8 occurrences total |
| `game/strategy/services/ship_stats_calculator.py` | Production | MIGRATE 20 read sites to `components` dict |
| `game/strategy/data/ship_instance_bridge.py` | Production | MIGRATE 6 sites (ShipInstance → Ship) |
| `game/strategy/data/ship_instance_serializer.py` | Production | REMOVE `component_damage` from save shape; bump format version |
| `game/strategy/data/component_state.py` | Production | 2 sites — verify API surface sufficient for all readers |
| `game/strategy/combat/post_battle_hook.py` | Production | DELETE dual-write at L155-162; keep `components` write at L152 |
| `game/simulation/entities/ship_design_stats.py` | Production | MIGRATE 4 sites |
| `tests/fixtures/strategy_entities.py` | Test | Update fixture to use `components` dict |
| `tests/unit/strategy/test_ship_instance_damage.py` | Test | 2 occurrences |
| `tests/unit/strategy/test_ship_display_formatter.py` | Test | 1 occurrence |
| `tests/unit/strategy/test_fleet_capability_calculator_di.py` | Test | 1 occurrence |
| `tests/unit/strategy/ship_stats/test_edge_cases.py` | Test | 3 occurrences |
| `tests/unit/strategy/ship_instance/test_validation.py` | Test | 1 occurrence |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | Test | 5 occurrences |
| `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | Test | 3 occurrences |
| `tests/unit/strategy/ship_instance/test_cost_queries.py` | Test | 1 occurrence |
| `tests/unit/strategy/services/test_ship_stats_pod_storage.py` | Test | 2 occurrences |
| `tests/unit/simulation/systems/test_ship_design_stats.py` | Test | 1 occurrence |
| `tests/integration/strategy/turn_engine/test_components.py` | Test | 2 occurrences |
| `tests/integration/save_load/test_roundtrip_ships.py` | Test | 3 occurrences |
| `tests/integration/resource_system/test_resource_pipeline.py` | Test | 1 occurrence |
| `docs/systems/strategy_layer.md` | Doc | Remove `component_damage` as "authoritative legacy" references |
| `docs/04_SERVICES.md` | Doc | Update ShipStatsCalculator doc |
| `docs/systems/combat_simulation.md` | Doc | Update PROJ-269 Phase 2 reference to reflect Phase 2 closed by this project |
