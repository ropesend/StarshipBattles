# PROJ-287 File Manifest

> Used for parallel execution conflict detection with PROJ-286, 288..290.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/core/protocols.py | Production (MODIFY) | Add `IRaceRegistry` `@runtime_checkable` Protocol with `get_race(race_id) -> Optional[RaceConfig]` |
| game/strategy/systems/race_library.py | Production (MODIFY) | Add `CachedRaceRegistry` class wrapping `RaceLibrary`. `save_race` emits invalidation (or caller invalidates) |
| game/strategy/facade/strategy_session_facade.py | Production (MODIFY) | Add `get_race_registry() -> IRaceRegistry` lazy-init method |
| game/strategy/data/empire.py | Production (MODIFY) | Add `resident_species() -> Set[str]` method |
| game/ui/screens/race_setup_screen.py | Production (MODIFY) | On race save, call `facade.get_race_registry().invalidate(race_id)` |
| tests/unit/core/test_protocols.py | Test (MODIFY) | Add `IRaceRegistry` TypeGuard-style tests if the file has that pattern |
| tests/unit/strategy/systems/test_race_library.py | Test (MODIFY) | Add `TestCachedRaceRegistry` class: cache-hit/miss, invalidate(), None-caching |
| tests/unit/strategy/facade/test_strategy_session_facade.py | Test (MODIFY) | Add test: `facade.get_race_registry()` returns same instance across calls |
| tests/unit/strategy/data/test_empire.py | Test (MODIFY / NEW) | Add `TestResidentSpecies`: empty empire, multi-species, excludes count=0, no duplicates |
| docs/01_ARCHITECTURE.md | Docs (MODIFY) | Add `IRaceRegistry` to the Protocols table (§Key Protocols) |
| docs/02_PATTERNS.md | Docs (MODIFY) | Optional: add a callout under the CQRS-lite pattern about read-interfaces on the facade |
| docs/04_SERVICES.md | Docs (MODIFY) | Add `CachedRaceRegistry` entry under the strategy-layer services catalog |
