# Project Proposal: Simulation Layer Test Coverage

## Summary

**Project ID:** PROJ-A (Prospective)
**Theme:** Test Coverage Gaps - Simulation Layer
**Priority:** High
**Estimated Effort:** Medium-Complex
**Findings Count:** 28

## Problem Statement

The simulation layer contains critical combat mechanics that are insufficiently tested. Three Critical-severity findings identify production code with zero unit tests:

1. **Projectile Entity** - Handles projectile physics, tracking, homing behavior, impact detection
2. **ShipStatQuerier** - Aggregates critical ship stats affecting combat calculations
3. **ShipValidator Rules** - 9 distinct validation rule classes with zero dedicated tests

These gaps represent significant risk because the simulation layer handles core combat mechanics that players experience directly.

## Scope

### Files Affected
- `game/simulation/entities/projectile.py`
- `game/simulation/entities/ship_stat_querier.py`
- `game/simulation/validation/ship_validator.py`
- `game/simulation/battle_controller.py`
- `game/simulation/combat/damage_calculator.py`
- `game/simulation/combat/weapon_firing_system.py`
- `game/simulation/combat/targeting_system.py`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/formula_system.py`
- `game/simulation/designs.py`
- `game/simulation/entities/ability_aggregator.py`
- `game/simulation/entities/ship_combat_engine.py`
- `game/simulation/projectile_manager.py`
- `game/simulation/components/abilities/propulsion.py`

### Test Files to Create/Enhance
- `tests/unit/simulation/entities/test_projectile.py` (NEW)
- `tests/unit/simulation/entities/test_ship_stat_querier.py` (NEW)
- `tests/unit/simulation/validation/test_ship_validator.py` (NEW)
- Various existing test files to enhance

## Findings Included

| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| TCG-SIM-001 | Critical | Projectile Entity Has No Unit Tests | Medium |
| TCG-SIM-002 | Critical | ShipStatQuerier Has No Unit Tests | Medium |
| TCG-SIM-003 | Critical | ShipValidator Rules Have No Unit Tests | Complex |
| TCG-SIM-004 | Major | BattleController Missing Edge Case Tests | Medium |
| TCG-SIM-005 | Major | DamageCalculator Armor Penetration Edge Cases | Simple |
| TCG-SIM-006 | Major | WeaponFiringSystem Missing Multishot Tests | Medium |
| TCG-SIM-007 | Major | TargetingSystem Missing AI Priority Tests | Medium |
| TCG-SIM-008 | Major | BattleEngine Tick Processing Incomplete | Medium |
| TCG-SIM-009 | Major | FormulaSystem Overflow/Underflow Not Tested | Simple |
| TCG-SIM-010 | Major | Design System Serialization Roundtrip Gaps | Medium |
| TCG-SIM-011 | Minor | AbilityAggregator Concurrent Modification | Simple |
| TCG-SIM-012 | Minor | ShipCombatEngine Heat Management Not Tested | Simple |
| TCG-SIM-013 | Minor | ShipFormation Complex Formation Tests | Simple |
| TCG-SIM-014 | Minor | BattleStateSerializer Version Migration | Simple |
| TCG-SIM-015 | Minor | PropulsionAbility Strategic Movement | Simple |
| TCG-SIM-016 | Minor | ProjectileManager Batch Update Tests | Simple |
| TCG-SIM-017 | Info | Test Organization Inconsistency | N/A |
| TCG-SIM-018 | Info | Simulation Integration Tests Sparse | N/A |

## Overlap Analysis

**PROJ-118 (Test Coverage -- Core and Simulation):** This prospective project has significant overlap with PROJ-118 which is in Planning status. Recommendation: Either merge these findings into PROJ-118 or treat PROJ-118 as covering simulation and this proposal as supplementary.

## Success Criteria

1. All 3 Critical findings have comprehensive unit tests
2. All 7 Major findings have edge case coverage added
3. Test coverage for simulation layer increases by at least 10%
4. No new test failures introduced
5. All new tests follow existing testing patterns and conventions

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Projectile physics tests may be complex | Use existing test patterns from similar entity tests |
| ShipValidator has 9 rule classes | Prioritize rules that affect common design paths |
| Tests may reveal existing bugs | Document bugs and create follow-up issues |

## Recommended Phases

### Phase 1: Critical Coverage (Days 1-3)
- Create test_projectile.py with core physics tests
- Create test_ship_stat_querier.py with aggregation tests
- Begin test_ship_validator.py with most common rules

### Phase 2: Major Edge Cases (Days 4-6)
- Complete ShipValidator rule tests
- Add BattleController edge cases
- Add DamageCalculator boundary tests

### Phase 3: Minor Gaps (Days 7-8)
- Address remaining Minor findings
- Improve test organization
- Document testing patterns used

## Dependencies

- No external dependencies
- May benefit from running after PROJ-118 if that project establishes testing conventions
