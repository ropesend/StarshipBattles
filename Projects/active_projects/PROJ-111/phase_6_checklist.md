# Phase 6: Workshop, Setup, and Complex Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for the remaining complex screens: WorkshopScreen, RaceSetupScreen, FormationEditor, FleetReportWindow, BuildQueueScreen, DesignSelectorWindow, and race asset components.
**Findings covered:** TCG-UI1-003, TCG-UI1-004, TCG-UI1-005, TCG-UI1-006, TCG-UI1-007, TCG-UI1-017, TCG-UI1-018, TCG-UI1-019
**Estimated tests:** ~100-140
**Actual tests:** 222 (27+25+30+24+22+35+13+46)

---

## Task 6.1: WorkshopScreen Tests [Complex]
**Finding:** TCG-UI1-007
**Source:** `game/ui/screens/workshop_screen.py` (608 lines)
**Tests:** `tests/unit/ui/screens/test_workshop_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock WorkshopContext, EventBus, WorkshopViewModel, all panel classes

- [x] Create `tests/unit/ui/screens/test_workshop_screen.py`

**Context initialization:**
- [x] Test initialization with `WorkshopContext.standalone()` mode
- [x] Test initialization with integrated mode (session parameter)
- [x] Test context mode property returns correct mode

**Event routing:**
- [x] Test `handle_event()` dispatches to WorkshopEventRouter
- [x] Test EventBus subscription for component selection

**View model:**
- [x] Test ship property returns viewmodel_ship
- [x] Test selected_components returns viewmodel selection
- [x] Test available_components returns viewmodel available

**Ship I/O operations:**
- [x] Test load ship calls WorkshopShipIO.load()
- [x] Test save ship calls WorkshopShipIO.save()
- [x] Test select target delegates to ship_io

**Data reloading:**
- [x] Test data reload rebuilds layer panel
- [x] Test data_reloader initialized

**Additional tests:**
- [x] Test error handling (show_error)
- [x] Test selection handling
- [x] Test lifecycle (cleanup, handle_resize)
- [x] Test button definitions (standalone vs integrated mode)
- [x] Test update loop
- [x] Test clear design
- [x] Test apply loaded ship

- [x] Verify: `pytest tests/unit/ui/screens/test_workshop_screen.py -v` (27 passed)

**Notes:** WorkshopScreen has many panel dependencies. Use bypass-init to avoid creating all panels. Set panel mocks manually.

---

## Task 6.2: RaceSetupScreen Tests [Complex]
**Finding:** TCG-UI1-006
**Source:** `game/ui/screens/race_setup_screen.py` (937 lines)
**Tests:** `tests/unit/ui/screens/test_race_setup_screen.py` (NEW)
**Mocks:** Bypass-init or mock UIWindow; mock all sub-panels (RaceEnvironmentPanel, RaceAptitudesPanel, etc.)

- [x] Create `tests/unit/ui/screens/test_race_setup_screen.py`

**Tab navigation:**
- [x] Test TAB_SUMMARY is default/first tab
- [x] Test tab switching updates visible panel
- [x] Test all 7 tabs accessible (SUMMARY, IDENTITY, VISUALS, SHIPS, ENVIRONMENT, APTITUDES, DESCRIPTION)
- [x] Test tab names match indices

**Data flow:**
- [x] Test aptitude changes update race config
- [x] Test identity panel syncs race name
- [x] Test environment preferences update config

**Race config creation:**
- [x] Test race config stores all tab data
- [x] Test save calls RaceLibrary.save()
- [x] Test load race populates all tabs

**Validation:**
- [x] Test validation checks required fields
- [x] Test validation catches missing name
- [x] Test validation checks point budget

**Additional tests:**
- [x] Test panel components (browser dialog open/close)
- [x] Test editing mode
- [x] Test callbacks
- [x] Test tab highlighting
- [x] Test navigation buttons

**Panel sub-components (stub tests):**
- [x] Test RaceBrowserDialog opens and closes
- [x] Test RaceValidator is called on save

- [x] Verify: `pytest tests/unit/ui/screens/test_race_setup_screen.py -v` (25 passed)

**Notes:** RaceSetupScreen inherits from `pygame_gui.elements.UIWindow`. Use bypass-init to avoid UIWindow.__init__. Multiple sub-panels are tested individually in `tests/unit/ui/panels/`.

---

## Task 6.3: FormationEditor Screen Tests [Medium]
**Finding:** TCG-UI1-005
**Source:** `game/ui/screens/formation_editor.py` (929 lines)
**Tests:** `tests/unit/ui/screens/test_formation_editor_screen.py` (NEW)
**Mocks:** Mock FormationRenderer, FormationInputHandler; mock tkinter file dialogs

Existing tests: `test_formation_editor_logic.py` (FormationCore data model), `test_formation_input_handler.py`, `test_formation_renderer.py`. Missing: FormationEditorScreen class.

- [x] Create `tests/unit/ui/screens/test_formation_editor_screen.py`

**FormationEditorScreen lifecycle:**
- [x] Test initialization creates FormationCore
- [x] Test initialization creates FormationRenderer
- [x] Test initialization creates FormationInputHandler
- [x] Test handle_event delegates to FormationInputHandler
- [x] Test draw delegates to FormationRenderer
- [x] Test update method calls ui_manager

**File I/O:**
- [x] Test save formation calls core.save_to_file
- [x] Test load formation calls core.load_from_file
- [x] Test save with no arrows saves empty formation

**Shape generation:**
- [x] Test generate_shape circle
- [x] Test generate_shape uses shape_count
- [x] Test generate_shape updates info

**Screen integration:**
- [x] Test return callback invoked when exiting
- [x] Test formation data accessible
- [x] Test handle_resize updates dimensions

**Property delegation:**
- [x] Test arrows property returns core arrows
- [x] Test arrow_attrs property returns core attrs
- [x] Test selected_indices property returns core selection
- [x] Test camera_zoom property returns renderer zoom
- [x] Test snap_enabled property returns renderer snap

**Core data operations:**
- [x] Test add_arrow delegates to core
- [x] Test delete_selected delegates to core
- [x] Test clone_selection delegates to core
- [x] Test clear_all delegates to core
- [x] Test move_arrow delegates to core

**Coordinate transforms:**
- [x] Test world_to_screen delegates to renderer
- [x] Test screen_to_world delegates to renderer
- [x] Test snap delegates to renderer

**Info update:**
- [x] Test update_info sets arrow count
- [x] Test update_info shows selection count

- [x] Verify: `pytest tests/unit/ui/screens/test_formation_editor_screen.py -v` (30 passed)

**Notes:** Tkinter import at module level. Tests must handle tkinter unavailability. Mock `filedialog` to prevent actual dialog popups.

---

## Task 6.4: FleetReportWindow Tests [Complex]
**Finding:** TCG-UI1-004
**Source:** `game/ui/screens/fleet_report_window.py` (1062 lines)
**Tests:** `tests/unit/ui/screens/test_fleet_report_window.py` (NEW) + existing `test_fleet_report_window_multi_select.py`
**Mocks:** Mock pygame_gui UIManager, UIWindow; mock fleet, empire, ships

- [x] Create `tests/unit/ui/screens/test_fleet_report_window.py`

**Initialization:**
- [x] Test window creation with fleet data
- [x] Test window title includes fleet ID
- [x] Test panel layout (left=summary, center=ship list, right=detail)

**Ship list:**
- [x] Test ship list populates with fleet ships
- [x] Test ship selection updates detail panel
- [x] Test ship list empty fleet shows message

**Filtering and sorting:**
- [x] Test ship list sorting by name
- [x] Test ship list sorting by class
- [x] Test ship list sorting toggles direction

**Multi-select (PROJ-06):**
- [x] Test multi-select mode toggle
- [x] Test selecting multiple ships updates summary
- [x] Test deselect maintains at least one

**Close behavior:**
- [x] Test close callback invoked on window close
- [x] Test close cleans up resources

**View model integration:**
- [x] Test view model manages ship list
- [x] Test view model update ships

**Column manager:**
- [x] Test column manager provides columns
- [x] Test column visibility toggle

**Detail panel:**
- [x] Test detail panel shows ship info
- [x] Test detail panel placeholder when no selection

**Remove ships:**
- [x] Test remove selected ships with empire
- [x] Test remove button updates with selection

**Summary:**
- [x] Test summary shows ship count
- [x] Test summary shows average HP

- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py -v` (24 passed)

