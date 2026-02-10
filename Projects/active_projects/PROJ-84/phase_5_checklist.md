# Phase 5: Update Simulation Test Scenarios

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the isinstance(layer_data, dict) checks in simulation test scenario ability extraction helpers.

---

## Tasks

### Task 5.1: Update ability extraction in base.py [Simple]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/ -x`

- [ ] Line ~689: Remove `isinstance(layer_data, dict) and 'components' in layer_data` guard
- [ ] Replace with direct `layer_data.components` access (LayerData always has components)
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.2: Update ability extraction in beam_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_beam*.py -x`

- [ ] Line ~123: Remove `isinstance(layer_data, dict) and 'components' in layer_data` guard
- [ ] Replace with direct `layer_data.components` access
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.3: Update ability extraction in modifier_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/modifier_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_modifier*.py -x`

- [ ] Line ~50: Remove isinstance guard in beam weapon extraction
- [ ] Line ~62: Remove isinstance guard in combat propulsion extraction
- [ ] Replace with direct `layer_data.components` access
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.4: Update ability extraction in defense_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/defense_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_defense*.py -x`

- [ ] Line ~397: Remove isinstance guard
- [ ] Replace with direct `layer_data.components` access
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.5: Update ability extraction in seeker_scenarios.py [Simple]
**File:** `simulation_tests/scenarios/seeker_scenarios.py`
**Tests:** `pytest simulation_tests/tests/test_seeker*.py -x`

- [ ] Line ~35: Remove isinstance guard
- [ ] Replace with direct `layer_data.components` access
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.6: Full simulation test run [Simple]
**Tests:** `pytest simulation_tests/ -x`

- [ ] Run all simulation tests
- [ ] Fix any failures
- [ ] Verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
