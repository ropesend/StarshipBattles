# Project Proposal: Test Coverage - Strategy and UI

## Overview

**Project ID:** PROJ-F_test-coverage-strategy-ui
**Theme:** Test Coverage Gaps (TCG) - Strategy, UI-Screens, UI-Framework
**Total Findings:** 52
**Severity Breakdown:** Critical: 4 | Major: 21 | Minor: 18 | Info: 9

## Problem Statement

The Strategy and UI layers have significant test coverage gaps that risk visual bugs, user experience issues, and game logic errors. These include:

1. **Critical gaps** - Core modules like strategy data (naming, physics) and UI viewers lack tests
2. **Missing screen tests** - Major UI screens and panels have no dedicated tests
3. **Integration gaps** - Screen transitions and cross-module interactions untested
4. **Test quality issues** - Some existing tests use problematic patterns (bypass-init, over-mocking)

The Strategy layer controls game flow and the UI layer is the user's interface - bugs here directly impact player experience.

## Scope

### In Scope
- All TCG findings from STR (Strategy) shard
- All TCG findings from UI1 (UI-Screens) shard
- All TCG findings from UI2 (UI-Framework) shard
- Unit tests for uncovered modules
- Integration tests for critical user flows

### Out of Scope
- Foundation layer test coverage (separate project)
- Simulation layer test coverage (separate project)
- Visual regression testing (may be follow-up project)

## Findings Summary

### Critical (4)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-001 | No dedicated tests for game/strategy/data/naming.py | `game/strategy/data/naming.py` | Simple |
| TCG-STR-002 | No dedicated tests for game/strategy/data/physics.py | `game/strategy/data/physics.py` | Medium |
| TCG-UI1-001 | BattleStateViewer has no unit tests | `game/ui/screens/battle_state_viewer.py` | Medium |
| TCG-UI1-002 | TestLabValidationManager has no unit tests | `game/ui/screens/test_lab/validation_manager.py` | Complex |

### Major (21)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-003 | No dedicated tests for game/strategy/engine/commands.py | `game/strategy/engine/commands.py` | Simple |
| TCG-STR-004 | TurnEngine.validate_colonize_order lacks edge case tests | `game/strategy/engine/turn_engine.py` | Simple |
| TCG-STR-005 | FleetOrder.to_dict() serialization has weak tests | `game/strategy/data/fleet.py` | Medium |
| TCG-STR-006 | QuickstartBuilder has no comprehensive tests | `game/strategy/quickstart_builder.py` | Medium |
| TCG-STR-007 | StrategySessionFacade has incomplete query tests | `game/strategy/facade/strategy_session_facade.py` | Medium |
| TCG-STR-008 | GameInitializer._setup_initial_scenario lacks tests | `game/strategy/engine/game_initializer.py` | Simple |
| TCG-STR-009 | ShipStatsCalculator.has_warp_capability missing tests | `game/strategy/services/ship_stats_calculator.py` | Medium |
| TCG-UI2-001 | UIConfig class has no dedicated test coverage | `game/ui/config.py` | Simple |
| TCG-UI2-004 | BattleUIService projectile color mapping untested | `game/ui/services/battle_ui_service.py` | Simple |
| TCG-UI1-005 | BuilderScreen (legacy) has no unit tests | `game/ui/screens/builder/main.py` | Complex |
| TCG-UI1-006 | FormationEditorScreen has incomplete tests | `game/ui/screens/formation_editor.py` | Medium |
| TCG-UI1-007 | PlanetReportPanel has no unit tests | `game/ui/panels/planet_report_panel.py` | Medium |
| TCG-UI1-008 | ShipDetailPanel has no unit tests | `game/ui/panels/ship_detail_panel.py` | Medium |
| TCG-UI1-009 | BaseGallery abstract class has no unit tests | `game/ui/panels/base_gallery.py` | Simple |
| TCG-UI1-010 | DesignReportPanel has no unit tests | `game/ui/panels/design_report_panel.py` | Simple |
| TCG-UI1-011 | Multiple builder submodules have no tests | `game/ui/screens/builder/` | Complex |
| TCG-UI1-012 | Multiple test_lab submodules have no tests | `game/ui/screens/test_lab/` | Complex |
| TCG-UI1-013 | GalaxyTest screen module has no tests | `game/ui/screens/galaxy_test/` | Simple |
| TCG-UI1-014 | Formation submodules have no tests | `game/ui/screens/formation/` | Medium |
| TCG-UI1-015 | Workshop helper modules have thin coverage | `game/ui/screens/workshop_*.py` | Medium |
| TCG-UI1-016 | Multiple race panel modules lack tests | `game/ui/panels/race_*.py` | Medium |
| TCG-UI1-017 | StrategyRenderer draw methods test only existence | `tests/unit/ui/screens/test_strategy.py` | Medium |
| TCG-UI1-018 | DesignStatsPanel tests use bypass-init pattern | `tests/unit/ui/panels/test_design_stats.py` | Medium |

