# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 41
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 5 | **Info:** 1

## Findings

#### MAJOR: Unused Exception Classes (AIException, TargetingException)
**ID:** LEG-FND-001
**Location:** `game/core/exceptions.py:216-232`
**Issue:** AIException and TargetingException are defined and documented in the exception hierarchy, but are never actually raised anywhere in the codebase. The AI module uses defensive programming with logging and fallback behavior instead of exceptions.
**Impact:** Dead code that suggests incomplete implementation or design mismatch. Developers may expect these exceptions to be raised when they won't be.
**Recommendation:** Either:
1. Delete these exception classes if the AI module intentionally avoids exceptions
2. Actually use them in the target_evaluator.py and controller.py where errors are currently logged and suppressed
**Effort:** Simple (if deleting) / Medium (if implementing)

#### MAJOR: Backward Compatibility Wrapper - load_resources()
**ID:** LEG-FND-002
**Location:** `game/core/resources.py:101-114`
**Issue:** The `load_resources()` function explicitly states it exists "for backward compatibility" and recommends new code use `load_resources_data()` instead. However, the function is still actively called from `game/app.py:97`.
**Impact:** The backward compatibility wrapper is not just legacy code but actively used. This is a partial migration - the new pattern exists but the old call site was never updated.
**Recommendation:** Update `game/app.py` to use the DI-friendly `load_resources_data()` pattern directly, then delete the wrapper function.
**Effort:** Simple

#### MINOR: Backward Compatibility Comment in ValidationResult.message
**ID:** LEG-FND-003
**Location:** `game/core/validation.py:100-107`
**Issue:** The `ValidationResult.message` property has a docstring stating it "provides backwards compatibility with code that expects a single message property." This suggests a migration from single-message to multi-message validation was done, but backward compat was retained.
**Impact:** Low impact - this is a simple property accessor. The comment documents intentional design.
**Recommendation:** Audit callers of `.message` property to see if they should switch to `.errors[0]` or iterate `.errors`. If all callers are updated, remove the property. If it's genuinely useful API, remove the "backward compatibility" comment as it's now just the API.
**Effort:** Simple

#### MINOR: Extensive getattr() with Defaults in AI Module
**ID:** LEG-FND-004
**Location:** `game/ai/controller.py`, `game/ai/behaviors.py`, `game/ai/target_evaluator.py`, `game/ai/combat_utils.py`
**Issue:** The AI module makes heavy use of `getattr(obj, 'attr', default)` patterns (30+ instances). While documented as "defensive programming for robustness," this pattern can mask bugs where attributes should exist but don't. Many of these access patterns seem to be handling raw Ship objects vs ShipControllableAdapter differences.
**Impact:** Could mask interface contract violations. Makes code harder to maintain as expected attributes are unclear.
**Recommendation:** Review whether all these defensive patterns are necessary post-PROJ-86 (God Class Decomposition). The ShipControllableAdapter should provide consistent interface. Consider using explicit type guards or Protocol checks instead of broad getattr fallbacks.
**Effort:** Medium

#### MINOR: Raw Ship vs Adapter Access Pattern in FormationBehavior
**ID:** LEG-FND-005
**Location:** `game/ai/behaviors.py:276-400` (FormationBehavior class)
**Issue:** Comments explicitly note that `formation_master returns a raw Ship, not adapter` and code accesses `master.position`, `master.angle`, `master.is_alive` directly on raw Ship objects while the adapter is used for `self.controller.ship`. This suggests incomplete adapter encapsulation.
**Impact:** Inconsistent access patterns make the code harder to understand and maintain. May indicate the adapter pattern wasn't fully applied to formation relationships.
**Recommendation:** Either extend ShipControllableAdapter to handle formation master access consistently, or document this as intentional design (formations access raw Ship for performance).
**Effort:** Medium

#### MINOR: DEBUG_SCREENSHOTS Hardcoded True
**ID:** LEG-FND-006
**Location:** `game/core/constants.py:41`
**Issue:** `DEBUG_SCREENSHOTS = True` is hardcoded in constants. This debug flag is used by `game/ui/services/screenshot_manager.py` to enable screenshot functionality. Having it always true suggests either it's not actually a debug flag, or it should be configurable.
**Impact:** Screenshots are always enabled regardless of build configuration.
**Recommendation:** Either rename to `ENABLE_SCREENSHOTS` to indicate it's a feature toggle not a debug flag, or move to a configuration system that can distinguish debug/release builds.
**Effort:** Simple

#### MINOR: Singleton Pattern Still in Use Despite DI Preference
**ID:** LEG-FND-007
**Location:** Multiple files in assigned scope (9 classes using SingletonMeta)
**Issue:** The codebase uses SingletonMeta for Logger, Profiler, StrategyManager, StrategyMetadataService, RegistryManager, and others. CLAUDE.md states "Dependency injection replaced singletons in many areas" but singletons are still prevalent in core infrastructure.
**Impact:** Singletons make testing harder and create hidden dependencies. However, these are legitimately global services (logging, profiling, registry) where singleton may be appropriate.
**Recommendation:** No action needed for Logger/Profiler (legitimately global). Consider whether StrategyManager and StrategyMetadataService should use DI instead - they're called via `.instance()` from AI code which could instead receive them as constructor parameters.
**Effort:** Complex (architectural decision)

#### INFO: Well-Organized Research Module
**ID:** LEG-FND-008
**Location:** `game/research/` (entire module)
**Issue:** None - This module is cleanly implemented with no legacy patterns detected. Uses proper dataclasses, clear separation (data/systems/ui), no singletons, and follows modern patterns.
**Impact:** Positive - this is a model for how other modules should look.
**Recommendation:** Use as reference when refactoring other modules.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-FND-002 (MAJOR):** Backward compatibility wrapper `load_resources()` is actively used but marked as deprecated. Complete the migration by updating `game/app.py` to use DI pattern.

2. **LEG-FND-001 (MAJOR):** Unused AIException and TargetingException classes create confusion about error handling contract in AI module. Decide on keeping or removing.

3. **LEG-FND-004 (MINOR):** Heavy getattr() usage in AI module may mask interface violations. Review post-God-Class-Decomposition to see if defensive patterns are still needed.

4. **LEG-FND-005 (MINOR):** Inconsistent raw Ship vs Adapter access in FormationBehavior. Document or fix the encapsulation gap.

5. **LEG-FND-003 (MINOR):** ValidationResult.message backward compat comment - audit callers to see if migration can be completed.
