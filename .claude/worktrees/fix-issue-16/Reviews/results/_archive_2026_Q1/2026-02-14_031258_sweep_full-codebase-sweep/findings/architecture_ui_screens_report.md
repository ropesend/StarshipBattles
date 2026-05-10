# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 109 (65 in game/ui/screens/, 19 in game/ui/screens/builder/, 14 in game/ui/screens/test_lab/, 3 in game/ui/screens/formation/, 5 in game/ui/screens/galaxy_test/, 25 in game/ui/panels/)
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 4 | **Minor:** 2 | **Info:** 1

## Findings

#### MAJOR: God Class - TestLabScreen (1906 lines)
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:1-1906`
**Issue:** File exceeds 500 lines significantly (1906 lines). God class indicator violating single-responsibility principle.
**Impact:** Difficult to maintain, test, and reason about. High coupling between unrelated concerns.
**Recommendation:** Continue extraction pattern used elsewhere - extract test execution, panel management, and data handling into separate modules similar to how TestLabExecutor, TestLabPanelManager, and TestLabDataExtractor have been extracted. The remaining 1906 lines suggest more extraction is needed.
**Effort:** Complex

#### MAJOR: God Class - fleet_report_window.py (1093 lines)
**ID:** ADR-UI1-002
**Location:** `game/ui/screens/fleet_report_window.py:1-1093`
**Issue:** File exceeds 500 lines significantly (1093 lines). Contains UI building, event handling, data formatting, and rendering logic.
**Impact:** Reduced testability, difficult navigation, high cognitive load for maintenance.
**Recommendation:** Extract FleetReportRenderer, FleetReportEventHandler, and leverage existing fleet_report_view_model.py and fleet_report_filters.py more extensively.
**Effort:** Medium

#### MAJOR: God Class - build_queue_screen.py (1084 lines)
**ID:** ADR-UI1-003
**Location:** `game/ui/screens/build_queue_screen.py:1-1084`
**Issue:** File exceeds 500 lines significantly (1084 lines). Handles UI creation, event routing, queue operations, and rendering.
**Impact:** Complex file difficult to maintain. Changes in one area risk regressions in unrelated functionality.
**Recommendation:** Extract BuildQueueRenderer and BuildQueueEventHandler. Note: BuildQueueController (597 lines) already exists in panels - consider whether build_queue_screen.py can delegate more to it.
**Effort:** Medium

#### MAJOR: God Class - weapons_panel.py (1037 lines)
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/builder/weapons_panel.py:1-1037`
**Issue:** File exceeds 500 lines significantly (1037 lines). Complex weapons display logic embedded in UI component.
**Impact:** Tight coupling between weapons data formatting and UI rendering. Hard to unit test weapons logic.
**Recommendation:** Extract WeaponsReportDataProvider for data computation separate from WeaponsReportPanel UI rendering.
**Effort:** Medium

#### MINOR: Near-God Classes (500-1000 lines)
**ID:** ADR-UI1-005
**Location:** Multiple files
**Issue:** Several files approach god class threshold:
- `race_setup_screen.py` (946 lines)
- `formation_editor.py` (941 lines)
- `test_run_details.py` (893 lines)
- `strategy_input_handler.py` (868 lines)
- `empire_build_queue_window.py` (863 lines)
- `strategy_screen.py` (819 lines)
- `strategy_renderer.py` (764 lines)
**Impact:** Risk of becoming maintenance burdens as features are added.
**Recommendation:** Monitor these files and extract components proactively before they exceed 1000 lines.
**Effort:** Simple (planning) to Medium (execution)

#### MINOR: Inconsistent Cross-Layer Import Documentation
**ID:** ADR-UI1-006
**Location:** Various files in game/ui/screens/
**Issue:** Some files document cross-layer imports clearly (e.g., `design_selector_window.py`, `strategy_fleet_ops.py`) while others do not. This inconsistency makes it harder to audit architectural compliance.
**Impact:** Reduced code clarity; harder for new developers to understand layer boundaries.
**Recommendation:** Standardize cross-layer import documentation in docstrings following the established pattern: `"Cross-layer imports (acceptable for UI): - Module: TYPE_CHECKING/Runtime - reason"`
**Effort:** Simple

#### INFO: Proper Architecture Patterns Observed
**ID:** ADR-UI1-007
**Location:** Throughout game/ui/screens/ and game/ui/panels/
**Issue:** Not an issue - observation of good practices.
**Impact:** Positive - maintains layer separation.
**Details:**
- **No pygame in non-UI layers:** Searched game/simulation/, game/strategy/, game/core/, game/ai/ - zero pygame imports found. The historical pygame.math.Vector2 issue has been resolved.
- **TYPE_CHECKING used correctly:** 50+ files use TYPE_CHECKING blocks appropriately to avoid circular imports while maintaining type hints.
- **Proper layer dependencies:** UI files import from core, simulation, strategy, and ai layers as expected. No reverse dependencies found.
- **Service/adapter pattern:** Files like `ShipFactory`, `DesignLoaderAdapter`, `VehicleClassService` properly abstract cross-layer calls.
- **Facade pattern:** `StrategySessionFacade` properly insulates UI from strategy engine internals.

## Top 5 Priority Issues

1. **ADR-UI1-001 (MAJOR):** TestLabScreen at 1906 lines is the most urgent god class to refactor. It is nearly 4x the 500-line threshold.

2. **ADR-UI1-002 (MAJOR):** fleet_report_window.py at 1093 lines combines too many concerns and would benefit from extraction patterns already established elsewhere.

3. **ADR-UI1-003 (MAJOR):** build_queue_screen.py at 1084 lines should delegate more to existing BuildQueueController and extract rendering logic.

4. **ADR-UI1-004 (MAJOR):** weapons_panel.py at 1037 lines embeds complex data processing in UI rendering code.

5. **ADR-UI1-005 (MINOR):** Monitor the 7 files approaching 1000 lines to prevent them from becoming maintenance burdens.

---

## Methodology Notes

### Phase 1: Import Graph Analysis
- Scanned all 109 Python files in scope
- Verified imports follow layer rules (Core <- Simulation <- Strategy <- UI, AI)
- No layer violations found in import statements

### Phase 2: Pygame Boundary Violations
- Searched game/core/, game/simulation/, game/strategy/, game/ai/ for pygame imports
- **Result:** Zero violations found - pygame is properly contained to UI layer

### Phase 3: Circular Dependencies
- Searched for "import here to avoid circular" comments - none found
- TYPE_CHECKING blocks are used appropriately for type hints without creating runtime dependencies
- No A->B->A import cycles detected in scanned files

### Phase 4: God Classes
- Identified 4 files exceeding 1000 lines
- Identified 7 files in 500-1000 line range that should be monitored
- Used wc -l analysis on all Python files in scope

### Phase 5: Data Flow Violations
- No evidence of UI-layer data (pixel coordinates, colors, font sizes) flowing into simulation/strategy logic
- Configuration properly separated between game logic and UI layout
- Simulation results do not contain UI formatting

### Phase 6: Dependency Direction Violations
- No callbacks from lower layers to higher layers detected
- Event handlers properly contained within UI layer
- Lower-layer services do not extend with UI-specific methods
