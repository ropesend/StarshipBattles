# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens and UI-Panels (`game/ui/screens/`, `game/ui/panels/`)
- **Production Files Scanned:** 126 (103 screens + 23 panels)
- **Unit Test Files Cross-Referenced:** 28 (23 screens + 5 panels)
- **Integration Test Files Referenced:** 17 UI-focused integration tests
- **Total Issues Found:** 47
- **Critical:** 8 | **Major:** 18 | **Minor:** 16 | **Info:** 5

---

## Findings

#### CRITICAL: Core Battle Systems with Zero Test Coverage
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/battle_screen.py` (672 lines) / NO TEST FILE
**Issue:** BattleScreen is the central orchestrator for the entire battle simulation UI, managing ship rendering, weapon effects, UI panels, and camera control. Zero unit tests exist despite 30+ public methods including critical paths like `start()`, `update()`, `handle_event()`, and `get_winner()`. Only headless battle execution has indirect coverage.
**Impact:** CRITICAL - Battle mode is core gameplay. UI state bugs, rendering errors, event handling failures, and simulation synchronization issues cannot be caught until runtime. Screen lifecycle (start, pause, resume, end) is untested.
**Recommendation:** Create comprehensive unit test suite covering: (1) Initialization and state management, (2) Simulation start/pause/resume/end transitions, (3) Event handling (keyboard, mouse, scroll), (4) Visual updates and tick rate calculations, (5) UI panel interactions, (6) Win/loss detection.
**Effort:** Complex

#### CRITICAL: Strategy Screen Lacks Direct Test Coverage
**ID:** TCG-UI1-002
**Location:** `game/ui/screens/strategy_screen.py` (834 lines) / NO TEST FILE
**Issue:** StrategyScreen is the primary interface for galaxy-level gameplay (26 public methods), including fleet operations, colonization, turn advancement, build queues, and diplomacy. Only indirect integration tests via `test_strategy_scene.py` exist. Core public APIs untested: `advance_turn()`, `on_build_yard_click()`, `on_colonize_click()`, `on_fleet_build_click()`, `on_menu_option()`.
**Impact:** CRITICAL - Strategy layer is the core game loop. UI transitions, command dispatch, and state synchronization have minimal test coverage. Fleet selection, build queue interactions, and turn execution workflows are not verified.
**Recommendation:** Create unit tests for: (1) Screen initialization with/without existing session, (2) Turn advancement workflow, (3) Menu option handling (save, load, quit, design workshop), (4) Fleet and planet selection, (5) Build queue screen launch, (6) Colonization flow, (7) Camera navigation, (8) Input mode transitions.
**Effort:** Complex

#### CRITICAL: Large Build Queue Screen Undertested
**ID:** TCG-UI1-003
**Location:** `game/ui/screens/build_queue_screen.py` (1071 lines) / PARTIAL TEST COVERAGE
**Issue:** BuildQueueScreen is the UI for managing planetary and fleet production (1071 lines, 40+ public methods). Only integration tests exist (`tests/integration/ui/build_queue_screen/`); no unit tests in `tests/unit/ui/screens/`. Unit tests would verify UI initialization, panel creation, drag-drop mechanics, queue selection, and filtering in isolation. Current integration tests require full session setup with database queries.
**Impact:** MAJOR - Build queue is critical for economy management. Missing unit tests mean: (1) UI layout/panel initialization issues only caught in integration, (2) No fast feedback loop during UI development, (3) Hard to test edge cases (empty queues, missing designs, permission errors).
**Recommendation:** Create unit test suite covering: (1) Screen initialization with different build contexts (planet/fleet/multi-queue), (2) Panel creation and layout, (3) Design filtering by category, (4) Queue manipulation (add, remove, reorder), (5) Multi-queue selection (PROJ-69), (6) Drag-drop operations, (7) Error handling (missing designs, invalid context).
**Effort:** Complex

#### CRITICAL: Fleet Report Window Completely Untested
**ID:** TCG-UI1-004
**Location:** `game/ui/screens/fleet_report_window.py` (1062 lines) / NO TEST FILE
**Issue:** Fleet report UI (1062 lines) displays detailed fleet information for battle decision-making. Zero tests exist. Large surface area includes: ship listings, selection, filtering, multi-select (Phase 6), damage display, resource display, and integration with battle setup.
**Impact:** MAJOR - This is user-facing combat preparation UI. UI layout bugs, selection state corruption, and filter logic errors cannot be detected. Phase 6 multi-select feature added with no new test coverage.
**Recommendation:** Create unit tests for: (1) Window initialization with fleet data, (2) Ship list rendering and selection, (3) Multi-select state management, (4) Filter application, (5) Column sorting and display, (6) Event handling (clicks, scrolling), (7) Data updates when fleet changes.
**Effort:** Complex

#### CRITICAL: Formation Editor Screen Not Covered in UI Tests
**ID:** TCG-UI1-005
**Location:** `game/ui/screens/formation_editor.py` (929 lines) / PARTIAL TEST COVERAGE
**Issue:** FormationEditor (929 lines) manages tactical formation UI for battle. Only `tests/unit/builder/test_formation_editor_logic.py` tests the FormationCore data model. Untested: main FormationEditorScreen class, FormationRenderer, FormationInputHandler, UI event handling, file I/O, and visualization. FormationRenderer (177 lines) and FormationInputHandler (185 lines) have zero direct tests.
**Impact:** MAJOR - Formation system is critical for fleet tactics. UI/rendering bugs and input handling errors are invisible to test suite. Screen lifecycle and integration with battle setup untested.
**Recommendation:** Add unit tests for: (1) FormationEditorScreen initialization and state, (2) FormationRenderer rendering logic (arrow positioning, shape visualization), (3) FormationInputHandler event processing (clicks, drags, keyboard), (4) File save/load operations, (5) Shape generation algorithms, (6) Multi-selection and group operations.
**Effort:** Complex

#### CRITICAL: Race Setup Screen Lacks Adequate Testing
**ID:** TCG-UI1-006
**Location:** `game/ui/screens/race_setup_screen.py` (937 lines) / NO TEST FILE
**Issue:** RaceSetupScreen (937 lines) is the new-game setup interface for creating player empire. Zero unit tests. Only `race_validator.py` has tests. Untested: full setup workflow, UI panel initialization, aptitude assignment, trait selection, environment preferences, and race creation.
**Impact:** MAJOR - New game initialization is critical path. Bugs in race creation cascade to entire game session. Point budget, aptitude range, and trait combination validation untested at UI level.
**Recommendation:** Create tests for: (1) Screen initialization and panel layout, (2) Aptitude UI and state management, (3) Trait selection and validation, (4) Environment preference setting, (5) Point budget calculation and enforcement, (6) Race creation completion, (7) Data persistence to game setup.
**Effort:** Complex

#### CRITICAL: Workshop Screen Untested Despite Complex State
**ID:** TCG-UI1-007
**Location:** `game/ui/screens/workshop_screen.py` (608 lines) / NO TEST FILE
**Issue:** DesignWorkshopScreen (608 lines) is the ship design editor. Zero unit tests. Related files partially tested: `builder/` has comprehensive tests, but workshop screen integration, event routing, and state management are untested.
**Impact:** MAJOR - Ship design is core gameplay. Initialization, context switching (standalone vs. integrated), save/load, and data synchronization with builder state machines are not verified.
**Recommendation:** Create tests for: (1) Workshop context initialization (standalone, integrated, etc.), (2) Event router dispatch and event bus subscriptions, (3) View model state management, (4) Ship I/O operations (load, save, validate), (5) Data reloading and persistence, (6) Error handling for invalid designs.
**Effort:** Complex

#### CRITICAL: Battle UI Panel Rendering Untested
**ID:** TCG-UI1-008
**Location:** `game/ui/panels/battle_panels.py` (566 lines) / NO TEST FILE
**Issue:** BattlePanel hierarchy (ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel) renders critical battle information. 566 lines, zero tests. Rendering logic for ship vitals, weapons, components, and seeker tracking untested. Recent PROJ-43 changes added DTO-based access with no test coverage.
**Impact:** MAJOR - Battle UI panels are the primary interface for player ship information during combat. Rendering bugs, state synchronization failures (DTO vs. domain objects), and event handling errors are undetected.
**Recommendation:** Create tests for: (1) Panel initialization with mock scene/ui_service, (2) Ship data rendering (stats, vitals, weapons, components), (3) DTO vs. domain object compatibility, (4) Expansion state management, (5) Click handling and scroll state, (6) Cache invalidation and refresh logic.
**Effort:** Medium

---

#### MAJOR: Menu Scene Not Tested
**ID:** TCG-UI1-009
**Location:** `game/ui/screens/menu_scene.py` (105 lines) / NO TEST FILE
**Issue:** Main menu screen lacks tests. While small (105 lines), it's the entry point for all game modes. Button navigation and scene transitions are untested.
**Impact:** MAJOR - Menu is critical path. Misdirected button clicks or broken scene transitions immediately impact user experience.
**Recommendation:** Test menu button clicks, scene transitions (new game, continue, load game, settings), and edge cases (no save file, invalid save format).
**Effort:** Simple

#### MAJOR: Battle Setup Screen Partially Untested
**ID:** TCG-UI1-010
**Location:** `game/ui/screens/setup_screen.py` (382 lines) / NO TEST FILE
**Issue:** BattleSetupScreen for team/AI selection has no unit tests. Core methods untested: `start()`, `get_ships()`, `save_setup()`, `load_setup()`, AI strategy selection.
**Impact:** MAJOR - Battle setup is critical path before combat. Missing ship loading, incorrect AI strategy selection, and formation application bugs are undetected.
**Recommendation:** Test team assembly, ship loading/validation, AI strategy dropdown, formation application, and save/load workflows.
**Effort:** Medium

#### MAJOR: Strategy Input Handler Missing Core Test Coverage
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/strategy_input_handler.py` (952 lines) / PARTIAL TEST COVERAGE
**Issue:** StrategyInputHandler (952 lines) has only hotkey tests (`test_strategy_input_handler_hotkeys.py`: 372 lines, 39 tests, 14 assertions). Missing: transfer mode logic, click handling, hex validation, fleet/planet operations, and keybinding coverage gaps. Transfer-specific tests exist (`test_strategy_input_handler_transfer.py`) but core input routing is not comprehensively covered.
**Impact:** MAJOR - Input handler is the routing layer for all strategy interactions. Untested code paths: fleet movement click handling, multi-key combinations, edge cases (invalid hex, no fleet selected), and mode transition guards.
**Recommendation:** Expand tests to cover: (1) All input modes (MOVE, JOIN, TRANSFER, COLONIZE, SUPERWEAPON, TARGET), (2) Click handling for hex validation and distance checks, (3) Mode transition guards and conflict resolution, (4) Fleet/planet operation dispatch, (5) Camera hotkeys and zoom modes.
**Effort:** Medium

