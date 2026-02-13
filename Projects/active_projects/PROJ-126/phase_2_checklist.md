# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-126 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Address findings in the Simulation module (7 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 2.1: ADR-SIM-001 - AI Layer Imports in Simulation Factory [Medium]
**File:** `game/simulation/factories/ai_factory.py` -> `game/ai/ai_factory.py`
**Tests:** `pytest tests/unit/simulation/factories/test_ai_factory.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Moved AIControllerFactory from simulation layer to AI layer (game/ai/ai_factory.py)
- Created IAIControllerFactory protocol in simulation/interfaces/ai_controller.py
- Updated factory to use two-phase initialization (set_grid pattern)
- Updated all callers to inject factory from higher layers (UI, strategy)
- Factory functions in battle_controller.py use late import helper
- 11870 tests pass

### Task 2.2: ADR-SIM-002 - TYPE_CHECKING Import of AI Controller [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/combat/test_battle_engine_core.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Updated TYPE_CHECKING imports to use protocols from simulation layer
- Removed direct imports from AI layer in simulation code
- Factory is now injected, TYPE_CHECKING only references protocols

### Task 2.3: ADR-SIM-003 - God Class - BattleController [Complex]
**File:** `game/simulation/battle_control`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.4: ADR-SIM-004 - God Class - Ship Entity [Complex]
**File:** `game/simulation/entities/ship.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.5: ADR-SIM-005 - Documented Circular Import in Ship.add_c [Medium]
**File:** `game/simulation/entities/ship.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.6: ADR-SIM-006 - Possible Circular Import Comment in ship [Simple]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 2.7: ADR-SIM-007 - Heavy Use of TYPE_CHECKING for Forward R [N]
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
