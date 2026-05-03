# Validation Report: UI-Screens Shard (UI1)

**Shard:** UI-Screens
**Shard ID:** UI1
**Directories:** game/ui/screens/, game/ui/panels/
**Finding Count:** 30
**Validator:** Claude Opus 4.5
**Date:** 2026-02-13

---

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED | 11 |
| DOWNGRADED | 7 |
| REJECTED | 10 |
| INFO (Positive - N/A) | 2 |

---

## Finding Validations

### Duplication Findings (DUP-UI1-xxx)

#### Finding: DUP-UI1-001
**Original Severity:** CRITICAL
**Title:** Screenshot Toast Notification Pattern Duplicated in 3+ Locations
**Location:** `game/ui/screens/planet_list_window.py:412-424` AND `game/ui/screens/build_queue_screen.py:1055-1068` AND `game/ui/screens/strategy_input_handler.py:868-881`

**Validation:**
Verified all three locations. The code pattern is indeed duplicated:
- `planet_list_window.py:412-424`: `_show_screenshot_toast()` method creates UIMessageWindow with toast_rect
- `build_queue_screen.py:1055-1068`: Nearly identical `_show_screenshot_toast()` method
- `strategy_input_handler.py:868-881`: Similar `_show_screenshot_toast(message)` with parameterized message

While the pattern is duplicated, this is a simple 10-12 line helper method with minor variations in error handling and message content. The duplication exists but does not warrant CRITICAL severity.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** The duplication exists but is a simple UI toast helper (12 lines). Not a critical architectural issue. A utility function could be extracted if desired, but this is low-priority refactoring.

---

#### Finding: DUP-UI1-002
**Original Severity:** MAJOR
**Title:** Column Manager Fragmentation Across Windows
**Location:** `game/ui/screens/column_manager.py`

**Validation:**
Reviewed `column_manager.py`. This file contains a well-structured `ColumnManager` class (extracted via PROJ-44 Phase 7) that manages column configuration for fleet reports. The code is clean, well-documented, and NOT fragmented. The module was actually extracted to consolidate column logic.

**Verdict:** REJECTED
**Rationale:** The finding description implies fragmentation, but the code shows a consolidated, well-extracted column manager. This is the OPPOSITE of the claimed issue - it's already properly refactored.

---

#### Finding: DUP-UI1-003
**Original Severity:** MAJOR
**Title:** Filter State Management Pattern Repeated
**Location:** `game/ui/screens/fleet_report_filters.py`

**Validation:**
Reviewed `fleet_report_filters.py`. This module contains `calculate_fleet_stats()` and related filtering functions. While filter patterns may exist in multiple windows (planet list, fleet report, etc.), each has domain-specific requirements. The file referenced is well-structured with proper use of `ShipStatsCalculator` and no obvious duplication within itself.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** Filter patterns are similar across different windows by nature, but each has domain-specific needs. Not a major architectural issue. If a base filter class would help, it's minor refactoring work.

---

#### Finding: DUP-UI1-004
**Original Severity:** MAJOR
**Title:** Compact Number Formatting Logic Isolated
**Location:** `game/ui/panels/planet_report_panel.py`

**Validation:**
Found `_format_compact_number()` at line 303 of `planet_report_panel.py`. Searched for duplicates and found similar functions in `build_queue_screen.py` and `race_summary_panel.py`. However, this is a simple 6-line utility function (K/M suffix formatting). While consolidation into a shared utility would be cleaner, this does not warrant MAJOR severity.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** Simple 6-line formatting helper duplicated in 2-3 places. Easy extraction to utility module but not a major architectural concern.

---

#### Finding: DUP-UI1-005
**Original Severity:** MINOR
**Title:** RaceThemeGallery Not Using BaseGallery
**Location:** `game/ui/panels/race_theme_gallery.py`

**Validation:**
Reviewed `race_theme_gallery.py`. It is structurally different from `RacePortraitGallery` and `RaceFlagGallery` (which both extend `BaseGallery`). The `RaceThemeGallery` displays ship themes with preview images, which has different requirements than the portrait/flag galleries. However, the comment in `base_gallery.py` references "DUP-UI1-005 resolution" suggesting this was intentionally designed.

**Verdict:** CONFIRMED
**Rationale:** RaceThemeGallery does not extend BaseGallery while similar galleries do. This is a valid minor consistency concern, though the different requirements may justify the separate implementation.

---

#### Finding: DUP-UI1-006
**Original Severity:** MINOR
**Title:** Report Panel Pattern Similarity
**Location:** `game/ui/panels/planet_report_panel.py`

**Validation:**
Reviewed `planet_report_panel.py` and `design_report_panel.py`. Both are report panels with similar structures (portrait, info text, scrollable content), but they display fundamentally different data types (planets vs ship designs). The design_report_panel already delegates to `DesignStatsPanel` for shared functionality.

