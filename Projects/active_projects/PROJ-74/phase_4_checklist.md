# Phase 4: Fleet Resupply Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement fuel transfer from facilities to fleets with range equalization

---

## Tasks

### Task 4.1: Write TDD tests for fleet resupply [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py -k fleet`

- [x] Write `test_fleet_at_planet_receives_fuel`:
  - Create fleet at same location as planet with fuel facility
  - Process resupply
  - Verify fleet ships have more fuel

- [x] Write `test_fleet_not_at_planet_no_fuel`:
  - Create fleet at different location than planet
  - Process resupply
  - Verify fleet ships unchanged

- [x] Write `test_owner_fleet_priority_over_others`:
  - Create planet owned by empire A
  - Create fleet from empire A and fleet from empire B at same location
  - Process resupply
  - Verify empire A fleet gets fuel, empire B does not

- [x] Write `test_fuel_distributed_to_equalize_range`:
  - Create fleet with ships of different fuel capacities and consumption rates
  - Process resupply
  - Verify all ships have same effective range

- [x] Write `test_tanker_ships_partially_fueled`:
  - Create fleet with "tanker" ship (high capacity, low consumption)
  - Process resupply with limited fuel
  - Verify tanker is partially fueled while combat ships are full

- [x] Write `test_facility_with_no_fuel_no_transfer`:
  - Create facility with empty fuel storage
  - Process resupply
  - Verify no fuel transferred

- [x] Verify: All new tests fail (TDD red phase)

**Notes:** 4 tests failed in red phase (2 passed because placeholder returns [] which is correct for "no fuel" and "not at planet" cases). All 6 pass in green phase.

---

### Task 4.2: Implement fleet resupply in ResupplyEngine [Complex]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [x] Implement `process_fleet_resupply(self, tick: int, empires, galaxy) -> List[ResupplyEvent]`
- [x] Implement `_calculate_fuel_distribution(self, fleet, available_fuel) -> Dict`
- [x] Implement `_transfer_fuel(self, distribution, available, facility) -> float` (extracted helper)
- [x] Verify: All tests from Task 4.1 pass (TDD green phase)

**Notes:** Used `ship.get_resource_capacity('fuel')` instead of checklist's `ship.get_fuel_capacity()` (which doesn't exist). Extracted `_transfer_fuel` as a clean helper method for fuel transfer execution.

---

### Task 4.3: Add owner priority logic [Simple]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py -k priority`

- [x] Verify owner check is in place: `if planet.owner_id != fleet.owner_id: continue`
- [x] Owner priority built into main process_fleet_resupply loop (no allied resupply)
- [x] Verify: Priority tests pass

**Notes:** Allied fleet resupply is documented as out of scope in plan.md. No TODO comment added per project convention (minimize TODOs).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - 6849 passed (1 pre-existing failure in test_protocols.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
