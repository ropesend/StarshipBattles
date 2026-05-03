# PROJ-C: UI God Class Decomposition

## Project Overview

**Goal:** Reduce all God Classes to maintainable sizes (<500 lines, <30 methods) through systematic decomposition.

**Context:** Multiple UI screens have grown beyond maintainable limits. TestLabScreen at 1908 lines and 75 methods is the most severe case.

## Current State

| Class | Lines | Methods | Over Limit |
|-------|-------|---------|------------|
| TestLabScreen | 1908 | 75 | 4x |
| BuilderMain | 1121 | 44 | 2x |
| BuildQueueScreen | 1098 | 31 | 2x |
| StrategyScreen | 811 | 45 | 1.5x |

## Target State

| Class | Target Lines | Target Methods |
|-------|--------------|----------------|
| TestLabScreen | <500 | <25 |
| BuilderMain | <500 | <25 |
| BuildQueueScreen | <500 | <25 |
| StrategyScreen | <500 | <25 |

## Phases

### Phase 1: Test Framework Decoupling
**Estimated Duration:** 2 days

#### 1.1 Create Adapter Interface
- [ ] Define `ITestExecutor` protocol in `game/ui/interfaces/`
- [ ] Define methods: `run_test()`, `get_results()`, `log_execution()`
- [ ] Create `TestFrameworkAdapter` implementing the protocol

#### 1.2 Decouple TestLabScreen
- [ ] Replace direct `TestRegistry` import with adapter
- [ ] Replace direct `TestHistory` import with adapter
- [ ] Move test execution logic to adapter

#### 1.3 Decouple BattleScreen
- [ ] Remove `test_framework.runner` import
- [ ] Remove `runner._log_test_execution` call
- [ ] Inject logging callback if needed

### Phase 2: TestLabScreen Decomposition
**Estimated Duration:** 3 days

#### 2.1 Extract PanelManager
- [ ] Create `TestLabPanelManager` class
- [ ] Move panel creation methods
- [ ] Move panel lifecycle management
- [ ] Move layout calculations

#### 2.2 Extract ExecutionManager
- [ ] Create `TestLabExecutionManager` class
- [ ] Move test execution logic
- [ ] Move result processing
- [ ] Move progress tracking

#### 2.3 Extract EventRouter
- [ ] Create `TestLabEventRouter` class
- [ ] Move event handling methods
- [ ] Move callback registrations
- [ ] Ensure clean event flow

#### 2.4 Extract ResultsManager
- [ ] Create `TestLabResultsManager` class
- [ ] Move results display logic
- [ ] Move filtering/sorting
- [ ] Move export functionality

### Phase 3: BuilderMain Decomposition
**Estimated Duration:** 2 days

#### 3.1 Extract Layout
- [ ] Create `BuilderLayout` class
- [ ] Move panel initialization
- [ ] Move layout calculations
- [ ] Move resize handling

#### 3.2 Consolidate Event Handling
- [ ] Expand `BuilderEventRouter` usage
- [ ] Move remaining event handlers
- [ ] Remove direct event handling from main

#### 3.3 Consolidate State
- [ ] Review `BuilderStateManager` completeness
- [ ] Move remaining state management
- [ ] Remove direct state manipulation

### Phase 4: Other God Classes
**Estimated Duration:** 3 days

#### 4.1 BuildQueueScreen
- [ ] Extract `BuildQueueLogic` for queue operations
- [ ] Keep screen focused on presentation
- [ ] Move validation to logic class

#### 4.2 StrategyScreen
- [ ] Create `StrategyScreenController`
- [ ] Move coordination logic to controller
- [ ] Keep screen focused on rendering

#### 4.3 ShipThemeManager
- [ ] Split caching responsibility
- [ ] Split loading responsibility
- [ ] Create focused helper classes

### Phase 5: Cleanup
**Estimated Duration:** 2 days

#### 5.1 Circular Dependency Resolution
- [ ] Create `ShipQueryService` facade
- [ ] Move ship stat calculations behind facade
- [ ] Remove late import workarounds

#### 5.2 Private Attribute Access
- [ ] Add public methods to WindowManager
- [ ] Add public methods to WorkshopScreen
- [ ] Create WorkshopActions protocol

#### 5.3 ViewModel Encapsulation
- [ ] Add setters to WorkshopViewModel
- [ ] Remove direct `_selected_components` access
- [ ] Add validation in setters

#### 5.4 Temporary Attributes
- [ ] Create PlanetDisplayData wrapper
- [ ] Create rendering cache dictionary
- [ ] Remove `_temp_*` attributes from domain objects

## Validation

### During Development
- Run `pytest tests/ --testmon` after each extraction
- Verify UI functionality with manual testing
- Run lint checks to catch import issues

### Completion Criteria
- [ ] All Critical findings resolved (2/2)
- [ ] All Major findings resolved (14/14)
- [ ] TestLabScreen < 500 lines
- [ ] BuilderMain < 500 lines
- [ ] BuildQueueScreen < 500 lines
- [ ] StrategyScreen < 500 lines
- [ ] No circular dependency workarounds
- [ ] Full test suite passes

## Notes

- Use extract-method refactoring to preserve behavior
- Create tests for extracted classes
- Document new class responsibilities
- Consider dependency injection patterns
