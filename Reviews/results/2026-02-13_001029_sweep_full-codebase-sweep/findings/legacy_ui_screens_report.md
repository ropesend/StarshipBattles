# Legacy System Holdovers Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 134
- **Total Issues Found:** 12
- **Critical:** 1 | **Major:** 5 | **Minor:** 5 | **Info:** 1

## Findings

#### CRITICAL: Backward Compatibility Aliases in RacePortraitGallery
**ID:** LEG-UI1-001
**Location:** `game/ui/panels/race_portrait_gallery.py:152-171`
**Issue:** The file contains four backward compatibility property aliases (`portrait_buttons`, `portrait_scroll`, `portrait_preview_panel`, `on_portrait_selected`) that are explicitly marked "Legacy compatibility aliases" and documented as "for backward compatibility." These aliases are not used by any production code - only by unit tests that specifically test these compatibility aliases.
**Impact:** These aliases create confusion about which API is authoritative (the `asset_buttons`/`scroll_container`/`preview_panel` base class attributes or the portrait-specific aliases). Tests are testing the compatibility layer rather than the actual API.
**Recommendation:** Remove the backward compatibility aliases and update tests to use the canonical attribute names (`asset_buttons`, `scroll_container`, `preview_panel`, `on_asset_selected`).
**Effort:** Simple

---

#### MAJOR: Legacy BuilderScreen (builder/main.py) Parallel to WorkshopScreen
**ID:** LEG-UI1-002
**Location:** `game/ui/screens/builder/main.py:1-1100+`
**Issue:** The file header explicitly states "Legacy standalone ship builder GUI" and notes that "DesignWorkshopScreen (workshop_screen.py) is the production version with MVVM architecture and dependency injection." The BuilderScreen class (1000+ lines) continues to exist alongside the production WorkshopScreen. While it may be used for standalone testing, this creates two parallel implementations of the same functionality.
**Impact:** Two parallel implementations create maintenance burden, potential divergence in behavior, and confusion about which system is authoritative. The legacy file still uses older patterns (e.g., direct singleton access at lines 118, 126).
**Recommendation:** Determine if BuilderScreen is still needed. If so, refactor to delegate to the production components. If not, mark for removal after verifying no critical test dependencies.
**Effort:** Complex

---

#### MAJOR: Legacy Tuple Format Support in ComponentDetailPanel
**ID:** LEG-UI1-003
**Location:** `game/ui/screens/builder/detail_panel.py:83-99`
**Issue:** The `on_selection_changed` method supports two formats: the new `ComponentRef` typed reference (preferred) and a legacy `(layer, idx, comp)` tuple format. The comment explicitly says "LEGACY: Support old (layer, idx, comp) tuple format." This is a classic backward compatibility shim.
**Impact:** Maintaining two input formats creates testing complexity and unclear API expectations. Callers may use either format, preventing clean migration.
**Recommendation:** Search for callers using the tuple format, migrate them to use `ComponentRef`, then remove the tuple format support.
**Effort:** Medium

---

#### MAJOR: Legacy API Comment in FleetReportWindow
**ID:** LEG-UI1-004
**Location:** `game/ui/screens/fleet_report_window.py:957`
**Issue:** The method `_on_remove_ship` has the docstring "Handle remove single ship from fleet (legacy API)." This suggests there's a newer API that should be used instead, but the legacy method remains.
**Impact:** The "legacy API" terminology indicates an incomplete migration - either the legacy label is stale (and should be removed) or a newer API exists that should be adopted.
**Recommendation:** Investigate whether a newer ship removal API exists. If so, migrate callers and remove this method. If not, remove the "legacy API" label.
**Effort:** Simple

---

#### MAJOR: Legacy Single-Selection Fields in EmpireBuildQueueWindow
**ID:** LEG-UI1-005
**Location:** `game/ui/screens/empire_build_queue_window.py:328`
**Issue:** The code contains a comment "Update legacy single-selection fields" followed by logic to maintain `selected_index` and `selected_source` fields alongside the newer `selected_indices` multi-selection system (PROJ-69). This is a backward compatibility shim maintaining parallel state.
**Impact:** Dual selection tracking (single and multi) creates opportunities for state inconsistency and confusion about which fields are authoritative.
**Recommendation:** Audit all callers of `selected_index` and `selected_source`. If they can use the multi-selection API, remove the legacy single-selection fields.
**Effort:** Medium

---

#### MAJOR: Fallback Mode in BuildQueueController
**ID:** LEG-UI1-006
**Location:** `game/ui/panels/build_queue_controller.py:519-560`
**Issue:** The `_add_to_fallback` method exists as a fallback mode when no queue source is explicitly set. The method comment says "Used when no queue source is explicitly set." This is a backward compatibility path for older callers that don't use the newer queue source selection system (PROJ-69).
**Impact:** Having a fallback mode allows callers to skip proper queue selection, potentially leading to incorrect behavior and making it unclear which queue will receive items.
**Recommendation:** Determine if any callers legitimately need the fallback mode. If not, make queue source selection mandatory and remove the fallback.
**Effort:** Medium