**Notes:** FleetReportWindow inherits from UIWindow. Use bypass-init or create with minimal UIManager.

---

## Task 6.5: BuildQueueScreen Unit Tests [Complex]
**Finding:** TCG-UI1-003
**Source:** `game/ui/screens/build_queue_screen.py` (1071 lines, 40+ methods)
**Tests:** `tests/unit/ui/screens/test_build_queue_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock UIManager, session, build_context, design_library

Integration tests exist at `tests/integration/ui/build_queue_screen/`. This task adds fast unit tests.

- [x] Create `tests/unit/ui/screens/test_build_queue_screen.py`

**Initialization:**
- [x] Test init with Planet build context
- [x] Test init with Fleet build context
- [x] Test init stores session
- [x] Test init requires hex_coord
- [x] Test init requires galaxy

**Design filtering:**
- [x] Test filter by category shows only matching designs
- [x] Test filter reset shows all designs
- [x] Test search text filters design list

**Queue operations:**
- [x] Test add design to queue
- [x] Test remove design from queue
- [x] Test reorder queue items

**Multi-queue (PROJ-69):**
- [x] Test queue sources populated
- [x] Test queue switching between sources
- [x] Test selected_queue_indices tracks selection

**Event handling:**
- [x] Test keyboard shortcuts (via InputMapper)
- [x] Test close callback invoked on exit

**Controller integration:**
- [x] Test controller manages designs
- [x] Test controller filters designs

**Portrait loader:**
- [x] Test portrait loader initialized
- [x] Test resource icons loaded

**Queue selector:**
- [x] Test queue selector available
- [x] Test queue selector updates active source

- [x] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen.py -v` (22 passed)

