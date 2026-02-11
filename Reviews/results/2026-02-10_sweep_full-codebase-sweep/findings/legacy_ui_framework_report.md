# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 34
- **Total Issues Found:** 8
- **Critical:** 2 | **Major:** 3 | **Minor:** 3 | **Info:** 0

## Findings

#### CRITICAL: Singleton Pattern Still in Use (SpriteManager & ShipThemeManager)
**ID:** LEG-UI2-001
**Location:** `game/ui/renderer/sprites.py:1-56` AND `game/ui/assets/ship_theme_manager.py:1-100`
**Issue:** Both classes use .instance() singleton pattern instead of dependency injection. This is an OLD pattern pre-dating the project's shift to DI. 18+ files actively using .instance() calls.
**Impact:** Test isolation issues, module-level state coupling, bypasses DI framework.
**Recommendation:** Migrate to DI - inject as dependencies rather than accessing singletons.
**Effort:** Complex

#### CRITICAL: Deprecated Flag-Based Action Attributes (BattleScreen/StrategyScreen)
**ID:** LEG-UI2-002
**Location:** `game/ui/screens/strategy_screen.py:634-636`
**Issue:** Flag-based transition self.action_open_design exists as fallback when scene_callback is not set. Old code from pre-callback era.
**Impact:** Code path rarely tested, creates confusion about which transition system is authoritative.
**Recommendation:** Delete the fallback. Ensure scene_callback is always provided.
**Effort:** Simple

#### MAJOR: Legacy Backward Compat Conversion Methods (ComponentRef)
**ID:** LEG-UI2-003
**Location:** `game/ui/screens/builder/component_ref.py:73-97`
**Issue:** .from_tuple() and .to_tuple() methods exist for migration from old tuple-based pattern. These methods are NEVER CALLED in the codebase.
**Impact:** Dead code bloat, migration incomplete.
**Recommendation:** Delete from_tuple() and to_tuple() methods.
**Effort:** Simple

#### MAJOR: Deprecated base_path Parameter (ShipThemeManager.initialize)
**ID:** LEG-UI2-004
**Location:** `game/ui/assets/ship_theme_manager.py:100-101`
**Issue:** base_path parameter is marked "deprecated/ignored in favor of Paths.ASSET_DIR" but parameter still accepted (unused).
**Impact:** API confusion, dead parameter.
**Recommendation:** Remove parameter from signature, update all callers.
**Effort:** Simple

#### MAJOR: Deprecated Property Access (StrategyScreen.turn_engine)
**ID:** LEG-UI2-005
**Location:** `game/ui/screens/strategy_screen.py:123-148`
**Issue:** @property turn_engine is deprecated per docstring and issues DeprecationWarning. Code still actively supports it.
**Impact:** Adds warning noise, supports old API.
**Recommendation:** Audit callers to migrate to facade methods, then delete property.
**Effort:** Simple

#### MINOR: Backwards Compat Wrapper Methods
**ID:** LEG-UI2-006
**Location:** `game/ui/screens/build_queue_screen.py:111-113, 274` AND `game/ui/panels/design_report_panel.py:165`
**Issue:** Multiple files contain "backward compat" comments with wrapper methods and aliases.
**Impact:** Unclear which API is canonical, test burden.
**Recommendation:** Audit all callers, migrate to new API, delete wrappers.
**Effort:** Medium

#### MINOR: Fallback Image Creation Pattern
**ID:** LEG-UI2-007
**Location:** `game/ui/assets/ship_theme_manager.py:246-250+`
**Issue:** _create_fallback_image() is defensive pattern for missing theme assets. Still actively used but indicates incomplete theme system.
**Impact:** Fallback hides missing data, makes real issues harder to debug.
**Recommendation:** Audit theme data completeness. Consider failing fast instead of silently falling back.
**Effort:** Medium

#### MINOR: Legacy Modifier Editing Pattern
**ID:** LEG-UI2-008
**Location:** `game/ui/screens/builder/legacy_components.py:1-197`
**Issue:** File explicitly named legacy_components.py contains ModifierEditorPanel. Marked for migration to ModifierLogic per docstring.
**Impact:** Confuses code maintenance, unclear if system should be modernized or replaced.
**Recommendation:** Rename to modifier_editor.py if keeping, or plan complete replacement.
**Effort:** Medium

## Top 5 Priority Issues
1. **LEG-UI2-001** (CRITICAL): Singleton pattern in SpriteManager/ShipThemeManager - 18+ call sites
2. **LEG-UI2-002** (CRITICAL): Deprecated flag-based transitions - parallel mechanism confusion
3. **LEG-UI2-003** (MAJOR): Dead ComponentRef tuple conversion methods - never called
4. **LEG-UI2-004** (MAJOR): Deprecated base_path parameter - dead parameter still in API
5. **LEG-UI2-005** (MAJOR): Deprecated turn_engine property - issues DeprecationWarning
