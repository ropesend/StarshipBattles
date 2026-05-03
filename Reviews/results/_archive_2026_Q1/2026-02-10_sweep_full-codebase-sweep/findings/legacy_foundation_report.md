# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 41
- **Total Issues Found:** 8
- **Critical:** 1 | **Major:** 3 | **Minor:** 3 | **Info:** 1

## Findings

#### CRITICAL: Backward Compatibility Shims in ValidationResult
**ID:** LEG-FND-001
**Location:** `game/core/validation.py:71-184`
**Issue:** ValidationResult class maintains two construction patterns for backward compatibility: Pattern 1 (simulation) uses errors=["Error 1", "Error 2"], Pattern 2 (strategy/UI) uses message="Error message". Also includes .message property (line 121-128) and factory methods .create() and validation_result() function for old-style usage. PROJ-21 consolidated 5 duplicate implementations but didn't fully unify the API.
**Impact:** Multiple entry points for same object. .message property actively used in UI files, masking schema inconsistency.
**Recommendation:** Standardize to single construction pattern; migrate all callers to unified API.
**Effort:** Medium

#### MAJOR: Proxy Pattern for Global Logger Access
**ID:** LEG-FND-002
**Location:** `game/core/logger.py:68-69, 71-81`
**Issue:** Module-level _logger global with proxy functions (log_debug, log_info, log_warning, log_error) that bypass the singleton Logger.instance() API. Adds unnecessary indirection layer.
**Impact:** Legacy pattern bypasses DI. Two access patterns for same functionality.
**Recommendation:** Remove _logger global and proxy functions; require direct Logger usage.
**Effort:** Medium

#### MAJOR: Global Proxy for Profiler Access
**ID:** LEG-FND-003
**Location:** `game/core/profiling.py:135-146`
**Issue:** _ProfilerProxy class wraps Profiler.instance() for "backwards compatibility (lazy, not module-level instantiation)". Code uses PROFILER.record() instead of Profiler.instance().record().
**Impact:** Creates unnecessary abstraction; mixing proxy and direct access patterns.
**Recommendation:** Remove proxy entirely; use Profiler.instance() directly.
**Effort:** Medium

#### MAJOR: Orphaned Factory Methods in ValidationResult
**ID:** LEG-FND-004
**Location:** `game/core/validation.py:105-118` (.create() method) AND `game/core/validation.py:168-183` (validation_result() function)
**Issue:** Two factory methods for creating ValidationResult exist alongside standard constructor. .create() is classmethod, validation_result() is module function — both do the same thing.
**Impact:** Code confusion about which API to use; increases maintenance burden.
**Recommendation:** Delete both factory methods; use standard constructor directly.
**Effort:** Simple

#### MINOR: Unused Parameters in Target Evaluator
**ID:** LEG-FND-005
**Location:** `game/ai/target_evaluator.py`
**Issue:** Multiple helper methods accept unused stat_helpers and ship_capabilities_cache parameters that default to None and are only optionally used.
**Impact:** Potential dead code paths if caching never used in practice.
**Recommendation:** Audit actual usage; remove unused parameters.
**Effort:** Simple

#### MINOR: MagicMock Detection in Production Code
**ID:** LEG-FND-006
**Location:** `game/ai/target_evaluator.py:53-67`
**Issue:** _get_position function tries get_position() interface method first, falls back to .position attribute with explicit comment about MagicMock detection. Test-specific logic in production code.
**Impact:** Suggests incomplete migration from mock-based to interface-based testing.
**Recommendation:** Remove MagicMock detection; require interface implementation or document fallback.
**Effort:** Simple

#### MINOR: Inconsistent "old_" Variable Naming Pattern
**ID:** LEG-FND-007
**Location:** `game/research/systems/research_service.py:78-140`
**Issue:** Variables named old_chance, old_level, old_allocation used to track previous state for event logging. Mirrors deprecated before-state tracking pattern.
**Impact:** Minor - code is functional but uses legacy naming convention.
**Recommendation:** Consider refactoring to immutable State objects with Before/After pattern.
**Effort:** Simple

#### INFO: TypeGuard Import Fallback
**ID:** LEG-FND-008
**Location:** `game/core/protocols.py:32-36`
**Issue:** Try/except import for TypeGuard (Python 3.9 fallback to typing_extensions). Python 3.9 is now EOL.
**Impact:** Functional but outdated. Can remove typing_extensions dependency if upgrading minimum version.
**Recommendation:** Document Python version requirement; consider 3.10+ minimum.
**Effort:** Simple

## Top 5 Priority Issues
1. **LEG-FND-001** (CRITICAL): ValidationResult backward compat shims - unify API
2. **LEG-FND-003** (MAJOR): _ProfilerProxy class - remove, use Profiler.instance() directly
3. **LEG-FND-002** (MAJOR): Logger proxy functions - remove, use Logger directly
4. **LEG-FND-004** (MAJOR): Orphaned factory methods - delete redundant construction paths
5. **LEG-FND-006** (MINOR): MagicMock detection in production - remove test-specific code
