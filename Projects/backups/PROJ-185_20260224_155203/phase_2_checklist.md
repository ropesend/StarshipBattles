# Phase 2: Remove Legacy Constant Aliases

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-185 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove unused backward compat aliases in propulsion scenarios

---

## Tasks

### Task 2.1: Remove propulsion legacy aliases [Simple]
**File:** `simulation_tests/scenarios/propulsion_scenarios.py`
**Tests:** `pytest simulation_tests/ -n 12`

- [x] Remove the entire legacy aliases block (lines 257-280), including section header comment
- [x] Confirmed: zero external consumers - BUT internal consumers existed in PropThrustMassRatioScenario and PropNoEngineScenario. Migrated to PROP002_/PROP001B_ constants.
- [x] Verify: `pytest tests/ -n 12` passes (12366 passed, 1 skipped)

**Notes:**
- Plan incorrectly stated "zero external consumers" - the aliases WERE used internally by PropThrustMassRatioScenario and PropNoEngineScenario in the same file
- Migrated all usages to proper PROP002_ and PROP001B_ prefixed constants
- Pre-existing simulation_tests failures unrelated to this change (PROP-001, PROP-003, PROP-004 were already failing before this phase)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
