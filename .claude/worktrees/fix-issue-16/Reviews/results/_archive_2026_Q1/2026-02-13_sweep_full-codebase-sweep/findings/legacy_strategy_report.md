# Legacy System Holdovers Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 89
- **Total Issues Found:** 10
- **Critical:** 0 | **Major:** 3 | **Minor:** 5 | **Info:** 2

## Findings

#### MAJOR: Legacy Behavior Branch in FleetOrderProcessor.process_colonize
**ID:** LEG-STR-001
**Location:** `game/strategy/engine/fleet_order_processor.py:180,231`
**Issue:** The `process_colonize` method has an explicit "legacy behavior" branch when `component_registry` is None that removes the entire fleet instead of just the colony ship.
**Impact:** Code maintains two code paths - the modern one (remove only colony ship) and legacy one (remove entire fleet). The comment explicitly says "Legacy behavior: remove entire fleet".
**Recommendation:** Audit all callers to ensure they always pass component_registry, then remove the legacy branch. If tests are the only callers without registry, update those tests.
**Effort:** Medium

#### MAJOR: Backward Compatibility Comment in GameSession._get_fleet_by_id
**ID:** LEG-STR-002
**Location:** `game/strategy/engine/game_session.py:210-227`
**Issue:** Method has explicit "Falls back to O(n) empire iteration for backward compatibility with tests" comment. The fallback path duplicates lookup logic.
**Impact:** Creates confusion about which path is authoritative. O(n) fallback may mask bugs in the O(1) path if tests only exercise the fallback.
**Recommendation:** Update all tests to properly register fleets with Galaxy, remove the O(n) fallback.
**Effort:** Medium

#### MAJOR: Legacy Items in ProductionEngine
**ID:** LEG-STR-003
**Location:** `game/strategy/engine/production_engine.py:96,154,220-221`
**Issue:** Multiple code paths handle "legacy items without cost tracking" - items that lack the new `cost_per_tick` and `resources_consumed` fields from PROJ-75. Comments explicitly state "Legacy items without cost tracking - fall back to old behavior".
**Impact:** Two code paths must be maintained - one for legacy queue items (turn-based decrement only) and one for new items (tick-based resource consumption).
**Recommendation:** Verify no legacy queue items exist in current saves, remove legacy handling code paths.
**Effort:** Medium

#### MINOR: Backward Compatibility Comment in FleetNavigationService
**ID:** LEG-STR-004
**Location:** `game/strategy/services/fleet_navigation_service.py:410-411`
**Issue:** Method `project_path_as_dicts` docstring explicitly states "for backward compatibility" as its purpose.
**Impact:** Low - the method is thin wrapper returning dicts from PathSegment objects. The comment suggests this was meant to be temporary.
**Recommendation:** Verify all callers can use `project_path()` directly with PathSegment objects, deprecate dict conversion.
**Effort:** Simple

#### MINOR: Backward Compat Default in Planet.from_dict
**ID:** LEG-STR-005
**Location:** `game/strategy/data/planet.py:355`
**Issue:** Comment explicitly states "default empty for backward compat" for deserializing populations list.
**Impact:** Low - this is save file deserialization defensiveness, not runtime behavior. Old saves without populations field will work.
**Recommendation:** Since project policy states "save files are disposable", this compat layer could be removed along with any old saves.
**Effort:** Simple

#### MINOR: Backward Compat Defaults in RaceConfig.from_dict
**ID:** LEG-STR-006
**Location:** `game/strategy/data/race_config.py:198`
**Issue:** Method docstring explicitly mentions "backward-compatible defaults" for deserialization.
**Impact:** Low - provides sensible defaults for missing fields during deserialization. Standard defensive coding for save file loading.
**Recommendation:** This is acceptable defensive coding for configuration files. Mark as acceptable if race configs are user-editable content (not disposable saves).
**Effort:** N/A (acceptable pattern for config files)

#### MINOR: Old Layer Format Detection in DesignMetadata
**ID:** LEG-STR-007
**Location:** `game/strategy/data/design_metadata.py:176-178,221`
**Issue:** Code detects and warns about "Old format" for layer data structure, then silently produces empty results for old formats.
**Impact:** Old design files with incorrect layer format produce incorrect combat_power and resource_cost calculations with only a warning.
**Recommendation:** If old format designs exist, either migrate them or fail loudly. Do not silently produce wrong data.
**Effort:** Simple

#### MINOR: Save Compatibility Field in DesignMetadata
**ID:** LEG-STR-008
**Location:** `game/strategy/data/design_metadata.py:36-38`
**Issue:** Comment states `sprite_preview` field "exists as a placeholder for save file compatibility".
**Impact:** Low - unused field consuming space in metadata. Comment suggests it is kept for file format stability.
**Recommendation:** Either implement the feature or remove the field. Per project policy, save files are disposable.
**Effort:** Simple

#### INFO: Test Mock Compatibility in FleetOrderProcessor
**ID:** LEG-STR-009
**Location:** `game/strategy/engine/fleet_order_processor.py:429,456-458`
**Issue:** Code explicitly wrapped in try/except "for mock compatibility in tests" when calling fleet methods.
**Impact:** Masks potential production bugs if these methods fail. Test mocks should properly implement the interface.
**Recommendation:** Update test mocks to properly implement fleet cargo methods, remove try/except guards.
**Effort:** Simple

#### INFO: Intercept Function Accepts Both Fleet and NavigationState
**ID:** LEG-STR-010
**Location:** `game/strategy/data/pathfinding.py:392`
**Issue:** Comment states function "Supports both for backward compatibility and pure function usage" for accepting both Fleet and NavigationState.
**Impact:** None - this is explicitly an adapter pattern comment (line 283-288 has detailed explanation that this is "intentional adapter pattern (not legacy compatibility)").
**Recommendation:** No action needed - the code correctly identifies this as a proper adapter pattern, not legacy compatibility.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-STR-001 (MAJOR):** FleetOrderProcessor has explicit "legacy behavior" branch removing entire fleet. Update callers to always pass component_registry, remove legacy path.

2. **LEG-STR-002 (MAJOR):** GameSession._get_fleet_by_id has O(n) fallback "for backward compatibility with tests". Update tests to use proper fleet registration.

3. **LEG-STR-003 (MAJOR):** ProductionEngine maintains dual code paths for legacy queue items without cost tracking fields. Verify no legacy items exist, remove old path.

4. **LEG-STR-007 (MINOR):** DesignMetadata silently produces wrong calculations for old layer formats. Either migrate old files or fail loudly.

5. **LEG-STR-004 (MINOR):** FleetNavigationService.project_path_as_dicts exists "for backward compatibility". Evaluate if callers can use PathSegment directly.
