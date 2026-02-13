# PROJ-E: UI Layer Test Coverage

## Project Overview

**Goal:** Achieve comprehensive test coverage for UI screens, panels, and services that currently have zero or insufficient unit tests.

**Context:** The sweep identified 4 Critical and 28 Major test coverage gaps in the UI layer. Core battle visualization components have no tests at all.

## Current State

- BattleScreen: 0 unit tests
- BattleUI: 0 unit tests
- BattleStateViewer: 0 unit tests
- BattlePanels: 0 unit tests
- Multiple builder/test_lab/formation modules: 0 tests
- Strategy layer: naming.py, physics.py with 0 tests

## Target State

- All Critical UI classes have comprehensive unit tests
- All Major gaps have basic coverage
- Test coverage for UI layer increases by 15%+
- Documented patterns for UI testing

## Phases

### Phase 1: Battle UI Tests
**Estimated Duration:** 4 days

#### 1.1 BattleScreen Tests
- [ ] Create `tests/unit/ui/screens/test_battle_screen.py`
- [ ] Test initialization with mock dependencies
- [ ] Test event handling methods
- [ ] Test state transitions
- [ ] Test rendering calls (mock pygame)

#### 1.2 BattleUI Tests
- [ ] Create `tests/unit/ui/screens/test_battle_ui.py`
- [ ] Test interface methods
- [ ] Test data transformation
- [ ] Test event routing

#### 1.3 BattleStateViewer Tests
- [ ] Create `tests/unit/ui/screens/test_battle_state_viewer.py`
- [ ] Test state display logic
- [ ] Test filtering/sorting

#### 1.4 BattlePanels Tests
- [ ] Create `tests/unit/ui/panels/test_battle_panels.py`
- [ ] Test ShipStatsPanel
- [ ] Test SeekerMonitor
- [ ] Test data binding

### Phase 2: Panel Tests
**Estimated Duration:** 3 days

#### 2.1 Report Panels
- [ ] Create `tests/unit/ui/panels/test_planet_report_panel.py`
- [ ] Create `tests/unit/ui/panels/test_ship_detail_panel.py`
- [ ] Create `tests/unit/ui/panels/test_design_report_panel.py`

#### 2.2 Gallery and Race Panels
- [ ] Create `tests/unit/ui/panels/test_base_gallery.py`
- [ ] Create tests for race panel modules

### Phase 3: Screen Module Tests
**Estimated Duration:** 4 days

#### 3.1 Builder Submodules
- [ ] Identify untested builder modules
- [ ] Create tests for each submodule
- [ ] Focus on logic, not rendering

#### 3.2 Test Lab Submodules
- [ ] Identify untested test_lab modules
- [ ] Create tests for each submodule

#### 3.3 Formation Modules
- [ ] Create tests for formation submodules

#### 3.4 Workshop Modules
- [ ] Improve workshop_*.py coverage

### Phase 4: Service and Framework Tests
**Estimated Duration:** 3 days

#### 4.1 UIConfig Tests
- [ ] Create `tests/unit/ui/test_config.py`
- [ ] Test configuration loading
- [ ] Test validation

#### 4.2 Renderer Tests
- [ ] Add draw_ship edge cases
- [ ] Add draw_hud edge cases
- [ ] Test with boundary values

#### 4.3 Service Tests
- [ ] BattleUIService projectile color tests
- [ ] ShipThemeManager scale factor tests

### Phase 5: Strategy Layer Tests
**Estimated Duration:** 3 days

#### 5.1 Data Module Tests
- [ ] Create `tests/unit/strategy/data/test_naming.py`
- [ ] Create `tests/unit/strategy/data/test_physics.py`
- [ ] Create `tests/unit/strategy/engine/test_commands.py`

#### 5.2 Service Tests
- [ ] Add ShipStatsCalculator.has_warp_capability tests
- [ ] Add StrategySessionFacade query tests

#### 5.3 Edge Cases
- [ ] Add TurnEngine validate_colonize_order tests
- [ ] Add FleetOrder serialization tests
- [ ] Add QuickstartBuilder tests

## Validation

### During Development
- Run `pytest tests/unit/ui/ -v` after each test file
- Verify no regressions with `pytest tests/ --testmon`

### Completion Criteria
- [ ] All Critical findings have tests (6/6)
- [ ] All Major findings have tests (28/28)
- [ ] UI layer coverage increased by 15%+
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Testing patterns documented

## Notes

- Use existing pygame mock patterns from other UI tests
- Focus on testable logic over rendering
- Coordinate with PROJ-119 for strategy layer
- Consider PROJ-105 for visual regression
