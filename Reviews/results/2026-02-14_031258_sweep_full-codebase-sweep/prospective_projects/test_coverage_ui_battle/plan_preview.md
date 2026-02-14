# Plan: Test Coverage - UI Battle Systems

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Add comprehensive test coverage to battle-related UI components including screens, panels, and services.

## Current State

Battle UI has critical test gaps:
- BattleScreen only has edge case tests (keyboard, mouse)
- BattleUI has no test file
- Battle panels (3 classes) have no tests
- Many strategy windows lack tests

## Target State

- All battle screens have functional tests
- Panel rendering and click handling is tested
- Service edge cases are covered
- Strategy windows have initialization tests

## Phases

### Phase 1: Battle Core Tests
**Files to create:**
- `tests/unit/ui/screens/test_battle_screen_functional.py`
- `tests/unit/ui/screens/test_battle_ui.py`
- `tests/unit/ui/panels/test_battle_panels.py`

**Coverage:**
- BattleScreen: `start()`, `update()`, `_run_single_tick()`, `is_battle_over()`
- BattleUI: `handle_click()`, `handle_resize()`, draw methods
- ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel

### Phase 2: Battle Services
**Files to create/update:**
- `tests/unit/ui/services/test_validation_service.py`
- `tests/unit/ui/services/test_battle_ui_service.py`
- `tests/unit/ui/renderer/test_game_renderer.py`

**Coverage:**
- Error paths for validation
- BattleUIService edge cases
- GameRenderer component rendering

### Phase 3: Strategy Windows
**Files to create:**
- `tests/unit/ui/screens/test_fleet_orders_window.py`
- `tests/unit/ui/screens/test_save_selection_window.py`
- `tests/unit/ui/screens/test_planet_list_window.py`
- `tests/unit/ui/screens/test_new_game_setup_screen.py`
- `tests/unit/ui/screens/test_strategy_event_router.py`

### Phase 4: Panel Tests
**Files to create:**
- `tests/unit/ui/panels/test_race_description_panel.py`
- `tests/unit/ui/panels/test_modifier_impact_grid.py`
- `tests/unit/ui/panels/test_build_queue_drag_handler.py`

### Phase 5: Dialog Tests
**Files to update/create:**
- Update `tests/unit/ui/test_race_browser_dialog.py`
- `tests/unit/ui/screens/test_system_selection_window.py`
- `tests/unit/ui/screens/test_planet_selection_window.py`
- `tests/unit/ui/screens/test_empire_panel_window.py`

## Checklist

### Phase 1: Battle Core
- [ ] Create test_battle_screen_functional.py
- [ ] Test tick execution flow
- [ ] Test headless vs visual mode
- [ ] Test controller integration
- [ ] Create test_battle_ui.py
- [ ] Test handle_click routing
- [ ] Create test_battle_panels.py
- [ ] Test ShipStatsPanel expansion logic
- [ ] Test SeekerMonitorPanel rendering
- [ ] Test BattleControlPanel clicks

### Phase 2: Services
- [ ] Test validation error paths
- [ ] Test BattleUIService edge cases
- [ ] Test GameRenderer components

### Phase 3: Windows
- [ ] Test FleetOrdersWindow undo/redo
- [ ] Test SaveSelectionWindow load/delete
- [ ] Test PlanetListWindow filtering
- [ ] Test NewGameSetupScreen validation
- [ ] Test StrategyEventRouter routing

### Phase 4: Panels
- [ ] Test race description editing
- [ ] Test modifier grid display
- [ ] Test build queue drag ops

### Phase 5: Dialogs
- [ ] Expand RaceBrowserDialog tests
- [ ] Test selection callbacks

## Dependencies

- May require UI test fixtures/mocks setup

## Risks

- UI tests may require pygame mocking
- Some tests may need integration-level setup
