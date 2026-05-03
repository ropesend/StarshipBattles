# Prospective Project: Test Coverage -- Strategy and UI

## Overview
This project addresses all test coverage gaps in the strategy layer, UI screens, and UI framework. These are the highest-volume test gaps found in the sweep (71 findings), with entire subpackages having zero tests (builder/, test_lab/, formation/) and critical strategy systems lacking dedicated unit tests (planet_gen, FleetOrderProcessor, GameSession). Many UI screen test gaps are for complex screens with hundreds of lines of untested logic.

## Grouping Rationale
Strategy and UI test gaps are grouped together because: (1) they represent the "upper layers" of the architecture, (2) many UI tests require strategy layer fixtures and mocks, (3) some findings span both layers (e.g., facade DTO tests touch the strategy/UI boundary), and (4) they share similar testing challenges (heavy mocking of lower layers, event-driven testing patterns). The combined count of 71 findings is at the upper end of project scope but appropriate because most individual test files are Simple effort.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 71 total (7 Critical, 28 Major, 26 Minor, 10 Info)

## Suggested Execution Order
**Execute seventh** (Order 7), last. Strategy and UI tests depend on stable lower layers. Ideally, architecture violations should be fixed first (making UI classes more testable), legacy dead code should be removed (fewer things to test), and core/simulation tests should be written first (establishing test patterns and fixtures that UI tests can reuse).

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-001 | planet_gen.py Has No Dedicated Unit Tests | `game/strategy/data/planet_gen.` | Complex |
| TCG-STR-002 | FleetOrderProcessor Transfer Logic Has Test Gaps | `game/strategy/engine/fleet_ord` | Medium |
| TCG-STR-003 | GameSession.handle_command() Dispatch Has No Tests | `game/strategy/engine/game_sess` | Medium |
| TCG-UI1-001 | Entire builder/ subpackage has zero tests | `game/ui/screens/builder/` | Medium |
| TCG-UI1-002 | Entire test_lab/ subpackage has zero tests | `game/ui/screens/test_lab/` | Medium |
| TCG-UI1-003 | Entire formation/ subpackage has zero tests | `game/ui/screens/formation/` | Simple |
| TCG-UI1-004 | BattleScreen and BattleUI have zero unit tests | `game/ui/screens/battle_screen.` | Medium |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-004 | FleetBattleAdapter Has Minimal Test Coverage | `game/strategy/data/fleet_battl` | Medium |
| TCG-STR-005 | FleetResourceAggregator Lacks Atomic Operation Tests | `game/strategy/data/fleet_resou` | Medium |
| TCG-STR-006 | QuickstartBuilder.spawn_initial_complexes Tests Missing | `game/strategy/quickstart_build` | Medium |
| TCG-STR-007 | Superweapon Command Handlers Missing Error Path Tests | `game/strategy/engine/superweap` | Medium |
| TCG-STR-008 | DesignMetadata.from_design_file() and from_dict() Not Tested | `game/strategy/data/design_meta` | Medium |
| TCG-STR-009 | ColonizeValidator Chain Validation Not Tested | `game/strategy/validation/colon` | Simple |
| TCG-STR-010 | EmpireEconomyCalculator Registry Fallback Not Tested | `game/strategy/engine/empire_ec` | Simple |
| TCG-STR-011 | TurnEngine._process_tick() Integration Not Tested | `game/strategy/engine/turn_engi` | Medium |
| TCG-STR-012 | FleetCapabilityCalculator.can_build_type Not Tested | `game/strategy/data/fleet_capab` | Simple |
| TCG-STR-013 | ShipResourceManager Missing Boundary Tests | `game/strategy/data/ship_resour` | Simple |
| TCG-UI2-001 | ShipThemeManager.get_portrait_image() and get_thumbnail() Not Tested | `game/ui/assets/ship_theme_mana` | Simple |
| TCG-UI2-002 | Slider Widget Tests Have Weak Assertions | `tests/unit/ui/test_ui_widgets.` | Simple |
| TCG-UI2-003 | test_no_duplicate_color_values Is a No-Op | `tests/unit/ui/test_colors.py` | Simple |
| TCG-UI2-004 | Camera.update_input() Has No Direct Unit Tests | `game/ui/renderer/camera.py` | Medium |
| TCG-UI2-005 | game_renderer.py draw_ship() Overlay Mode Not Tested | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-006 | ShipFactory.setup_formation() Does Not Test Formation Logic | `game/ui/services/ship_factory.` | Simple |
| TCG-UI2-007 | Widgets Button.draw() and Slider.draw() Not Tested | `game/ui/widgets.py` | Medium |
| TCG-UI1-005 | battle_state_viewer.py has zero tests (619 lines) | `game/ui/screens/battle_state_v` | Simple |
| TCG-UI1-006 | galaxy_test/ subpackage has zero test coverage | `game/ui/screens/galaxy_test/` | Medium |
| TCG-UI1-007 | WorkshopViewModel has no direct tests (551 lines) | `game/ui/screens/workshop_viewm` | Medium |
| TCG-UI1-008 | FleetReportFilters and FleetReportViewModel No Tests | `game/ui/screens/fleet_report_f` | Simple |
| TCG-UI1-009 | ColumnManager has no tests (233 lines) | `game/ui/screens/column_manager` | Simple |
| TCG-UI1-010 | setup_data_io.py has no tests (233 lines) | `game/ui/screens/setup_data_io.` | Medium |
| TCG-UI1-011 | WorkshopShipIO has no tests (261 lines) | `game/ui/screens/workshop_ship_` | Medium |
| TCG-UI1-012 | 16 panel files have no tests | `game/ui/panels/` | Complex |
| TCG-UI1-013 | WorkshopEventRouter has no tests (496 lines) | `game/ui/screens/workshop_event` | Medium |
| TCG-UI1-014 | WorkshopDataLoader and WorkshopDataReloader No Tests | `game/ui/screens/workshop_data_` | Simple |
| TCG-UI1-015 | StrategyEventRouter, StrategyPanelManager No Tests | `game/ui/screens/strategy_event` | Medium |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-014 | ShipDisplayFormatter.get_resource_percent Not Tested | `game/strategy/data/ship_displa` | Simple |
| TCG-STR-015 | ShipCargoManager.load_cargo() and unload Not Tested | `game/strategy/data/ship_cargo_` | Simple |
| TCG-STR-016 | SuperweaponOrderProcessor._find_system_at_location Not Tested | `game/strategy/engine/superweap` | Simple |
| TCG-STR-017 | EventTypes Enum and EventLog Serialization Not Tested | `game/strategy/events/event_typ` | Simple |
| TCG-STR-018 | Facade DTO from_* Methods Missing Edge Case Tests | `game/strategy/facade/dto/` | Simple |
| TCG-STR-019 | RegionClassifier Has No Test for Ring/Band edge cases | `game/strategy/generation/regio` | Simple |
| TCG-STR-020 | placement_strategies.py DensityBasedPlacement Not Tested | `game/strategy/generation/place` | Simple |
| TCG-STR-021 | GameConfig and PlayerConfig Missing Validation Tests | `game/strategy/engine/game_conf` | Simple |
| TCG-UI2-008 | Camera.update() Target Following Does Not Test Smoothing | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-009 | ValidationService Does Not Test Thread Safety | `game/ui/services/validation_se` | Simple |
| TCG-UI2-010 | BattleUIService conftest mock_ship Uses deprecated pattern | `tests/unit/ui/services/battle_` | Simple |
| TCG-UI2-011 | Slider.handle_event() MOUSEBUTTONUP Return Not Tested | `game/ui/widgets.py` | Simple |
| TCG-UI2-012 | ShipIOAdapter Does Not Test save_ship Callback | `game/ui/services/ship_io_adapt` | Simple |
| TCG-UI2-013 | ComponentService.is_modifier_allowed() Does Not Test all paths | `game/ui/services/component_ser` | Simple |
| TCG-UI2-014 | DesignLoaderAdapter Does Not Test Default/Fallback paths | `game/ui/services/design_loader` | Simple |
| TCG-UI2-015 | game_renderer.py draw_hud() Does Not Test all branches | `game/ui/renderer/game_renderer` | Simple |
| TCG-UI1-016 | planet_list_presets.py, planet_list_sidebar.py No Tests | `game/ui/screens/planet_list_pr` | Simple |
| TCG-UI1-017 | builder_selection.py has no tests (110 lines) | `game/ui/screens/builder_select` | Simple |
| TCG-UI1-018 | build_queue_helpers.py has no tests (63 lines) | `game/ui/screens/build_queue_he` | Simple |
| TCG-UI1-019 | save_selection_window.py has no tests (330 lines) | `game/ui/screens/save_selection` | Medium |
| TCG-UI1-020 | new_game_setup_screen.py has no tests (603 lines) | `game/ui/screens/new_game_setup` | Medium |
| TCG-UI1-021 | empire_panel_window.py has no tests (526 lines) | `game/ui/screens/empire_panel_w` | Medium |
| TCG-UI1-022 | race_browser_dialog.py has no tests (290 lines) | `game/ui/screens/race_browser_d` | Medium |
| TCG-UI1-023 | build_queue_list_window.py and build_queue_detail No Tests | `game/ui/screens/build_queue_li` | Simple |
| TCG-UI1-024 | race_asset_loader.py has no tests (276 lines) | `game/ui/screens/race_asset_loa` | Medium |
| TCG-UI1-025 | workshop_context.py has no tests (158 lines) | `game/ui/screens/workshop_conte` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-022 | Test Organization -- Some Test Files in Wrong Directory | `Unknown` | Simple |
| TCG-STR-023 | Validation Module Has No __init__.py Tests | `tests/unit/strategy/validation` | Simple |
| TCG-STR-024 | Heavy Mock Usage in FleetOrderProcessor Tests (fragile) | `tests/unit/strategy/test_fleet` | Medium |
| TCG-UI2-016 | test_atlas_fallback_logic Is Empty (Pass-only) | `tests/unit/ui/test_sprites.py` | Simple |
| TCG-UI2-017 | Inconsistent Import Patterns in Service Tests | `Unknown` | Simple |
| TCG-UI2-018 | BattleUIService Integration Tests Are Confusing | `tests/unit/ui/services/battle_` | Simple |
| TCG-UI1-026 | Tests using inspect.getsource() verify structure not behavior | `tests/unit/ui/screens/test_pla` | Medium |
| TCG-UI1-027 | Some tests use .called instead of .assert_called() | `tests/unit/ui/screens/test_fle` | Simple |
| TCG-UI1-028 | Heavy mock usage in screen tests may mask real bugs | `Unknown` | Complex |
| TCG-UI1-029 | No tests for StrategyFleetOps or StrategyColonize | `game/ui/screens/strategy_fleet` | Medium |

