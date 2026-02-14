# Legacy System Holdovers Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 131 (106 in screens/, 25 in panels/)
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 3 | **Minor:** 7 | **Info:** 2

## Findings

#### MAJOR: Legacy Single-Selection Fields Maintained Alongside Multi-Select
**ID:** LEG-UI1-001
**Location:** `game/ui/screens/empire_build_queue_window.py:128-129, 328-335`
**Issue:** The code maintains `selected_source` and `selected_index` fields for "legacy single-selection" compatibility alongside the newer `selected_indices` set for multi-selection. The comment explicitly states "Update legacy single-selection fields" on line 328.
**Impact:** These legacy fields are only used internally (line 461 checks `clicked_index == self.selected_index`) and add confusion about which selection mechanism is authoritative. Creates maintenance burden and potential bugs if the two selection systems fall out of sync.
**Recommendation:** Migrate all selection logic to use `selected_indices` exclusively. Remove `selected_source` and `selected_index` fields. Update line 461 to use `selected_indices`.
**Effort:** Simple

#### MAJOR: Unused Imports Across Multiple Files
**ID:** LEG-UI1-002
**Location:** Multiple files in `game/ui/screens/` and `game/ui/panels/`
**Issue:** AST analysis detected numerous unused imports. Notable examples:
- `battle_screen.py`: `BattleConfig`, `Ship`, `random`, `math`, `BattleController`, `List` (some are TYPE_CHECKING only but still cluttering the namespace)
- `build_queue_screen.py`: `Galaxy`, `Fleet`, `BuildContext`, `InputMapper`, `HexCoord`, `Empire`, `DesignLoaderAdapter`, `DesignLibrary`, `Planet`, `UIConfig`
- `build_queue_controller.py`: `BuildContext`, `DesignLoaderAdapter`, `HexCoord`, `Planet`, `Fleet`, `Empire`, `DesignReportPanel`, `DesignLibrary`, `Galaxy`, `BuildQueueSource`
- `builder_widgets.py`: `GameRegistries`, `log_debug`, `log_info` (log_debug/log_info are imported but not called)
**Impact:** Code clutter, slower static analysis, confusion about actual dependencies. Some imports may be remnants of removed functionality.
**Recommendation:** Run a linter (ruff, flake8) with unused import checks and remove all genuinely unused imports. Verify TYPE_CHECKING imports are actually used in type annotations.
**Effort:** Simple

#### MAJOR: Fallback Pattern to Direct scene.ships Access
**ID:** LEG-UI1-003
**Location:** `game/ui/panels/battle_panels.py:30-44`
**Issue:** The `_get_ships()` method implements a fallback pattern: first tries `ui_service.get_ships()`, then falls back to `getattr(self.scene, 'ships', [])`. The comment on line 49-50 explicitly mentions "fallback to scene.ships for direct access." This dual-access pattern suggests an incomplete migration to the ui_service architecture.
**Impact:** Masks potential bugs where ui_service is not properly set up. Creates confusion about which data access pattern is authoritative (DTO via service vs direct domain access).
**Recommendation:** Complete the migration to ui_service exclusively. All callers should properly set up ui_service. Remove the fallback path once all tests pass without it.
**Effort:** Medium

#### MINOR: Empty __init__ Method
**ID:** LEG-UI1-004
**Location:** `game/ui/screens/race_asset_loader.py:27-29`
**Issue:** The `RaceAssetLoader.__init__` method contains only `pass`. This is a code smell suggesting either incomplete implementation or unnecessary initialization.
**Impact:** Minor clutter. The class is stateless and all methods are instance methods that could potentially be static methods.
**Recommendation:** Either convert to a module with standalone functions (if no state needed) or remove the empty `__init__` and let Python's default handle it.
**Effort:** Simple

#### MINOR: Disabled Feature Left as pass Statement
**ID:** LEG-UI1-005
**Location:** `game/ui/screens/builder/schematic_view.py:113-115`
**Issue:** Comment "Draw Components - DISABLED" followed by "User requested to stop showing component icons" with just `pass`. This is dead code that should be removed rather than left as documentation.
**Impact:** Minor clutter. The comment provides useful context but the code block is unnecessary.
**Recommendation:** Remove the entire block (lines 113-115). If historical context is important, use git history instead.
**Effort:** Simple

#### MINOR: get_component_at Returns None Unconditionally
**ID:** LEG-UI1-006
**Location:** `game/ui/screens/builder/schematic_view.py:54-60`
**Issue:** The `get_component_at` method always returns `None` with a comment explaining the feature is "DISABLED". This is a stub method that provides no functionality.
**Impact:** Callers may still call this method expecting it to work. The method signature suggests functionality that doesn't exist.
**Recommendation:** Either remove the method entirely and update callers, or add a deprecation warning. If the feature might return, consider raising `NotImplementedError` with a clear message.
**Effort:** Simple

