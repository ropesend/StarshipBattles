# Phase 1: Fix Execution-Time Validation (Bugs 1 + 2)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Ensure `process_colonize()` validates colony pod match at execution time AND fails gracefully when no match exists.

---

## Tasks

### Task 1.1: Write Tests for Execution-Time Validation [Simple]
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py` (NEW)
**Reuse fixtures from:** `tests/integration/colonization/test_planet_specific_colonization.py` (MockPlanet, MockGalaxy, MockSystem, make_colony_ship, make_combat_ship, component_registry)
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

- [x] Create test file with fixtures (copy MockPlanet, MockGalaxy, MockSystem, make_colony_ship, make_combat_ship, component_registry from test_planet_specific_colonization.py)
- [x] Test: `test_process_colonize_wrong_pod_type_fails` — Fleet with CONTINENTAL pod at ICE_DWARF planet, `component_registry` provided. Assert `result.colonized is False`, planet `owner_id` remains `None`
- [x] Test: `test_process_colonize_correct_pod_type_succeeds` — Fleet with ICE_DWARF pod at ICE_DWARF planet, `component_registry` provided. Assert `result.colonized is True`
- [x] Test: `test_process_colonize_no_matching_pod_does_not_consume_ship` — Fleet has ships but none with matching pod. Assert no ships removed from fleet
- [x] Test: `test_process_colonize_no_matching_pod_pops_order` — Same scenario. Assert COLONIZE order was popped from queue
- [x] Test: `test_process_colonize_legacy_without_registry_still_works` — No `component_registry` passed. Assert `result.colonized is True` (backward compat)
- [x] Verify: All 5 tests fail initially (TDD — tests written before fix)

**Notes:** 5 tests created. `test_process_colonize_wrong_pod_type_fails` failed as expected (Bug 1 confirmed).

### Task 1.2: Pass `component_registry` to Validator [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

- [x] Line 194: Change `ColonizeValidator.validate(galaxy, fleet, target_planet)` to `ColonizeValidator.validate(galaxy, fleet, target_planet, component_registry)`
- [x] Verify: Tests for wrong pod type now fail at validation (not at ship removal)

**Notes:** Added `skip_chain_check=True` parameter to validator call for execution-time validation (vs pre-queue validation). Updated ColonizeValidator.validate() to support this parameter.

### Task 1.3: Restructure `process_colonize()` to Pre-Check Ship [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py tests/integration/colonization/ -v`

Restructure lines 200-234 so colony ship is found BEFORE any mutation:
- [x] After determining `final_planet` (lines 200-206), add pre-check block
- [x] Keep `empire.add_colony(final_planet)` AFTER pre-check succeeds
- [x] Keep `fleet.pop_order()` AFTER pre-check succeeds
- [x] Keep `_transfer_founding_population()` call unchanged
- [x] Simplified ship removal block using pre-checked colony_ship
- [x] Verify: All new tests pass
- [x] Verify: `pytest tests/integration/colonization/ -v` — all existing tests pass
- [x] Verify: `pytest tests/unit/strategy/engine/test_colonize_population.py -v` — population tests pass

**Notes:** Also updated test fixtures in:
- `tests/conftest.py`: Added `make_colony_ship_for_planet()` helper
- `tests/integration/colonization/test_edge_cases.py`: Use proper colony ships
- `tests/integration/colonization/test_execution.py`: Use proper colony ships
- `tests/integration/strategy/test_colonize_logic.py`: Use proper planet types and colony ships
- `tests/integration/strategy/turn_engine/conftest.py`: Added `create_colony_ship()` and `MockPlanetType`
- `tests/integration/strategy/turn_engine/test_basics.py`: Use proper colony ships

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
