# PROJ-XXX: Test Coverage - UI Layer

## Project Goal
Add comprehensive test coverage to critical UI components that currently have zero or minimal testing, using BattleUIService tests as the quality template.

## Current State
- game_renderer.py: 0% coverage (ship rendering, visual critical path)
- ship_detail_panel.py: 0% coverage (447 lines)
- planet_report_panel.py: 0% coverage (509 lines)
- design_report_panel.py: 0% coverage (284 lines)
- battle_factories.py: No dedicated tests
- strategy_widgets.py: No tests for graph rendering

## Target State
- All critical UI components have > 80% line coverage
- Panel test patterns established for future panels
- Error propagation tested in adapters
- Visual logic (coordinate transforms, scaling) verified

---

## Phase 1: Critical UI Framework Tests
**Status:** Not Started

### Tasks
- [ ] 1.1 Create `tests/unit/ui/renderer/test_game_renderer.py`
- [ ] 1.2 Test `draw_ship()` culling logic (ships outside viewport)
- [ ] 1.3 Test theme image scaling and rotation
- [ ] 1.4 Test overlay mode rendering paths
- [ ] 1.5 Test low-zoom fallback behavior
- [ ] 1.6 Create `tests/unit/ui/services/test_battle_factories.py`
- [ ] 1.7 Test each factory function returns correctly configured controller
- [ ] 1.8 Test ship cloning in hypothetical battles
- [ ] 1.9 Create `tests/unit/ui/test_config.py` with constant validation
- [ ] 1.10 Run test suite

### Files Created
- `tests/unit/ui/renderer/test_game_renderer.py`
- `tests/unit/ui/services/test_battle_factories.py`
- `tests/unit/ui/test_config.py`

---

## Phase 2: Panel Test Coverage
**Status:** Not Started

### Tasks
- [ ] 2.1 Create `tests/unit/ui/panels/test_ship_detail_panel.py`
- [ ] 2.2 Test `get_damage_color()` boundary values (0, 0.49, 0.5, 0.74, 0.75, 1.0)
- [ ] 2.3 Test `update_ship()` with None input (placeholder behavior)
- [ ] 2.4 Test `toggle_layer()` state changes
- [ ] 2.5 Create `tests/unit/ui/panels/test_planet_report_panel.py`
- [ ] 2.6 Test `compute_planet_production()` pure function
- [ ] 2.7 Test `_format_compact_number()` edge cases (0, 999, 1000, 999999, 1000000)
- [ ] 2.8 Create `tests/unit/ui/panels/test_design_report_panel.py`
- [ ] 2.9 Test portrait path generation logic
- [ ] 2.10 Test ship class parsing regex
- [ ] 2.11 Create `tests/unit/ui/panels/test_strategy_widgets.py`
- [ ] 2.12 Test AtmosphereGraph logarithmic scaling
- [ ] 2.13 Test SpectrumGraph normalization
- [ ] 2.14 Run test suite

### Files Created
- `tests/unit/ui/panels/test_ship_detail_panel.py`
- `tests/unit/ui/panels/test_planet_report_panel.py`
- `tests/unit/ui/panels/test_design_report_panel.py`
- `tests/unit/ui/panels/test_strategy_widgets.py`

---

## Phase 3: Service Error Paths
**Status:** Not Started

### Tasks
- [ ] 3.1 Add error propagation tests to `test_ship_io_adapter.py`
- [ ] 3.2 Test Tkinter unavailability propagation
- [ ] 3.3 Test file permission error handling
- [ ] 3.4 Test malformed JSON handling
- [ ] 3.5 Add edge case tests to `test_battle_orchestrator.py`
- [ ] 3.6 Test AI creation for ships with None values
- [ ] 3.7 Test large team sizes
- [ ] 3.8 Create `tests/unit/ui/panels/test_system_tree_panel.py`
- [ ] 3.9 Create `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
- [ ] 3.10 Run test suite

### Files Affected
- `tests/unit/ui/services/test_ship_io_adapter.py`
- `tests/unit/ui/test_battle_orchestrator.py`
- `tests/unit/ui/panels/test_system_tree_panel.py` (new)
- `tests/unit/ui/panels/test_component_modifier_grid_panel.py` (new)

---

## Phase 4: Edge Case Enhancements
**Status:** Not Started

### Tasks
- [ ] 4.1 Add BattleScreen edge case tests (resize, overlay, limits)
- [ ] 4.2 Add colors.py boundary value tests
- [ ] 4.3 Create test pattern documentation in `tests/unit/ui/README.md`
- [ ] 4.4 Add basic smoke tests for galaxy_test screen
- [ ] 4.5 Run full test suite
- [ ] 4.6 Final coverage report

---

## Success Metrics
- [ ] game_renderer.py has tests with > 80% coverage
- [ ] All 6 panel test files created
- [ ] Error paths verified in ship_io_adapter
- [ ] All tests passing
- [ ] Test patterns documented for future reference
