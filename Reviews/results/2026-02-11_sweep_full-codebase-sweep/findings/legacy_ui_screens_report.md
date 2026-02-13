# Legacy System Holdovers Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (`game/ui/screens/` and `game/ui/panels/`)
- **Files Scanned:** 134 (109 in screens/, 25 in panels/)
- **Total Issues Found:** 16
- **Critical:** 1 | **Major:** 5 | **Minor:** 8 | **Info:** 2

## Findings

#### CRITICAL: Legacy BuilderScreen (builder/main.py) - 1123-line Dead Module
**ID:** LEG-UI1-001
**Location:** `game/ui/screens/builder/main.py:1-1123`
**Issue:** The entire `BuilderScreen` class (1123 lines) is the original standalone ship builder, superseded by `DesignWorkshopScreen` (workshop_screen.py) which uses MVVM architecture and dependency injection. `BuilderScreen` is never imported or instantiated anywhere in production code (`game/` directory). It is only referenced in a few test import-verification files. It also drags along its own `ModifierEditorPanel` in `builder/modifier_editor.py` (196 lines, labeled "Legacy modifier editor panel" in its docstring), which duplicates the production `ModifierEditorPanel` in `panels/builder_widgets.py`. The legacy builder uses `RegistryManager.instance()` singleton access (line 957) instead of the project-standard DI pattern.
**Impact:** 1319 lines of dead production code that duplicates the production workshop screen. Creates confusion about which builder system is authoritative. The duplicate `ModifierEditorPanel` class name creates import ambiguity. Uses the deprecated singleton pattern the project explicitly migrated away from.
**Recommendation:** Delete `builder/main.py` and `builder/modifier_editor.py` entirely. Update the few test verification files that reference them. The `builder/` subpackage's other modules (left_panel, right_panel, layer_panel, etc.) are shared by both builders and should remain.
**Effort:** Medium (need to verify test-only references before deleting)

#### MAJOR: Backward Compatibility Aliases in Race Gallery Panels
**ID:** LEG-UI1-002
**Location:** `game/ui/panels/race_flag_gallery.py:164-183`, `game/ui/panels/race_portrait_gallery.py:152-171`
**Issue:** Both gallery classes have explicit "Legacy compatibility aliases" sections with 3 property aliases each (`flag_buttons`/`portrait_buttons`, `flag_scroll`/`portrait_scroll`, `flag_preview_panel`/`portrait_preview_panel`) and wrapper methods (`on_flag_selected`, `on_portrait_selected`). Grep confirms these aliases are NEVER called from any production code. They are only exercised in tests that were written against the old API. The base class `BaseGallery` (extracted in PROJ-108) provides the canonical attribute names (`asset_buttons`, `scroll_container`, `preview_panel`, `on_asset_selected`).
**Impact:** Active backward compatibility layer that directly violates the project's "eradicate old system" policy. Creates confusion about which API to use.
**Recommendation:** Delete all 6 alias properties and 2 wrapper methods. Update tests to use the base class names (`asset_buttons`, `on_asset_selected`, etc.).
**Effort:** Simple

#### MAJOR: Deprecated Methods on BattleScreen (handle_click, handle_scroll)
**ID:** LEG-UI1-003
**Location:** `game/ui/screens/battle_screen.py:570-597`
**Issue:** Two methods are marked `DEPRECATED: Use handle_event() instead for IScene compliance` in their docstrings: `handle_click(mx, my, button, screen_size)` (lines 570-590) and `handle_scroll(scroll_y, screen_height)` (lines 592-597). After PROJ-88 Phase 5, `app.py` exclusively uses `handle_event()` for all scenes. These deprecated methods duplicate the logic already in `handle_event()` (lines 302-317). No external caller with the `screen_size` signature exists.
**Impact:** 28 lines of dead code that duplicate event handling logic. Risk of divergence if one path is updated but not the other.
**Recommendation:** Delete both deprecated methods.
**Effort:** Simple

#### MAJOR: Legacy Tuple Format Support in detail_panel.py
**ID:** LEG-UI1-004
**Location:** `game/ui/screens/builder/detail_panel.py:82-99`
**Issue:** `on_selection_changed()` accepts three data formats: `ComponentRef` (new), `tuple` (legacy `(layer, idx, comp)` format), and direct component objects. The comment on line 93 explicitly says `# LEGACY: Support old (layer, idx, comp) tuple format`. The new `ComponentRef` pattern was introduced specifically to replace these fragile tuples. All producers in the codebase should now emit `ComponentRef` objects.
**Impact:** Maintains a deprecated data format path that adds complexity and prevents full adoption of the typed `ComponentRef` pattern.
**Recommendation:** Audit all callers of `on_selection_changed()`. If none pass raw tuples, remove the `isinstance(selection_data, tuple)` branch. If some do, migrate them to use `ComponentRef`.
**Effort:** Medium

