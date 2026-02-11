# Phase 6: Workshop, Setup, and Complex Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for the remaining complex screens: WorkshopScreen, RaceSetupScreen, FormationEditor, FleetReportWindow, BuildQueueScreen, DesignSelectorWindow, and race asset components.
**Findings covered:** TCG-UI1-003, TCG-UI1-004, TCG-UI1-005, TCG-UI1-006, TCG-UI1-007, TCG-UI1-017, TCG-UI1-018, TCG-UI1-019
**Estimated tests:** ~100-140

---

## Task 6.1: WorkshopScreen Tests [Complex]
**Finding:** TCG-UI1-007
**Source:** `game/ui/screens/workshop_screen.py` (608 lines)
**Tests:** `tests/unit/ui/screens/test_workshop_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock WorkshopContext, EventBus, WorkshopViewModel, all panel classes

- [ ] Create `tests/unit/ui/screens/test_workshop_screen.py`

**Context initialization:**
- [ ] Test initialization with `WorkshopContext.standalone()` mode
- [ ] Test initialization with integrated mode (session parameter)
- [ ] Test context mode property returns correct mode

**Event routing:**
- [ ] Test `handle_event()` dispatches to WorkshopEventRouter
- [ ] Test EventBus subscription for component selection
- [ ] Test EventBus subscription for layer changes

**View model:**
- [ ] Test ship load updates WorkshopViewModel state
- [ ] Test component selection updates view model
- [ ] Test layer selection updates view model

**Ship I/O operations:**
- [ ] Test load ship calls WorkshopShipIO.load()
- [ ] Test save ship calls WorkshopShipIO.save()
- [ ] Test save with no current ship -> error handling
- [ ] Test validate ship calls WorkshopShipIO.validate()

**Data reloading:**
- [ ] Test data reload refreshes panels
- [ ] Test data reload preserves current selection

- [ ] Verify: `pytest tests/unit/ui/screens/test_workshop_screen.py -v`

**Notes:** WorkshopScreen has many panel dependencies. Use bypass-init to avoid creating all panels. Set panel mocks manually.

---

## Task 6.2: RaceSetupScreen Tests [Complex]
**Finding:** TCG-UI1-006
**Source:** `game/ui/screens/race_setup_screen.py` (937 lines)
**Tests:** `tests/unit/ui/screens/test_race_setup_screen.py` (NEW)
**Mocks:** Bypass-init or mock UIWindow; mock all sub-panels (RaceEnvironmentPanel, RaceAptitudesPanel, etc.)

- [ ] Create `tests/unit/ui/screens/test_race_setup_screen.py`

**Tab navigation:**
- [ ] Test TAB_SUMMARY is default/first tab
- [ ] Test tab switching updates visible panel
- [ ] Test all 7 tabs accessible (SUMMARY, IDENTITY, VISUALS, SHIPS, ENVIRONMENT, APTITUDES, DESCRIPTION)

**Data flow:**
- [ ] Test aptitude changes propagate to summary panel
- [ ] Test trait selection updates point budget
- [ ] Test environment preference changes update race config

**Race config creation:**
- [ ] Test creating race from current state produces valid RaceConfig
- [ ] Test RaceConfig includes all tab data (identity, visuals, environment, aptitudes)
- [ ] Test race save via RaceLibrary.save()
- [ ] Test race load from RaceLibrary populates all tabs

**Validation:**
- [ ] Test validation catches missing required fields
- [ ] Test validation checks point budget compliance

**Panel sub-components (stub tests):**
- [ ] Test RaceBrowserDialog opens and closes
- [ ] Test RaceValidator is called on save

- [ ] Verify: `pytest tests/unit/ui/screens/test_race_setup_screen.py -v`

**Notes:** RaceSetupScreen inherits from `pygame_gui.elements.UIWindow`. Use bypass-init to avoid UIWindow.__init__. Multiple sub-panels are tested individually in `tests/unit/ui/panels/`.

---

## Task 6.3: FormationEditor Screen Tests [Medium]
**Finding:** TCG-UI1-005
**Source:** `game/ui/screens/formation_editor.py` (929 lines)
**Tests:** `tests/unit/ui/screens/test_formation_editor_screen.py` (NEW)
**Mocks:** Mock FormationRenderer, FormationInputHandler; mock tkinter file dialogs

Existing tests: `test_formation_editor_logic.py` (FormationCore data model), `test_formation_input_handler.py`, `test_formation_renderer.py`. Missing: FormationEditorScreen class.

- [ ] Create `tests/unit/ui/screens/test_formation_editor_screen.py`

**FormationEditorScreen lifecycle:**
- [ ] Test initialization creates FormationCore, FormationRenderer, FormationInputHandler
- [ ] Test handle_event delegates to FormationInputHandler
- [ ] Test draw delegates to FormationRenderer
- [ ] Test update method (if present)

**File I/O:**
- [ ] Test save formation (mock tkinter filedialog.asksaveasfilename)
- [ ] Test load formation (mock tkinter filedialog.askopenfilename)
- [ ] Test save with no arrows -> saves empty formation
- [ ] Test load invalid JSON -> error handling

**Shape generation:**
- [ ] Test shape generation algorithms produce correct number of arrows
- [ ] Test shape generation with different shape_count values

**Screen integration:**
- [ ] Test return callback invoked when exiting
- [ ] Test formation data passed back to caller

- [ ] Verify: `pytest tests/unit/ui/screens/test_formation_editor_screen.py -v`

**Notes:** Tkinter import at module level. Tests must handle tkinter unavailability. Mock `filedialog` to prevent actual dialog popups.

---

## Task 6.4: FleetReportWindow Tests [Complex]
**Finding:** TCG-UI1-004
**Source:** `game/ui/screens/fleet_report_window.py` (1062 lines)
**Tests:** `tests/unit/ui/screens/test_fleet_report_window.py` (NEW) + existing `test_fleet_report_window_multi_select.py`
**Mocks:** Mock pygame_gui UIManager, UIWindow; mock fleet, empire, ships

- [ ] Create `tests/unit/ui/screens/test_fleet_report_window.py`

**Initialization:**
- [ ] Test window creation with fleet data
- [ ] Test window title includes fleet ID
- [ ] Test panel layout (left=summary, center=ship list, right=detail)

**Ship list:**
- [ ] Test ship list populates with fleet ships
- [ ] Test ship selection updates detail panel
- [ ] Test ship list with empty fleet -> shows "No ships" message

**Filtering and sorting:**
- [ ] Test ship list sorting by name
- [ ] Test ship list sorting by class
- [ ] Test ship list sorting by damage level

**Multi-select (PROJ-06):**
- [ ] Test multi-select mode toggle
- [ ] Test selecting multiple ships updates summary
- [ ] (Extend existing `test_fleet_report_window_multi_select.py` if needed)

**Close behavior:**
- [ ] Test close callback invoked on window close
- [ ] Test close cleans up resources

- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py -v`

