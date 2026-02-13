# Prospective Project: Test Coverage - UI Components

## Overview
This project addresses critical test coverage gaps in the UI layer, including completely untested modules (Builder, Galaxy Test), minimally tested modules (Test Lab, Workshop), and numerous UI screens and panels lacking comprehensive tests. The UI layer represents the user-facing interface and bugs here directly impact player experience.

## Grouping Rationale
These findings all relate to test coverage gaps in the UI layer:
1. **Same layer** - All findings affect game/ui/ components
2. **Shared fix strategy** - Writing unit tests for UI components (may require pygame mocking)
3. **Priority by user impact** - Builder and Workshop affect ship design; critical user feature
4. **Common test infrastructure** - UI tests share similar patterns and mocking needs

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 34 total (2 Critical, 12 Major, 12 Minor, 8 Info)

## Suggested Execution Order
**Should be done THIRD** - After architecture and strategy engine tests. UI tests benefit from stable lower layers and can validate end-to-end behavior.

## Findings

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-UI2-001 | game_renderer.py Has No Test Coverage | `game/ui/renderer/game_renderer.py` | Medium |
| TCG-UI1-001 | Builder Module Completely Untested | `game/ui/screens/builder/` | Complex |

### Major (12)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-001 | PhysicsBody Has Minimal Direct Unit Tests | `game/engine/physics.py` | Medium |
| TCG-FND-002 | Research UI Components Have No Pygame-Integration Tests | `game/research/ui/` | Complex |
| TCG-UI1-002 | Test Lab Module Minimal Coverage | `game/ui/screens/test_lab/` | Medium |
| TCG-UI1-003 | Galaxy Test Module No Tests | `game/ui/screens/galaxy_test/` | Simple |
| TCG-UI1-004 | Formation Module Missing Core Tests | `game/ui/screens/formation/` | Simple |
| TCG-UI1-005 | Panel Files Missing Tests | `game/ui/panels/` | Medium |
| TCG-UI1-007 | Strategy Screen Complex Modules | `game/ui/screens/strategy_*.py` | Medium |
| TCG-UI1-008 | Workshop Data Components Untested | `game/ui/screens/workshop_*.py` | Medium |
| TCG-UI2-002 | ShipIOAdapter Has No Dedicated Tests | `game/ui/services/ship_io_adapter.py` | Simple |
| TCG-UI2-005 | DesignLoaderAdapter Missing Error Path Tests | `game/ui/services/design_loader_adapter.py` | Simple |
| TCG-FND-006 | TargetEvaluator Rule Processing Missing Tests | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-007 | AIControllerFactory Missing Error Path Tests | `game/ai/ai_factory.py` | Simple |

### Minor (12)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-UI2-003 | UIConfig Has No Tests | `game/ui/config.py` | Simple |
| TCG-UI2-006 | BattleUIService Missing Tests for Edge Cases | `game/ui/services/battle_ui_service.py` | Simple |
| TCG-UI2-007 | ValidationService Missing Boundary Value Tests | `game/ui/services/validation_service.py` | Simple |
| TCG-UI2-008 | SpriteManager Test Skips Production Directory | `game/ui/renderer/sprites.py` | Medium |
| TCG-UI2-010 | ShipThemeManager Tests Skip When Federation Missing | `game/ui/assets/ship_theme_manager.py` | Medium |
| TCG-UI2-012 | colors.py WHITE and BLACK Constants Not Tested | `game/ui/colors.py` | Simple |
| TCG-UI1-006 | BattlePanel Classes Undertested | `game/ui/panels/battle_panels.py` | Simple |
| TCG-UI1-009 | Fleet Report Components Undertested | `game/ui/screens/fleet_*.py` | Simple |
| TCG-UI1-011 | Planet List Components | `game/ui/screens/planet_list_*.py` | Simple |
| TCG-UI1-014 | Column Manager | `game/ui/screens/column_manager.py` | Simple |
| TCG-UI1-017 | Setup Screen Components | `game/ui/screens/setup_*.py` | Simple |
| TCG-UI1-018 | Empire Panel Window | `game/ui/screens/empire_panel_window.py` | Simple |

