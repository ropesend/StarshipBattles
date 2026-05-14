# PROJ-415 Phase 1a — Caller Migration Table

> Generated 2026-05-13 by AST scan over `game/`, `tests/`, `combat_lab/`, `Tools/`.
> Tool: `python` AST walker matching `ImportFrom(module='game.strategy.data.planet')` for symbols `PlanetaryFacility`, `SpeciesPopulation`, `ColonySpeciesConfig`.

## Summary

- **Total import nodes:** 64
- **Total symbol references:** 65 (one node imports two shim symbols)
- **Distinct caller files:** 61
- **Per symbol:** `PlanetaryFacility`=53, `SpeciesPopulation`=12, `ColonySpeciesConfig`=0 external
- **Parse failures (non-blocking):** `Tools/visual_test_galaxy/visual_test_galaxy.py` (pre-existing syntax error, no shim imports affected)

## Group A — production (`game/`) — 9 files

| File | Line | Imported names | Migrate |
|------|------|----------------|---------|
| `game/strategy/quickstart_builder.py` | 16 | PlanetaryFacility | -> planetary_facility |
| `game/strategy/data/build_queue_source.py` | 20 (TYPE_CHECKING) | PlanetaryFacility | -> planetary_facility |
| `game/strategy/engine/game_initializer.py` | 19 | SpeciesPopulation | -> species_population |
| `game/strategy/engine/harvesting_engine.py` | 42 (TYPE_CHECKING) | Planet, PlanetaryFacility | split: Planet stays; PlanetaryFacility -> planetary_facility |
| `game/strategy/engine/population_engine.py` | 29 (TYPE_CHECKING) | Planet, SpeciesPopulation | split |
| `game/strategy/engine/production_spawner.py` | 13 | PlanetaryFacility | -> planetary_facility |
| `game/strategy/engine/resupply_engine.py` | 30 (TYPE_CHECKING) | PlanetaryFacility | -> planetary_facility |
| `game/strategy/engine/order_handlers/colonize.py` | 152 (local) | PlanetaryFacility | -> planetary_facility |
| `game/strategy/engine/order_handlers/transfer_branches.py` | 213 (local) | SpeciesPopulation | -> species_population |

## Group B — unit tests (`tests/unit/`) — 27 files

| File | Line | Imported names |
|------|------|----------------|
| `tests/fixtures/yard_facility.py` | 40 | PlanetaryFacility |
| `tests/performance/bench_turn_processing.py` | 35 | PlanetaryFacility |
| `tests/unit/core/test_protocols.py` | 42 | Planet, PlanetaryFacility, PlanetType |
| `tests/unit/quickstart/test_quickstart_builder.py` | 20 | PlanetaryFacility |
| `tests/unit/strategy/test_engine_event_emission.py` | 66 | PlanetaryFacility |
| `tests/unit/strategy/test_quickstart_builder.py` | 267 | PlanetaryFacility |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | 25 | Planet, PlanetType, PlanetaryFacility |
| `tests/unit/strategy/data/test_build_context.py` | 156 | PlanetaryFacility |
| `tests/unit/strategy/data/test_build_queue_source.py` | 18 | Planet, PlanetaryFacility |
| `tests/unit/strategy/data/test_colony_yard_registries.py` | 13 | PlanetaryFacility |
| `tests/unit/strategy/data/test_facility_construction_queue.py` | 8 | Planet, PlanetaryFacility |
| `tests/unit/strategy/data/test_facility_resource_tracking.py` | 10 | Planet, PlanetaryFacility |
| `tests/unit/strategy/data/test_population_model.py` | 8 | Planet, SpeciesPopulation, PlanetType |
| `tests/unit/strategy/engine/test_colonize_population.py` | 19 | Planet, PlanetType, SpeciesPopulation |
| `tests/unit/strategy/engine/test_empire_economy_calculator.py` | 18 | Planet, PlanetaryFacility |
| `tests/unit/strategy/engine/test_harvesting_engine.py` | 18 | Planet, PlanetaryFacility |
| `tests/unit/strategy/engine/test_order_processor_transfer.py` | 18 | SpeciesPopulation |
| `tests/unit/strategy/engine/test_planetary_yard_requirement.py` | 14 | PlanetaryFacility |
| `tests/unit/strategy/engine/test_population_engine.py` | 11 | Planet, SpeciesPopulation, PlanetType |
| `tests/unit/strategy/engine/test_resupply_engine.py` | 11 | PlanetaryFacility |
| `tests/unit/strategy/engine/test_set_build_queue_paused_command.py` | 13 | Planet, PlanetaryFacility |
| `tests/unit/strategy/engine/test_transfer_order.py` | 13 | Planet, PlanetType, SpeciesPopulation |
| `tests/unit/strategy/facade/test_empire_dto.py` | 174 | Planet, PlanetType, PlanetaryFacility |
| `tests/unit/strategy/facade/test_population_dtos.py` | 8 | Planet, PlanetType, SpeciesPopulation |
| `tests/unit/strategy/facade/test_system_dto.py` | 389 | Planet, PlanetType, PlanetaryFacility |
| `tests/unit/strategy/planet/test_planet_validation.py` | 4 | Planet, PlanetType, PlanetaryFacility, SpeciesPopulation |
| `tests/unit/strategy/production_engine/test_paused_queue.py` | 18 | PlanetaryFacility |
| `tests/unit/strategy/production_engine/test_spawning.py` | 10 | PlanetaryFacility |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | 13 | PlanetaryFacility |
| `tests/unit/strategy/services/test_planet_economy_projector.py` | 27 | Planet, PlanetaryFacility, PlanetType |
| `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py` | 14 | SpeciesPopulation |