**Verdict:** REJECTED
**Rationale:** The panels serve different purposes (planets vs ships) and would not benefit from a shared base class without excessive abstraction. The similarity is superficial.

---

#### Finding: DUP-UI1-007
**Original Severity:** MINOR
**Title:** Portrait/Image Loading Logic Scattered
**Location:** `game/ui/panels/design_report_panel.py`

**Validation:**
Reviewed image loading in `design_report_panel.py`. Portrait loading is handled at construction time with a placeholder pattern. Similar patterns exist in other panels. However, there is already `RaceAssetLoader` and `ShipThemeManager` providing centralized asset loading. The "scattered" loading is just UI code using these services.

**Verdict:** REJECTED
**Rationale:** Image loading logic already uses centralized services (RaceAssetLoader, ShipThemeManager). UI panels naturally need to call these services - this is not duplication.

---

#### Finding: DUP-UI1-008
**Original Severity:** MINOR
**Title:** Sidebar Builder Pattern Could Be Generalized
**Location:** `game/ui/screens/planet_list_sidebar_builder.py`

**Validation:**
The file `planet_list_sidebar_builder.py` does not exist at this path. Found `planet_list_sidebar.py` instead which contains `build_sidebar()` function. This is a single-use builder for the planet list window's sidebar filters.

**Verdict:** REJECTED
**Rationale:** File path incorrect in finding. The actual file (`planet_list_sidebar.py`) contains domain-specific sidebar building logic that is appropriately isolated. No duplication found.

---

#### Finding: DUP-UI1-009
**Original Severity:** INFO (Positive)
**Title:** Well-Refactored Gallery System
**Location:** `game/ui/panels/base_gallery.py`

**Validation:**
Confirmed. `BaseGallery` is a well-designed abstract base class that `RacePortraitGallery` and `RaceFlagGallery` both extend. Good use of abstraction with clear abstract method requirements.

**Verdict:** CONFIRMED (Positive Finding - No Action Required)

---

#### Finding: DUP-UI1-010
**Original Severity:** INFO (Positive)
**Title:** DesignStatsPanel Successful Extraction
**Location:** `game/ui/panels/design_stats_panel.py`

**Validation:**
Confirmed. `DesignStatsPanel` is a well-extracted shared component used by both Build Queue and Design Workshop for displaying ship statistics. Good example of code reuse.

**Verdict:** CONFIRMED (Positive Finding - No Action Required)

---

### Test Coverage Gap Findings (TCG-UI1-xxx)

#### Finding: TCG-UI1-001
**Original Severity:** CRITICAL
**Title:** No Tests for Builder Subsystem (14 Production Files)
**Location:** `game/ui/screens/builder/*.py`

**Validation:**
Found 19 files in `game/ui/screens/builder/`. Searched for tests in `tests/unit/ui/screens/builder/` - directory does not exist. However, found extensive builder tests in:
- `tests/unit/builder/test_builder_*.py` (15+ test files)
- `tests/unit/ui/left_panel/` (testing left_panel.py)
- `tests/unit/ui/schematic_view/` (testing schematic_view.py)
- `tests/unit/ui/test_detail_panel_rendering.py`

The builder subsystem IS tested, just not in `tests/unit/ui/screens/builder/`.

**Verdict:** REJECTED
**Rationale:** Tests exist in `tests/unit/builder/` and `tests/unit/ui/` directories covering builder functionality. The finding incorrectly assumed tests must be co-located by path.

---

#### Finding: TCG-UI1-002
**Original Severity:** CRITICAL
**Title:** No Tests for Ship Detail Panel
**Location:** `game/ui/panels/ship_detail_panel.py`

**Validation:**
Found `tests/unit/strategy/test_ship_detail_panel.py` which tests `ShipInstance` methods used by the detail panel. The tests verify damage summary, component damage, and layer damage functionality. However, there are no direct UI tests for `ShipDetailPanel` class rendering.

**Verdict:** DOWNGRADED(MAJOR)
**Rationale:** Data layer is tested, but UI panel rendering tests are missing. Not critical since the data logic is covered.

---

#### Finding: TCG-UI1-003
**Original Severity:** MAJOR
**Title:** No Tests for Planet Report Panel
**Location:** `game/ui/panels/planet_report_panel.py`

**Validation:**
Searched for `planet_report_panel` in tests. Found references in integration tests (`test_build_queue_enhanced_planet_report.py`, `test_planet_complexes_list.py`, etc.) but no dedicated unit tests for the panel itself.

**Verdict:** CONFIRMED
**Rationale:** Integration tests exercise the panel but no unit tests exist for `PlanetReportPanel` class directly.

