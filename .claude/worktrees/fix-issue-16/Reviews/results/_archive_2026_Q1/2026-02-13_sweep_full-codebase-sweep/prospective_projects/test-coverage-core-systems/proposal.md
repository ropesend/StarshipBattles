# Project Proposal: Test Coverage - Core Systems

## Overview

**Project ID:** PROJ-E_test-coverage-core-systems
**Theme:** Test Coverage Gaps (TCG) - Foundation and Simulation
**Total Findings:** 35
**Severity Breakdown:** Critical: 4 | Major: 14 | Minor: 13 | Info: 4

## Problem Statement

The Foundation (FND) and Simulation (SIM) layers have significant test coverage gaps that risk production bugs and regression issues. These include:

1. **Critical gaps** - Core systems like CollisionSystem, ResearchService lack edge case tests
2. **Missing module tests** - Some modules have no dedicated tests at all
3. **Edge case gaps** - Many modules have basic tests but missing boundary/edge coverage
4. **Interface tests** - Protocols and interfaces lack verification tests

The Foundation and Simulation layers are critical to game correctness - bugs here propagate to all higher layers.

## Scope

### In Scope
- All TCG findings from FND (Foundation) shard
- All TCG findings from SIM (Simulation) shard
- Unit tests for uncovered modules
- Edge case tests for partially covered modules
- Interface compliance tests

### Out of Scope
- Strategy layer test coverage (separate project)
- UI layer test coverage (separate project)
- Integration tests (may be follow-up project)

## Findings Summary

### Critical (4)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-001 | CollisionSystem raycasting edge cases untested | `game/engine/collision.py` | Medium |
| TCG-FND-002 | ResearchService leaky bucket algorithm edge cases | `game/research/systems/research_service.py` | Medium |

### Major (14)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-003 | AIController navigation and avoidance algorithms | `game/ai/controller.py` | Medium |
| TCG-FND-004 | TargetEvaluator rule evaluation missing tests | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-005 | Behavior classes missing state transition tests | `game/ai/behaviors.py` | Medium |
| TCG-FND-006 | TechTree validation methods lack test coverage | `game/research/data/tech_tree.py` | Simple |
| TCG-FND-007 | TechRequirement fuzzy resolution edge cases | `game/research/data/tech_node.py` | Simple |
| TCG-FND-009 | SpatialGrid query_radius does not filter correctly | `game/engine/spatial.py` | Simple |
| TCG-SIM-004 | designs.py Lacks Any Test Coverage | `game/simulation/designs.py` | Simple |
| TCG-SIM-005 | resource_manager.py (ResourceRegistry) Missing Tests | `game/simulation/systems/resource_manager.py` | Medium |
| TCG-SIM-006 | battle_controller.py Missing State Transition Tests | `game/simulation/battle_controller.py` | Medium |
| TCG-SIM-007 | formula_system.py Edge Cases Not Tested | `game/simulation/formula_system.py` | Simple |
| TCG-SIM-008 | projectile_manager.py Missing Guidance System Tests | `game/simulation/projectile_manager.py` | Medium |
| TCG-SIM-009 | battle_state.py Serialization Round-Trip Tests | `game/simulation/battle_state.py` | Medium |
| TCG-SIM-010 | combat/damage_calculator.py Missing Armor Interaction Tests | `game/simulation/combat/damage_calculator.py` | Medium |

### Minor (13)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-010 | PhysicsBody x/y property setters not tested | `game/engine/physics.py` | Simple |
| TCG-FND-011 | ShipControllableAdapter formation methods | `game/ai/interfaces/controllable.py` | Simple |
| TCG-FND-012 | Logger module singleton behavior not fully tested | `game/core/logger.py` | Simple |
| TCG-FND-013 | Config module edge cases for clamp values | `game/core/config.py` | Simple |
| TCG-FND-014 | Error code enum completeness not verified | `game/core/error_codes.py` | Simple |
| TCG-FND-015 | Profiling decorator edge cases not tested | `game/core/profiling.py` | Simple |
| TCG-FND-016 | hex_ring negative radius input not tested | `game/core/hex_math.py` | Simple |
| TCG-SIM-011 | components/abilities/weapons.py Tests Sparse | `game/simulation/components/abilities/weapons.py` | Simple |
| TCG-SIM-012 | components/abilities/defense.py Tests Lacking | `game/simulation/components/abilities/defense.py` | Simple |
| TCG-SIM-013 | components/abilities/propulsion.py Missing Tests | `game/simulation/components/abilities/propulsion.py` | Simple |
| TCG-SIM-015 | interfaces/ai_controller.py Interface Tests Missing | `game/simulation/interfaces/ai_controller.py` | Simple |
| TCG-SIM-016 | validation/ship_validator.py Missing Comprehensive Tests | `game/simulation/validation/ship_validator.py` | Simple |

### Info (4)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-017 | Research system UI rendering tests use mocks | `game/research/ui/research_renderer.py` | N/A |
| TCG-FND-018 | Test file organization follows production structure | Multiple files | N/A |
| TCG-SIM-017 | Test Organization Could Use Consolidation | Multiple files | N/A |
| TCG-SIM-018 | No Performance/Load Tests for Simulation | `game/simulation/systems/battle_engine.py` | N/A |

## Effort Estimate

- **Simple tasks:** 18 findings
- **Medium tasks:** 13 findings
- **N/A (monitoring):** 4 findings

**Estimated Duration:** 2-3 sprints

## Recommended Phases

### Phase 1: Critical Gaps (Medium)
Address the most critical test coverage gaps first.
1. TCG-FND-001 - CollisionSystem raycasting edge cases
2. TCG-FND-002 - ResearchService leaky bucket algorithm

### Phase 2: AI/Combat Core (Medium)
Test core AI and combat systems.
3. TCG-FND-003 - AIController navigation tests
4. TCG-FND-005 - Behavior state transition tests
5. TCG-SIM-006 - BattleController state transitions
6. TCG-SIM-010 - Damage calculator armor interactions

### Phase 3: Simulation Systems (Simple/Medium)
Test simulation layer modules.
7. TCG-SIM-004 - designs.py test coverage
8. TCG-SIM-005 - ResourceRegistry tests
9. TCG-SIM-007 - FormulaSystem edge cases
10. TCG-SIM-008 - Projectile guidance tests
11. TCG-SIM-009 - Battle state serialization

### Phase 4: Foundation Core (Simple)
Test foundation layer modules.
12. TCG-FND-004 - TargetEvaluator rule tests
13. TCG-FND-006, TCG-FND-007 - Tech tree tests
14. TCG-FND-009 - SpatialGrid query tests

### Phase 5: Edge Cases and Utilities (Simple)
Complete coverage with edge case tests.
15. TCG-FND-010 through TCG-FND-016 - Core module edge cases
16. TCG-SIM-011 through TCG-SIM-016 - Component and interface tests

## Potential Overlaps

Per `overlap_check.md`:
- **PROJ-120 (PROJ-A_simulation-test-coverage)** - Status: Planning - Direct overlap with SIM findings
- **PROJ-118 (Test Coverage -- Core and Simulation)** - Status: Planning - Direct overlap

**Recommendation:** Review PROJ-120 and PROJ-118 scopes. This proposal may duplicate or extend existing projects.

## Success Criteria

1. All CRITICAL test coverage gaps resolved
2. All MAJOR test coverage gaps resolved
3. CollisionSystem has >90% branch coverage
4. Battle simulation has state transition tests
5. All component abilities have unit tests
6. Test baseline increases by 200+ tests
