# PROJ-67 Phase 3: Fleet Production Engine

**Objective:** Extend ProductionEngine to process fleet build queues. Built ships join the building fleet.

## Completion Criteria
- [x] All tasks below checked off
- [x] `pytest tests/unit/strategy/production_engine/` passes
- [x] `pytest tests/unit/strategy/turn_engine/` passes
- [x] `pytest tests/ --testmon` passes (no regressions)

---

## Task 3.1: Add Fleet Production Processing [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [x] Add `process_fleet_production()` method to ProductionEngine
- [x] Iterate empires → fleets → fleets with BUILD order and non-empty construction_queue
- [x] For each fleet: same queue processing as planets (decrement turns, spawn on completion)
- [x] Shipyard check: fleet must still have space_shipyard (not destroyed mid-build)
- [x] Write test: fleet with BUILD order and queue item gets turns decremented
- [x] Write test: fleet without BUILD order is skipped
- [x] Write test: fleet without shipyard pauses production

**Notes:** Added `process_fleet_production()` method following planet production pattern.

---

## Task 3.2: Fleet Ship Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [x] Add `_spawn_fleet_ship()` method
- [x] Create ShipInstance from design (same as `_spawn_ship` pattern)
- [x] Add ship to building fleet via `fleet.add_ship_instance()`
- [x] Increment design's times_built counter
- [x] Write test: completed ship joins the building fleet
- [x] Write test: fleet speed recalculates after ship added (implicit via add_ship_instance)

**Notes:** Ships join the fleet directly rather than creating new fleets.

---

## Task 3.3: Fleet Complex Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [x] Add `_spawn_fleet_complex()` method
- [x] Validate fleet is still at planet hex (galaxy lookup)
- [x] If valid: create PlanetaryFacility and add to planet.facilities (same as `_spawn_complex`)
- [x] If not valid (fleet moved): log warning, skip (item already removed from queue)
- [x] Write test: complex spawns to planet when fleet is at planet hex
- [x] Write test: complex spawn fails gracefully when fleet not at planet

**Notes:** Uses galaxy.get_planets_at_global_hex() for planet lookup.

---

## Task 3.4: Integrate Fleet Production into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [x] Call `self.production_engine.process_fleet_production()` after `process_production()` in `process_turn()` (line ~201)
- [x] Pass `empires`, `galaxy`, `save_path` parameters
- [x] Write test: turn processing includes fleet production phase

**Notes:** Added as Phase 4 in turn processing, after colony production (Phase 3).

---

## Task 3.5: Update IProductionEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [x] Add `process_fleet_production()` to `IProductionEngine` interface
- [x] Match signature: `(self, empires: List, galaxy: Any = None, save_path: Optional[str] = None) -> None`

**Notes:** Also updated MockProductionEngine in test mocks and inline test mocks.

---

## Phase 3 Summary

**Files Modified:**
- `game/strategy/engine/production_engine.py` - Added fleet production methods
- `game/strategy/engine/turn_engine.py` - Added fleet production call
- `game/strategy/interfaces/engines.py` - Added interface method

**Tests Added:**
- `tests/unit/strategy/production_engine/test_fleet_production.py` - 11 new tests
- `tests/unit/strategy/turn_engine/test_turn_processing.py` - 1 new test

**Mock Updates:**
- `tests/unit/strategy/mocks/mock_engines.py` - MockProductionEngine
- `tests/unit/strategy/turn_engine/conftest.py` - mock_fleet fixture
- `tests/unit/strategy/turn_engine/test_dependency_injection.py` - inline fleet mocks
- `tests/unit/strategy/interfaces/test_engine_interfaces.py` - inline MockProductionEngine

**Test Results:** 6361 passed, 2 pre-existing failures (bug_15 screenshot tests)