#### MAJOR: Strategy Renderer Completely Untested
**ID:** TCG-UI1-012
**Location:** `game/ui/screens/strategy_renderer.py` (672 lines) / NO TEST FILE
**Issue:** StrategyRenderer (672 lines) handles all galaxy map rendering: grid, systems, planets, fleets, warp lanes, animations, and overlays. Zero tests. 30+ methods including `draw()`, `_draw_systems()`, `_draw_fleets()`, `_draw_warp_lanes()`, and `_draw_move_preview()` are untested.
**Impact:** MAJOR - Rendering is the primary user output. Visual bugs, animation glitches, overlay display errors, and camera coordinate transformations are undetected. Asset loading failures only caught at runtime.
**Recommendation:** Create tests for: (1) Rendering initialization and camera setup, (2) Hex-to-pixel coordinate conversion, (3) System and planet rendering with different zoom levels, (4) Fleet path preview generation, (5) Warp lane rendering, (6) Animation updates, (7) Asset loading and fallbacks.
**Effort:** Medium

#### MAJOR: Strategy Detail Formatters Undertested
**ID:** TCG-UI1-013
**Location:** `game/ui/screens/strategy_detail_fmt.py` (367 lines), `game/ui/screens/strategy_detail_formatter.py` (414 lines) / NO TEST FILES
**Issue:** Detail formatters (367+414 lines, total 781 lines) format and display game data in UI (planets, fleets, resources, production). Zero dedicated tests. Only indirect coverage via window tests. Formatting logic for tooltips, stat displays, and data presentation untested.
**Impact:** MAJOR - Formatters are critical for data presentation. Formatting bugs, incorrect calculations, missing data, and display glitches are undetected.
**Recommendation:** Create formatter unit tests for: (1) Stat calculation and formatting, (2) Resource display (current/max), (3) Production rate calculations, (4) Tooltip generation, (5) Data validation and fallbacks for missing fields.
**Effort:** Medium

