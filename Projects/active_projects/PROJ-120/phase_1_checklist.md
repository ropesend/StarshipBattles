# Phase 1: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-120 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Address findings in the Simulation module (18 findings, 3 critical)
**Priority:** High

---

## Tasks

### Task 1.1: TCG-SIM-001 - Projectile Entity Has No Unit Tests [Medium]
**File:** `game/simulation/entities/projectile.py`
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Created comprehensive unit tests (37 tests) covering initialization, validation exceptions, movement, lifetime, damage, and missile guidance. Tests in correct location: tests/unit/simulation/entities/test_projectile.py

### Task 1.2: TCG-SIM-002 - ShipStatQuerier Has No Unit Tests [Medium]
**File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** `pytest tests/unit/entities/test_ship_stat_querier.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Already complete - comprehensive tests exist (45 tests) covering all methods, edge cases, and type handling. Tests in tests/unit/entities/test_ship_stat_querier.py

### Task 1.3: TCG-SIM-003 - ShipValidator Rules Have No Unit Tests [Complex]
**File:** `game/simulation/validation/ship_validator.py`
**Tests:** `pytest tests/unit/simulation/validation/test_ship_validator_rules.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Created comprehensive unit tests (50 tests) for all validation rules: LayerConstraintRule, UniqueComponentRule, ExclusiveGroupRule, MountDependencyRule, LayerRestrictionDefinitionRule, MassBudgetRule, ClassRequirementsRule, ResourceDependencyRule, ShipDesignValidator. Also tests helper functions and RestrictionPrefixes constants.

### Task 1.4: TCG-SIM-004 - BattleController Missing Edge Case Tests [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/test_edge_cases.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Created comprehensive edge case tests (32 tests) in new test_edge_cases.py file covering:
- apply_results_to_fleets edge cases (4 tests)
- add_reinforcements with no engine (3 tests)
- load_state with projectile restoration (4 tests)
- mode_handler property access (3 tests)
- Multiple reconfiguration scenarios (3 tests)
- Callback edge cases (3 tests)
- _retreat_allowed logic (4 tests)
- _reinforcements_allowed logic (3 tests)
- _update_retreats (2 tests)
- get_results edge cases (3 tests)
Total BattleController tests now: 134 (was 102)

### Task 1.5: TCG-SIM-005 - DamageCalculator Armor Penetration Edge [Simple]
**File:** `game/simulation/combat/damage_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.6: TCG-SIM-006 - WeaponFiringSystem Missing Multishot Tes [Medium]
**File:** `game/simulation/combat/weapon_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.7: TCG-SIM-007 - TargetingSystem Missing AI Priority Test [Medium]
**File:** `game/simulation/combat/targeti`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.8: TCG-SIM-008 - BattleEngine Tick Processing Incomplete [Medium]
**File:** `game/simulation/systems/battle`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.9: TCG-SIM-009 - FormulaSystem Overflow/Underflow Not Tes [Simple]
**File:** `game/simulation/formula_system`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.10: TCG-SIM-010 - Design System Serialization Roundtrip Ga [Medium]
**File:** `game/simulation/designs.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.11: TCG-SIM-011 - AbilityAggregator Missing Concurrent Mod [Simple]
**File:** `game/simulation/entities/abili`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.12: TCG-SIM-012 - ShipCombatEngine Heat Management Not Tes [Simple]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.13: TCG-SIM-013 - ShipFormation Missing Complex Formation [Simple]
**File:** `tests/unit/simulation/entities`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.14: TCG-SIM-014 - BattleStateSerializer Version Migration [Simple]
**File:** `tests/unit/simulation/test_bat`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.15: TCG-SIM-015 - PropulsionAbility Strategic Movement Not [Simple]
**File:** `game/simulation/components/abi`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.16: TCG-SIM-016 - ProjectileManager Missing Batch Update T [Simple]
**File:** `game/simulation/projectile_man`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.17: TCG-SIM-017 - Test Organization Inconsistency [N]
**File:** `tests/unit/simulation/`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.18: TCG-SIM-018 - Simulation Integration Tests Sparse [N]
**File:** `tests/integration/`
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
