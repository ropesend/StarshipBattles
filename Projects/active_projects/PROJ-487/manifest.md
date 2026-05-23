# PROJ-487 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planetary_facility.py` | Production | Delete | Phase 2: delete 4 deprecated fuel wrappers (lines 209-221, ~16 LOC) and header comment at line 196 |
| `game/strategy/engine/resupply_engine.py` | Production | Migrate-callers | Phase 1: migrate 3 call sites (lines 135, 208, 293) to generic `*_consumable("fuel", ...)` API |
| `tests/unit/strategy/data/test_facility_resource_tracking.py` | Test | Migrate-callers | Phase 2: migrate ~56 test call sites of fuel wrappers to generic consumable API |
| `tests/unit/strategy/engine/test_resupply_engine.py` | Test | Migrate-callers | Phase 2: migrate 3 mock-call assertions (`facility.withdraw_fuel.assert_called_once_with(...)` at lines 492, 512, 531) to `withdraw_consumable` with the `"fuel"` resource_id |
| `tests/integration/strategy/test_resupply_system.py` | Test | Migrate-callers | Phase 2: migrate 4 assertions on `facility.get_fuel_storage()` (lines 300, 344, 375, 401) to `get_consumable_storage("fuel")` |
| `tests/integration/save_load/test_resupply_persistence.py` | Test | Migrate-callers | Phase 2: migrate 1 assertion on `restored.facilities[0].get_fuel_storage()` (line 100) to `get_consumable_storage("fuel")` |
