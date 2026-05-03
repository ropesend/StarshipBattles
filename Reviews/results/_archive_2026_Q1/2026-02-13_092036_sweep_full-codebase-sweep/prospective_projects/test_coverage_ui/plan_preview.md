# [PROJ-XXX] Test Coverage - UI Components

## Status: Planning
## Created: 2026-02-13
## Source: Sweep 2026-02-13_092036_sweep_full-codebase-sweep

---

## Overview

Add comprehensive test coverage for UI layer components including completely untested modules (Builder, Galaxy Test), minimally tested modules (Test Lab, Workshop), and numerous screens and panels lacking tests.

### Problem Statement
The UI layer has significant test coverage gaps:
- Builder module (17+ files) has ZERO test coverage
- Test Lab module (14 files) has only 2 test files
- Workshop data components are untested
- Many panels and screens lack dedicated tests
- game_renderer.py has no tests despite being critical infrastructure

### Goals
1. Achieve test coverage for all currently untested UI modules
2. Add edge case and error path tests for existing partial coverage
3. Create reusable test fixtures for pygame/UI mocking
4. Document UI testing patterns for future development

### Success Criteria
- Builder module has test coverage for logic-heavy components
- Test Lab data extraction and validation are tested
- Workshop save/load operations are tested
- No untested production files in UI layer (except pure rendering)
- UI test suite runs in <60 seconds

---

## Design Decisions

### DD-001: UI Testing Strategy
**Decision:** Use mock-based testing without requiring pygame display
**Rationale:** Allows tests to run in CI without display server
**Alternatives considered:** Pygame headless mode (rejected - complex setup)

### DD-002: Test File Organization
**Decision:** Mirror production file structure in tests/unit/ui/
**Rationale:** Easy to locate tests, matches existing pattern
**Alternatives considered:** Flat test directory (rejected - doesn't scale)

### DD-003: Builder Module Priority
**Decision:** Test logic components first, UI components second
**Rationale:** modifier_logic.py, event_bus.py have testable logic; panels are mostly rendering
**Alternatives considered:** All-or-nothing (rejected - too large)

---

## Phases

### Phase 1: UI Services and Adapters
**Target:** TCG-UI2-* service findings
**Scope:** Service layer supporting UI screens
**Tests Required:** 15-20 new test methods

- [ ] Create test_ship_io_adapter.py
- [ ] Add design_loader_adapter error path tests
- [ ] Add battle_ui_service edge case tests
- [ ] Add validation_service boundary value tests
- [ ] Add UIConfig tests
- [ ] Add input_mapper and screenshot_manager tests

### Phase 2: Builder Module
**Target:** TCG-UI1-001
**Scope:** Completely untested builder module
**Tests Required:** 40-60 new test methods

- [ ] Create test infrastructure and fixtures for builder tests
- [ ] Create tests/unit/ui/screens/builder/ directory
- [ ] Add test_modifier_logic.py (highest priority)
- [ ] Add test_event_bus.py (highest priority)
- [ ] Add test_interaction_controller.py
- [ ] Add test_grouping_strategies.py
- [ ] Add test_drop_target.py
- [ ] Add tests for remaining components as time permits

### Phase 3: Test Lab and Workshop
**Target:** TCG-UI1-002, TCG-UI1-008
**Scope:** Minimally tested UI modules
**Tests Required:** 25-35 new test methods

- [ ] Add test_data_extractor.py for Test Lab
- [ ] Add test_validation_manager.py for Test Lab
- [ ] Add test_test_executor.py for Test Lab
- [ ] Add test_workshop_ship_io.py
- [ ] Add test_workshop_viewmodel.py
- [ ] Add test_workshop_data_loader.py

### Phase 4: Panels and Core Screens
**Target:** TCG-UI1-005, TCG-UI2-001, TCG-UI1-006, TCG-UI1-004
**Scope:** Panel and screen test gaps
**Tests Required:** 20-30 new test methods

- [ ] Add planet_report_panel tests
- [ ] Add design_report_panel tests
- [ ] Add build_queue_drag_handler tests
- [ ] Add game_renderer tests
- [ ] Add formation renderer boundary tests
- [ ] Add battle panel additional tests

### Phase 5: Strategy and List Screens
**Target:** TCG-UI1-007, TCG-UI1-009, TCG-UI1-011, TCG-UI1-003
**Scope:** Strategy-related UI screens
**Tests Required:** 15-20 new test methods

- [ ] Add strategy_fleet_ops tests
- [ ] Add strategy_colonization tests
- [ ] Add fleet_report_view_model tests
- [ ] Add planet list component tests
- [ ] Add galaxy_test smoke tests

### Phase 6: Foundation UI Components
**Target:** TCG-FND-001, TCG-FND-002, TCG-FND-006, TCG-FND-007
**Scope:** Foundation components used by UI
**Tests Required:** 10-15 new test methods

- [ ] Add PhysicsBody direct unit tests
- [ ] Add Research UI integration tests
- [ ] Add TargetEvaluator rule processing tests
- [ ] Add AIControllerFactory error path tests

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pygame dependency in tests | High | Create mock infrastructure upfront |
| Builder module complexity | Medium | Start with pure logic components |
| Test maintenance burden | Medium | Use shared fixtures and patterns |
| Slow test execution | Low | Use pytest marks for UI tests |

---

## Notes

- Builder module is the highest-priority gap due to user-facing impact
- Consider visual regression testing for pure rendering components (PROJ-105)
- UI tests should not require actual game data files
- Coordinate with PROJ-131 and PROJ-124 to avoid duplicate work
