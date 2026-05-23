# PROJ-487 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planetary_facility.py` | Production | Delete | Phase 2: delete 4 deprecated fuel wrappers (lines 209-221, ~16 LOC) and header comment at line 196 |
| `game/strategy/engine/resupply_engine.py` | Production | Migrate-callers | Phase 1: migrate 3 call sites (lines 135, 208, 293) to generic `*_consumable("fuel", ...)` API |
| `tests/unit/strategy/data/test_facility_resource_tracking.py` | Test | Migrate-callers | Phase 2: migrate ~56 test call sites of fuel wrappers to generic consumable API |
