# Project Proposal: Test Coverage - UI Builder & Test Lab

## Overview

This project addresses the complete lack of test coverage in the ship builder UI subsystem and the minimal coverage in the test lab subsystem. These are major features with zero dedicated tests across 32+ production files.

## Rationale

The builder and test_lab subpackages are critical features:
- builder/ has 18 production files (~2000+ lines) with ZERO test files
- test_lab/ has 14 production files with only 3 test files covering data formatting
- InteractionController (drag-drop core) has no tests
- Ship design is a core gameplay feature completely untested at the UI level

This represents a significant risk - bugs in ship design UI would break core gameplay without any test detection.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| TCG-UI1-004 | Critical | InteractionController (drag-drop) has no tests | game/ui/screens/builder/interaction_controller.py | Medium |
| TCG-UI1-012 | Major | builder/ subpackage has no test files at all | game/ui/screens/builder/*.py | Complex |
| TCG-UI1-013 | Major | test_lab/ subpackage has minimal direct tests | game/ui/screens/test_lab/*.py | Medium |
| TCG-UI1-011 | Major | FormationInputHandler only has indirect coverage | game/ui/screens/formation/input_handler.py | Medium |
| TCG-UI1-017 | Minor | DesignSelectorWindow tests don't cover rendering | tests/unit/ui/screens/test_design_selector_window.py | Simple |
| TCG-UI1-018 | Minor | GalaxyTestScreen only has basic tests | game/ui/screens/galaxy_test/*.py | Simple |
| TCG-UI1-019 | Minor | race_asset_loader.py, workshop_data_loader.py have no tests | game/ui/screens/ | Simple |
| TCG-UI1-020 | Minor | column_manager.py and fleet_report_filters.py have no tests | game/ui/screens/ | Simple |
| TCG-UI1-021 | Minor | workshop_event_router.py, workshop_data_reloader.py have no tests | game/ui/screens/ | Simple |
| TCG-UI1-022 | Minor | setup_renderer.py has no tests | game/ui/screens/setup_renderer.py | Simple |
| TCG-UI2-005 | Minor | ShipThemeManager Missing Tests for Concurrency | game/ui/assets/ship_theme_manager.py | Complex |
| TCG-UI2-007 | Minor | InputMapper Missing Tests for Numpad Keys | game/ui/services/input_mapper.py | Simple |
| TCG-UI2-008 | Minor | ScreenshotManager Missing Tests for Edge Cases | game/ui/services/screenshot_manager.py | Simple |
| TCG-UI2-009 | Minor | ShipFactory Missing Tests for Invalid Designs | game/ui/services/ship_factory.py | Simple |

## Summary Statistics

- **Total Findings:** 14
- **Critical:** 1 | **Major:** 3 | **Minor:** 10
- **Estimated Effort:** Complex (due to builder subpackage scope)
- **Primary Location:** game/ui/screens/builder/, game/ui/screens/test_lab/

## Overlap with Active Projects

Potential overlap with:
- PROJ-142: 2_test_coverage_ui (overlapping scope)
- PROJ-136: Test Coverage - UI Components (overlapping)

**Recommendation:** This project focuses specifically on builder/test_lab subsystems. Can run in parallel with battle UI testing project.

## Success Criteria

1. `tests/unit/ui/screens/builder/` directory exists with test files
2. InteractionController has comprehensive drag-drop tests
3. Key builder modules (event_bus, modifier_logic, layer_panel) have tests
4. test_lab panel rendering and interaction tests exist
5. Formation input handler state machine is tested directly
