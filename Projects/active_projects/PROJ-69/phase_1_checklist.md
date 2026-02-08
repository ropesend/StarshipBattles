# Phase 1: Data Model - Facility Queues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Give each shipyard facility its own construction queue and create the BuildQueueSource abstraction for discovering queues at a hex.

---

## Tasks

### Task 1.1: Add construction_queue to PlanetaryFacility [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/ -k "planet or facility"`

- [ ] Add `construction_queue: List[Dict[str, Any]] = field(default_factory=list)` to `PlanetaryFacility` dataclass (after line 30, before `is_operational`)
- [ ] Add import `from typing import Dict, List, Optional, Any` is already present (line 3) - verify `List` and `Dict` are imported
- [ ] Update `Planet.to_dict()` facility serialization (line 239-247) to include `'construction_queue': f.construction_queue` in the facility dict
- [ ] Update `Planet.from_dict()` facility deserialization (around line 280+) to load `construction_queue` from saved data with default `[]`
- [ ] Write unit test: PlanetaryFacility with queue items serializes correctly via Planet.to_dict()
- [ ] Write unit test: Planet.from_dict() correctly restores facility construction_queue
- [ ] Write unit test: PlanetaryFacility defaults to empty queue when not specified
- [ ] Verify: run `pytest tests/unit/strategy/ -n 4` - all pass

**Notes:**

---

### Task 1.2: Create BuildQueueSource dataclass and collector [Medium]
**File:** `game/strategy/data/build_queue_source.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Create new file `game/strategy/data/build_queue_source.py`
- [ ] Define `BuildQueueSource` dataclass with fields:
  - `queue_id: str` - Unique ID (facility `instance_id`, `f"planet_{id}_base"`, or `f"fleet_{id}"`)
  - `display_name: str` - Auto-generated display name
  - `owner_entity: Any` - Reference to Planet or Fleet
  - `construction_queue: List[Dict[str, Any]]` - Reference to actual queue list
  - `can_build_ships: bool` - Whether ships/fighters/satellites can be queued
  - `can_build_complexes: bool` - Whether complexes can be queued
  - `context_type: str` - "planet" or "fleet"
- [ ] Create helper `_facility_is_shipyard(facility: PlanetaryFacility) -> bool`:
  - Reuse same logic as `Planet.has_space_shipyard` (planet.py:147-165)
  - Check `design_data` layers for component `id == "space_shipyard"` or ability `"SpaceShipyard"`
- [ ] Create `collect_build_queues_at_hex(hex_coord, galaxy, empire) -> List[BuildQueueSource]`:
  - Get planets via `galaxy.get_planets_at_global_hex(hex_coord)`
  - Filter by `planet.owner_id == empire.id`
  - For each planet: create base queue source (complexes only, `construction_queue=planet.construction_queue`)
  - For each planet: iterate `planet.facilities`, find operational shipyards via `_facility_is_shipyard()`, create queue source per shipyard (`construction_queue=facility.construction_queue`, can build ships+complexes)
  - For each fleet in `empire.fleets` where `fleet.location == hex_coord` and `fleet.has_space_shipyard`: create queue source (`construction_queue=fleet.construction_queue`, can build ships+complexes)
  - Return list of all sources
- [ ] Write unit test: `collect_build_queues_at_hex` with planet having 0 shipyards returns 1 source (base)
- [ ] Write unit test: planet with 2 shipyards returns 3 sources (base + 2 shipyard)
- [ ] Write unit test: fleet with space yard at same hex included in results
- [ ] Write unit test: planet owned by different empire excluded
- [ ] Write unit test: non-operational shipyard facility excluded
- [ ] Write unit test: `_facility_is_shipyard` correctly identifies shipyard facilities
- [ ] Verify: run `pytest tests/unit/strategy/data/test_build_queue_source.py` - all pass

**Notes:**

---

### Task 1.3: Verify Fleet serialization unchanged [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet"`

- [ ] Verify `fleet.to_dict()` (line 754) serializes `construction_queue` correctly (no changes expected)
- [ ] Verify `fleet.from_dict()` (line 819) deserializes `construction_queue` correctly (no changes expected)
- [ ] Run `pytest tests/unit/strategy/ -k "fleet"` - all pass
- [ ] Run `pytest tests/integration/strategy/production/test_fleet_save_load.py` - passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
