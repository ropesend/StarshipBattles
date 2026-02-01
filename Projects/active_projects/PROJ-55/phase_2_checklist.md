# Phase 2: Enhance Validation Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add pod detection and chain validation to colonization validator

---

## Tasks

### Task 2.1: Add Pod Detection Methods [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [ ] Add import at top: `from game.simulation.components.abilities import ColonizePlanet` (if not already present)
- [ ] Add static method `find_ship_with_colony_pod(fleet, planet_type_str: str) -> Optional[Any]`:
  - Iterate through `fleet.ships`
  - For each ship, iterate through `ship.get_all_components()`
  - Get `component.get_ability('ColonizePlanet')`
  - If ability exists and `ability.planet_type == planet_type_str`, return ship
  - Return None if not found
- [ ] Add static method `get_available_colony_pods(fleet) -> Dict[str, int]`:
  - Initialize empty dict `pod_counts = {}`
  - Iterate fleet.ships → components → ColonizePlanet abilities
  - Count pods by planet type: `pod_counts[ability.planet_type] = pod_counts.get(..., 0) + 1`
  - Return pod_counts dict
- [ ] Add static method `get_committed_colony_pods(fleet) -> Dict[str, int]`:
  - Initialize empty dict `committed = {}`
  - Iterate through `fleet.orders`
  - For COLONIZE orders with target: count `order.target.planet_type.name`
  - Return committed dict
- [ ] Verify: Methods compile, no syntax errors

**Notes:**

---

### Task 2.2: Modify validate() Method for Pod Checking [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py::test_validate_no_colony_pod -v`

- [ ] Find `validate(galaxy, fleet, target_planet)` method (around line 30-80)
- [ ] After existing location/ownership checks, add pod validation block:
  ```python
  # Check for colony pod (if target specified)
  if target_planet is not None:
      planet_type_str = target_planet.planet_type.name
      ship_with_pod = ColonizeValidator.find_ship_with_colony_pod(fleet, planet_type_str)

      if ship_with_pod is None:
          return ValidationResult(
              success=False,
              error_code="NO_COLONY_POD",
              message=f"No ship in fleet has {planet_type_str} colony pod"
          )
  ```
- [ ] Add chain limit validation block:
  ```python
  # Check chain limits
  if target_planet is not None:
      planet_type_str = target_planet.planet_type.name
      available = ColonizeValidator.get_available_colony_pods(fleet)
      committed = ColonizeValidator.get_committed_colony_pods(fleet)

      available_count = available.get(planet_type_str, 0)
      committed_count = committed.get(planet_type_str, 0)

      if committed_count >= available_count:
          return ValidationResult(
              success=False,
              error_code="COLONY_POD_EXHAUSTED",
              message=f"All {planet_type_str} colony pods already assigned"
          )
  ```
- [ ] Verify: Code compiles, logic flows correctly

**Notes:** Place pod validation AFTER location/ownership checks (fail fast on common errors first)

---

### Task 2.3: Update Validation Tests [Medium]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [ ] Add test: `test_validate_requires_matching_colony_pod()`
  - Create fleet with ship that has Continental colony pod
  - Create Ice Dwarf planet at fleet location
  - Call `validate(galaxy, fleet, planet)`
  - Assert: `result.success == False`, `result.error_code == "NO_COLONY_POD"`
- [ ] Add test: `test_validate_accepts_matching_colony_pod()`
  - Create fleet with ship that has Ice Dwarf colony pod
  - Create Ice Dwarf planet at fleet location, unowned
  - Call `validate(galaxy, fleet, planet)`
  - Assert: `result.success == True`
- [ ] Add test: `test_get_available_colony_pods()`
  - Create fleet with 2 ships: one with Ice Dwarf pod, one with Continental pod
  - Call `get_available_colony_pods(fleet)`
  - Assert: Returns `{"ICE_DWARF": 1, "CONTINENTAL": 1}`
- [ ] Add test: `test_get_committed_colony_pods()`
  - Create fleet with 2 COLONIZE orders (both Ice Dwarf planets)
  - Call `get_committed_colony_pods(fleet)`
  - Assert: Returns `{"ICE_DWARF": 2}`
- [ ] Add test: `test_validate_rejects_overcommitted_pods()`
  - Create fleet with 1 Ice Dwarf pod
  - Add 1 COLONIZE order to fleet (Ice Dwarf planet)
  - Try to validate 2nd Ice Dwarf colonization
  - Assert: `result.error_code == "COLONY_POD_EXHAUSTED"`
- [ ] Run tests: `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`
- [ ] Verify: All new tests pass, no regressions

**Notes:** Will need to update existing tests that assume any fleet can colonize

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/validation/ -v` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
