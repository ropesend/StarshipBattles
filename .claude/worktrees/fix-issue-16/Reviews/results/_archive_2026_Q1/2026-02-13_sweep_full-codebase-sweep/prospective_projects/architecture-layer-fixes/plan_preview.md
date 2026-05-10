# Project Plan: Architecture Layer Fixes

## Project Metadata

- **Project ID:** PROJ-XXX
- **Title:** Architecture Layer Fixes
- **Status:** Planning
- **Created:** 2026-02-13
- **Source:** Sweep 2026-02-13_sweep_full-codebase-sweep

## Overview

This project addresses 29 architecture drift findings from the codebase sweep. The primary goals are:

1. Fix layer violations (simulation importing AI, UI importing test framework)
2. Resolve circular dependencies via proper dependency injection
3. Clean up private attribute access patterns
4. Plan decomposition for god classes

## Phases

### Phase 1: Critical Layer Violations

**Objective:** Remove test framework coupling from production code and fix simulation layer violations.

**Tasks:**
- [ ] Remove test framework import from `battle_screen.py` (ADR-UI1-002)
- [ ] Create test execution adapter interface for test_lab (ADR-UI1-001)
- [ ] Move AI factory to engine layer or use DI (ADR-SIM-001)

**Estimated Effort:** 3-5 days

### Phase 2: Private Attribute Access Cleanup

**Objective:** Replace private attribute access with proper public interfaces.

**Tasks:**
- [ ] Add public methods to WindowManager for close notifications (ADR-UI1-008)
- [ ] Create WorkshopActions interface (ADR-UI1-009)
- [ ] Add proper setters to WorkshopViewModel (ADR-UI1-010)
- [ ] Make FleetCapabilityCalculator._ship_has_ability public (ADR-UI1-014)
- [ ] Make InputMapper._extract_modifiers public (ADR-UI1-015)

**Estimated Effort:** 2-3 days

### Phase 3: Circular Dependency Resolution

**Objective:** Break circular imports using proper patterns.

**Tasks:**
- [ ] Break Ship<->ModifierService cycle via dependency injection (ADR-SIM-005)
- [ ] Create ShipQueryService facade for UI (ADR-UI1-007)
- [ ] Replace AI type hints with IAIController interface (ADR-SIM-002)

**Estimated Effort:** 3-4 days

### Phase 4: God Class Analysis

**Objective:** Document decomposition plans for large classes.

**Tasks:**
- [ ] Analyze BattleController responsibilities (ADR-SIM-003)
- [ ] Analyze Ship entity responsibilities (ADR-SIM-004)
- [ ] Document TestLabScreen decomposition plan (ADR-UI1-003)
- [ ] Document BuilderMain decomposition plan (ADR-UI1-005)
- [ ] Document BuildQueueScreen decomposition plan (ADR-UI1-006)

**Estimated Effort:** 2-3 days (analysis only)

## Success Criteria

1. All CRITICAL findings resolved
2. No test framework imports in production code
3. Simulation layer has no AI layer imports
4. All private attribute access converted to public APIs
5. God class decomposition documented for future projects

## Dependencies

- None (self-contained)

## Risks

- God class decomposition may be complex and require follow-up projects
- Test framework decoupling may require significant test refactoring
