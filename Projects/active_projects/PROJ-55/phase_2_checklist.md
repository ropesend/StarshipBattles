# Phase 2: Enhance Validation Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add pod detection and chain validation to colonization validator

---

## Tasks

### Task 2.1: Add Pod Detection Methods [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Add static method `find_ship_with_colony_pod(fleet, planet_type_str, component_registry)`:
  - Iterate through `fleet.ships`
  - For each ship, iterate through design_data['layers']
  - Look up component in registry and check for ColonizePlanet ability
  - If ability exists and matches planet_type_str, return ship
  - Return None if not found
- [x] Add static method `get_available_colony_pods(fleet, component_registry) -> Dict[str, int]`:
  - Initialize empty dict `pod_counts = {}`
  - Iterate fleet.ships → design_data['layers'] → component registry lookups
  - Count pods by planet type
  - Return pod_counts dict
- [x] Add static method `get_committed_colony_pods(fleet) -> Dict[str, int]`:
  - Initialize empty dict `committed = {}`
  - Iterate through `fleet.orders`
  - For COLONIZE orders with target: count `order.target.planet_type.name`
  - Return committed dict
- [x] Verify: Methods compile, no syntax errors

**Notes:** Implemented using design_data pattern consistent with ShipStatsCalculator. Used component_registry parameter for DI rather than global lookup.

---

### Task 2.2: Modify validate() Method for Pod Checking [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Modified `validate(galaxy, fleet, target_planet, component_registry=None)` to accept optional registry
- [x] After existing location/ownership checks, added pod validation block:
  - Check if fleet has a matching colony pod via find_ship_with_colony_pod()
  - Return NO_COLONY_POD error if not found
- [x] Added chain limit validation block:
  - Compare available_count vs committed_count
  - Return COLONY_POD_EXHAUSTED if committed >= available
- [x] Verify: Code compiles, logic flows correctly

**Notes:** Pod validation is optional (only when component_registry is provided). Backward compatible with existing callers.

---

### Task 2.3: Update Validation Tests [Medium]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Add test: `test_validate_requires_matching_colony_pod()` - validates NO_COLONY_POD error
- [x] Add test: `test_validate_accepts_matching_colony_pod()` - validates success with matching pod
- [x] Add test: `test_validate_no_colony_pod_at_all()` - validates NO_COLONY_POD when fleet has no pods
- [x] Add test: `test_get_available_colony_pods()` - counts available pods correctly
- [x] Add test: `test_get_available_colony_pods_multiple_same_type()` - counts multiple same-type pods
- [x] Add test: `test_get_committed_colony_pods()` - counts committed pods from orders
- [x] Add test: `test_validate_rejects_overcommitted_pods()` - validates COLONY_POD_EXHAUSTED error
- [x] Add test: `test_validate_allows_different_pod_types_independently()` - pod types tracked separately
- [x] Run tests: `pytest tests/unit/strategy/validation/test_colonize_validator.py -v` - all pass
- [x] Verify: All 22 tests pass (14 existing + 8 new), no regressions

**Notes:** Added TestColonizeValidatorColonyPods test class. All existing tests continue to pass (backward compatible).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/validation/ -v` - all tests pass (22 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
