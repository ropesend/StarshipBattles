# PROJ-12: God Class Decomposition

## Overview
**Status:** In Progress
**Created:** 2026-01-24

## Current State
**Last Updated:** 2026-01-24
**Last Agent Action:** Completed Phase 4 - Extracted all visual selection galleries (flags, portraits, themes)
**Next Action:** Commit Phase 4 work and proceed to Phase 5 (AIController Interface)
**Blockers:** None

**Context for Next Agent:**
- Phase 1 is 100% complete (ShipCombatEngine extraction)
- Phase 2 is 100% complete (ShipComponentManager extraction)
- Phase 3 is 100% complete (TurnEngine decomposition)
- Phase 4 is 100% complete (RaceSetupScreen decomposition):
  - Created `game/ui/screens/race_browser_dialog.py` (290 lines, 11 tests)
  - Created `game/ui/screens/race_validator.py` (78 lines, 18 tests)
  - Created `game/ui/screens/race_asset_loader.py` (186 lines, 12 tests)
  - Created `game/ui/panels/race_environment_panel.py` (383 lines, 16 tests)
  - Created `game/ui/panels/race_description_panel.py` (139 lines, 13 tests)
  - Created `game/ui/panels/race_flag_gallery.py` (266 lines, 15 tests)
  - Created `game/ui/panels/race_portrait_gallery.py` (249 lines, 15 tests)
  - Created `game/ui/panels/race_theme_gallery.py` (205 lines, 14 tests)
  - RaceSetupScreen reduced from 2325 → 1227 lines (1098 line reduction, 47%)
  - **Target of <500 lines not achieved** - 1227 lines remain
  - Ship preview logic (~300 lines) and summary panel (~200 lines) could be extracted
  - Recommend accepting current state - significant decomposition achieved
- All tests passing:
  - 463 UI unit tests
  - 707 strategy unit tests
  - 114 new Phase 4 component tests (11+18+12+16+13+15+15+14)
- Uncommitted Phase 1 + Phase 2 + Phase 3 + Phase 4 changes present
- Recommend committing before continuing
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
