# Phase 2: Remove Legacy Constant Aliases

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-185 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove unused backward compat aliases in propulsion scenarios

---

## Tasks

### Task 2.1: Remove propulsion legacy aliases [Simple]
**File:** `simulation_tests/scenarios/propulsion_scenarios.py`
**Tests:** `pytest simulation_tests/ -n 12`

- [ ] Remove the entire legacy aliases block (lines 257-280), including section header comment:
  ```python
  # =============================================================================
  # LEGACY ALIASES (for backward compatibility during transition)
  # These are used by other scenarios until they are updated to use PROP*_ prefixed constants
  # =============================================================================
  LOW_MASS = PROP001_TOTAL_MASS           # 400
  LOW_MASS_THRUST = PROP001_ENGINE_THRUST  # 500
  LOW_MASS_MAX_SPEED = PROP001_MAX_SPEED   # 31.25
  MED_MASS = PROP002_MED_MASS              # 3000
  MED_MASS_THRUST = PROP002_THRUST         # 500
  MED_MASS_MAX_SPEED = PROP002_MED_MAX_SPEED  # 4.1667
  HIGH_MASS = PROP002_HIGH_MASS            # 11000
  HIGH_MASS_THRUST = PROP002_THRUST        # 500
  HIGH_MASS_MAX_SPEED = PROP002_HIGH_MAX_SPEED  # 1.1364
  THRUSTER_MASS = PROP003_TOTAL_MASS       # 400
  THRUSTER_RAW_TURN_RATE = PROP003_RAW_TURN_RATE  # 5.0
  THRUSTER_EXPECTED_TURN_SPEED = PROP003_TURN_SPEED  # 15.625
  NO_ENGINE_MASS = PROP001B_TOTAL_MASS     # 400
  THRUSTER_ONLY_MASS = PROP003B_TOTAL_MASS  # 400
  THRUSTER_ONLY_TURN_SPEED = PROP003B_TURN_SPEED  # 15.625
  ```
- [ ] Confirmed: zero external consumers (search verified only usage is definitions)
- [ ] Verify: `pytest simulation_tests/ -n 12` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
