# Phase 3: Other

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-143 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Address findings not mapped to a specific shard
**Priority:** Normal

---

## Tasks

### Task 3.1: UNK-01 - Missing integration tests for component destruction cascade [DONE]
**File:** `game/simulation/combat/damage_calculator.py`
**Tests:** `pytest tests/integration/fleet_combat/test_component_destruction_cascade.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 13 integration tests covering: engine destruction -> thrust=0, shield destruction -> max_shields reduced, damage cascade through DamageCalculator, partial damage edge cases, combat flow integration.

### Task 3.2: UNK-04 - Resource consumption during combat tick [DONE]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/integration/fleet_combat/test_combat_resource_consumption.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 25 tests covering: ResourceState basics (consume, has_sufficient, add, update), ResourceRegistry integration (multi-resource tracking, stacking storage/generation, reset), ship resource consumption, combat resource flow (depletion, regeneration), edge cases.

### Task 3.3: UNK-02 - Defense ability classes undertested in isolation [ALREADY DONE]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** File already exists with 67 comprehensive tests covering ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor classes - all __init__, recalculate, get_ui_rows, get_primary_value methods and edge cases.

### Task 3.4: UNK-03 - Crew ability classes have minimal test coverage [DONE]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 55 tests covering CrewCapacity, LifeSupportCapacity, CrewRequired - all __init__ variants, recalculate with modifiers, get_ui_rows, get_primary_value, stat bindings, edge cases (large values, zero multipliers, sqrt scaling for CrewRequired).

### Task 3.5: UNK-05 - BattleLogger tests exist but outside sim [Unknown]
**File:** `tests/unit/combat/test_battle_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.6: UNK-06 - Formula system exception handling edge c [Unknown]
**File:** `game/simulation/formula_system`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.7: UNK-07 - ShipStatQuerier class lacks dedicated te [Unknown]
**File:** `game/simulation/entities/ship_`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 3.8: UNK-08 - ship_serialization module could use erro [Unknown]
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
