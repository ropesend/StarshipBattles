# Phase 1: Data Model - Facility Queues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Give each shipyard facility its own construction queue and create the BuildQueueSource abstraction for discovering queues at a hex.

---

## Tasks

### Task 1.1: Add construction_queue to PlanetaryFacility [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/ -k "planet or facility"`

- [x] Add `construction_queue: List[Dict[str, Any]] = field(default_factory=list)` to `PlanetaryFacility` dataclass (after `is_operational`)
- [x] Add import `from typing import Dict, List, Optional, Any` is already present (line 3) - verify `List` and `Dict` are imported
- [x] Update `Planet.to_dict()` facility serialization to include `'construction_queue': list(f.construction_queue)` in the facility dict
- [x] Update `Planet.from_dict()` facility deserialization to load `construction_queue` from saved data with default `[]`
- [x] Write unit test: PlanetaryFacility with queue items serializes correctly via Planet.to_dict()
- [x] Write unit test: Planet.from_dict() correctly restores facility construction_queue
- [x] Write unit test: PlanetaryFacility defaults to empty queue when not specified
- [x] Verify: run `pytest tests/unit/strategy/data/test_facility_construction_queue.py` - 7 passed

**Notes:** Field placed after `is_operational` (both have defaults). Serialization uses `list()` for independent copy.

---

### Task 1.2: Create BuildQueueSource dataclass and collector [Medium]
**File:** `game/strategy/data/build_queue_source.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Create new file `game/strategy/data/build_queue_source.py`
- [x] Define `BuildQueueSource` dataclass with fields:
  - `queue_id: str` - Unique ID (facility `instance_id`, `f"planet_{id}_base"`, or `f"fleet_{id}"`)
  - `display_name: str` - Auto-generated display name
  - `owner_entity: Any` - Reference to Planet or Fleet
  - `construction_queue: List[Dict[str, Any]]` - Reference to actual queue list
  - `can_build_ships: bool` - Whether ships/fighters/satellites can be queued
  - `can_build_complexes: bool` - Whether complexes can be queued
  - `context_type: str` - "planet" or "fleet"
- [x] Create helper `_facility_is_shipyard(facility: PlanetaryFacility) -> bool`:
  - Reuse same logic as `Planet.has_space_shipyard` (planet.py:147-165)
  - Check `design_data` layers for component `id == "space_shipyard"` or ability `"SpaceShipyard"`
  - Also checks `is_operational` flag
- [x] Create `collect_build_queues_at_hex(hex_coord, galaxy, empire) -> List[BuildQueueSource]`:
  - Get planets via `galaxy.get_planets_at_global_hex(hex_coord)`
  - Filter by `planet.owner_id == empire.id`
  - For each planet: create base queue source (complexes only)
  - For each planet: iterate facilities, find operational shipyards, create queue source per shipyard
  - For each fleet at hex with space yard: create queue source
  - Return list of all sources
- [x] Write unit test: `collect_build_queues_at_hex` with planet having 0 shipyards returns 1 source (base)
- [x] Write unit test: planet with 2 shipyards returns 3 sources (base + 2 shipyard)
- [x] Write unit test: fleet with space yard at same hex included in results
- [x] Write unit test: planet owned by different empire excluded
- [x] Write unit test: non-operational shipyard facility excluded
- [x] Write unit test: `_facility_is_shipyard` correctly identifies shipyard facilities
- [x] Verify: run `pytest tests/unit/strategy/data/test_build_queue_source.py` - 15 passed

**Notes:** Also added tests for: fleet without yard excluded, fleet at different hex excluded, empty hex, queue references shared, mixed facilities.

---

### Task 1.3: Verify Fleet serialization unchanged [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet"`

- [x] Verify `fleet.to_dict()` serializes `construction_queue` correctly (no changes needed)
- [x] Verify `fleet.from_dict()` deserializes `construction_queue` correctly (no changes needed)
- [x] Run `pytest tests/unit/strategy/fleet/` - 99 passed
- [x] Run `pytest tests/integration/strategy/production/test_fleet_save_load.py` - 6 passed

**Notes:** No changes to fleet.py required. All fleet serialization tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - 6518 passed, 1 pre-existing failure (IFleet mock spec)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
