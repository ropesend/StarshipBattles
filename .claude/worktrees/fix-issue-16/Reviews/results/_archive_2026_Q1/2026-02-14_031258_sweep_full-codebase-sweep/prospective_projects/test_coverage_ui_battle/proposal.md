# Project Proposal: Test Coverage - UI Battle Systems

## Overview

This project addresses critical test coverage gaps in the UI layer's battle-related systems, including BattleScreen, BattleUI, battle panels, and related components. These are the primary visual interfaces for combat gameplay.

## Rationale

Battle UI is central to gameplay but has severe test gaps:
- BattleScreen (645 lines) handles battle simulation with only edge case tests
- BattleUI (292 lines) has NO test file at all
- battle_panels.py (ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel) has NO tests
- Critical interaction features like battle tick execution and panel rendering are untested

Combat is a core gameplay loop - visual bugs and interaction issues directly impact player experience.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| TCG-UI1-001 | Critical | BattleScreen has minimal functional tests | game/ui/screens/battle_screen.py | Complex |
| TCG-UI1-002 | Critical | BattleUI panel rendering has no test file | game/ui/screens/battle_ui.py | Medium |
| TCG-UI1-003 | Critical | battle_panels.py has no tests | game/ui/panels/battle_panels.py | Medium |
| TCG-UI2-001 | Major | Missing Tests for Validation Service Error Paths | game/ui/services/validation_service.py | Medium |
| TCG-UI2-002 | Major | BattleUIService Missing Tests for Edge Cases | game/ui/services/battle_ui_service.py | Medium |
| TCG-UI2-003 | Major | GameRenderer Missing Tests for Components | game/ui/renderer/game_renderer.py | Medium |
| TCG-UI1-005 | Major | FleetOrdersWindow has no tests | game/ui/screens/fleet_orders_window.py | Medium |
| TCG-UI1-006 | Major | SaveSelectionWindow has no tests | game/ui/screens/save_selection_window.py | Medium |
| TCG-UI1-007 | Major | PlanetListWindow has no direct test file | game/ui/screens/planet_list_window.py | Medium |
| TCG-UI1-008 | Minor | EmpirePanelWindow has no tests | game/ui/screens/empire_panel_window.py | Simple |
| TCG-UI1-009 | Major | NewGameSetupScreen has no tests | game/ui/screens/new_game_setup_screen.py | Medium |
| TCG-UI1-010 | Minor | StrategyEventRouter has no tests | game/ui/screens/strategy_event_router.py | Simple |
| TCG-UI1-014 | Major | RaceDescriptionPanel, ModifierImpactGrid, BuildQueueDragHandler have no tests | game/ui/panels/ | Medium |
| TCG-UI1-015 | Minor | RaceBrowserDialog tests are minimal | tests/unit/ui/test_race_browser_dialog.py | Simple |
| TCG-UI1-016 | Minor | SystemSelectionWindow and PlanetSelectionWindow have no tests | game/ui/screens/ | Simple |

## Summary Statistics

- **Total Findings:** 15
- **Critical:** 3 | **Major:** 8 | **Minor:** 4
- **Estimated Effort:** Complex (due to BattleScreen complexity)
- **Primary Location:** game/ui/screens/, game/ui/panels/, game/ui/services/

## Overlap with Active Projects

Potential overlap with:
- PROJ-142: 2_test_coverage_ui (likely duplicate scope)
- PROJ-136: Test Coverage - UI Components (overlapping)
- PROJ-124: PROJ-E_ui-test-coverage (overlapping)
- PROJ-119: Test Coverage -- Strategy and UI (partial overlap)
- PROJ-105: Visual Regression Testing for UI Panels (different approach)

**Recommendation:** This project focuses on functional/unit tests. Coordinate with visual regression testing projects if active.

## Success Criteria

1. BattleScreen has tests for tick execution, test scenario flow, headless/visual modes
2. BattleUI has dedicated test file covering handle_click, handle_resize, draw methods
3. battle_panels.py has tests for all three panel classes
4. All strategy windows have basic initialization and callback tests
5. Test coverage for game/ui/ increases measurably