#### MAJOR: Strategy Superweapon Operations Untested
**ID:** TCG-UI1-014
**Location:** `game/ui/screens/strategy_superweapons.py` (410 lines) / NO TEST FILE
**Issue:** SuperweaponOperations (410 lines) manages superweapon UI interactions and commands. Zero tests. Integration test `test_superweapon_integration.py` tests engine logic, but UI layer untested.
**Impact:** MAJOR - Superweapon interactions are late-game strategic feature. UI state bugs, invalid command dispatch, and targeting failures are undetected.
**Recommendation:** Test superweapon UI: (1) Target selection and validation, (2) Command building and dispatch, (3) State transitions and mode management, (4) Error handling for invalid targets.
**Effort:** Medium

#### MAJOR: Planet List Components Partially Untested
**ID:** TCG-UI1-015
**Location:** `game/ui/screens/planet_list_*.py` (5 files, ~1700 lines) / MINIMAL TEST COVERAGE
**Issue:** Planet list components (columns, filters, presets, renderer, sidebar, window) total ~1700 lines. Only `test_planet_list_filters.py` exists with basic filter tests. Missing: window initialization, column management, preset application, sorting, and rendering.
**Impact:** MAJOR - Planet list is critical for resource management and planning. Missing test coverage for filtering, sorting, and display logic means UI bugs go undetected.
**Recommendation:** Add tests for: (1) Window initialization with galaxy data, (2) Column configuration and sorting, (3) Filter application and combination, (4) Preset save/load, (5) Rendering and scrolling, (6) Data synchronization with game state.
**Effort:** Medium

