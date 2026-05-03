# Legacy System Holdovers Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 130 (105 screens + 25 panels)
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 3 | **Minor:** 7 | **Info:** 2

## Findings

#### MAJOR: Legacy Single-Selection Fields in EmpireBuildQueueWindow
**ID:** LEG-UI1-001
**Location:** `game/ui/screens/empire_build_queue_window.py:128-135, 328-335`
**Issue:** The window maintains both multi-select (`selected_indices: Set[int]`) and legacy single-select (`selected_source`, `selected_index`) fields simultaneously. Comment on line 328 explicitly states "Update legacy single-selection fields". This dual tracking creates maintenance burden and potential for state inconsistency.
**Impact:** Confusing API surface with two ways to track selection state. Risk of bugs if either field gets out of sync.
**Recommendation:** Remove `selected_source` and `selected_index` fields, update all callers to use `get_selected_sources()` and `selected_indices`.
**Effort:** Medium - requires auditing all usages of the legacy fields

#### MAJOR: Backward Compatibility Property in TestLabScreen
**ID:** LEG-UI1-002
**Location:** `game/ui/screens/test_lab/screen.py:249-252`
**Issue:** Property `_components_cache` is documented as "for backward compatibility" and simply delegates to the data extractor's internal cache. This suggests incomplete migration where the cache access should have been fully moved to the data extractor.
**Impact:** Exposes internal implementation detail of data extractor through screen class.
**Recommendation:** Audit all callers of `_components_cache` and update them to access the data extractor directly, then remove the property.
**Effort:** Simple - grep for callers and update

#### MAJOR: Legacy API Method in FleetReportWindow
**ID:** LEG-UI1-003
**Location:** `game/ui/screens/fleet_report_window.py:956-969`
**Issue:** Method `_on_remove_ship` is documented as "Handle remove single ship from fleet (legacy API)". The newer `_on_remove_selected_ships` method (line 971) provides the modern multi-select version. The legacy method remains for single-ship removal operations.
**Impact:** Two separate code paths for ship removal creates inconsistency risk and maintenance burden.
**Recommendation:** Unify ship removal through the multi-select path with single-item support, remove legacy method.
**Effort:** Medium - requires careful testing of ship removal flows

#### MINOR: Comments Referencing "Legacy Dispatch" in StrategyInputHandler
**ID:** LEG-UI1-004
**Location:** `game/ui/screens/strategy_input_handler.py:70, 75`
**Issue:** Comments mention "PROJ-88: folded from app.py legacy dispatch" suggesting this code was migrated from an older location. While the code is functional, the comments should be cleaned up to remove migration history.
**Impact:** Comments create confusion about whether migration is complete.
**Recommendation:** Remove "legacy dispatch" comments, keep only functional documentation.
**Effort:** Simple - comment cleanup only

#### MINOR: Pass Statements in Stub Methods
**ID:** LEG-UI1-005
**Location:** `game/ui/screens/test_lab/ship_panels.py:45-47, 134-136`, `game/ui/screens/empire_build_queue_window.py:493-495`
**Issue:** Several `update()` methods contain only `pass` statements with comments like "Update hover states" but no implementation. In `empire_build_queue_window.py:495`, comment says "Future: update visible rows for virtual scrolling" indicating planned but incomplete functionality.
**Impact:** Empty methods suggest incomplete implementations or dead code paths.
**Recommendation:** Either implement the intended functionality or remove the stub methods if not needed.
**Effort:** Simple - remove or implement

#### MINOR: Extensive hasattr() Checks for Optional Attributes
**ID:** LEG-UI1-006
**Location:** Multiple files including `strategy_input_handler.py`, `workshop_event_router.py`, `fleet_report_window.py`, `strategy_ui.py` (100+ occurrences)
**Issue:** Widespread use of `hasattr()` checks to test for attributes that should always exist in modern code. Examples include checking for `build_queue_screen`, `test_scenario`, `current_empire`. While some are legitimate interface checks, many suggest defensive coding from when attributes were optional during migration.
**Impact:** Code verbosity and potential masking of bugs when attributes are unexpectedly missing.
**Recommendation:** Audit high-frequency hasattr patterns. If attributes should always exist in modern code, remove the checks. Convert necessary checks to protocol/interface definitions.
**Effort:** Complex - requires careful analysis of each case

#### MINOR: Singleton Instance Access Pattern
**ID:** LEG-UI1-007
**Location:** 22 locations across screens, including:
- `workshop_screen.py:64,94,97` (ScreenshotManager, SpriteManager, ShipThemeManager)
- `builder/right_panel.py:114,206` (StrategyMetadataService)
- `fleet_report_window.py:735` (ShipThemeManager)
- `planet_list_renderer.py:151` (AssetManager)
**Issue:** Direct singleton access via `.instance()` pattern is used throughout the UI layer. Project conventions prefer dependency injection. While singletons are sometimes appropriate for managers, the pattern creates hidden dependencies.
**Impact:** Makes testing harder, creates implicit coupling.
**Recommendation:** Consider injecting these services where possible, especially in new code. Low priority for existing stable code.
**Effort:** Complex - architectural change