## Group C — integration tests (`tests/integration/`) — 21 files

| File | Line(s) | Imported names |
|------|---------|----------------|
| `tests/integration/test_complex_workflow.py` | 11 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/gameplay_loop/test_turn_execution.py` | 15 | PlanetaryFacility |
| `tests/integration/resource_system/test_custom_resource_lifecycle.py` | 23 | PlanetaryFacility |
| `tests/integration/save_load/test_resupply_persistence.py` | 10 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/test_economy_e2e.py` | 20 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/test_planetary_facilities.py` | 2 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/test_production_rates.py` | 17 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/test_projector_drain_matches_engine.py` | 36 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/test_resupply_system.py` | 15 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/ui/test_strategy_buttons.py` | 82 | PlanetaryFacility |
| `tests/integration/ui/build_queue_screen/conftest.py` | 7 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/ui/build_queue_screen/test_basics.py` | 7 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/ui/build_queue_screen/test_queue_selector.py` | 14, 109, 298, 375 | PlanetaryFacility (4 imports) |
| `tests/integration/strategy/facade/test_system_queries.py` | 13 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/production/conftest.py` | 10 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/production/test_completion.py` | 14 | PlanetaryFacility |
| `tests/integration/strategy/production/test_queue.py` | 15 | PlanetaryFacility |
| `tests/integration/strategy/transfer/conftest.py` | 11 | Planet, PlanetType, SpeciesPopulation |
| `tests/integration/strategy/turn_engine/test_harvesting.py` | 17 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/turn_engine/test_mid_turn_invariants.py` | 39 | Planet, PlanetType, PlanetaryFacility |
| `tests/integration/strategy/turn_engine/test_resupply.py` | 16 | Planet, PlanetType, PlanetaryFacility |

## Group D — combat_lab and Tools

None — zero shim usages.

## Phase 1c shim deletion target

- `game/strategy/data/planet.py:19-25`
  - lines 19-21: comment block removed
  - line 22: `from game.strategy.data.planetary_facility import PlanetaryFacility  # noqa: F401` — deleted
  - line 23: `from game.strategy.data.species_population import SpeciesPopulation  # noqa: F401` — deleted
  - line 24: `# PROJ-284: per-colony per-species config (food allocation slider, etc.)` — deleted
  - line 25: `from game.strategy.data.colony_species_config import ColonySpeciesConfig  # noqa: F401` — kept; drop the `# noqa: F401` (runtime dep at lines 107, 187, 190)
