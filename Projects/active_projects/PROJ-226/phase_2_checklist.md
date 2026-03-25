# PROJ-226 Phase 2: Strategy Data Consolidation

## DUP-SD-01: Companion Star Generation
- [ ] Identify duplicated companion/secondary star generation logic in `game/strategy/generation/planet_gen.py`
- [ ] Consolidate into a single generation path
- [ ] Update tests in `tests/unit/strategy/data/test_planet_gen.py` and `tests/integration/strategy/test_planet_gen.py`
- [ ] Verify star generation integration tests pass

## DUP-SD-02: Planet Registration
- [ ] Map all planet registration paths across:
  - `game/strategy/data/galaxy_entity_registry.py`
  - `game/strategy/data/galaxy_spatial_index.py`
  - `game/strategy/data/galaxy_system_generator.py`
  - `game/strategy/data/galaxy.py`
- [ ] Consolidate to a single authoritative registration method
- [ ] Update all call sites
- [ ] Verify integration tests pass

## DUP-SD-06: Dead `_generate_mass`
- [ ] Confirm `_generate_mass` is dead code in `game/strategy/data/stars.py` and/or `game/strategy/generation/planet_gen.py`
- [ ] Remove the dead method(s)
- [ ] Update `tests/unit/strategy/data/test_stars.py` if needed
- [ ] Verify no references remain

## DUP-SD-09: `occupied_hexes` Consolidation
- [ ] Audit `occupied_hexes` logic across all 7 files:
  - `game/strategy/generation/storm_generator.py`
  - `game/strategy/data/stars.py`
  - `game/strategy/data/storm.py`
  - `game/strategy/data/planet.py`
  - `game/strategy/data/galaxy_spatial_index.py`
  - `game/strategy/data/galaxy_entity_registry.py`
  - `game/strategy/data/galaxy.py`
- [ ] Centralize into `galaxy_spatial_index.py` as single authority
- [ ] Update all consumers to use the centralized version
- [ ] Verify spatial tests pass

## DUP-SD-10: `_facility_is_shipyard` Consolidation
- [ ] Identify duplicated shipyard check logic in:
  - `game/strategy/data/build_queue_source.py`
  - `game/strategy/engine/production_engine.py`
  - `game/strategy/engine/empire_economy_calculator.py`
- [ ] Extract to a shared utility or method on facility/planet
- [ ] Update all call sites
- [ ] Verify production and build queue tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 2 items verified
