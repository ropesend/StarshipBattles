# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-146 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the Simulation module (12 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: ADR-SIM-001 - Simulation Depends on game.engine (Physi [Medium]
**File:** `game/simulation/entities/ship.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.2: ADR-SIM-002 - Simulation Depends on game.engine (Spati [Medium]
**File:** `game/simulation/systems/battle`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.3: ADR-SIM-003 - Circular Import Risk - Ship and Modifier [Medium]
**File:** `game/simulation/entities/ship.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.4: ADR-SIM-004 - Circular Import Risk - ShipSerializer an [Simple]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.5: ADR-SIM-005 - God Class Indicator - Ship Class (810 LO [Complex]
**File:** `game/simulation/entities/ship.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.6: ADR-SIM-006 - God Class Indicator - Component Class (7 [Medium]
**File:** `game/simulation/components/com`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.7: CON-SIM-009 - Magic Numbers in Physics Calculations [Simple]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.8: CON-SIM-012 - Component Type Checking via String vs is [Medium]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.9: ADR-SIM-007 - TYPE_CHECKING Used Extensively for Layer [N]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.10: CON-SIM-018 - Singleton Pattern Usage [Complex]
**File:** `game/simulation/components/com`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.11: CON-SIM-019 - Ability Registry as Module-Level Dict [Medium]
**File:** `game/simulation/components/abi`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.12: CON-SIM-020 - Late Import Comments [N]
**File:** `game/simulation/entities/ship_`
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
