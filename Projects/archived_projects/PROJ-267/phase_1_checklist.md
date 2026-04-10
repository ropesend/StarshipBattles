# Phase 1: Consolidate Shared Helpers into Conftest Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-267 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate duplicate test helper definitions by consolidating into shared conftest files or helper modules.

---

## Task 1.1: Consolidate make_colony_ship helpers [Medium]
**Canonical location:** `tests/conftest.py` line 339 (`make_colony_ship_for_planet`)
**Tests:** `pytest tests/integration/colonization/ tests/integration/strategy/test_colonize_logic.py tests/unit/strategy/engine/test_colonize_mission_handler.py tests/unit/strategy/engine/test_process_colonize_validation.py -v`

Two naming variants exist: `make_colony_ship(name, owner_id, pod_type)` (simpler) and `make_colony_ship_for_planet(planet, owner_id)` (derives pod type from planet). The root conftest has the `_for_planet` variant.

**Step 1: Add both variants to root conftest (if needed)**
- [ ] Read `tests/conftest.py` lines 339-380 to understand the canonical `make_colony_ship_for_planet()`
- [ ] Determine if a simpler `make_colony_ship(name, owner_id, pod_type)` variant is also needed (some test files create ships without a planet object)
- [ ] If needed, add a `make_colony_ship(name, owner_id, pod_type)` function to root conftest that creates a ShipInstance with a specified pod type directly
- [ ] Verify: both functions are importable from tests at any level

**Step 2: Remove duplicate from `tests/integration/colonization/conftest.py`**
- [ ] Read `tests/integration/colonization/conftest.py` line 41-82
- [ ] Confirm it is identical (or functionally equivalent) to root conftest version
- [ ] Delete the `make_colony_ship_for_planet()` definition from this file
- [ ] Run `pytest tests/integration/colonization/ -v` -- all pass

**Step 3: Update `tests/integration/gameplay_loop/test_commands_colonization.py`**
- [ ] Read file to understand its `make_colony_ship_for_planet()` at line 18
- [ ] Delete the local definition
- [ ] Import from root conftest (or use pytest fixture if converted)
- [ ] Run `pytest tests/integration/gameplay_loop/test_commands_colonization.py -v` -- all pass

**Step 4: Update `tests/integration/colonization/test_planet_specific_colonization.py`**
- [ ] Read file to understand its `make_colony_ship()` at line 104
- [ ] Delete the local definition
- [ ] Import the canonical version (may need the simpler variant)
- [ ] Run `pytest tests/integration/colonization/test_planet_specific_colonization.py -v` -- all pass

**Step 5: Update `tests/integration/strategy/test_colonize_logic.py`**
- [ ] Check if this file still exists (PROJ-263 may have deleted it)
- [ ] If exists: read file, delete local `make_colony_ship()` at line 65, import canonical
- [ ] Run `pytest tests/integration/strategy/test_colonize_logic.py -v` -- all pass

**Step 6: Update `tests/integration/strategy/test_command_handlers.py`**
- [ ] Read file to understand its `make_colony_ship()` at line 13
- [ ] Delete local definition, import canonical version
- [ ] Run `pytest tests/integration/strategy/test_command_handlers.py -v` -- all pass

**Step 7: Update `tests/integration/strategy/facade/test_facade_integration.py`**
- [ ] Read file to understand its `make_colony_ship_for_planet()` at line 19
- [ ] Delete local definition, import from root conftest
- [ ] Run `pytest tests/integration/strategy/facade/test_facade_integration.py -v` -- all pass

**Step 8: Update `tests/unit/strategy/engine/test_colonize_mission_handler.py`**
- [ ] Read file to understand its `make_colony_ship()` at line 17
- [ ] Delete local definition, import canonical version
- [ ] Run `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py -v` -- all pass

**Step 9: Update `tests/unit/strategy/engine/test_process_colonize_validation.py`**
- [ ] Read file to understand its `make_colony_ship()` at line 84
- [ ] Delete local definition, import canonical version
- [ ] Run `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v` -- all pass

**Step 10: Run full colonization test suite**
- [ ] `pytest tests/integration/colonization/ tests/integration/strategy/test_colonize_logic.py tests/unit/strategy/engine/test_colonize_mission_handler.py tests/unit/strategy/engine/test_process_colonize_validation.py tests/unit/strategy/engine/test_process_colonize_cargo.py tests/integration/gameplay_loop/test_commands_colonization.py -v`
- [ ] All tests pass with zero local `make_colony_ship` definitions remaining

**Notes:**

---

## Task 1.2: Consolidate MockGalaxy/MockSystem/MockPlanet [Complex]
**Target:** Create `tests/helpers/mock_galaxy.py` with shared mock classes
**Tests:** Run all files that currently define MockGalaxy after each change

