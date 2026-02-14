# Legacy System Holdovers Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 86
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 5 | **Minor:** 5 | **Info:** 2

## Findings

#### MAJOR: Backward Compatibility Fallback in GameSession._get_fleet_by_id()
**ID:** LEG-STR-001
**Location:** `game/strategy/engine/game_session.py:210-232`
**Issue:** After the Galaxy fleet registry was added (PROJ-87 Phase 6), a fallback O(n) iteration pattern was kept "for backward compatibility with tests that don't register fleets with the galaxy." This creates two code paths where only the registry path should exist.
**Impact:** Confusion about which lookup is authoritative, maintenance burden from supporting two paths, tests may pass with unregistered fleets masking real bugs.
**Recommendation:** Update all tests to register fleets properly with galaxy, then remove the fallback iteration loop entirely.
**Effort:** Medium

#### MAJOR: Legacy Behavior Comments in FleetOrderProcessor.process_colonize()
**ID:** LEG-STR-002
**Location:** `game/strategy/engine/fleet_order_processor.py:180-265`
**Issue:** Multiple comments reference "legacy behavior" for when `component_registry` is None:
- Line 180: "When None, entire fleet is removed (legacy behavior)"
- Line 230: "# Legacy behavior: pick first valid candidate"
- Line 264: "# Legacy behavior: remove entire fleet"
This indicates a migration from whole-fleet removal to selective colony-ship removal that was never completed.
**Impact:** Two distinct behaviors (legacy vs modern) exist based on whether registry is provided. Tests without registry may exercise the wrong path.
**Recommendation:** Ensure component_registry is always provided during turn execution, then remove all None-handling legacy branches.
**Effort:** Medium

#### MAJOR: Backward Compatibility Default in Planet.from_dict()
**ID:** LEG-STR-003
**Location:** `game/strategy/data/planet.py:385`
**Issue:** Comment says "Deserialize populations (default empty for backward compat)" - this is save file compatibility code for saves that predate multi-species populations. Per project policy, old saves should be discarded, not accommodated.
**Impact:** Maintains code for save format that should be obsolete.
**Recommendation:** Remove the "for backward compat" logic. If populations is missing from save data, it indicates a corrupted save that should fail to load.
**Effort:** Simple

#### MAJOR: Backward Compatibility in FleetNavigationService.project_path_as_dicts()
**ID:** LEG-STR-004
**Location:** `game/strategy/services/fleet_navigation_service.py:410`
**Issue:** Method docstring says "return as list of dicts for backward compatibility." The PathSegment dataclass has a to_dict() method specifically for this, suggesting callers should have been migrated to use PathSegment directly.
**Impact:** Maintains unnecessary wrapper method that converts typed dataclasses to untyped dicts.
**Recommendation:** Audit all callers and migrate them to use project_path() returning PathSegment objects directly, then remove project_path_as_dicts().
**Effort:** Medium

#### MAJOR: Legacy Production Items in ProductionEngine
**ID:** LEG-STR-005
**Location:** `game/strategy/engine/production_engine.py:96, 154, 220`
**Issue:** Multiple references to "legacy items without cost tracking":
- Line 96: "fields (legacy items) are skipped for resource consumption"
- Line 154: "Skip legacy items without cost tracking"
- Line 220: "Legacy items without cost tracking - fall back to old behavior"
This indicates an incomplete migration from a simple turns-based system to per-tick resource consumption (PROJ-75).
**Impact:** Two production systems (legacy turn decrement vs tick-based resource consumption) running in parallel.
**Recommendation:** Ensure all queue items have cost_per_tick set (migrate old items on load or reject them), then remove legacy fallback code.
**Effort:** Medium

