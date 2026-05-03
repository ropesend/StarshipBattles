# Project Proposal: Test Coverage - Strategy and AI Systems

## Overview
This project addresses Critical and Major test coverage gaps in the Strategy layer and AI/Foundation systems. These are core game logic systems where bugs directly impact gameplay balance and player experience. The findings include completely untested modules (commands.py, physics.py) and critical edge cases in targeting, navigation, and ship stats.

## Priority
**High** - Contains 2 Critical findings affecting core gameplay systems and 10 Major findings for critical game logic.

## Scope

### Included Findings (22 total)
| ID | Severity | Title |
|----|----------|-------|
| TCG-FND-001 | Critical | AIController Integration with StrategyManager Missing Edge Case Tests |
| TCG-STR-001 | Critical | Commands Module Has No Dedicated Unit Tests |
| TCG-FND-002 | Major | TargetEvaluator Rule Types Missing Comprehensive Tests |
| TCG-FND-004 | Major | TechTree.validate_requirements() Return Value Not Tested |
| TCG-STR-004 | Major | FleetNavigationService Unit Tests Are Thin |
| TCG-STR-005 | Major | ShipStatsCalculator Edge Cases Untested |
| TCG-STR-006 | Major | Superweapon Command Handlers Have Limited Validation Tests |
| UNK-01 | Major | Missing integration tests for component damage |
| UNK-04 | Major | Resource consumption during combat tick |
| TCG-FND-007 | Minor | Resources Module Missing Test Coverage |
| TCG-FND-008 | Minor | ResearchService.estimate_turns_to_breakthrough Edge Cases |
| TCG-FND-009 | Minor | Profiler Test Coverage Could Be Enhanced |
| TCG-FND-010 | Minor | Controllable Interface Adapter Test Enhancement |
| TCG-STR-009 | Minor | DesignMetadata Tests Are Sparse |
| TCG-STR-010 | Minor | FleetResourceAggregator Edge Cases |
| TCG-STR-011 | Minor | PlacementStrategies Lack Regression Tests |
| TCG-STR-012 | Minor | RegionClassifier Tests Thin |
| TCG-STR-013 | Minor | TransferValidator Missing Specific Edge Case Tests |
| TCG-STR-014 | Minor | ColonizeValidator "Any Planet" Logic Complex |
| TCG-FND-012 | Info | TechRequirement Negation Logic Test Enhancement Opportunity |
| TCG-STR-015 | Info | Test Organization Inconsistency |

### Also Related (Unknown shards)
- UNK-02: Defense ability classes undertested
- UNK-03: Crew ability classes minimal test coverage
- UNK-05: BattleLogger tests outside simulation tests
- UNK-06: Formula system exception handling
- UNK-07: ShipStatQuerier lacks dedicated tests
- UNK-08: ship_serialization error path tests

## Estimated Effort
**Medium-Complex** - 10-14 days of focused work

### Phase Breakdown
1. **Phase 1: Critical Module Tests** (3 days)
   - commands.py tests (19 command dataclasses)
   - physics.py tests (radiation calculations)
   - AIController edge cases

2. **Phase 2: AI and Targeting** (3 days)
   - TargetEvaluator all 14 rule types
   - AIFactory unit tests
   - ControllableAdapter edge cases

3. **Phase 3: Strategy Services** (3 days)
   - FleetNavigationService edge cases
   - ShipStatsCalculator edge cases
   - Superweapon handler validation failures

4. **Phase 4: Minor Coverage Gaps** (3 days)
   - DTO module tests
   - Validator edge cases
   - Generation determinism tests

## Success Criteria
- commands.py has dedicated test file with 100% coverage
- All 14 TargetEvaluator rule types tested
- FleetNavigationService edge cases (zero speed, max iterations) covered
- ShipStatsCalculator formula error handling tested
- All tests pass

## Overlap with Existing Projects
- **PROJ-135 (Test Coverage - Strategy Engine)**: Planning - direct overlap
- **PROJ-130 (test-coverage-core-systems)**: Planning - overlaps on FND findings
- **PROJ-118 (Test Coverage -- Core and Simulation)**: Planning - overlaps
- **PROJ-119 (Test Coverage -- Strategy and UI)**: Planning - overlaps
- **PROJ-120 (PROJ-A_simulation-test-coverage)**: Planning - overlaps on simulation tests

## Risks
- AIController edge case testing may require complex mock setup
- Strategy physics may need scientific review for correctness
- Some tests may uncover actual bugs that need fixing

## Dependencies
- None - can run independently