#### MAJOR: Backwards Compatibility Fallbacks in workshop_event_router.py
**ID:** LEG-UI1-005
**Location:** `game/ui/screens/workshop_event_router.py:199-304`, `game/ui/screens/builder/main.py:513-592`
**Issue:** Three handler methods (`_handle_remove_group`, `_handle_remove_individual`, `_handle_add_component`) in both `workshop_event_router.py` and `builder/main.py` contain backwards-compatibility code that checks `isinstance(data, tuple)` and falls back to treating `data` as a bare value if it's not a tuple. The docstrings explicitly state this is "for backwards compatibility". However, the ONLY producer of these action payloads (`structure_list_items.py` lines 181, 183, 339, 341) ALWAYS sends tuples with `(component/group_key, layer_type)`. The non-tuple fallback path is dead code.
**Impact:** ~50 lines of unreachable fallback code across two files that obscures the actual data contract. The "search all layers" fallback in the non-tuple path is significantly slower than the targeted-layer path.
**Recommendation:** Remove all `isinstance(data, tuple)` checks and the `else` fallback branches. Always unpack as `(key, layer_type)`. For `builder/main.py`, this is moot if LEG-UI1-001 is addressed (delete the file).
**Effort:** Simple

#### MAJOR: Legacy Shim Skip List in detail_panel.py
**ID:** LEG-UI1-006
**Location:** `game/ui/screens/builder/detail_panel.py:162-164`
**Issue:** Lines 162-164 contain `if k in ["ProjectileWeapon", "BeamWeapon", "Armor"]: continue` with comment "Skip legacy shims (if they still exist in data)". This is a hardcoded skip list for ability names that were part of an old ability system. PROJ-58 (Eradicate Backward Compat Shims) should have ensured these shims no longer exist in data. If they do still exist, that's a data cleanup issue; if they don't, this is dead guard code.
**Impact:** Confusing guard clause that references a system that should have been eradicated. Masks potential data issues.
**Recommendation:** Verify no component data contains these ability keys. If clean, delete the skip block.
**Effort:** Simple

#### MINOR: Duplicate show_overlay Toggle Keybindings in BattleScreen
**ID:** LEG-UI1-007
**Location:** `game/ui/screens/battle_screen.py:324-332`
**Issue:** Two different keys toggle the exact same `show_overlay` property: `K_F3` (line 325, toggles `self.ui.show_overlay`) and `K_o` (line 332, toggles `self.show_overlay` which is a property delegating to `self.ui.show_overlay`). Both produce identical results. The comment on line 323 says "Visual controls (from update_visuals)" and line 330 says "Speed/pause controls (from BattleInputHandler)", suggesting these came from two different source files during a merge/extraction.
**Impact:** Confusing duplicate keybinding. Minor user confusion if both are documented.
**Recommendation:** Remove one of the duplicate toggle bindings (likely K_o, keeping F3 as the canonical toggle).
**Effort:** Simple

#### MINOR: Stale Comment about Removed Duplicate Method
**ID:** LEG-UI1-008
**Location:** `game/ui/screens/battle_screen.py:512`
**Issue:** Line 512 contains the comment `# Note: method removed duplicate update_visuals here (it was in orig file twice?)`. This is a historical note about a past cleanup, providing no value to current readers.
**Impact:** Noise in the codebase.
**Recommendation:** Delete the comment.
**Effort:** Simple

