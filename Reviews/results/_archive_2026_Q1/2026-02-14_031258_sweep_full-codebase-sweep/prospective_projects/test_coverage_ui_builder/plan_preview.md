# Plan: Test Coverage - UI Builder & Test Lab

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Create test coverage for the builder and test_lab UI subsystems which currently have zero to minimal test files.

## Current State

- builder/ subpackage: 18 files, 0 test files
- test_lab/ subpackage: 14 files, 3 test files (logic only)
- InteractionController (drag-drop core) has no tests
- Formation input handler is only indirectly tested

## Target State

- Builder has test directory with key module tests
- InteractionController has comprehensive drag-drop tests
- Test lab panels have rendering tests
- Formation state machine is directly tested

## Phases

### Phase 1: Builder Core Infrastructure
**Files to create:**
- `tests/unit/ui/screens/builder/__init__.py`
- `tests/unit/ui/screens/builder/test_interaction_controller.py`
- `tests/unit/ui/screens/builder/test_event_bus.py`

**Coverage:**
- Drag-drop interactions (handle_event for all mouse events)
- Drop target registration
- Selection state management
- Event bus publish/subscribe

### Phase 2: Builder Panels
**Files to create:**
- `tests/unit/ui/screens/builder/test_layer_panel.py`
- `tests/unit/ui/screens/builder/test_schematic_view.py`
- `tests/unit/ui/screens/builder/test_modifier_logic.py`

**Coverage:**
- Layer panel component display
- Schematic view rendering
- Modifier restriction logic

### Phase 3: Test Lab UI
**Files to create:**
- `tests/unit/ui/screens/test_lab/test_ship_panels.py`
- `tests/unit/ui/screens/test_lab/test_results_panel.py`

**Coverage:**
- Ship panel rendering
- Results panel display and interaction
- Test executor callbacks

### Phase 4: Formation Input Handler
**Files to create:**
- `tests/unit/ui/screens/formation/test_input_handler.py`

**Coverage:**
- State machine transitions (IDLE, DRAGGING, BOX_SELECT, RESIZING, PANNING)
- Transition guards
- Calculation methods

### Phase 5: Workshop & Loaders
**Files to create:**
- `tests/unit/ui/screens/test_workshop_event_router.py`
- `tests/unit/ui/screens/test_workshop_data_loader.py`
- `tests/unit/ui/screens/test_race_asset_loader.py`
- `tests/unit/ui/screens/test_column_manager.py`
- `tests/unit/ui/screens/test_fleet_report_filters.py`

### Phase 6: Services & Utilities
**Files to update/create:**
- Update InputMapper tests for numpad
- Add ScreenshotManager edge case tests
- Add ShipFactory invalid design tests
- Expand DesignSelectorWindow tests

## Checklist

### Phase 1: Builder Core
- [ ] Create tests/unit/ui/screens/builder/
- [ ] Test InteractionController handle_event
- [ ] Test drop target registration
- [ ] Test clone operations (Alt+click)
- [ ] Test multi-placement (Shift+drop)
- [ ] Test event_bus publish/subscribe

### Phase 2: Builder Panels
- [ ] Test layer panel initialization
- [ ] Test schematic view component display
- [ ] Test modifier logic restrictions

### Phase 3: Test Lab
- [ ] Test ship panel rendering
- [ ] Test results panel display
- [ ] Test executor integration

### Phase 4: Formation
- [ ] Test state transitions
- [ ] Test DRAGGING_ITEMS state
- [ ] Test BOX_SELECT state
- [ ] Test RESIZING_GROUP state
- [ ] Test PANNING state

### Phase 5: Workshop
- [ ] Test event routing
- [ ] Test data loading/reloading
- [ ] Test asset loader fallbacks
- [ ] Test column toggling
- [ ] Test filter application

### Phase 6: Services
- [ ] Test numpad key mapping
- [ ] Test screenshot edge cases
- [ ] Test invalid design handling

## Dependencies

- May need to establish UI test patterns from battle UI project

## Risks

- Builder is complex; may need incremental approach
- Pygame mocking may be required for render tests
