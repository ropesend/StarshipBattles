# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 41
- **Total Issues Found:** 6
- **Critical:** 0 | **Major:** 1 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Stale Documentation Reference to Removed TargetingException
**ID:** LEG-FND-001
**Location:** `game/ai/target_evaluator.py:16`
**Issue:** The module docstring states "For fatal errors that indicate programming bugs, TargetingException is raised." However, TargetingException was removed from the codebase (it no longer exists in game/core/exceptions.py). The documentation is now misleading.
**Impact:** Developers may search for TargetingException, find no definition, and be confused about error handling. The AI module actually uses defensive programming with logging and fallback behavior, not exceptions.
**Recommendation:** Update the docstring to accurately describe the current error handling approach (defensive programming with logging).
**Effort:** Simple

#### MINOR: Extensive getattr() with Defaults in AI Module
**ID:** LEG-FND-002
**Location:** `game/ai/controller.py`, `game/ai/behaviors.py`, `game/ai/target_evaluator.py`, `game/ai/combat_utils.py`
**Issue:** The AI module makes heavy use of `getattr(obj, 'attr', default)` patterns (30+ instances). While documented as "defensive programming for robustness," this pattern can mask bugs where attributes should exist but don't. Many of these access patterns seem to be handling raw Ship objects vs ShipControllableAdapter differences.
**Impact:** Could mask interface contract violations. Makes code harder to maintain as expected attributes are unclear.
**Recommendation:** Review whether all these defensive patterns are necessary post-PROJ-86 (God Class Decomposition). The ShipControllableAdapter should provide consistent interface. Consider using explicit type guards or Protocol checks instead of broad getattr fallbacks.
**Effort:** Medium

#### MINOR: Raw Ship vs Adapter Access Pattern in FormationBehavior
**ID:** LEG-FND-003
**Location:** `game/ai/behaviors.py:276-400` (FormationBehavior class)
**Issue:** Comments explicitly note that `formation_master returns a raw Ship, not adapter` and code accesses `master.position`, `master.angle`, `master.is_alive` directly on raw Ship objects while the adapter is used for `self.controller.ship`. This suggests incomplete adapter encapsulation.
**Impact:** Inconsistent access patterns make the code harder to understand and maintain. May indicate the adapter pattern wasn't fully applied to formation relationships.
**Recommendation:** Either extend ShipControllableAdapter to handle formation master access consistently, or document this as intentional design (formations access raw Ship for performance).
**Effort:** Medium

#### MINOR: Singleton Pattern Still in Use Despite DI Preference
**ID:** LEG-FND-004
**Location:** Multiple files in assigned scope (9 classes using SingletonMeta)
**Issue:** The codebase uses SingletonMeta for Logger, Profiler, StrategyManager, StrategyMetadataService, RegistryManager, and others. CLAUDE.md states "Dependency injection replaced singletons in many areas" but singletons are still prevalent in core infrastructure.
**Impact:** Singletons make testing harder and create hidden dependencies. However, these are legitimately global services (logging, profiling, registry) where singleton may be appropriate.
**Recommendation:** No action needed for Logger/Profiler (legitimately global). Consider whether StrategyManager and StrategyMetadataService should use DI instead - they're called via `.instance()` from AI code which could instead receive them as constructor parameters.
**Effort:** Complex (architectural decision)

#### MINOR: Unused AI_STATE_ERROR ErrorCode
**ID:** LEG-FND-005
**Location:** `game/core/error_codes.py:153`
**Issue:** ErrorCode.AI_STATE_ERROR = "A001" is defined but only referenced in test coverage files (`test_error_codes_coverage.py`). No actual production code uses this error code for AI state handling.
**Impact:** Dead enumeration member adds slight confusion when reviewing error codes.
**Recommendation:** Verify if AI state error handling was planned but never implemented, or if this is a vestige from old code. Remove if unused, or add proper usage if intended.
**Effort:** Simple

#### INFO: Well-Organized Research Module
**ID:** LEG-FND-006
**Location:** `game/research/` (entire module)
**Issue:** None - This module is cleanly implemented with no legacy patterns detected. Uses proper dataclasses, clear separation (data/systems/ui), no singletons, and follows modern patterns.
**Impact:** Positive - this is a model for how other modules should look.
**Recommendation:** Use as reference when refactoring other modules.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-FND-001 (MAJOR):** Stale documentation reference to removed TargetingException in target_evaluator.py docstring. Update to match current error handling approach.

2. **LEG-FND-002 (MINOR):** Heavy getattr() usage in AI module may mask interface violations. Review post-God-Class-Decomposition to see if defensive patterns are still needed.

3. **LEG-FND-003 (MINOR):** Inconsistent raw Ship vs Adapter access in FormationBehavior. Document or fix the encapsulation gap.

4. **LEG-FND-004 (MINOR):** Singleton pattern still prevalent - document which singletons are intentional (logging, profiling) vs candidates for DI migration.

5. **LEG-FND-005 (MINOR):** AI_STATE_ERROR unused - simple cleanup opportunity to remove dead enumeration member.

## Cleanup Verified Since Previous Sweep

The following issues from previous sweeps have been verified as FIXED:

1. **FIXED:** `load_resources()` backward compatibility wrapper - removed from `game/core/resources.py`
2. **FIXED:** AIException and TargetingException classes - removed from `game/core/exceptions.py`
3. **FIXED:** DEBUG_SCREENSHOTS renamed to ENABLE_SCREENSHOTS (PROJ-121) in `game/core/constants.py:42`

## Notes

The Foundation shard is remarkably clean after multiple cleanup cycles. Evidence of prior work:

- **No TODO/FIXME/HACK comments** found in any of the 41 files
- **No "legacy", "deprecated", "compat", "old_" naming patterns** in active code
- **Registry pattern consistently used** where appropriate
- **Error codes well-organized** with clear enum structure
- **Protocols properly defined** in game/core/protocols.py

The research subsystem (game/research/) is particularly well-structured as a standalone module.
The engine subsystem (game/engine/) is minimal and focused with good test coverage.
