# PROJ-67 Phase 3: Fleet Production Engine

**Objective:** Extend ProductionEngine to process fleet build queues. Built ships join the building fleet.

## Completion Criteria
- [ ] All tasks below checked off
- [ ] `pytest tests/unit/strategy/production_engine/` passes
- [ ] `pytest tests/unit/strategy/turn_engine/` passes
- [ ] `pytest tests/ --testmon` passes (no regressions)

---

## Task 3.1: Add Fleet Production Processing [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] Add `process_fleet_production()` method to ProductionEngine
- [ ] Iterate empires → fleets → fleets with BUILD order and non-empty construction_queue
- [ ] For each fleet: same queue processing as planets (decrement turns, spawn on completion)
- [ ] Shipyard check: fleet must still have space_shipyard (not destroyed mid-build)
- [ ] Write test: fleet with BUILD order and queue item gets turns decremented
- [ ] Write test: fleet without BUILD order is skipped
- [ ] Write test: fleet without shipyard pauses production

**Notes:**

---

## Task 3.2: Fleet Ship Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] Add `_spawn_fleet_ship()` method
- [ ] Create ShipInstance from design (same as `_spawn_ship` pattern)
- [ ] Add ship to building fleet via `fleet.add_ship_instance()`
- [ ] Increment design's times_built counter
- [ ] Write test: completed ship joins the building fleet
- [ ] Write test: fleet speed recalculates after ship added

**Notes:**

---

## Task 3.3: Fleet Complex Spawning [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] Add `_spawn_fleet_complex()` method
- [ ] Validate fleet is still at planet hex (galaxy lookup)
- [ ] If valid: create PlanetaryFacility and add to planet.facilities (same as `_spawn_complex`)
- [ ] If not valid (fleet moved): log warning, skip (item already removed from queue)
- [ ] Write test: complex spawns to planet when fleet is at planet hex
- [ ] Write test: complex spawn fails gracefully when fleet not at planet

**Notes:**

---

## Task 3.4: Integrate Fleet Production into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [ ] Call `self.production_engine.process_fleet_production()` after `process_production()` in `process_turn()` (line ~201)
- [ ] Pass `empires`, `galaxy`, `save_path` parameters
- [ ] Write test: turn processing includes fleet production phase

**Notes:**

---

## Task 3.5: Update IProductionEngine Interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** N/A (interface only)

- [ ] Add `process_fleet_production()` to `IProductionEngine` interface
- [ ] Match signature: `(self, empires: List, galaxy: Any = None, save_path: Optional[str] = None) -> None`

**Notes:**
