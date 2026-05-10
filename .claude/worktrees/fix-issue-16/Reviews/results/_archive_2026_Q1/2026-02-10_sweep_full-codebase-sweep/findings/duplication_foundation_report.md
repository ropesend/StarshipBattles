# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 40
- **Total Issues Found:** 6
- **Critical:** 1 | **Major:** 3 | **Minor:** 2 | **Info:** 0

## Findings

#### CRITICAL: Singleton Initialization Pattern Duplication (5 Implementations)
**ID:** DUP-FND-001
**Location:** `game/core/logger.py` AND `game/core/profiler.py` AND `game/core/registry_manager.py` AND `game/engine/screenshot_manager.py` AND `game/engine/strategy_manager.py`
**Issue:** All 5 classes implement identical double-checked locking singleton pattern with _lock, _instance, and identical instance() classmethod. 7 instances of `with cls._lock:` across the codebase. Each independently reimplements the same thread-safe creation logic. ~25 lines duplicated per class, ~125 lines total.
**Impact:** High maintenance burden. Any change to singleton pattern must be applied in 5 places. Inconsistent error messages and reset behavior across singletons.
**Recommendation:** Create SingletonMeta metaclass or BaseSingleton mixin to eliminate boilerplate.
**Effort:** Medium

#### MAJOR: Position and Rotation Helper Functions Duplicated
**ID:** DUP-FND-002
**Location:** `game/ai/target_evaluator.py:35-98` AND similar patterns in `game/ai/controllable.py`
**Issue:** _get_position() and _get_rotation() in target_evaluator.py implement defensive fallback logic from interface methods to direct attribute access. Same concept needed in controllable.py. 64 lines of near-identical defensive code.
**Impact:** Both include fallback logic that could diverge. If position access pattern changes, must update in multiple places.
**Recommendation:** Extract shared PositionAccessor utility with safe position/rotation getters.
**Effort:** Simple

#### MAJOR: JSON File Loading Pattern (15 files)
**ID:** DUP-FND-003
**Location:** `game/core/resources.py` AND `game/core/component.py` AND `game/strategy/data/design_metadata.py` AND 12+ other files
**Issue:** Identical try-catch-log-return-default patterns for JSON file loading. All files contain 5-15 line near-duplicate error handling code. Each independently handles FileNotFoundError, json.JSONDecodeError with logging.
**Impact:** Low risk individually, but maintenance burden across 15+ files. If error handling needs enhancement (e.g., custom exception), must update everywhere.
**Recommendation:** Consolidate into shared load_json_safe() wrapper in game/core/resources.py.
**Effort:** Simple

#### MAJOR: HP Percentage and PDC Arc Check Utilities Duplicated
**ID:** DUP-FND-004
**Location:** `game/ai/controller.py:269-282` AND `game/ai/target_evaluator.py`
**Issue:** _stat_get_hp_percent() / _get_hp_percent() and _stat_is_in_pdc_arc() / _is_in_pdc_arc() duplicated in both files. Static + instance versions in controller.py, only static in target_evaluator.py. 30+ lines of duplicated calculation logic.
**Impact:** Bug fix in HP calculation would need to be applied to both versions. Confusing that same calculation has different method names.
**Recommendation:** Extract to shared AI utility module with single implementation.
**Effort:** Simple

#### MINOR: Validation Result Creation Pattern Redundancy
**ID:** DUP-FND-005
**Location:** `game/core/validation.py`
**Issue:** ValidationResult class supports two construction patterns: list of errors vs. single message. Additional factory methods (create(), validation_result()) provide redundant ways to construct results. 50+ lines could be consolidated into one pattern.
**Impact:** Low - multiple valid construction patterns, but cognitive overhead for developers choosing which to use.
**Recommendation:** Standardize on one construction pattern, deprecate alternatives.
**Effort:** Simple

#### MINOR: Distance Calculation Across Modules (5 files)
**ID:** DUP-FND-006
**Location:** `game/ai/target_evaluator.py:108-132` (_safe_distance) AND `game/ai/controller.py:466` AND various other files
**Issue:** Distance calculations implemented independently in 5 files with different safety checks and fallbacks. _safe_distance() in target_evaluator is the most robust but others use inline calculations.
**Impact:** Low - distance calculation is simple, but inconsistent safety checks could cause edge-case bugs.
**Recommendation:** Extract distance utilities to shared module.
**Effort:** Simple

## Top 5 Priority Issues
1. **DUP-FND-001: Singleton Pattern** - 125 lines of identical code across 5 classes
2. **DUP-FND-002: Position/Rotation Helpers** - 64 lines of defensive code duplicated in AI module
3. **DUP-FND-003: JSON Loading Pattern** - 15 files with identical error handling boilerplate
4. **DUP-FND-004: HP/PDC Utilities** - Confusing dual implementations in AI module
5. **DUP-FND-006: Distance Calculations** - Inconsistent safety checks across 5 files
