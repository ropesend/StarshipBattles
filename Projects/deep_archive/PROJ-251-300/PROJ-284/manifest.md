# PROJ-284 File Manifest

> Generated during project initialization. Used for parallel execution conflict detection.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/colony_species_config.py | Production (NEW) | Phase 1 ✓ added: `ColonySpeciesConfig(food_allocation=1.0, last_food_ratio=1.0)` with `to_dict` that excludes the transient `last_food_ratio`; `__post_init__` validates `food_allocation >= 0` |
| game/strategy/data/planet.py | Production (MODIFY) | Phase 1 ✓ added `species_configs: Dict[str, ColonySpeciesConfig]` field + `get_species_config(race_id)` lazy-create-and-store helper; to_dict/from_dict round-trip |
| data/economy.json | Data (NEW) | Phase 2: data-driven population food resource |
| game/strategy/config/economy_config.py | Production (NEW) | Phase 2: `EconomyConfig` loader with `get_default_*` accessor |
| game/strategy/engine/organics_consumption_engine.py | Production (NEW) | Phase 2: drains food resource per turn; writes `last_food_ratio` |
| game/strategy/engine/happiness_engine.py | Production (NEW) | Phase 3: derives `pop.happiness` each turn |
| game/strategy/engine/population_engine.py | Production (MODIFY) | Phase 3: rework growth formula + decline term |
| game/strategy/engine/turn_engine.py | Production (MODIFY) | Phase 2+3: wire two new engines between the tick loop and population growth |
| game/strategy/interfaces/engines.py | Production (MODIFY) | Phase 2+3: add `IOrganicsConsumptionEngine` + `IHappinessEngine` protocols |
| game/ui/screens/food_allocation_editor.py | Production (NEW) | Phase 4: per-colony per-species slider UI |
| game/ui/screens/planet_abilities_window.py | Production (MODIFY) | Phase 4: add "Food Allocation" button |
| game/ui/screens/strategy_window_manager.py | Production (MODIFY) | Phase 4: wire food-editor button open callback |
| tests/unit/strategy/data/test_colony_species_config.py | Test (NEW) | Phase 1 ✓ added: 11 tests covering defaults, validation, transient-field serialization contract, round-trip |
| tests/unit/strategy/data/test_planet_species_configs.py | Test (NEW) | Phase 1 ✓ added: 9 tests covering species_configs field, `get_species_config` lazy-create, round-trip (transient field resets to 1.0), back-compat for old saves without the key. File lives at `test_planet_species_configs.py` (not `test_planet.py`) because the existing planet test suite is split by concern — follows convention |
| tests/unit/strategy/config/test_economy_config.py | Test (NEW) | Phase 2 |
| tests/unit/strategy/engine/test_organics_consumption_engine.py | Test (NEW) | Phase 2 |
| tests/unit/strategy/engine/test_happiness_engine.py | Test (NEW) | Phase 3 |
| tests/unit/strategy/engine/test_population_engine.py | Test (MODIFY) | Phase 3: rework around new formula |
| tests/unit/strategy/engine/test_turn_engine.py | Test (MODIFY) | Phase 2+3: verify new phase order |
| tests/integration/strategy/test_demographics_loop.py | Test (NEW) | Phase 3: end-to-end integration |
| tests/unit/ui/screens/test_food_allocation_editor.py | Test (NEW) | Phase 4 |
| tests/unit/ui/screens/test_planet_abilities_window.py | Test (MODIFY) | Phase 4: new button |
| docs/systems/strategy_layer.md | Docs (MODIFY) | Phase 5 |
| docs/04_SERVICES.md | Docs (MODIFY) | Phase 5 |
| CLAUDE.md | Docs (MODIFY) | Phase 5: optional pattern callout |