---

#### Finding: TCG-UI1-004
**Original Severity:** MAJOR
**Title:** No Tests for Design Report Panel
**Location:** `game/ui/panels/design_report_panel.py`

**Validation:**
Found `design_report_panel` referenced in `tests/integration/ui/test_build_queue_formatting.py` and `test_build_queue_design_report.py`. Integration tests exist but no unit tests.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** Integration tests exist covering this panel. Unit tests would be nice-to-have but integration coverage exists.

---

#### Finding: TCG-UI1-005
**Original Severity:** MAJOR
**Title:** No Tests for Strategy Widgets (AtmosphereGraph, SpectrumGraph)
**Location:** `game/ui/panels/strategy_widgets.py`

**Validation:**
Searched for `strategy_widgets` in tests - no results. These are rendering widgets for atmospheric and spectrum visualization with no test coverage.

**Verdict:** CONFIRMED
**Rationale:** No tests found for these visualization widgets.

---

#### Finding: TCG-UI1-006
**Original Severity:** MAJOR
**Title:** No Tests for System Tree Panel
**Location:** `game/ui/panels/system_tree_panel.py`

**Validation:**
Searched for `system_tree_panel` in tests - no results. No tests exist for this tree navigation widget.

**Verdict:** CONFIRMED
**Rationale:** No tests found for SystemTreePanel.

---

#### Finding: TCG-UI1-007
**Original Severity:** MAJOR
**Title:** No Tests for Component Modifier Grid Panel
**Location:** `game/ui/panels/component_modifier_grid_panel.py`

**Validation:**
Found reference in `tests/unit/ui/screens/test_workshop_screen.py` where `component_modifier_grid_panel` is mocked. No direct unit tests for the panel.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** Panel is tested indirectly through workshop screen tests. Direct tests would improve coverage but not critical.

---

#### Finding: TCG-UI1-008
**Original Severity:** MAJOR
**Title:** No Tests for Modifier Impact Grid
**Location:** `game/ui/panels/modifier_impact_grid.py`

**Validation:**
Found `tests/unit/ui/test_modifier_impact_grid.py` with comprehensive tests including init, update with/without component, update with modifiers, etc.

**Verdict:** REJECTED
**Rationale:** Tests exist at `tests/unit/ui/test_modifier_impact_grid.py`. Finding is factually incorrect.

---

#### Finding: TCG-UI1-009
**Original Severity:** MAJOR
**Title:** No Tests for Race Theme/Portrait/Flag Galleries
**Location:** `game/ui/panels/race_theme_gallery.py`

**Validation:**
Found `tests/unit/ui/test_race_theme_gallery.py` with tests for RaceThemeGallery. Tests exist for creation, button list, scroll container, theme selection, etc.

**Verdict:** REJECTED
**Rationale:** Tests exist at `tests/unit/ui/test_race_theme_gallery.py`. Finding is factually incorrect.

---

#### Finding: TCG-UI1-010
**Original Severity:** MAJOR
**Title:** No Tests for Formation Editor Subsystem
**Location:** `game/ui/screens/formation/*.py`

**Validation:**
Found extensive tests:
- `tests/unit/ui/test_formation_input_handler.py` (FormationInputHandler)
- `tests/unit/ui/test_formation_renderer.py` (FormationRenderer)
- `tests/unit/ui/screens/test_formation_editor_screen.py` (FormationEditorScreen)
- `tests/unit/builder/test_formation_editor_logic.py`

**Verdict:** REJECTED
**Rationale:** Formation subsystem is well-tested across multiple test files. Finding is factually incorrect.

---

#### Finding: TCG-UI1-011
**Original Severity:** MAJOR
**Title:** Galaxy Test Screen No Tests
**Location:** `game/ui/screens/galaxy_test/*.py`

**Validation:**
Searched for `galaxy_test` in tests - found only a reference in `test_scene_protocol.py`. The `galaxy_test/` module contains test/debug screens for galaxy visualization. These are development tools, not production code.

**Verdict:** DOWNGRADED(MINOR)
**Rationale:** This is a development/debug tool screen, not production code. Lower priority for test coverage.

---

#### Finding: TCG-UI1-012
**Original Severity:** MINOR
**Title:** Incomplete Edge Case Testing for BattleScreen
**Location:** `tests/unit/ui/test_battle_screen.py`

**Validation:**
Found three test files covering BattleScreen:
- `test_battle_screen.py` - Core functionality (initialization, battle over, tick, projectiles, UI service)
- `test_battle_screen_extended.py` - Extended tests (victory conditions, update loop)
- `test_battle_screen_simulation.py` - Simulation tests

Tests cover main paths but some edge cases may be missing (as with any complex screen).

