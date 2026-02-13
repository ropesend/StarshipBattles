# Project Proposal: UI God Class Decomposition

## Summary

**Project ID:** PROJ-C (Prospective)
**Theme:** Architecture - God Class Decomposition
**Priority:** High
**Estimated Effort:** Complex
**Findings Count:** 23

## Problem Statement

Multiple UI screens have grown into "God Classes" - classes with too many responsibilities, too many methods, and too many lines of code. The project guidelines recommend classes stay under 500 lines and 30 methods.

Current violations:
- **TestLabScreen:** 1908 lines, 75 methods (4x over limits)
- **BuilderMain:** 1121 lines, 44 methods
- **BuildQueueScreen:** 1098 lines, 31 methods
- **StrategyScreen:** 811 lines, 45 methods

These God Classes also exhibit related issues: circular dependency workarounds, private attribute access across boundaries, and direct viewmodel state mutation.

## Scope

### Primary God Classes

| Class | File | Lines | Methods |
|-------|------|-------|---------|
| TestLabScreen | game/ui/screens/test_lab/screen.py | 1908 | 75 |
| BuilderMain | game/ui/screens/builder/main.py | 1121 | 44 |
| BuildQueueScreen | game/ui/screens/build_queue_screen.py | 1098 | 31 |
| StrategyScreen | game/ui/screens/strategy_screen.py | 811 | 45 |
| ShipThemeManager | game/ui/assets/ship_theme_manager.py | ~400 | ~20 |

### Related Architecture Issues

- Late imports to avoid circular dependencies
- Private attribute access across class boundaries
- Direct viewmodel state mutation
- Test framework coupling in production code

## Findings Included

| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| ADR-UI1-001 | Critical | Test Framework Coupling in Production UI | Medium |
| ADR-UI1-002 | Critical | Test Framework Import in Battle Screen | Simple |
| ADR-UI1-003 | Major | God Class - TestLabScreen (1908 lines) | Complex |
| ADR-UI1-004 | Major | God Class - StrategyScreen (811 lines) | Medium |
| ADR-UI1-005 | Major | God Class - BuilderMain (1121 lines) | Medium |
| ADR-UI1-006 | Major | God Class - BuildQueueScreen (1098 lines) | Medium |
| ADR-UI1-007 | Major | Circular Dependency Workarounds | Medium |
| ADR-UI1-008 | Major | Private Attribute Access - StrategyEventRouter | Simple |
| ADR-UI1-009 | Major | Private Attribute Access - WorkshopEventRouter | Simple |
| ADR-UI1-010 | Major | Direct ViewModel State Mutation | Simple |
| ADR-UI2-002 | Major | God Class Potential - ShipThemeManager | Medium |
| ADR-SIM-003 | Major | God Class - BattleController | Complex |
| ADR-SIM-004 | Major | God Class - Ship Entity | Complex |
| ADR-STR-003 | Major | Galaxy Class Approaching God Class | Complex |
| PP-002 | Major | Incomplete God Class Decomposition | Complex |
| MOD-002 | Minor | Mixed Responsibility in screen.py | Complex |
| ADR-UI1-011 | Minor | Simulation Layer TYPE_CHECKING Imports | Simple |
| ADR-UI1-012 | Minor | Planet Filter Cached Attributes | Simple |
| ADR-UI1-013 | Minor | Strategy Renderer Temporary Attributes | Simple |
| ADR-UI1-014 | Minor | FleetCapabilityCalculator Private Method | Simple |
| ADR-UI1-015 | Minor | InputMapper Private Method Access | Simple |
| ADR-UI1-016 | Info | Test Lab Executor Private Field Access | Simple |
| ADR-UI1-017 | Info | Deep Object Chain in StrategyUI | Simple |

## Overlap Analysis

No direct overlap with existing projects identified. This is a pure architecture improvement project.

## Success Criteria

1. All God Classes reduced to <500 lines
2. All classes have <30 methods
3. No circular dependency workarounds needed
4. No private attribute access across class boundaries
5. ViewModels properly encapsulated
6. Test framework decoupled from production UI

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Comprehensive test coverage before refactoring |
| Introducing new bugs | Extract-method refactoring preserves behavior |
| Test Lab depends on test framework | Create adapter interface for test execution |

## Recommended Phases

### Phase 1: Test Framework Decoupling (Days 1-2)
- Create TestExecutionAdapter interface
- Move test framework imports behind adapter
- Remove test framework coupling from battle_screen

### Phase 2: TestLabScreen Decomposition (Days 3-5)
- Extract PanelManager for panel lifecycle
- Extract ExecutionManager for test execution
- Extract EventRouter for event handling
- Extract ResultsManager for result display
- Target: <500 lines main screen

### Phase 3: BuilderMain Decomposition (Days 6-7)
- Extract BuilderLayout for panel initialization
- Move event handling to BuilderEventRouter
- Consolidate state management
- Target: <500 lines main screen

### Phase 4: Other God Classes (Days 8-10)
- BuildQueueScreen: Extract BuildQueueLogic
- StrategyScreen: Add StrategyScreenController
- ShipThemeManager: Split caching from loading
- Address simulation God Classes (BattleController, Ship)

### Phase 5: Cleanup (Days 11-12)
- Remove circular dependency workarounds
- Add public methods for private attribute access
- Add proper setters to ViewModels
- Remove temporary attributes from domain objects

## Dependencies

- Should run after or coordinate with PROJ-B (Legacy Eradication)
- Tests should pass before starting decomposition