The MockGalaxy class appears in 20+ files with slight variations. A shared module with a configurable MockGalaxy is the cleanest approach.

**Step 1: Catalog all MockGalaxy variants**
- [ ] Read each MockGalaxy definition to understand what attributes/methods each test needs
- [ ] Document the superset of required attributes: `systems`, `get_planets_at_global_hex()`, `get_system_at_hex()`, `warp_lanes`, etc.
- [ ] Identify which MockSystem/MockPlanet definitions are also needed

**Step 2: Create shared mock module**
- [ ] Create `tests/helpers/__init__.py` (if directory doesn't exist)
- [ ] Create `tests/helpers/mock_galaxy.py` with:
  - `MockGalaxy` class supporting all required attributes with sensible defaults
  - `MockSystem` class with configurable planets and location
  - `MockPlanet` / `MockPlanetType` as needed
- [ ] Write a brief test or smoke check that the shared mocks work

**Step 3: Update colonization test files (highest duplication)**
- [ ] Update `tests/unit/strategy/engine/test_process_colonize_validation.py` -- replace local MockGalaxy/MockSystem (lines 55-64)
- [ ] Update `tests/unit/strategy/engine/test_process_colonize_cargo.py` -- replace local MockGalaxy/MockSystem (lines 73-80)
- [ ] Update `tests/integration/colonization/test_planet_specific_colonization.py` -- replace local MockGalaxy/MockSystem (lines 75-84)
- [ ] Update `tests/integration/strategy/test_colonize_logic.py` -- replace local MockGalaxy/MockSystem (lines 22-46) (if file still exists)
- [ ] Run: `pytest tests/unit/strategy/engine/test_process_colonize_validation.py tests/unit/strategy/engine/test_process_colonize_cargo.py tests/integration/colonization/ -v` -- all pass

**Step 4: Update strategy test files**
- [ ] Update `tests/integration/strategy/test_command_handlers.py` -- replace MockGalaxy (line 39)
- [ ] Update `tests/integration/strategy/test_path_projection.py` -- replace MockGalaxy/MockSystem (lines 8-14)
- [ ] Update `tests/integration/strategy/test_fleet_navigation_consistency.py` -- replace MockGalaxy (line 35)
- [ ] Update `tests/integration/strategy/test_economy_e2e.py` -- replace MockGalaxy (line 243)
- [ ] Update `tests/integration/strategy/test_resupply_system.py` -- replace MockGalaxy (line 98)
- [ ] Update `tests/integration/strategy/transfer/conftest.py` -- replace MockGalaxy/MockSystem (lines 130-139)
- [ ] Update `tests/integration/strategy/turn_engine/conftest.py` -- replace MockGalaxy (line 7)
- [ ] Update `tests/unit/strategy/engine/test_colonize_population.py` -- replace MockGalaxy (line 124)
- [ ] Run: `pytest tests/integration/strategy/ tests/unit/strategy/engine/ -v --testmon` -- all pass

**Step 5: Update UI build queue test files**
- [ ] Update `tests/integration/ui/build_queue_screen/conftest.py` -- replace MockGalaxy (line 14)
- [ ] Update `tests/integration/ui/test_build_queue_formatting.py` -- replace MockGalaxy (line 16)
- [ ] Update `tests/integration/ui/test_build_queue_drag_drop.py` -- replace MockGalaxy (line 11)
- [ ] Update `tests/integration/ui/build_queue_screen/test_queue_selector.py` -- replace MockGalaxy (line 22)
- [ ] Update `tests/integration/ui/build_queue_screen/test_portrait_logging.py` -- replace MockGalaxy (line 15)
- [ ] Update `tests/integration/ui/build_queue_screen/test_basics.py` -- replace MockGalaxy (line 13)
- [ ] Run: `pytest tests/integration/ui/ -v` -- all pass

**Step 6: Verify no remaining inline MockGalaxy definitions**
- [ ] Grep for `class MockGalaxy` across tests/ -- only `tests/helpers/mock_galaxy.py` should define it
- [ ] Exception: `tests/performance/benchmark_planet_list.py` may keep its own if it has unique needs

**Notes:**

---

## Task 1.3: Consolidate _make_shipyard helpers [Medium]
**Canonical location:** `tests/integration/strategy/production/conftest.py` line 120 (`create_shipyard`)
**Tests:** `pytest tests/integration/strategy/production/ tests/unit/strategy/production_engine/ -v`

The existing `create_shipyard()` in the production conftest is the canonical version. Five other files define their own `_make_shipyard()` variants.

**Step 1: Verify canonical create_shipyard() covers all use cases**
- [ ] Read `tests/integration/strategy/production/conftest.py` line 120+ to understand `create_shipyard()` signature and behavior
- [ ] Read each `_make_shipyard()` variant to compare signatures
- [ ] Note any differences (e.g., `construction_queue` parameter in `test_tick_consumption.py`)
- [ ] If `create_shipyard()` needs enhancement to cover all cases, enhance it

**Step 2: Update integration/strategy/production tests**
- [ ] Update `tests/integration/strategy/production/test_completion.py` -- delete `_make_shipyard()` at line 28, use `create_shipyard` fixture
- [ ] Update `tests/integration/strategy/production/test_queue.py` -- delete `_make_shipyard()` at line 29, use `create_shipyard` fixture
- [ ] Run: `pytest tests/integration/strategy/production/ -v` -- all pass

**Step 3: Add shared helper for unit tests**
- [ ] The unit tests in `tests/unit/strategy/production_engine/` cannot use the integration conftest fixture
- [ ] Create or update `tests/unit/strategy/production_engine/conftest.py` with a `make_shipyard()` helper
- [ ] Update `tests/unit/strategy/production_engine/test_tick_consumption.py` -- delete `_make_shipyard()` at line 79, use shared helper
- [ ] Update `tests/unit/strategy/production_engine/test_spawning.py` -- delete `_make_shipyard()` at line 14, use shared helper
- [ ] Run: `pytest tests/unit/strategy/production_engine/ -v` -- all pass

**Step 4: Evaluate remaining _make_shipyard_facility variants**
- [ ] Read `tests/unit/strategy/test_engine_event_emission.py` line 64 -- determine if it can use a shared helper
- [ ] Read `tests/unit/strategy/data/test_build_queue_source.py` line 65 -- determine if it can use a shared helper
- [ ] Read `tests/unit/strategy/data/test_facility_construction_queue.py` line 34 -- determine if it can use a shared helper
- [ ] Read `tests/integration/strategy/test_production_rates.py` line 25 -- determine if it can use a shared helper
- [ ] For each: either consolidate into shared helper or leave in place with a comment if it has unique requirements
- [ ] Run: `pytest tests/unit/strategy/ tests/integration/strategy/test_production_rates.py -v --testmon` -- all pass

**Notes:** The `_make_shipyard_facility()` variants may have different enough signatures (some take `queue`, some take `instance_id`, some take both) that full consolidation is not worth the complexity. If so, document the decision and move on.

---

## Task 1.4: Consolidate MockGameSession [Simple]
**Canonical location:** `tests/unit/strategy/save_game_service/conftest.py` line 12
**Tests:** `pytest tests/unit/strategy/save_game_service/ -v`

Three identical `MockGameSession` classes exist within the save_game_service test directory.

**Step 1: Remove duplicate from test_save_load_ops.py**
- [ ] Read `tests/unit/strategy/save_game_service/test_save_load_ops.py` lines 23-39
- [ ] Confirm it is identical to conftest version
- [ ] Delete the `MockGameSession` class from this file
- [ ] Verify it picks up the conftest version (pytest auto-imports conftest fixtures)
- [ ] Note: `MockGameSession` in conftest is a class, not a fixture -- test files may need `from .conftest import MockGameSession` or the conftest needs to provide it as a fixture
- [ ] Run: `pytest tests/unit/strategy/save_game_service/test_save_load_ops.py -v` -- all pass

**Step 2: Remove duplicate from test_error_handling.py**
- [ ] Read `tests/unit/strategy/save_game_service/test_error_handling.py` lines 23-39
- [ ] Confirm it is identical to conftest version
- [ ] Delete the `MockGameSession` class from this file
- [ ] Run: `pytest tests/unit/strategy/save_game_service/test_error_handling.py -v` -- all pass

**Step 3: Evaluate external MockGameSession copies**
- [ ] Read `tests/unit/ui/test_save_selection.py` line 15 -- compare with canonical
- [ ] Read `tests/unit/strategy/test_auto_save.py` line 15 -- compare with canonical
- [ ] If identical or nearly so: move to a shared helper or root conftest
- [ ] If materially different: leave in place with a comment explaining why
- [ ] Run all affected test files

**Notes:** The conftest MockGameSession is a regular class, not a pytest fixture. Test files in the same directory can import it directly since pytest adds conftest to the module namespace. If this doesn't work, convert it to a pytest fixture that returns an instance.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero duplicate `make_colony_ship` definitions (only root conftest canonical versions)
- [ ] Zero duplicate `MockGalaxy` class definitions (only `tests/helpers/mock_galaxy.py`)
- [ ] Zero duplicate `_make_shipyard` in production test files (use `create_shipyard` or shared conftest)
- [ ] Zero duplicate `MockGameSession` in save_game_service directory (only conftest version)
- [ ] `pytest tests/ -n 12` -- all tests pass, count unchanged
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