#### MINOR: Fallback Chains in Workshop Context
**ID:** LEG-UI1-008
**Location:** `game/ui/screens/workshop_context.py:66-74`
**Issue:** The `__post_init__` method attempts to get default registries and catches exceptions with a pass, leaving registries as None. This defensive pattern was added during PROJ-58 migration but may no longer be necessary if registries are always available.
**Impact:** Silent failure if registries aren't available could mask configuration issues.
**Recommendation:** Verify that registries are always available in production use cases. If so, remove the try/except and require explicit DI.
**Effort:** Simple - verify and simplify

#### MINOR: PROJ-40 Migration Comments Still Present
**ID:** LEG-UI1-009
**Location:** `game/ui/screens/fleet_report_filters.py:5`, `game/ui/screens/workshop_viewmodel.py:10,50,65,243,323,341`
**Issue:** Multiple files contain comments documenting PROJ-40 migration changes ("Removed backward-compat wrapper", "Removed fallback to global", "Require registries via context"). While these comments are informative, they document completed migrations and could be simplified.
**Impact:** Comment clutter that documents historical changes rather than current behavior.
**Recommendation:** Simplify to document current behavior only, remove migration history.
**Effort:** Simple - comment cleanup

#### MINOR: getattr() Defensive Patterns
**ID:** LEG-UI1-010
**Location:** `game/ui/screens/empire_panel_window.py:206,270,283,318-367,410-445` (40+ occurrences)
**Issue:** Extensive use of `getattr(obj, 'attr', default)` for accessing race_config attributes. While this provides safety, it may mask missing attributes that should be present in valid configurations.
**Impact:** Silent defaults could hide data issues.
**Recommendation:** If race_config is a well-defined dataclass/schema, direct attribute access should be safe. Review whether defaults are still needed.
**Effort:** Medium - requires understanding of data contracts

#### INFO: Dual-Path Ship/DTO Support in BattlePanels
**ID:** LEG-UI1-011
**Location:** `game/ui/panels/battle_panels.py:30-44, 59-74, 263-274`
**Issue:** Methods like `_get_ships()`, `_get_ship_id()`, and `_get_projectile_id()` support both DTO objects (with `.id` attribute) and domain objects (using `.name` or Python object id as fallback). This is documented as PROJ-43 design, supporting gradual migration to DTOs.
**Impact:** Intentional dual-support during DTO migration. No immediate action needed if migration is ongoing.
**Recommendation:** Monitor DTO migration progress. Once complete, remove fallback paths.
**Effort:** Deferred until DTO migration completes

#### INFO: Build Queue Fallback Mode
**ID:** LEG-UI1-012
**Location:** `game/ui/panels/build_queue_controller.py:283-289, 519-559`
**Issue:** `_add_to_fallback()` method provides a fallback when no queue source is explicitly set, adding items directly to `build_context.construction_queue`. This exists alongside the modern multi-queue and single-queue paths.
**Impact:** Legitimate backward-compatible path for simpler use cases.
**Recommendation:** Document when fallback mode is appropriate vs multi-queue mode.
**Effort:** None - documentation only

## Top 5 Priority Issues

1. **LEG-UI1-001** (Major): Legacy single-selection fields in EmpireBuildQueueWindow create dual state tracking that can cause sync issues.

2. **LEG-UI1-003** (Major): Legacy `_on_remove_ship` API in FleetReportWindow creates two code paths for ship removal operations.

3. **LEG-UI1-002** (Major): Backward compatibility property `_components_cache` in TestLabScreen exposes internal implementation.

4. **LEG-UI1-006** (Minor): Extensive hasattr() checks throughout UI code may mask bugs and add verbosity - warrants systematic audit.

5. **LEG-UI1-007** (Minor): Singleton access pattern conflicts with DI conventions - low priority but impacts testability.

## Observations

The UI screens and panels layer is generally clean with no critical legacy issues. Most findings are:
- Well-documented migration remnants (PROJ-40, PROJ-43, PROJ-88 references)
- Defensive coding patterns that were appropriate during migrations
- Intentional dual-support for gradual transitions (DTO migration)

The project's migration discipline appears effective - backward compatibility layers are clearly documented when they exist, and most have comments explaining their purpose. The main cleanup opportunities are removing completed migration documentation and consolidating dual-state tracking in a few windows.
