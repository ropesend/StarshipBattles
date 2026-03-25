# PROJ-223 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/core/json_utils.py` | Production | Add @register_serializable decorator (Phase 1) |
| `game/strategy/data/empire.py` | Production | Fix built_ship_designs set ordering (Phase 1) |
| `tests/infrastructure/deep_compare.py` | Test | NEW — Deep comparison utility (Phase 1) |
| `tests/infrastructure/state_snapshot.py` | Test | NEW — State snapshot & verification harness (Phase 6) |
| `tests/fixtures/strategy_entities.py` | Test | NEW — Factory functions for all serializable types (Phase 1) |
| `tests/integration/save_load/conftest.py` | Test | Extend with round-trip helpers and fixtures (Phase 1) |
| `tests/unit/infrastructure/test_deep_compare.py` | Test | NEW — Tests for deep comparison utility (Phase 1) |
| `tests/unit/infrastructure/test_state_snapshot.py` | Test | NEW — Tests for state snapshot utility (Phase 6) |
| `tests/unit/fixtures/test_strategy_entities.py` | Test | NEW — Tests for factory functions (Phase 1) |
| `tests/integration/save_load/test_roundtrip_stars.py` | Test | NEW — Spectrum, Star round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_storms.py` | Test | NEW — StormEffect, Storm round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_galaxy.py` | Test | NEW — WarpPoint, StarSystem, Galaxy round-trip (Phase 2-3) |
| `tests/integration/save_load/test_roundtrip_planet.py` | Test | NEW — SpeciesPopulation, PlanetaryFacility, Planet round-trip (Phase 2-3) |
| `tests/integration/save_load/test_roundtrip_empire.py` | Test | NEW — RaceConfig, Empire round-trip (Phase 2-3) |
| `tests/integration/save_load/test_roundtrip_events.py` | Test | NEW — Event, EventLog round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_config.py` | Test | NEW — GameConfig, PlayerConfig round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_designs.py` | Test | NEW — DesignMetadata round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_research.py` | Test | NEW — NodeState, ResearchTracker round-trip (Phase 2-3) |
| `tests/integration/save_load/test_roundtrip_orders.py` | Test | NEW — FleetOrder all 7 formats round-trip (Phase 2) |
| `tests/integration/save_load/test_roundtrip_ships.py` | Test | NEW — ShipInstance round-trip (Phase 3) |
| `tests/integration/save_load/test_roundtrip_fleet.py` | Test | NEW — Fleet round-trip (Phase 3) |
| `tests/integration/save_load/test_registry_injection.py` | Test | NEW — DI registry injection validation (Phase 4) |
| `tests/integration/save_load/test_reference_integrity.py` | Test | NEW — Cross-object reference integrity (Phase 4) |
| `tests/integration/save_load/test_full_roundtrip.py` | Test | NEW — Full GameSession end-to-end (Phase 5) |
| `tests/integration/save_load/test_live_verification.py` | Test | NEW — Live state comparison tests (Phase 6) |
