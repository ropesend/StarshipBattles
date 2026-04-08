# PROJ-226 Phase 2: Strategy Data Consolidation

## DUP-SD-01: Companion Star Generation
- [x] Identify duplicated companion/secondary star generation logic in `game/strategy/data/stars.py`
- [x] Consolidate into a single generation path
- [x] Verify star generation integration tests pass

Extracted `_generate_companions()` method that both `generate_from_blueprint` and `_generate_random_stars` call. The only difference (mass generation function) is passed as a callable.

## DUP-SD-02: Planet Registration
- [x] Map all planet registration paths
- [x] Consolidate to a single authoritative registration method
- [x] Verify integration tests pass

Extracted `_index_planet()` private method in `galaxy_entity_registry.py`. Both `register_planet` and `restore_planet` now delegate to it.

## DUP-SD-06: Dead `_generate_mass`
- [x] Confirm `_generate_mass` is dead code in `game/strategy/data/planet_gen.py`
- [x] Remove the dead method
- [x] Update tests — removed 3 dead tests from test_planet_gen.py, 1 from test_planet_physics.py
- [x] Verify no references remain

Note: `_generate_mass` in `stars.py` is NOT dead (called in star generation). Only the `planet_gen.py` version was dead.

## DUP-SD-09: `occupied_hexes` Consolidation
- [x] Audit `occupied_hexes` logic across all files
- [x] Decision: NOT consolidated — 1-line protocol implementations, over-engineering to extract

## DUP-SD-10: `_facility_is_shipyard` Consolidation
- [x] Inlined to `facility.is_shipyard` directly
- [x] Deleted `_facility_is_shipyard` wrapper from `build_queue_source.py`
- [x] Updated imports in `production_engine.py` and `empire_economy_calculator.py`
- [x] Updated tests in `test_build_queue_source.py`
- [x] Verify production and build queue tests pass

## Completion
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All Phase 2 items verified

Test delta: 13433 passed (1 dead test removed), 2 skipped
