# Test Coverage Gaps Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Production Files Scanned:** 125 (100 screens, 25 panels)
- **Test Files Cross-Referenced:** 60
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 9 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: No Tests for Builder Subsystem (14 Production Files)
**ID:** TCG-UI1-001
**Location:** `game/ui/screens/builder/*.py` (production) / No tests exist
**Issue:** The entire builder subsystem has NO test coverage. This includes 14 production files:
- `interaction_controller.py` - Drag-drop interaction handling (162 lines)
- `layer_panel.py` - Layer management panel
- `left_panel.py` - Component palette panel
- `right_panel.py` - Ship stats panel
- `schematic_view.py` - Ship schematic rendering
- `detail_panel.py` - Component detail view
- `weapons_panel.py` - Weapons display panel
- `drop_target.py` - Drop target interface
- `grouping_strategies.py` - Component grouping logic
- `modifier_config.py`, `modifier_row.py`, `modifier_logic.py` - Modifier system
- `preset_ui.py`, `stats_config.py`, `event_bus.py` - Supporting modules
**Impact:** Critical builder UI functionality (drag-drop, component placement, modifier editing) is completely untested. Any regression would go undetected.
**Recommendation:** Create comprehensive tests for `interaction_controller.py` and `layer_panel.py` as minimum coverage. Add integration tests for the full drag-drop workflow.
**Effort:** Complex (requires Pygame mocking patterns similar to existing battle_panels tests)

#### CRITICAL: No Tests for Ship Detail Panel
**ID:** TCG-UI1-002
**Location:** `game/ui/panels/ship_detail_panel.py` (production) / No test file exists
**Issue:** `ShipDetailPanel` (447 lines) has no test coverage. This panel handles:
- Ship damage visualization with color coding
- Component damage display organized by layer
- Layer collapse/expand toggle functionality
- Remove ship button event handling
- Resource display formatting
- Combat stats display (battles_survived, kills, experience)
**Impact:** Fleet management UI displays ship status. Incorrect damage colors, layer toggle bugs, or event handling issues would go undetected.
**Recommendation:** Create `tests/unit/ui/panels/test_ship_detail_panel.py` with tests for:
- `get_damage_color()` function boundary values (0, 0.49, 0.5, 0.74, 0.75, 1.0)
- `update_ship()` with None input (placeholder behavior)
- `toggle_layer()` state changes
- `process_event()` button handling
**Effort:** Medium

#### MAJOR: No Tests for Planet Report Panel
**ID:** TCG-UI1-003
**Location:** `game/ui/panels/planet_report_panel.py` (production) / No test file exists
**Issue:** `PlanetReportPanel` (509 lines) and its helper `compute_planet_production()` have no dedicated tests. The panel handles:
- Planet portrait rendering with type-based colors
- Atmosphere graph visualization
- Complexes list display
- Resource grid with icons and production rates
- Production rate calculation from facilities
**Impact:** Planet information display in build queue and strategy screens could have formatting/calculation bugs.
**Recommendation:** Create tests for `compute_planet_production()` pure function logic (mocked planet/facilities). Test `_format_compact_number()` edge cases (0, 999, 1000, 999999, 1000000).
**Effort:** Medium

#### MAJOR: No Tests for Design Report Panel
**ID:** TCG-UI1-004
**Location:** `game/ui/panels/design_report_panel.py` (production) / No test file exists
**Issue:** `DesignReportPanel` (284 lines) has no tests. It handles:
- Ship portrait loading with fallback to generated placeholder
- Ship name and class parsing (handles "Large Escort (Scout)" format)
- Delegation to `DesignStatsPanel`
- Placeholder display when no design selected
**Impact:** Design display in build queue and workshop could show incorrect ship class names or broken portraits.
**Recommendation:** Test portrait path generation logic, ship class parsing regex, and placeholder behavior.
**Effort:** Simple