**Notes:** BuildQueueScreen is the largest screen (1071 lines). Focus unit tests on logic paths. Integration tests already cover full workflows.

---

## Task 6.6: DesignSelectorWindow Tests [Medium]
**Finding:** TCG-UI1-017
**Source:** `game/ui/screens/design_selector_window.py` (551 lines)
**Tests:** `tests/unit/ui/screens/test_design_selector_window.py` (NEW)
**Mocks:** Mock UIManager, DesignLibrary; mock design metadata objects

- [x] Create `tests/unit/ui/screens/test_design_selector_window.py`

**Initialization:**
- [x] Test init with "load" mode sets correct title
- [x] Test init with "target" mode sets correct title
- [x] Test init stores design_library reference

**Filtering:**
- [x] Test filter by ship class
- [x] Test filter by vehicle type
- [x] Test text search filters by design name
- [x] Test obsolete filter toggle
- [x] Test combined filters

**Selection:**
- [x] Test selecting design invokes on_select_callback with design ID
- [x] Test double-click selects and closes
- [x] Test no selection available when library is empty

- [x] Verify: `pytest tests/unit/ui/screens/test_design_selector_window.py -v` (35 passed)

---

## Task 6.7: Race Asset Components [Simple]
**Finding:** TCG-UI1-018
**Source:** `game/ui/screens/race_asset_loader.py` (166 lines), `game/ui/screens/race_browser_dialog.py` (287 lines)
**Tests:** `tests/unit/ui/test_race_asset_loader.py` (existing, extend) + `tests/unit/ui/test_race_browser_dialog.py` (existing, extend)
**Mocks:** Mock file system, ShipThemeManager

- [x] Test RaceAssetLoader with missing asset directory -> graceful handling
- [x] Test RaceAssetLoader caching behavior (load once, return cached)
- [x] Test RaceAssetLoader with invalid image files
- [x] Test RaceBrowserDialog initialization with empty race library
- [x] Test RaceBrowserDialog selection callback
- [x] Test RaceBrowserDialog search filtering
- [x] Verify: `pytest tests/unit/ui/test_race_asset_loader.py tests/unit/ui/test_race_browser_dialog.py -v` (53 passed)

---

## Task 6.8: High-Value Panel Coverage [Medium]
**Finding:** TCG-UI1-019
**Source:** Various panels in `game/ui/panels/` (highest-value: ship_stats_renderer, design_stats_panel, planet_report_panel)
**Tests:** `tests/unit/ui/panels/test_ship_stats_renderer.py` (NEW), `tests/unit/ui/panels/test_design_stats_panel.py` (NEW)
**Mocks:** Mock pygame surfaces, mock ship/design data

**ship_stats_renderer.py (402 lines):**
- [x] Create `tests/unit/ui/panels/test_ship_stats_renderer.py`
- [x] Test `draw_stat_bar()` with 0%, 50%, 100% values
- [x] Test `get_hp_bar_color()` for HP coloring
- [x] Test `get_component_status_display()` for status text
- [x] Test `draw_ship_resources()` renders fuel, energy, ammo
- [x] Test RESOURCE_COLORS and RESOURCE_ORDER_PRIORITY constants

**design_stats_panel.py (451 lines):**
- [x] Create `tests/unit/ui/panels/test_design_stats_panel.py`
- [x] Test panel initialization with design data
- [x] Test stat calculation accuracy (mass, thrust, speed)
- [x] Test stat display formatting
- [x] Test StatRow helper class

- [x] Verify: `pytest tests/unit/ui/panels/test_ship_stats_renderer.py tests/unit/ui/panels/test_design_stats_panel.py -v` (46 passed)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new tests passing
- [x] No regressions: `pytest tests/ -n 12` (9684 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