#### MINOR: Hardcoded 1920x1080 Fallback Resolution
**ID:** LEG-UI1-009
**Location:** `game/ui/screens/new_game_setup_screen.py:433-434`
**Issue:** `screen_width = 1920` and `screen_height = 1080` are used as fallback values if `ui_manager` is None. The project targets 2560x1600 minimum resolution. 1920x1080 is below the minimum display target and would cause incorrect centering on the actual target resolution.
**Impact:** If the fallback is ever triggered, the race setup dialog would be mispositioned.
**Recommendation:** Update fallback to 2560x1600 or, better, make `ui_manager` required (it's always available in practice).
**Effort:** Simple

#### MINOR: Duplicate Assignment on Consecutive Lines
**ID:** LEG-UI1-010
**Location:** `game/ui/screens/builder/left_panel.py:38-39`
**Issue:** `self.list_y = 125 # Was 80` appears on two consecutive lines (38 and 39), an obvious copy-paste artifact.
**Impact:** Harmless but sloppy. Second assignment overwrites the first with the same value.
**Recommendation:** Delete line 39.
**Effort:** Simple

#### MINOR: Unnecessary hasattr Guard for _facade
**ID:** LEG-UI1-011
**Location:** `game/ui/screens/strategy_window_manager.py:201`
**Issue:** `hasattr(self.scene, "_facade")` guard before accessing `self.scene._facade.get_all_events()`. The `_facade` attribute is always created in `StrategyScreen.__init__()` (line 77). This guard is unnecessary and suggests the code was written before the facade was guaranteed.
**Impact:** Minor: unnecessary defensive check that suggests uncertainty about the architecture.
**Recommendation:** Remove the `hasattr` check; access `self.scene._facade` directly.
**Effort:** Simple

#### MINOR: Dead hasattr Check for print_headless_summary
**ID:** LEG-UI1-012
**Location:** `game/ui/screens/battle_screen.py:657-660`
**Issue:** `if hasattr(self.ui, 'print_headless_summary')` always evaluates to False because `BattleUI` does not define `print_headless_summary`. The `else` branch (line 660, `log_info(...)`) always executes.
**Impact:** Dead conditional branch; the delegation to `self.ui.print_headless_summary()` never runs.
**Recommendation:** Remove the `hasattr` check and the dead `if` branch. Keep only the `log_info` call.
**Effort:** Simple

#### MINOR: Monkey-Patching Domain Objects with Temporary Attributes
**ID:** LEG-UI1-013
**Location:** `game/ui/screens/strategy_renderer.py:446-454`, `game/ui/screens/planet_list_filters.py:26-31`
**Issue:** Two UI modules attach temporary attributes directly to domain objects: `strategy_renderer.py` sets `p._temp_screen_pos` and `p._temp_draw_r` on Planet objects during rendering; `planet_list_filters.py` sets `p._temp_system_ref`, `p._cached_gravity_g`, `p._cached_mass_earth`, `p._cached_name_lower`, and `p._cached_type_category` on Planet objects during filtering. This violates the layer separation principle (UI mutating domain objects) and can cause subtle bugs if cached values become stale.
**Impact:** UI layer pollutes domain objects with rendering/filtering state. Cached values are never cleaned up and could leak across sessions.
**Recommendation:** Use a local dict keyed by planet ID to store computed values instead of monkey-patching domain objects. For `strategy_renderer.py`, store screen positions in a local list within the render loop.
**Effort:** Medium

#### MINOR: Unused Module-Level Constants
**ID:** LEG-UI1-014
**Location:** `game/ui/screens/builder/stats_config.py:355-356`
**Issue:** `STATS_CREW_LOGISTICS` and `STATS_FIGHTER_SUPPORT` are loaded from JSON config at module level but never referenced anywhere in the codebase (confirmed via project-wide grep).
**Impact:** Unused constants loaded on every import of the module.
**Recommendation:** Delete both lines.
**Effort:** Simple

#### INFO: Deprecated Properties on StrategyScreen Still Heavily Used
**ID:** LEG-UI1-015
**Location:** `game/ui/screens/strategy_screen.py:122-149`
**Issue:** Six convenience properties (`galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire`, `human_player_ids`) are marked with the comment "NOTE: These are deprecated for external access. Use facade methods instead." However, these properties are used extensively by 8+ delegate modules (`strategy_renderer.py`, `strategy_input_handler.py`, `strategy_colonization.py`, `strategy_fleet_ops.py`, `strategy_superweapons.py`, `strategy_window_manager.py`, `strategy_event_router.py`, `strategy_camera_nav.py`). The facade (`_facade`) is barely used (4 call sites total). The migration to facade-based access was started but never completed.
**Impact:** The "deprecated" annotation is misleading since these are the primary access pattern. The facade migration is essentially abandoned, creating inconsistency.
**Recommendation:** Either complete the facade migration (move all delegate access through `_facade`) or remove the deprecation comment and accept these properties as the canonical API. Given the scope, removing the deprecation comment is the pragmatic choice.
**Effort:** Simple (if removing comment) / Complex (if completing facade migration)

#### INFO: test_lab/screen.py Accepts Game Object "for Legacy Compatibility"
**ID:** LEG-UI1-016
**Location:** `game/ui/screens/test_lab/screen.py:58, 66-67, 249-252`
**Issue:** `TestLabScreen.__init__` accepts a `game` parameter described as "for legacy compatibility, provides battle_scene access" (line 58). Line 249-252 exposes a `_components_cache` property "for backward compatibility" that delegates to the data extractor's internal cache. These are compatibility shims from when the test lab was more tightly coupled to the Game class.
**Impact:** Minor coupling artifact. The `_components_cache` property exposes an internal implementation detail.
**Recommendation:** Refactor `TestLabScreen` to accept specific dependencies instead of the entire `game` object. Remove the `_components_cache` compatibility property; callers should use the data extractor directly.
**Effort:** Medium

## Top 5 Priority Issues

1. **LEG-UI1-001 (CRITICAL):** Legacy `BuilderScreen` in `builder/main.py` -- 1319 lines of dead code (including `modifier_editor.py`) that duplicates the production `DesignWorkshopScreen`. Uses deprecated singleton pattern. Should be deleted entirely.

2. **LEG-UI1-002 (MAJOR):** Backward compatibility aliases in `race_flag_gallery.py` and `race_portrait_gallery.py` -- Explicitly labeled legacy shims that are never used in production code. Direct violation of the "eradicate old system" policy. Straightforward to remove.

3. **LEG-UI1-005 (MAJOR):** Backwards compatibility fallbacks in `workshop_event_router.py` and `builder/main.py` -- ~50 lines of dead fallback code for a data format that is never actually produced. Obscures the real data contract.

4. **LEG-UI1-003 (MAJOR):** Deprecated `handle_click`/`handle_scroll` methods on `BattleScreen` -- 28 lines of dead code duplicating `handle_event()` logic. Risk of divergence.

5. **LEG-UI1-004 (MAJOR):** Legacy tuple format support in `detail_panel.py` -- Maintains a deprecated data format path that prevents full adoption of the typed `ComponentRef` pattern.