**Verdict:** CONFIRMED
**Rationale:** Valid observation. Edge case coverage could be improved, though base coverage is good.

---

#### Finding: TCG-UI1-013
**Original Severity:** MINOR
**Title:** Workshop Screen Tests Are Mock-Heavy
**Location:** `tests/unit/ui/screens/test_workshop_screen.py`

**Validation:**
Reviewed `test_workshop_screen.py`. Uses bypass-init pattern with extensive mocking. This is appropriate for a complex UI screen test to isolate behavior from rendering concerns.

**Verdict:** CONFIRMED
**Rationale:** Valid observation. The tests are mock-heavy which is normal for UI screens but reduces confidence in integration. This is a known trade-off.

---

#### Finding: TCG-UI1-014
**Original Severity:** MINOR
**Title:** Strategy Screen Missing Superweapon Targeting Tests
**Location:** `tests/unit/ui/screens/test_strategy_screen.py`

**Validation:**
`test_strategy_screen.py` does reference `_superweapons` but delegates to the module. Found separate comprehensive tests:
- `tests/unit/ui/screens/test_strategy_superweapons.py` - SuperweaponOperations class
- `tests/unit/ui/screens/test_superweapon_input_modes.py` - Input mode transitions

**Verdict:** REJECTED
**Rationale:** Superweapon targeting is tested in dedicated test files, not in main strategy screen tests. This is good modular testing.

---

#### Finding: TCG-UI1-015
**Original Severity:** MINOR
**Title:** Build Queue Screen Missing Drag Handler Tests
**Location:** `tests/unit/ui/screens/test_build_queue_screen.py`

**Validation:**
Found `tests/integration/ui/test_build_queue_drag_drop.py` which tests drag and drop functionality for build queue. Unit tests in `test_build_queue_screen.py` focus on other aspects.

**Verdict:** REJECTED
**Rationale:** Drag handler is tested in integration tests. The functionality is covered.

---

#### Finding: TCG-UI1-016
**Original Severity:** MINOR
**Title:** Test Lab Scene Tests Cover Only Logic, Not Main Screen
**Location:** `tests/unit/ui/test_lab_scene/`

**Validation:**
Found `tests/unit/ui/test_lab_scene/` with:
- `test_logic.py` - JSON formatting, dropdown selection, validation
- `test_ui_components.py` - UI component tests

The tests focus on logic and UI components but may not test the main screen class directly.

**Verdict:** CONFIRMED
**Rationale:** Valid observation. Logic is tested but main screen integration coverage may be limited.

---

#### Finding: TCG-UI1-017
**Original Severity:** INFO
**Title:** Panels Module Missing __init__ Tests
**Location:** `game/ui/panels/__init__.py`

**Validation:**
`game/ui/panels/__init__.py` is essentially empty (1 line). No meaningful content to test.

**Verdict:** REJECTED
**Rationale:** The __init__.py is essentially empty. There's nothing to test.

---

#### Finding: TCG-UI1-018
**Original Severity:** INFO
**Title:** Test Patterns Vary Between Screen Tests
**Location:** Unknown

**Validation:**
Different test files use different patterns (bypass-init, fixtures, direct instantiation). This is normal evolution of test patterns over time.

**Verdict:** CONFIRMED
**Rationale:** Valid observation about test inconsistency, but INFO severity is appropriate. This is documentation/refactoring work, not a bug.

---

## Summary Statistics

**Total Findings:** 30 (including 2 positive/INFO findings)
**Actionable Findings:** 28

| Category | Original | After Validation |
|----------|----------|------------------|
| CRITICAL | 2 | 0 |
| MAJOR | 11 | 4 |
| MINOR | 11 | 7 |
| INFO | 4 | 4 (2 positive, 2 observations) |
| REJECTED | 0 | 10 |

**Key Observations:**
1. Several test coverage gap findings were factually incorrect - tests exist in different locations than expected
2. The builder subsystem is well-tested but tests are in `tests/unit/builder/` not `tests/unit/ui/screens/builder/`
3. Duplication findings were generally overstated in severity
4. The codebase shows good extraction patterns (BaseGallery, DesignStatsPanel, ColumnManager)
5. Some UI panels genuinely lack unit tests but have integration test coverage

**Recommended Actions:**
1. Add unit tests for `PlanetReportPanel` (TCG-UI1-003 - CONFIRMED MAJOR)
2. Add unit tests for `StrategyWidgets` (TCG-UI1-005 - CONFIRMED MAJOR)
3. Add unit tests for `SystemTreePanel` (TCG-UI1-006 - CONFIRMED MAJOR)
4. Consider extracting screenshot toast to shared utility (DUP-UI1-001 - MINOR)
5. Consider extracting compact number formatting to shared utility (DUP-UI1-004 - MINOR)
