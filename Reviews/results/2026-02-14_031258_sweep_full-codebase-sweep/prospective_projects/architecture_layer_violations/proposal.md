# Project Proposal: Architecture Layer Violations

## Overview

This project addresses architecture drift findings including layer violations, god classes, and circular import workarounds. The focus is on restoring proper layer boundaries and reducing class complexity.

## Rationale

The codebase has documented architecture layers (Core, Simulation, Strategy, AI, UI) but several violations exist:
- Strategy layer imports from AI layer (CRITICAL - violates documented architecture)
- Multiple god classes exceed 1000 lines (maintainability risk)
- Circular import workarounds indicate structural coupling issues
- Presentation logic has leaked into strategy layer

These issues make the code harder to test, understand, and maintain.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| ADR-STR-001 | Critical | Strategy Layer Imports from AI Layer | game/strategy/adapters/simulation_adapter.py | Medium |
| ADR-FND-001 | Major | Research UI imports game.ui.renderer.camera | game/research/ui/research_scene.py | Medium |
| ADR-SIM-001 | Major | Ship Class is Approaching God Class Territory | game/simulation/entities/ship.py | Simple |
| ADR-SIM-002 | Major | Intentional Late Imports for Circular Dependency | game/simulation/ | Medium |
| ADR-STR-002 | Major | ShipDisplayFormatter in Strategy Layer | game/strategy/data/ship_display_formatter.py | Medium |
| ADR-STR-003 | Major | Circular Import Workaround in Galaxy | game/strategy/data/galaxy.py | Medium |
| ADR-UI2-001 | Major | ShipIO Direct Import of Simulation Entities | game/ui/services/ship_io.py | Medium |
| ADR-UI2-002 | Major | Camera Uses pygame.math.Vector2 | game/ui/renderer/camera.py | Simple |
| ADR-UI1-001 | Major | God Class - TestLabScreen (1906 lines) | game/ui/screens/test_lab/screen.py | Complex |
| ADR-UI1-002 | Major | God Class - fleet_report_window.py (1093 lines) | game/ui/screens/fleet_report_window.py | Medium |
| ADR-UI1-003 | Major | God Class - build_queue_screen.py (1084 lines) | game/ui/screens/build_queue_screen.py | Medium |
| ADR-UI1-004 | Major | God Class - weapons_panel.py (1037 lines) | game/ui/screens/builder/weapons_panel.py | Medium |
| ADR-FND-002 | Minor | Research UI subpackage uses pygame directly | game/research/ui/ | Medium |
| ADR-SIM-003 | Minor | Component Module Contains Multiple Concerns | game/simulation/components/ | Simple |
| ADR-STR-004 | Minor | Intentional Late Imports - Documented but Numerous | game/strategy/ | Complex |
| ADR-STR-005 | Minor | RGB Color Tuples in Game Config | game/strategy/engine/game_config.py | Simple |
| ADR-UI2-003 | Minor | Game Renderer Inline Import of ShipThemeManager | game/ui/renderer/game_renderer.py | Simple |
| ADR-UI1-005 | Minor | Near-God Classes (500-1000 lines) | game/ui/screens/ | Simple |
| ADR-UI1-006 | Minor | Inconsistent Cross-Layer Import Documentation | game/ui/screens/ | Simple |

## Summary Statistics

- **Total Findings:** 19
- **Critical:** 1 | **Major:** 11 | **Minor:** 7
- **Estimated Effort:** Complex (due to god class refactoring)
- **Primary Location:** game/strategy/, game/ui/screens/

## Overlap with Active Projects

Strong overlap with:
- PROJ-146: 6_architecture_consistency (likely duplicate)
- PROJ-132: Architecture Layer Violations (likely duplicate)
- PROJ-126: architecture-layer-fixes (likely duplicate)
- PROJ-123: PROJ-D_architecture-cleanup (overlapping)

**Recommendation:** Review PROJ-126, PROJ-132, PROJ-146 status before starting. This sweep provides fresh findings that may supplement or replace existing project plans.

## Success Criteria

1. Strategy layer no longer imports from AI layer directly
2. AIControllerFactory is injected via dependency injection
3. God classes are documented with refactoring notes (or refactored if time permits)
4. Circular import workarounds are documented with ADR
5. Layer violations have documented justifications or fixes
