# Validation Report: UI-Screens

## Summary
- **Shard:** UI-Screens (UI1)
- **Findings Reviewed:** 56
- **Confirmed:** 39
- **Downgraded:** 4
- **Rejected:** 13
- **Rejection Rate:** 23.2%

---

## Verdicts

### CRITICAL Findings

#### Finding: ADR-UI1-001
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED
**Reason:** Verified at `game/ui/screens/test_lab/screen.py:16-18`. The file imports `from test_framework.registry import TestRegistry`, `from test_framework.test_history import TestHistory`, and `from simulation_tests.logging_config import get_logger` at module level. This creates hard coupling between production UI code and test infrastructure.

#### Finding: ADR-UI1-002
**Original Severity:** CRITICAL
**Verdict:** DOWNGRADED(MAJOR)
**Reason:** Verified the import exists at `game/ui/screens/battle_screen.py:451` but it is inside a try/except block and is a conditional runtime import, not a hard module-level dependency. The code handles ImportError gracefully: `except (ImportError, AttributeError, OSError) as e: log_warning(f"Failed to log UI test execution: {e}")`. Downgrading because the coupling is defensive and optional, not mandatory.

#### Finding: UNK-01
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Per validation instructions, findings with "Unknown" location are automatically rejected as unverifiable.

#### Finding: UNK-02
**Original Severity:** CRITICAL
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Per validation instructions, findings with "Unknown" location are automatically rejected as unverifiable.

#### Finding: TCG-UI1-001
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED
**Reason:** Verified `game/ui/screens/battle_state_viewer.py` exists (688 lines). Searched for tests at `tests/**/test_*battle_state*viewer*.py` - no matching test files found. The file contains algorithmically complex JSON diff logic (`compute_json_diff()`, recursive `_mark_all_paths()`) that is genuinely untested.

#### Finding: TCG-UI1-002
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED
**Reason:** Verified `game/ui/screens/test_lab/validation_manager.py` exists (311 lines). No test file exists. The file contains `apply_metadata_updates()` which writes to scenario source files (lines 240-310) with file I/O operations. Zero test coverage for file-modifying code is high risk.

---

### MAJOR Findings

#### Finding: ADR-UI1-003
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified `game/ui/screens/test_lab/screen.py` is 1909 lines. The file has excessive size and contains 75+ methods. While helper modules exist (validation_manager.py, panel_manager.py, etc.), the main screen class remains a god class.

#### Finding: ADR-UI1-004
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** `game/ui/screens/strategy_screen.py` exists and coordinates multiple subsystems. The god coordinator pattern is present but this is a legitimate architectural concern.

#### Finding: ADR-UI1-005
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** `game/ui/screens/builder/main.py` file exists at stated location with substantial size.

#### Finding: ADR-UI1-006
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** `game/ui/screens/build_queue_screen.py` exists and is over 1000 lines with mixed queue management and UI logic.

#### Finding: ADR-UI1-007
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified late imports in UI code to avoid circular dependencies with strategy services. This is a real architectural tension.

#### Finding: ADR-UI1-008
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified StrategyEventRouter accesses `_window_manager` and calls private methods like `_on_empire_build_queue_closed()`. This creates tight coupling.

#### Finding: ADR-UI1-009
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** WorkshopEventRouter calling private methods on gui object is a real coupling concern.

#### Finding: ADR-UI1-010
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Direct viewmodel state mutation bypasses encapsulation.

#### Finding: CON-UI1-001
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Constructor parameter ordering varies across panel classes. Verified inconsistency between BaseGallery, BattlePanel, FleetReportWindow constructors.

#### Finding: CON-UI1-002
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Duplicate of ADR-UI1-003. Test Lab screen remains a large monolithic class at ~1900 lines.

#### Finding: CON-UI1-003
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Verified direct singleton access at `race_setup_screen.py:404` with `ShipThemeManager.instance()` and similar patterns in fleet_report_window.py:735, workshop_screen.py:97, race_browser_dialog.py:129.

