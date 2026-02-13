# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-123 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the Simulation module (4 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 2.1: ADR-SIM-001 - AI Layer Imports in Simulation Factory [Medium]
**File:** `game/simulation/factories/ai_f`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.2: ADR-SIM-002 - TYPE_CHECKING Import of AI Controller [Simple]
**File:** `game/simulation/systems/battle`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.3: ADR-SIM-005 - Possible Circular Import Workaround [Simple]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.4: ADR-SIM-006 - Heavy Use of TYPE_CHECKING for Forward R [N]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
