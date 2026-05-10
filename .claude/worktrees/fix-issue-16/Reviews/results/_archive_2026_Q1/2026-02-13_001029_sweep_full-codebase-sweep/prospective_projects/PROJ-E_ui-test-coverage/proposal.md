# Project Proposal: UI Layer Test Coverage

## Summary

**Project ID:** PROJ-E (Prospective)
**Theme:** Test Coverage Gaps - UI Layer
**Priority:** Medium
**Estimated Effort:** Complex
**Findings Count:** 63

## Problem Statement

The UI layer has significant test coverage gaps across screens, panels, and services. Multiple Critical findings identify core UI components with zero unit tests, including:

1. **BattleScreen** - Core battle visualization with no tests
2. **BattleUI** - Battle interface layer with no tests
3. **BattleStateViewer** - State debugging view with no tests
4. **BattlePanels** - Ship stats and seeker monitoring with no tests

Additionally, there are 27 Major and 26 Minor test coverage gaps across builder modules, strategy screens, panels, and test quality issues.

## Scope

### UI Screens Requiring Tests
- `game/ui/screens/battle_screen.py`
- `game/ui/screens/battle_ui.py`
- `game/ui/screens/battle_state_viewer.py`
- `game/ui/screens/builder/` (multiple modules)
- `game/ui/screens/test_lab/` (multiple modules)
- `game/ui/screens/formation/` (multiple modules)
- `game/ui/screens/workshop_*.py`

### UI Panels Requiring Tests
- `game/ui/panels/battle_panels.py`
- `game/ui/panels/planet_report_panel.py`
- `game/ui/panels/ship_detail_panel.py`
- `game/ui/panels/base_gallery.py`
- `game/ui/panels/design_report_panel.py`
- `game/ui/panels/race_*.py`

### UI Services Requiring Tests
- `game/ui/config.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/assets/ship_theme_manager.py`

## Findings Included

### Critical (5)
| ID | Title | Location |
|----|-------|----------|
| TCG-UI1-001 | BattleScreen has no unit tests | game/ui/screens/battle_screen.py |
| TCG-UI1-002 | BattleUI has no unit tests | game/ui/screens/battle_ui.py |
| TCG-UI1-003 | BattleStateViewer has no unit tests | game/ui/screens/battle_state_viewer.py |
| TCG-UI1-004 | BattlePanels has no unit tests | game/ui/panels/battle_panels.py |

### Major (28)
Includes:
- TCG-UI1-005 through TCG-UI1-018 (UI Screen gaps)
- TCG-UI2-001 through TCG-UI2-005 (UI Framework gaps)
- Strategy layer test gaps (TCG-STR-001 through TCG-STR-009)

### Minor (30)
Includes:
- Edge case tests for existing coverage
- Test quality improvements
- Integration test recommendations

## Overlap Analysis

**PROJ-119 (Test Coverage -- Strategy and UI):** This prospective project has significant overlap with PROJ-119 which is in Planning status. Strategy-layer findings are included here but may belong in PROJ-119.

**PROJ-105 (Visual Regression Testing for UI Panels):** May complement this project for visual testing specifically.

## Success Criteria

1. All Critical UI test gaps have comprehensive tests
2. All Major UI test gaps have basic coverage
3. Test coverage for UI layer increases by 15%+
4. No new test failures introduced
5. Test patterns documented for future UI tests

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| UI tests may require pygame mocking | Use existing pygame mock patterns |
| Battle screen complexity | Focus on testable logic, not rendering |
| Large scope | Phase by priority - Critical first |

## Recommended Phases

### Phase 1: Battle UI Tests (Days 1-4)
- Create test_battle_screen.py
- Create test_battle_ui.py
- Create test_battle_state_viewer.py
- Create test_battle_panels.py

### Phase 2: Panel Tests (Days 5-7)
- Create test_planet_report_panel.py
- Create test_ship_detail_panel.py
- Create test_base_gallery.py
- Create test_design_report_panel.py

### Phase 3: Screen Module Tests (Days 8-11)
- Builder submodule tests
- Test lab submodule tests
- Formation module tests
- Workshop module tests

### Phase 4: Service and Framework Tests (Days 12-14)
- UIConfig tests
- game_renderer edge cases
- battle_ui_service tests
- ship_theme_manager tests

### Phase 5: Strategy Layer Tests (Days 15-17)
- naming.py tests
- physics.py tests
- commands.py tests
- Other strategy gaps

## Dependencies

- Should coordinate with PROJ-119 for strategy layer coverage
- May benefit from PROJ-105 for visual regression patterns
- Should run after PROJ-C if UI is being decomposed