**Notes:** FleetReportWindow inherits from UIWindow. Use bypass-init or create with minimal UIManager.

---

## Task 6.5: BuildQueueScreen Unit Tests [Complex]
**Finding:** TCG-UI1-003
**Source:** `game/ui/screens/build_queue_screen.py` (1071 lines, 40+ methods)
**Tests:** `tests/unit/ui/screens/test_build_queue_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock UIManager, session, build_context, design_library

Integration tests exist at `tests/integration/ui/build_queue_screen/`. This task adds fast unit tests.

- [ ] Create `tests/unit/ui/screens/test_build_queue_screen.py`

**Initialization:**
- [ ] Test init with Planet build context
- [ ] Test init with Fleet build context
- [ ] Test init with BuildContext wrapper

**Design filtering:**
- [ ] Test filter by category shows only matching designs
- [ ] Test filter reset shows all designs
- [ ] Test search text filters design list

**Queue operations:**
- [ ] Test add design to queue
- [ ] Test remove design from queue
- [ ] Test reorder queue items
- [ ] Test queue with max capacity behavior

**Multi-queue (PROJ-69):**
- [ ] Test BuildQueueSelector with multiple queue sources at hex
- [ ] Test queue switching between planet and fleet queues

**Event handling:**
- [ ] Test keyboard shortcuts (via InputMapper)
- [ ] Test close callback invoked on exit

- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen.py -v`