### Minor (18)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-010 | DensityMap.from_config() lacks test coverage | `game/strategy/generation/density_map.py` | Simple |
| TCG-STR-011 | RegionClassifier._classify_spiral edge cases | `game/strategy/generation/region_classifier.py` | Simple |
| TCG-STR-012 | calculate_habitability has no negative tests | `game/strategy/formulas/habitability.py` | Simple |
| TCG-STR-013 | EmpireEconomyCalculator doesn't test edge cases | `game/strategy/engine/empire_economy_calculator.py` | Simple |
| TCG-STR-014 | Component inspector service lacks edge case tests | `game/strategy/services/component_inspector.py` | Simple |
| TCG-STR-015 | Fleet.trigger_speed_recalculation has no tests | `game/strategy/data/fleet.py` | Simple |
| TCG-STR-016 | Transfer order validator edge cases | `game/strategy/validation/transfer_validator.py` | Simple |
| TCG-UI2-007 | InputMapper save_user_overrides file permissions | `game/ui/services/input_mapper.py` | Simple |
| TCG-UI2-008 | ScreenshotManager capture_strategy_layer untested | `game/ui/services/screenshot_manager.py` | Simple |
| TCG-UI2-009 | BattleOrchestrator lacks tests for AI coordination | `game/ui/orchestration/battle_orchestrator.py` | Simple |
| TCG-UI2-010 | SpriteManager thread safety tests are limited | `game/ui/renderer/sprites.py` | Medium |
| TCG-UI2-011 | colors.py basic constants not tested | `game/ui/colors.py` | Simple |
| TCG-UI1-019 | StrategyScreen tests have incomplete method coverage | `tests/unit/ui/screens/test_strategy.py` | Medium |
| TCG-UI1-020 | Screen transition handling untested | Multiple files | Simple |
| TCG-UI1-021 | Input handling edge cases untested | `game/ui/screens/strategy_input_handler.py` | Simple |
| TCG-UI1-022 | Source code inspection used instead of behavior tests | `tests/unit/ui/screens/test_strategy.py` | Simple |
| TCG-UI1-023 | Mock verification without assertions on return values | `tests/unit/ui/screens/test_strategy.py` | Simple |
| TCG-UI1-024 | Test helper function tests its own mock | `tests/unit/ui/panels/test_design_stats.py` | Simple |
| TCG-UI1-025 | Missing parameterized edge case tests | Multiple files | Simple |
| TCG-UI1-026 | No end-to-end battle UI flow tests | Multiple files | Medium |
| TCG-UI1-027 | Strategy screen + build queue integration untested | Multiple files | Medium |
| TCG-UI1-028 | Workshop + ship I/O roundtrip untested | Multiple files | Medium |
| TCG-UI1-029 | No resize handling tests | Multiple files | Simple |

### Info (9)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-017 | Test fixtures use hardcoded component IDs | Multiple files | Complex |
| TCG-STR-018 | Heavy mocking in TurnEngine tests | `tests/unit/strategy/turn_engine.py` | Medium |
| TCG-UI2-012 | Test organization could be improved | `tests/unit/ui/` | Complex |
| TCG-UI1-030 | No error recovery tests for UI screens | Multiple files | Complex |
| TCG-UI1-031 | No performance/stress tests for panels | `game/ui/panels/battle_panels.py` | Medium |
| TCG-UI1-032 | UI panels lack null/empty data tests | Multiple files | Simple |

## Effort Estimate

- **Simple tasks:** 24 findings
- **Medium tasks:** 20 findings
- **Complex tasks:** 8 findings

**Estimated Duration:** 3-4 sprints

## Recommended Phases

### Phase 1: Critical Strategy Gaps (Simple/Medium)
1. TCG-STR-001 - Add naming.py tests
2. TCG-STR-002 - Add physics.py tests
3. TCG-STR-003 - Add commands.py tests

### Phase 2: Critical UI Gaps (Medium/Complex)
4. TCG-UI1-001 - Add BattleStateViewer tests
5. TCG-UI1-002 - Add TestLabValidationManager tests
6. TCG-UI2-001 - Add UIConfig tests

### Phase 3: Strategy Engine Tests (Simple/Medium)
7. TCG-STR-004 through TCG-STR-009 - Engine and service tests

### Phase 4: UI Panel Tests (Simple/Medium)
8. TCG-UI1-007 through TCG-UI1-010 - Panel unit tests
9. TCG-UI1-016 - Race panel tests

### Phase 5: Screen Module Tests (Medium/Complex)
10. TCG-UI1-005 - BuilderScreen tests
11. TCG-UI1-006 - FormationEditor tests
12. TCG-UI1-011, TCG-UI1-012 - Submodule tests
13. TCG-UI1-014, TCG-UI1-015 - Workshop and formation tests

### Phase 6: Integration and Quality (Medium)
14. TCG-UI1-017 through TCG-UI1-019 - Fix test quality issues
15. TCG-UI1-026 through TCG-UI1-028 - Integration tests

## Potential Overlaps

Per `overlap_check.md`:
- **PROJ-124 (PROJ-E_ui-test-coverage)** - Status: Planning - Direct overlap with UI findings
- **PROJ-119 (Test Coverage -- Strategy and UI)** - Status: Planning - Direct overlap
- **PROJ-105 (Visual Regression Testing for UI Panels)** - Status: Planning - Related

**Recommendation:** Review PROJ-124 and PROJ-119 scopes. This proposal consolidates strategy and UI test coverage.

## Success Criteria

1. All CRITICAL test coverage gaps resolved
2. All MAJOR test coverage gaps resolved
3. Strategy data modules have comprehensive tests
4. All major UI panels have unit tests
5. At least 3 integration tests for user flows
6. Test baseline increases by 300+ tests
