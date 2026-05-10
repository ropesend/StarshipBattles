# Legacy System Holdovers Sweep: Strategy

## Summary
- **Shard:** Strategy (game/strategy/)
- **Files Scanned:** 95
- **Total Issues Found:** 11
- **Critical:** 0 | **Major:** 3 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Dead Code Methods in HarvestingEngine
**ID:** LEG-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:247-274`
**Issue:** Two private methods `_get_harvester_info()` and `_get_harvester_from_registry()` are defined but never called. These instance methods duplicate module-level functions `get_harvester_info()` and `get_harvester_from_registry()` at the top of the same file. The actual harvesting logic in `_process_facility()` (line 241) calls the module-level `get_harvester_info()` function directly, not the instance methods.
**Impact:** Dead code increases maintenance burden and creates confusion about which function to use. The docstrings indicate they exist for "delegation" but no delegation occurs.
**Recommendation:** Delete `_get_harvester_info()` and `_get_harvester_from_registry()` instance methods (lines 247-274).
**Effort:** Simple

#### MAJOR: Legacy Behavior Branch in FleetOrderProcessor.process_colonize
**ID:** LEG-STR-002
**Location:** `game/strategy/engine/fleet_order_processor.py:180, 230-231, 264-265`
**Issue:** The `process_colonize()` method contains explicit "Legacy behavior" code paths that trigger when `component_registry` is None:
- Line 180: Comment states "entire fleet is removed (legacy behavior)"
- Lines 230-231: "Legacy behavior: pick first valid candidate" instead of matching colony pod types
- Lines 264-265: "Legacy behavior: remove entire fleet" instead of removing just the colony ship
These paths were intended as transitional code during PROJ-55 migration to component-aware colonization, but component registries are now always available via dependency injection (PROJ-50/58).
**Impact:** Creates confusion about authoritative behavior and maintains two parallel code paths that may drift over time.
**Recommendation:** Remove the None-registry branches and make `component_registry` a required parameter. Update all call sites to always pass the registry.
**Effort:** Medium

#### MAJOR: Backward Compatibility O(n) Fallback in GameSession._get_fleet_by_id
**ID:** LEG-STR-003
**Location:** `game/strategy/engine/game_session.py:210-232`
**Issue:** Method contains an O(n) fallback iteration "for backward compatibility with tests that don't register fleets with the galaxy". The docstring explicitly states this is a backward compatibility layer. Modern tests should use proper fleet registration, and the O(1) Galaxy registry lookup should be the only path.
**Impact:** Tests that rely on this fallback may mask real issues with fleet registration. The fallback path is rarely tested in production scenarios.
**Recommendation:** Audit test suite to ensure all tests properly register fleets with Galaxy. Remove the O(n) fallback. Add assertion that fleet should be found if it exists.
**Effort:** Medium

#### MINOR: Unused sprite_preview Field Placeholder
**ID:** LEG-STR-004
**Location:** `game/strategy/data/design_metadata.py:36-38`
**Issue:** The `sprite_preview` field is documented as "Reserved for future use" and marked as a "placeholder for save file compatibility". However, no code ever reads or writes this field beyond serialization. If sprite preview is implemented, it should be in a UI cache per the comment, making this field obsolete.
**Impact:** Minor dead field that clutters the data structure. No functional impact.
**Recommendation:** Remove the field if sprite preview is implemented elsewhere, or implement it properly with a clear purpose.
**Effort:** Simple

#### MINOR: Fallback Fleet-Like Object Creation in FleetNavigationService
**ID:** LEG-STR-005
**Location:** `game/strategy/services/fleet_navigation_service.py:173-178`
**Issue:** The `compute_path()` method creates a dynamic "fleet-like" object with `type('Fleet', (), {...})()` to pass to `find_hybrid_path()`. This is a workaround because `find_hybrid_path()` expects a Fleet object for warp capability checking. The `_ChaserProxy` adapter in `pathfinding.py` already exists for this purpose and is the proper pattern.
**Impact:** Creates a second adapter pattern where one already exists. Minor code smell.
**Recommendation:** Consider using `_ChaserProxy` consistently or extracting the warp capability interface check.
**Effort:** Simple

#### MINOR: Legacy Species Default in _execute_load
**ID:** LEG-STR-006
**Location:** `game/strategy/engine/fleet_order_processor.py:374-375`
**Issue:** Comment states "Legacy/Default: use first species" when `species_id` is not provided. This suggests older code paths that didn't track species. Modern transfers should always specify species.
**Impact:** Minor - behavior is acceptable as a default, but the "Legacy" comment suggests this was intended to be temporary.
**Recommendation:** Evaluate whether species_id should be required for transfers, or document this as intentional default behavior.
**Effort:** Simple

#### MINOR: TODO Comment for Future Feature
**ID:** LEG-STR-007
**Location:** `game/strategy/engine/fleet_order_processor.py:383`
**Issue:** Comment "TODO: If we ever track species in fleet cargo, use species_id here" indicates incomplete feature. Cargo species tracking may or may not be needed.
**Impact:** Minor - comment is a reminder, not dead code.
**Recommendation:** Either implement species tracking in cargo or remove the TODO if not needed.
**Effort:** Simple

#### MINOR: try/except for Mock Compatibility
**ID:** LEG-STR-008
**Location:** `game/strategy/engine/fleet_order_processor.py:462-466, 488-491`
**Issue:** Comments state "Wrap in try/except for mock compatibility in tests". This suggests test mocks that don't fully implement the Fleet interface. Production code should not contain special handling for incomplete test mocks.
**Impact:** Minor - defensive coding for tests, but indicates test setup could be improved.
**Recommendation:** Update tests to use proper mock objects that implement the full interface, then remove try/except blocks.
**Effort:** Simple

#### MINOR: Old Format Warning in DesignMetadata
**ID:** LEG-STR-009
**Location:** `game/strategy/data/design_metadata.py:176-178, 221-222`
**Issue:** Code logs warnings for "Old layer format" when layers are not in list format. This suggests migration from an older format that should no longer exist. The warnings have likely stopped occurring but the code remains.
**Impact:** Minor dead code path - if old format truly doesn't exist anymore, the fallback code is never executed.
**Recommendation:** Verify old format is fully eradicated from all save files and designs, then remove fallback handling.
**Effort:** Simple

#### INFO: project_path_as_dicts Backward Compatibility Wrapper
**ID:** LEG-STR-010
**Location:** `game/strategy/services/fleet_navigation_service.py:403-424`
**Issue:** Method comment explicitly states "for backward compatibility" - converts PathSegment objects to dicts. This is called by `pathfinding.py:project_fleet_path()`. However, this is not true "legacy" backward compatibility - it's internal API consistency where dict format is needed by intercept calculation code.
**Impact:** None - intentional API design, not a holdover. The comment is slightly misleading.
**Recommendation:** Update comment to clarify this is for internal API consistency with `pathfinding.py`, not external backward compatibility. Already noted in the `to_dict()` docstring.
**Effort:** Simple

#### INFO: has_race_config Check in _transfer_founding_population
**ID:** LEG-STR-011
**Location:** `game/strategy/engine/fleet_order_processor.py:472-478`
**Issue:** Complex check for "actual RaceConfig (not MagicMock)" with comment explaining why. This is defensive coding for test compatibility where empire.race_config might be a MagicMock that doesn't have proper race_id.
**Impact:** None - necessary for test compatibility. The check is well-documented.
**Recommendation:** Consider improving test setup to avoid needing this check, but low priority.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-STR-001 (Major):** Dead methods in HarvestingEngine - Clear dead code that should be deleted. Simple fix with no risk.

2. **LEG-STR-002 (Major):** Legacy colonization branches - Creates confusion about authoritative behavior. Requires verifying component_registry is always available before removal.

3. **LEG-STR-003 (Major):** O(n) fleet lookup fallback - Backward compatibility layer for tests that masks potential registration issues. Requires test audit before removal.

4. **LEG-STR-008 (Minor):** Try/except for mock compatibility - Indicates test setup issues. Cleaning up tests would allow production code simplification.

5. **LEG-STR-009 (Minor):** Old format handling in DesignMetadata - If old formats are truly gone, this dead code can be removed after verification.

## Notes

The strategy layer is generally clean with well-documented extraction patterns from god class decomposition projects (PROJ-86 through PROJ-89). Most "fallback" patterns found are either:
1. Intentional default behaviors (planet image fallbacks, pathfinding fallbacks for disconnected graphs)
2. Required for robustness (fuel endurance returning -1 for unlimited)
3. Documented adapter patterns (not legacy compatibility shims)

The codebase shows evidence of completed migrations with clear PROJ-XX comments indicating when patterns were introduced. The few legacy holdovers found are minor compared to the overall codebase quality.
