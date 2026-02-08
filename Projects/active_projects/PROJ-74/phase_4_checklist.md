# Phase 4: Fleet Resupply Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement fuel transfer from facilities to fleets with range equalization

---

## Tasks

### Task 4.1: Write TDD tests for fleet resupply [Medium]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py -k fleet`

- [ ] Write `test_fleet_at_planet_receives_fuel`:
  - Create fleet at same location as planet with fuel facility
  - Process resupply
  - Verify fleet ships have more fuel

- [ ] Write `test_fleet_not_at_planet_no_fuel`:
  - Create fleet at different location than planet
  - Process resupply
  - Verify fleet ships unchanged

- [ ] Write `test_owner_fleet_priority_over_others`:
  - Create planet owned by empire A
  - Create fleet from empire A and fleet from empire B at same location
  - Process resupply
  - Verify empire A fleet gets fuel, empire B does not

- [ ] Write `test_fuel_distributed_to_equalize_range`:
  - Create fleet with ships of different fuel capacities and consumption rates
  - Process resupply
  - Verify all ships have same effective range

- [ ] Write `test_tanker_ships_partially_fueled`:
  - Create fleet with "tanker" ship (high capacity, low consumption)
  - Process resupply with limited fuel
  - Verify tanker is partially fueled while combat ships are full

- [ ] Write `test_facility_with_no_fuel_no_transfer`:
  - Create facility with empty fuel storage
  - Process resupply
  - Verify no fuel transferred

- [ ] Verify: All new tests fail (TDD red phase)

**Notes:**

---

### Task 4.2: Implement fleet resupply in ResupplyEngine [Complex]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Implement `process_fleet_resupply(self, tick: int, empires, galaxy) -> List[ResupplyEvent]`:
  ```python
  def process_fleet_resupply(self, tick: int, empires, galaxy) -> List[ResupplyEvent]:
      events = []
      for empire in empires:
          for fleet in empire.fleets:
              # Get planets at fleet's location
              planets = galaxy.get_planets_at_global_hex(fleet.location)

              # Find owner's planet with fuel in facilities
              for planet in planets:
                  if planet.owner_id != fleet.owner_id:
                      continue  # Owner priority

                  for facility in planet.facilities:
                      if not facility.is_operational:
                          continue

                      available = facility.get_fuel_storage()
                      if available <= 0:
                          continue

                      # Calculate distribution
                      distribution = self._calculate_fuel_distribution(fleet, available)

                      # Transfer fuel
                      total_transferred = 0.0
                      for ship, amount in distribution.items():
                          actual = min(amount, available - total_transferred)
                          if actual > 0:
                              ship.resupply('fuel', actual)
                              total_transferred += actual

                      # Withdraw from facility
                      facility.withdraw_fuel(total_transferred)

                      if total_transferred > 0:
                          events.append(ResupplyEvent(
                              facility_name=facility.name,
                              fuel_generated=0,
                              fuel_transferred=total_transferred,
                              fleet_id=fleet.id
                          ))

      return events
  ```

- [ ] Implement `_calculate_fuel_distribution(self, fleet, available_fuel) -> Dict`:
  ```python
  def _calculate_fuel_distribution(self, fleet, available_fuel):
      """Distribute fuel to equalize range across all ships."""
      ships = [s for s in fleet.ships if s.is_combat_capable()]
      if not ships:
          return {}

      # Calculate fleet's total fuel cost per hex
      total_cost_per_hex = sum(s.get_fuel_cost_per_hex() for s in ships)
      if total_cost_per_hex <= 0:
          return {}

      # Calculate max range with available + current fuel
      current_total = sum(s.get_current_fuel() for s in ships)
      max_range = (available_fuel + current_total) / total_cost_per_hex

      # Each ship gets fuel for max_range hexes (capped at capacity)
      distribution = {}
      for ship in ships:
          target = ship.get_fuel_cost_per_hex() * max_range
          target = min(target, ship.get_fuel_capacity())
          deficit = target - ship.get_current_fuel()
          distribution[ship] = max(0, deficit)

      return distribution
  ```

- [ ] Verify: All tests from Task 4.1 pass (TDD green phase)

**Notes:**

---

### Task 4.3: Add owner priority logic [Simple]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py -k priority`

- [ ] Verify owner check is in place: `if planet.owner_id != fleet.owner_id: continue`
- [ ] Consider future extension: Allied fleets after owner (add TODO comment)
- [ ] Verify: Priority tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