### Info (8)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-019 | Planet Population Model Edge Cases | `game/strategy/data/planet.py` | Simple |
| TCG-STR-020 | FleetDTO Build Validation | `game/strategy/facade/dto/fleet_dto.py` | Simple |
| TCG-UI2-009 | InputMapper Missing Tests for Modifier Combinations | `game/ui/services/input_mapper.py` | Simple |
| TCG-UI2-011 | ScreenshotManager capture() Region Clipping | `game/ui/services/screenshot_manager.py` | Simple |
| TCG-UI2-014 | test_atlas_fallback_logic Is Empty | `tests/unit/ui/test_sprites.py` | Simple |
| TCG-UI1-020 | Design Selector Window | `game/ui/screens/design_selector_window.py` | Simple |
| TCG-UI1-021 | Test Quality - Bypass-Init Pattern Usage | `tests/unit/ui/screens/` | Medium |
| TCG-UI1-022 | Test Quality - Mock Heavy Tests | `tests/unit/ui/screens/` | Medium |

## Affected Files

### UI Renderer
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`

### UI Screens - Builder
- `game/ui/screens/builder/` (17+ files)

### UI Screens - Test Lab
- `game/ui/screens/test_lab/` (14 files)

### UI Screens - Workshop
- `game/ui/screens/workshop_*.py` (5 files)

### UI Screens - Strategy
- `game/ui/screens/strategy_*.py` (7 files)
- `game/ui/screens/fleet_*.py`
- `game/ui/screens/planet_list_*.py`

### UI Panels
- `game/ui/panels/` (17 files, 8 with tests)

### UI Services
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/screenshot_manager.py`

### UI Assets and Config
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/assets/ship_theme_manager.py`

### Foundation (related)
- `game/engine/physics.py`
- `game/research/ui/`
- `game/ai/target_evaluator.py`
- `game/ai/ai_factory.py`

## Effort Estimate
- **Simple tasks:** 20
- **Medium tasks:** 10
- **Complex tasks:** 4
- **Overall scope:** Large

## Overlap with Existing Projects
- **PROJ-131 (test-coverage-strategy-ui)** - Direct overlap with UI test coverage
- **PROJ-124 (PROJ-E_ui-test-coverage)** - Direct overlap
- **PROJ-105 (Visual Regression Testing for UI Panels)** - Related UI testing

## Suggested Phases

### Phase 1: UI Services and Adapters (3-4 days)
Test the service layer that supports UI screens:
1. TCG-UI2-002: ShipIOAdapter tests
2. TCG-UI2-005: DesignLoaderAdapter error path tests
3. TCG-UI2-006, TCG-UI2-007: BattleUIService and ValidationService tests
4. TCG-UI2-003: UIConfig tests
5. TCG-UI2-009, TCG-UI2-011: InputMapper and ScreenshotManager tests

### Phase 2: Builder Module (5-7 days)
Address the completely untested builder module:
1. TCG-UI1-001: Create test infrastructure for builder module
2. Prioritize: modifier_logic.py, event_bus.py, interaction_controller.py
3. Add tests for grouping_strategies.py, drop_target.py
4. Add tests for remaining builder components

### Phase 3: Test Lab and Workshop (4-5 days)
1. TCG-UI1-002: Test Lab data_extractor.py, validation_manager.py, test_executor.py
2. TCG-UI1-008: Workshop ship_io.py, viewmodel.py, data_loader.py
3. Add remaining test lab component tests

### Phase 4: Panels and Core Screens (4-5 days)
1. TCG-UI1-005: Panel tests (planet_report, design_report, build_queue_drag)
2. TCG-UI2-001: game_renderer.py tests
3. TCG-UI1-006: BattlePanel additional tests
4. TCG-UI1-004: Formation module tests

### Phase 5: Strategy and List Screens (3-4 days)
1. TCG-UI1-007: Strategy screen module tests
2. TCG-UI1-009, TCG-UI1-011: Fleet report and planet list tests
3. TCG-UI1-003: Galaxy test module smoke tests
4. Remaining minor findings

### Phase 6: Foundation UI Components (2-3 days)
1. TCG-FND-001: PhysicsBody unit tests
2. TCG-FND-002: Research UI integration tests
3. TCG-FND-006, TCG-FND-007: AI component tests