#### MINOR: Legacy Pattern Comment Without Active Code
**ID:** LEG-UI1-007
**Location:** `game/ui/screens/builder/stats_config.py:70-71`
**Issue:** Comment "Note: Legacy pattern using negative CrewCapacity was removed in PROJ-42" is documentation of removed code. While informative, this is project archaeology that belongs in commit messages/PR descriptions, not active code.
**Impact:** Minor noise in codebase.
**Recommendation:** Remove the comment. Historical context is available in git history and PROJ-42 documentation.
**Effort:** Simple

#### MINOR: Excessive hasattr Checks Suggesting Duck-Typing Overuse
**ID:** LEG-UI1-008
**Location:** Multiple files (120+ occurrences across screens/ and panels/)
**Issue:** Heavy use of `hasattr()` checks suggests objects with inconsistent interfaces are being passed around. Examples include:
- `strategy_screen.py`: Multiple `hasattr(self, 'build_queue_screen')` checks
- `fleet_report_window.py`: Numerous `hasattr(self, ...)` for UI elements
- `planet_list_filters.py`: `hasattr(p, 'surface_temperature')` checks

While some are defensive programming for mocks/DTOs (noted in battle_panels.py comments), many suggest incomplete interfaces or optional attributes that should be formalized.
**Impact:** Code brittleness, difficulty reasoning about object capabilities, potential runtime errors masked by silent fallbacks.
**Recommendation:** Formalize interfaces using Protocols or abstract base classes. For optional features, use explicit Optional types or feature flags rather than hasattr checks.
**Effort:** Complex

#### MINOR: Formation File Format Comment Suggests Recent Migration
**ID:** LEG-UI1-009
**Location:** `game/ui/screens/formation_editor.py:214-217`
**Issue:** Comment "PROJ-42 Phase 4: Removed legacy list format support" with validation that raises `ValueError` for non-dict format. This is migration validation code that could be simplified once all old format files are gone.
**Impact:** Minor. The validation is useful if old format files might still exist.
**Recommendation:** After confirming no old format files exist, the isinstance check and error message can be simplified to just process dict format directly.
**Effort:** Simple

#### MINOR: Fallback Mode in Build Queue Controller
**ID:** LEG-UI1-010
**Location:** `game/ui/panels/build_queue_controller.py:519-559`
**Issue:** The `_add_to_fallback` method is documented as "fallback mode" for "when no queue source is explicitly set." This suggests an incomplete migration to the multi-queue source system.
**Impact:** Adds complexity to the build queue logic with two code paths.
**Recommendation:** Investigate if the fallback path is actually used. If not, remove it. If it is, consider whether the architecture should be simplified to always use explicit queue sources.
**Effort:** Medium

#### INFO: Module-Level Singleton Pattern
**ID:** LEG-UI1-011
**Location:** `game/ui/screens/builder_utils.py:54-59`
**Issue:** Comment "Singleton instances for easy import" followed by module-level constant instances (`PANEL_WIDTHS`, `PANEL_HEIGHTS`, etc.). While technically a singleton pattern, this is implemented as module-level constants which is the Pythonic approach for immutable configuration.
**Impact:** None. This is acceptable usage despite the "singleton" terminology.
**Recommendation:** No action needed. Consider renaming the comment to "Module-level constants for easy import" for clarity.
**Effort:** None

#### INFO: Backward Compatibility Comment in Documentation
**ID:** LEG-UI1-012
**Location:** `game/ui/screens/fleet_report_filters.py:5`
**Issue:** Comment "PROJ-40: Removed backward-compat wrapper - use ShipStatsCalculator directly" is historical documentation. The wrapper has been removed; this is just noting the change.
**Impact:** None. Documentation of completed migration.
**Recommendation:** No action needed. This type of historical context in docstrings is useful.
**Effort:** None

## Top 5 Priority Issues

1. **LEG-UI1-001 (MAJOR):** Legacy single-selection fields in `empire_build_queue_window.py` - Creates dual selection systems that can fall out of sync. Simple fix with clear benefit.

2. **LEG-UI1-003 (MAJOR):** Fallback pattern in `battle_panels.py` to direct `scene.ships` access - Suggests incomplete DTO migration. Medium effort but important for architectural consistency.

3. **LEG-UI1-002 (MAJOR):** Unused imports across multiple files - Easy to fix with automated tooling. Reduces noise and clarifies actual dependencies.

4. **LEG-UI1-010 (MINOR):** Fallback mode in build queue controller - May be dead code. Worth investigating if the path is actually exercised.

5. **LEG-UI1-008 (MINOR):** Excessive hasattr checks - Complex to address but improves type safety. Consider addressing incrementally during other refactoring work.
