# PROJ-285 File Manifest

> Generated during project initialization. Used for parallel execution conflict detection.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/formulas/colony_output.py | Production (NEW) | Phase 1: `planet_habitability_multiplier` helper |
| game/strategy/data/planet.py | Production (MODIFY) | Phase 1: per-turn cache accessor |
| game/strategy/engine/harvesting_engine.py | Production (MODIFY) | Phase 2: habitability multiplier hook |
| game/strategy/engine/production_engine.py | Production (MODIFY) | Phase 3: habitability multiplier hook |
| game/strategy/engine/turn_engine.py | Production (MODIFY) | Phase 2+3: set `current_turn` on engines at turn start |
| tests/unit/strategy/formulas/test_colony_output.py | Test (NEW) | Phase 1 |
| tests/unit/strategy/data/test_planet.py | Test (MODIFY) | Phase 1: cache behavior tests |
| tests/unit/strategy/engine/test_harvesting_engine.py | Test (MODIFY) | Phase 2: retarget to ideal-planet fixture; add hostile-planet tests |
| tests/unit/strategy/engine/test_production_engine.py | Test (MODIFY) | Phase 3: retarget + add hostile-planet tests |
| tests/integration/strategy/test_habitability_on_economy.py | Test (NEW) | Phase 2+3: end-to-end ideal vs hostile comparison |
| tests/conftest.py | Test helper (MODIFY) | Phase 2: add `ideal_planet_fixture` / `ideal_race_fixture` helpers (if not already present from PROJ-283 Phase 4) |
| docs/systems/production_system.md | Docs (MODIFY) | Phase 4 |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Phase 4 |
| docs/04_SERVICES.md | Docs (MODIFY) | Phase 4 |
| CLAUDE.md | Docs (MODIFY) | Phase 4: optional per-turn-cache callout |
