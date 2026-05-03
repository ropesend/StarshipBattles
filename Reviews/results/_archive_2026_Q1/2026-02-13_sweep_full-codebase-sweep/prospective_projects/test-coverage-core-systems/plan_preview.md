# Project Plan: Test Coverage - Core Systems

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Test Coverage - Core Systems
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 35 test coverage findings from the Foundation and Simulation layers. The primary goals are:

1. Add edge case tests for critical systems (collision, research)
2. Add unit tests for uncovered modules
3. Add state transition tests for battle and AI systems
4. Complete interface compliance tests

## Phases

### Phase 1: Critical Systems

**Objective:** Address critical test coverage gaps.

**Tasks:**
- [ ] Add CollisionSystem raycasting edge case tests (TCG-FND-001)
- [ ] Add ResearchService leaky bucket algorithm tests (TCG-FND-002)

**Estimated Effort:** 2-3 days

### Phase 2: AI and Combat Core

**Objective:** Test AI and combat systems thoroughly.

**Tasks:**
- [ ] Add AIController navigation tests (TCG-FND-003)
- [ ] Add Behavior state transition tests (TCG-FND-005)
- [ ] Add BattleController state transition tests (TCG-SIM-006)
- [ ] Add damage calculator armor interaction tests (TCG-SIM-010)

**Estimated Effort:** 3-4 days

### Phase 3: Simulation Layer

**Objective:** Complete simulation layer test coverage.

**Tasks:**
- [ ] Add designs.py unit tests (TCG-SIM-004)
- [ ] Add ResourceRegistry tests (TCG-SIM-005)
- [ ] Add FormulaSystem edge case tests (TCG-SIM-007)
- [ ] Add projectile guidance system tests (TCG-SIM-008)
- [ ] Add battle state serialization tests (TCG-SIM-009)

**Estimated Effort:** 3-4 days

### Phase 4: Foundation Layer

**Objective:** Complete foundation layer test coverage.

**Tasks:**
- [ ] Add TargetEvaluator rule evaluation tests (TCG-FND-004)
- [ ] Add TechTree validation tests (TCG-FND-006)
- [ ] Add TechRequirement edge case tests (TCG-FND-007)
- [ ] Add SpatialGrid query tests (TCG-FND-009)

**Estimated Effort:** 2-3 days

### Phase 5: Edge Cases and Utilities

**Objective:** Complete coverage with remaining tests.

**Tasks:**
- [ ] Add PhysicsBody property setter tests (TCG-FND-010)
- [ ] Add ShipControllableAdapter tests (TCG-FND-011)
- [ ] Add core module edge case tests (TCG-FND-012 through TCG-FND-016)
- [ ] Add component ability tests (TCG-SIM-011 through TCG-SIM-013)
- [ ] Add interface compliance tests (TCG-SIM-015, TCG-SIM-016)

**Estimated Effort:** 2-3 days

## Success Criteria

1. All CRITICAL test coverage gaps resolved
2. All MAJOR test coverage gaps resolved
3. CollisionSystem has >90% branch coverage
4. Battle simulation has full state transition coverage
5. All component abilities have unit tests
6. Test baseline increases by 200+ tests

## Dependencies

- None (self-contained)

## Risks

- Some tests may require refactoring for testability
- Complex state machine tests may be time-consuming
