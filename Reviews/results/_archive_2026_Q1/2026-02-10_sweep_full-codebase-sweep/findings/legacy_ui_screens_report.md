# Legacy System Holdovers Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 99
- **Total Issues Found:** 11
- **Critical:** 2 | **Major:** 5 | **Minor:** 4 | **Info:** 0

## Findings

#### CRITICAL: Deprecated Action Flags for Scene Transitions
**ID:** LEG-UI1-001
**Location:** `game/ui/screens/battle_screen.py:109-111, 160-161, 272-273, 502, 509`
**Issue:** BattleScreen maintains deprecated action_return_to_setup and action_return_to_test_lab flags as fallbacks for scene transitions. Lines 109-111 explicitly mark these as deprecated, recommending scene_callback instead. The fallback implementation is still present when scene_callback is None.
**Impact:** Creates confusion about which mechanism is authoritative for scene transitions. The fallback path is still active and tested by test_lab/screen.py:457.
**Recommendation:** Remove the fallback implementation entirely. Ensure all callers provide scene_callback. Update TestLabScreen to use callbacks exclusively.
**Effort:** Medium

#### CRITICAL: Backward Compatibility Shims for BuildQueueScreen
**ID:** LEG-UI1-002
**Location:** `game/ui/screens/build_queue_screen.py:111-120, 274-277, 283-284`
**Issue:** BuildQueueScreen maintains backward compatibility for legacy single build_context mode. When hex_coord is None, it wraps context as BuildQueueSource with synthetic _legacy ID. Also exposes queue_selector_panel, queue_selector_scrollable, queue_selector_buttons as aliases for backward compat with tests.
**Impact:** Keeps both old and new queue selection paths alive. Synthetic legacy ID indicates incomplete migration.
**Recommendation:** Remove legacy wrapping logic. Update all callers to provide hex_coord, galaxy, empire. Delete alias properties.
**Effort:** Medium

#### MAJOR: Legacy Tuple-Based Component Selection API
**ID:** LEG-UI1-003
**Location:** `game/ui/screens/builder/component_ref.py:73-97`
**Issue:** ComponentRef provides from_tuple() and to_tuple() conversion methods to bridge from old (layer_type, index, component) tuple-based API. These methods exist solely for backward compatibility but no callers found.
**Impact:** Callers can still use the old fragile tuple pattern instead of migrating to typed ComponentRef.
**Recommendation:** Delete from_tuple() and to_tuple() methods. Grep confirms no callers exist.
**Effort:** Simple

#### MAJOR: Unused Getters in Stats Configuration
**ID:** LEG-UI1-004
**Location:** `game/ui/screens/builder/stats_config.py:140-149, 274-278`
**Issue:** Functions get_fuel_recharge(), get_ammo_recharge(), and get_zero() are defined and registered in GETTERS registry but never referenced by data/stats_layout.json. Comments indicate "Placeholder: No regen mechanism yet".
**Impact:** Dead code increases maintenance surface. Functions serve no purpose.
**Recommendation:** Remove the three unused getter functions and their registry entries.
**Effort:** Simple

#### MAJOR: Hardcoded Backward Compat Fallback for Input Handling
**ID:** LEG-UI1-005
**Location:** `game/ui/screens/strategy_input_handler.py:24-26, 102-107, 316-390`
**Issue:** StrategyInputHandler falls back to hardcoded key checks when InputMapper is not provided. _handle_keydown_legacy() (316-390) contains duplicated hardcoded pygame key checks for all fleet operations.
**Impact:** Two parallel input dispatch paths. Bug fixes or new keybindings only affect mapped path, leaving legacy path out of sync.
**Recommendation:** Remove legacy fallback entirely. Require InputMapper at construction.
**Effort:** Medium

#### MAJOR: Backward Compatibility Properties in WorkshopViewModel
**ID:** LEG-UI1-006
**Location:** `game/ui/screens/workshop_viewmodel.py:124-127`
**Issue:** selected_component property is marked "Alias for primary_selection for backward compatibility". Adds no value, just maintains old call signature.
**Impact:** Callers can continue using old name instead of migrating to primary_selection.
**Recommendation:** Delete selected_component alias. Rename callers to use primary_selection.
**Effort:** Simple

#### MAJOR: Legacy Component Editor Still Used
**ID:** LEG-UI1-007
**Location:** `game/ui/screens/builder/legacy_components.py`, `game/ui/screens/builder/main.py:45`
**Issue:** File explicitly named legacy_components.py contains ModifierEditorPanel. Though updated to use ComponentService, file name indicates awaiting full migration.
**Impact:** Confuses code maintenance, unclear if system should be modernized or replaced.
**Recommendation:** Rename to modifier_editor.py if keeping, or plan complete replacement.
**Effort:** Medium

#### MINOR: Sync Methods for Backward Compatibility in BuilderRightPanel
**ID:** LEG-UI1-008
**Location:** `game/ui/screens/builder/right_panel.py:324-327`
**Issue:** _sync_from_stats_panel() syncs internal references for backward compatibility. Copies rows_map and current_logistics_keys to maintain compat with code expecting direct attributes.
**Impact:** Keeps dual access paths alive.
**Recommendation:** Remove sync method and direct attributes. Update references to go through self.stats_panel.
**Effort:** Simple

#### MINOR: DesignReportPanel Backward Compatibility Sync
**ID:** LEG-UI1-009
**Location:** `game/ui/panels/design_report_panel.py:165-166`
**Issue:** rows_map exposed directly on DesignReportPanel for test compatibility, though authoritative source is internal _stats_panel.
**Impact:** Tests depend on implementation details rather than public API.
**Recommendation:** Update tests to access rows_map through public interface. Remove direct exposure.
**Effort:** Simple

#### MINOR: Deprecated action_return_to_test_lab Flag Usage in TestLabScreen
**ID:** LEG-UI1-010
**Location:** `game/ui/screens/test_lab/screen.py:457`
**Issue:** TestLabScreen explicitly sets self.game.battle_scene.action_return_to_test_lab = False, relying on deprecated flag mechanism.
**Impact:** Keeps deprecated flag mechanism alive.
**Recommendation:** Update to use scene_callback mechanism instead.
**Effort:** Simple

#### MINOR: Dead Legacy Buttons List
**ID:** LEG-UI1-011
**Location:** `game/ui/screens/test_lab/screen.py:307`
**Issue:** self.buttons = [] is legacy list "kept for compatibility but not used for new UIButtons". Never read.
**Impact:** Dead attribute confuses developers.
**Recommendation:** Delete the attribute and comment.
**Effort:** Simple

## Top 5 Priority Issues
1. **LEG-UI1-001** (CRITICAL): Deprecated BattleScreen action flags - ambiguity about which transition system is authoritative
2. **LEG-UI1-002** (CRITICAL): BuildQueueScreen backward compat wrapping - synthetic legacy ID and test aliases
3. **LEG-UI1-005** (MAJOR): Parallel input dispatch paths in StrategyInputHandler - duplicated logic
4. **LEG-UI1-004** (MAJOR): Unused placeholder getter functions - quick win deletion
5. **LEG-UI1-003** (MAJOR): ComponentRef tuple conversion API - blocks eradication of tuple patterns
