# Phase 1: Fix Execution-Time Validation (Bugs 1 + 2)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure `process_colonize()` validates colony pod match at execution time AND fails gracefully when no match exists.

---

## Tasks

### Task 1.1: Write Tests for Execution-Time Validation [Simple]
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py` (NEW)
**Reuse fixtures from:** `tests/integration/colonization/test_planet_specific_colonization.py` (MockPlanet, MockGalaxy, MockSystem, make_colony_ship, make_combat_ship, component_registry)
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

- [ ] Create test file with fixtures (copy MockPlanet, MockGalaxy, MockSystem, make_colony_ship, make_combat_ship, component_registry from test_planet_specific_colonization.py)
- [ ] Test: `test_process_colonize_wrong_pod_type_fails` — Fleet with CONTINENTAL pod at ICE_DWARF planet, `component_registry` provided. Assert `result.colonized is False`, planet `owner_id` remains `None`
- [ ] Test: `test_process_colonize_correct_pod_type_succeeds` — Fleet with ICE_DWARF pod at ICE_DWARF planet, `component_registry` provided. Assert `result.colonized is True`
- [ ] Test: `test_process_colonize_no_matching_pod_does_not_consume_ship` — Fleet has ships but none with matching pod. Assert no ships removed from fleet
- [ ] Test: `test_process_colonize_no_matching_pod_pops_order` — Same scenario. Assert COLONIZE order was popped from queue
- [ ] Test: `test_process_colonize_legacy_without_registry_still_works` — No `component_registry` passed. Assert `result.colonized is True` (backward compat)
- [ ] Verify: All 5 tests fail initially (TDD — tests written before fix)

**Notes:**

### Task 1.2: Pass `component_registry` to Validator [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

- [ ] Line 194: Change `ColonizeValidator.validate(galaxy, fleet, target_planet)` to `ColonizeValidator.validate(galaxy, fleet, target_planet, component_registry)`
- [ ] Verify: Tests for wrong pod type now fail at validation (not at ship removal)

**Notes:**

### Task 1.3: Restructure `process_colonize()` to Pre-Check Ship [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py tests/integration/colonization/ -v`

Restructure lines 200-234 so colony ship is found BEFORE any mutation:
- [ ] After determining `final_planet` (lines 200-206), add pre-check block:
  ```python
  # Pre-check colony ship availability
  colony_ship = None
  if component_registry is not None:
      planet_type_str = final_planet.planet_type.name
      colony_ship = ColonizeValidator.find_ship_with_colony_pod(
          fleet, planet_type_str, component_registry
      )
      if colony_ship is None:
          log_warning(f"FleetOrderProcessor: No matching colony pod for {planet_type_str}")
          fleet.pop_order()
          return ColonizeResult(colonized=False)
  ```
- [ ] Keep `empire.add_colony(final_planet)` AFTER pre-check succeeds
- [ ] Keep `fleet.pop_order()` AFTER pre-check succeeds
- [ ] Keep `_transfer_founding_population()` call unchanged
- [ ] Replace old ship removal block (lines 215-232) with simplified:
  ```python
  if component_registry is not None and colony_ship is not None:
      fleet.remove_ship(colony_ship)
      log_debug(f"FleetOrderProcessor: Removed colony ship '{colony_ship.name}'")
      if len(fleet.ships) == 0:
          empire.remove_fleet(fleet)
          log_debug(f"FleetOrderProcessor: Fleet {fleet.id} removed (no ships remaining)")
  else:
      # Legacy behavior: remove entire fleet
      empire.remove_fleet(fleet)
  ```
- [ ] Verify: All new tests pass
- [ ] Verify: `pytest tests/integration/colonization/ -v` — all existing tests pass
- [ ] Verify: `pytest tests/unit/strategy/engine/test_colonize_population.py -v` — population tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