**Notes:** BuildQueueScreen is the largest screen (1071 lines). Focus unit tests on logic paths. Integration tests already cover full workflows.

---

## Task 6.6: DesignSelectorWindow Tests [Medium]
**Finding:** TCG-UI1-017
**Source:** `game/ui/screens/design_selector_window.py` (551 lines)
**Tests:** `tests/unit/ui/screens/test_design_selector_window.py` (NEW)
**Mocks:** Mock UIManager, DesignLibrary; mock design metadata objects

- [ ] Create `tests/unit/ui/screens/test_design_selector_window.py`

**Initialization:**
- [ ] Test init with "load" mode sets correct title
- [ ] Test init with "target" mode sets correct title
- [ ] Test init stores design_library reference

**Filtering:**
- [ ] Test filter by ship class
- [ ] Test filter by vehicle type
- [ ] Test text search filters by design name
- [ ] Test obsolete filter toggle
- [ ] Test combined filters

**Selection:**
- [ ] Test selecting design invokes on_select_callback with design ID
- [ ] Test double-click selects and closes
- [ ] Test no selection available when library is empty

- [ ] Verify: `pytest tests/unit/ui/screens/test_design_selector_window.py -v`

---

## Task 6.7: Race Asset Components [Simple]
**Finding:** TCG-UI1-018
**Source:** `game/ui/screens/race_asset_loader.py` (166 lines), `game/ui/screens/race_browser_dialog.py` (287 lines)
**Tests:** `tests/unit/ui/test_race_asset_loader.py` (existing, extend) + `tests/unit/ui/test_race_browser_dialog.py` (existing, extend)
**Mocks:** Mock file system, ShipThemeManager

- [ ] Test RaceAssetLoader with missing asset directory -> graceful handling
- [ ] Test RaceAssetLoader caching behavior (load once, return cached)
- [ ] Test RaceAssetLoader with invalid image files
- [ ] Test RaceBrowserDialog initialization with empty race library
- [ ] Test RaceBrowserDialog selection callback
- [ ] Test RaceBrowserDialog search filtering
- [ ] Verify: `pytest tests/unit/ui/test_race_asset_loader.py tests/unit/ui/test_race_browser_dialog.py -v`

---

## Task 6.8: High-Value Panel Coverage [Medium]
**Finding:** TCG-UI1-019
**Source:** Various panels in `game/ui/panels/` (highest-value: ship_stats_renderer, design_stats_panel, planet_report_panel)
**Tests:** `tests/unit/ui/panels/test_ship_stats_renderer.py` (NEW), `tests/unit/ui/panels/test_design_stats_panel.py` (NEW)
**Mocks:** Mock pygame surfaces, mock ship/design data

**ship_stats_renderer.py (402 lines):**
- [ ] Create `tests/unit/ui/panels/test_ship_stats_renderer.py`
- [ ] Test `draw_stat_bar()` with 0%, 50%, 100% values
- [ ] Test `draw_ship_info_header()` with mock ship data
- [ ] Test `draw_ship_vitals()` renders HP and shield bars
- [ ] Test `draw_ship_resources()` renders fuel, energy, ammo
- [ ] Test `draw_ship_weapons()` renders weapon list
- [ ] Test `draw_ship_components()` renders component list

**design_stats_panel.py (451 lines):**
- [ ] Create `tests/unit/ui/panels/test_design_stats_panel.py`
- [ ] Test panel initialization with design data
- [ ] Test stat calculation accuracy (mass, thrust, speed)
- [ ] Test stat display formatting

- [ ] Verify: `pytest tests/unit/ui/panels/test_ship_stats_renderer.py tests/unit/ui/panels/test_design_stats_panel.py -v`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