#### MAJOR: No Tests for Strategy Widgets (AtmosphereGraph, SpectrumGraph)
**ID:** TCG-UI1-005
**Location:** `game/ui/panels/strategy_widgets.py` (production) / No test file exists
**Issue:** `AtmosphereGraph` (82 lines) and `SpectrumGraph` (96 lines) have no tests. These render scientific visualizations:
- AtmosphereGraph: Bar chart of atmospheric gas composition with logarithmic scaling
- SpectrumGraph: Star energy spectrum visualization
**Impact:** Scientific data visualization could have calculation errors (log scaling, normalization) or rendering issues.
**Recommendation:** Test render() output dimensions, verify logarithmic scaling math, test edge cases (empty atmosphere, zero values, max values).
**Effort:** Simple

#### MAJOR: No Tests for System Tree Panel
**ID:** TCG-UI1-006
**Location:** `game/ui/panels/system_tree_panel.py` (production) / No test file exists
**Issue:** System tree panel for displaying star system hierarchies has no test coverage.
**Impact:** Star system navigation/display could have bugs in tree structure building or collapse/expand logic.
**Recommendation:** Create unit tests for tree structure building from system data.
**Effort:** Medium

#### MAJOR: No Tests for Component Modifier Grid Panel
**ID:** TCG-UI1-007
**Location:** `game/ui/panels/component_modifier_grid_panel.py` (production) / No test file exists
**Issue:** Component modifier grid for ship building has no test coverage.
**Impact:** Modifier application UI could have bugs affecting ship customization.
**Recommendation:** Test modifier grid population and selection handling.
**Effort:** Medium

#### MAJOR: No Tests for Modifier Impact Grid
**ID:** TCG-UI1-008
**Location:** `game/ui/panels/modifier_impact_grid.py` (production) / No test file exists
**Issue:** Modifier impact visualization grid has no test coverage.
**Impact:** Players may see incorrect modifier impact calculations in UI.
**Recommendation:** Test impact calculation and grid cell rendering logic.
**Effort:** Simple

#### MAJOR: No Tests for Race Theme/Portrait/Flag Galleries
**ID:** TCG-UI1-009
**Location:** `game/ui/panels/race_theme_gallery.py`, `race_portrait_gallery.py`, `race_flag_gallery.py`, `base_gallery.py` (production) / No test files exist
**Issue:** Four gallery panels for race customization have no test coverage:
- `base_gallery.py` - Base gallery class
- `race_theme_gallery.py` - Ship theme selection
- `race_portrait_gallery.py` - Leader portrait selection
- `race_flag_gallery.py` - Empire flag selection
**Impact:** Race customization UI could have selection, navigation, or rendering bugs.
**Recommendation:** Test base gallery item selection, pagination, and callback invocation.
**Effort:** Medium

#### MAJOR: No Tests for Formation Editor Subsystem
**ID:** TCG-UI1-010
**Location:** `game/ui/screens/formation/*.py` (production) / No specific tests
**Issue:** Formation editor subsystem (`input_handler.py`, `renderer.py`) lacks dedicated tests. While `test_formation_editor_screen.py` exists, it may not cover the modular subsystem files.
**Impact:** Fleet formation editing could have input handling or rendering bugs.
**Recommendation:** Verify existing tests cover input_handler and renderer modules, add tests if missing.
**Effort:** Simple

#### MAJOR: Galaxy Test Screen No Tests
**ID:** TCG-UI1-011
**Location:** `game/ui/screens/galaxy_test/*.py` (production) / No test files exist
**Issue:** Galaxy test screen subsystem (4 files: screen.py, constants.py, galaxy_mode.py, system_mode.py) has no test coverage.
**Impact:** Galaxy visualization/debugging tool could have rendering or mode-switching bugs.
**Recommendation:** Low priority - this appears to be a development/debug tool, but basic smoke tests would prevent regressions.
**Effort:** Simple

#### MINOR: Incomplete Edge Case Testing for BattleScreen
**ID:** TCG-UI1-012
**Location:** `tests/unit/ui/test_battle_screen.py`
**Issue:** BattleScreen tests (159 lines, 9 tests) cover initialization and basic operations but miss:
- Resize handling edge cases
- UI overlay toggling
- Multiple projectile tracking at limits
- Battle end conditions with ties
**Impact:** Edge case bugs could cause crashes or incorrect battle outcomes.
**Recommendation:** Add tests for resize, overlay, and edge case battle conditions.
**Effort:** Simple