---

#### MINOR: Backward Compat Attribute Exposure in RightPanel
**ID:** LEG-UI1-007
**Location:** `game/ui/screens/builder/right_panel.py:321`
**Issue:** Comment says "Expose attributes for backward compat with update methods" followed by `_sync_from_stats_panel()`. This suggests attributes are being exposed specifically for backward compatibility rather than good API design.
**Impact:** Minor maintenance burden, unclear ownership of data.
**Recommendation:** Audit callers and determine if the exposure is still needed.
**Effort:** Simple

---

#### MINOR: Backward Compatibility in WorkshopEventRouter
**ID:** LEG-UI1-008
**Location:** `game/ui/screens/workshop_event_router.py:204,252,288`
**Issue:** Three handler methods (`_handle_remove_group`, `_handle_remove_individual`, `_handle_select_individual`) each support two data formats: the new tuple format with layer_type, and an older format "for backwards compatibility."
**Impact:** Callers can use either format, preventing clean migration to the newer format.
**Recommendation:** Search for callers using the old format, migrate them, then remove backward compatibility.
**Effort:** Simple

---

#### MINOR: Test Lab Screen Legacy Game Parameter
**ID:** LEG-UI1-009
**Location:** `game/ui/screens/test_lab/screen.py:58`
**Issue:** The `__init__` docstring states "game: Game instance (for legacy compatibility, provides battle_scene access)." The `_components_cache` property at line 251 also mentions "backward compatibility."
**Impact:** Unclear what the newer API should be. The "legacy compatibility" label suggests this pattern should be migrated.
**Recommendation:** Determine if a cleaner dependency injection pattern exists; if so, migrate.
**Effort:** Medium

---

#### MINOR: Compatibility Setter in BuilderStateManager
**ID:** LEG-UI1-010
**Location:** `game/ui/screens/builder/state_manager.py:62-64`
**Issue:** The `selected_components` setter has docstring "(for compatibility)." This suggests it exists only to maintain backward compatibility with code that directly sets this property.
**Impact:** Minor - allows direct state manipulation that bypasses proper state management methods.
**Recommendation:** Audit callers and determine if direct setting is needed or can be replaced with proper state management calls.
**Effort:** Simple

---

#### MINOR: Deprecated Properties in StrategyScreen
**ID:** LEG-UI1-011
**Location:** `game/ui/screens/strategy_screen.py:123-145`
**Issue:** The file contains a note "NOTE: These are deprecated for external access. Use facade methods instead. Internal use within StrategyScene is still valid." followed by properties for `galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire`. These properties are marked deprecated but still exist and are heavily used within the file itself (50+ internal usages).
**Impact:** The deprecation note creates confusion about whether these properties should be used. Since they're still needed internally, the deprecation may be misleading.
**Recommendation:** Either complete the facade migration and remove the properties, or remove the misleading deprecation note.
**Effort:** Complex

---

#### INFO: Legacy Keys Filtering in stats_config.py
**ID:** LEG-UI1-012
**Location:** `game/ui/screens/builder/stats_config.py:576-577`
**Issue:** Code filters out "legacy resource rows" by key: `legacy_keys = ['max_fuel', 'max_energy', 'max_ammo', 'fuel_endurance', 'ammo_endurance', 'energy_endurance']`. This suggests a previous migration from hardcoded resource keys to a dynamic system.
**Impact:** Minimal - the filtering code handles potential legacy data but the legacy data may no longer exist.
**Recommendation:** Verify if the JSON configuration file ever contains these legacy keys. If not, remove the defensive filtering.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **LEG-UI1-001 (CRITICAL) - Backward Compatibility Aliases in RacePortraitGallery**: Clear backward compatibility shim that violates the "eradicate old systems" policy. Only tests use the aliases; production code does not. Simple fix with high clarity improvement.

2. **LEG-UI1-002 (MAJOR) - Legacy BuilderScreen**: 1000+ line legacy implementation parallel to production WorkshopScreen. Major maintenance burden and potential for behavioral divergence. Needs careful audit before removal.

3. **LEG-UI1-003 (MAJOR) - Legacy Tuple Format in ComponentDetailPanel**: Classic backward compatibility pattern supporting two input formats. Clean migration target that will simplify the API.

4. **LEG-UI1-005 (MAJOR) - Legacy Single-Selection Fields**: Dual selection state tracking creates confusion about authoritative state. Should be unified with the multi-selection system.

5. **LEG-UI1-006 (MAJOR) - Fallback Mode in BuildQueueController**: Fallback code path that allows callers to bypass proper queue selection. Making queue selection mandatory would enforce better caller behavior.