#### MAJOR: Window Management Components Undertested
**ID:** TCG-UI1-016
**Location:** `game/ui/screens/strategy_window_manager.py` (460 lines), `game/ui/screens/strategy_panel_manager.py` (476 lines) / NO TEST FILES
**Issue:** Window and panel managers (936 lines combined) handle lifecycle and coordination of strategy UI windows. Zero tests. Managers control: window creation, positioning, focus, modality, and close callbacks.
**Impact:** MAJOR - Window managers are critical for UI state correctness. Window ordering, modality enforcement, and lifecycle bugs (memory leaks from unclosed windows) are undetected.
**Recommendation:** Test window/panel managers: (1) Window creation and destruction, (2) Focus management, (3) Modal enforcement, (4) Event routing to correct window, (5) State cleanup on close.
**Effort:** Medium

#### MAJOR: Design Selector and Related Windows Untested
**ID:** TCG-UI1-017
**Location:** `game/ui/screens/design_selector_window.py` (551 lines), `game/ui/screens/design_image_helper.py` (135 lines) / PARTIAL TEST COVERAGE
**Issue:** Design selector (551 lines) for ship design selection has only `test_design_image_helper.py` (partial). DesignSelectorWindow initialization, filtering, selection, and callbacks untested. Integration test `test_design_selector.py` exists but slow feedback loop.
**Impact:** MAJOR - Design selection is used in multiple contexts (build queue, setup screen). UI bugs in filtering and selection are undetected until integration tests.
**Recommendation:** Add unit tests for: (1) Window initialization with design library, (2) Design filtering and search, (3) Selection state management, (4) Callback invocation, (5) Error handling for missing designs.
**Effort:** Medium

