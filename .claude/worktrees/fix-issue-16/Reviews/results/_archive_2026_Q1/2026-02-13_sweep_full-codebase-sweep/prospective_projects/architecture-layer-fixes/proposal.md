# Project Proposal: Architecture Layer Fixes

## Overview

**Project ID:** PROJ-A_architecture-layer-fixes
**Theme:** Architecture Drift (ADR)
**Total Findings:** 29
**Severity Breakdown:** Critical: 3 | Major: 11 | Minor: 8 | Info: 7

## Problem Statement

The codebase has accumulated various architectural violations that break the intended layer separation and design principles. These include:

1. **Layer violations** - Simulation layer importing from AI layer, test framework coupling in production UI
2. **God classes** - Several classes exceeding 800-1900 lines with 40-75 methods
3. **Circular dependencies** - Documented workarounds via late imports
4. **Private attribute access** - External code accessing underscore-prefixed internals

These violations make the codebase harder to test, maintain, and reason about.

## Scope

### In Scope
- All ADR (Architecture Drift) findings from all shards
- Layer violation fixes in simulation and UI
- God class decomposition planning/partial implementation
- Circular dependency resolution
- Private attribute access cleanup

### Out of Scope
- Test coverage improvements (separate project)
- Code consistency issues (separate project)
- Legacy code cleanup (separate project)

## Findings Summary

### Critical (3)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-001 | AI Layer Imports in Simulation Factory | `game/simulation/factories/ai_factory.py` | Medium |
| ADR-UI1-001 | Test Framework Coupling in Production UI | `game/ui/screens/test_lab/screen.py` | Medium |
| ADR-UI1-002 | Test Framework Import in Battle Screen | `game/ui/screens/battle_screen.py` | Simple |

### Major (11)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-002 | TYPE_CHECKING Import of AI Controller | `game/simulation/systems/battle_engine.py` | Simple |
| ADR-SIM-003 | God Class - BattleController | `game/simulation/battle_controller.py` | Complex |
| ADR-SIM-004 | God Class - Ship Entity | `game/simulation/entities/ship.py` | Complex |
| ADR-SIM-005 | Documented Circular Import in Ship.add_component | `game/simulation/entities/ship.py` | Medium |
| ADR-UI2-002 | God Class Potential in ShipThemeManager | `game/ui/assets/ship_theme_manager.py` | Medium |
| ADR-UI1-003 | God Class - TestLabScreen (1908 lines, 75 methods) | `game/ui/screens/test_lab/screen.py` | Complex |
| ADR-UI1-004 | God Class - StrategyScreen (811 lines, 45 methods) | `game/ui/screens/strategy_screen.py` | Medium |
| ADR-UI1-005 | God Class - BuilderMain (1121 lines, 44 methods) | `game/ui/screens/builder/main.py` | Medium |
| ADR-UI1-006 | God Class - BuildQueueScreen (1098 lines, 31 methods) | `game/ui/screens/build_queue_screen.py` | Medium |
| ADR-UI1-007 | Circular Dependency Workarounds (Late Imports) | `game/ui/screens/column_manager.py` | Medium |
| ADR-UI1-008 | Private Attribute Access - StrategyEventRouter | `game/ui/screens/strategy_event_router.py` | Simple |
| ADR-UI1-009 | Private Attribute Access - WorkshopEventRouter | `game/ui/screens/workshop_event_router.py` | Simple |
| ADR-UI1-010 | Direct ViewModel State Mutation | `game/ui/screens/workshop_screen.py` | Simple |

### Minor (8)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | behaviors.py File Growing Large | `game/ai/behaviors.py` | Simple |
| ADR-SIM-006 | Possible Circular Import Comment in ship_stats.py | `game/simulation/entities/ship_stats.py` | Simple |
| ADR-UI2-003 | Lazy Import Pattern in ship_factory.py | `game/ui/services/ship_factory.py` | Simple |
| ADR-UI1-011 | Simulation Layer TYPE_CHECKING Imports | Multiple files | Simple |
| ADR-UI1-012 | Planet Filter Cached Attributes | `game/ui/screens/planet_list_filters.py` | Simple |
| ADR-UI1-013 | Strategy Renderer Temporary Attributes | `game/ui/screens/strategy_renderer.py` | Simple |
| ADR-UI1-014 | FleetCapabilityCalculator Private Method Access | `game/ui/screens/column_manager.py` | Simple |
| ADR-UI1-015 | InputMapper Private Method Access | `game/ui/screens/keybindings_scene.py` | Simple |

### Info (7)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-007 | Heavy Use of TYPE_CHECKING for Forward References | Multiple files | N/A |
| ADR-UI2-005 | BattleOrchestrator Correctly Documents Concerns | `game/ui/orchestration/battle_orchestrator.py` | N/A |
| ADR-UI1-016 | Test Lab Executor Private Field Access | `game/ui/screens/test_lab/test_executor.py` | Simple |
| ADR-UI1-017 | Deep Object Chain in StrategyUI | `game/ui/screens/strategy_ui.py` | Simple |
| ADR-UI1-018 | Large Method Counts in UI Screens | Multiple screens | N/A |

## Effort Estimate

- **Simple tasks:** 11 findings
- **Medium tasks:** 9 findings
- **Complex tasks:** 4 findings
- **N/A (monitoring/info):** 5 findings

**Estimated Duration:** 2-3 sprints

## Recommended Phases

### Phase 1: Critical Layer Violations (Simple/Medium)
1. ADR-UI1-002 - Remove test framework import from battle_screen.py
2. ADR-UI1-001 - Extract test execution adapter interface
3. ADR-SIM-001 - Move AI factory to higher layer or inject dependencies

### Phase 2: Private Attribute Access (Simple)
4. ADR-UI1-008 - Add public methods to WindowManager
5. ADR-UI1-009 - Create WorkshopActions interface
6. ADR-UI1-010 - Add proper setters to WorkshopViewModel
7. ADR-UI1-014, ADR-UI1-015 - Make private methods public

### Phase 3: Circular Dependencies (Medium)
8. ADR-SIM-005 - Break Ship<->ModifierService cycle via DI
9. ADR-UI1-007 - Create ShipQueryService facade
10. ADR-SIM-002 - Replace AI type hints with interfaces

### Phase 4: God Class Planning (Complex)
11. ADR-SIM-003, ADR-SIM-004 - Plan BattleController/Ship decomposition
12. ADR-UI1-003, ADR-UI1-005, ADR-UI1-006 - Plan UI god class decomposition

## Potential Overlaps

Per `overlap_check.md`:
- **PROJ-123 (PROJ-D_architecture-cleanup)** - Status: Planning - Overlaps with Architecture Drift findings
- **PROJ-121 (PROJ-B_legacy-eradication)** - Some overlap with legacy patterns

**Recommendation:** Review PROJ-123 scope. If it covers similar ground, this proposal could be merged or deferred.

## Success Criteria

1. No remaining CRITICAL architecture violations
2. All layer violations resolved (simulation no longer imports AI layer)
3. No test framework imports in production code
4. All private attribute access converted to public interfaces
5. God classes have documented decomposition plans (full implementation may span multiple projects)
