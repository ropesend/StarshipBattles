# Project Proposal: Test Coverage - UI Layer

## Overview
This project addresses Critical and Major test coverage gaps in the UI layer, including completely untested modules (game_renderer.py, ship_detail_panel.py, builder subsystem) and panels with no test coverage. The UI layer has significant untested visual and interaction code.

## Priority
**High** - Contains 4 Critical findings covering completely untested critical UI components, plus 14 Major findings for untested panels and screens.

## Scope

### Included Findings (24 total)
| ID | Severity | Title |
|----|----------|-------|
| TCG-UI2-001 | Critical | No Tests for game_renderer.py (Ship Rendering Logic) |
| TCG-UI1-002 | Critical | No Tests for Ship Detail Panel |
| TCG-UI1-001 | Critical | No Tests for Builder Subsystem (14 Production Files) - Excluded from scope |
| TCG-UI2-002 | Major | No Tests for battle_factories.py |
| TCG-UI2-003 | Major | config.py Has No Test Coverage |
| TCG-UI2-005 | Major | ship_io_adapter.py Needs Error Path Testing |
| TCG-UI1-003 | Major | No Tests for Planet Report Panel |
| TCG-UI1-004 | Major | No Tests for Design Report Panel |
| TCG-UI1-005 | Major | No Tests for Strategy Widgets |
| TCG-UI1-006 | Major | No Tests for System Tree Panel |
| TCG-UI1-007 | Major | No Tests for Component Modifier Grid Panel |
| TCG-UI1-011 | Major | Galaxy Test Screen No Tests |
| TCG-UI2-006 | Minor | BattleOrchestrator Missing Edge Case Tests |
| TCG-UI2-007 | Minor | screenshot_manager.py Tests Could Mock Less Heavily |
| TCG-UI2-008 | Minor | colors.py Has Test Coverage but Missing Edge Cases |
| TCG-UI1-012 | Minor | Incomplete Edge Case Testing for BattleScreen |
| TCG-UI1-013 | Minor | Workshop Screen Tests Are Mock-Heavy |
| TCG-UI1-016 | Minor | Test Lab Scene Tests Cover Only Logic, Not Screen |
| TCG-UI2-009 | Info | Excellent Test Coverage on BattleUIService (positive reference) |
| TCG-UI1-018 | Info | Test Patterns Vary Between Screen Tests |

### Explicitly Excluded
- **TCG-UI1-001 (Builder Subsystem)**: 14 files with Complex effort - too large for this project; warrants its own dedicated project
- **TCG-UI1-009 (Race Galleries)**: Gallery testing could be its own mini-project

## Estimated Effort
**Medium-Complex** - 8-12 days of focused work

### Phase Breakdown
1. **Phase 1: Critical UI Framework Tests** (3 days)
   - game_renderer.py tests
   - battle_factories.py tests
   - config.py validation tests

2. **Phase 2: Panel Test Coverage** (4 days)
   - ship_detail_panel.py tests
   - planet_report_panel.py tests (including compute_planet_production)
   - design_report_panel.py tests
   - strategy_widgets.py tests (AtmosphereGraph, SpectrumGraph)

3. **Phase 3: Service Error Paths** (2 days)
   - ship_io_adapter.py error path tests
   - BattleOrchestrator edge cases
   - screenshot_manager integration tests

4. **Phase 4: Edge Case Enhancements** (2 days)
   - BattleScreen edge cases
   - colors.py boundary values
   - Documentation of test patterns

## Success Criteria
- game_renderer.py has > 80% line coverage
- All panel test files created with meaningful tests
- Error propagation paths verified in adapters
- All tests pass

## Overlap with Existing Projects
- **PROJ-136 (Test Coverage - UI Components)**: Planning - direct overlap, should be merged or superseded
- **PROJ-131 (test-coverage-strategy-ui)**: Planning - partial overlap on UI tests
- **PROJ-124 (PROJ-E_ui-test-coverage)**: Planning - direct overlap
- **PROJ-105 (Visual Regression Testing)**: Planning - complementary, not overlapping

## Risks
- game_renderer.py requires pygame mocking patterns that may be complex
- Panel tests may need significant test fixture setup
- Some tests may require understanding visual rendering logic

## Dependencies
- Existing `BattleUIService` test patterns can serve as templates
- May benefit from completing UI Duplication project first (cleaner code to test)