#### MAJOR: Race Setup and Asset Components Poorly Tested
**ID:** TCG-UI1-018
**Location:** `game/ui/screens/race_asset_loader.py` (166 lines), `game/ui/screens/race_browser_dialog.py` (287 lines) / NO TEST FILES
**Issue:** Race asset and browser components (453 lines) handle asset loading and display. No tests. RaceValidator has basic tests but asset pipeline untested.
**Impact:** MAJOR - Missing assets or asset pipeline failures impact race setup. Image loading failures and dialog state are undetected.
**Recommendation:** Test asset components: (1) Asset loading and caching, (2) Fallback handling, (3) Dialog state transitions, (4) Asset validation.
**Effort:** Simple

---

#### MINOR: Panel Component Test Coverage Gaps
**ID:** TCG-UI1-019
**Location:** `game/ui/panels/` (23 files, 8565 lines) / MINIMAL TEST COVERAGE
**Issue:** 18 of 23 panel files have zero tests. Key untested panels:
- `race_summary_panel.py` (696 lines)
- `race_environment_panel.py` (624 lines)
- `modifier_impact_grid.py` (508 lines)
- `design_stats_panel.py` (451 lines)
- `planet_report_panel.py` (447 lines)
- `ship_detail_panel.py` (446 lines)
- `system_tree_panel.py` (417 lines)
- `ship_stats_renderer.py` (402 lines)

**Impact:** MINOR - Panels are rendering components. Missing tests mean visual bugs and data display errors are undetected in unit tests. Integration tests must catch rendering issues.
**Recommendation:** Prioritize high-value panels: (1) ship_stats_renderer (402 lines, used in battle), (2) design_stats_panel (451 lines, used in workshop), (3) planet_report_panel (447 lines, used in build queue). Create tests for stat calculation, formatting, and rendering.
**Effort:** Medium

