# Phase 1: Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-131 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the Strategy module (18 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 1.1: TCG-STR-001 - No dedicated tests for game/strategy/dat [Simple]
**File:** `game/strategy/data/naming.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.2: TCG-STR-002 - No dedicated tests for game/strategy/dat [Medium]
**File:** `game/strategy/data/physics.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.3: TCG-STR-003 - No dedicated tests for game/strategy/eng [Simple]
**File:** `game/strategy/engine/commands.`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.4: TCG-STR-004 - TurnEngine.validate_colonize_order lacks [Simple]
**File:** `game/strategy/engine/turn_engi`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.5: TCG-STR-005 - FleetOrder.to_dict() serialization has w [Medium]
**File:** `game/strategy/data/fleet.py::F`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.6: TCG-STR-006 - QuickstartBuilder has no comprehensive t [Medium]
**File:** `game/strategy/quickstart_build`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.7: TCG-STR-007 - StrategySessionFacade has incomplete que [Medium]
**File:** `game/strategy/facade/strategy_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.8: TCG-STR-008 - GameInitializer._setup_initial_scenario [Simple]
**File:** `game/strategy/engine/game_init`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.9: TCG-STR-009 - ShipStatsCalculator.has_warp_capability [Medium]
**File:** `game/strategy/services/ship_st`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.10: TCG-STR-010 - DensityMap.from_config() lacks test cove [Simple]
**File:** `game/strategy/generation/densi`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.11: TCG-STR-011 - RegionClassifier._classify_spiral edge c [Simple]
**File:** `game/strategy/generation/regio`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.12: TCG-STR-012 - calculate_habitability has no negative t [Simple]
**File:** `game/strategy/formulas/habitab`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.13: TCG-STR-013 - EmpireEconomyCalculator doesn't test des [Simple]
**File:** `game/strategy/engine/empire_ec`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.14: TCG-STR-014 - Component inspector service lacks edge c [Simple]
**File:** `game/strategy/services/compone`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.15: TCG-STR-015 - Fleet.trigger_speed_recalculation has no [Simple]
**File:** `game/strategy/data/fleet.py::t`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.16: TCG-STR-016 - Transfer order validator edge cases [Simple]
**File:** `game/strategy/validation/trans`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.17: TCG-STR-017 - Test fixtures use hardcoded component ID [Complex]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.18: TCG-STR-018 - Heavy mocking in TurnEngine tests [Medium]
**File:** `tests/unit/strategy/turn_engin`
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