## Affected Files

**Strategy:**
- `game/strategy/data/design_metadata.py`
- `game/strategy/data/fleet_battle_adapter.py`
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/data/fleet_resource_aggregator.py`
- `game/strategy/data/planet_gen.py`
- `game/strategy/data/ship_cargo_manager.py`
- `game/strategy/data/ship_display_formatter.py`
- `game/strategy/data/ship_resource_manager.py`
- `game/strategy/engine/empire_economy_calculator.py`
- `game/strategy/engine/fleet_order_processor.py`
- `game/strategy/engine/game_config.py`
- `game/strategy/engine/game_session.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `game/strategy/engine/turn_engine.py`
- `game/strategy/events/event_types.py`
- `game/strategy/facade/dto/`
- `game/strategy/generation/placement_strategies.py`
- `game/strategy/generation/region_classifier.py`
- `game/strategy/quickstart_builder.py`
- `game/strategy/validation/colonize_validator.py`

**UI:**
- `game/ui/assets/ship_theme_manager.py`
- `game/ui/panels/` (16 untested files)
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/screens/battle_screen.py`
- `game/ui/screens/battle_state_viewer.py`
- `game/ui/screens/build_queue_helpers.py`
- `game/ui/screens/build_queue_list_window.py`
- `game/ui/screens/builder/`
- `game/ui/screens/builder_selection.py`
- `game/ui/screens/column_manager.py`
- `game/ui/screens/empire_panel_window.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/ui/screens/formation/`
- `game/ui/screens/galaxy_test/`
- `game/ui/screens/new_game_setup_screen.py`
- `game/ui/screens/planet_list_presets.py`
- `game/ui/screens/race_asset_loader.py`
- `game/ui/screens/race_browser_dialog.py`
- `game/ui/screens/save_selection_window.py`
- `game/ui/screens/setup_data_io.py`
- `game/ui/screens/strategy_event_router.py`
- `game/ui/screens/strategy_fleet_ops.py`
- `game/ui/screens/test_lab/`
- `game/ui/screens/workshop_context.py`
- `game/ui/screens/workshop_data_loader.py`
- `game/ui/screens/workshop_event_router.py`
- `game/ui/screens/workshop_ship_io.py`
- `game/ui/screens/workshop_viewmodel.py`
- `game/ui/services/component_service.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/validation_service.py`
- `game/ui/widgets.py`

**Tests:**
- `tests/unit/strategy/`
- `tests/unit/ui/`

## Effort Estimate
- **Simple tasks:** 40
- **Medium tasks:** 28
- **Complex tasks:** 3
- **Overall scope:** Large

## Overlap with Existing Projects
- **PROJ-111** (Test Coverage - UI and Framework) - Direct overlap for UI findings. Should be merged or superseded.
- **PROJ-105** (Visual Regression Testing for UI Panels) - Partial overlap for UI panel test coverage.
- **PROJ-110** (Test Coverage - Core Systems) - No overlap (that project covers core, this one covers strategy and UI).

## Suggested Phases
1. **Phase 1: Strategy Data Layer Tests** - Write tests for planet_gen, FleetBattleAdapter, FleetResourceAggregator, DesignMetadata, ShipResourceManager, ShipCargoManager, FleetCapabilityCalculator.
2. **Phase 2: Strategy Engine Tests** - Write tests for GameSession command dispatch, FleetOrderProcessor transfers, TurnEngine tick processing, Superweapon error paths, EmpireEconomyCalculator, ColonizeValidator.
3. **Phase 3: UI Framework Tests** - Write tests for ShipThemeManager, Camera, Slider/Button widgets, ShipFactory formation, game_renderer draw methods, UI services.
4. **Phase 4: UI Screen Tests (Strategy)** - Write tests for StrategyEventRouter, StrategyPanelManager, WorkshopViewModel, WorkshopEventRouter, WorkshopDataLoader, column managers.
5. **Phase 5: UI Screen Tests (Combat and Builder)** - Write tests for BattleScreen, BattleStateViewer, builder/ subpackage, test_lab/ subpackage, formation/ subpackage, remaining untested screens and panels.
