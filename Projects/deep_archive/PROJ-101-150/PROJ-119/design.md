# PROJ-119: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 7
- **Major:** 28
- **Selected for remediation:** 71

## Selected Findings Summary

### TCG-STR-001: planet_gen.py Has No Dedicated Unit Test
- **Severity:** Critical
- **Location:** `game/strategy/data/planet_gen.`
- **Effort:** Complex

### TCG-STR-002: FleetOrderProcessor Transfer Logic Has T
- **Severity:** Critical
- **Location:** `game/strategy/engine/fleet_ord`
- **Effort:** Medium

### TCG-STR-003: GameSession.handle_command() Dispatch Ha
- **Severity:** Critical
- **Location:** `game/strategy/engine/game_sess`
- **Effort:** Medium

### TCG-UI1-001: Entire builder/ subpackage has zero test
- **Severity:** Critical
- **Location:** `game/ui/screens/builder/`
- **Effort:** Medium

### TCG-UI1-002: Entire test_lab/ subpackage has zero tes
- **Severity:** Critical
- **Location:** `game/ui/screens/test_lab/`
- **Effort:** Medium

### TCG-UI1-003: Entire formation/ subpackage has zero te
- **Severity:** Critical
- **Location:** `game/ui/screens/formation/`
- **Effort:** Simple

### TCG-UI1-004: BattleScreen and BattleUI have zero unit
- **Severity:** Critical
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Medium

### TCG-STR-004: FleetBattleAdapter Has Minimal Test Cove
- **Severity:** Major
- **Location:** `game/strategy/data/fleet_battl`
- **Effort:** Medium

### TCG-STR-005: FleetResourceAggregator Lacks Atomic Ope
- **Severity:** Major
- **Location:** `game/strategy/data/fleet_resou`
- **Effort:** Medium

### TCG-STR-006: QuickstartBuilder.spawn_initial_complexe
- **Severity:** Major
- **Location:** `game/strategy/quickstart_build`
- **Effort:** Medium

### TCG-STR-007: Superweapon Command Handlers Missing Err
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Medium

### TCG-STR-008: DesignMetadata.from_design_file() and fr
- **Severity:** Major
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Medium

### TCG-STR-009: ColonizeValidator Chain Validation Not T
- **Severity:** Major
- **Location:** `game/strategy/validation/colon`
- **Effort:** Simple

### TCG-STR-010: EmpireEconomyCalculator Registry Fallbac
- **Severity:** Major
- **Location:** `game/strategy/engine/empire_ec`
- **Effort:** Simple

### TCG-STR-011: TurnEngine._process_tick() Integration N
- **Severity:** Major
- **Location:** `game/strategy/engine/turn_engi`
- **Effort:** Medium

### TCG-STR-012: FleetCapabilityCalculator.can_build_type
- **Severity:** Major
- **Location:** `game/strategy/data/fleet_capab`
- **Effort:** Simple

### TCG-STR-013: ShipResourceManager Missing Boundary Tes
- **Severity:** Major
- **Location:** `game/strategy/data/ship_resour`
- **Effort:** Simple

### TCG-UI2-001: ShipThemeManager.get_portrait_image() an
- **Severity:** Major
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### TCG-UI2-002: Slider Widget Tests Have Weak Assertions
- **Severity:** Major
- **Location:** `tests/unit/ui/test_ui_widgets.`
- **Effort:** Simple

### TCG-UI2-003: test_no_duplicate_color_values Is a No-O
- **Severity:** Major
- **Location:** `tests/unit/ui/test_colors.py`
- **Effort:** Simple

### TCG-UI2-004: Camera.update_input() Has No Direct Unit
- **Severity:** Major
- **Location:** `game/ui/renderer/camera.py`
- **Effort:** Medium

### TCG-UI2-005: game_renderer.py draw_ship() Overlay Mod
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### TCG-UI2-006: ShipFactory.setup_formation() Does Not T
- **Severity:** Major
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### TCG-UI2-007: Widgets Button.draw() and Slider.draw()
- **Severity:** Major
- **Location:** `game/ui/widgets.py`
- **Effort:** Medium

### TCG-UI1-005: battle_state_viewer.py has zero tests (6
- **Severity:** Major
- **Location:** `game/ui/screens/battle_state_v`
- **Effort:** Simple

### TCG-UI1-006: galaxy_test/ subpackage has zero test co
- **Severity:** Major
- **Location:** `game/ui/screens/galaxy_test/`
- **Effort:** Medium

### TCG-UI1-007: WorkshopViewModel has no direct tests (5
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_viewm`
- **Effort:** Medium

### TCG-UI1-008: FleetReportFilters and FleetReportViewMo
- **Severity:** Major
- **Location:** `game/ui/screens/fleet_report_f`
- **Effort:** Simple

### TCG-UI1-009: ColumnManager has no tests (233 lines, p
- **Severity:** Major
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Simple

### TCG-UI1-010: setup_data_io.py has no tests (233 lines
- **Severity:** Major
- **Location:** `game/ui/screens/setup_data_io.`
- **Effort:** Medium

### TCG-UI1-011: WorkshopShipIO has no tests (261 lines)
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_ship_`
- **Effort:** Medium

### TCG-UI1-012: 16 panel files have no tests
- **Severity:** Major
- **Location:** `game/ui/panels/`
- **Effort:** Complex

### TCG-UI1-013: WorkshopEventRouter has no tests (496 li
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_event`
- **Effort:** Medium

### TCG-UI1-014: WorkshopDataLoader and WorkshopDataReloa
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_data_`
- **Effort:** Simple

