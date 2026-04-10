# PROJ-267 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### Phase 1: Consolidate Shared Helpers

| File | Type | Notes |
|------|------|-------|
| `tests/conftest.py` | Test infra | Canonical `make_colony_ship_for_planet()`; may add `make_colony_ship()` variant |
| `tests/helpers/__init__.py` | Test infra | New directory for shared test helpers |
| `tests/helpers/mock_galaxy.py` | Test infra | New file: shared MockGalaxy/MockSystem/MockPlanet classes |
| `tests/integration/colonization/conftest.py` | Test infra | Remove duplicate `make_colony_ship_for_planet()` |
| `tests/integration/gameplay_loop/test_commands_colonization.py` | Test | Remove local `make_colony_ship_for_planet()`, import canonical |
| `tests/integration/colonization/test_planet_specific_colonization.py` | Test | Remove local `make_colony_ship()`, import canonical |
| `tests/integration/strategy/test_colonize_logic.py` | Test | Remove local `make_colony_ship()`, MockGalaxy, MockSystem (if file exists) |
| `tests/integration/strategy/test_command_handlers.py` | Test | Remove local `make_colony_ship()`, MockGalaxy |
| `tests/integration/strategy/facade/test_facade_integration.py` | Test | Remove local `make_colony_ship_for_planet()` |
| `tests/unit/strategy/engine/test_colonize_mission_handler.py` | Test | Remove local `make_colony_ship()` |
| `tests/unit/strategy/engine/test_process_colonize_validation.py` | Test | Remove local `make_colony_ship()`, MockGalaxy, MockSystem |
| `tests/unit/strategy/engine/test_process_colonize_cargo.py` | Test | Remove local MockGalaxy, MockSystem |
| `tests/integration/strategy/test_path_projection.py` | Test | Remove local MockGalaxy, MockSystem |
| `tests/integration/strategy/test_fleet_navigation_consistency.py` | Test | Remove local MockGalaxy |
| `tests/integration/strategy/test_economy_e2e.py` | Test | Remove local MockGalaxy |
| `tests/integration/strategy/test_resupply_system.py` | Test | Remove local MockGalaxy |
| `tests/integration/strategy/transfer/conftest.py` | Test infra | Remove local MockGalaxy, MockSystem |
| `tests/integration/strategy/turn_engine/conftest.py` | Test infra | Remove local MockGalaxy |
| `tests/unit/strategy/engine/test_colonize_population.py` | Test | Remove local MockGalaxy |
| `tests/integration/ui/build_queue_screen/conftest.py` | Test infra | Remove local MockGalaxy |
| `tests/integration/ui/test_build_queue_formatting.py` | Test | Remove local MockGalaxy |
| `tests/integration/ui/test_build_queue_drag_drop.py` | Test | Remove local MockGalaxy |
| `tests/integration/ui/build_queue_screen/test_queue_selector.py` | Test | Remove local MockGalaxy |
| `tests/integration/ui/build_queue_screen/test_portrait_logging.py` | Test | Remove local MockGalaxy |
| `tests/integration/ui/build_queue_screen/test_basics.py` | Test | Remove local MockGalaxy |
| `tests/integration/strategy/production/conftest.py` | Test infra | Canonical `create_shipyard()`; may enhance |
| `tests/integration/strategy/production/test_completion.py` | Test | Remove local `_make_shipyard()`, use conftest |
| `tests/integration/strategy/production/test_queue.py` | Test | Remove local `_make_shipyard()`, use conftest |
| `tests/unit/strategy/production_engine/conftest.py` | Test infra | New or updated: shared `make_shipyard()` for unit tests |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | Test | Remove local `_make_shipyard()`, use conftest |
| `tests/unit/strategy/production_engine/test_spawning.py` | Test | Remove local `_make_shipyard()`, use conftest |
| `tests/unit/strategy/save_game_service/conftest.py` | Test infra | Canonical `MockGameSession` (already there) |
| `tests/unit/strategy/save_game_service/test_save_load_ops.py` | Test | Remove duplicate `MockGameSession` |
| `tests/unit/strategy/save_game_service/test_error_handling.py` | Test | Remove duplicate `MockGameSession` |

### Phase 2: Colonize Validator Refactor

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/validation/test_colonize_validator.py` | Test | Refactor: extract fixtures, remove duplication, reduce ~1247 to ~700 LOC |

### Phase 3: Relocate Misplaced Test Files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/entities/test_ship_theme_logic.py` | Test | Move to `tests/unit/ui/test_ship_theme_logic.py` |
| `tests/integration/strategy/test_hex_math_strategy.py` | Test | Move to `tests/unit/core/` (or deleted by PROJ-263) |
| `tests/unit/combat/test_battle_setup_logic.py` | Test | Move to `tests/unit/ui/screens/test_battle_setup_logic.py` |
| `tests/integration/strategy/facade/test_empire_dto.py` | Test | Move to `tests/unit/strategy/facade/test_empire_dto.py` |
| `tests/integration/strategy/facade/test_fleet_dto.py` | Test | Move to `tests/unit/strategy/facade/test_fleet_dto.py` |
| `tests/integration/strategy/facade/test_system_dto.py` | Test | Move to `tests/unit/strategy/facade/test_system_dto.py` |

## Conflict Notes

- **Phase 1 and Phase 2 are independent.** They touch completely different files and can run in parallel.
- **Phase 3 is independent** of Phases 1 and 2 (file moves, not content changes).
- **PROJ-263 overlap:** Phase 1 touches `test_colonize_logic.py` (remove helper) and Phase 3 touches `test_hex_math_strategy.py` (relocate). PROJ-263 may delete both files. Check at execution time.
- **PROJ-263 Phase 3 overlap:** PROJ-263 may modify `test_planet_specific_colonization.py` and `test_colonize_logic.py` as part of colonization duplicate cleanup. Coordinate if both projects are active simultaneously.
- **No production code is modified in any phase.** All changes are test infrastructure only.
