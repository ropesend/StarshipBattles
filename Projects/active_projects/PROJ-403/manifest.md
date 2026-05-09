# PROJ-403 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/strategy/data/test_galaxy_entity_registry.py | Test | Replace `_MockGalaxy` with real `GalaxyState` instance (or shared helper). |
| tests/unit/strategy/data/test_galaxy_spatial_index.py | Test | Same migration. |
| tests/fixtures/galaxy_state_helpers.py | Test (optional) | Optional shared `make_galaxy_state(...)` helper if extraction makes sense. |
| game/strategy/data/galaxy_state.py | Production (read-only) | Canonical field names (`global_hex_planets`, `planet_to_system`, `global_hex_zones`, `next_planet_id`). |
| game/strategy/data/galaxy_entity_registry.py | Production (read-only) | Delegate that reads `GalaxyState` fields. |
| game/strategy/data/galaxy_spatial_index.py | Production (read-only) | Delegate that reads `GalaxyState` fields. |