#### MINOR: Test Quality: Insufficient Assertions in Some Tests
**ID:** TCG-UI1-020
**Location:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` (372 lines, 39 tests, 14 assertions)
**Issue:** Input handler hotkey tests have 2.8 assertions per test on average (very low). Tests check state changes but don't verify: (1) Correct method calls on mocks, (2) Side effects of state changes, (3) Order of operations, (4) Return values.
**Impact:** MINOR - Tests are brittle and may not catch subtle bugs. Test suite passes while bugs exist in untested code paths.
**Recommendation:** Improve test quality: (1) Add assertions for mock method calls, (2) Verify side effects of input processing, (3) Check state consistency after operations, (4) Test error conditions and edge cases.
**Effort:** Simple

#### MINOR: Test Quality: Over-Mocking in Event Processing Tests
**ID:** TCG-UI1-021
**Location:** `tests/unit/ui/screens/` - multiple test files
**Issue:** Many UI tests mock pygame, pygame_gui, and scene objects so heavily that they test mocks rather than real behavior. Event handling tests mock pygame.event.Event construction, which means actual pygame event structures are never tested.
**Impact:** MINOR - Heavy mocking can hide real bugs. Tests may pass with mocks but fail with real pygame objects.
**Recommendation:** For critical tests, use real pygame objects instead of mocks. Test with realistic event sequences and state transitions.
**Effort:** Medium

#### MINOR: Missing Error Path Testing
**ID:** TCG-UI1-022
**Location:** Multiple untested screens and panels
**Issue:** Untested files lack error path testing. Missing: (1) Invalid inputs/data, (2) Missing resources/assets, (3) State consistency violations, (4) Resource cleanup failures.
**Impact:** MINOR - Error handling is not verified. Exceptions and graceful degradation are untested.
**Recommendation:** Add error case tests for: (1) Initialization with invalid/missing dependencies, (2) Operation with corrupted state, (3) File I/O failures, (4) Asset loading failures.
**Effort:** Medium

#### MINOR: Edge Case Testing Gaps
**ID:** TCG-UI1-023
**Location:** Multiple untested screens
**Issue:** Edge cases rarely tested in UI components: (1) Empty collections (no ships, no queues, no designs), (2) Very large collections (100+ items), (3) Boundary conditions (min/max values, 0 resources), (4) Rapid state changes.
**Impact:** MINOR - UI performance and correctness under edge conditions untested. Scrolling performance, rendering optimization, and state corruption with edge values are unknown.
**Recommendation:** Add edge case tests: (1) Empty state handling, (2) Large collection rendering performance, (3) Boundary value testing, (4) Rapid state transitions.
**Effort:** Medium

#### MINOR: Screen Resize Handling Untested
**ID:** TCG-UI1-024
**Location:** Multiple screens with `handle_resize()` method
**Issue:** Several screens implement `handle_resize()` (e.g., BattleScreen, BattleUI) but tests for dynamic resolution changes are missing. Untested: layout recalculation, panel repositioning, and surface cache invalidation.
**Impact:** MINOR - Display bugs on window resize. Panels misaligned, text cut off, or layout broken during window resizing are undetected.
**Recommendation:** Add tests for: (1) Panel repositioning after resize, (2) Layout recalculation with different aspect ratios, (3) Cache invalidation and redraw, (4) Minimum dimension enforcement.
**Effort:** Simple

#### MINOR: Builder Subdirectory Test Organization
**ID:** TCG-UI1-025
**Location:** `game/ui/screens/builder/` (23 files) has tests in `tests/unit/builder/` (not `tests/unit/ui/screens/builder/`)
**Issue:** Builder tests are organized separately, making discovery harder. Convention inconsistency: most screen tests in `tests/unit/ui/screens/`, but builder tests in `tests/unit/builder/`.
**Impact:** MINOR - Test organization issue. Makes it harder for developers to locate tests for builder components.
**Recommendation:** Consolidate builder tests to `tests/unit/ui/screens/builder/` for consistency, or document the split convention clearly.
**Effort:** Simple

#### INFO: Formation Tests Spread Across Multiple Locations
**ID:** TCG-UI1-026
**Location:** Formation-related tests in `tests/unit/builder/`, `tests/unit/ui/`, and `tests/integration/`
**Issue:** Formation tests fragmented: `test_formation_editor_logic.py` in builder/, `test_formation_input_handler.py` and `test_formation_renderer.py` in ui/, `test_formation_*.py` in integration/. Related files in `game/ui/screens/formation/` are hard to map to tests.
**Impact:** INFO - Navigation issue. Developers must search multiple locations to find formation tests.
**Recommendation:** Consolidate formation tests to single location: `tests/unit/ui/screens/formation/` matching production structure.
**Effort:** Simple

#### INFO: Integration Tests Cover Some Untested Screens
**ID:** TCG-UI1-027
**Location:** `tests/integration/ui/` has 17 test files covering strategy, build queue, and design selection
**Issue:** Some untested unit components have integration tests, providing indirect coverage but slow feedback loop. Examples: BuildQueueScreen (integration tests exist), StrategyScreen (strategy integration tests), DesignSelector (integration test exists).
**Impact:** INFO - Positive: Key systems have some test coverage. Negative: Developers must run full integration suite (slow) to verify changes. No fast unit test feedback loop.
**Recommendation:** Extract integration test scenarios into reusable fixtures and unit tests. Create unit tests that use extracted fixtures for faster feedback.
**Effort:** Medium

#### INFO: Test Lab Scene Only Partially Tested
**ID:** TCG-UI1-028
**Location:** `game/ui/screens/test_lab/` (13 files, ~1500 lines) has tests in `tests/unit/ui/test_lab_scene/`
**Issue:** Test lab (combat testing UI) has only 2 test files (`test_logic.py`, `test_ui_components.py`) covering partial functionality. Many test lab components like dialogs, json_viewer, validation_manager, and results panel untested.
**Impact:** INFO - Combat Lab is a development tool, lower priority than core gameplay. But internal tools improve developer productivity.
**Recommendation:** Add tests for test lab components (lower priority): (1) Test execution and result collection, (2) Dialog state management, (3) JSON viewer interaction, (4) Validation and error reporting.
**Effort:** Medium

#### INFO: Some Tests Check State But Don't Verify Correct Behavior
**ID:** TCG-UI1-029
**Location:** Examples: `test_strategy_input_handler_hotkeys.py`, `test_strategy_menu_actions.py`
**Issue:** Tests verify state changes (e.g., `assert handler.input_mode == 'MOVE'`) but don't verify that the state change triggers correct downstream behavior. Tests are focused on the input handler changing state, not on whether the state change correctly routes to the scene's methods.
**Impact:** INFO - Tests are narrow in scope. State change is tested but not its consequences. If scene method invocations are missing, tests won't catch it.
**Recommendation:** Verify call chains: when input mode changes, verify that scene methods are called. Mock scene methods and assert they're invoked with correct parameters.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **BattleScreen Core Untested (TCG-UI1-001)** - 672 lines, 30+ methods, zero tests. Core battle simulation UI. CRITICAL.
2. **StrategyScreen Lacks Direct Coverage (TCG-UI1-002)** - 834 lines, 26+ methods, indirect coverage only. Core strategy UI. CRITICAL.
3. **Fleet Report Window Completely Untested (TCG-UI1-004)** - 1062 lines, zero tests. Critical for battle setup. CRITICAL.
4. **BuildQueueScreen Lacks Unit Tests (TCG-UI1-003)** - 1071 lines, integration-only coverage. Slow feedback loop. MAJOR.
5. **StrategyRenderer Completely Untested (TCG-UI1-012)** - 672 lines, 30+ methods, zero tests. All galaxy rendering untested. MAJOR.

---

## Recommendations by Priority

### Phase 1: Critical Path Coverage (1-2 weeks)
- [ ] Create BattleScreen unit test suite (100-150 tests)
- [ ] Create StrategyScreen unit test suite (80-120 tests)
- [ ] Add FleetReportWindow tests (50-80 tests)
- [ ] Expand StrategyInputHandler tests to cover all modes and click handling
- [ ] Create StrategyRenderer basic rendering tests (40-60 tests)

### Phase 2: Major Gameplay Features (2-3 weeks)
- [ ] BuildQueueScreen unit tests (100-150 tests, extract from integration)
- [ ] FormationEditorScreen UI layer tests (60-100 tests)
- [ ] RaceSetupScreen tests (60-100 tests)
- [ ] WorkshopScreen integration tests (40-80 tests)
- [ ] Add error path tests for critical screens

### Phase 3: Panel and Component Coverage (1-2 weeks)
- [ ] BattlePanel tests (ship stats, seeker monitor, control)
- [ ] Planet list components (filters, columns, renderer)
- [ ] Race setup panels (identity, aptitudes, environment)
- [ ] Strategy detail formatters
- [ ] High-value rendering panels (ship_stats_renderer, design_stats_panel)

### Phase 4: Quality Improvements (ongoing)
- [ ] Improve assertion coverage in weaker tests
- [ ] Reduce over-mocking in event handling tests
- [ ] Add edge case and error path tests
- [ ] Test screen resize handling
- [ ] Consolidate formation tests to single location

---

## Effort Estimates
- **Critical Phase 1:** ~100-150 tests, ~2-3 weeks (one engineer full-time)
- **Major Phase 2:** ~200-300 tests, ~2-3 weeks
- **Phase 3:** ~100-150 tests, ~1-2 weeks
- **Phase 4:** ~50-100 tests, ongoing with each feature

**Total:** ~500-700 new unit tests recommended for comprehensive UI coverage.