#### MINOR: Unused Import StarType in galaxy.py
**ID:** LEG-STR-006
**Location:** `game/strategy/data/galaxy.py:11`
**Issue:** `StarType` is imported but not used directly in the module (it's used via StarGenerator).
**Impact:** Minor clutter.
**Recommendation:** Remove unused import.
**Effort:** Simple

#### MINOR: Reserved/Placeholder Field sprite_preview in DesignMetadata
**ID:** LEG-STR-007
**Location:** `game/strategy/data/design_metadata.py:37-38`
**Issue:** Field `sprite_preview` is "Reserved for future use" and exists "as a placeholder for save file compatibility." This is pre-emptive compatibility for a feature that may never be implemented.
**Impact:** Field is serialized/deserialized but never populated or read.
**Recommendation:** Remove the field. If sprite preview is ever implemented, add it then.
**Effort:** Simple

#### MINOR: Backward Compatibility Comment in race_config.py
**ID:** LEG-STR-008
**Location:** `game/strategy/data/race_config.py:199`
**Issue:** Method docstring says "Deserialize from dictionary with backward-compatible defaults." All the .get() calls with defaults are for optional fields, not backward compatibility.
**Impact:** Misleading documentation suggests old format support.
**Recommendation:** Change docstring to "Deserialize from dictionary with sensible defaults."
**Effort:** Simple

#### MINOR: Backward Compatibility Comment in game_config.py
**ID:** LEG-STR-009
**Location:** `game/strategy/engine/game_config.py:82`
**Issue:** Comment says "Only include race fields if set (backwards compatibility)" - but this is just sparse serialization, not compatibility with old formats.
**Impact:** Misleading comment.
**Recommendation:** Change to "Only include optional race fields when set (sparse serialization)."
**Effort:** Simple

#### MINOR: Support for Old Layer Format in DesignMetadata
**ID:** LEG-STR-010
**Location:** `game/strategy/data/design_metadata.py:176-178, 221-222`
**Issue:** Code handles "Old format detected" with a warning for layers that aren't in list format. Per project policy, old formats should be rejected, not gracefully handled.
**Impact:** Silently handles corrupted or old-format design files instead of failing.
**Recommendation:** Raise an exception instead of logging warning and returning empty components.
**Effort:** Simple

#### INFO: hasattr() Checks for Standard Attributes
**ID:** LEG-STR-011
**Location:** Multiple files
**Issue:** Several files use `hasattr()` to check for standard attributes that should always exist on typed objects:
- `game/strategy/engine/game_session.py:129` - checking `galaxy.get_system_of_object`
- `game/strategy/data/galaxy.py:144,191,215,231,297,366,406,409,911` - checking `location`, `diameter_hexes`, `occupied_hexes`
- `game/strategy/engine/fleet_order_processor.py:142,215,476,620` - checking `location`, `planet_type`, `race_id`

Most of these appear to be defensive coding for mocked objects in tests rather than actual backward compatibility. However, they add runtime overhead and suggest incomplete type contracts.
**Impact:** Code clutter, minor performance overhead.
**Recommendation:** Review each usage. Replace test mocks with proper typed fixtures where possible.
**Effort:** Medium

#### INFO: Placeholder Production Sources in EmpireEconomyCalculator
**ID:** LEG-STR-012
**Location:** `game/strategy/engine/empire_economy_calculator.py:92-105`
**Issue:** Comments mark several fields as "Placeholder production sources (future implementation)" and "Placeholder expense categories (future implementation)". These fields exist in EmpireEconomySnapshot but are always set to zero.
**Impact:** Code exists for features that may never be implemented.
**Recommendation:** Either implement these features or remove the placeholder fields. Per project policy, prefer removing dead code over keeping placeholders.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-STR-001** (GameSession fallback iteration) - Creates dual lookup paths where only one should exist. Tests may hide bugs by not requiring proper fleet registration.

2. **LEG-STR-002** (FleetOrderProcessor legacy behavior) - Entire colonization subsystem has two behaviors based on registry availability. Should enforce registry is always provided.

3. **LEG-STR-005** (ProductionEngine legacy items) - Two production systems running in parallel (turn-based vs tick-based). Incomplete PROJ-75 migration.

4. **LEG-STR-004** (FleetNavigationService dict wrapper) - Maintains untyped dict API when typed PathSegment exists. Simple cleanup once callers are audited.

5. **LEG-STR-003** (Planet backward compat populations) - Per project policy, save compatibility code should not exist. Fix tests/saves and remove.