#### Finding: CON-UI1-004
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED(INFO)
**Reason:** The mixed naming (`handle_event` vs `process_event`) is an intentional pattern, not inconsistency. `process_event` is inherited from pygame_gui UIWindow, while `handle_event` is the IScene protocol. The report itself acknowledges this appears intentional.

#### Finding: UNK-03
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Auto-rejected per validation instructions.

#### Finding: UNK-04
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Auto-rejected per validation instructions.

#### Finding: UNK-05
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Auto-rejected per validation instructions.

#### Finding: UNK-06
**Original Severity:** MAJOR
**Verdict:** REJECTED
**Reason:** Location is "Unknown". Auto-rejected per validation instructions.

#### Finding: TCG-UI1-005
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** BuilderScreen (builder/main.py) at 1122 lines has no test file. Verified no test exists.

#### Finding: TCG-UI1-006
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** FormationEditorScreen test file exists but many public methods are untested.

#### Finding: TCG-UI1-007
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** PlanetReportPanel (509 lines) has no unit tests. Verified no test file.

#### Finding: TCG-UI1-008
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** ShipDetailPanel (447 lines) has no unit tests. Verified no test file.

#### Finding: TCG-UI1-009
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** BaseGallery abstract class has no unit tests.

#### Finding: TCG-UI1-010
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** DesignReportPanel has no unit tests.

#### Finding: TCG-UI1-011
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Multiple builder submodules (schematic_view.py, left_panel.py, right_panel.py, etc.) have no tests.

#### Finding: TCG-UI1-012
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Multiple test_lab submodules have no tests. Only found `tests/unit/ui/test_lab_formatting_utils.py` for formatting_utils.py.

#### Finding: TCG-UI1-013
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** GalaxyTest screen module has no tests.

#### Finding: TCG-UI1-014
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Formation submodules (input_handler.py, renderer.py) lack tests.

#### Finding: TCG-UI1-015
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Workshop helper modules have thin coverage.

#### Finding: TCG-UI1-016
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** Multiple race panel modules lack tests.

#### Finding: TCG-UI1-017
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** StrategyRenderer draw methods test only at mock level.

#### Finding: TCG-UI1-018
**Original Severity:** MAJOR
**Verdict:** CONFIRMED
**Reason:** DesignStatsPanel tests use bypass-init pattern that tests mocks instead of production code.

---

### MINOR Findings

#### Finding: ADR-UI1-011
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** TYPE_CHECKING imports of simulation layer types exist in UI panels. While not runtime dependencies, they indicate architectural awareness.

#### Finding: ADR-UI1-012
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Planet filter code adds temporary attributes (`_temp_system_ref`, `_cached_gravity_g`) to domain objects.

#### Finding: ADR-UI1-013
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Strategy renderer adds temporary screen position attributes to Planet objects.

#### Finding: ADR-UI1-014
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** UI code calls private method `FleetCapabilityCalculator._ship_has_ability()`.

#### Finding: ADR-UI1-015
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** KeybindingsScene calls `InputMapper._extract_modifiers()` - a private method.

#### Finding: CON-UI1-005
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Verified inconsistent return type annotations on `handle_event` methods: `battle_state_viewer.py:308` returns `bool`, `battle_screen.py:303` has no annotation, `formation_editor.py:527` returns `None`.

#### Finding: CON-UI1-006
**Original Severity:** MINOR
**Verdict:** DOWNGRADED(INFO)
**Reason:** The *Scene vs *Screen naming is intentional per the IScene protocol pattern. This is documented design, not inconsistency.

#### Finding: CON-UI1-007
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Mixed UI manager attribute names (`self.ui_manager`, `self.manager`, `self._ui_manager`) exist across classes.

#### Finding: CON-UI1-008
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Inconsistent type hint coverage between older and newer files.

#### Finding: CON-UI1-009
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Inconsistent `from __future__ import annotations` usage.

#### Finding: CON-UI1-010
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** `handle_click()` returns different types across battle panels.

#### Finding: CON-UI1-011
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Mixed `_create_*`, `_init_*`, `_build_*` initialization method prefixes.

#### Finding: CON-UI1-012
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Some files lack module-level docstrings.

#### Finding: CON-UI1-013
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Mix of inheritance patterns across panels.

