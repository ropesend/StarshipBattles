# PROJ-A: Simulation Layer Test Coverage

## Project Overview

**Goal:** Achieve comprehensive test coverage for critical simulation layer components that currently have zero or insufficient unit tests.

**Context:** The sweep identified 3 Critical and 7 Major test coverage gaps in the simulation layer. These gaps represent significant risk because the simulation layer handles core combat mechanics.

## Current State

- Projectile entity: 0 unit tests
- ShipStatQuerier: 0 unit tests
- ShipValidator: 0 unit tests for 9 rule classes
- BattleController: Has tests but missing edge cases
- Combat subsystems: Partial coverage with gaps

## Target State

- All critical classes have comprehensive unit tests
- Edge cases are covered for all major combat paths
- Test organization mirrors production structure
- 10%+ increase in simulation layer coverage

## Phases

### Phase 1: Critical Class Coverage
**Estimated Duration:** 3 days

#### 1.1 Projectile Entity Tests
- [ ] Create `tests/unit/simulation/entities/test_projectile.py`
- [ ] Test projectile initialization with various weapon types
- [ ] Test straight-line movement physics
- [ ] Test homing/tracking behavior
- [ ] Test lifetime/endurance expiration
- [ ] Test impact detection logic
- [ ] Test stealth level handling
- [ ] Test target acquisition and retargeting

#### 1.2 ShipStatQuerier Tests
- [ ] Create `tests/unit/simulation/entities/test_ship_stat_querier.py`
- [ ] Test `get_ability_total()` with various ability types
- [ ] Test stack group rules (MAX within group, MULTIPLY across)
- [ ] Test `get_total_ability_value()` with operational_only flag
- [ ] Test `max_weapon_range` calculation
- [ ] Test edge cases: no components, no abilities, destroyed components

#### 1.3 ShipValidator Tests
- [ ] Create `tests/unit/simulation/validation/test_ship_validator.py`
- [ ] Test LayerConstraintRule
- [ ] Test UniqueComponentRule
- [ ] Test ExclusiveGroupRule
- [ ] Test MountDependencyRule
- [ ] Test LayerRestrictionDefinitionRule
- [ ] Test MassBudgetRule
- [ ] Test ClassRequirementsRule
- [ ] Test ResourceDependencyRule
- [ ] Test ShipDesignValidator integration

### Phase 2: Major Edge Cases
**Estimated Duration:** 3 days

#### 2.1 BattleController Edge Cases
- [ ] Add reinforcement arrival tests
- [ ] Add multiple simultaneous death tests
- [ ] Add pause/resume state transition tests
- [ ] Add large battle performance tests
- [ ] Add zero-ship edge case tests

#### 2.2 Combat System Edge Cases
- [ ] DamageCalculator: armor piercing > total armor
- [ ] DamageCalculator: exactly zero armor remaining
- [ ] WeaponFiringSystem: multi-shot weapons
- [ ] WeaponFiringSystem: spread patterns
- [ ] WeaponFiringSystem: point defense
- [ ] TargetingSystem: AI priority scoring
- [ ] TargetingSystem: stealth/detection interaction

#### 2.3 Formula and Serialization
- [ ] FormulaSystem: integer overflow tests
- [ ] FormulaSystem: float precision tests
- [ ] FormulaSystem: NaN/Infinity handling
- [ ] Designs: roundtrip serialization
- [ ] Designs: corrupted data handling

### Phase 3: Minor Gaps and Organization
**Estimated Duration:** 2 days

#### 3.1 Minor Test Gaps
- [ ] AbilityAggregator: concurrent modification
- [ ] ShipCombatEngine: heat management
- [ ] ShipFormation: large formations
- [ ] BattleStateSerializer: version migration
- [ ] PropulsionAbility: strategic movement
- [ ] ProjectileManager: batch updates

#### 3.2 Test Organization
- [ ] Review test file locations
- [ ] Document testing patterns
- [ ] Add integration test recommendations

## Validation

### During Development
- Run `pytest tests/unit/simulation/ -v` after each test file
- Verify no regressions with `pytest tests/ --testmon`

### Completion Criteria
- [ ] All Critical findings have tests (3/3)
- [ ] All Major findings have tests (7/7)
- [ ] All Minor findings addressed (6/6)
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Coverage increased by 10%+

## Notes

- Coordinate with PROJ-118 if it becomes active
- Use existing test patterns from similar entity tests
- Document any bugs discovered during test creation