#### MINOR: Workshop Screen Tests Are Mock-Heavy
**ID:** TCG-UI1-013
**Location:** `tests/unit/ui/screens/test_workshop_screen.py`
**Issue:** Workshop screen tests (638 lines) use extensive mocking via `_make_workshop_screen()` bypass-init pattern. Many tests test mock interactions rather than actual behavior:
- Tests like `test_save_ship_delegates_to_ship_io()` just verify mock calls
- Property delegation tests set up properties manually then test them
- No integration with real ship/component data
**Impact:** Real integration bugs between workshop and ship systems could go undetected.
**Recommendation:** Add at least one integration test that creates a real workshop context and performs actual operations.
**Effort:** Medium

#### MINOR: Strategy Screen Missing Superweapon Targeting Tests
**ID:** TCG-UI1-014
**Location:** `tests/unit/ui/screens/test_strategy_screen.py` (1027 lines)
**Issue:** Strategy screen tests are comprehensive but lack coverage for:
- Superweapon input mode transitions
- Superweapon target selection validation
- Superweapon activation callbacks
**Impact:** Superweapon UI could have input mode or targeting bugs.
**Recommendation:** Add tests for `_superweapons` module integration.
**Effort:** Simple

#### MINOR: Build Queue Screen Missing Drag Handler Tests
**ID:** TCG-UI1-015
**Location:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Issue:** Build queue tests (548 lines, 39 tests) cover controller and selection but don't test:
- `BuildQueueDragHandler` integration (mouse event sequences)
- Queue item reordering via drag
- Drag preview rendering
**Impact:** Drag-drop functionality could have bugs in reordering logic.
**Recommendation:** Add tests for `_handle_drag_operations()` with mock mouse events.
**Effort:** Medium

#### MINOR: Test Lab Scene Tests Cover Only Logic, Not Screen
**ID:** TCG-UI1-016
**Location:** `tests/unit/ui/test_lab_scene/` (77 tests across 2 files)
**Issue:** Test lab scene tests cover `formatting_utils.py` and UI component calculations but don't test:
- `screen.py` main screen class
- `test_executor.py` test running logic
- `validation_manager.py` test validation
- `ship_panels.py` panel rendering
**Impact:** Test lab screen could have bugs in test execution or result display.
**Recommendation:** Add tests for screen initialization and test execution flow.
**Effort:** Medium

#### INFO: Panels Module Missing __init__ Tests
**ID:** TCG-UI1-017
**Location:** `game/ui/panels/__init__.py`
**Issue:** No test verifies that all panel exports are correctly configured in `__init__.py`.
**Impact:** Import errors could occur if exports are misconfigured.
**Recommendation:** Add an import smoke test in `tests/unit/ui/test_ui_imports.py`.
**Effort:** Simple

#### INFO: Test Patterns Vary Between Screen Tests
**ID:** TCG-UI1-018
**Location:** Multiple test files in `tests/unit/ui/screens/`
**Issue:** Different test files use different patterns:
- Some use `_make_*_screen()` helpers with bypass-init
- Some use direct construction
- Some use fixtures, others don't
- Mocking approaches vary (patch.dict vs patch.object)
**Impact:** Maintenance burden, inconsistent test quality.
**Recommendation:** Document preferred testing patterns in a testing guidelines file.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-UI1-001 (CRITICAL)**: Builder subsystem (14 files) has ZERO test coverage - critical UI functionality for ship design is completely untested.

2. **TCG-UI1-002 (CRITICAL)**: ShipDetailPanel (447 lines) has no tests - damage visualization and ship management UI untested.

3. **TCG-UI1-003 (MAJOR)**: PlanetReportPanel (509 lines) including `compute_planet_production()` has no tests - production calculations could be wrong.

4. **TCG-UI1-009 (MAJOR)**: Race customization galleries (4 panels) have no tests - race setup UI untested.

5. **TCG-UI1-005 (MAJOR)**: Scientific visualization widgets (SpectrumGraph, AtmosphereGraph) have no tests - mathematical calculations in rendering untested.