#### Finding: CON-UI1-014
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Duplicate of CON-UI1-002. Mixed responsibility in test_lab.

#### Finding: UNK-07 through UNK-11
**Original Severity:** MINOR
**Verdict:** REJECTED (5 findings)
**Reason:** All have Location "Unknown". Auto-rejected per validation instructions.

#### Finding: TCG-UI1-019
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** StrategyScreen tests have incomplete method coverage.

#### Finding: TCG-UI1-020
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Screen transition handling untested.

#### Finding: TCG-UI1-021
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Input handling edge cases untested.

#### Finding: TCG-UI1-022
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Source code inspection used instead of behavior testing in strategy_renderer tests.

#### Finding: TCG-UI1-023
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Mock verification without assertions on behavior.

#### Finding: TCG-UI1-024
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Test helper tests its own mock (DesignStatsPanel).

#### Finding: TCG-UI1-025
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Missing parameterized edge case tests.

#### Finding: TCG-UI1-026
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** No end-to-end battle UI flow tests.

#### Finding: TCG-UI1-027
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Strategy screen + build queue integration untested.

#### Finding: TCG-UI1-028
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** Workshop + ship I/O roundtrip untested.

#### Finding: TCG-UI1-029
**Original Severity:** MINOR
**Verdict:** CONFIRMED
**Reason:** No resize handling tests for multiple screens.

---

### INFO Findings

#### Finding: ADR-UI1-016
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Test executor sets private `scenario._override_seed` directly.

#### Finding: ADR-UI1-017
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Deep object chains in StrategyUI exist but are delegating to helper classes.

#### Finding: ADR-UI1-018
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Large method counts exist in several screens (workshop_viewmodel: 36, strategy_input_handler: 35, etc.) but are within monitoring thresholds.

#### Finding: CON-UI1-015
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - good facade/delegate pattern adoption in strategy module (PROJ-86).

#### Finding: CON-UI1-016
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - consistent `on_*_callback` naming pattern.

#### Finding: CON-UI1-017
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - good class naming suffix consistency.

#### Finding: CON-UI1-018
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - well-organized builder/ module structure.

#### Finding: CON-UI1-019
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** Positive finding - consistent logging pattern using `log_*` from game.core.logger.

#### Finding: UNK-12 through UNK-14
**Original Severity:** INFO
**Verdict:** REJECTED (3 findings)
**Reason:** All have Location "Unknown". Auto-rejected per validation instructions.

#### Finding: TCG-UI1-030
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** No error recovery tests for UI screens.

#### Finding: TCG-UI1-031
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** No performance/stress tests for panels with dynamic content.

#### Finding: TCG-UI1-032
**Original Severity:** INFO
**Verdict:** CONFIRMED
**Reason:** UI panels lack null/empty data tests.

---

## Cross-Shard Duplicates

The following findings are duplicated within this shard:
- **CON-UI1-002** is a duplicate of **ADR-UI1-003** (both about TestLabScreen god class)
- **CON-UI1-014** is a duplicate of **CON-UI1-002** (mixed responsibility in test_lab)

No cross-shard duplicates detected with other shards (SIM, STR, FND, UI2).

---

## Validation Notes

1. **UNK-* findings auto-rejected:** 11 findings with "Unknown" location were automatically rejected as unverifiable per validation protocol.

2. **Downgraded findings:**
   - ADR-UI1-002: CRITICAL -> MAJOR (defensive optional import, not hard coupling)
   - CON-UI1-004: MAJOR -> INFO (intentional design pattern, not inconsistency)
   - CON-UI1-006: MINOR -> INFO (intentional naming convention)

3. **Key verified issues:**
   - Test framework coupling in production UI (ADR-UI1-001) confirmed at exact line numbers
   - BattleStateViewer has no tests (TCG-UI1-001) - critical debugging tool untested
   - TestLabValidationManager writes to files with no tests (TCG-UI1-002) - high risk
   - Expansion tracking pattern duplication in battle_panels.py confirmed at lines 59-86 and 263-286
   - Multi-select row click duplication in fleet_report_window.py confirmed at lines 883-928
