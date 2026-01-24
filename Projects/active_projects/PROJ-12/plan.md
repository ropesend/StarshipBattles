# PROJ-12: God Class Decomposition

## Overview
**Status:** Planning
**Created:** 2026-01-24
**Source:** Review 2026-01-24_general_full-codebase-maintainability

This project addresses the "god class" anti-pattern identified across multiple layers. These large, monolithic classes with too many responsibilities are major blockers to maintainability and testability.

## Goals
1. Decompose Ship class (750+ lines) into focused components
2. Decompose TurnEngine class (737 lines) into specialized services
3. Decompose RaceSetupScreen (2,325 lines) into reusable UI components
4. Improve testability of all decomposed classes
5. Maintain backward compatibility during transition

## Scope

### In Scope
- CQ-003 / AR-004: Ship class decomposition
- STRAT-003: TurnEngine decomposition
- AR-008: RaceSetupScreen decomposition
- CQ-002: fire_weapons() method extraction
- SIM-02: Ship-Component coupling reduction
- SIM-09: Ability aggregation consolidation
- AR-003: AIController interface extraction

### Out of Scope
- Layer separation (covered in PROJ-11 - should be done first)
- Error handling (covered in PROJ-10)
- UI architectural patterns beyond RaceSetupScreen

## Success Criteria
- [ ] Ship class < 400 lines
- [ ] TurnEngine class < 400 lines
- [ ] RaceSetupScreen < 500 lines with extracted components
- [ ] All decomposed classes have unit tests
- [ ] No functionality regression
- [ ] All tests pass

## Phases

### Phase 1: Ship Combat Extraction
Extract combat logic from Ship class into ShipCombatEngine.

### Phase 2: Ship Component Manager
Extract component management into ShipComponentManager.

### Phase 3: TurnEngine Decomposition
Split TurnEngine into FleetMovementEngine, CombatResolutionEngine, ProductionEngine.

### Phase 4: RaceSetupScreen Components
Extract RacePreviewRenderer, RaceValidator, RaceBrowserDialog.

### Phase 5: AIController Interface
Create ShipAIInterface and decouple AI from Ship internals.

## Dependencies
- **PROJ-11** (Architecture Layer Separation) should be completed first
- Phase 5 depends on Phase 1-2 completion

## Risks
- **High:** Ship class changes affect many parts of the codebase
- **Mitigation:** Use facade pattern - keep Ship as thin wrapper during transition
- **Medium:** Breaking changes to serialization
- **Mitigation:** Maintain to_dict/from_dict compatibility

## Related Documents
- [Design Document](design.md)
- [Decisions Log](decisions.md)
- [Phase 1 Checklist](phase_1_checklist.md)
- [Phase 2 Checklist](phase_2_checklist.md)
- [Phase 3 Checklist](phase_3_checklist.md)
- [Phase 4 Checklist](phase_4_checklist.md)
- [Phase 5 Checklist](phase_5_checklist.md)
- [Source Review - Code Quality](../../Reviews/results/2026-01-24_general_full-codebase-maintainability/findings/code_quality_report.md)
- [Source Review - Simulation](../../Reviews/results/2026-01-24_general_full-codebase-maintainability/findings/simulation_specialist_report.md)
- [Source Review - Strategy](../../Reviews/results/2026-01-24_general_full-codebase-maintainability/findings/strategy_specialist_report.md)