### TCG-UI1-015: StrategyEventRouter, StrategyPanelManage
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_event`
- **Effort:** Medium

### TCG-STR-014: ShipDisplayFormatter.get_resource_percen
- **Severity:** Minor
- **Location:** `game/strategy/data/ship_displa`
- **Effort:** Simple

### TCG-STR-015: ShipCargoManager.load_cargo() and unload
- **Severity:** Minor
- **Location:** `game/strategy/data/ship_cargo_`
- **Effort:** Simple

### TCG-STR-016: SuperweaponOrderProcessor._find_system_a
- **Severity:** Minor
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### TCG-STR-017: EventTypes Enum and EventLog Serializati
- **Severity:** Minor
- **Location:** `game/strategy/events/event_typ`
- **Effort:** Simple

### TCG-STR-018: Facade DTO from_* Methods Missing Edge C
- **Severity:** Minor
- **Location:** `game/strategy/facade/dto/`
- **Effort:** Simple

### TCG-STR-019: RegionClassifier Has No Test for Ring/Ba
- **Severity:** Minor
- **Location:** `game/strategy/generation/regio`
- **Effort:** Simple

### TCG-STR-020: placement_strategies.py DensityBasedPlac
- **Severity:** Minor
- **Location:** `game/strategy/generation/place`
- **Effort:** Simple

### TCG-STR-021: GameConfig and PlayerConfig Missing Vali
- **Severity:** Minor
- **Location:** `game/strategy/engine/game_conf`
- **Effort:** Simple

### TCG-UI2-008: Camera.update() Target Following Does No
- **Severity:** Minor
- **Location:** `game/ui/renderer/camera.py`
- **Effort:** Simple

### TCG-UI2-009: ValidationService Does Not Test Thread S
- **Severity:** Minor
- **Location:** `game/ui/services/validation_se`
- **Effort:** Simple

### TCG-UI2-010: BattleUIService conftest mock_ship Uses
- **Severity:** Minor
- **Location:** `tests/unit/ui/services/battle_`
- **Effort:** Simple

### TCG-UI2-011: Slider.handle_event() MOUSEBUTTONUP Retu
- **Severity:** Minor
- **Location:** `game/ui/widgets.py`
- **Effort:** Simple

### TCG-UI2-012: ShipIOAdapter Does Not Test save_ship Ca
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Simple

### TCG-UI2-013: ComponentService.is_modifier_allowed() D
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Simple

### TCG-UI2-014: DesignLoaderAdapter Does Not Test Defaul
- **Severity:** Minor
- **Location:** `game/ui/services/design_loader`
- **Effort:** Simple

### TCG-UI2-015: game_renderer.py draw_hud() Does Not Tes
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### TCG-UI1-016: planet_list_presets.py, planet_list_side
- **Severity:** Minor
- **Location:** `game/ui/screens/planet_list_pr`
- **Effort:** Simple

### TCG-UI1-017: builder_selection.py has no tests (110 l
- **Severity:** Minor
- **Location:** `game/ui/screens/builder_select`
- **Effort:** Simple

### TCG-UI1-018: build_queue_helpers.py has no tests (63
- **Severity:** Minor
- **Location:** `game/ui/screens/build_queue_he`
- **Effort:** Simple

### TCG-UI1-019: save_selection_window.py has no tests (3
- **Severity:** Minor
- **Location:** `game/ui/screens/save_selection`
- **Effort:** Medium

### TCG-UI1-020: new_game_setup_screen.py has no tests (6
- **Severity:** Minor
- **Location:** `game/ui/screens/new_game_setup`
- **Effort:** Medium

### TCG-UI1-021: empire_panel_window.py has no tests (526
- **Severity:** Minor
- **Location:** `game/ui/screens/empire_panel_w`
- **Effort:** Medium

### TCG-UI1-022: race_browser_dialog.py has no tests (290
- **Severity:** Minor
- **Location:** `game/ui/screens/race_browser_d`
- **Effort:** Medium

### TCG-UI1-023: build_queue_list_window.py and build_que
- **Severity:** Minor
- **Location:** `game/ui/screens/build_queue_li`
- **Effort:** Simple

### TCG-UI1-024: race_asset_loader.py has no tests (276 l
- **Severity:** Minor
- **Location:** `game/ui/screens/race_asset_loa`
- **Effort:** Medium

### TCG-UI1-025: workshop_context.py has no tests (158 li
- **Severity:** Minor
- **Location:** `game/ui/screens/workshop_conte`
- **Effort:** Simple

### TCG-STR-022: Test Organization -- Some Test Files in
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### TCG-STR-023: Validation Module Has No __init__.py Tes
- **Severity:** Info
- **Location:** `tests/unit/strategy/validation`
- **Effort:** Simple

### TCG-STR-024: Heavy Mock Usage in FleetOrderProcessor
- **Severity:** Info
- **Location:** `tests/unit/strategy/test_fleet`
- **Effort:** Medium

### TCG-UI2-016: test_atlas_fallback_logic Is Empty (Pass
- **Severity:** Info
- **Location:** `tests/unit/ui/test_sprites.py`
- **Effort:** Simple

### TCG-UI2-017: Inconsistent Import Patterns in Service
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple

### TCG-UI2-018: BattleUIService Integration Tests Are Co
- **Severity:** Info
- **Location:** `tests/unit/ui/services/battle_`
- **Effort:** Simple

### TCG-UI1-026: Tests using inspect.getsource() verify s
- **Severity:** Info
- **Location:** `tests/unit/ui/screens/test_pla`
- **Effort:** Medium

### TCG-UI1-027: Some tests use .called instead of .asser
- **Severity:** Info
- **Location:** `tests/unit/ui/screens/test_fle`
- **Effort:** Simple

### TCG-UI1-028: Heavy mock usage in screen tests may mas
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### TCG-UI1-029: No tests for StrategyFleetOps or Strateg
- **Severity:** Info
- **Location:** `game/ui/screens/strategy_fleet`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
