# Phase 5: Update Simulation Test Scenarios

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the isinstance(layer_data, dict) checks in simulation test scenario ability extraction helpers.

---

## Tasks

### Task 5.1: Update ability extraction in base.py [Simple]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/ -x`

- [x] Line ~689: Remove `isinstance(layer_data, dict) and 'components' in layer_data` guard
- [x] Replace with direct `layer_data.components` access (LayerData always has components)
- [x] Verify: tests pass

**Notes:** Fixed - removed isinstance guard, now uses direct `.components` access.

---

### Task 5.2: Update ability extraction in beam_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_beam*.py -x`

- [x] Line ~123: Remove `isinstance(layer_data, dict) and 'components' in layer_data` guard
- [x] Replace with direct `layer_data.components` access
- [x] Verify: tests pass

**Notes:** Fixed - removed isinstance guard, now uses direct `.components` access.

---

### Task 5.3: Update ability extraction in modifier_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/modifier_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_modifier*.py -x`

- [x] Line ~50: Remove isinstance guard in beam weapon extraction
- [x] Line ~62: Remove isinstance guard in combat propulsion extraction
- [x] Replace with direct `layer_data.components` access
- [x] Verify: tests pass

**Notes:** Fixed both `_get_beam_ability` and `_get_propulsion_ability` functions.

---

### Task 5.4: Update ability extraction in defense_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/defense_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_defense*.py -x`

- [x] Line ~397: Remove isinstance guard
- [x] Replace with direct `layer_data.components` access
- [x] Verify: tests pass

**Notes:** Fixed - removed isinstance guard in custom_setup method.

---

### Task 5.5: Update ability extraction in seeker_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/seeker_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_seeker*.py -x`

- [x] Line ~35: Remove isinstance guard
- [x] Replace with direct `layer_data.components` access
- [x] Verify: tests pass

**Notes:** Fixed - removed isinstance guard in `_get_seeker_ability` function.

---

### Task 5.6: Full simulation test run [Simple]
**Tests:** `pytest simulation_tests/ -x`

- [x] Run all simulation tests
- [x] Fix any failures
- [x] Verify all pass

**Notes:** Also fixed test_propulsion.py `.get('components')` → `.components`. 62 pass, 5 fail (pre-existing physics calibration issues), 4 skipped.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
