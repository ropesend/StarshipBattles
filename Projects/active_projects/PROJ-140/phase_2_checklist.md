# Phase 2: Fix "Any Planet" Validation (Bug 5)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-140 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** When target is "Any Planet", validate that fleet has a pod matching at least one candidate. Select a candidate that matches available pods.

---

## Tasks

### Task 2.1: Write Tests for "Any Planet" Pod Validation [Simple]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py` (ADD to existing file)
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

Add new test class `TestColonizeValidatorAnyPlanetPods`:
- [x] Test: `test_any_planet_with_registry_no_matching_pod_fails` — Fleet with CONTINENTAL pod, only ICE_DWARF planets at location. `component_registry` provided. Assert `is_valid is False`, `error_code == "NO_COLONY_POD"`
- [x] Test: `test_any_planet_with_registry_matching_pod_succeeds` — Fleet with ICE_DWARF pod, ICE_DWARF planet at location. `component_registry` provided. Assert `is_valid is True`
- [x] Test: `test_any_planet_without_registry_skips_pod_check` — No `component_registry`. Assert `is_valid is True` (backward compat)
- [x] Test: `test_any_planet_with_registry_exhausted_pods_fails` — Fleet with ICE_DWARF pod already committed to COLONIZE order. Another ICE_DWARF at location. Assert `is_valid is False`, `error_code == "COLONY_POD_EXHAUSTED"` or `"NO_COLONY_POD"`
- [x] Verify: New tests fail initially (TDD)

**Notes:** All 4 tests added to TestColonizeValidatorAnyPlanetPods class.

### Task 2.2: Write Tests for "Any Planet" Execution Selection [Simple]
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py` (ADD to existing)
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

Add new test class `TestProcessColonizeAnyPlanet`:
- [x] Test: `test_any_planet_selects_matching_pod_planet` — Fleet with ICE_DWARF pod at location with [CONTINENTAL, ICE_DWARF] planets. Assert ICE_DWARF planet is colonized (not CONTINENTAL)
- [x] Test: `test_any_planet_no_matching_pod_fails` — Fleet with CONTINENTAL pod at location with only ICE_DWARF planets. `component_registry` provided. Assert `result.colonized is False`
- [x] Verify: New tests fail initially (TDD)

**Notes:** All 2 tests added to TestProcessColonizeAnyPlanet class.

### Task 2.3: Fix Validator "Any Planet" Path [Simple]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

Modify lines 85-89 (`if target_planet is None:` block):
- [x] After `if not valid_candidates:` check, when `component_registry is not None`:
  - Get available pods: `available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)`
  - Get committed pods: `committed = ColonizeValidator.get_committed_colony_pods(fleet)`
  - Check if ANY candidate planet matches an available uncommitted pod
  - If no match: return `ValidationResult(is_valid=False, errors=["No matching colony pod for any planet at this location."], error_code="NO_COLONY_POD")`
- [x] Verify: Validator "any planet" tests pass
- [x] Verify: `pytest tests/unit/strategy/validation/test_colonize_validator.py -v` — all existing tests still pass (30 passed)

**Notes:** Added pod-matching logic to "Any Planet" validation path with skip_chain_check support.

### Task 2.4: Fix `process_colonize()` "Any Planet" Selection [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py tests/integration/colonization/ -v`

Modify the "Any" case (lines 200-206):
- [x] When `target_planet is None` and `component_registry is not None`:
  - Iterate `valid_candidates` and pick first one that matches an available pod via `ColonizeValidator.find_ship_with_colony_pod()`
  - If no candidate matches, `fleet.pop_order()` and return `ColonizeResult(colonized=False)`
- [x] When `target_planet is None` and `component_registry is None` (legacy): keep existing `valid_candidates[0]` behavior
- [x] Verify: All "Any Planet" tests pass
- [x] Verify: `pytest tests/integration/colonization/ -v` — all existing tests pass (36 passed)

**Notes:** Added pod-matching planet selection to process_colonize(). Also updated test_commands.py to include proper fleet.ships mock.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
